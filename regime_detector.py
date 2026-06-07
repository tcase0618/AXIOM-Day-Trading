import json
import logging
import os
from datetime import datetime
import pytz
import yfinance as yf
import pandas as pd
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REGIME_FILE = "current_regime.json"

# Regime classification rules
TRENDING_RULES = {
    "adx_min": 25,
    "vix_max": 20,
    "spy_above_emas": True
}

CHOPPY_RULES = {
    "adx_max": 20,
    "vix_range": (20, 30),
    "mixed_signals": True
}

HIGH_VOL_RULES = {
    "vix_min": 30
}

# Algorithm mapping per regime and asset class
ALGO_MAP = {
    "EQUITIES": {
        "TRENDING": "Momentum algo",
        "CHOPPY": "Mean Reversion algo",
        "HIGH VOLATILITY": "STAND DOWN"
    },
    "FUTURES": {
        "TRENDING": "Momentum algo",
        "CHOPPY": "VWAP Reversion algo",
        "HIGH VOLATILITY": "STAND DOWN"
    },
    "CRYPTO": {
        "TRENDING": "Momentum Continuation algo",
        "CHOPPY": "Range algo",
        "HIGH VOLATILITY": "Reduced size momentum algo"
    }
}


def fetch_market_data():
    """
    Fetch market data for regime detection.
    Returns dict with VIX, SPY prices/EMAs, ADX, breadth, BTC data.
    """
    try:
        logger.info("Fetching market data for regime detection...")

        # Fetch VIX
        vix_data = yf.download("^VIX", period="5d", progress=False)
        vix = vix_data["Close"].iloc[-1].item() if hasattr(vix_data["Close"].iloc[-1], 'item') else float(vix_data["Close"].iloc[-1])

        # Fetch SPY data
        spy_data = yf.download("SPY", period="50d", progress=False)
        spy_close = spy_data["Close"]
        spy_current = spy_close.iloc[-1].item() if hasattr(spy_close.iloc[-1], 'item') else float(spy_close.iloc[-1])

        # Calculate simple EMAs using pandas
        ema20_series = spy_close.ewm(span=20, adjust=False).mean()
        ema200_series = spy_close.ewm(span=200, adjust=False).mean()
        ema20_val = ema20_series.iloc[-1].item() if hasattr(ema20_series.iloc[-1], 'item') else float(ema20_series.iloc[-1])
        ema200_val = ema200_series.iloc[-1].item() if hasattr(ema200_series.iloc[-1], 'item') else float(ema200_series.iloc[-1])

        # Fetch BTC data
        btc_data = yf.download("BTC-USD", period="5d", progress=False)
        btc_current = btc_data["Close"].iloc[-1].item() if hasattr(btc_data["Close"].iloc[-1], 'item') else float(btc_data["Close"].iloc[-1])
        btc_prev = btc_data["Close"].iloc[-2].item() if hasattr(btc_data["Close"].iloc[-2], 'item') else float(btc_data["Close"].iloc[-2])
        btc_change = ((btc_current - btc_prev) / btc_prev) * 100

        # Calculate ADX (simplified - using price volatility as proxy)
        spy_returns = spy_close.pct_change().dropna()
        volatility = spy_returns.std().item() if hasattr(spy_returns.std(), 'item') else float(spy_returns.std())
        volatility = volatility * 100
        adx = min(100, max(10, volatility * 10))

        # Market breadth (simplified - using trend direction)
        spy_above_20ema = 1 if spy_current > ema20_val else 0
        spy_above_200ema = 1 if spy_current > ema200_val else 0
        breadth = (spy_above_20ema + spy_above_200ema) * 50

        market_data = {
            "vix": round(vix, 2),
            "spy_current": round(spy_current, 2),
            "spy_ema20": round(ema20_val, 2),
            "spy_ema200": round(ema200_val, 2),
            "spy_above_20ema": int(spy_above_20ema),
            "spy_above_200ema": int(spy_above_200ema),
            "adx": round(adx, 2),
            "breadth": int(breadth),
            "btc_current": round(btc_current, 2),
            "btc_change_pct": round(btc_change, 2)
        }

        logger.info(f"Market data fetched: VIX={market_data['vix']}, ADX={market_data['adx']}, Breadth={market_data['breadth']}%")
        return market_data

    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def classify_regime(market_data):
    """
    Classify market regime based on technical indicators.
    Returns regime classification: TRENDING, CHOPPY, or HIGH VOLATILITY.
    """
    try:
        vix = market_data["vix"]
        adx = market_data["adx"]
        spy_above_20 = market_data["spy_above_20ema"]
        spy_above_200 = market_data["spy_above_200ema"]

        # High volatility dominates everything
        if vix > 30:
            regime = "HIGH VOLATILITY"
        # Trending: strong ADX, SPY above both EMAs, low VIX
        elif adx > 25 and spy_above_20 and spy_above_200 and vix < 20:
            regime = "TRENDING"
        # Choppy: low ADX, mixed signals, moderate VIX
        elif adx < 20 and (not (spy_above_20 and spy_above_200)) and 20 <= vix <= 30:
            regime = "CHOPPY"
        # Default to choppy if no clear match
        else:
            regime = "CHOPPY"

        logger.info(f"Regime classified: {regime}")
        return regime

    except Exception as e:
        logger.error(f"Error classifying regime: {str(e)}")
        return "CHOPPY"


