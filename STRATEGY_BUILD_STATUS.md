# 🚀 AXIOM v2.0 - STRATEGY BUILD STATUS

**Date**: 2026-06-06  
**Phase**: Phase 2 & 3 - Strategy Development & Backtesting  
**Current Task**: Strategy 1 (FUTURES ORB US Open - ES1!)

---

## 📊 BUILD ROADMAP

| # | Strategy | Asset Class | Status | Notes |
|---|----------|-------------|--------|-------|
| 1 | **FUTURES ORB US Open (9:30am ET)** | ES1!, NQ1! | 🟡 READY FOR TEST | Code complete, awaiting backtest |
| 2 | EQUITIES ORB (9:30am ET) | AAPL | ⬜ PENDING | Queued after #1 |
| 3 | FUTURES VWAP Mean Reversion | ES1! | ⬜ PENDING | Queued after #2 |
| 4 | EQUITIES VWAP Mean Reversion | AAPL | ⬜ PENDING | Queued after #3 |
| 5 | CRYPTO RSI Mean Reversion 24/7 | BTCUSDT | ⬜ PENDING | Queued after #4 |
| 6-9 | Remaining Strategies | Mixed | ⬜ PENDING | Crypto ORB, Overnight Trend, EMA |

---

## ✅ STRATEGY 1: COMPLETE SPECIFICATION

### File Location
- **Pine Script**: `C:\Case Capital\Axiom day trading\strategies\futures_orb_us_open.pine`
- **Setup Guide**: `C:\Case Capital\Axiom day trading\STRATEGY_1_SETUP_GUIDE.md`

### Strategy Details
**Name**: FUTURES ORB US Open - ES1! 5-minute  
**Asset**: ES1! (E-mini S&P 500 Futures)  
**Timeframe**: 5-minute candles  
**Session**: US Market Open (9:30am - 11:00am ET)  
**Max Trades**: 2 per session  

### Entry Logic
```
Opening Range Formation: 9:30am - 9:45am ET
├─ Calculate ORB High = max(high) during period
├─ Calculate ORB Low = min(low) during period
└─ Entry Window: 9:45am - 11:00am ET

LONG Entry: close > ORB_HIGH AND rsi > 50 AND volume > avg×1.5
SHORT Entry: close < ORB_LOW AND rsi < 50 AND volume > avg×1.5
```

### Exit Logic
```
Stop Loss: ATR × 1.5 (approximately 15-20 points on ES1!)
Target (Dynamic):
├─ Default: ATR × 2.0
├─ If swing structure exists: Use nearest swing high/low
└─ Minimum distance: ATR × 1.5

Time Exit: 90 minutes (close all at 11:00am if not closed)
```

### Code Features
✅ ATR-based stops (not fixed points)  
✅ Dynamic targets from swing structure  
✅ Volume confirmation (1.5x average minimum)  
✅ Session time filter (Eastern Time)  
✅ Risk = 1% per trade (1 contract per $100k equity)  
✅ Higher timeframe context (15-min EMA 21)  
✅ Prepared for SMC confluence scoring (Phase 4)  

### Acceptance Criteria
```
PASS: Win Rate ≥ 55% AND Profit Factor ≥ 1.3 AND Net PnL > 0
ONE ITERATION: Win Rate 48-54% OR Profit Factor 1.1-1.29 (adjust params once)
NEEDS REVIEW: Win Rate < 48% OR Profit Factor < 1.1 OR Net PnL < 0
```

### Test Requirements
- **Data**: ES1! 5-minute, 2024-01-01 to 2026-06-06 (2 years)
- **Expected Trades**: 150-300 trades (ORB setup appears 4-5x per week)
- **Minimum Valid**: 100 trades to statistically validate
- **Execution**: Real commission (0.05%) + 2-point slippage

---

## 📋 USER ACTION REQUIRED

### Immediate Actions (Before Testing Strategy 1):
1. ✅ Open TradingView Desktop
2. ✅ Load ES1! chart, set to 5-minute timeframe
3. ✅ Add "Smart Money Concepts" indicator by LuxAlgo
4. ✅ Follow setup guide in: `STRATEGY_1_SETUP_GUIDE.md`
5. ✅ Copy code from: `futures_orb_us_open.pine`
6. ✅ Paste into Pine Editor and save
7. ✅ Run backtest (Strategy Tester panel)
8. ✅ Record all metrics
9. ✅ Report results below

### Results Reporting Format
Once backtest completes, provide:

```
STRATEGY 1 BACKTEST RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symbol: ES1!
Timeframe: 5-minute
Test Period: 2024-01-01 to 2026-06-06

METRICS:
Total Trades: ___
Win Rate: ___%
Profit Factor: ___
Max Drawdown: ___%
Net Profit/Loss: $___
Sharpe Ratio: ___
Avg Trade Duration: ___ minutes

DECISION:
[ ] PASS - Proceed to Strategy 2
[ ] ONE ITERATION - Adjust parameters and retest
[ ] NEEDS REVIEW - Flag and move to Strategy 2
```

---

## 🔄 PARAMETER ADJUSTMENT OPTIONS (if needed)

If first test doesn't meet acceptance criteria, you have **ONE** iteration to adjust:

### Option A: RSI Sensitivity
```pine
// Current
rsi > 50  // Long bias threshold
rsi < 50  // Short bias threshold

// Try looser
rsi > 45  // Long (more entries)
rsi < 55  // Short (more entries)
```

### Option B: Stop Loss Width
```pine
// Current
stop_level := entry_price - (atr * 1.5)  // ~15-20 points

// Try tighter
stop_level := entry_price - (atr * 1.0)  // ~10-13 points
```

### Option C: Target Distance
```pine
// Current
target_level := entry_price + (atr * 2.0)  // ~20-26 points

// Try further
target_level := entry_price + (atr * 2.5)  // ~26-32 points
```

### Option D: Time Exit Window
```pine
// Current
bars_in_trade > 18  // 90 minutes (9:30am → 11:00am)

// Try longer
bars_in_trade > 24  // 120 minutes (9:30am → 11:30am)
```

---

## 🎯 SUCCESS BENCHMARK

For ES1! ORB, industry benchmarks show:

| Metric | Conservative | Target | Aggressive |
|--------|--------------|--------|-----------|
| Win Rate | 48% | 55% | 65% |
| Profit Factor | 1.2 | 1.5 | 2.0+ |
| R:R Ratio | 1.0 | 1.5 | 2.0+ |
| Max DD | 20% | 15% | 10% |

**Our targets (55% win rate, 1.3 PF) are realistic and achievable for ORB strategies.**

---

## ⏭️ NEXT STRATEGY IN QUEUE

Once Strategy 1 is tested and decision made:

**STRATEGY 2: EQUITIES ORB on AAPL** (same ORB logic, adapted for equities)
- Symbol: AAPL
- Timeframe: 5-minute
- Session: 9:30am - 11:00am ET (same window)
- Differences:
  - Wider opening range (equities more volatile than ES1!)
  - Lower contract size (buy actual shares vs futures)
  - Tighter stop (equities punish gap-throughs more)

---

## 📝 NOTES

- **SMC Integration Ready**: Code structure allows reading LuxAlgo SMC values in future phases
- **Confluence Scoring**: Will add 0-10 scoring system once baseline ORB validates
- **Parallel Development**: Other 6 strategies are drafted and ready for sequential testing
- **Timeline**: Testing all 9 strategies at 2-3 per day = 3-4 days to complete Phase 3

---

**Status**: 🟡 **READY FOR TESTING**  
**Next Action**: User to execute backtest of Strategy 1 and report results  
**Expected Completion**: Within 24 hours

