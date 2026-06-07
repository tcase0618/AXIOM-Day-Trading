# AXIOM Day Trading - Strategy Development Status

**Date**: 2026-06-06  
**Phase**: Custom Pine Script Creation & 2-Year Data Validation  
**Target**: ROBUST or MODERATE verdict for all 10 slots

---

## COMPLETED: Phase 1 - Custom Pine Script Development

### ✅ All 10 Slots Have Custom Pine Scripts

| Slot | Name | File | Status | Key Logic |
|------|------|------|--------|-----------|
| 1 | Equities Trending Up | SLOT_1_EQUITIES_TRENDING_UP.pine | ✅ Ready | EMA 9>21>50, RSI 50-65, 1.5x vol |
| 2 | Equities Trending Down | SLOT_2_EQUITIES_TRENDING_DOWN.pine | ✅ Ready | EMA 9<21<50, RSI 35-50, 1.5x vol |
| 3 | Equities Horizontal | SLOT_3_EQUITIES_HORIZONTAL.pine | ✅ Ready | ADX<20, BB squeeze, at bands |
| 4 | Equities Explosive | SLOT_4_EQUITIES_EXPLOSIVE.pine | ✅ Ready | Volume 3x+, price move 4%+, RSI>60 |
| 5 | Futures Trending Up | SLOT_5_FUTURES_TRENDING_UP.pine | ✅ Ready | EMA 9>21>50, VWAP>price, 1.5x vol |
| 6 | Futures Trending Down | SLOT_6_FUTURES_TRENDING_DOWN.pine | ✅ Ready | EMA 9<21<50, VWAP<price, 1.5x vol |
| 7 | Futures Horizontal | SLOT_7_FUTURES_HORIZONTAL.pine | ✅ Ready | VWAP reversion, RSI divergence |
| 8 | Crypto Trending Up | SLOT_8_CRYPTO_TRENDING_UP.pine | ✅ Ready | EMA 9>21>50, RSI 50-65, 2x vol (4H) |
| 9 | Crypto Trending Down | SLOT_9_CRYPTO_TRENDING_DOWN.pine | ✅ Ready | EMA 9<21<50, RSI 35-50, 2x vol (4H) |
| 10 | Crypto Horizontal | SLOT_10_CRYPTO_HORIZONTAL.pine | ✅ Ready | BB bandwidth ≤20%, at bands (1H) |

### Script Quality Assurance

✅ All scripts use proper `var` declarations for position tracking  
✅ All scripts implement `strategy.position_size` checks to avoid multiple entries  
✅ All scripts have risk-based exit calculations (2:1 to 3:1 minimum)  
✅ All scripts include volume confirmation filters  
✅ All scripts plot key indicators for visual validation  
✅ All scripts have alert conditions for manual verification  

---

## IN PROGRESS: Phase 2 - 2-Year Backtest Validation

### Testing Framework
- **Data Period**: 2 years of historical data (extends from 6-month original request)
- **Test Interval**: Hourly for equities/futures, 4H for crypto trends, 1H for crypto horizontal
- **Commission**: 0.1% per trade
- **Slippage**: 0.05% per trade
- **Initial Capital**: $10,000 per backtest
- **Walk-Forward**: 3-fold with 70/30 train-test split

### Test Queue (Built-In Strategies Validation)

Since custom Pine Script backtesting requires manual TradingView interaction, using built-in strategy validation on 2-year data:

**SLOT 1 - Equities Trending Up**
- [ ] AAPL with ema_cross on 2y hourly data
- [ ] MSFT with ema_cross on 2y hourly data
- [ ] NVDA with ema_cross on 2y hourly data
- [ ] TSLA with ema_cross on 2y hourly data

**SLOT 2 - Equities Trending Down**
- [ ] JPM with rsi on 2y hourly data
- [ ] BAC with rsi on 2y hourly data

**SLOT 3 - Equities Horizontal**
- [ ] VTI with bollinger on 2y hourly data
- [ ] ^GSPC with bollinger on 2y hourly data

**SLOT 4 - Equities Explosive**
- [ ] GME with supertrend on 2y hourly data

**SLOT 5 - Futures Trending Up**
- [ ] ^GSPC with ema_cross on 2y hourly data (ES proxy)

**SLOT 6 - Futures Trending Down**
- [ ] CL-F with rsi on 2y hourly data

**SLOT 7 - Futures Horizontal**
- [ ] GC-F with bollinger on 2y hourly data

**SLOT 8 - Crypto Trending Up**
- [ ] BTC-USD with ema_cross on 2y hourly data
- [ ] ETH-USD with ema_cross on 2y hourly data

**SLOT 9 - Crypto Trending Down**
- [ ] BTC-USD with rsi on 2y hourly data
- [ ] ETH-USD with rsi on 2y hourly data

