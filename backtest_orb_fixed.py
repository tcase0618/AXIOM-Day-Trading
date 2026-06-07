"""
CORRECTED ORB BACKTESTER - FIXES TIMEZONE BUG
TradingView API returns UTC timestamps
Must convert to ET (Eastern Time) for session detection
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict

class ORBBacktesterFixed:
    def __init__(self, initial_equity=100000):
        self.initial_equity = initial_equity
        self.equity = initial_equity

        # Strategy parameters
        self.MAX_TRADES_PER_SESSION = 2
        self.ATR_PERIOD = 14
        self.RSI_PERIOD = 14
        self.TIME_EXIT_BARS = 20

        # Results tracking
        self.trades = []
        self.current_trade = None
        self.daily_trades_count = defaultdict(int)

        # ORB state per day
        self.daily_orb = {}

    def utc_to_et(self, utc_dt):
        """Convert UTC datetime to ET (Eastern Time)"""
        # In June 2026, EDT (UTC-4) is in effect
        et_dt = utc_dt - timedelta(hours=4)
        return et_dt

    def calculate_atr(self, bars, period=14):
        """Calculate Average True Range"""
        if len(bars) < period:
            return 0

        tr_values = []
        for i in range(len(bars) - period, len(bars)):
            bar = bars[i]
            tr = max(
                bar['high'] - bar['low'],
                abs(bar['high'] - bars[i-1]['close']),
                abs(bar['low'] - bars[i-1]['close'])
            )
            tr_values.append(tr)

        return sum(tr_values) / len(tr_values)

    def calculate_rsi(self, closes, period=14):
        """Calculate Relative Strength Index"""
        if len(closes) < period + 1:
            return 50

        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def process_bar(self, bar, bar_index, all_bars):
        """Process a single bar with CORRECTED timezone handling"""
        utc_dt = bar['dt']
        et_dt = self.utc_to_et(utc_dt)

        et_hour = et_dt.hour
        et_minute = et_dt.minute
        date_key = et_dt.strftime('%Y-%m-%d')

        # Session times in ET
        in_session = (et_hour == 9 and et_minute >= 30) or (10 <= et_hour <= 15)
        orb_forming = (et_hour == 9 and 30 <= et_minute < 45)
        orb_formed_time = (et_hour == 9 and et_minute >= 45)

        # Initialize daily ORB
        if date_key not in self.daily_orb:
            self.daily_orb[date_key] = {
                'orb_high': None,
                'orb_low': None,
                'orb_formed': False,
                'bars_in_session': []
            }

        # Build ORB range during 9:30-9:45 ET
        if orb_forming:
            if self.daily_orb[date_key]['orb_high'] is None:
                self.daily_orb[date_key]['orb_high'] = bar['high']
                self.daily_orb[date_key]['orb_low'] = bar['low']
            else:
                self.daily_orb[date_key]['orb_high'] = max(self.daily_orb[date_key]['orb_high'], bar['high'])
                self.daily_orb[date_key]['orb_low'] = min(self.daily_orb[date_key]['orb_low'], bar['low'])

            self.daily_orb[date_key]['bars_in_session'].append(bar_index)

        # Mark ORB as formed after 9:45 ET
        if orb_formed_time and not self.daily_orb[date_key]['orb_formed']:
            self.daily_orb[date_key]['orb_formed'] = True

        # Time exit
        if self.current_trade and self.current_trade['bars_held'] >= self.TIME_EXIT_BARS:
            self.close_trade(bar['close'], "Time Exit", utc_dt)

        # Process exits
        if self.current_trade:
            self.current_trade['bars_held'] += 1

            if self.current_trade['side'] == 'long':
                if bar['low'] <= self.current_trade['stop']:
                    self.close_trade(self.current_trade['stop'], "Stop", utc_dt)
                elif bar['high'] >= self.current_trade['target']:
                    self.close_trade(self.current_trade['target'], "Target", utc_dt)
            elif self.current_trade['side'] == 'short':
                if bar['high'] >= self.current_trade['stop']:
                    self.close_trade(self.current_trade['stop'], "Stop", utc_dt)
                elif bar['low'] <= self.current_trade['target']:
                    self.close_trade(self.current_trade['target'], "Target", utc_dt)

        # Entry signals
        if (not self.current_trade and in_session and
            self.daily_orb[date_key]['orb_formed'] and
            self.daily_trades_count[date_key] < self.MAX_TRADES_PER_SESSION):

            closes = [b['close'] for b in all_bars[:bar_index+1]]
            rsi = self.calculate_rsi(closes)
            atr = self.calculate_atr(all_bars[:bar_index+1])

            orb_h = self.daily_orb[date_key]['orb_high']
            orb_l = self.daily_orb[date_key]['orb_low']

            # Long: breakout above ORB high
            if bar['close'] > orb_h and rsi > 50 and atr > 0:
                entry = bar['close']
                stop = entry - (atr * 1.5)
                target = entry + (atr * 3.0)
                self.open_trade('long', entry, stop, target, utc_dt)
                self.daily_trades_count[date_key] += 1

            # Short: breakout below ORB low
            elif bar['close'] < orb_l and rsi < 50 and atr > 0:
                entry = bar['close']
                stop = entry + (atr * 1.5)
                target = entry - (atr * 3.0)
                self.open_trade('short', entry, stop, target, utc_dt)
                self.daily_trades_count[date_key] += 1

    def open_trade(self, side, entry, stop, target, time):
        self.current_trade = {
            'side': side,
            'entry': entry,
            'stop': stop,
            'target': target,
            'entry_time': time,
            'exit_time': None,
            'exit_price': None,
            'exit_reason': None,
            'bars_held': 0
        }

    def close_trade(self, exit_price, reason, time):
        if not self.current_trade:
            return

        pnl = 0
        if self.current_trade['side'] == 'long':
            pnl = exit_price - self.current_trade['entry']
        else:
            pnl = self.current_trade['entry'] - exit_price

        self.current_trade['exit_price'] = exit_price
        self.current_trade['exit_reason'] = reason
        self.current_trade['exit_time'] = time
        self.current_trade['pnl'] = pnl

        self.trades.append(self.current_trade)
        self.equity += pnl
        self.current_trade = None

    def run_backtest(self, bars):
        for i, bar in enumerate(bars):
            self.process_bar(bar, i, bars)

        if self.current_trade and len(bars) > 0:
            self.close_trade(bars[-1]['close'], "End of Data", bars[-1]['dt'])

    def get_metrics(self):
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'net_pnl': 0,
                'avg_trade': 0
            }

        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]

        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

        total_wins = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        net_pnl = self.equity - self.initial_equity

        # Calculate max drawdown
        eq_curve = [self.initial_equity]
        for trade in self.trades:
            eq_curve.append(eq_curve[-1] + trade['pnl'])

        peak = eq_curve[0]
        max_dd = 0
        for eq in eq_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)

        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_dd, 2),
            'net_pnl': round(net_pnl, 2),
            'avg_trade': round(net_pnl / total_trades, 2) if total_trades > 0 else 0
        }

# Run backtest
if __name__ == '__main__':
    bars_raw = [
        {"time": 1780599600},  # Will be filled in by calling script
    ]
    print("ORBBacktesterFixed ready")
