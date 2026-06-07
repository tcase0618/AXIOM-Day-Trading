import json
import logging
from datetime import datetime
from typing import Dict, Tuple
from telegram_service import send_trade_alert
from ict_confluence import calculate_ict_score

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REQUIRED_FIELDS = [
    "ticker", "direction", "asset_class", "setup", "price", "stop", "target",
    "volume_vs_avg", "confidence", "timeframe", "session"
]

# ICT context fields are optional but improve setup quality
ICT_CONTEXT_FIELDS = [
    "at_order_block", "in_fvg", "liquidity_sweep", "in_ote_zone",
    "in_discount_zone", "in_premium_zone", "choch_detected"
]


def handle_tradingview_alert(payload: dict) -> Tuple[bool, str, dict]:
    """
    Process incoming TradingView alert and send to Telegram.

    Args:
        payload: Dictionary containing trade alert data from TradingView

    Returns:
        Tuple of (success: bool, message: str, trade_data: dict)
    """
    try:
        # Validate required fields
        missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.warning(f"Validation failed: {error_msg}")
            return False, error_msg, {}

        # Extract and normalize data
        ticker = payload.get("ticker", "").upper()
        direction = payload.get("direction", "").upper()
        asset_class = payload.get("asset_class", "").upper()

        if direction not in ["LONG", "SHORT"]:
            error_msg = f"Invalid direction: {direction}. Must be LONG or SHORT."
            logger.warning(error_msg)
            return False, error_msg, {}

        if asset_class not in ["EQUITIES", "FUTURES", "CRYPTO"]:
            error_msg = f"Invalid asset class: {asset_class}"
            logger.warning(error_msg)
            return False, error_msg, {}

        # Extract numeric values
        price = float(payload.get("price", 0))
        stop = float(payload.get("stop", 0))
        target = float(payload.get("target", 0))
        size = payload.get("size", 0)
        confidence = int(payload.get("confidence", 0))
        volume_vs_avg = float(payload.get("volume_vs_avg", 0))

        # Calculate percentages and R:R
        stop_pct = ((stop - price) / price) * 100
        target_pct = ((target - price) / price) * 100
        risk = abs(price - stop) * size
        rr_ratio = abs(target_pct) / abs(stop_pct) if stop_pct != 0 else 0

        # Check for catalyst warnings
        catalyst = payload.get("catalyst", "None")
        if catalyst.upper() != "NONE":
            catalyst_status = catalyst
        else:
            catalyst_status = "None"

        # Calculate ICT Confluence Score (optional)
        ict_score = 0
        ict_factors = []
        ict_context = {
            "at_order_block": payload.get("at_order_block", False),
            "in_fvg": payload.get("in_fvg", False),
            "liquidity_sweep": payload.get("liquidity_sweep", False),
            "in_ote_zone": payload.get("in_ote_zone", False),
            "in_discount_zone": payload.get("in_discount_zone", False),
            "in_premium_zone": payload.get("in_premium_zone", False),
            "choch_detected": payload.get("choch_detected", False),
        }

        # Only calculate if at least one ICT context field is provided
        if any(ict_context.values()):
            ict_score, ict_factors = calculate_ict_score(ict_context, direction)
            logger.info(f"ICT Confluence Score: {ict_score}/10 | Factors: {' + '.join(ict_factors)}")

            # Check if setup meets minimum ICT confluence threshold (3+)
            if asset_class in ["EQUITIES", "FUTURES"] and ict_score < 3 and ict_factors:
                logger.warning(f"Setup below minimum ICT confluence threshold: {ict_score}/10")
                error_msg = f"Setup below minimum ICT confluence ({ict_score}/10 < 3)"
                return False, error_msg, {}

        # Build trade data for Telegram
        trade_data = {
            "symbol": f"${ticker}",
            "direction": direction,
            "asset_class": asset_class,
            "setup": payload.get("setup", "N/A"),
            "regime": payload.get("regime", "N/A"),
            "momentum_algo": payload.get("regime", "N/A").split("|")[1].strip() if "|" in payload.get("regime", "") else "N/A",
            "entry": f"${price:.2f}",
            "stop": f"${stop:.2f}",
            "stop_percent": f"({stop_pct:.2f}%)",
            "target": f"${target:.2f}",
            "target_percent": f"({target_pct:.2f}%)",
            "size": size,
            "risk": f"{risk:.2f}",
            "rr_ratio": f"1:{abs(rr_ratio):.1f}",
            "volume_multiplier": volume_vs_avg,
            "nearest_level": payload.get("nearest_level", "N/A"),
            "level_distance": payload.get("level_distance", "N/A"),
            "session": payload.get("session", "Regular Hours"),
            "catalyst": catalyst_status,
            "confidence": confidence,
            "ict_score": ict_score,
            "ict_factors": " + ".join(ict_factors) if ict_factors else "None",
            "chart_timeframe": f"{payload.get('timeframe', '5min')} chart",
            "base_currency": payload.get("base_currency", "USD"),
            "timestamp": datetime.now().isoformat()
        }

        # Send to Telegram
        telegram_success = send_trade_alert(trade_data)
        if not telegram_success:
            error_msg = "Failed to send Telegram alert"
            logger.error(error_msg)
            return False, error_msg, trade_data

        # Append to trades log
        try:
            with open("trades_log.json", "r") as f:
                trades = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            trades = []

        trades.append(trade_data)

        with open("trades_log.json", "w") as f:
            json.dump(trades, f, indent=2)

        logger.info(f"Trade alert processed successfully: {ticker} {direction}")
        return True, "Trade alert processed and sent", trade_data

    except ValueError as e:
        error_msg = f"Invalid numeric value in payload: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, {}
    except Exception as e:
        error_msg = f"Error processing trade alert: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, {}
