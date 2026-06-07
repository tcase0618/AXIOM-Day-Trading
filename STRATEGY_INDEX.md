# 📊 AXIOM v2.0 - MASTER STRATEGY INDEX

**Generated**: 2026-06-06  
**Phase**: 3 - All 8 Strategies Built & Ready for Sequential Testing  
**Status**: 🟢 **READY FOR TESTING**

---

## 📋 STRATEGY TESTING QUEUE

### ✅ STRATEGY 1: FUTURES ORB US OPEN (9:30am ET)
- **File**: `C:\Case Capital\Axiom day trading\strategies\futures_orb_us_open.pine`
- **Symbol**: ES1! (E-mini S&P 500)
- **Timeframe**: 5-minute
- **Session**: 9:30am - 11:00am ET daily
- **Max Trades**: 2 per session
- **Setup**: Opening Range Breakout on first 15-min range
- **Status**: 🟡 **AWAITING BACKTEST**
- **Setup Guide**: `STRATEGY_1_SETUP_GUIDE.md`
- **Quick Start**: `QUICK_START_STRATEGY_1.txt`

---

### ⬜ STRATEGY 2: EQUITIES ORB (9:30am ET)
- **File**: `C:\Case Capital\Axiom day trading\strategies\equities_orb_aapl.pine`
- **Symbol**: AAPL (also test on MSFT, NVDA, AMD)
- **Timeframe**: 5-minute
- **Session**: 9:30am - 11:30am ET daily
- **Max Trades**: 2 per session
- **Setup**: Same ORB logic as Strategy 1, adapted for equities (wider stops)
- **Key Difference**: ATR × 2.0 stops (vs 1.5 for futures)
- **Status**: ⬜ **QUEUED - AFTER STRATEGY 1**
- **Expected Win Rate**: 54-58% (slightly lower than futures)

---

### ⬜ STRATEGY 3: FUTURES VWAP MEAN REVERSION
- **File**: `C:\Case Capital\Axiom day trading\strategies\futures_vwap_mean_reversion.pine`
- **Symbol**: ES1!
- **Timeframe**: 5-minute
- **Session**: 10:30am - 2:30pm ET (avoid opening volatility & close chop)
- **Max Trades**: 2 per session
- **Setup**: Price overshoots VWAP, RSI extreme, then recovers
- **Entry Signal**: 
  - Long: Price below VWAP + RSI < 30, then close above VWAP
  - Short: Price above VWAP + RSI > 70, then close below VWAP
- **Target**: Back to VWAP or nearest swing structure
- **Stop**: ATR × 1.5 (tight - mean reversion resolves quickly)
- **Time Exit**: 60 minutes (quick scalp)
- **Status**: ⬜ **QUEUED - AFTER STRATEGY 2**
- **Expected Win Rate**: 55-62% (mean reversion is higher probability)

---

### ⬜ STRATEGY 4: EQUITIES VWAP MEAN REVERSION
- **File**: `C:\Case Capital\Axiom day trading\strategies\equities_vwap_mean_reversion.pine`
- **Symbol**: AAPL (also test on MSFT, NVDA, AMD)
- **Timeframe**: 5-minute
- **Session**: 10:30am - 2:30pm ET
- **Max Trades**: 2 per session
- **Setup**: Same VWAP mean reversion adapted for equities
- **Key Difference**: ATR × 2.0 stops (wider for equities)
- **Status**: ⬜ **QUEUED - AFTER STRATEGY 3**
- **Expected Win Rate**: 54-60%

---

### ⬜ STRATEGY 5: CRYPTO RSI MEAN REVERSION (24/7)
- **File**: `C:\Case Capital\Axiom day trading\strategies\crypto_rsi_mean_reversion.pine`
- **Symbol**: BTCUSDT (also test ETH, SOL)
- **Timeframe**: 5-minute
- **Session**: 24/7 (crypto never closes)
- **Max Trades**: 4 per 4-hour window
- **Setup**: RSI extremely oversold/overbought, then recovers
- **Entry Signal**:
  - Long: RSI < 25 + volume spike, then RSI crosses above 40 + EMA21 > EMA50
  - Short: RSI > 75 + volume spike, then RSI crosses below 60 + EMA21 < EMA50
