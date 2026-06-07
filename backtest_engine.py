import importlib.util
import json
from pathlib import Path
from typing import List, Dict

STRATEGY_DIR = Path("strategies")


def load_strategy_modules() -> List[Dict]:
    results = []

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

            results.append(
                {
                    "id": module_name,
                    "path": str(path),
                    "module": module_name,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "id": module_name,
                    "path": str(path),
                    "module": module_name,
                    "error": str(exc),
                }
            )

    return results


def build_inventory() -> Dict:
    metrics_path = Path("backtest_results.json")
    existing_metrics = {}
    if metrics_path.exists():
        try:
            existing_metrics = json.loads(metrics_path.read_text())
        except Exception:
            existing_metrics = {}

    items = []
    for entry in load_strategy_modules():
        item = {
            "id": entry["id"],
            "module": entry["module"],
            "path": entry["path"],
            "backtest_status": "blocked" if "error" in entry else "ready",
        }

        metrics_key = entry["id"]
        if metrics_key in existing_metrics:
            item["metrics"] = existing_metrics[metrics_key]

        if "error" in entry:
            item["load_error"] = entry["error"]

        items.append(item)

    inventory = {
        "general": {
            "strategy_dir": str(STRATEGY_DIR),
        },
        "count": len(items),
        "items": items,
    }

    return inventory


def main():
    inventory = build_inventory()
    print(json.dumps(inventory, indent=2))


if __name__ == "__main__":
    main()
