import requests
import json

BASE_URL = "http://127.0.0.1:8001"

# Test payload 1: EQUITIES
equities_payload = {
    "ticker": "AAPL",
    "direction": "LONG",
    "asset_class": "EQUITIES",
    "setup": "Opening Range Breakout",
    "regime": "Trending | Momentum Algo",
    "price": 214.32,
    "stop": 212.80,
    "target": 217.50,
    "volume_vs_avg": 2.3,
    "confidence": 87,
    "timeframe": "5min",
    "session": "Regular Hours",
    "catalyst": "None",
    "nearest_level": "$213.10 support",
    "level_distance": "0.57",
    "size": 14,
    "risk": 21.28,
    "base_currency": "USD"
}

# Test payload 2: FUTURES
futures_payload = {
    "ticker": "ES",
    "direction": "SHORT",
    "asset_class": "FUTURES",
    "setup": "Head and Shoulders",
    "regime": "Mean Reversion | Breakout",
    "price": 5842.50,
    "stop": 5865.25,
    "target": 5800.00,
    "volume_vs_avg": 1.8,
    "confidence": 72,
    "timeframe": "15min",
    "session": "Regular Hours",
    "catalyst": "FOMC Meeting",
    "nearest_level": "$5850 resistance",
    "level_distance": "0.13",
    "size": 3,
    "risk": 68.25,
    "base_currency": "USD"
}

# Test payload 3: CRYPTO
crypto_payload = {
    "ticker": "BTCUSD",
    "direction": "LONG",
    "asset_class": "CRYPTO",
    "setup": "Cup and Handle",
    "regime": "Trending | Technical",
    "price": 68500.00,
    "stop": 66800.00,
    "target": 72500.00,
    "volume_vs_avg": 2.5,
    "confidence": 91,
    "timeframe": "1h",
    "session": "24/7",
    "catalyst": "None",
    "nearest_level": "$70000 resistance",
    "level_distance": "2.19",
    "size": 0.5,
    "risk": 850.00,
    "base_currency": "BTC"
}

payloads = [
    ("EQUITIES", equities_payload),
    ("FUTURES", futures_payload),
    ("CRYPTO", crypto_payload)
]

print("Testing TradingView webhook endpoint...\n")

for asset_class, payload in payloads:
    print(f"Sending {asset_class} alert...")
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/tradingview",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f"[OK] {asset_class} alert sent successfully")
            print(f"    Response: {response.json()['message']}\n")
        else:
            print(f"[FAIL] {asset_class} alert failed")
            print(f"    Status: {response.status_code}")
            print(f"    Error: {response.json()}\n")
    except Exception as e:
        print(f"[ERROR] {asset_class} request failed: {str(e)}\n")

print("Testing complete. Check Telegram for alerts.")
