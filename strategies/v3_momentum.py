"""
AXIOM Day Trading - v3 ADX Momentum
Momentum entries on ADX strength with ATR stop placeholder.
"""
import pandas as pd

def add_indicators(df: pd.DataFrame):
    df = df.copy()
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    atr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs(),
    ], axis=1).max(axis=1)
    df['atr'] = atr.ewm(span=14, adjust=False).mean()
    tr = atr
    smooth = atr.ewm(span=14, adjust=False).mean()
    plus = 100 * plus_dm.ewm(span=14, adjust=False).mean() / smooth.replace(0, float('nan'))
    minus = 100 * minus_dm.ewm(span=14, adjust=False).mean() / smooth.replace(0, float('nan'))
    df['adx'] = (plus - minus).abs().ewm(span=14, adjust=False).mean()
    df['plus_di'] = plus
    df['minus_di'] = minus
    return df

def detect_signals(df: pd.DataFrame):
    df = add_indicators(df)
    signals = []
    adx_min = 25
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        if pd.isna(row['adx']):
            continue
        if row['adx'] >= adx_min and prev['plus_di'] < prev['minus_di'] and row['plus_di'] > row['minus_di']:
            signals.append({'time': row.name.isoformat(), 'side': 'long', 'price': float(row['close'])})
        elif row['adx'] >= adx_min and prev['minus_di'] < prev['plus_di'] and row['minus_di'] > row['plus_di']:
            signals.append({'time': row.name.isoformat(), 'side': 'short', 'price': float(row['close'])})
    return signals