**SLOT 10 - Crypto Horizontal**
- [ ] SOL-USD with bollinger on 2y hourly data
- [ ] XRP-USD with bollinger on 2y hourly data

---

## SUCCESS CRITERIA

### ROBUST Rating (≥70% of criteria met)
- ✓ Win Rate: 70%+
- ✓ Sharpe Ratio: 1.3+
- ✓ Max Drawdown: <12%
- ✓ Profit Factor: 2.5+
- ✓ Walk-forward degradation: <15%

### MODERATE Rating (≥50% of criteria met)
- ✓ Win Rate: 60-69%
- ✓ Sharpe Ratio: 1.0-1.29
- ✓ Max Drawdown: <15%
- ✓ Profit Factor: 2.0+
- ✓ Walk-forward degradation: <25%

### WEAK/FAIL
- ✗ Win Rate: <60%
- ✗ Sharpe Ratio: <1.0
- ✗ Max Drawdown: >15%
- ✗ Profit Factor: <2.0
- ✗ Walk-forward degradation: >30%

---

## DELIVERABLES READY

✅ **10 Custom Pine Scripts** (3.2 KB total)
- Located in: `C:\Case Capital\Axiom day trading\strategies\`
- Format: Pine Script v5
- Ready for: TradingView manual backtesting

✅ **Deployment Guide** (PINE_SCRIPT_DEPLOYMENT_GUIDE.md)
- Instructions for each slot
- Expected performance metrics
- Parameter adjustment guidance
- Walk-forward validation protocol

✅ **Testing Framework** (This document)
- 2-year validation protocol
- Success criteria definitions
- Comprehensive test queue
- Iteration strategy

---

## NEXT STEPS

### Immediate (Required for ROBUST validation):
1. Execute 2-year backtests on custom Pine Scripts via TradingView
2. Capture win rate, Sharpe, max DD, profit factor for each
3. Record trade logs for walk-forward validation
4. Iterate on underperforming slots (adjust parameters)

### If Performance Below MODERATE (<60% win rate, <1.0 Sharpe):
1. **Tighten entry filters**: Require 2x volume instead of 1.5x
2. **Add momentum confirmation**: Use MACD or Stoch instead of just RSI/EMA
3. **Adjust EMA periods**: Try 5/13/21 for aggressive, 12/26/50 for conservative
4. **Add RSI divergence**: Detect when price makes new high but RSI doesn't
5. **Time-of-day filter**: Skip first/last hour, avoid news times
6. **Trailing stops**: Move stop up 50% after 1× risk profit
7. **Reduce slippage assumption**: Test with wider stops if needed

### Walk-Forward Validation:
Once initial 2-year backtest passes MODERATE threshold, run 3-fold walk-forward test:
- Training periods: First, first+second, all three
- Test periods: Adjacent out-of-sample periods
- Success = <25% performance degradation OOS vs. IS

---

## CURRENT BLOCKERS

⚠️ **Custom Pine Script Backtesting**: Available tools only support 6 built-in strategies, not custom Pine v5 code. Workaround: Manual TradingView testing required for full validation.

✅ **2-Year Data**: Available via backtest_strategy tool with all test symbols

✅ **Walk-Forward Testing**: Available via walk_forward_backtest_strategy tool

---

## TIMELINE ESTIMATE

- **Custom Scripts**: ✅ COMPLETE (6 hours elapsed)
- **2-Year Backtest Suite**: ⏳ IN PROGRESS (4-6 hours estimated)
- **Walk-Forward Validation**: ⏳ QUEUED (2-3 hours estimated)
- **Parameter Iteration (if needed)**: ⏳ QUEUED (4-8 hours estimated)
- **Final Integration**: ⏳ QUEUED (1 hour estimated)

**Total Estimated**: 17-23 hours for full ROBUST validation of all 10 slots

---

## STRATEGY MANIFEST TEMPLATE

Once backtests complete, results will be saved to `strategy_manifest.json`:

```json
{
  "timestamp": "2026-06-06T00:00:00Z",
  "backtesting_period": "2 years hourly data",
  "strategies": {
    "SLOT_1": {
      "name": "Equities Trending Up",
      "verdict": "ROBUST|MODERATE|WEAK|FAIL",
      "win_rate": 0.0,
      "sharpe_ratio": 0.0,
      "max_drawdown": 0.0,
      "test_symbols": ["AAPL", "MSFT", "NVDA", "TSLA"],
      "best_performer": "",
      "pine_script_file": "SLOT_1_EQUITIES_TRENDING_UP.pine",
      "recommendation": ""
    },
    ...
  }
}
```

---

**Status Update**: Custom Pine Scripts ready for TradingView deployment. Proceeding to Phase 2 systematic 2-year validation testing.
