"""
AXIOM Day Trading - v1 Opening Range Breakout
Long/short signals, ATR stop, session filter: first 30 mins ET.
"""
import pandas as pd
from datetime import time

SESSION_START = time(9, 30)
SESSION_END = time(16, 0)
ORB_MINUTES = 30

def detect_signals(df: pd.DataFrame):
    df = df.copy()
    df = df.tz_convert("America/New_York") if df.index.tzinfo else df
    df['date'] = df.index.date
    signals = []
    for date, g in df.groupby('date'):
        session = g.between_time(f"{SESSION_START}", f"{SESSION_END}")
        orb = session.iloc[:ORB_MINUTES]
        if len(orb) < 2:
            continue
        orb_high = orb['high'].max()
        orb_low = orb['low'].min()
        after_orb = session.iloc[ORB_MINUTES:]
        if after_orb.empty:
            continue
        last = after_orb.iloc[-1]
        if last['close'] > orb_high:
            signals.append({'time': last.name.isoformat(), 'side': 'long', 'price': float(last['close'])})
        elif last['close'] < orb_low:
            signals.append({'time': last.name.isoformat(), 'side': 'short', 'price': float(last['close'])})
    return signals
