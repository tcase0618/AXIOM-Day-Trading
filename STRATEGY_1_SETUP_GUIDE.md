# STRATEGY 1: FUTURES ORB US Open - ES1! 5min

## 📋 SETUP INSTRUCTIONS

### Step 1: Launch TradingView Desktop & Load Chart
1. Open **TradingView Desktop**
2. In chart search, type: **ES1!**
3. Set timeframe to **5 minutes**
4. Ensure the chart is displaying **ES1! (CME E-mini S&P 500)**

### Step 2: Add LuxAlgo Smart Money Concepts Indicator
1. In TradingView, click **"Indicators"** (bottom left)
2. Search: **"Smart Money Concepts"** (by LuxAlgo)
3. Click to add to chart
4. Configure settings (defaults are fine):
   - Order Blocks: ON
   - Fair Value Gaps: ON
   - Liquidity Sweeps: ON
   - Show Lines: ON

### Step 3: Inject the Strategy
1. Click **Pine Editor** (left sidebar)
2. Click **New Script** → **Strategy**
3. **DELETE all default code**
4. **COPY the entire code from**: `C:\Case Capital\Axiom day trading\strategies\futures_orb_us_open.pine`
5. **PASTE into Pine Editor**
6. Click **Save** (top left)
7. Name it: **"FUTURES ORB US Open - ES1!"**
8. Click **Add to Chart**

### Step 4: Backtest Settings
1. Click **Strategy Tester** (bottom panel)
2. Verify these settings:
   - **Data**: ES1! 5-minute
   - **Date Range**: 2024-01-01 to 2026-06-06 (2 years)
   - **Equity**: $100,000
   - **Commission**: 0.05%
   - **Slippage**: 2 points
3. Click **Run Backtest**
4. **Wait 1-2 minutes for results**

### Step 5: Record Results
Once backtest completes, capture:
- **Total Trades**
- **Win Rate %**
- **Profit Factor**
- **Max Drawdown %**
- **Net Profit/Loss**
- **Avg Trade Duration**

---

## 🎯 STRATEGY LOGIC

### Entry Rules:
1. **Opening Range (9:30-9:45 AM ET)**: Calculate high/low of first 15 minutes
2. **Breakout Entry**:
   - **LONG**: Price closes above ORB high + RSI > 50 + Volume > 1.5x avg
   - **SHORT**: Price closes below ORB low + RSI < 50 + Volume > 1.5x avg
3. **Maximum**: 2 trades per session

### Exit Rules:
1. **Stop Loss**: ATR × 1.5 (wider for futures volatility)
2. **Target**: 
   - Default: ATR × 2.0
   - Dynamic: Nearest swing high/low (if closer)
3. **Time Exit**: Close entire position after 90 minutes (9:30am → 11:00am)

### Higher Timeframe Context:
- 15-min EMA 21 plotted as bias reference (blue line)
- Best results when price above/below EMA aligned with direction

---

## 📊 ACCEPTANCE CRITERIA

✅ **PASS if**:
- Win Rate ≥ 55%
- Profit Factor ≥ 1.3
- Net PnL > 0 (positive)
- Max Drawdown ≤ 15%

⚠️ **ONE ITERATION if**:
- Win Rate 48-54%
- Profit Factor 1.1-1.29
- Will adjust: RSI threshold (45-55 range) or ATR multiplier (1.2-2.0)

❌ **NEEDS REVIEW if**:
- Win Rate < 48%
- Profit Factor < 1.1
- Net PnL negative
- Move to Strategy 2

---

## 🔧 PARAMETER ADJUSTMENT (if needed for one iteration)

If strategy fails acceptance criteria, try ONE of these:

**Option A: Loosen RSI Filter**
- Change line: `rsi > 50` → `rsi > 45`
- Change line: `rsi < 50` → `rsi < 55`

**Option B: Tighter ATR Stop**
- Change line: `stop_level := entry_price - (atr * 1.5)` → `(atr * 1.0)`
- Change line: `target_level := entry_price + (atr * 2.0)` → `(atr * 2.5)`

**Option C: Longer Time Exit**
- Change line: `bars_in_trade > 18` → `bars_in_trade > 24` (120 minutes instead of 90)

---

## 📝 NOTES

- **SMC Confluence**: The code is prepared to read LuxAlgo SMC values in future iterations
- **Current Version**: Uses simple ORB + RSI + volume baseline
- **Historical Data**: Requires 2+ years of ES1! 5-minute data for valid backtest
- **Slippage**: 2-point slippage assumes typical ES1! micro-second execution delays

---

## ⏭️ NEXT STEPS

1. Follow setup steps 1-4 above
2. Wait for backtest to complete
3. Record all metrics
4. Report results in format:
```
STRATEGY 1 BACKTEST RESULTS
Symbol: ES1!
Timeframe: 5-minute
Period: 2024-01-01 to 2026-06-06

Total Trades: [X]
Win Rate: [X]%
Profit Factor: [X]
Max Drawdown: [X]%
Net Profit: $[X]
Avg Trade Duration: [X] minutes

Status: [PASS / ONE ITERATION / NEEDS REVIEW]
```

5. If PASS → Proceed to Strategy 2: EQUITIES ORB on AAPL
6. If ONE ITERATION → Adjust parameters and retest
7. If NEEDS REVIEW → Flag and move to Strategy 2
