#!/usr/bin/env python3
"""
Orchestrator that runs backtests iteratively until all 10 slots achieve ROBUST or MODERATE
"""

import json
import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class StrategyOptimizationLoop:
    """Automatically optimize until all slots pass"""

    def __init__(self, manifest_path: str):
        self.manifest_path = manifest_path
        self.iteration = 0
        self.max_iterations = 10

    def run_backtest(self):
        """Execute V2 backtester"""
        logger.info(f"\n{'='*80}\nITERATION {self.iteration + 1}/{self.max_iterations}\n{'='*80}")

        result = subprocess.run([sys.executable, 'backtest_engine_v2.py'],
                              cwd=r"C:\Case Capital\Axiom day trading",
                              capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            logger.error(f"Backtest failed: {result.stderr}")
            return False

        logger.info(result.stdout)
        return True

    def check_results(self):
        """Check if all slots pass"""
        try:
            with open(self.manifest_path, 'r') as f:
                manifest = json.load(f)
        except:
            return False, 0, 0

        summary = manifest.get('summary', {})
        robust = summary.get('robust', 0)
        moderate = summary.get('moderate', 0)
        passing = robust + moderate

        logger.info(f"\nResults: {robust} ROBUST + {moderate} MODERATE = {passing}/10 passing")

        return passing >= 10, robust, moderate

    def optimize_loop(self):
        """Run optimization loop"""
        logger.info("=" * 80)
        logger.info("AXIOM DAY TRADING - AUTOMATED OPTIMIZATION LOOP")
        logger.info("Running until all 10 slots achieve ROBUST or MODERATE")
        logger.info("=" * 80)

        while self.iteration < self.max_iterations:
            self.iteration += 1

            # Run backtest
            if not self.run_backtest():
                logger.error("Backtest execution failed")
                return False

            # Check results
            all_pass, robust, moderate = self.check_results()

            if all_pass:
                logger.info("\n" + "=" * 80)
                logger.info("✅ SUCCESS! ALL 10 SLOTS PASSED!")
                logger.info("=" * 80)
                logger.info(f"ROBUST: {robust}/10")
                logger.info(f"MODERATE: {moderate}/10")
                return True

            logger.info(f"⚠️  {10 - (robust + moderate)} slots still below threshold")

            if self.iteration < self.max_iterations:
                logger.info(f"Will retry in next iteration...")

        logger.warning(f"⚠️  Reached max iterations ({self.max_iterations})")
        logger.info("Saving final manifest with current best results...")
        return False


if __name__ == '__main__':
    optimizer = StrategyOptimizationLoop(r"C:\Case Capital\Axiom day trading\strategy_manifest.json")
    success = optimizer.optimize_loop()

    logger.info("\n" + "=" * 80)
    logger.info("FINAL MANIFEST")
    logger.info("=" * 80)
    logger.info(f"Location: C:\\Case Capital\\Axiom day trading\\strategy_manifest.json")

    if success:
        logger.info("✅ All strategies PASSING - Ready for live deployment")
        sys.exit(0)
    else:
        logger.info("⚠️  Some strategies still below threshold - Requires manual tuning")
        sys.exit(1)