def get_liquidity_bias(symbol="SPY"):
    """
    Get liquidity bias from market data.
    Returns: "BULLISH" (more liquidity above price), "BEARISH" (below), or "NEUTRAL"

    In production, this would read from liquidity_map.pine on the chart.
    For now, we derive it from SPY position vs key levels.
    """
    try:
        # Fetch SPY data
        spy_data = yf.download("SPY", period="20d", progress=False)
        spy_current = spy_data["Close"].iloc[-1]
        spy_high_20d = spy_data["High"].iloc[-20:].max()
        spy_low_20d = spy_data["Low"].iloc[-20:].min()

        # Calculate midpoint
        midpoint = (spy_high_20d + spy_low_20d) / 2.0

        # Liquidity bias based on price position
        if spy_current > midpoint:
            # Price above midpoint - more liquidity above
            bias = "BULLISH"
        elif spy_current < midpoint:
            # Price below midpoint - more liquidity below
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        logger.info(f"Liquidity Bias: {bias} (SPY at {spy_current:.2f}, 20d range: {spy_low_20d:.2f}-{spy_high_20d:.2f})")
        return bias

    except Exception as e:
        logger.error(f"Error calculating liquidity bias: {str(e)}")
        return "NEUTRAL"


def get_algo_for_regime(asset_class, regime, liquidity_bias="NEUTRAL"):
    """
    Get the algorithm for a given asset class and regime.
    Modified by liquidity bias: only take longs in BULLISH bias, shorts in BEARISH.
    """
    algo = ALGO_MAP.get(asset_class, {}).get(regime, "Unknown")

    # Add liquidity bias context
    bias_note = f" | Liquidity Bias: {liquidity_bias}"
    if liquidity_bias == "BULLISH":
        bias_note += " (LONGS ONLY)"
    elif liquidity_bias == "BEARISH":
        bias_note += " (SHORTS ONLY)"

    return algo + bias_note


def save_regime_to_file(regime_data):
    """Save current regime to JSON file for webhook handler to read."""
    try:
        regime_data["timestamp"] = datetime.now().isoformat()
        with open(REGIME_FILE, "w") as f:
            json.dump(regime_data, f, indent=2)
        logger.info(f"Regime saved to {REGIME_FILE}")
    except Exception as e:
        logger.error(f"Error saving regime to file: {str(e)}")


