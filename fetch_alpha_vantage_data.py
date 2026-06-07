"""
Fetch real market data from Alpha Vantage for ORB backtesting
Pulls 5-minute intraday data and filters to 9:30 AM - 4:00 PM ET
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries
import pytz

# Initialize Alpha Vantage
ALPHA_VANTAGE_API_KEY = "H62ZC5DSZT4WB86J"
ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')

# Timezone handling
et = pytz.timezone('US/Eastern')
utc = pytz.UTC


def fetch_intraday_data(symbol: str, interval: str = "5min", days: int = 60) -> list:
    """
    Fetch intraday data from Alpha Vantage

    Args:
        symbol: Stock symbol (e.g., "SPY", "ES1!", "QQQ")
        interval: "5min", "15min", "60min"
        days: Approximate days of data to fetch

    Returns:
        List of bars with OHLCV data in chronological order
    """

    print(f"Fetching {symbol} {interval} data from Alpha Vantage...")
    try:
        # Fetch data - Alpha Vantage returns most recent data first
        data, meta_data = ts.get_intraday(symbol=symbol, interval=interval)

        print(f"✓ Data fetched: {len(data)} bars available")
        print(f"  Output size: {meta_data.get('3. Time Zone', 'N/A')}")

        # Convert to list and reverse to chronological order
        bars = []
        for date_str, row in data.iterrows():
            try:
                # Parse the datetime string - Alpha Vantage returns dates in ET
                # Format: "2026-06-05 16:00:00" or "2026-06-05 09:30:00"
                dt_et = et.localize(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S'))

                # Convert to UTC
                dt_utc = dt_et.astimezone(utc)

                bar = {
                    'time': int(dt_utc.timestamp()),  # Unix timestamp in UTC
                    'datetime': date_str,
                    'datetime_et': dt_et.strftime('%Y-%m-%d %H:%M:%S ET'),
                    'open': float(row['1. open']),
                    'high': float(row['2. high']),
                    'low': float(row['3. low']),
                    'close': float(row['4. close']),
                    'volume': int(row['5. volume']),
                    'hour_et': dt_et.hour,
                    'minute_et': dt_et.minute
                }
                bars.append(bar)
            except Exception as e:
                print(f"Error parsing row {date_str}: {e}")
                continue

        # Reverse to chronological order (earliest first)
        bars.reverse()

        print(f"\nData Range:")
        if bars:
            print(f"  First bar: {bars[0]['datetime_et']} | Price: {bars[0]['close']:.2f}")
            print(f"  Last bar:  {bars[-1]['datetime_et']} | Price: {bars[-1]['close']:.2f}")

        return bars

    except Exception as e:
        print(f"Error fetching data from Alpha Vantage: {e}")
        print("Note: Alpha Vantage has rate limits. Free tier: 5 calls/min, 500/day")
        return []


def filter_market_hours(bars: list, start_hour: int = 9, start_min: int = 30,
                       end_hour: int = 16, end_min: int = 0) -> list:
    """
    Filter bars to market hours only (9:30 AM - 4:00 PM ET by default)

    Args:
        bars: List of OHLCV bars
        start_hour, start_min: Market open time (default 9:30)
        end_hour, end_min: Market close time (default 16:00 / 4:00 PM)

    Returns:
        Filtered list of bars within market hours
    """

    filtered = []
    for bar in bars:
        hour = bar['hour_et']
        minute = bar['minute_et']

        # Check if bar is within market hours
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        bar_minutes = hour * 60 + minute

        if start_minutes <= bar_minutes <= end_minutes:
            filtered.append(bar)

    print(f"\nMarket Hours Filter (9:30 AM - 4:00 PM ET):")
    print(f"  Original bars: {len(bars)}")
    print(f"  After filter:  {len(filtered)}")

    return filtered


def analyze_daily_sessions(bars: list) -> dict:
    """
    Analyze bars by trading day
    """

    sessions = {}
    for bar in bars:
        date_key = bar['datetime'][:10]  # YYYY-MM-DD

        if date_key not in sessions:
            sessions[date_key] = {
                'bars': [],
                'open_time': None,
                'close_time': None,
                'open_price': None,
                'close_price': None
            }

        sessions[date_key]['bars'].append(bar)
        if sessions[date_key]['open_time'] is None:
            sessions[date_key]['open_time'] = bar['datetime_et']
            sessions[date_key]['open_price'] = bar['open']
        sessions[date_key]['close_time'] = bar['datetime_et']
        sessions[date_key]['close_price'] = bar['close']

    print(f"\nDaily Sessions Analysis:")
    print(f"  Trading days: {len(sessions)}")

    for date_key in sorted(sessions.keys()):
        session = sessions[date_key]
        print(f"  {date_key}: {len(session['bars'])} bars | {session['open_time']} to {session['close_time']}")

    return sessions


def save_bars_to_json(bars: list, filename: str = "alpha_vantage_backtest_data.json"):
    """Save bars to JSON file for backtesting"""

    output_path = f"C:/Case Capital/Axiom day trading/{filename}"
    try:
        with open(output_path, 'w') as f:
            json.dump(bars, f, indent=2)
        print(f"\n✓ Data saved to {filename} ({len(bars)} bars)")
        return output_path
    except Exception as e:
        print(f"Error saving data: {e}")
        return None


if __name__ == "__main__":
    print("="*80)
    print("ALPHA VANTAGE DATA FETCHER FOR ORB BACKTESTING")
    print("="*80)

    # Fetch 5-minute intraday data for SPY
    symbol = "SPY"
    interval = "5min"

    bars = fetch_intraday_data(symbol, interval)

    if bars:
        # Filter to market hours
        filtered_bars = filter_market_hours(bars)

        # Analyze daily sessions
        sessions = analyze_daily_sessions(filtered_bars)

        # Save for backtesting
        if filtered_bars:
            save_bars_to_json(filtered_bars, f"alpha_vantage_{symbol}_5min.json")
            print(f"\n✓ Ready for backtesting: {len(filtered_bars)} bars of {symbol} 5-min data")
        else:
            print("\n❌ No market hours data available")
    else:
        print("\n❌ Failed to fetch data from Alpha Vantage")
        print("   Check API key and rate limits")
