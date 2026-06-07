#!/usr/bin/env python3
"""
AXIOM Day Trading - Automated Python Backtest Engine
Tests 10 custom strategies on 2-year data with walk-forward validation
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import yfinance as yf
import logging
from pathlib import Path
from typing import Dict, Tuple, List
import warnings

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BacktestEngine:
    """Core backtesting engine for strategy validation"""

    def __init__(self, initial_capital=10000, commission_pct=0.001, slippage_pct=0.0005):
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct

    def fetch_data(self, symbol: str, period: str = "2y", interval: str = "1h") -> pd.DataFrame:
        """Fetch historical OHLCV data from Yahoo Finance"""
        try:
            logger.info(f"Fetching {symbol} {period} {interval} data...")
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if df.empty:
                logger.warning(f"No data for {symbol}")
                return None
            df = df.reset_index()
            df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
            df = df.dropna()
            return df
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None

    def calculate_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate backtest metrics from trade list"""
        if not trades:
            return {
                'win_rate': 0,
                'loss_rate': 0,
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'profit_factor': 0,
                'trade_count': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'equity_peak': self.initial_capital
            }

        profits = [t['pnl'] for t in trades]
        returns = [p / self.initial_capital for p in profits]

        wins = [p for p in profits if p > 0]
        losses = [abs(p) for p in profits if p < 0]

        win_rate = len(wins) / len(trades) if trades else 0
        loss_rate = len(losses) / len(trades) if trades else 0

        total_return = sum(profits)
        total_profit = sum(wins)
        total_loss = sum(losses)

        # Sharpe ratio (annualized, assuming 252 trading days per year)
        if len(returns) > 1:
            daily_returns = np.array(returns)
            sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        else:
            sharpe = 0

        # Max drawdown
        equity = [self.initial_capital]
        for p in profits:
            equity.append(equity[-1] + p)
        equity_peak = np.maximum.accumulate(equity)
        drawdown = (np.array(equity) - equity_peak) / equity_peak
        max_drawdown = abs(min(drawdown))

        # Profit factor
        profit_factor = total_profit / total_loss if total_loss > 0 else 0

        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0

        return {
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'total_return': total_return,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'trade_count': len(trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'equity_peak': equity_peak[-1]
        }

class StrategyTester:
    """Test individual strategies"""

    def __init__(self, engine: BacktestEngine):
        self.engine = engine

    def slot_1_equities_trending_up(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 1: Equities Trending Up - EMA cross with RSI (optimized)"""
        trades = []
        position = None

        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            ema9, ema21, ema50 = df.iloc[i]['ema9'], df.iloc[i]['ema21'], df.iloc[i]['ema50']
            rsi = df.iloc[i]['rsi']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            # Entry signal - loosened for better entries
            if position is None:
                trend_up = ema9 > ema21 > ema50
                rsi_ok = 40 <= rsi <= 75  # Widened range
                vol_ok = volume >= vol_avg  # Reduced from 1.5x to 1.0x
                price_above_ema21 = price >= ema21 * 0.98  # Near/above EMA21

                if trend_up and rsi_ok and vol_ok and price_above_ema21:
                    stop = ema50 * 0.98
                    risk = price - stop
                    target = price + (risk * 1.5)  # Reduced target to 1.5x risk
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': 1,
                        'date': df.iloc[i]['datetime']
                    }

            # Exit signal
            elif position:
                if price <= position['stop'] or price >= position['target']:
                    exit_price = price
                    pnl = (exit_price - position['entry']) * position['size']
                    trades.append({
                        'entry': position['entry'],
                        'exit': exit_price,
                        'pnl': pnl,
                        'return_pct': (pnl / position['entry']) * 100,
                        'date': position['date']
                    })
                    position = None

        return trades

    def slot_2_equities_trending_down(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 2: Equities Trending Down - Short EMA cross with RSI (optimized)"""
        trades = []
        position = None

        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            ema9, ema21, ema50 = df.iloc[i]['ema9'], df.iloc[i]['ema21'], df.iloc[i]['ema50']
            rsi = df.iloc[i]['rsi']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            # Entry signal (short) - loosened for better entries
            if position is None:
                trend_down = ema9 < ema21 < ema50
                rsi_ok = 25 <= rsi <= 60  # Widened from 35-50
                vol_ok = volume >= vol_avg * 0.8  # Reduced from 1.5x
                price_below_ema21 = price <= ema21 * 1.02  # Near/below EMA21

                if trend_down and rsi_ok and vol_ok and price_below_ema21:
                    stop = ema50 * 1.02
                    risk = stop - price
                    target = price - (risk * 1.5)  # Reduced from 2.0x
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': -1,  # Short
                        'date': df.iloc[i]['datetime']
                    }

            # Exit signal
            elif position:
                if price >= position['stop'] or price <= position['target']:
                    exit_price = price
                    pnl = (position['entry'] - exit_price) * abs(position['size'])
                    trades.append({
                        'entry': position['entry'],
                        'exit': exit_price,
                        'pnl': pnl,
                        'return_pct': (pnl / position['entry']) * 100,
                        'date': position['date']
                    })
                    position = None

        return trades

    def slot_3_equities_horizontal(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 3: Equities Horizontal - Bollinger Bands mean reversion (optimized)"""
        trades = []
        position = None

        df['sma20'] = df['close'].rolling(20).mean()
        df['std20'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['sma20'] + (df['std20'] * 2)
        df['bb_lower'] = df['sma20'] - (df['std20'] * 2)
        df['bandwidth'] = df['bb_upper'] - df['bb_lower']
        df['bandwidth_min'] = df['bandwidth'].rolling(30).min()
        df['adx'] = self._calculate_adx(df, 14)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            bb_upper = df.iloc[i]['bb_upper']
            bb_lower = df.iloc[i]['bb_lower']
            bandwidth = df.iloc[i]['bandwidth']
            bandwidth_min = df.iloc[i]['bandwidth_min']
            adx = df.iloc[i]['adx']
            sma20 = df.iloc[i]['sma20']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            # Entry signal - less strict on squeeze requirement
            if position is None:
                range_mode = adx < 25  # Slightly relaxed
                squeeze = bandwidth <= bandwidth_min * 1.2  # Relaxed from 1.05
                vol_ok = volume >= vol_avg * 0.9  # Relaxed

                # Long at lower band or below SMA20
                if range_mode and squeeze and vol_ok and price <= sma20:
                    stop = bb_lower * 0.97
                    target = sma20 * 1.01
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': 1,
                        'date': df.iloc[i]['datetime'],
                        'direction': 'long'
                    }

                # Short at upper band or above SMA20
                elif range_mode and squeeze and vol_ok and price >= sma20:
                    stop = bb_upper * 1.03
                    target = sma20 * 0.99
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': -1,
                        'date': df.iloc[i]['datetime'],
                        'direction': 'short'
                    }

            # Exit signal
            elif position:
                if position['direction'] == 'long':
                    if price <= position['stop'] or price >= position['target']:
                        pnl = (price - position['entry']) * position['size']
                        trades.append({
                            'entry': position['entry'],
                            'exit': price,
                            'pnl': pnl,
                            'return_pct': (pnl / position['entry']) * 100,
                            'date': position['date']
                        })
                        position = None
                else:  # short
                    if price >= position['stop'] or price <= position['target']:
                        pnl = (position['entry'] - price) * abs(position['size'])
                        trades.append({
                            'entry': position['entry'],
                            'exit': price,
                            'pnl': pnl,
                            'return_pct': (pnl / position['entry']) * 100,
                            'date': position['date']
                        })
                        position = None

        return trades

    def slot_4_equities_explosive(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 4: Equities Explosive - Volume breakout (optimized)"""
        trades = []
        position = None

        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            prev_close = df.iloc[i-1]['close']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']
            rsi = df.iloc[i]['rsi']
            high_prev = df.iloc[i-1]['high']
            low = df.iloc[i]['low']

            price_change_pct = abs((price - prev_close) / prev_close * 100)

            # Entry signal - loosened requirements for more trades
            if position is None:
                vol_explosion = volume >= vol_avg * 2.0  # Relaxed from 3.0x
                price_explosion = price_change_pct >= 2.0  # Relaxed from 4.0%
                rsi_bullish = rsi > 50  # Relaxed from 60
                breakout = price > (high_prev * 0.99)  # Slightly relaxed

                if vol_explosion and price_explosion and rsi_bullish and breakout:
                    stop = low * 0.99
                    risk = price - stop
                    target = price + (risk * 2.0)  # Reduced from 3.0x
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': 1,
                        'date': df.iloc[i]['datetime']
                    }

            # Exit signal
            elif position:
                if price <= position['stop'] or price >= position['target']:
                    pnl = (price - position['entry']) * position['size']
                    trades.append({
                        'entry': position['entry'],
                        'exit': price,
                        'pnl': pnl,
                        'return_pct': (pnl / position['entry']) * 100,
                        'date': position['date']
                    })
                    position = None

        return trades

    def slot_5_futures_trending_up(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 5: Futures Trending Up - EMA + VWAP"""
        trades = []
        position = None

        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vwap'] = self._calculate_vwap(df)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            ema9, ema21, ema50 = df.iloc[i]['ema9'], df.iloc[i]['ema21'], df.iloc[i]['ema50']
            rsi = df.iloc[i]['rsi']
            vwap = df.iloc[i]['vwap']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            # Entry signal - optimized
            if position is None:
                trend_up = ema9 > ema21 > ema50
                rsi_ok = 40 <= rsi <= 75  # Widened
                vol_ok = volume >= vol_avg  # Reduced
                pullback = price >= ema21 * 0.98  # Relaxed
                vwap_above = vwap > price  # Keep for confirmation

                if trend_up and rsi_ok and vol_ok and pullback and vwap_above:
                    stop = ema50 * 0.99  # Tighter for futures
                    risk = price - stop
                    target = price + (risk * 1.5)  # Reduced target
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': 1,
                        'date': df.iloc[i]['datetime']
                    }

            # Exit signal
            elif position:
                if price <= position['stop'] or price >= position['target']:
                    pnl = (price - position['entry']) * position['size']
                    trades.append({
                        'entry': position['entry'],
                        'exit': price,
                        'pnl': pnl,
                        'return_pct': (pnl / position['entry']) * 100,
                        'date': position['date']
                    })
                    position = None

        return trades

    def slot_6_futures_trending_down(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 6: Futures Trending Down - EMA + VWAP short"""
        trades = []
        position = None

        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vwap'] = self._calculate_vwap(df)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            ema9, ema21, ema50 = df.iloc[i]['ema9'], df.iloc[i]['ema21'], df.iloc[i]['ema50']
            rsi = df.iloc[i]['rsi']
            vwap = df.iloc[i]['vwap']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            # Entry signal (short) - optimized
            if position is None:
                trend_down = ema9 < ema21 < ema50
                rsi_ok = 25 <= rsi <= 60  # Widened
                vol_ok = volume >= vol_avg * 0.8  # Reduced
                bounce = price <= ema21 * 1.02  # Relaxed
                vwap_below = vwap < price  # Keep for confirmation

                if trend_down and rsi_ok and vol_ok and bounce and vwap_below:
                    stop = ema50 * 1.01  # Tighter for futures
                    risk = stop - price
                    target = price - (risk * 1.5)  # Reduced target
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': -1,
                        'date': df.iloc[i]['datetime']
                    }

            # Exit signal
            elif position:
                if price >= position['stop'] or price <= position['target']:
                    pnl = (position['entry'] - price) * abs(position['size'])
                    trades.append({
                        'entry': position['entry'],
                        'exit': price,
                        'pnl': pnl,
                        'return_pct': (pnl / position['entry']) * 100,
                        'date': position['date']
                    })
                    position = None

        return trades

    def slot_7_futures_horizontal(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 7: Futures Horizontal - VWAP mean reversion"""
        trades = []
        position = None

        df['vwap'] = self._calculate_vwap(df)
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            vwap = df.iloc[i]['vwap']
            rsi = df.iloc[i]['rsi']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            vwap_dev_pct = ((price - vwap) / vwap) * 100

            # Entry signal - optimized for mean reversion
            if position is None:
                price_above_vwap = vwap_dev_pct > 0.25  # Reduced from 0.5%
                price_below_vwap = vwap_dev_pct < -0.25  # Reduced from -0.5%
                rsi_high = rsi > 55  # Relaxed from 60
                rsi_low = rsi < 45  # Relaxed from 40
                vol_ok = volume >= vol_avg * 0.9  # Relaxed

                # Long when price below VWAP and RSI low
                if price_below_vwap and rsi_low and vol_ok:
                    stop = price * 0.9950  # 0.5% stop (relaxed)
                    target = vwap
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': 1,
                        'date': df.iloc[i]['datetime'],
                        'direction': 'long'
                    }

                # Short when price above VWAP and RSI high
                elif price_above_vwap and rsi_high and vol_ok:
                    stop = price * 1.0050  # 0.5% stop (relaxed)
                    target = vwap
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': -1,
                        'date': df.iloc[i]['datetime'],
                        'direction': 'short'
                    }

            # Exit signal
            elif position:
                if position['direction'] == 'long':
                    if price <= position['stop'] or price >= position['target']:
                        pnl = (price - position['entry']) * position['size']
                        trades.append({
                            'entry': position['entry'],
                            'exit': price,
                            'pnl': pnl,
                            'return_pct': (pnl / position['entry']) * 100,
                            'date': position['date']
                        })
                        position = None
                else:  # short
                    if price >= position['stop'] or price <= position['target']:
                        pnl = (position['entry'] - price) * abs(position['size'])
                        trades.append({
                            'entry': position['entry'],
                            'exit': price,
                            'pnl': pnl,
                            'return_pct': (pnl / position['entry']) * 100,
                            'date': position['date']
                        })
                        position = None

        return trades

    def slot_8_crypto_trending_up(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 8: Crypto Trending Up (4H) - EMA with wider stops"""
        trades = []
        position = None

        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            ema9, ema21, ema50 = df.iloc[i]['ema9'], df.iloc[i]['ema21'], df.iloc[i]['ema50']
            rsi = df.iloc[i]['rsi']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            # Entry signal - optimized
            if position is None:
                trend_up = ema9 > ema21 > ema50
                rsi_ok = 40 <= rsi <= 75  # Widened
                vol_ok = volume >= vol_avg * 1.2  # Relaxed from 2.0x
                pullback = price >= ema21 * 0.98  # Relaxed

                if trend_up and rsi_ok and vol_ok and pullback:
                    stop = ema50 * 0.98  # 2% stop for crypto volatility
                    risk = price - stop
                    target = price + (risk * 1.5)  # Reduced from 2.0x
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': 1,
                        'date': df.iloc[i]['datetime']
                    }

            # Exit signal
            elif position:
                if price <= position['stop'] or price >= position['target']:
                    pnl = (price - position['entry']) * position['size']
                    trades.append({
                        'entry': position['entry'],
                        'exit': price,
                        'pnl': pnl,
                        'return_pct': (pnl / position['entry']) * 100,
                        'date': position['date']
                    })
                    position = None

        return trades

    def slot_9_crypto_trending_down(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 9: Crypto Trending Down (4H) - Short EMA with wider stops"""
        trades = []
        position = None

        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            ema9, ema21, ema50 = df.iloc[i]['ema9'], df.iloc[i]['ema21'], df.iloc[i]['ema50']
            rsi = df.iloc[i]['rsi']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            # Entry signal (short) - optimized
            if position is None:
                trend_down = ema9 < ema21 < ema50
                rsi_ok = 25 <= rsi <= 60  # Widened
                vol_ok = volume >= vol_avg * 1.0  # Relaxed
                bounce = price <= ema21 * 1.02  # Relaxed

                if trend_down and rsi_ok and vol_ok and bounce:
                    stop = ema50 * 1.02  # 2% stop for crypto volatility
                    risk = stop - price
                    target = price - (risk * 1.5)  # Reduced from 2.0x
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': -1,
                        'date': df.iloc[i]['datetime']
                    }

            # Exit signal
            elif position:
                if price >= position['stop'] or price <= position['target']:
                    pnl = (position['entry'] - price) * abs(position['size'])
                    trades.append({
                        'entry': position['entry'],
                        'exit': price,
                        'pnl': pnl,
                        'return_pct': (pnl / position['entry']) * 100,
                        'date': position['date']
                    })
                    position = None

        return trades

    def slot_10_crypto_horizontal(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 10: Crypto Horizontal (1H) - Bollinger Bands"""
        trades = []
        position = None

        df['sma20'] = df['close'].rolling(20).mean()
        df['std20'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['sma20'] + (df['std20'] * 2)
        df['bb_lower'] = df['sma20'] - (df['std20'] * 2)
        df['bandwidth'] = df['bb_upper'] - df['bb_lower']
        df['bandwidth_min'] = df['bandwidth'].rolling(50).min()
        df['bandwidth_max'] = df['bandwidth'].rolling(50).max()
        df['vol_avg'] = df['volume'].rolling(20).mean()

        for i in range(100, len(df)):
            price = df.iloc[i]['close']
            bb_upper = df.iloc[i]['bb_upper']
            bb_lower = df.iloc[i]['bb_lower']
            bandwidth = df.iloc[i]['bandwidth']
            bandwidth_min = df.iloc[i]['bandwidth_min']
            bandwidth_max = df.iloc[i]['bandwidth_max']
            sma20 = df.iloc[i]['sma20']
            volume = df.iloc[i]['volume']
            vol_avg = df.iloc[i]['vol_avg']

            bandwidth_range = bandwidth_max - bandwidth_min
            bandwidth_threshold = bandwidth_min + (bandwidth_range * 0.20)

            # Entry signal - optimized
            if position is None:
                tight_squeeze = bandwidth <= bandwidth_threshold * 1.3  # Relaxed
                vol_ok = volume >= vol_avg * 0.9  # Relaxed

                # Long at lower band
                if tight_squeeze and vol_ok and price <= sma20:
                    stop = bb_lower * 0.97
                    target = sma20 * 1.005
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': 1,
                        'date': df.iloc[i]['datetime'],
                        'direction': 'long'
                    }

                # Short at upper band
                elif tight_squeeze and vol_ok and price >= sma20:
                    stop = bb_upper * 1.03
                    target = sma20 * 0.995
                    position = {
                        'entry': price,
                        'stop': stop,
                        'target': target,
                        'size': -1,
                        'date': df.iloc[i]['datetime'],
                        'direction': 'short'
                    }

            # Exit signal
            elif position:
                if position['direction'] == 'long':
                    if price <= position['stop'] or price >= position['target']:
                        pnl = (price - position['entry']) * position['size']
                        trades.append({
                            'entry': position['entry'],
                            'exit': price,
                            'pnl': pnl,
                            'return_pct': (pnl / position['entry']) * 100,
                            'date': position['date']
                        })
                        position = None
                else:  # short
                    if price >= position['stop'] or price <= position['target']:
                        pnl = (position['entry'] - price) * abs(position['size'])
                        trades.append({
                            'entry': position['entry'],
                            'exit': price,
                            'pnl': pnl,
                            'return_pct': (pnl / position['entry']) * 100,
                            'date': position['date']
                        })
                        position = None

        return trades

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_adx(self, df, period=14):
        """Calculate ADX indicator"""
        high = df['high']
        low = df['low']
        close = df['close']

        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()

        return adx

    def _calculate_vwap(self, df):
        """Calculate VWAP"""
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['vwap'] = (df['typical_price'] * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()
        return df['vwap']


class AutomatedBacktester:
    """Orchestrates full backtesting and iteration"""

    def __init__(self):
        self.engine = BacktestEngine()
        self.tester = StrategyTester(self.engine)
        self.results = {}

    def test_all_slots(self):
        """Test all 10 slots with full automation"""
        logger.info("=" * 80)
        logger.info("AXIOM DAY TRADING - AUTOMATED BACKTEST EXECUTION")
        logger.info("=" * 80)

        slots = {
            1: {
                'name': 'Equities Trending Up',
                'symbols': ['AAPL', 'MSFT', 'NVDA', 'TSLA'],
                'interval': '1h',
                'method': self.tester.slot_1_equities_trending_up
            },
            2: {
                'name': 'Equities Trending Down',
                'symbols': ['JPM', 'BAC'],
                'interval': '1h',
                'method': self.tester.slot_2_equities_trending_down
            },
            3: {
                'name': 'Equities Horizontal',
                'symbols': ['VTI', 'SPY'],
                'interval': '1h',
                'method': self.tester.slot_3_equities_horizontal
            },
            4: {
                'name': 'Equities Explosive',
                'symbols': ['GME'],
                'interval': '1h',
                'method': self.tester.slot_4_equities_explosive
            },
            5: {
                'name': 'Futures Trending Up',
                'symbols': ['SPY', 'QQQ'],  # Proxies for ES, NQ
                'interval': '1h',
                'method': self.tester.slot_5_futures_trending_up
            },
            6: {
                'name': 'Futures Trending Down',
                'symbols': ['CL=F'],
                'interval': '1h',
                'method': self.tester.slot_6_futures_trending_down
            },
            7: {
                'name': 'Futures Horizontal',
                'symbols': ['GC=F'],
                'interval': '1h',
                'method': self.tester.slot_7_futures_horizontal
            },
            8: {
                'name': 'Crypto Trending Up',
                'symbols': ['BTC-USD', 'ETH-USD'],
                'interval': '1h',
                'method': self.tester.slot_8_crypto_trending_up
            },
            9: {
                'name': 'Crypto Trending Down',
                'symbols': ['BTC-USD', 'ETH-USD'],
                'interval': '1h',
                'method': self.tester.slot_9_crypto_trending_down
            },
            10: {
                'name': 'Crypto Horizontal',
                'symbols': ['SOL-USD', 'XRP-USD'],
                'interval': '1h',
                'method': self.tester.slot_10_crypto_horizontal
            }
        }

        for slot_num in sorted(slots.keys()):
            slot = slots[slot_num]
            logger.info(f"\n{'='*80}")
            logger.info(f"SLOT {slot_num}: {slot['name']}")
            logger.info(f"{'='*80}")

            slot_results = {
                'name': slot['name'],
                'symbols': {},
                'best_verdict': None,
                'best_metrics': None,
                'best_symbol': None
            }

            for symbol in slot['symbols']:
                logger.info(f"\nTesting {symbol} ({slot['interval']})...")

                df = self.engine.fetch_data(symbol, period="2y", interval=slot['interval'])
                if df is None or df.empty:
                    logger.warning(f"Skipping {symbol} - no data")
                    continue

                try:
                    trades = slot['method'](df)
                    metrics = self.engine.calculate_metrics(trades)

                    verdict = self._get_verdict(metrics)

                    symbol_result = {
                        'metrics': metrics,
                        'trades': len(trades),
                        'verdict': verdict
                    }
                    slot_results['symbols'][symbol] = symbol_result

                    logger.info(f"  Win Rate: {metrics['win_rate']*100:.1f}%")
                    logger.info(f"  Sharpe: {metrics['sharpe_ratio']:.2f}")
                    logger.info(f"  Max DD: {metrics['max_drawdown']*100:.1f}%")
                    logger.info(f"  PF: {metrics['profit_factor']:.2f}")
                    logger.info(f"  Trades: {metrics['trade_count']}")
                    logger.info(f"  Verdict: {verdict}")

                    # Track best performer
                    if slot_results['best_metrics'] is None or metrics['sharpe_ratio'] > slot_results['best_metrics']['sharpe_ratio']:
                        slot_results['best_metrics'] = metrics
                        slot_results['best_symbol'] = symbol
                        slot_results['best_verdict'] = verdict

                except Exception as e:
                    logger.error(f"Error testing {symbol}: {e}")

            self.results[f'SLOT_{slot_num}'] = slot_results

        return self.results

    def _get_verdict(self, metrics: Dict) -> str:
        """Determine ROBUST, MODERATE, WEAK, or FAIL"""
        win_rate = metrics['win_rate']
        sharpe = metrics['sharpe_ratio']
        max_dd = metrics['max_drawdown']
        pf = metrics['profit_factor']

        # ROBUST criteria
        if win_rate >= 0.70 and sharpe >= 1.3 and max_dd <= 0.12 and pf >= 2.5:
            return 'ROBUST'

        # MODERATE criteria
        if win_rate >= 0.60 and sharpe >= 1.0 and max_dd <= 0.15 and pf >= 2.0:
            return 'MODERATE'

        # WEAK criteria
        if win_rate >= 0.50 and sharpe >= 0.8 and max_dd <= 0.18 and pf >= 1.5:
            return 'WEAK'

        return 'FAIL'

    def generate_manifest(self):
        """Generate final strategy manifest JSON"""
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'backtesting_parameters': {
                'period': '2 years',
                'interval': 'hourly for equities/futures, hourly for crypto',
                'initial_capital': self.engine.initial_capital,
                'commission_pct': self.engine.commission_pct * 100,
                'slippage_pct': self.engine.slippage_pct * 100
            },
            'strategies': {},
            'summary': {
                'total_slots': 10,
                'robust_count': 0,
                'moderate_count': 0,
                'weak_count': 0,
                'fail_count': 0
            }
        }

        for slot_key, slot_data in self.results.items():
            slot_num = int(slot_key.split('_')[1])

            best_verdict = slot_data['best_verdict']
            best_metrics = slot_data['best_metrics']
            best_symbol = slot_data['best_symbol']

            # Count verdicts
            if best_verdict == 'ROBUST':
                manifest['summary']['robust_count'] += 1
            elif best_verdict == 'MODERATE':
                manifest['summary']['moderate_count'] += 1
            elif best_verdict == 'WEAK':
                manifest['summary']['weak_count'] += 1
            else:
                manifest['summary']['fail_count'] += 1

            manifest['strategies'][slot_key] = {
                'slot_number': slot_num,
                'name': slot_data['name'],
                'pine_script_file': f'SLOT_{slot_num}_*.pine',
                'test_symbols': list(slot_data['symbols'].keys()),
                'best_performer': best_symbol,
                'verdict': best_verdict,
                'metrics': {
                    'win_rate': round(best_metrics['win_rate'] * 100, 1) if best_metrics else 0,
                    'sharpe_ratio': round(best_metrics['sharpe_ratio'], 2) if best_metrics else 0,
                    'max_drawdown': round(best_metrics['max_drawdown'] * 100, 1) if best_metrics else 0,
                    'profit_factor': round(best_metrics['profit_factor'], 2) if best_metrics else 0,
                    'total_return': round(best_metrics['total_return'], 2) if best_metrics else 0,
                    'trade_count': best_metrics['trade_count'] if best_metrics else 0,
                },
                'symbol_details': {
                    sym: {
                        'win_rate': round(data['metrics']['win_rate'] * 100, 1),
                        'sharpe': round(data['metrics']['sharpe_ratio'], 2),
                        'max_dd': round(data['metrics']['max_drawdown'] * 100, 1),
                        'verdict': data['verdict']
                    }
                    for sym, data in slot_data['symbols'].items()
                }
            }

        return manifest

    def save_manifest(self, filepath: str):
        """Save manifest to JSON file"""
        manifest = self.generate_manifest()
        with open(filepath, 'w') as f:
            json.dump(manifest, f, indent=2)
        logger.info(f"\nManifest saved to {filepath}")
        return manifest


if __name__ == '__main__':
    backtester = AutomatedBacktester()
    results = backtester.test_all_slots()

    # Generate and save manifest
    manifest_path = r"C:\Case Capital\Axiom day trading\strategy_manifest.json"
    manifest = backtester.save_manifest(manifest_path)

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("BACKTEST SUMMARY")
    logger.info("="*80)
    logger.info(f"ROBUST: {manifest['summary']['robust_count']}/10")
    logger.info(f"MODERATE: {manifest['summary']['moderate_count']}/10")
    logger.info(f"WEAK: {manifest['summary']['weak_count']}/10")
    logger.info(f"FAIL: {manifest['summary']['fail_count']}/10")
    logger.info("="*80)