- **Target**: ATR × 1.5 above entry (mean reversion targets are small)
- **Stop**: ATR × 1.2 (tight)
- **Time Exit**: 60 minutes
- **Status**: ⬜ **QUEUED - AFTER STRATEGY 4**
- **Expected Win Rate**: 52-60% (crypto mean reversion very reliable)

---

### ⬜ STRATEGY 6: FUTURES LONDON OPEN ORB (3am ET)
- **File**: `C:\Case Capital\Axiom day trading\strategies\futures_london_orb.pine`
- **Symbol**: ES1!, NQ1!
- **Timeframe**: 15-minute (London session less liquid than US)
- **Session**: 3:00am - 6:00am ET (London open)
- **Max Trades**: 1 per session (lower volume)
- **Setup**: ORB on London open range
- **Time Exit**: Closes at 9:20am ET (before US open)
- **Status**: ⬜ **QUEUED - AFTER STRATEGY 5**
- **Expected Win Rate**: 50-54% (lower volume = tougher conditions)
- **Note**: Lower volume means wider spreads, higher slippage

---

### ⬜ STRATEGY 7: CRYPTO EMA TREND FOLLOWING (4-hour)
- **File**: `C:\Case Capital\Axiom day trading\strategies\crypto_ema_trend.pine`
- **Symbol**: BTCUSDT (also test ETH)
- **Timeframe**: 4-hour
- **Session**: 24/7
- **Max Trades**: 2 per trend
- **Setup**: EMA(12) crossover EMA(26), MACD confirmation, RSI alignment
- **Entry Signal**:
  - Long: EMA12 > EMA26 + MACD > 0 + RSI > 50
  - Short: EMA12 < EMA26 + MACD < 0 + RSI < 50
- **Target**: ATR × 3.0 (trend trades hold longer)
- **Stop**: ATR × 2.0 (wider for trend volatility)
- **Time Exit**: 20 bars (~80 hours / 3 days)
- **Trailing Stop**: Tighten after 5% profit
- **Status**: ⬜ **QUEUED - AFTER STRATEGY 6**
- **Expected Win Rate**: 48-54% (trend following lower % but bigger wins)

---

### ⬜ STRATEGY 8: CRYPTO SESSION BREAKOUT (24/7)
- **File**: `C:\Case Capital\Axiom day trading\strategies\crypto_session_breakout.pine`
- **Symbol**: BTCUSDT (also test ETH, SOL)
- **Timeframe**: 5-minute
- **Session**: 24/7 (trades at Asia/London/US session opens)
- **Max Trades**: 2 per session
- **Setup**: Breakout of first 60-minute range at major session opens
- **Sessions**:
  - Asia Open: ~8pm UTC (20:00)
  - London Open: 3am ET (3:00 UTC+1)
  - US Open: 9:30am ET (14:30 UTC)
- **Target**: ATR × 2.0
- **Stop**: ATR × 1.3
- **Time Exit**: 90 minutes
- **Status**: ⬜ **QUEUED - AFTER STRATEGY 7**
- **Expected Win Rate**: 52-58% (breakouts reliable in crypto)

---

## 🎯 TESTING WORKFLOW

### For Each Strategy:
1. **Open TradingView** → Load appropriate symbol & timeframe
2. **Add LuxAlgo SMC indicator** (optional for confluence, future enhancement)
3. **Copy Pine Script** from `strategies/` folder
4. **Inject into Strategy Editor** → Save & Add to Chart
5. **Open Strategy Tester** → Set date range 2024-01-01 to 2026-06-06
6. **Run Backtest** → Wait for completion (1-2 minutes)
7. **Record All Metrics**:
   - Total Trades
   - Win Rate %
   - Profit Factor
   - Max Drawdown %
   - Net Profit/Loss
   - Avg Trade Duration
   - Sharpe Ratio (if available)

### Decision Logic:
```
IF Win Rate ≥ 55% AND Profit Factor ≥ 1.3 AND Net PnL > 0:
  → PASS ✅ (Proceed to next strategy)
  
ELSE IF Win Rate 48-54% OR Profit Factor 1.1-1.29:
  → ONE PARAMETER ITERATION (adjust RSI, ATR multiplier, or time exit)
  → Retest once
  
ELSE IF second test also fails:
  → NEEDS MANUAL REVIEW ⚠️ (flag and move to next strategy)
```

