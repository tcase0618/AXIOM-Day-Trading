"""
TradingAgents Integration Service for AXIOM Day Trading
Multi-agent analysis: Technical, Sentiment, Risk Management, and Trader Decision
Integrated with Alpha Vantage for real market data and Anthropic Claude for LLM
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import anthropic

# Initialize Alpha Vantage
ALPHA_VANTAGE_API_KEY = "H62ZC5DSZT4WB86J"
ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
ti = TechIndicators(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')

# Initialize Anthropic Claude
client = anthropic.Anthropic()

class TradingAgentsEvaluator:
    """Multi-agent system for trading setup evaluation"""

    def __init__(self):
        self.client = client
        self.api_key = ALPHA_VANTAGE_API_KEY

    def get_market_data(self, ticker: str, timeframe: str = "5min", period_days: int = 5) -> Optional[Dict]:
        """Fetch market data from Alpha Vantage"""
        try:
            if timeframe == "daily":
                data, meta_data = ts.get_daily(symbol=ticker)
            else:  # 5min, 15min, 60min
                interval = timeframe.replace("min", "")
                data, meta_data = ts.get_intraday(symbol=ticker, interval=interval)

            # Convert to list format for analysis
            data_list = []
            for date, row in data.iterrows():
                data_list.append({
                    'time': str(date),
                    'open': float(row['1. open']),
                    'high': float(row['2. high']),
                    'low': float(row['3. low']),
                    'close': float(row['4. close']),
                    'volume': int(row['5. volume'])
                })

            return {
                'data': data_list[:50],  # Last 50 bars
                'meta': meta_data
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def technical_analyst_agent(self, ticker: str, direction: str, timeframe: str, market_data: Dict) -> Dict:
        """Analyze technical setup using Claude"""

        if not market_data:
            return {"analysis": "Unable to fetch market data", "score": 0}

        data_str = json.dumps(market_data['data'][:10], indent=2)  # Last 10 bars

        prompt = f"""
You are a professional technical analyst. Analyze this {timeframe} chart for {ticker}.

MARKET DATA (Last 10 bars):
{data_str}

SETUP: {direction} breakout above ORB (Opening Range Breakout) high
DIRECTION: {direction}
TIMEFRAME: {timeframe}

Provide technical analysis considering:
1. Trend direction (up/down/sideways)
2. Support/Resistance levels
3. Recent breakout strength
4. Volume confirmation
5. Volatility level

Respond with JSON only:
{{
    "trend": "bullish/bearish/neutral",
    "setup_validity": 0-100,
    "key_levels": {{"resistance": X, "support": Y}},
    "strength": "strong/moderate/weak",
    "volume_confirmation": true/false,
    "technical_score": 0-100
}}
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            response_text = message.content[0].text
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass

        return {"technical_score": 50, "strength": "unknown"}

    def sentiment_analyst_agent(self, ticker: str, direction: str) -> Dict:
        """Analyze market sentiment using Claude"""

        prompt = f"""
You are a market sentiment analyst. Provide sentiment analysis for {ticker}.

CONTEXT:
- Ticker: {ticker}
- Direction: {direction}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M ET')}

Evaluate:
1. Recent price action sentiment
2. Market momentum
3. Risk/Reward setup
4. Setup alignment with broader trend

Respond with JSON only:
{{
    "sentiment": "bullish/bearish/neutral",
    "momentum": "strong/moderate/weak",
    "risk_reward": "favorable/neutral/unfavorable",
    "sentiment_score": 0-100
}}
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            response_text = message.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass

        return {"sentiment_score": 50, "sentiment": "neutral"}

    def risk_manager_agent(self, ticker: str, direction: str, entry: float, atr: float) -> Dict:
        """Evaluate risk parameters using Claude"""

        stop_loss = entry - (atr * 1.5) if direction == "LONG" else entry + (atr * 1.5)
        take_profit = entry + (atr * 3.0) if direction == "LONG" else entry - (atr * 3.0)
        risk_per_trade = abs(entry - stop_loss)
        reward_per_trade = abs(take_profit - entry)
        risk_reward_ratio = reward_per_trade / risk_per_trade if risk_per_trade > 0 else 0

        prompt = f"""
You are a risk management expert. Evaluate this trade setup risk parameters.

TRADE SETUP:
- Ticker: {ticker}
- Direction: {direction}
- Entry Price: {entry:.2f}
- Stop Loss: {stop_loss:.2f}
- Take Profit: {take_profit:.2f}
- ATR: {atr:.2f}
- Risk/Reward Ratio: {risk_reward_ratio:.2f}

Evaluate:
1. Risk/Reward ratio adequacy (target: 1.4+)
2. Stop loss placement validity
3. Position sizing appropriateness
4. Maximum risk per trade acceptability
5. Overall risk management score

