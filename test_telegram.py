from telegram_service import send_trade_alert

test_trade = {
    "symbol": "$AAPL",
    "direction": "LONG",
    "asset_class": "EQUITIES",
    "setup": "Opening Range Breakout",
    "regime": "Trending",
    "momentum_algo": "Momentum Algo",
    "entry": "$214.32",
    "stop": "$212.80",
    "stop_percent": "(-0.71%)",
    "target": "$217.50",
    "target_percent": "(+1.48%)",
    "size": 14,
    "risk": "21.28",
    "rr_ratio": "1:2.1",
    "volume_multiplier": 2.3,
    "nearest_level": "$213.10 support",
    "level_distance": "0.57",
    "session": "Regular Hours",
    "catalyst": "None",
    "confidence": 87,
    "chart_timeframe": "5min chart"
}

print("Sending test trade alert to Telegram...")
success = send_trade_alert(test_trade)

if success:
    print("[OK] Test alert sent successfully!")
else:
    print("[FAIL] Failed to send test alert. Check credentials and logs.")
