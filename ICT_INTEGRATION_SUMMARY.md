# AXIOM Day Trading — ICT Integration Complete

**Status**: ✅ **COMPLETE** — All ICT concepts integrated into AXIOM pipeline  
**Date**: 2026-06-06  
**Target Asset Classes**: EQUITIES & FUTURES (Crypto unchanged)

---

## FILES CREATED

### Pine Scripts (5 new files)

#### 1. `strategies/ict_detector.pine` ✅
- **Purpose**: Real-time detection and plotting of ICT concepts on 5-minute chart
- **Concepts Detected**:
  - Fair Value Gaps (FVG) — bullish/bearish gaps with fill detection
  - Order Blocks (OB) — last candle before structure moves
  - Liquidity Sweeps — wick below/above then close opposite
  - Break of Structure (BOS) — close above/below prior swings
  - Change of Character (ChoCh) — BOS in opposite direction (HIGHEST PRIORITY)
  - Optimal Trade Entry (OTE) — 62-79% retracement zones
  - Premium/Discount Zones — 50% equilibrium levels
- **Outputs**: Color-coded zones, alerts, plots for all concepts
- **Status**: Ready for chart injection

#### 2. `strategies/liquidity_map.pine` ✅
- **Purpose**: Map resting liquidity pools that act as price magnets
- **Liquidity Levels Identified**:
  - Equal Highs/Lows (EQH/EQL) — retail stop clusters
  - Prior Session Highs/Lows — PDH, PDL, PWH, PWL
  - Swing Highs and Lows — all significant structure
  - Buy/Sell Side Liquidity Zones — retail stops above/below extremes
  - Liquidity Magnet Score (1-10) — probability weighting for each level
  - Daily Bias Indicator — BULLISH/BEARISH/NEUTRAL based on liquidity distribution
- **Status**: Ready for chart injection

#### 3. `strategies/slot12_ict_price_action_equities.pine` ✅
- **Strategy**: ICT Price Action Entry (EQUITIES)
- **Entry Window**: 9:30am - 4:00pm EST
- **Entry Conditions** (ALL required for maximum confluence):
  - BOS or ChoCh detected
  - Price pulling back to OTE zone (62-79% retracement)
  - Pullback touches Order Block OR enters FVG
  - RSI shows divergence at pullback
  - Volume weak (below average) on pullback
- **Entry**: First 5min candle closing back in BOS direction
- **Stop**: At OB level (ICT-style placement)
- **Target**: Next liquidity (prior swing high/low)
- **Risk**: 1% of account
- **Max Trades**: 2 per session
- **Status**: Ready for backtesting
- **Test Symbols**: AAPL, MSFT, NVDA

#### 4. `strategies/slot13_ict_price_action_futures.pine` ✅
- **Strategy**: ICT Price Action Entry (FUTURES)
- **Entry Window**: 24/7 (all futures sessions)
- **Key Difference**: ORB + OTE confluence is maximum conviction setup
- **Entry Conditions**:
  - ORB detected (on 15-minute structure)
  - Pullback to OTE zone of ORB move
  - Price at Order Block or FVG
  - RSI divergence
  - Volume weak
- **Entry**: First 5min candle after pullback closes back in ORB direction
- **Stop**: Wider (1.5x ATR) for futures volatility
- **Target**: Next session liquidity (prior session high/low)
- **Max Trades**: 2 per session
- **Status**: Ready for backtesting
- **Test Symbols**: ES1!, NQ1!

---

## PYTHON FILES UPDATED/CREATED

### 1. `ict_confluence.py` ✅ (NEW)
**Purpose**: ICT Confluence Scoring System

**Scoring System**:
```
+2: Order Block (unmitigated)
+2: Fair Value Gap (unfilled)
+2: Liquidity Sweep (recent)
+2: Optimal Trade Entry (OTE zone)
+1: Discount Zone (longs) / Premium Zone (shorts)
+1: Change of Character (ChoCh)
─────
Max: 10 points
Min to trade: 3 points (for EQUITIES/FUTURES only)
```

**Functions**:
- `ICTConfluenceScorer.score_setup()` — Calculate score based on confluence factors
- `ICTConfluenceScorer.is_tradable()` — Check if score meets minimum threshold
- `calculate_ict_score()` — Convenience function for webhook integration

**Integration**: Imported by `webhook_handler.py`

---

### 2. `webhook_handler.py` ✅ (UPDATED)
**Changes**:
- ✅ Added `from ict_confluence import calculate_ict_score`
- ✅ Added `ICT_CONTEXT_FIELDS` for optional ICT parameters
- ✅ Calculate ICT confluence score from incoming payload
- ✅ Validate minimum score threshold (3/10) for EQUITIES/FUTURES
- ✅ Return error if below threshold (EQUITIES/FUTURES only)
- ✅ Add `ict_score` and `ict_factors` to `trade_data` dict

