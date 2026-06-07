"""
AXIOM Day Trading - Universal strategy backtest runner
- Loads all v*.py strategies from ./strategies
- Uses yfinance when available, otherwise synthetic demo data
- Generates backtest_results.json
- Updates strategy_manifest.json
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta

try:
    import yfinance as yf  # type: ignore

    HAS_YFINANCE = True
except Exception:  # pragma: no cover
    HAS_YFINANCE = False

import pandas as pd
import numpy as np

STRATEGY_DIR = Path("strategies")
OUT_MANIFEST = Path("strategy_manifest.json")
OUT_RESULTS = Path("backtest_results.json")
DEFAULT_TICKER = "SPY"
DEFAULT_LOOKBACK_DAYS = 90


def _to_naive_et(df: pd.DataFrame) -> pd.DataFrame:
    if df.index.tzinfo is not None:
        try:
            df = df.tz_convert("America/New_York")
        except Exception:
            df = df.tz_convert("UTC").tz_convert("America/New_York")
        df.index = df.index.tz_localize(None)
    return df


def _default_index(days: int = DEFAULT_LOOKBACK_DAYS) -> pd.DatetimeIndex:
    end = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)
    index = pd.date_range(start=start, end=end, freq="5min", tz="America/New_York")
    index = index[(index.time >= pd.Timestamp("09:30:00").time()) & (index.time <= pd.Timestamp("16:00:00").time())]
    return index


def _synthetic(ticker: str, days: int = DEFAULT_LOOKBACK_DAYS) -> pd.DataFrame:
    idx = _default_index(days)
    rng = np.random.default_rng(0)
    prices = 100 + np.cumsum(rng.normal(0, 0.5, size=len(idx)))
    vols = np.abs(rng.normal(1e6, 2e5, size=len(idx)))
    high = prices + rng.uniform(0.0, 0.5, size=len(idx))
    low = prices - rng.uniform(0.0, 0.5, size=len(idx))
    df = pd.DataFrame({"open": prices, "high": high, "low": low, "close": prices, "volume": vols}, index=idx)
    df.index.name = "datetime"
    return df


def fetch_data(ticker: str, days: int = DEFAULT_LOOKBACK_DAYS) -> pd.DataFrame:
    if HAS_YFINANCE:
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period=f"{days}d", interval="5m")
            if hist is None or hist.empty:
                raise ValueError(f"No data from yfinance for {ticker}")
            hist.index.name = "datetime"
            hist = hist.rename(columns={c: c.lower() for c in hist.columns})
            needed = {"open", "high", "low", "close", "volume"}
            missing = needed - set(hist.columns)
            if missing:
                raise ValueError(f"Missing columns from yfinance: {missing}")
            return _to_naive_et(hist[["open", "high", "low", "close", "volume"]])
        except Exception:
            pass
    return _synthetic(ticker, days)


def load_strategy_modules() -> List[Tuple[str, Any]]:
    modules: List[Tuple[str, Any]] = []
    for path in sorted(STRATEGY_DIR.glob("v*.py")):
        module_name = path.stem
        if module_name == "backtest_engine":
            continue
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if not hasattr(module, "detect_signals"):
                raise RuntimeError("Missing detect_signals()")
            modules.append((module_name, module))
        except Exception as exc:
            modules.append((module_name, None))
    return modules


def run_strategy(name: str, module: Any, df: pd.DataFrame) -> Dict[str, Any]:
    signals = []
    try:
        signals = module.detect_signals(df)
    except Exception as exc:
        return {"name": name, "status": "blocked", "error": str(exc), "trades": 0}

    trades: List[Dict[str, Any]] = []
    for sig in signals:
        price = float(sig.get("price", 0.0) or 0.0)
        side = str(sig.get("side", "long"))
        if price <= 0.0:
            continue
        if not trades:
            trades.append({"time": str(sig.get("time")), "side": side, "entry": price, "exit": None})
            continue
        last = trades[-1]
        if last.get("exit") is None:
            last["exit"] = price
            trades.append({"time": str(sig.get("time")), "side": side, "entry": price, "exit": None})

    # Close any open trades at last known close
    if trades and trades[-1].get("exit") is None and len(df) > 0:
        trades[-1]["exit"] = float(df["close"].iloc[-1])

    closed = [t for t in trades if t.get("exit") is not None]
    pnls = [t["exit"] - t["entry"] if t["side"] == "long" else t["entry"] - t["exit"] for t in closed]

    win = sum(1 for p in pnls if p > 0)
    loss = sum(1 for p in pnls if p < 0)
    gross_profit = sum(p for p in pnls if p > 0)
    gross_loss = abs(sum(p for p in pnls if p < 0))
    trade_count = len(closed)

    win_rate = (win / trade_count) if trade_count > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float("inf") if gross_profit > 0 else 0.0)
    avg_win = (gross_profit / win) if win > 0 else 0.0
    avg_loss = (gross_loss / loss) if loss > 0 else 0.0
    expectancy = ((win / trade_count) * avg_win) if trade_count > 0 else 0.0
    avg_r = (avg_win / avg_loss) if avg_loss > 0 else 0.0

    equity = [0.0]
    for p in pnls:
        equity.append(equity[-1] + p)
    peak = max(equity)
    max_dd = max(peak - v for v in equity) if equity else 0.0

    return {
        "name": name,
        "status": "completed",
        "trades": trade_count,
        "win_rate": round(win_rate, 6),
        "profit_factor": round(profit_factor, 6) if math.isfinite(profit_factor) else None,
        "expectancy": round(expectancy, 6),
        "avg_r": round(avg_r, 6),
        "max_drawdown": round(float(max_dd), 6),
        "sample_signals": len(signals),
    }


def build_manifest(modules: List[Tuple[str, Any]], results: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = []
    by_name = {r["name"]: r for r in results}
    for name, _module in modules:
        result = by_name.get(name)
        if result is None:
            items.append({"id": name, "status": "error", "error": "No backtest result"})
        else:
            items.append(result)
    return {
        "project": "AXIOM",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(items),
        "strategies_in_order": [name for name, _ in modules],
        "items": items,
    }


def main() -> None:
    print("Fetching market data...")
    df = fetch_data(DEFAULT_TICKER)
    print(f"Data rows: {len(df)}")

    modules = load_strategy_modules()
    print(f"Found strategies: {len(modules)}")

    results: List[Dict[str, Any]] = []
    backtest_results: Dict[str, Any] = {}

    for name, module in modules:
        if module is None:
            results.append({"name": name, "status": "blocked", "error": "Module load failed"})
            continue
        result = run_strategy(name, module, df)
        results.append(result)
        backtest_results[name] = {k: v for k, v in result.items() if k != "name"}

    manifest = build_manifest(modules, results)

    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2))
    OUT_RESULTS.write_text(json.dumps(backtest_results, indent=2))

    print("Wrote", OUT_MANIFEST)
    print("Wrote", OUT_RESULTS)
    for item in results:
        print(item["name"], "->", item["status"], "trades=", item.get("trades", 0))


if __name__ == "__main__":
    main()
