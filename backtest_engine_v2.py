#!/usr/bin/env python3
"""
AXIOM Day Trading - Backtest Engine v2
Revised strategies using simpler, more robust logic for hourly data
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import yfinance as yf
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


class SimplifiedBacktester:
    """Simplified backtester with robust hourly-optimized strategies"""

    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.results = {}

    def fetch_data(self, symbol: str, period: str = "2y", interval: str = "1h"):
        """Fetch OHLCV data"""
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if df.empty:
                return None
            df = df.reset_index()
            df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
            return df.dropna()
        except:
            return None

    def calculate_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        if not trades:
            return {'win_rate': 0, 'sharpe_ratio': 0, 'max_drawdown': 0, 'profit_factor': 0,
                    'total_return': 0, 'trade_count': 0}

        profits = [t['pnl'] for t in trades]
        wins = [p for p in profits if p > 0]
        losses = [abs(p) for p in profits if p < 0]

        win_rate = len(wins) / len(trades) if trades else 0
        total_profit = sum(wins)
        total_loss = sum(losses)

        returns = [p / self.initial_capital for p in profits]
        sharpe = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0

        equity = [self.initial_capital]
        for p in profits:
            equity.append(equity[-1] + p)
        equity_peak = np.maximum.accumulate(equity)
        drawdown = (np.array(equity) - equity_peak) / equity_peak
        max_drawdown = abs(min(drawdown)) if len(drawdown) > 0 else 0

        profit_factor = total_profit / total_loss if total_loss > 0 else 0

        return {
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'total_return': sum(profits),
            'trade_count': len(trades)
        }

    def get_verdict(self, metrics: Dict) -> str:
        """Determine strategy verdict"""
        wr = metrics['win_rate']
        sharpe = metrics['sharpe_ratio']

        if wr >= 0.60 and sharpe >= 1.0 and metrics['profit_factor'] >= 2.0:
            return 'ROBUST'
        elif wr >= 0.55 and sharpe >= 0.8 and metrics['profit_factor'] >= 1.8:
            return 'MODERATE'
        elif wr >= 0.50:
            return 'WEAK'
        return 'FAIL'

    def simple_ma_trend_long(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 1/5/8: Simple MA crossover for trending up"""
        trades = []
        df['sma9'] = df['close'].rolling(9).mean()
        df['sma21'] = df['close'].rolling(21).mean()
        df['atr'] = self._calculate_atr(df, 14)

        in_trade = False
        entry_price = 0
        stop_price = 0
        target_price = 0

        for i in range(50, len(df)):
            price = df.iloc[i]['close']
            sma9 = df.iloc[i]['sma9']
            sma21 = df.iloc[i]['sma21']
            atr = df.iloc[i]['atr']

            if not in_trade:
                # Entry: when 9-SMA crosses above 21-SMA
                if sma9 > sma21 and df.iloc[i-1]['sma9'] <= df.iloc[i-1]['sma21']:
                    entry_price = price
                    stop_price = entry_price - (atr * 1.5)
                    target_price = entry_price + (atr * 2.5)
                    in_trade = True

            else:
                # Exit
                if price <= stop_price or price >= target_price:
                    pnl = price - entry_price
                    trades.append({'entry': entry_price, 'exit': price, 'pnl': pnl})
                    in_trade = False

        return trades

    def simple_ma_trend_short(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 2/6/9: Simple MA crossover for trending down"""
        trades = []
        df['sma9'] = df['close'].rolling(9).mean()
        df['sma21'] = df['close'].rolling(21).mean()
        df['atr'] = self._calculate_atr(df, 14)

        in_trade = False
        entry_price = 0
        stop_price = 0
        target_price = 0

        for i in range(50, len(df)):
            price = df.iloc[i]['close']
            sma9 = df.iloc[i]['sma9']
            sma21 = df.iloc[i]['sma21']
            atr = df.iloc[i]['atr']

            if not in_trade:
                # Entry: when 9-SMA crosses below 21-SMA
                if sma9 < sma21 and df.iloc[i-1]['sma9'] >= df.iloc[i-1]['sma21']:
                    entry_price = price
                    stop_price = entry_price + (atr * 1.5)
                    target_price = entry_price - (atr * 2.5)
                    in_trade = True

            else:
                # Exit
                if price >= stop_price or price <= target_price:
                    pnl = entry_price - price
                    trades.append({'entry': entry_price, 'exit': price, 'pnl': pnl})
                    in_trade = False

        return trades

    def simple_bb_mean_reversion(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 3/7/10: Simple Bollinger Bands mean reversion"""
        trades = []
        df['sma20'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['sma20'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['sma20'] - (df['bb_std'] * 2)
        df['atr'] = self._calculate_atr(df, 14)

        in_trade = False
        entry_price = 0
        stop_price = 0
        target_price = 0
        direction = None

        for i in range(50, len(df)):
            price = df.iloc[i]['close']
            bb_upper = df.iloc[i]['bb_upper']
            bb_lower = df.iloc[i]['bb_lower']
            sma20 = df.iloc[i]['sma20']
            atr = df.iloc[i]['atr']

            if not in_trade:
                # Entry: price touches bands
                if price <= bb_lower * 1.01:
                    entry_price = price
                    stop_price = entry_price - (atr * 1.0)
                    target_price = sma20
                    direction = 'long'
                    in_trade = True

                elif price >= bb_upper * 0.99:
                    entry_price = price
                    stop_price = entry_price + (atr * 1.0)
                    target_price = sma20
                    direction = 'short'
                    in_trade = True

            else:
                # Exit
                if direction == 'long':
                    if price <= stop_price or price >= target_price:
                        pnl = price - entry_price
                        trades.append({'entry': entry_price, 'exit': price, 'pnl': pnl})
                        in_trade = False
                else:
                    if price >= stop_price or price <= target_price:
                        pnl = entry_price - price
                        trades.append({'entry': entry_price, 'exit': price, 'pnl': pnl})
                        in_trade = False

        return trades

    def simple_breakout(self, df: pd.DataFrame) -> List[Dict]:
        """SLOT 4: Simple breakout strategy"""
        trades = []
        df['highest'] = df['high'].rolling(20).max()
        df['lowest'] = df['low'].rolling(20).min()
        df['atr'] = self._calculate_atr(df, 14)

        in_trade = False
        entry_price = 0
        stop_price = 0
        target_price = 0

        for i in range(50, len(df)):
            price = df.iloc[i]['close']
            highest = df.iloc[i-1]['highest']
            atr = df.iloc[i]['atr']

            if not in_trade:
                # Entry: price breaks above 20-bar high
                if price > highest:
                    entry_price = price
                    stop_price = entry_price - (atr * 2.0)
                    target_price = entry_price + (atr * 3.0)
                    in_trade = True

            else:
                # Exit
                if price <= stop_price or price >= target_price:
                    pnl = price - entry_price
                    trades.append({'entry': entry_price, 'exit': price, 'pnl': pnl})
                    in_trade = False

        return trades

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(period).mean()

    def test_all_slots(self):
        """Test all 10 slots"""
        logger.info("=" * 80)
        logger.info("AXIOM BACKTEST ENGINE V2 - SIMPLIFIED STRATEGIES")
        logger.info("=" * 80)

        slots = {
            1: {'name': 'Equities Trending Up', 'symbols': ['AAPL', 'MSFT', 'NVDA', 'TSLA'], 'method': self.simple_ma_trend_long},
            2: {'name': 'Equities Trending Down', 'symbols': ['JPM', 'BAC'], 'method': self.simple_ma_trend_short},
            3: {'name': 'Equities Horizontal', 'symbols': ['VTI', 'SPY'], 'method': self.simple_bb_mean_reversion},
            4: {'name': 'Equities Explosive', 'symbols': ['GME'], 'method': self.simple_breakout},
            5: {'name': 'Futures Trending Up', 'symbols': ['SPY', 'QQQ'], 'method': self.simple_ma_trend_long},
            6: {'name': 'Futures Trending Down', 'symbols': ['CL=F'], 'method': self.simple_ma_trend_short},
            7: {'name': 'Futures Horizontal', 'symbols': ['GC=F'], 'method': self.simple_bb_mean_reversion},
            8: {'name': 'Crypto Trending Up', 'symbols': ['BTC-USD', 'ETH-USD'], 'method': self.simple_ma_trend_long},
            9: {'name': 'Crypto Trending Down', 'symbols': ['BTC-USD', 'ETH-USD'], 'method': self.simple_ma_trend_short},
            10: {'name': 'Crypto Horizontal', 'symbols': ['SOL-USD', 'XRP-USD'], 'method': self.simple_bb_mean_reversion}
        }

        for slot_num, slot in slots.items():
            logger.info(f"\nSLOT {slot_num}: {slot['name']}")
            best_metrics = None
            best_symbol = None
            best_verdict = 'FAIL'

            for symbol in slot['symbols']:
                df = self.fetch_data(symbol)
                if df is None or df.empty:
                    logger.warning(f"  {symbol}: No data")
                    continue

                try:
                    trades = slot['method'](df)
                    metrics = self.calculate_metrics(trades)
                    verdict = self.get_verdict(metrics)

                    logger.info(f"  {symbol}: WR={metrics['win_rate']*100:.1f}%, Sharpe={metrics['sharpe_ratio']:.2f}, Trades={metrics['trade_count']}, Verdict={verdict}")

                    if best_metrics is None or metrics['sharpe_ratio'] > best_metrics['sharpe_ratio']:
                        best_metrics = metrics
                        best_symbol = symbol
                        best_verdict = verdict

                except Exception as e:
                    logger.error(f"  {symbol}: {e}")

            if best_metrics:
                self.results[f'SLOT_{slot_num}'] = {
                    'name': slot['name'],
                    'best_symbol': best_symbol,
                    'metrics': best_metrics,
                    'verdict': best_verdict
                }

        return self.results

    def generate_manifest(self):
        """Generate final manifest"""
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'strategies': {},
            'summary': {'robust': 0, 'moderate': 0, 'weak': 0, 'fail': 0}
        }

        for slot_key, data in self.results.items():
            verdict = data['verdict']
            manifest['summary'][verdict.lower()] += 1

            slot_num = int(slot_key.split('_')[1])
            manifest['strategies'][slot_key] = {
                'slot_number': slot_num,
                'name': data['name'],
                'best_performer': data['best_symbol'],
                'verdict': verdict,
                'metrics': {
                    'win_rate': round(data['metrics']['win_rate'] * 100, 1),
                    'sharpe_ratio': round(data['metrics']['sharpe_ratio'], 2),
                    'max_drawdown': round(data['metrics']['max_drawdown'] * 100, 1),
                    'profit_factor': round(data['metrics']['profit_factor'], 2),
                    'total_return': round(data['metrics']['total_return'], 2),
                    'trade_count': data['metrics']['trade_count']
                }
            }

        return manifest

    def save_manifest(self, filepath: str):
        """Save manifest to JSON"""
        manifest = self.generate_manifest()
        with open(filepath, 'w') as f:
            json.dump(manifest, f, indent=2)
        logger.info(f"Manifest saved: {filepath}")
        return manifest


if __name__ == '__main__':
    backtester = SimplifiedBacktester()
    backtester.test_all_slots()
    manifest = backtester.save_manifest(r"C:\Case Capital\Axiom day trading\strategy_manifest.json")

    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"ROBUST: {manifest['summary']['robust']}")
    logger.info(f"MODERATE: {manifest['summary']['moderate']}")
    logger.info(f"WEAK: {manifest['summary']['weak']}")
    logger.info(f"FAIL: {manifest['summary']['fail']}")
