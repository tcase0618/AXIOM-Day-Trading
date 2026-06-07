# SLOT 13 BASELINE VERSION — Simplified Entry Conditions

**Date**: 2026-06-06  
**Strategy**: SLOT 13: ICT Price Action - Futures (Baseline)  
**Symbol**: ES1! (S&P 500 E-mini)  
**Timeframe**: 5-minute  
**Status**: ✅ Compiled, Injected, Ready for Backtest

---

## 📋 **What Changed**

### ❌ REMOVED (Too Strict for Current Data)
- ✗ ORB (Opening Range Breakout) requirement — was filtering out too many trades
- ✗ OTE (Optimal Trade Entry) — 62-79% Fibonacci zone was too restrictive
- ✗ Order Block requirement — eliminated
- ✗ RSI Divergence — removed complex divergence logic
- ✗ Weak volume check — changed to STRONG volume requirement

### ✅ SIMPLIFIED ENTRY RULES (New Baseline)

**LONG Entry (ALL conditions required)**:
1. BOS Bullish detected (close > last swing high)
2. Price pulls back to EMA21 (within 0.5*ATR above/below)
3. RSI > 50 (simple momentum)
4. Volume ≥ 1.5x average on entry candle
5. No existing position

**SHORT Entry (ALL conditions required)**:
1. BOS Bearish detected (close < last swing low)
2. Price pulls back to EMA21 (within 0.5*ATR above/below)
3. RSI < 50 (simple momentum)
4. Volume ≥ 1.5x average on entry candle
5. No existing position

---

## 🎯 **Risk Management**

| Component | Value |
|-----------|-------|
| Stop Loss | Below EMA50 (−0.3*ATR for longs, +0.3*ATR for shorts) |
| Target | 2x Risk (risked amount × 2) |
| Max Trades/Session | 2 |
| Commission | 0.05% |
| Slippage | 2 points |

---

## 🔧 **Key Parameters**

```
ATR_PERIOD = 14
RSI_PERIOD = 14
EMA21_PERIOD = 21  (Entry zone)
EMA50_PERIOD = 50  (Stop placement)
VOLUME_MULTIPLIER = 1.5  (Strong volume threshold)
```

---

## 🚀 **Expected Behavior**

Since we removed the restrictive ICT conditions:

- **Trade Frequency**: Should generate 50-150+ trades in 2-month window (vs. 0 before)
- **Entry Triggers**: More frequent BOS + EMA21 + RSI combos
- **Quality**: Lower (more noise), but enough data to see what works
- **Win Rate**: Likely 45-55% range initially

---

## 📊 **Next Steps**

1. **Run Backtest on ES1! 5-minute**:
   - Ensure 2-year data loaded (2024-01-01 to 2026-06-06)
   - Click "Test" in Strategy Tester
   - Record: Total Trades, Win Rate %, Profit Factor, Max Drawdown %, Avg R:R

2. **Check Results Against Baseline Criteria**:
   - Win Rate target: 50%+ (reduced from 58% for baseline)
   - R:R target: 1.5:1+ (reduced from 1.8 for baseline)
   - Max Drawdown: 12%+ acceptable for baseline

3. **Add ICT Conditions Back One At A Time**:
   - Once baseline trades execute, add conditions back incrementally
   - Test each addition to see if it improves win rate
   - Order of addition (by priority):
     1. OTE zone (62-79% retracement)
     2. Order Block proximity
     3. RSI Divergence
     4. Weak volume filter (convert to volume strength filter)

---

## 💡 **Philosophy**

This baseline approach follows the principle: **"Start simple, add complexity only if it improves results."**

The old ICT version required ALL conditions to align (too strict → 0 trades).  
The new version requires FEWER conditions but combines them efficiently (should generate ~100+ trades).

Once we see this baseline's performance, we'll selectively re-add ICT rules that genuinely improve edge.

---

## 📁 **File Locations**

- **Strategy Code**: `C:\Case Capital\Axiom day trading\strategies\slot13_ict_price_action_futures.pine`
- **Backtest Results**: Will be logged to `backtest_results.json`
- **Documentation**: This file (`SLOT13_BASELINE_README.md`)

---

## ⚠️ **Important**

This is a **BASELINE TEST VERSION**, not production-ready. Its purpose is to:
1. Generate sufficient trade data
2. Identify base entry signal quality
3. Determine which ICT filters improve performance
4. Build a minimal viable trading strategy

Once results are captured, we'll iterate and optimize.

---

**Status**: ✅ Ready for manual backtest execution in TradingView Strategy Tester
