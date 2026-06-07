from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
import uvicorn
import logging
from datetime import datetime
from webhook_handler import handle_tradingview_alert
from regime_detector import start_regime_scheduler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AXIOM Day Trading system...")
    start_regime_scheduler()
    logger.info("Regime detection scheduler started")
    yield
    logger.info("Shutting down AXIOM Day Trading system...")


app = FastAPI(lifespan=lifespan)


class TradeAlert(BaseModel):
    ticker: str
    direction: str
    asset_class: str
    setup: str
    regime: str = None
    price: float
    stop: float
    target: float
    volume_vs_avg: float
    confidence: int
    timeframe: str
    session: str
    catalyst: str = "None"
    nearest_level: str = None
    level_distance: str = None
    size: float = 0
    risk: float = 0
    base_currency: str = "USD"


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "AXIOM Day Trading"}


@app.post("/webhook/tradingview")
async def webhook_tradingview(alert: TradeAlert):
    """
    Receive TradingView alert and process trade.
    """
    timestamp = datetime.now().isoformat()
    logger.info(f"[{timestamp}] Incoming TradingView alert: {alert.ticker} {alert.direction}")

    try:
        payload = alert.dict()
        success, message, trade_data = handle_tradingview_alert(payload)

        if success:
            logger.info(f"[{timestamp}] Alert processed: {alert.ticker}")
            return {
                "status": "success",
                "message": message,
                "trade": alert.dict()
            }
        else:
            logger.warning(f"[{timestamp}] Alert validation failed: {message}")
            raise HTTPException(status_code=400, detail=message)

    except Exception as e:
        error_msg = f"Error processing webhook: {str(e)}"
        logger.error(f"[{timestamp}] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
