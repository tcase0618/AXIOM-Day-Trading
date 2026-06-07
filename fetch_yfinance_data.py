"""
Fetch real 5-minute intraday data using yfinance (free, unlimited)
Filters to market hours (9:30 AM - 4:00 PM ET) for ORB backtesting
"""

import json
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# Timezone handling
et = pytz.timezone('US/Eastern')
utc = pytz.UTC


def fetch_intraday_data(symbol: str, interval: str = "5m", period: str = "60d") -> list:
    """
    Fetch intraday data using yfinance (FREE, no API key needed)

    Args:
        symbol: Stock symbol (e.g., "SPY", "QQQ", "IVV")
        interval: "1m", "5m", "15m", "60m"
        period: "5d", "30d", "60d", "1y"

    Returns:
        List of bars with OHLCV data in chronological order
    """

    print(f"\nFetching {symbol} {interval} data from Yahoo Finance...")
    print(f"Period: {period}")

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(interval=interval, period=period)

        print(f"Data fetched: {len(hist)} bars available")

        # Convert to bar list
        bars = []
        for idx, (date, row) in enumerate(hist.iterrows()):
            try:
                # yfinance returns data in market timezone (ET for US stocks)
                dt_et = date.tz_localize('US/Eastern') if date.tz is None else date.astimezone(et)

                # Convert to UTC for consistent storage
                dt_utc = dt_et.astimezone(utc)

                bar = {
                    'time': int(dt_utc.timestamp()),  # Unix timestamp
                    'datetime': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'datetime_et': dt_et.strftime('%Y-%m-%d %H:%M:%S ET'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'hour_et': dt_et.hour,
                    'minute_et': dt_et.minute
                }
                bars.append(bar)

            except Exception as e:
                print(f"Error parsing row {date}: {e}")
                continue

        if bars:
            print(f"\n[OK] Data Range:")
            print(f"  First bar: {bars[0]['datetime_et']} | Close: {bars[0]['close']:.2f}")
            print(f"  Last bar:  {bars[-1]['datetime_et']} | Close: {bars[-1]['close']:.2f}")
            print(f"  Total bars: {len(bars)}")

        return bars

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def filter_market_hours(bars: list, start_hour: int = 9, start_min: int = 30,
                       end_hour: int = 16, end_min: int = 0) -> list:
    """
    Filter bars to market hours only (9:30 AM - 4:00 PM ET)
    Removes pre-market and after-hours data
    """

    filtered = []
    for bar in bars:
        hour = bar['hour_et']
        minute = bar['minute_et']

        # Only include bars during market hours
        start_mins = start_hour * 60 + start_min
        end_mins = end_hour * 60 + end_min
        bar_mins = hour * 60 + minute

        if start_mins <= bar_mins <= end_mins:
            filtered.append(bar)

    print(f"\nMarket Hours Filter (9:30 AM - 4:00 PM ET):")
    print(f"  Original:  {len(bars)} bars")
    print(f"  Filtered:  {len(filtered)} bars ({100*len(filtered)/len(bars):.1f}% retained)")

    return filtered


def analyze_daily_sessions(bars: list) -> dict:
    """Analyze bars by trading day to verify complete sessions"""

    sessions = {}
    for bar in bars:
        date_key = bar['datetime'][:10]

        if date_key not in sessions:
            sessions[date_key] = {
                'count': 0,
                'first_bar_time': None,
                'last_bar_time': None,
                'open_price': None,
                'high': 0,
                'low': float('inf'),
                'close_price': None
            }

        sessions[date_key]['count'] += 1
        if sessions[date_key]['first_bar_time'] is None:
            sessions[date_key]['first_bar_time'] = bar['datetime_et']
            sessions[date_key]['open_price'] = bar['open']
        sessions[date_key]['last_bar_time'] = bar['datetime_et']
        sessions[date_key]['close_price'] = bar['close']
        sessions[date_key]['high'] = max(sessions[date_key]['high'], bar['high'])
        sessions[date_key]['low'] = min(sessions[date_key]['low'], bar['low'])

    print(f"\nDaily Trading Sessions:")
    print(f"  Total days: {len(sessions)}")
    print(f"  {'Date':<12} {'Bars':>5} {'Open Time':<17} {'Close Time':<17}")
    print(f"  {'-'*60}")

    for date_key in sorted(sessions.keys()):
        s = sessions[date_key]
        print(f"  {date_key}  {s['count']:>5}   {s['first_bar_time']:<17} {s['last_bar_time']:<17}")

    # Check for complete market open data
    has_market_open = any(
        s['first_bar_time'] and '09:30' in s['first_bar_time']
        for s in sessions.values()
    )

    print(f"\n  ORB Ready: {'[OK] YES' if has_market_open else '[NO] NO'} (9:30 AM data present)")

    return sessions


def save_bars_to_json(bars: list, filename: str = "backtest_data.json"):
    """Save bars to JSON for backtesting"""

    output_path = f"C:/Case Capital/Axiom day trading/{filename}"
    try:
        with open(output_path, 'w') as f:
            json.dump(bars, f, indent=2)
        print(f"\n[OK] Data saved: {filename}")
        print(f"  Location: {output_path}")
        print(f"  Size: {len(bars)} bars")
        return output_path
    except Exception as e:
        print(f"Error saving data: {e}")
        return None


if __name__ == "__main__":
    print("="*80)
    print("YFINANCE DATA FETCHER - 5MIN ORB BACKTESTING")
    print("="*80)

    # Fetch 5-minute data for SPY (S&P 500 ETF)
    symbol = "SPY"
    interval = "5m"
    period = "60d"  # 60 days of data

    print(f"\nFetching {symbol} 5-minute data for ORB backtesting...")
    print(f"Target: {period} of historical data with complete market open sessions")

    bars = fetch_intraday_data(symbol, interval, period)

    if bars:
        # Filter to market hours
        print("\nApplying market hours filter...")
        filtered_bars = filter_market_hours(bars)

        if filtered_bars:
            # Analyze sessions
            sessions = analyze_daily_sessions(filtered_bars)

            # Save data
            json_file = save_bars_to_json(filtered_bars, "yfinance_SPY_5min_marketHours.json")

            if json_file:
                print(f"\n{'='*80}")
                print(f"SUCCESS: Ready for ORB backtest")
                print(f"  Symbol: {symbol}")
                print(f"  Timeframe: 5-minute")
                print(f"  Bars: {len(filtered_bars)}")
                print(f"  Trading days: {len(sessions)}")
                print(f"  File: {json_file}")
                print(f"{'='*80}\n")
        else:
            print("No market hours data found")
    else:
        print("Failed to fetch data")
