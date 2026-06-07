AXIOM DAY TRADING - EXECUTION PLAN v2
========================================

ASSIGNMENTS
-----------
[2] Build/clean universal backtest engine  → Codex (implementer)
[3] Backtest all completed strategies      → Codex (implementer, after #2)
Reviewer for both                          → Claude Code

SCOPE BOUNDARY
--------------
NO CODE MODIFICATION in this plan.
This document is project management only.

==============================
SEQUENCING
==============================

Step 1: Issue #2 (Codex implements)
  - Create branch: issue/2-backtest-engine
  - Build canonical backtest engine
  - Use existing strategy files
  - Do NOT redesign strategies
  - Use yfinance
  - Output: backtest_results.json
  - No lookahead bias
  - Preserve Eastern Time handling
  - Target: PR #2 → Codex self-review → flags for Claude Code review

Step 2: Issue #2 review (Claude Code)
  - Reviewer prompt provided below
  - Focus: correctness, no lookahead, ET handling, yfinance usage
  - Output: APPROVED / CHANGES REQUESTED
  - If CHANGES REQUESTED → Codex fixes → Claude Code re-reviews

Step 3: Issue #3 (Codex implements, branch from merged #2)
  - Create branch: issue/3-backtest-run-all
  - Base: issue/2-backtest-engine (after PR #2 merged)
  - Run every strategy through canonical engine
  - Generate metrics:
      * win rate
      * profit factor
      * expectancy
      * average R
      * max drawdown
      * trade count
  - Update strategy_manifest.json
  - Target: PR #3 → Codex self-review → flags for Claude Code review

Step 4: Issue #3 review (Claude Code)
  - Reviewer prompt provided below
  - Focus: metric correctness, manifest format, coverage of all strategies
  - Output: APPROVED / CHANGES REQUESTED

Step 5: Merge sequence
  - PR #2 merges to main
  - PR #3 merges to main (rebased on #2)

==============================
AGENT PROMPTS
==============================

------------------------------
CODEX - Issue #2 IMPLEMENTATION
------------------------------

You are implementing GitHub Issue #2 for repository tcase0618/AXIOM-Day-Trading.

TASK:
Build/clean universal backtest engine.

REQUIREMENTS:
1. Create one canonical backtest engine.
2. Use existing strategy files as they currently exist.
3. Do NOT redesign strategies.
4. Use yfinance for data.
5. Output backtest_results.json.
6. Ensure no lookahead bias.
7. Preserve Eastern Time handling.

DELIVERABLES:
- backtest engine module/file
- backtest_results.json (sample output from a test run)
- README or docstring explaining usage
- No other files modified

CONSTRAINTS:
- Do not touch scanner.py, webhook_handler.py, or other live systems.
- Do not modify any strategy logic, only adapt them INTO the engine if needed.
- Preserve existing file structure.
- If a strategy is incompatible, document it in a BLOCKERS.md file instead of forcing it.

SUCCESS CRITERIA:
- Engine runs without errors against all discoverable strategy files.
- backtest_results.json is produced.
- No lookahead bias present in bar iteration.
- Eastern Time timestamps preserved throughout.

Create branch: issue/2-backtest-engine
Open PR with title: "[2] Build/clean universal backtest engine"

------------------------------
CLAUDE CODE - Issue #2 REVIEW
------------------------------

You are reviewing PR #2 for repository tcase0618/AXIOM-Day-Trading.

SCOPE:
Issue #2: Build/clean universal backtest engine.

WHAT TO CHECK:
1. Correctness: Does the engine iterate bars in strict chronological order?
2. No lookahead bias: At bar T, are ONLY bars <= T used for signals/risk?
3. yfinance usage: Is data fetched correctly with timezone awareness?
4. Eastern Time: Are all timestamps Eastern? Are daylight transitions handled?
5. Output format: Does backtest_results.json match expected schema?
6. Strategy preservation: Were any strategy files modified? If yes, flag as violation.
7. Error handling: Missing data, corporate actions, splits?
8. Reproducibility: Can results be rerun deterministically?

OUTPUT FORMAT:
### APPROVED
or
### CHANGES REQUESTED
- [ ] Checklist item
- Comment / evidence

If CHANGES REQUESTED, provide line-level feedback.

Do NOT modify code. Review only.

------------------------------
CODEX - Issue #3 IMPLEMENTATION
------------------------------

You are implementing GitHub Issue #3 for repository tcase0618/AXIOM-Day-Trading.

TASK:
Backtest all completed strategies.

REQUIREMENTS:
1. Run every strategy through the canonical backtest engine (from PR #2).
2. Do NOT build a new engine. Use the existing one.
3. Generate for each strategy:
   - win rate
   - profit factor
   - expectancy
   - average R
   - max drawdown
   - trade count
4. Update strategy_manifest.json.

DELIVERABLES:
- Updated strategy_manifest.json
- Optional: run script or CI snippet showing how metrics were generated

CONSTRAINTS:
- Do not modify the backtest engine from Issue #2.
- Do not modify scanner.py or live systems.
- Use existing strategy files from Issue #1 inventory.
- If a strategy cannot be backtested, mark it in manifest with status: blocked and reason.

SUCCESS CRITERIA:
- All completed strategies have metrics.
- strategy_manifest.json exists and is well-formed.
- No engine code was changed.

Create branch: issue/3-backtest-run-all
Open PR with title: "[3] Backtest all completed strategies"

------------------------------
CLAUDE CODE - Issue #3 REVIEW
------------------------------

You are reviewing PR #3 for repository tcase0618/AXIOM-Day-Trading.

SCOPE:
Issue #3: Backtest all completed strategies.

WHAT TO CHECK:
1. Completeness: Does every completed strategy from strategy_inventory.json have metrics?
2. Metric correctness: Are win rate, profit factor, expectancy, average R, max drawdown, trade count calculated correctly?
   - Win rate = wins / (wins + losses)
   - Profit factor = gross profit / gross loss
   - Expectancy = (win rate * avg win) - (loss rate * avg loss)
   - Average R = avg win / avg loss (or defined consistently)
   - Max drawdown = peak-to-trough of equity curve
3. Manifest format: Is strategy_manifest.json parseable and consistent?
4. Engine integrity: Was the backtest engine from Issue #2 modified? If yes, flag as violation.
5. Blocked strategies: Are any blocked strategies documented with reasons?

OUTPUT FORMAT:
### APPROVED
or
### CHANGES REQUESTED
- [ ] Checklist item
- Comment / evidence

If CHANGES REQUESTED, provide line-level feedback.

Do NOT modify code. Review only.

==============================
MERGE ORDER
==============================

1. PR #2 → merge to main
   - Block on: Claude Code approves Issue #2
   - Branch cleanup: delete issue/2-backtest-engine

2. PR #3 → merge to main
   - Block on: Claude Code approves Issue #3
   - Must rebase on main after #2 merged
   - Branch cleanup: delete issue/3-backtest-run-all

==============================
CRITICAL BLOCKERS
==============================

- Issue #1 must exist before #2 starts (inventory provides the strategy file list).
- Issue #2 approval is a hard gate for Issue #3.
- Any engine bug found by Claude Code blocks #3 until fixed in #2.
- If Issue #3 finds strategies incompatible with the engine, that becomes a new blocker issue.

==============================
CHECKPOINTS
==============================

Checkpoint A: Issue #2 branch pushed
Checkpoint B: Issue #2 PR opened
Checkpoint C: Claude Code review of #2 complete
Checkpoint D: Issue #2 merged
Checkpoint E: Issue #3 branch pushed (from merged #2)
Checkpoint F: Issue #3 PR opened
Checkpoint G: Claude Code review of #3 complete
Checkpoint H: Issue #3 merged

NOTES:
- Codex is responsible for opening PRs and self-reviewing before flagging Claude Code.
- Claude Code is responsible for review only, not implementation.
- No code changes in this plan.