---

## 📊 PERFORMANCE BENCHMARKS

| Metric | Futures ORB | Equities ORB | VWAP MR | RSI MR | Trend | Breakout |
|--------|-------------|--------------|---------|---------|-------|----------|
| Win Rate | 55-60% | 54-58% | 55-62% | 52-60% | 48-54% | 52-58% |
| Profit Factor | 1.5-2.0 | 1.3-1.8 | 1.6-2.2 | 1.4-1.9 | 1.8-2.5 | 1.4-1.9 |
| Avg Trade | 45 min | 60 min | 20 min | 25 min | 2-3 days | 30 min |
| Max DD | 12% | 15% | 10% | 8% | 20% | 10% |

---

## 🚀 EXPECTED TIMELINE

| Task | Time | Status |
|------|------|--------|
| Strategy 1 test & decision | 30 min | ⏳ IN PROGRESS |
| Strategy 2 test & decision | 30 min | ⏳ QUEUED |
| Strategy 3 test & decision | 30 min | ⏳ QUEUED |
| Strategy 4 test & decision | 30 min | ⏳ QUEUED |
| Strategy 5 test & decision | 30 min | ⏳ QUEUED |
| Strategy 6 test & decision | 30 min | ⏳ QUEUED |
| Strategy 7 test & decision | 30 min | ⏳ QUEUED |
| Strategy 8 test & decision | 30 min | ⏳ QUEUED |
| **TOTAL** | **4 hours** | **All strategies** |

**Expected Completion**: 2026-06-06 evening (same day if testing continuously)

---

## 📁 FILE STRUCTURE

```
C:\Case Capital\Axiom day trading\
├── strategies/
│   ├── futures_orb_us_open.pine ✅
│   ├── equities_orb_aapl.pine ✅
│   ├── futures_vwap_mean_reversion.pine ✅
│   ├── equities_vwap_mean_reversion.pine ✅
│   ├── crypto_rsi_mean_reversion.pine ✅
│   ├── futures_london_orb.pine ✅
│   ├── crypto_ema_trend.pine ✅
│   └── crypto_session_breakout.pine ✅
│
├── STRATEGY_INDEX.md (this file)
├── STRATEGY_1_SETUP_GUIDE.md
├── QUICK_START_STRATEGY_1.txt
├── STRATEGY_BUILD_STATUS.md
└── backtest_results.json
```

---

## 🎓 NEXT PHASES (After All 8 Strategies Validated)

### Phase 4: Confluence Scoring Integration
- Read LuxAlgo SMC values for each strategy
- Add 0-10 confluence scoring
- Filter entries by minimum score (3-5 points)
- Expected improvement: +3-5% win rate

### Phase 5: Market Regime Integration  
- Detect TRENDING vs CHOPPY vs VOLATILE days
- Route to optimal strategy per market condition
- Expected improvement: +2-3% win rate

### Phase 6: Live Deployment
- Deploy all validated strategies to live chart
- Monitor first 100 trades
- Track slippage vs backtest
- Fine-tune execution parameters

---

## ⚠️ IMPORTANT NOTES

✅ **All strategies use**:
- ATR-based stops (NOT fixed points)
- Dynamic targets (swing structure)
- Volume confirmation
- Session time filters
- Risk = 1% per trade

❌ **Avoid**:
- Fixed point stops/targets
- Trading outside session hours
- Ignoring commission & slippage
- Over-optimizing parameters

📊 **Minimum data**: 2+ years of minute-level bars  
📊 **Minimum validation**: 100 trades per strategy  
📊 **Realistic expectations**: 50-60% win rate, 1.3-1.8 profit factor  

---

## 🎬 ACTION REQUIRED

**User must**:
1. Open TradingView
2. Load ES1! 5-minute chart
3. Follow `STRATEGY_1_SETUP_GUIDE.md`
4. Run backtest
5. Report results back with metrics
6. I will evaluate and provide next strategy

**Current Status**: Awaiting Strategy 1 backtest results...

---

**Generated by**: AXIOM Development System  
**Version**: v2.0 Phase 3 Complete  
**Date**: 2026-06-06
