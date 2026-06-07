"""
FUTURES ORB US OPEN BACKTESTER
Implements the strategy logic from futures_orb_us_open.pine in Python
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict

class ORBBacktester:
    def __init__(self, initial_equity=100000, risk_per_trade=0.01):
        self.initial_equity = initial_equity
        self.equity = initial_equity
        self.risk_per_trade = risk_per_trade

        # Strategy parameters
        self.MAX_TRADES_PER_SESSION = 2
        self.ATR_PERIOD = 14
        self.RSI_PERIOD = 14
        self.MIN_BOS_MOVE = 4.0  # Min 4 points for ES1!
        self.MIN_VOLUME_MULT = 1.5
        self.TIME_EXIT_BARS = 20  # 100 minutes at 5-min bars

        # Results tracking
        self.trades = []
        self.current_trade = None
        self.daily_trades_count = defaultdict(int)

        # ORB state
        self.orb_high = None
        self.orb_low = None
        self.orb_formed = False
        self.session_start = None
        self.bars_in_trade = 0

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
        """Process a single bar and update strategy state"""
        bar_time = bar['time']
        hour = datetime.fromisoformat(bar_time).hour
        minute = datetime.fromisoformat(bar_time).minute

        # Eastern Time session check (9:30am - 3:45pm ET)
        in_session = (hour == 9 and minute >= 30) or (10 <= hour <= 15)

        # ORB Formation: 9:30-9:45 ET
        orb_forming = (hour == 9 and 30 <= minute < 45)
        orb_formed_time = (hour == 9 and minute >= 45)

        # Reset ORB at session start
        if hour == 9 and minute == 30:
            self.orb_high = bar['high']
            self.orb_low = bar['low']
            self.orb_formed = False
            self.bars_in_trade = 0

        # Build ORB range
        if orb_forming:
            self.orb_high = max(self.orb_high or bar['high'], bar['high'])
            self.orb_low = min(self.orb_low or bar['low'], bar['low'])

        # Mark ORB as formed
        if orb_formed_time and not self.orb_formed:
            self.orb_formed = True

        # Close position on time exit
        if self.current_trade and self.bars_in_trade >= self.TIME_EXIT_BARS:
            self.close_trade(bar['close'], "Time Exit", bar_time)

        # Process exits if we have a position
        if self.current_trade:
            self.bars_in_trade += 1

            if self.current_trade['side'] == 'long':
                # Exit on stop
                if bar['low'] <= self.current_trade['stop']:
                    self.close_trade(self.current_trade['stop'], "Stop", bar_time)
                # Exit on target
                elif bar['high'] >= self.current_trade['target']:
                    self.close_trade(self.current_trade['target'], "Target", bar_time)

            elif self.current_trade['side'] == 'short':
                # Exit on stop
                if bar['high'] >= self.current_trade['stop']:
                    self.close_trade(self.current_trade['stop'], "Stop", bar_time)
                # Exit on target
                elif bar['low'] <= self.current_trade['target']:
                    self.close_trade(self.current_trade['target'], "Target", bar_time)

        # Entry signals (only in session, after ORB formed)
        if not self.current_trade and in_session and self.orb_formed:
            closes = [b['close'] for b in all_bars[:bar_index+1]]
            rsi = self.calculate_rsi(closes)
            atr = self.calculate_atr(all_bars[:bar_index+1])

            daily_key = bar_time.split('T')[0]
            session_trades = self.daily_trades_count[daily_key]

            # Long entry: Breakout above ORB high with RSI > 50
            if (bar['close'] > self.orb_high and
                rsi > 50 and
                session_trades < self.MAX_TRADES_PER_SESSION):

                entry_price = bar['close']
                stop = entry_price - (atr * 1.5)
                target = entry_price + (atr * 3.0)

                self.open_trade('long', entry_price, stop, target, bar_time)
                self.daily_trades_count[daily_key] += 1

            # Short entry: Breakout below ORB low with RSI < 50
            elif (bar['close'] < self.orb_low and
                  rsi < 50 and
                  session_trades < self.MAX_TRADES_PER_SESSION):

                entry_price = bar['close']
                stop = entry_price + (atr * 1.5)
                target = entry_price - (atr * 3.0)

                self.open_trade('short', entry_price, stop, target, bar_time)
                self.daily_trades_count[daily_key] += 1

    def open_trade(self, side, entry, stop, target, time):
        """Open a new trade"""
        self.current_trade = {
            'side': side,
            'entry': entry,
            'stop': stop,
            'target': target,
            'entry_time': time,
            'exit_time': None,
            'exit_price': None,
            'exit_reason': None
        }
        self.bars_in_trade = 0

    def close_trade(self, exit_price, reason, time):
        """Close current trade and record result"""
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
        self.current_trade['pnl_pct'] = (pnl / self.current_trade['entry']) * 100

        self.trades.append(self.current_trade)
        self.equity += pnl
        self.current_trade = None

    def run_backtest(self, bars):
        """Run the backtest on all bars"""
        for i, bar in enumerate(bars):
            self.process_bar(bar, i, bars)

        # Close any open position at end
        if self.current_trade and len(bars) > 0:
            self.close_trade(bars[-1]['close'], "End of Data", bars[-1]['time'])

    def get_metrics(self):
        """Calculate backtest metrics"""
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

        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
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
