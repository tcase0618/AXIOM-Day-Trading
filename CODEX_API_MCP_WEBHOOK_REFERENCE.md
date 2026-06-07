# AXIOM DAY TRADING - COMPLETE API & MCP REFERENCE FOR CODEX
**Generated: 2026-06-07 | For AI Assistant Integration**

---

## TABLE OF CONTENTS
1. [MCP Servers](#mcp-servers)
2. [REST APIs](#rest-apis)
3. [Webhooks & Triggers](#webhooks--triggers)
4. [Authentication](#authentication)
5. [Data Formats](#data-formats)
6. [Integration Examples](#integration-examples)
7. [Current System State](#current-system-state)

---

## MCP SERVERS

### 1. TRADINGVIEW-LIVE (78 Tools)
**Base Protocol:** Model Context Protocol (MCP)
**Status:** ACTIVE & LOADED
**Purpose:** Real-time TradingView Desktop chart control and data retrieval

#### Tools by Category:

##### Chart Control (6 tools)
```
- chart_set_symbol(symbol: str)
  └─ Changes the current chart symbol (e.g., "ES1!", "SPY", "AAPL")

- chart_set_timeframe(timeframe: str)
  └─ Sets chart timeframe (e.g., "5", "15", "60", "D", "W")

- chart_set_type(type: str)
  └─ Sets chart type ("candlestick", "line", "bar", "heikin_ashi")

- chart_scroll_to_date(date: str)
  └─ Jumps to specific date (ISO format: "2026-06-07")

- chart_get_state()
  └─ Returns current symbol, timeframe, indicators, entity IDs

- chart_get_visible_range()
  └─ Returns visible bar range on current chart
```

##### Data Retrieval (10 tools)
```
- data_get_ohlcv(summary=true)
  └─ Gets OHLCV bars (when summary=true: returns count only, else full bars)
  └─ Returns: [{time, open, high, low, close, volume}, ...]

- data_get_study_values(study_id: str)
  └─ Gets current indicator values (RSI, MACD, Bollinger Bands, EMA, etc.)
  └─ Returns: {indicator_name: {values: [...]}}

- data_get_strategy_results()
  └─ Gets backtest metrics from strategy tester
  └─ Returns: {total_trades, win_rate, profit_factor, max_drawdown, net_pnl}

- data_get_equity()
  └─ Gets equity curve data

- quote_get()
  └─ Gets real-time price snapshot
  └─ Returns: {last, open, high, low, close, volume, bid, ask}

- data_get_pine_lines(study_filter: str)
  └─ Gets horizontal lines from Pine Script indicators
  └─ Returns: [{price, style, color}, ...]

- data_get_pine_labels(study_filter: str)
  └─ Gets text labels from Pine indicators
  └─ Returns: [{text, price, time}, ...]

- data_get_pine_boxes(study_filter: str)
  └─ Gets drawn boxes (price zones)
  └─ Returns: [{high, low}, ...]

- data_get_pine_tables(study_filter: str)
  └─ Gets table data from Pine indicators
  └─ Returns: {rows: [[cell1, cell2, ...], ...]}

- data_get_trades()
  └─ Gets individual trade data from strategy tester
  └─ Returns: [{entry_time, entry_price, exit_time, exit_price, pnl}, ...]
```

##### Pine Script Development (10 tools)
```
- pine_new(name: str, indicator_type: str)
  └─ Creates new Pine Script (type: "indicator", "strategy", "library")

- pine_open(script_name: str)
  └─ Opens existing script by name

- pine_set_source(source_code: str)
  └─ Injects Pine Script source code

- pine_get_source()
  └─ Retrieves current script source (WARNING: can return 200KB+)

- pine_smart_compile()
  └─ Compiles and validates Pine Script, returns errors if any

- pine_check()
  └─ Syntax check without compilation

- pine_compile()
  └─ Full compilation

- pine_get_errors()
  └─ Returns compilation errors array

- pine_get_console()
  └─ Returns console output (debug statements)

- pine_list_scripts()
  └─ Lists all user Pine Scripts on account
```

##### Indicator Management (3 tools)
```
- chart_manage_indicator(action: "add"|"remove", indicator_name: str)
  └─ Adds/removes indicators (use FULL names: "Relative Strength Index" not "RSI")

- indicator_set_inputs(indicator_id: str, inputs: dict)
  └─ Changes indicator settings (length, source, etc.)
  └─ Example: {"length": 14, "source": "close"}

- indicator_toggle_visibility(indicator_id: str)
  └─ Shows/hides indicator on chart
```

##### Drawing & Markup (5 tools)
```
- draw_shape(type: str, coordinates: dict, style: dict)
  └─ Types: "horizontal_line", "trend_line", "rectangle", "text"
  └─ Example: draw_shape("horizontal_line", {"price": 425.50}, {"color": "red"})

- draw_get_properties(shape_id: str)
  └─ Gets drawing properties

- draw_list()
  └─ Lists all drawings on chart
  └─ Returns: [{id, type, properties}, ...]

- draw_remove_one(shape_id: str)
  └─ Removes single drawing

- draw_clear()
  └─ Removes all drawings
```

##### Alerts (3 tools)
```
- alert_create(condition: str, message: str)
  └─ Creates TradingView alert
  └─ Example: condition="close > 425", message="Price above 425"

- alert_list()
  └─ Lists all active alerts
  └─ Returns: [{id, condition, message}, ...]

- alert_delete(alert_id: str)
  └─ Deletes alert by ID
```

##### Replay Engine (5 tools)
```
- replay_start(date: str, time: str)
  └─ Starts replay from specific datetime
  └─ Format: date="2026-06-07", time="09:30"

- replay_step(bars: int)
  └─ Advances replay by N bars (default 1)

- replay_trade()
  └─ Executes next strategy trade in replay

- replay_status()
  └─ Returns current replay position and metrics

- replay_stop()
  └─ Stops replay
```

##### Utilities (10+ tools)
```
- capture_screenshot(region: str)
  └─ Takes screenshot (region: "full"|"chart"|"strategy_tester")

- batch_run(symbols: list, action: str)
  └─ Runs action across multiple symbols

- tv_health_check()
  └─ Verifies TradingView connection

- tv_launch()
  └─ Launches TradingView application

- tab_new(), tab_switch(), tab_close()
  └─ Tab management

- layout_list(), layout_switch()
  └─ Save/load chart layouts

- pane_list(), pane_focus(), pane_set_layout()
  └─ Pane management

- symbol_search(), symbol_info()
  └─ Symbol lookup and info

- depth_get()
  └─ Gets depth of market data
```

---

### 2. TRADINGVIEW-SCANNER (Market Screener)
**Base Protocol:** Model Context Protocol (MCP)
**Status:** ACTIVE & LOADED
**Purpose:** Real-time multi-market scanning and technical analysis

#### Tools by Category:

##### Stock Screeners (8 tools)
```
- top_gainers()
  └─ Returns top gaining stocks
  └─ Returns: [{symbol, change%, price, volume}, ...]

- top_losers()
  └─ Returns top losing stocks

- bollinger_scan(deviation: float, symbol: str)
  └─ Scans for Bollinger Band breakouts

- volume_breakout_scanner()
  └─ Finds volume breakout setups

- consecutive_candles_scan(pattern: str)
  └─ Scans for candle patterns (bullish/bearish)

- smart_volume_scanner()
  └─ Advanced volume analysis

- advanced_candle_pattern()
  └─ Pattern recognition (engulfing, hammer, doji, etc.)

- rating_filter(min_rating: float)
  └─ Filters by TradingView ratings
```

##### Multi-Timeframe Analysis (5 tools)
```
- multi_agent_analysis(symbol: str, timeframes: list)
  └─ Runs multi-agent evaluation
  └─ Returns: {decision, confidence, technical_score, sentiment_score, risk_score}

- multi_timeframe_analysis(symbol: str)
  └─ Analyzes across 1m, 5m, 15m, 60m, daily

- combined_analysis(symbol: str)
  └─ Combines all analysis types

- compare_strategies(symbol: str, strategies: list)
  └─ Compares multiple strategy performance

- walk_forward_backtest_strategy(symbol: str, strategy: str)
  └─ Runs walk-forward validation
```

##### Backtesting (2 tools)
```
- backtest_strategy(symbol: str, strategy: str, period: str)
  └─ Backtests strategy on historical data
  └─ Returns: {total_trades, win_rate, profit_factor, max_drawdown, net_pnl}

- walk_forward_backtest_strategy(symbol: str, strategy: str)
  └─ Advanced validation with forward testing
```

##### Market Analysis (3 tools)
```
- market_snapshot()
  └─ Current market overview
  └─ Returns: {indices, sectors, market_sentiment}

- market_sentiment()
  └─ Overall market sentiment (bullish/neutral/bearish)

- financial_news()
  └─ Latest financial news affecting markets
```

##### Crypto (1 tool)
```
- coin_analysis(symbol: str)
  └─ Cryptocurrency analysis
  └─ Supports: BTC, ETH, major altcoins on KuCoin, Binance, Bybit, MEXC
```

##### Egyptian Exchange (7 tools)
```
- egx_market_overview()
- egx_sector_scan()
- egx_sector_scanner()
- egx_stock_screener()
- egx_trade_plan()
- egx_fibonacci_retracement()
- egx_index_analysis()
```

##### Utilities (2 tools)
```
- yahoo_price(symbol: str)
  └─ Gets current price from Yahoo Finance

- financial_news(symbol: str)
  └─ Gets news for specific symbol
```

#### Supported Exchanges
```
Stocks: NASDAQ, NYSE
Crypto: Binance, KuCoin, Bybit, MEXC
International: EGX (Egypt), BIST (Turkey), HKEX (Hong Kong), SSE (China), SZSE (China)
```

---

### 3. OTHER MCPs (Available on Demand)
**Load via: ToolSearch("select:<mcp_name>")**

```
- claude-in-chrome
  └─ Browser automation (navigate, click, fill forms, read pages)

- claude-preview
  └─ UI testing and preview screenshots

- scheduled-tasks
  └─ Schedule cron jobs and automated tasks

- mcp-registry
  └─ Discover and search for more MCPs
```

---

## REST APIs

### 1. REMOTE TRIGGER API (Claude)
**Endpoint:** `https://claude.ai/v1/code/triggers`
**Authentication:** OAuth (auto-added in-process)
**Purpose:** Schedule and execute Python code remotely

#### Endpoints

```http
LIST All Triggers
  GET /v1/code/triggers
  Response: {triggers: [{id, name, schedule, created_at}, ...]}

GET Specific Trigger
  GET /v1/code/triggers/{trigger_id}
  Response: {id, name, schedule, code, created_at}

CREATE New Trigger
  POST /v1/code/triggers
  Body: {
    "name": "Daily ORB Backtest",
    "schedule": "0 9 * * MON-FRI",  // Cron format (9 AM weekdays)
    "code": "python backtest_orb_real_data.py"
  }
  Response: {id, url: "https://claude.ai/..."}

UPDATE Trigger
  POST /v1/code/triggers/{trigger_id}
  Body: {schedule: "0 9 * * *", code: "..."}

RUN Trigger
  POST /v1/code/triggers/{trigger_id}/run
  Optional Body: {override_params: {...}}
  Response: {status: "running|completed", output: "...", duration_ms: 1234}
```

#### Cron Schedule Format
```
*    *    *    *    *
┬    ┬    ┬    ┬    ┬
│    │    │    │    └─── Day of week (0-7, 0/7=Sunday)
│    │    │    └──────── Month (1-12)
│    │    └───────────── Day of month (1-31)
│    └────────────────── Hour (0-23)
└─────────────────────── Minute (0-59)

Examples:
0 9 * * MON-FRI    → 9:00 AM weekdays
0 9,16 * * *       → 9:00 AM & 4:00 PM daily
*/30 9-16 * * *    → Every 30 min, 9 AM - 4 PM
0 0 * * *          → Midnight daily
```

---

### 2. ALPHA VANTAGE API
**Base URL:** `https://www.alphavantage.co/query`
**API Key:** `H62ZC5DSZT4WB86J`
**Rate Limit:** 5 calls/minute, 500/day (free tier)
**Purpose:** Historical and real-time market data

#### Endpoints

```http
INTRADAY DATA
  GET /query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&apikey={KEY}
  
  Query Params:
    function=TIME_SERIES_INTRADAY (required)
    symbol=SPY (required)
    interval=5min|15min|60min (required - 5min is PREMIUM ONLY on free tier)
    outputsize=compact|full (default: compact = last 100 bars)
    datatype=json|csv (default: json)
    apikey={API_KEY} (required)
  
  Response:
  {
    "Meta Data": {...},
    "Time Series (5min)": {
      "2026-06-07 16:00:00": {
        "1. open": "425.50",
        "2. high": "425.75",
        "3. low": "425.25",
        "4. close": "425.60",
        "5. volume": "15234"
      },
      ...
    }
  }

DAILY DATA (FREE TIER OK)
  GET /query?function=TIME_SERIES_DAILY&symbol=SPY&apikey={KEY}
  
  Same params as INTRADAY but no interval needed

TECHNICAL INDICATORS
  GET /query?function=RSI&symbol=SPY&interval=5min&time_period=14&apikey={KEY}
  
  Available: RSI, MACD, STOCH, ADX, CCI, ATR, BBANDS, EMA, SMA, etc.
```

#### Python Integration
```python
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

API_KEY = "H62ZC5DSZT4WB86J"
ts = TimeSeries(key=API_KEY, output_format='pandas')
ti = TechIndicators(key=API_KEY, output_format='pandas')

# Get daily data (works on free tier)
data, meta = ts.get_daily(symbol="SPY")

# Get intraday (5min requires PREMIUM)
data, meta = ts.get_intraday(symbol="SPY", interval="5min")

# Get indicators
rsi, meta = ti.get_rsi(symbol="SPY", interval="5min", time_period=14)
atr, meta = ti.get_atr(symbol="SPY", interval="5min", time_period=14)
```

---

### 3. YFINANCE API (FREE)
**Base:** Python library (no API key needed, unlimited calls)
**Purpose:** Free 5-minute intraday data, daily data

#### Python Integration
```python
import yfinance as yf
from datetime import datetime, timedelta

# Get intraday data (5-min)
ticker = yf.Ticker("SPY")
hist = ticker.history(interval="5m", period="60d")
# Returns: DataFrame with Open, High, Low, Close, Volume columns

# Iterate through bars
for date, row in hist.iterrows():
    print(f"{date}: Close={row['Close']}, Volume={row['Volume']}")

# Get daily data
hist = ticker.history(period="1y")

# Access individual fields
hist['Close']       # Series of closing prices
hist['Volume']      # Series of volumes
hist.iloc[-1]       # Latest bar
```

#### Data Structure
```python
{
  'Open': float,
  'High': float,
  'Low': float,
  'Close': float,
  'Volume': int,
  'Dividends': float,
  'Stock Splits': float
}
```

---

### 4. ANTHROPIC CLAUDE API
**Endpoint:** `https://api.anthropic.com/v1/messages`
**API Key:** Configured via `ANTHROPIC_API_KEY` environment variable
**Model:** `claude-3-5-sonnet-20241022`
**Purpose:** LLM-powered multi-agent analysis

#### Python Integration
```python
import anthropic
import json

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Analyze this chart for bullish setup..."
        }
    ]
)

response_text = message.content[0].text
print(response_text)
```

#### Multi-Agent Evaluation Pattern
```python
def technical_analyst(ticker: str, market_data: dict) -> dict:
    """Agent 1: Technical Analysis"""
    prompt = f"Analyze {ticker} chart: {json.dumps(market_data)}"
    response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=400,
                                     messages=[{"role": "user", "content": prompt}])
    return json.loads(response.content[0].text)

def sentiment_analyst(ticker: str) -> dict:
    """Agent 2: Market Sentiment"""
    prompt = f"Sentiment for {ticker}: bullish/bearish/neutral?"
    response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=300,
                                     messages=[{"role": "user", "content": prompt}])
    return json.loads(response.content[0].text)

def risk_manager(entry: float, stop: float, target: float) -> dict:
    """Agent 3: Risk Validation"""
    rr = (target - entry) / (entry - stop)
    prompt = f"Validate risk setup: Entry={entry}, Stop={stop}, Target={target}, R:R={rr}"
    response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=300,
                                     messages=[{"role": "user", "content": prompt}])
    return json.loads(response.content[0].text)

def trader_decision(technical: dict, sentiment: dict, risk: dict) -> dict:
    """Agent 4: Final Decision"""
    prompt = f"""Make final trade decision:
    Technical: {json.dumps(technical)}
    Sentiment: {json.dumps(sentiment)}
    Risk: {json.dumps(risk)}
    
    Respond with JSON: {{decision: CONFIRMED|REJECTED, confidence: 0-100}}"""
    response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=300,
                                     messages=[{"role": "user", "content": prompt}])
    return json.loads(response.content[0].text)

# Use all agents
technical = technical_analyst("AAPL", market_data)
sentiment = sentiment_analyst("AAPL")
risk = risk_manager(entry=150, stop=148, target=156)
decision = trader_decision(technical, sentiment, risk)
print(f"Decision: {decision['decision']} ({decision['confidence']}% confidence)")
```

---

## WEBHOOKS & TRIGGERS

### 1. TradingView Alert Webhooks
**Type:** Outgoing alert webhook from TradingView
**Configuration:** TradingView → Alerts → Create Alert → Webhook URL

#### Setup
```
Alert Name: ORB_LONG_SIGNAL
Condition: close > orb_high AND rsi > 50
Message: {
  "symbol": "SPY",
  "direction": "LONG",
  "setup": "ORB",
  "entry": "{{close}}",
  "atr": "{{ta.atr(14)}}",
  "time": "{{time}}"
}
Webhook URL: https://your-backend.com/webhook/orb-signal
```

#### Receiving Webhook (Python Flask)
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/orb-signal', methods=['POST'])
def handle_orb_signal():
    data = request.json
    symbol = data.get('symbol')
    direction = data.get('direction')
    entry = float(data.get('entry'))
    atr = float(data.get('atr'))
    
    # Run TradingAgents confirmation
    from trading_agents_yfinance import evaluate_setup
    result = evaluate_setup(symbol, direction, "ORB", "5min", entry, atr)
    
    if result['decision'] == 'CONFIRMED':
        # Send Telegram alert
        send_telegram_alert(f"{symbol} {direction} ORB - Confidence: {result['confidence']}%")
    
    return jsonify({"status": "processed", "decision": result['decision']})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### 2. Remote Trigger Webhooks
**Type:** Schedule Python code to run on interval
**Method:** Create trigger via Remote Trigger API

#### Example: Daily ORB Backtest
```python
import requests
import json

API_URL = "https://claude.ai/v1/code/triggers"
HEADERS = {"Content-Type": "application/json"}

# Create trigger
trigger_data = {
    "name": "Daily ORB Backtest",
    "schedule": "0 9 * * MON-FRI",  # 9 AM weekdays
    "code": """
import subprocess
result = subprocess.run(['python', 'C:/Case Capital/Axiom day trading/backtest_orb_real_data.py'], 
                       capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("ERROR:", result.stderr)
"""
}

response = requests.post(API_URL, json=trigger_data, headers=HEADERS)
trigger = response.json()
print(f"Trigger created: {trigger['id']}")
print(f"View at: {trigger['url']}")

# Run manually
run_response = requests.post(f"{API_URL}/{trigger['id']}/run", headers=HEADERS)
print(f"Status: {run_response.json()['status']}")
```

---

### 3. TradingAgents Confirmation Webhook
**Type:** Internal webhook for multi-agent validation

#### Flow
```
TradingView Alert
    ↓
POST /webhook/orb-signal
    ↓
1. Extract signal data (symbol, entry, atr)
2. Call trading_agents_yfinance.evaluate_setup()
3. Check decision (CONFIRMED or REJECTED)
4. If CONFIRMED: Send Telegram alert with confidence
5. If REJECTED: Log but don't alert
    ↓
Telegram Notification (if confirmed)
```

#### Implementation
```python
def process_orb_signal(webhook_data):
    """Process TradingView ORB alert and apply multi-agent confirmation"""
    symbol = webhook_data['symbol']
    direction = webhook_data['direction']
    entry = webhook_data['entry']
    atr = webhook_data['atr']
    
    # Step 1: Run technical confirmation
    technical_pass = check_technical_confirmation(symbol, direction)
    if not technical_pass:
        return {"status": "REJECTED", "reason": "Technical confirmation failed"}
    
    # Step 2: Run TradingAgents evaluation
    from trading_agents_yfinance import evaluate_setup
    agents_result = evaluate_setup(symbol, direction, "ORB", "5min", entry, atr)
    
    # Step 3: Check decision
    if agents_result['decision'] != 'CONFIRMED':
        return {
            "status": "REJECTED",
            "reason": f"TradingAgents: {agents_result['reasoning']}",
            "confidence": agents_result['confidence']
        }
    
    # Step 4: Send Telegram alert
    message = f"""
🟢 ORB SIGNAL CONFIRMED
Symbol: {symbol}
Direction: {direction}
Entry: {entry:.2f}
ATR: {atr:.2f}
TradingAgents Confidence: {agents_result['confidence']}%
Technical Score: {agents_result['technical_score']}/100
Sentiment Score: {agents_result['sentiment_score']}/100
Risk Score: {agents_result['risk_score']}/100
    """
    send_telegram(message)
    
    return {
        "status": "CONFIRMED",
        "message": message,
        "confidence": agents_result['confidence']
    }
```

---

## AUTHENTICATION

### 1. API Keys & Credentials (SECURE)
```
ANTHROPIC_API_KEY
  └─ Used for: Claude LLM multi-agent analysis
  └─ Store in: Environment variable or .env file
  └─ Usage: from anthropic import Anthropic; client = Anthropic()
  └─ Safety: Never commit to git, load from env only

ALPHA_VANTAGE_API_KEY = H62ZC5DSZT4WB86J
  └─ Used for: Market data (premium features limited)
  └─ Store in: fetch_alpha_vantage_data.py or .env
  └─ Safety: Rate limited to 500/day, low security concern
  └─ Limitation: 5-min data requires PREMIUM subscription

TradingView Login
  └─ Used for: TradingView MCP connection
  └─ Required: Desktop app must be running and logged in
  └─ Protocol: MCP connects to local TradingView instance
  └─ No credentials needed (local connection)
```

### 2. OAuth (Remote Triggers)
```
Remote Trigger API
  └─ Authentication: OAuth (automatic)
  └─ How it works: Claude Code automatically adds auth token in-process
  └─ Scope: Full access to your trigger creation/execution
  └─ Security: Token never exposed to user code
  └─ Usage: Just call RemoteTrigger tool, auth is handled
```

### 3. TradingView MCP Authentication
```
Method: Local Socket Connection
  └─ TradingView Desktop must be running
  └─ MCP connects via localhost socket
  └─ No credentials required (local machine only)
  └─ Implicit user authentication (logged-in user in TradingView)
```

---

## DATA FORMATS

### 1. OHLCV Bar Format
```json
{
  "time": 1717785600,
  "datetime": "2026-06-07 09:30:00",
  "datetime_et": "2026-06-07 09:30:00 ET",
  "open": 425.50,
  "high": 425.75,
  "low": 425.25,
  "close": 425.60,
  "volume": 15234,
  "hour_et": 9,
  "minute_et": 30
}
```

### 2. Strategy Metrics Format
```json
{
  "total_trades": 120,
  "win_rate": 39.17,
  "profit_factor": 0.96,
  "max_drawdown": 0.01,
  "net_pnl": -3.38,
  "avg_trade": -0.03,
  "winning_trades": 47,
  "losing_trades": 73
}
```

### 3. TradingAgents Evaluation Result
```json
{
  "decision": "CONFIRMED|REJECTED",
  "confidence": 85,
  "reasoning": "Strong technical setup with bullish sentiment",
  "technical_score": 78,
  "sentiment_score": 72,
  "risk_score": 82,
  "overall_score": 77,
  "timestamp": "2026-06-07T14:30:00",
  "agents": {
    "technical": {
      "trend": "bullish",
      "strength": "strong",
      "technical_score": 78
    },
    "sentiment": {
      "sentiment": "bullish",
      "momentum": "strong",
      "sentiment_score": 72
    },
    "risk": {
      "rr_ratio_valid": true,
      "stop_placement": "ideal",
      "risk_score": 82,
      "approved": true
    },
    "trader": {
      "decision": "CONFIRMED",
      "confidence": 85,
      "reasoning": "..."
    }
  }
}
```

### 4. TradingView Alert Webhook Payload
```json
{
  "symbol": "SPY",
  "direction": "LONG",
  "setup": "ORB",
  "entry": 425.60,
  "atr": 2.15,
  "time": "2026-06-07 09:45:00",
  "orb_high": 425.75,
  "orb_low": 425.25,
  "rsi": 58
}
```

---

## INTEGRATION EXAMPLES

### Example 1: Complete Live Trading Pipeline
```python
#!/usr/bin/env python3
"""
Complete ORB trading pipeline:
1. TradingView detects setup
2. Webhook triggers Python code
3. Multi-agent confirmation
4. Telegram alert sent
"""

from flask import Flask, request, jsonify
import requests
from trading_agents_yfinance import evaluate_setup
from datetime import datetime
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

def send_telegram(message: str):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=data)

@app.route('/webhook/orb-signal', methods=['POST'])
def handle_orb_signal():
    """Receive ORB signal from TradingView and process with multi-agent system"""
    
    data = request.json
    symbol = data.get('symbol')
    direction = data.get('direction')
    entry = float(data.get('entry'))
    atr = float(data.get('atr'))
    
    print(f"[{datetime.now()}] Received ORB signal: {symbol} {direction}")
    
    # Run multi-agent evaluation
    result = evaluate_setup(symbol, direction, "ORB", "5min", entry, atr)
    
    # Build message
    message = f"""
🔔 ORB SIGNAL ALERT

Symbol: {symbol}
Direction: {direction}
Entry: ${entry:.2f}
ATR: {atr:.2f}

🤖 MULTI-AGENT ANALYSIS:
Decision: {result['decision']}
Confidence: {result['confidence']}%

Technical Score: {result['technical_score']}/100
Sentiment Score: {result['sentiment_score']}/100
Risk Score: {result['risk_score']}/100
Overall: {result['overall_score']}/100

Reasoning: {result['reasoning']}
Timestamp: {result['timestamp']}
    """
    
    # Send alert if confirmed
    if result['decision'] == 'CONFIRMED':
        send_telegram(message)
        status = "SENT"
    else:
        status = "REJECTED"
        print(f"Signal rejected: {result['reasoning']}")
    
    return jsonify({
        "status": status,
        "decision": result['decision'],
        "confidence": result['confidence']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Example 2: Scheduled Daily Backtest via Remote Triggers
```python
"""
Schedule backtest to run daily at 9 AM via Remote Trigger API
"""

import requests
import json
from datetime import datetime

API_URL = "https://claude.ai/v1/code/triggers"

trigger_config = {
    "name": "Daily ORB Backtest",
    "schedule": "0 9 * * MON-FRI",  # 9 AM on weekdays
    "code": """
import sys
sys.path.insert(0, '/Case Capital/Axiom day trading')
from backtest_orb_real_data import *
from fetch_yfinance_data import *

# Fetch fresh data
bars = fetch_intraday_data("SPY", "5m", "30d")
filtered = filter_market_hours(bars)
save_bars_to_json(filtered, "yfinance_SPY_5min_marketHours.json")

# Run backtest
data = load_backtest_data("yfinance_SPY_5min_marketHours.json")
bars_bt = convert_to_backtest_format(data)
bt = ORBBacktesterFixed()
bt.run_backtest(bars_bt)
metrics = bt.get_metrics()

# Log results
print(f"BACKTEST COMPLETE: Win Rate={metrics['win_rate']}%, P&L=${metrics['net_pnl']:.2f}")
"""
}

# Create trigger
response = requests.post(
    API_URL,
    json=trigger_config,
    headers={"Content-Type": "application/json"}
)

trigger = response.json()
print(f"✓ Trigger created: {trigger['id']}")
print(f"  URL: {trigger['url']}")
print(f"  Schedule: 0 9 * * MON-FRI (9 AM weekdays)")
```

### Example 3: Multi-Timeframe Analysis
```python
"""
Use TradingView Scanner to analyze symbol across multiple timeframes
"""

from mcp__tradingview_scanner import multi_timeframe_analysis

# Analyze SPY across all timeframes
result = multi_timeframe_analysis(symbol="SPY")

# Returns analysis for: 1m, 5m, 15m, 60m, daily
for timeframe, analysis in result.items():
    print(f"\n{timeframe}:")
    print(f"  Trend: {analysis['trend']}")
    print(f"  Strength: {analysis['strength']}")
    print(f"  Score: {analysis['score']}/100")

# Use for alignment check (all timeframes bullish = stronger signal)
if all(a['trend'] == 'bullish' for a in result.values()):
    print("\n✓ ALL TIMEFRAMES BULLISH - Strong setup")
```

---

## CURRENT SYSTEM STATE

### Files on Disk
```
C:/Case Capital/Axiom day trading/
├── backtest_orb_fixed.py                          [Core backtester - v1 COMPLETE]
├── backtest_orb_real_data.py                      [Runner with real data - TESTED]
├── fetch_yfinance_data.py                         [Data fetcher - WORKING]
├── fetch_alpha_vantage_data.py                    [Alpha Vantage fetcher - INSTALLED]
├── trading_agents_service.py                      [Multi-agent with Alpha Vantage - INSTALLED]
├── trading_agents_yfinance.py                     [Multi-agent with yfinance - TESTED ✓]
├── yfinance_SPY_5min_marketHours.json             [Real data - 4,680 bars, 60 days]
├── confirmer.py                                   [Signal confirmation - NEEDS UPDATE]
├── CODEX_API_MCP_WEBHOOK_REFERENCE.md            [This file]
└── MEMORY.md                                      [Strategy constraints]
```

### Installed Python Packages
```
yfinance              [Free 5-min data - ACTIVE]
alpha_vantage         [Premium data source - INSTALLED]
anthropic             [Claude LLM - ACTIVE]
pytz                  [Timezone handling - ACTIVE]
pandas                [Data manipulation - ACTIVE]
flask                 [Webhook server - OPTIONAL]
requests              [HTTP calls - ACTIVE]
```

### Environment Variables Required
```bash
export ANTHROPIC_API_KEY="sk-ant-..."        # For Claude LLM
export ALPHA_VANTAGE_API_KEY="H62ZC5DSZT4WB86J"  # For market data (already in code)
export TELEGRAM_BOT_TOKEN="..."              # For alerts (optional)
export TELEGRAM_CHAT_ID="..."                # For alerts (optional)
```

### Current Performance Metrics
```
ORB Strategy (Real Data - SPY 5-min):
  Total Trades: 120
  Win Rate: 39.17%          [TARGET: 55%+]
  Profit Factor: 0.96       [TARGET: 1.3+]
  Max Drawdown: 0.01%
  Net P&L: -$3.38           [TARGET: Positive]
  Trades/Day: 2.0           [ACCEPTABLE]
  
Status: FUNCTIONAL but NEEDS OPTIMIZATION
```

### Next Steps
```
Priority 1: Optimize ORB parameters (RSI, ATR, session times)
Priority 2: Enhance TradingAgents with market context
Priority 3: Integrate confirmer.py with multi-agent check
Priority 4: Deploy webhook server for live signals
Priority 5: Set up Remote Triggers for scheduled backtests
```

---

## QUICK REFERENCE COMMANDS

### Run Backtest
```bash
cd "C:/Case Capital/Axiom day trading"
python backtest_orb_real_data.py
```

### Fetch Fresh Data
```bash
python fetch_yfinance_data.py
```

### Test Multi-Agent System
```bash
python trading_agents_yfinance.py
```

### Create Remote Trigger
```python
from RemoteTrigger import RemoteTrigger
trigger = RemoteTrigger(action="create", body={
    "name": "My Backtest",
    "schedule": "0 9 * * *",
    "code": "python backtest_orb_real_data.py"
})
```

### Get TradingView Chart Data
```python
from mcp__tradingview_live import data_get_ohlcv
bars = data_get_ohlcv(summary=False)  # Get all visible bars
```

---

**Last Updated:** 2026-06-07
**For Codex Integration** - Copy this entire file and paste into Codex with: "Use this API/MCP reference to help build the AXIOM trading system"
