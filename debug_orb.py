import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from datetime import datetime
from collections import defaultdict

# 300 bars of real ES1! 5-minute data from TradingView
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
    {"time": 1780602600, "open": 7606.5, "high": 7609, "low": 7602.25, "close": 7604.25, "volume": 23276},
    {"time": 1780602900, "open": 7604.25, "high": 7604.5, "low": 7598.25, "close": 7599.5, "volume": 86280},
    {"time": 1780603200, "open": 7599.75, "high": 7602, "low": 7594.25, "close": 7595, "volume": 21184},
    {"time": 1780603500, "open": 7595, "high": 7596.75, "low": 7593, "close": 7595.25, "volume": 7040},
    {"time": 1780603800, "open": 7595.25, "high": 7595.5, "low": 7593, "close": 7594, "volume": 5484},
    {"time": 1780604100, "open": 7593.75, "high": 7595, "low": 7591, "close": 7591.5, "volume": 3083},
    {"time": 1780604400, "open": 7591.5, "high": 7592, "low": 7589.75, "close": 7591.25, "volume": 1765},
    {"time": 1780604700, "open": 7591.5, "high": 7591.5, "low": 7587.5, "close": 7588.75, "volume": 2312},
    {"time": 1780605000, "open": 7588.75, "high": 7590.75, "low": 7588.25, "close": 7589.5, "volume": 1636},
    {"time": 1780605300, "open": 7589.5, "high": 7590.5, "low": 7588.5, "close": 7589.5, "volume": 1222},
    {"time": 1780605600, "open": 7589.5, "high": 7591.25, "low": 7588.5, "close": 7588.75, "volume": 1619},
    {"time": 1780605900, "open": 7588.75, "high": 7589.5, "low": 7587.25, "close": 7587.25, "volume": 1381},
    {"time": 1780606200, "open": 7587.5, "high": 7589.75, "low": 7587.25, "close": 7589, "volume": 1073},
    {"time": 1780606500, "open": 7589.25, "high": 7590.25, "low": 7587.75, "close": 7587.75, "volume": 1984},
]

# Convert timestamps to datetime
bars = []
for bar in bars_raw:
    dt = datetime.utcfromtimestamp(bar['time'])
    bars.append({
        'time': bar['time'],
        'dt': dt,
        'open': bar['open'],
        'high': bar['high'],
        'low': bar['low'],
        'close': bar['close'],
        'volume': bar['volume']
    })

print("="*80)
print("DEBUG: ORB DETECTION ANALYSIS")
print("="*80)
print("")

# Print first 10 bars to verify timezone and data
print("FIRST 10 BARS (verify timestamps and timezone):")
print("-" * 80)
for i in range(min(10, len(bars))):
    bar = bars[i]
    dt = bar['dt']
    print("Bar {}: {} UTC (Hour: {}, Min: {}) | O:{} H:{} L:{} C:{}".format(
        i,
        dt.isoformat(),
        dt.hour,
        dt.minute,
        bar['open'],
        bar['high'],
        bar['low'],
        bar['close']
    ))

print("")
print("="*80)
print("SESSION DETECTION (9:30am-3:45pm ET = 13:30-19:45 UTC)")
print("="*80)
print("")

# Track sessions
session_data = defaultdict(lambda: {'bars': [], 'orb_high': None, 'orb_low': None, 'orb_formed': False})

for idx, bar in enumerate(bars):
    dt = bar['dt']
    hour = dt.hour
    minute = dt.minute
    date_key = dt.strftime('%Y-%m-%d')

    # Check: is this bar during session?
    # ET time = UTC - 4 (EDT) or UTC - 5 (EST)
    # 9:30am ET = 13:30 UTC (EDT) or 14:30 UTC (EST)
    # 3:45pm ET = 19:45 UTC (EDT) or 20:45 UTC (EST)

    # For June 2026, should be EDT (UTC-4)
    # So 9:30am ET = 13:30 UTC
    # Let's check both possibilities

    et_hour_edt = hour - 4 if hour >= 4 else hour + 20
    et_minute = minute

    is_orb_forming = (et_hour_edt == 9 and 30 <= et_minute < 45)
    is_session_start = (et_hour_edt == 9 and 30 <= et_minute)

    if is_session_start:
        print("BAR {}: {} | DATETIME: {} UTC | ET EQUIV: {}:{}".format(
            idx,
            date_key,
            dt.isoformat(),
            et_hour_edt,
            str(et_minute).zfill(2)
        ))
        print("  -> SESSION START DETECTED | Price: {} | ORB will form for next 15 min".format(bar['close']))

        # Initialize session
        session_data[date_key]['orb_high'] = bar['high']
        session_data[date_key]['orb_low'] = bar['low']
        session_data[date_key]['bars'].append(idx)

print("")
print("="*80)
print("SESSION SUMMARY")
print("="*80)
for date_key, data in sorted(session_data.items()):
    if data['orb_high'] is not None:
        print("Date: {} | ORB High: {} | ORB Low: {} | Bars in session: {}".format(
            date_key,
            data['orb_high'],
            data['orb_low'],
            len(data['bars'])
        ))

print("")
print("="*80)
print("ANALYSIS")
print("="*80)
print("")
print("PROBLEM: The data shows UTC timestamps (13:30-14:30+ range)")
print("but the strategy code assumes ET timezone hour checks.")
print("")
print("In the Pine Script code:")
print("  (hour == 9 and minute >= 30) checks for 9:30am")
print("")
print("But the TradingView API returns UTC timestamps, where:")
print("  9:30am ET (EDT) = 13:30 UTC")
print("  So hour would be 13, not 9")
print("")
print("SOLUTION: The ORB detection is looking for hour==9")
print("but the data has hour==13-14 (UTC).")
print("That's why it only fires 2 times - likely on bars where")
print("something else coincidentally matched the logic.")
print("")
