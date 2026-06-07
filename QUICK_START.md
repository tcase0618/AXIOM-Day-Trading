# AXIOM Day Trading - Quick Start Guide

**Status**: All 10 custom Pine Scripts ready for validation  
**Time to deploy**: 30 minutes if using Option B (Python backtest)

---

## What's Ready Now

✅ **SLOT_1_EQUITIES_TRENDING_UP.pine** - EMA trend + RSI entry  
✅ **SLOT_2_EQUITIES_TRENDING_DOWN.pine** - EMA trend + RSI entry  
✅ **SLOT_3_EQUITIES_HORIZONTAL.pine** - ADX + Bollinger squeeze  
✅ **SLOT_4_EQUITIES_EXPLOSIVE.pine** - Volume breakout + RSI  
✅ **SLOT_5_FUTURES_TRENDING_UP.pine** - EMA trend + VWAP confirmation  
✅ **SLOT_6_FUTURES_TRENDING_DOWN.pine** - EMA trend + VWAP confirmation  
✅ **SLOT_7_FUTURES_HORIZONTAL.pine** - VWAP mean reversion  
✅ **SLOT_8_CRYPTO_TRENDING_UP.pine** - EMA trend (4H timeframe)  
✅ **SLOT_9_CRYPTO_TRENDING_DOWN.pine** - EMA trend (4H timeframe)  
✅ **SLOT_10_CRYPTO_HORIZONTAL.pine** - Bollinger squeeze (1H timeframe)  

---

## Option 1: Test on TradingView (Manual, 7.5 hours)

```
For each SLOT_X_*.pine file:
1. Open TradingView → Chart
2. Set symbol (see list below)
3. Pine Editor → Load Script
4. Strategy Tester → Backtest (2 years, see timeframe below)
5. Record: Win%, Sharpe, Max DD, Trade Count
6. Repeat for all symbols in category
```

**Symbols per Slot:**

```
SLOT 1 → AAPL, MSFT, NVDA, TSLA (1H)
SLOT 2 → JPM, BAC (1H)
SLOT 3 → VTI, ^GSPC (1H)
SLOT 4 → GME (1H)
SLOT 5 → SPY or ES1! (1H)
SLOT 6 → CL-F (1H)
SLOT 7 → GC-F (1H)
SLOT 8 → BTC-USD, ETH-USD (4H)
SLOT 9 → BTC-USD, ETH-USD (4H)
SLOT 10 → SOL-USD, XRP-USD (1H)
```

---

## Option 2: Build Python Backtester (Automated, 2 hours build + 30 min run)

I can create a Python script that:
1. Loads 2-year OHLCV data via yfinance
2. Translates Pine Script logic to pandas/TA-Lib
3. Simulates all trades with commissions/slippage
4. Calculates Win%, Sharpe, Max DD, Profit Factor
5. Saves results to JSON
6. Runs walk-forward validation automatically

**Command to build:**
```
I need to build a Python backtest engine. Should I proceed?
```

---

## Success Metrics (Per Slot)

| Rating | Win Rate | Sharpe | Max DD | Status |
|--------|----------|--------|--------|--------|
| ROBUST | 70%+ | 1.3+ | <12% | ✅ Deploy Live |
| MODERATE | 60-69% | 1.0-1.29 | <15% | ✅ Deploy Live (Monitor) |
| WEAK | 50-59% | 0.8-0.99 | <18% | ⚠️ Tune Parameters |
| FAIL | <50% | <0.8 | >18% | ❌ Redesign |

---

## What Happens If Strategy Doesn't Meet MODERATE

1. Adjust entry filters (increase volume requirement)
2. Tweak indicator parameters (RSI 50-65 → 52-62)
3. Add confirmation (MACD histogram, ADX strength)
4. Add time-of-day filter
5. Use trailing stops instead of static stops
6. Re-backtest on 2-year data
7. Iterate until MODERATE+ achieved

---

## Files Location

```
C:\Case Capital\Axiom day trading\strategies\
├── SLOT_1_EQUITIES_TRENDING_UP.pine
├── SLOT_2_EQUITIES_TRENDING_DOWN.pine
├── SLOT_3_EQUITIES_HORIZONTAL.pine
├── SLOT_4_EQUITIES_EXPLOSIVE.pine
├── SLOT_5_FUTURES_TRENDING_UP.pine
├── SLOT_6_FUTURES_TRENDING_DOWN.pine
├── SLOT_7_FUTURES_HORIZONTAL.pine
├── SLOT_8_CRYPTO_TRENDING_UP.pine
├── SLOT_9_CRYPTO_TRENDING_DOWN.pine
└── SLOT_10_CRYPTO_HORIZONTAL.pine
```

Documentation:
```
C:\Case Capital\Axiom day trading\
├── PINE_SCRIPT_DEPLOYMENT_GUIDE.md (Detailed specs per slot)
├── STRATEGY_DEVELOPMENT_STATUS.md (Progress tracking)
├── IMPLEMENTATION_READY.md (Full testing framework)
└── QUICK_START.md (This file)
```

---

## Next: Choose Your Path

**Path A** → Manual TradingView testing (7.5 hours, highest confidence)  
**Path B** → Python backtest automation (2.5 hours total, fastest iteration)

Which would you prefer?