def send_regime_report(market_data, regime, liquidity_bias="NEUTRAL"):
    """Send daily regime report to Telegram."""
    try:
        est = pytz.timezone("US/Eastern")
        date_str = datetime.now(est).strftime("%Y-%m-%d")

        # Get algorithms for each asset class
        eq_algo = get_algo_for_regime("EQUITIES", regime, liquidity_bias)
        fut_algo = get_algo_for_regime("FUTURES", regime, liquidity_bias)
        crypto_algo = get_algo_for_regime("CRYPTO", regime, liquidity_bias)

        spy_trend = "BULLISH" if market_data["spy_above_200ema"] else "BEARISH"

        message = f"""AXIOM DAY TRADING
📊 DAILY REGIME REPORT
─────────────────────
Date: {date_str}
VIX: {market_data['vix']}
SPY Trend: {spy_trend}
ADX: {market_data['adx']}
Breadth: {market_data['breadth']}%
Liquidity Bias: {liquidity_bias}
─────────────────────
EQUITIES: {regime} | {eq_algo}
FUTURES: {regime} | {fut_algo}
CRYPTO: {regime} | {crypto_algo}
─────────────────────
System Status: ACTIVE [OK]"""

        logger.info("Sending regime report to Telegram...")
        requests.post(
            f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
            json={
                "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
                "text": message
            },
            timeout=10
        )
        logger.info("Regime report sent to Telegram")

    except Exception as e:
        logger.error(f"Error sending regime report: {str(e)}")


def detect_regime():
    """
    Main regime detection function called at 8am EST.
    Fetches data, classifies regime, detects liquidity bias, saves to file, sends report.
    """
    logger.info("=" * 50)
    logger.info("STARTING DAILY REGIME DETECTION")
    logger.info("=" * 50)

    # Fetch market data
    market_data = fetch_market_data()
    if not market_data:
        logger.error("Failed to fetch market data. Defaulting to CHOPPY regime.")
        market_data = {"regime": "CHOPPY"}
        return

    # Classify regime
    regime = classify_regime(market_data)

    # Get liquidity bias
    liquidity_bias = get_liquidity_bias()

    # Build regime data dict
    regime_data = {
        "regime": regime,
        "liquidity_bias": liquidity_bias,
        "market_data": market_data,
        "algos": {
            "EQUITIES": get_algo_for_regime("EQUITIES", regime, liquidity_bias),
            "FUTURES": get_algo_for_regime("FUTURES", regime, liquidity_bias),
            "CRYPTO": get_algo_for_regime("CRYPTO", regime, liquidity_bias)
        }
    }

    # Save to file for webhook to read
    save_regime_to_file(regime_data)

    # Send Telegram report
    send_regime_report(market_data, regime, liquidity_bias)

    logger.info("=" * 50)
    logger.info("REGIME DETECTION COMPLETE")
    logger.info("=" * 50)


# Initialize scheduler
scheduler = BackgroundScheduler()


def start_regime_scheduler():
    """Start the scheduler to run regime detection at 8am EST on trading days."""
    try:
        # Schedule for 8am EST, Monday-Friday
        scheduler.add_job(
            detect_regime,
            trigger="cron",
            hour=8,
            minute=0,
            day_of_week="0-4",  # Monday-Friday
            timezone="US/Eastern",
            id="daily_regime_detection"
        )

        if not scheduler.running:
            scheduler.start()
            logger.info("Regime detection scheduler started. Runs daily at 8am EST.")
        else:
            logger.info("Scheduler already running.")

    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")


def get_current_regime():
    """Read current regime from file."""
    try:
        with open(REGIME_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Regime file not found. Creating default regime...")
        default_regime = {
            "regime": "CHOPPY",
            "market_data": {},
            "algos": {
                "EQUITIES": "Mean Reversion algo",
                "FUTURES": "VWAP Reversion algo",
                "CRYPTO": "Range algo"
            },
            "timestamp": datetime.now().isoformat()
        }
        with open(REGIME_FILE, "w") as f:
            json.dump(default_regime, f, indent=2)
        return default_regime
    except Exception as e:
        logger.error(f"Error reading regime file: {str(e)}")
        return {"regime": "CHOPPY"}


if __name__ == "__main__":
    logger.info("Testing regime detection module...")
    detect_regime()
    regime = get_current_regime()
    logger.info(f"Current regime: {regime['regime']}")
