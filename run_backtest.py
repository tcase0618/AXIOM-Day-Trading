import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from backtest_orb import ORBBacktester
from datetime import datetime
import json

# ES1! 5-minute bar data from TradingView
bars_raw = [
    {"time": 1780599600, "open": 7604.5, "high": 7607.25, "low": 7604.25, "close": 7607.25, "volume": 5282},
    {"time": 1780599900, "open": 7607.25, "high": 7609, "low": 7606.75, "close": 7607.25, "volume": 7089},
    {"time": 1780600200, "open": 7607.5, "high": 7607.75, "low": 7605, "close": 7606, "volume": 6401},
    {"time": 1780600500, "open": 7606.25, "high": 7606.25, "low": 7604, "close": 7605.25, "volume": 6422},
    {"time": 1780600800, "open": 7605, "high": 7608.25, "low": 7604.75, "close": 7608, "volume": 6876},
    {"time": 1780601100, "open": 7608, "high": 7611.25, "low": 7607.5, "close": 7611, "volume": 8344},
    {"time": 1780601400, "open": 7611, "high": 7611.5, "low": 7609.25, "close": 7609.75, "volume": 7981},
    {"time": 1780601700, "open": 7609.75, "high": 7611, "low": 7609, "close": 7610.25, "volume": 6571},
    {"time": 1780602000, "open": 7610.25, "high": 7610.25, "low": 7606, "close": 7606.5, "volume": 9612},
    {"time": 1780602300, "open": 7606.25, "high": 7607.5, "low": 7604.5, "close": 7606.75, "volume": 11023},
]

print("Processing ES1! 5-minute bar data...")
print("Total bars: " + str(len(bars_raw)))

# Convert timestamps
bars = []
for bar in bars_raw:
    dt = datetime.utcfromtimestamp(bar['time']).isoformat()
    bars.append({
        'time': dt,
        'open': bar['open'],
        'high': bar['high'],
        'low': bar['low'],
        'close': bar['close'],
        'volume': bar['volume']
    })

# Run backtest
bt = ORBBacktester()
bt.run_backtest(bars)
metrics = bt.get_metrics()

print("")
print("="*60)
print("FUTURES ORB US OPEN BACKTEST RESULTS")
print("="*60)
print("Total Trades: " + str(metrics['total_trades']))
print("Win Rate: " + str(metrics['win_rate']) + "%")
print("Profit Factor: " + str(metrics['profit_factor']))
print("Max Drawdown: " + str(metrics['max_drawdown']) + "%")
print("Net P&L: $" + str(metrics['net_pnl']))
print("="*60)

print("\nRESULT: Strategy produced " + str(metrics['total_trades']) + " trades")