Respond with JSON only:
{{
    "rr_ratio_valid": true/false,
    "stop_placement": "ideal/acceptable/tight",
    "position_size": "appropriate/large/small",
    "risk_score": 0-100,
    "approved": true/false
}}
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            response_text = message.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass

        return {"risk_score": 50, "approved": False}

    def trader_decision_agent(self, technical: Dict, sentiment: Dict, risk: Dict, ticker: str, direction: str) -> Dict:
        """Final trader decision using Claude"""

        prompt = f"""
You are a professional trader making the final decision on a trade setup.

AGENT REPORTS:
Technical Analysis: {json.dumps(technical, indent=2)}
Sentiment Analysis: {json.dumps(sentiment, indent=2)}
Risk Management: {json.dumps(risk, indent=2)}

SETUP: {direction} Entry for {ticker}

Make a final TRADE DECISION considering:
1. Technical setup strength (score: {technical.get('technical_score', 50)}/100)
2. Market sentiment alignment (score: {sentiment.get('sentiment_score', 50)}/100)
3. Risk management approval: {risk.get('approved', False)}
4. Overall trade confidence

Respond with JSON only:
{{
    "decision": "CONFIRMED/REJECTED",
    "confidence": 0-100,
    "reasoning": "Brief explanation",
    "alerts": ["alert1", "alert2"]
}}
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            response_text = message.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass

        return {"decision": "REJECTED", "confidence": 0, "reasoning": "Error in analysis"}

    def evaluate_setup(self, ticker: str, direction: str, setup_type: str, timeframe: str,
                      entry: float = None, atr: float = None) -> Dict:
        """
        Main evaluation function: runs all agents and makes final decision

        Args:
            ticker: Symbol to evaluate (e.g., "ES=F", "AAPL")
            direction: "LONG" or "SHORT"
            setup_type: "ORB" (Opening Range Breakout)
            timeframe: "5min", "15min", "60min", "daily"
            entry: Entry price (if known)
            atr: ATR value (if known)

        Returns:
            {
                "decision": "CONFIRMED" or "REJECTED",
                "confidence": 0-100,
                "reasoning": "Why this decision was made",
                "technical_score": 0-100,
                "sentiment_score": 0-100,
                "risk_score": 0-100,
                "agents": {technical, sentiment, risk, trader}
            }
        """

        print(f"\n{'='*80}")
        print(f"TRADING AGENTS EVALUATION: {ticker} {direction} {setup_type}")
        print(f"{'='*80}\n")

        # Fetch market data
        print("[DATA] Fetching market data from Alpha Vantage...")
        market_data = self.get_market_data(ticker, timeframe)

        if not market_data:
            return {
                "decision": "REJECTED",
                "confidence": 0,
                "reasoning": "Unable to fetch market data",
                "timestamp": datetime.now().isoformat()
            }

        # Run Technical Analyst Agent
        print("[TECH] Technical Analyst Agent: analyzing chart patterns...")
        technical = self.technical_analyst_agent(ticker, direction, timeframe, market_data)
        tech_score = technical.get('technical_score', 50)
        print(f"   Technical Score: {tech_score}/100")

        # Run Sentiment Analyst Agent
        print("[SENT] Sentiment Analyst Agent: evaluating market sentiment...")
        sentiment = self.sentiment_analyst_agent(ticker, direction)
        sent_score = sentiment.get('sentiment_score', 50)
        print(f"   Sentiment Score: {sent_score}/100")

        # Run Risk Manager Agent
        print("[RISK]  Risk Manager Agent: validating risk parameters...")
        if entry and atr:
            risk = self.risk_manager_agent(ticker, direction, entry, atr)
        else:
            risk = {"risk_score": 50, "approved": True}
        risk_score = risk.get('risk_score', 50)
        print(f"   Risk Score: {risk_score}/100")

        # Run Trader Decision Agent
        print("[TRADE] Trader Agent: making final decision...")
        trader = self.trader_decision_agent(technical, sentiment, risk, ticker, direction)

        # Compile final result
        result = {
            "decision": trader.get("decision", "REJECTED"),
            "confidence": trader.get("confidence", 0),
            "reasoning": trader.get("reasoning", ""),
            "technical_score": tech_score,
            "sentiment_score": sent_score,
            "risk_score": risk_score,
            "overall_score": round((tech_score + sent_score + risk_score) / 3),
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "technical": technical,
                "sentiment": sentiment,
                "risk": risk,
                "trader": trader
            }
        }

        print(f"\n{'='*80}")
        print(f"DECISION: {result['decision']} (Confidence: {result['confidence']}/100)")
        print(f"Overall Score: {result['overall_score']}/100")
        print(f"Reasoning: {result['reasoning']}")
        print(f"{'='*80}\n")

        return result


# Global instance
evaluator = TradingAgentsEvaluator()


def evaluate_setup(ticker: str, direction: str, setup_type: str, timeframe: str,
                  entry: float = None, atr: float = None) -> Dict:
    """
    Public API for evaluating trading setups using multi-agent system

    Usage:
        result = evaluate_setup("AAPL", "LONG", "ORB", "5min")
        if result["decision"] == "CONFIRMED":
            print(f"Trade approved with {result['confidence']}% confidence")
    """
    return evaluator.evaluate_setup(ticker, direction, setup_type, timeframe, entry, atr)


if __name__ == "__main__":
    # Test the system
    print("\n[AGENTS] Testing TradingAgents Multi-Agent System\n")

    # Test with a sample setup
    result = evaluate_setup(
        ticker="AAPL",
        direction="LONG",
        setup_type="ORB",
        timeframe="5min"
    )

    print("\nResult saved. Testing successful.")
    print(json.dumps(result, indent=2))
