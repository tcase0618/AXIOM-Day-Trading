"""
AXIOM Day Trading - v4 Volume Breakout
Long breakout entries on volume burst above threshold with ATR-based stop.
No short entries.
"""
import pandas as pd

def add_indicators(df: pd.DataFrame):
    df = df.copy()
    if 'atr' not in df.columns:
        tr = pd.concat([
            df['high'] - df['low'],
            (df['high'] - df['close'].shift()).abs(),
            (df['low'] - df['close'].shift()).abs(),
        ], axis=1).max(axis=1)
        df['atr'] = tr.ewm(span=14, adjust=False).mean()
    if 'volume_ma' not in df.columns:
        df['volume_ma'] = df['volume'].rolling(20).mean()
    return df

def detect_signals(df: pd.DataFrame):
    df = add_indicators(df)
    signals = []
    vol_mult = df['volume_ma'].mean() * 2.0
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        if pd.isna(row['volume_ma']) or pd.isna(row['atr']):
            continue
        if row['volume'] > vol_mult and row['close'] > prev['high']:
            signals.append({'time': row.name.isoformat(), 'side': 'long', 'price': float(row['close'])})
    return signals
