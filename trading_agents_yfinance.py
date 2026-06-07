"""
TradingAgents Multi-Agent Evaluation Service (using yfinance for data)
Evaluates trading setups using Technical, Sentiment, Risk, and Trader agents
"""

import json
import yfinance as yf
from datetime import datetime
from typing import Dict, Optional
import anthropic

# Initialize Anthropic Claude
client = anthropic.Anthropic()

class TradingAgentsEvaluator:
    """Multi-agent system for trading setup evaluation"""

    def __init__(self):
        self.client = client

    def get_market_data_yfinance(self, ticker: str, period: str = "30d", interval: str = "1d") -> Optional[Dict]:
        """Fetch market data using yfinance (free, no API key)"""
        try:
            print(f"  Fetching {ticker} data from Yahoo Finance...")
            hist = yf.Ticker(ticker).history(period=period, interval=interval)

            data_list = []
            for date, row in hist.iterrows():
                data_list.append({
                    'time': str(date.date()),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })

            return {
                'data': data_list[-30:],  # Last 30 bars
                'bars_count': len(data_list)
            }
        except Exception as e:
            print(f"  Error: {e}")
            return None

    def technical_analyst_agent(self, ticker: str, direction: str, market_data: Dict) -> Dict:
        """Analyze technical setup using Claude"""

        if not market_data:
            return {"technical_score": 50, "strength": "unknown"}

        data_str = json.dumps(market_data['data'][-10:], indent=2)

        prompt = f"""
You are a professional technical analyst. Analyze this chart for {ticker}.

MARKET DATA (Last 10 bars):
{data_str}

SETUP: {direction} Entry for {ticker}

Provide technical analysis in JSON format:
{{
    "trend": "bullish/bearish/neutral",
    "strength": "strong/moderate/weak",
    "volume_confirmation": true/false,
    "technical_score": 0-100,
    "reasoning": "Brief explanation"
}}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
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

Ticker: {ticker}
Direction: {direction}
Context: Day trading setup evaluation

Respond with JSON only:
{{
    "sentiment": "bullish/bearish/neutral",
    "momentum": "strong/moderate/weak",
    "sentiment_score": 0-100,
    "reasoning": "Brief explanation"
}}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass

        return {"sentiment_score": 50, "sentiment": "neutral"}

    def risk_manager_agent(self, ticker: str, direction: str, entry: float = 100, atr: float = 2) -> Dict:
        """Evaluate risk parameters using Claude"""

        stop_loss = entry - (atr * 1.5) if direction == "LONG" else entry + (atr * 1.5)
        take_profit = entry + (atr * 3.0) if direction == "LONG" else entry - (atr * 3.0)
        rr_ratio = abs(take_profit - entry) / abs(entry - stop_loss) if entry != stop_loss else 0

        prompt = f"""
You are a risk management expert. Evaluate this risk setup.

Trade Parameters:
- Direction: {direction}
- Entry: {entry:.2f}
- Stop Loss: {stop_loss:.2f}
- Take Profit: {take_profit:.2f}
- Risk/Reward Ratio: {rr_ratio:.2f}

Respond with JSON only:
{{
    "rr_ratio_valid": {str(rr_ratio >= 1.3).lower()},
    "stop_placement": "ideal/acceptable/tight",
    "risk_score": 0-100,
    "approved": true/false,
    "reasoning": "Brief explanation"
}}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

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
Technical Analysis Score: {technical.get('technical_score', 50)}/100
Sentiment Score: {sentiment.get('sentiment_score', 50)}/100
Risk Management Approved: {risk.get('approved', False)}

Setup: {direction} Entry for {ticker}

Make a FINAL TRADE DECISION. Respond with JSON only:
{{
    "decision": "CONFIRMED/REJECTED",
    "confidence": 0-100,
    "reasoning": "Brief explanation"
}}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass

        return {"decision": "REJECTED", "confidence": 0, "reasoning": "Error in analysis"}

    def evaluate_setup(self, ticker: str, direction: str, setup_type: str = "ORB",
                      entry: float = None, atr: float = None) -> Dict:
        """Main evaluation function"""

        print(f"\n{'='*80}")
        print(f"TRADING AGENTS EVALUATION: {ticker} {direction}")
        print(f"{'='*80}\n")

        # Fetch market data
        print("[DATA] Fetching market data...")
        market_data = self.get_market_data_yfinance(ticker)

        if not market_data:
            return {
                "decision": "REJECTED",
                "confidence": 0,
                "reasoning": "Unable to fetch market data",
                "timestamp": datetime.now().isoformat()
            }

        # Technical analysis
        print("[TECH] Analyzing chart patterns...")
        technical = self.technical_analyst_agent(ticker, direction, market_data)
        tech_score = technical.get('technical_score', 50)
        print(f"  Technical Score: {tech_score}/100")

        # Sentiment analysis
        print("[SENT] Evaluating market sentiment...")
        sentiment = self.sentiment_analyst_agent(ticker, direction)
        sent_score = sentiment.get('sentiment_score', 50)
        print(f"  Sentiment Score: {sent_score}/100")

        # Risk analysis
        print("[RISK] Validating risk parameters...")
        if entry is None:
            entry = 100  # Default value
        if atr is None:
            atr = 2  # Default value
        risk = self.risk_manager_agent(ticker, direction, entry, atr)
        risk_score = risk.get('risk_score', 50)
        print(f"  Risk Score: {risk_score}/100")

        # Trader decision
        print("[TRADE] Making final decision...")
        trader = self.trader_decision_agent(technical, sentiment, risk, ticker, direction)

        # Compile result
        result = {
            "decision": trader.get("decision", "REJECTED"),
            "confidence": trader.get("confidence", 0),
            "reasoning": trader.get("reasoning", ""),
            "technical_score": tech_score,
            "sentiment_score": sent_score,
            "risk_score": risk_score,
            "overall_score": round((tech_score + sent_score + risk_score) / 3),
            "timestamp": datetime.now().isoformat()
        }

        print(f"\n{'='*80}")
        print(f"DECISION: {result['decision']} (Confidence: {result['confidence']}/100)")
        print(f"Overall Score: {result['overall_score']}/100")
        print(f"{'='*80}\n")

        return result


# Global instance
evaluator = TradingAgentsEvaluator()

def evaluate_setup(ticker: str, direction: str, setup_type: str = "ORB",
                  entry: float = None, atr: float = None) -> Dict:
    """Public API"""
    return evaluator.evaluate_setup(ticker, direction, setup_type, entry, atr)


if __name__ == "__main__":
    print("[AGENTS] Testing TradingAgents Multi-Agent System\n")

    # Test with sample setup
    result = evaluate_setup(
        ticker="AAPL",
        direction="LONG",
        setup_type="ORB"
    )

    print("Result Summary:")
    print(json.dumps({
        "decision": result["decision"],
        "confidence": result["confidence"],
        "overall_score": result["overall_score"],
        "reasoning": result["reasoning"]
    }, indent=2))
