# AXIOM Day Trading — Backtest Engine Decision

## Canonical engine

**File:** `backtest_engine_v7_final.py`

This is the single canonical backtest engine path for the repo.
All other `backtest_engine_v*.py` files (v2–v7) are retained as
legacy/evolution history. Do not delete them.

When running a full backtest pass, use:

```bash
python backtest_engine_v7_final.py
```

or the convenience wrapper:

```bash
python run_backtest_v7.py
```

## Why `v7_final`?

* It is the latest and most complete evolution of the engine.
* It covers all 10 strategy slots with explicit slot-to-strategy mapping.
* It ships with a final results block that prints ROBUST/MODERATE/FAIL counts.
* It writes outputs to portable, repo-local paths (`strategy_manifest.json`).
* It is the only engine patched to load yfinance defensively and use
  `pathlib.Path` for output paths, making it safe under Python 3.14.

## Legacy files

* `backtest_engine_v2.py` .. `v7_final.py`
* `run_backtest.py`, `run_fixed_backtest.py`, `run_until_passing.py`,
  `full_backtest.py`, `run_backtest_all.py`

These are kept for traceability but are no longer the canonical path.
Historically they targeted hard-coded `C:\Case Capital\...` manifest
paths; `v7_final` is the first that writes to the repo-local output.

## Outputs

* `strategy_manifest.json` — slot-by-slot verdict summary + metrics
* Console results showing per-symbol metrics and overall pass count

## Python/runtime notes

Verified with `C:\Users\tcase\AppData\Local\Python\bin\python.exe`
using `pandas` and `yfinance`. If `yfinance` is missing the engine
handles it gracefully and fails signals rather than crashing.
