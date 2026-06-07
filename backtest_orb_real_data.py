"""
ORB Strategy Backtest on Real 5-Minute SPY Data from Yahoo Finance
Uses timezone-corrected backtester with actual market data
"""

import json
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from backtest_orb_fixed import ORBBacktesterFixed

def load_backtest_data(filename: str) -> list:
    """Load OHLCV data from JSON file"""
    try:
        with open(f"C:/Case Capital/Axiom day trading/{filename}", 'r') as f:
            data = json.load(f)
        print(f"[OK] Loaded {len(data)} bars from {filename}")
        return data
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filename}")
        return []

def convert_to_backtest_format(data: list) -> list:
    """Convert JSON data to backtest format"""
    bars = []
    for bar_data in data:
        dt = datetime.utcfromtimestamp(bar_data['time'])

        bar = {
            'time': bar_data['time'],
            'dt': dt,
            'open': bar_data['open'],
            'high': bar_data['high'],
            'low': bar_data['low'],
            'close': bar_data['close'],
            'volume': bar_data['volume']
        }
        bars.append(bar)

    return bars

if __name__ == "__main__":
    print("="*80)
    print("ORB STRATEGY BACKTEST - REAL 5-MINUTE SPY DATA")
    print("="*80)

    # Load real data
    data = load_backtest_data("yfinance_SPY_5min_marketHours.json")

    if not data:
        print("Failed to load data. Exiting.")
        sys.exit(1)

    # Convert to backtest format
    bars = convert_to_backtest_format(data)

    print(f"\nData Summary:")
    print(f"  Total bars: {len(bars)}")
    print(f"  First bar: {bars[0]['dt'].isoformat()} UTC")
    print(f"  Last bar:  {bars[-1]['dt'].isoformat()} UTC")

    # Analyze daily sessions
    print(f"\nDaily Sessions Summary:")
    sessions = {}
    for bar in bars:
        from datetime import timedelta
        et_dt = bar['dt'] - timedelta(hours=4)  # UTC to ET
        date_key = et_dt.strftime('%Y-%m-%d')

        if date_key not in sessions:
            sessions[date_key] = {'count': 0, 'orb_open': None}
        sessions[date_key]['count'] += 1
        if sessions[date_key]['orb_open'] is None:
            sessions[date_key]['orb_open'] = et_dt.strftime('%H:%M ET')

    print(f"  Trading days: {len(sessions)}")
    for date_key in sorted(list(sessions.keys())[:5]):
        s = sessions[date_key]
        print(f"    {date_key}: {s['count']} bars, ORB opens at {s['orb_open']}")
    print(f"    ... ({len(sessions)-5} more days)")

    # Run backtest
    print(f"\n{'='*80}")
    print("RUNNING ORB BACKTEST")
    print(f"{'='*80}\n")

    bt = ORBBacktesterFixed(initial_equity=100000)

    # Run the backtest
    bt.run_backtest(bars)
    metrics = bt.get_metrics()

    # Print results
    print(f"\n{'='*80}")
    print("BACKTEST RESULTS - REAL DATA")
    print(f"{'='*80}")
    print(f"\nStrategy Metrics:")
    print(f"  Total Trades:    {metrics['total_trades']}")
    print(f"  Win Rate:        {metrics['win_rate']}%")
    print(f"  Profit Factor:   {metrics['profit_factor']:.2f}")
    print(f"  Max Drawdown:    {metrics['max_drawdown']}%")
    print(f"  Net P&L:         ${metrics['net_pnl']:.2f}")
    print(f"  Avg Trade:       ${metrics['avg_trade']:.2f}")

    # Trade validation
    print(f"\nValidation Against Requirements:")
    print(f"  Min Win Rate (55%+):     {'PASS' if metrics['win_rate'] >= 55 else 'FAIL'} ({metrics['win_rate']}%)")
    print(f"  Min Profit Factor (1.3+): {'PASS' if metrics['profit_factor'] >= 1.3 else 'FAIL'} ({metrics['profit_factor']:.2f})")
    print(f"  Positive P&L:             {'PASS' if metrics['net_pnl'] > 0 else 'FAIL'} (${metrics['net_pnl']:.2f})")

    # Trade frequency
    if len(sessions) > 0 and metrics['total_trades'] > 0:
        trades_per_day = metrics['total_trades'] / len(sessions)
        print(f"\nTrade Frequency:")
        print(f"  Total trading days: {len(sessions)}")
        print(f"  Total trades:       {metrics['total_trades']}")
        print(f"  Trades per day:     {trades_per_day:.2f}")
        print(f"  Expected (1 per day): {'PASS' if trades_per_day >= 0.8 else 'NEED MORE DATA'}")

    # Detailed trades
    if metrics['total_trades'] > 0:
        print(f"\n{'='*80}")
        print("INDIVIDUAL TRADES")
        print(f"{'='*80}")
        print(f"\n{'#':<3} {'Date':<12} {'Time':<9} {'Side':<6} {'Entry':<8} {'Exit':<8} {'P&L':<10} {'Status':<8}")
        print("-" * 80)

        for i, trade in enumerate(bt.trades[:20], 1):
            entry_dt = bt.utc_to_et(trade['entry_time'])
            exit_dt = bt.utc_to_et(trade['exit_time'])
            status = "WIN" if trade['pnl'] > 0 else "LOSS" if trade['pnl'] < 0 else "BREAK"
            print(f"{i:<3} {entry_dt.strftime('%Y-%m-%d'):<12} {entry_dt.strftime('%H:%M'):<9} {trade['side'].upper():<6} {trade['entry']:<8.2f} {trade['exit_price']:<8.2f} ${trade['pnl']:<9.2f} {status:<8}")

        if len(bt.trades) > 20:
            print(f"\n... ({len(bt.trades) - 20} more trades)")

    print(f"\n{'='*80}")

    # Overall status
    print(f"\nBacktest Status: {'READY FOR LIVE TRADING' if all([
        metrics['win_rate'] >= 55,
        metrics['profit_factor'] >= 1.3,
        metrics['net_pnl'] > 0
    ]) else 'NEEDS OPTIMIZATION'}")

    print(f"\n{'='*80}\n")
