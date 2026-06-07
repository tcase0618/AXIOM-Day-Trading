import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SCAN_LOG = Path("scan_log.json")
TRADE_LOG = Path("trades_log.json")
STRATEGY_MANIFEST = Path("strategy_manifest.json")


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load %s: %s", path, exc)
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _append_log(path: Path, entry: dict) -> None:
    entries = _load_json(path, [])
    entries.append(entry)
    _write_json(path, entries)


def _load_strategy_manifest():
    return _load_json(STRATEGY_MANIFEST, {"strategies": {}})


def _choose_top_strategy(manifest: dict) -> dict | None:
    items = manifest.get("strategies_in_order") or [
        item.get("name") for item in manifest.get("items", [])
    ]
    item_map = {item["name"]: item for item in manifest.get("items", [])}
    ranked = []
    for key in items:
        strategy = item_map.get(key, {})
        ranked.append(
            (
                key,
                strategy,
                strategy.get("win_rate", 0),
                strategy.get("profit_factor", 0),
                strategy.get("avg_r", 0),
            )
        )
    if not ranked:
        return None
    key, strategy, *_ = sorted(ranked, key=lambda t: (t[2], t[3], t[4]), reverse=True)[0]
    return {"key": key, "strategy": strategy}


def _build_scan_result(top) -> dict:
    strategy = top.get("strategy", {}) if top else {}
    payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "no_candidate",
        "strategy_key": top.get("key") if top else None,
        "strategy_name": strategy.get("name"),
        "win_rate": strategy.get("win_rate"),
        "profit_factor": strategy.get("profit_factor"),
        "avg_r": strategy.get("avg_r"),
        "max_drawdown": strategy.get("max_drawdown"),
        "trades": strategy.get("trades"),
    }
    if top:
        payload["status"] = "candidate"
    return payload


def run_scan() -> dict:
    logger.info("Starting scan cycle")
    manifest = _load_strategy_manifest()
    top = _choose_top_strategy(manifest)
    scan = _build_scan_result(top)

    _append_log(SCAN_LOG, scan)
    logger.info("Scan complete: %s", scan)
    return scan


if __name__ == "__main__":
    result = run_scan()
    print(json.dumps(result, indent=2))
