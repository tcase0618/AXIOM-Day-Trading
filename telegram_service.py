import os
import requests
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_trade_alert(trade: dict) -> bool:
    """
    Send a formatted trade alert to Telegram.

    Args:
        trade: Dictionary containing trade details with keys:
            - direction: "LONG" or "SHORT"
            - symbol: Stock/futures/crypto symbol (e.g., "$AAPL")
            - asset_class: "EQUITIES", "FUTURES", or "CRYPTO"
            - setup: Trading setup name
            - regime: Market regime
            - momentum_algo: Momentum algorithm used
            - entry: Entry price
            - stop: Stop loss price
            - stop_percent: Stop loss percentage
            - target: Target price
            - target_percent: Target percentage
            - risk: Risk amount in dollars
            - size: Position size (numeric)
            - base_currency: For CRYPTO, the currency name (e.g., "BTC")
            - rr_ratio: Risk:Reward ratio (e.g., "1:2.1")
            - volume_multiplier: Volume relative to average (e.g., 2.3)
            - nearest_level: Nearest support/resistance level
            - level_distance: Distance to nearest level in percent
            - session: Trading session (e.g., "Regular Hours")
            - catalyst: Catalyst description or "None"
            - confidence: Confidence percentage (0-100)

    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        direction = trade.get("direction", "LONG").upper()
        asset_class = trade.get("asset_class", "EQUITIES").upper()

        direction_emoji = "🟢" if direction == "LONG" else "🔴"
        volume_multiplier = trade.get("volume_multiplier", 0)
        volume_emoji = "✅" if volume_multiplier >= 2.0 else "⚠️"
        catalyst = trade.get("catalyst", "None")
        catalyst_emoji = "✅" if catalyst.upper() == "NONE" else "⚠️"

        size_value = trade.get("size")
        if asset_class == "EQUITIES":
            size_str = f"Size: {size_value} shares"
        elif asset_class == "FUTURES":
            size_str = f"Size: {size_value} contracts"
        elif asset_class == "CRYPTO":
            base_currency = trade.get("base_currency", "BTC")
            size_str = f"Size: {size_value} {base_currency}"
        else:
            size_str = f"Size: {size_value}"

        est = pytz.timezone("US/Eastern")
        timestamp = datetime.now(est).strftime("%I:%M %p EST")

        symbol = trade.get("symbol", "N/A")
        setup = trade.get("setup", "N/A")
        regime = trade.get("regime", "N/A")
        momentum_algo = trade.get("momentum_algo", "N/A")
        entry = trade.get("entry", "N/A")
        stop = trade.get("stop", "N/A")
        stop_percent = trade.get("stop_percent", "N/A")
        target = trade.get("target", "N/A")
        target_percent = trade.get("target_percent", "N/A")
        risk = trade.get("risk", "N/A")
        rr_ratio = trade.get("rr_ratio", "N/A")
        nearest_level = trade.get("nearest_level", "N/A")
        level_distance = trade.get("level_distance", "N/A")
        session = trade.get("session", "Regular Hours")
        confidence = trade.get("confidence", "N/A")
        ict_score = trade.get("ict_score", 0)
        ict_factors = trade.get("ict_factors", "None")
        chart_timeframe = trade.get("chart_timeframe", "5min chart")

        # Build ICT line if score is present
        ict_line = ""
        if ict_score > 0:
            ict_line = f"ICT Confluence: {ict_score}/10 | {ict_factors}\n"

        message = f"""AXIOM DAY TRADING
{direction_emoji} {direction} | {symbol} | {asset_class}
─────────────────────
Setup: {setup}
Regime: {regime} | {momentum_algo}
Entry: {entry}
Stop: {stop} ({stop_percent})
Target: {target} ({target_percent})
R:R: {rr_ratio} | {size_str} | ${risk} risk
─────────────────────
Volume: {volume_multiplier}x avg {volume_emoji}
Nearest Level: {nearest_level} ({level_distance}% below)
Session: {session}
Catalyst: {catalyst} {catalyst_emoji}
Confidence: {confidence}%
{ict_line}─────────────────────
⏰ {timestamp} | {chart_timeframe}"""

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)

        if response.status_code == 200:
            logger.info(f"Trade alert sent successfully for {symbol}")
            return True
        else:
            logger.error(f"Failed to send trade alert. Status: {response.status_code}, Response: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error sending trade alert: {str(e)}")
        return False
