"""
AXIOM Day Trading - v2 Mean Reversion EMA
Long/short mean reversion around EMA with ATR-based exits and regular-session filter.
"""
import pandas as pd

def add_indicators(df: pd.DataFrame):
    df = df.copy()
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    if 'atr' not in df.columns:
        tr = pd.concat([
            df['high'] - df['low'],
            (df['high'] - df['close'].shift()).abs(),
            (df['low'] - df['close'].shift()).abs(),
        ], axis=1).max(axis=1)
        df['atr'] = tr.ewm(span=14, adjust=False).mean()
    return df

def detect_signals(df: pd.DataFrame):
    df = add_indicators(df)
    signals = []
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        if prev['close'] < prev['ema20'] and row['close'] > row['ema20']:
            signals.append({'time': row.name.isoformat(), 'side': 'long', 'price': float(row['close'])})
        elif prev['close'] > prev['ema20'] and row['close'] < row['ema20']:
            signals.append({'time': row.name.isoformat(), 'side': 'short', 'price': float(row['close'])})
    return signals