**New Payload Fields** (optional):
```json
{
  "at_order_block": true,
  "in_fvg": false,
  "liquidity_sweep": true,
  "in_ote_zone": true,
  "in_discount_zone": false,
  "in_premium_zone": false,
  "choch_detected": false
}
```

**Minimum ICT Score Filter**: Only EQUITIES and FUTURES require 3+ score. Crypto unaffected.

---

### 3. `telegram_service.py` ✅ (UPDATED)
**Changes**:
- ✅ Added `ict_score` and `ict_factors` to message template
- ✅ Display ICT line in alert: `ICT Confluence: {score}/10 | {factors}`
- ✅ Example output: `ICT Confluence: 7/10 | OB + FVG + OTE`

**New Message Section**:
```
ICT Confluence: 7/10 | OB + FVG + OTE
```
Appears after Confidence line, before final separator.

---

### 4. `regime_detector.py` ✅ (UPDATED)
**Changes**:
- ✅ Added `get_liquidity_bias()` function
  - Calculates BULLISH/BEARISH/NEUTRAL based on price position vs 20-day range
  - Returns liquidity bias to inform directional bias
  
- ✅ Updated `get_algo_for_regime()` to include liquidity bias
  - Appends bias context: "(LONGS ONLY)" for BULLISH, "(SHORTS ONLY)" for BEARISH
  
- ✅ Updated `detect_regime()` to call `get_liquidity_bias()` and include in regime_data
  
- ✅ Updated `send_regime_report()` to display liquidity bias in daily report

**Liquidity Bias Application**:
- BULLISH bias: Only take LONG setups for that session
- BEARISH bias: Only take SHORT setups for that session
- NEUTRAL bias: Take both directions

---

## INTEGRATION PIPELINE

### Data Flow: Chart → Webhook → Telegram

```
┌─────────────────────────────────────────────────────────────────┐
│ TradingView LIVE (5-minute chart)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [ict_detector.pine]    [liquidity_map.pine]    [slot12/13.pine]│
│   ↓ Real-time ICT         ↓ Liquidity levels    ↓ Trade signal    │
│   detection              mapping              + ICT confluence    │
│                                                                   │
│  ┌─────────────────────────────────────────────────┐            │
│  │ Webhook Alert to: http://localhost:8001/webhook/tradingview  │
│  └─────────────────────────────────────────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                      [webhook_handler.py]
                            ↓
                 ┌──────────────────────────┐
                 │ Extract trade data       │
                 │ Calculate ICT score:     │
                 │  - Check OB              │
                 │  - Check FVG             │
                 │  - Check sweep           │
                 │  - Check OTE             │
                 │  - Check zones           │
                 │  - Check ChoCh           │
                 │ Score: 0-10              │
                 │ Min threshold: 3         │
                 └──────────────────────────┘
                            ↓
                      [Validation]
                      │
                      ├─ PASS (score ≥ 3) → Send to Telegram
                      ├─ FAIL (score < 3) → Reject alert
                      └─ CRYPTO → Skip validation (always trade)
                            ↓
                    [telegram_service.py]
                            ↓
                    ┌─────────────────────┐
                    │ Format message:     │
                    │ - Entry             │
                    │ - Stop/Target       │
                    │ - R:R               │
                    │ - Regime            │
                    │ ─────────────────   │
                    │ ICT Confluence:     │
                    │ {score}/10 | {fx}   │
                    │ ─────────────────   │
                    └─────────────────────┘
                            ↓
                    Send to Telegram 💬
```

---

## REGIME DETECTION INTEGRATION

**Daily Regime Report** (sent at 8am EST):
```
AXIOM DAY TRADING
📊 DAILY REGIME REPORT
─────────────────────
Date: 2026-06-06
VIX: 16.5
SPY Trend: BULLISH
ADX: 28.3
Breadth: 85%
Liquidity Bias: BULLISH
─────────────────────
EQUITIES: TRENDING | Momentum algo | Liquidity Bias: BULLISH (LONGS ONLY)
FUTURES: TRENDING | Momentum algo | Liquidity Bias: BULLISH (LONGS ONLY)
CRYPTO: TRENDING | Momentum Continuation algo | Liquidity Bias: BULLISH
─────────────────────
System Status: ACTIVE [OK]
```

**Liquidity Bias Application**:
- Stored in `current_regime.json`
- Read by webhook handler
- Filters entry conditions: only long setups if BULLISH, only shorts if BEARISH

---

## BACKTEST REQUIREMENTS

### SLOT 12 (Equities ICT)
- **Minimum Criteria**:
  - 30+ trades in 2-year backtest
  - Win rate ≥ 52%
  - R:R ratio ≥ 1.8:1
  - Max drawdown ≤ 15%
- **Test Symbols**: AAPL, MSFT, NVDA
- **Timeframe**: 5-minute
- **Status**: ⏳ Pending backtest

### SLOT 13 (Futures ICT)
- **Minimum Criteria**: Same as SLOT 12
- **Test Symbols**: ES1!, NQ1!
- **Timeframe**: 5-minute
- **Status**: ⏳ Pending backtest

---

## FILE STRUCTURE

```
C:\Case Capital\Axiom day trading
├── main.py (FastAPI server — unchanged)
├── webhook_handler.py ✅ (UPDATED — ICT scoring added)
├── telegram_service.py ✅ (UPDATED — ICT score display)
├── regime_detector.py ✅ (UPDATED — liquidity bias)
├── ict_confluence.py ✅ (NEW — ICT scoring system)
├── current_regime.json (auto-generated daily)
├── strategies/
│   ├── slot1_momentum_up.pine
│   ├── slot2_momentum_down.pine
│   ├── ... (existing slots 1-11)
│   ├── slot12_ict_price_action_equities.pine ✅ (NEW)
│   ├── slot13_ict_price_action_futures.pine ✅ (NEW)
│   ├── ict_detector.pine ✅ (NEW)
│   └── liquidity_map.pine ✅ (NEW)
└── ICT_INTEGRATION_SUMMARY.md (this file)
```

---

## DEPLOYMENT CHECKLIST

- [x] Create ict_detector.pine (all 7 ICT concepts)
- [x] Create liquidity_map.pine (7 liquidity levels)
- [x] Create slot12_ict_price_action_equities.pine
- [x] Create slot13_ict_price_action_futures.pine
- [x] Create ict_confluence.py (scoring system)
- [x] Update webhook_handler.py (ICT validation)
- [x] Update telegram_service.py (ICT display)
- [x] Update regime_detector.py (liquidity bias)
- [ ] Backtest slot12 on AAPL, MSFT, NVDA
- [ ] Backtest slot13 on ES1!, NQ1!
- [ ] Deploy Pine Scripts to TradingView chart
- [ ] Validate ICT score calculations in production
- [ ] Monitor first 10 trades for ICT confluence accuracy

---

## ICT CONFLUENCE SCORING EXAMPLES

### Trade 1: AAPL Long, High Confluence
```
✅ At Order Block (+2)
✅ In FVG (+2)
✅ Liquidity Sweep (+2)
⚪ OTE zone (−)
⚪ Discount zone (−)
✅ ChoCh detected (+1)
─────────────
SCORE: 7/10 | Factors: OB + FVG + Sweep + ChoCh
STATUS: PASS (≥ 3) → Trade executed
```

### Trade 2: SPY Short, Low Confluence
```
⚪ Order Block (−)
✅ In FVG (+2)
⚪ Sweep (−)
⚪ OTE zone (−)
⚪ Premium zone (−)
⚪ ChoCh (−)
─────────────
SCORE: 2/10 | Factors: FVG
STATUS: FAIL (< 3) → Alert rejected
```

### Trade 3: ES1! Long, Medium Confluence
```
✅ At Order Block (+2)
⚪ FVG (−)
✅ Sweep (+2)
✅ OTE zone (+2)
⚪ Discount zone (−)
⚪ ChoCh (−)
─────────────
SCORE: 6/10 | Factors: OB + Sweep + OTE
STATUS: PASS (≥ 3) → Trade executed
```

---

## KEY FEATURES

✅ **Automated ICT Detection**: No manual chart analysis required  
✅ **Confluence Filtering**: Minimum 3/10 score prevents low-quality entries  
✅ **Multi-Concept Integration**: 7 ICT concepts + 7 liquidity levels  
✅ **Crypto Unaffected**: Only EQUITIES/FUTURES require ICT filtering  
✅ **Liquidity Bias**: Regime detector now includes market structure  
✅ **Telegram Alerts**: Real-time ICT scores in trade messages  
✅ **Scalable**: Can add more confluence factors as needed  

---

## NEXT STEPS

1. **Backtest SLOT 12**: Inject on AAPL/MSFT/NVDA, run Strategy Tester
2. **Backtest SLOT 13**: Inject on ES1!/NQ1!, run Strategy Tester
3. **Monitor Results**: Track ICT score accuracy vs. actual trade performance
4. **Optimize Thresholds**: Adjust minimum score (currently 3) based on results
5. **Live Deployment**: Once backtests pass, deploy to live chart

---

**Integration Status**: ✅ **COMPLETE**  
**Testing Status**: ⏳ Pending  
**Deployment Status**: ⏳ Ready for backtest
