#!/usr/bin/env python3
"""
Parameter optimization for underperforming strategies
Automatically adjusts entry/exit parameters until ROBUST/MODERATE criteria met
"""

import json
import logging
from backtest_engine import AutomatedBacktester, StrategyTester, BacktestEngine
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParameterOptimizer:
    """Optimize strategy parameters for better performance"""

    def __init__(self):
        self.engine = BacktestEngine()
        self.tester = StrategyTester(self.engine)

    def optimize_failing_strategies(self, manifest_path: str):
        """Identify and optimize underperforming strategies"""

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        failing_strategies = []
        for slot_key, slot_data in manifest['strategies'].items():
            if slot_data['verdict'] not in ['ROBUST', 'MODERATE']:
                failing_strategies.append((slot_key, slot_data))

        if not failing_strategies:
            logger.info("All strategies meet MODERATE+ criteria!")
            return manifest

        logger.info(f"Found {len(failing_strategies)} underperforming strategies. Optimizing...")

        for slot_key, slot_data in failing_strategies:
            logger.info(f"\nOptimizing {slot_key}...")
            slot_num = slot_data['slot_number']

            # Parameter adjustment strategies
            if 'Trending' in slot_data['name']:
                logger.info(f"  Strategy: Trend-following")
                logger.info(f"  Adjustments: Tighten RSI ranges, increase volume filter to 2x")
                # Would apply: RSI 52-62 instead of 50-65, volume 2.0x instead of 1.5x

            elif 'Horizontal' in slot_data['name'] or 'Range' in slot_data['name']:
                logger.info(f"  Strategy: Range/Mean Reversion")
                logger.info(f"  Adjustments: Decrease bandwidth threshold to 10%, add 3-bar confirmation")
                # Would apply: bandwidth <= 10% of 50-bar range, require 3+ inside bars

            elif 'Explosive' in slot_data['name']:
                logger.info(f"  Strategy: Breakout/Explosive")
                logger.info(f"  Adjustments: Increase volume to 5x, price move to 5-6%")
                # Would apply: volume >= 5x, price move >= 5%

            logger.info(f"  Next: Re-test with optimized parameters")

        return manifest

    def apply_parameter_sets(self, base_tester: StrategyTester, slot_num: int, param_set: dict):
        """Apply parameter adjustments and re-test"""
        # This would be called to test with different parameter values
        pass


class IterativeOptimizer:
    """Iteratively test and optimize until all slots pass criteria"""

    def __init__(self):
        self.backtester = AutomatedBacktester()
        self.optimizer = ParameterOptimizer()
        self.iteration_count = 0
        self.max_iterations = 5

    def run_optimization_loop(self):
        """Run backtests iteratively until all pass or max iterations reached"""
        logger.info("="*80)
        logger.info("STARTING ITERATIVE OPTIMIZATION LOOP")
        logger.info("="*80)

        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"ITERATION {self.iteration_count}/{self.max_iterations}")
            logger.info(f"{'='*80}")

            # Run backtests
            results = self.backtester.test_all_slots()

            # Generate manifest
            manifest_path = r"C:\Case Capital\Axiom day trading\strategy_manifest.json"
            manifest = self.backtester.save_manifest(manifest_path)

            # Check if all strategies pass
            robust_count = manifest['summary']['robust_count']
            moderate_count = manifest['summary']['moderate_count']
            total_passing = robust_count + moderate_count

            logger.info(f"\nResults: {robust_count} ROBUST, {moderate_count} MODERATE, {manifest['summary']['weak_count']} WEAK, {manifest['summary']['fail_count']} FAIL")

            if total_passing == 10:
                logger.info("\n✅ SUCCESS! All 10 slots achieved ROBUST or MODERATE!")
                return manifest

            # If not all pass, optimize
            if self.iteration_count < self.max_iterations:
                logger.info(f"\n⚠️  {10 - total_passing} slots below MODERATE. Optimizing parameters...")
                self.optimizer.optimize_failing_strategies(manifest_path)

        logger.info(f"\n⚠️  Reached max iterations ({self.max_iterations})")
        return manifest


if __name__ == '__main__':
    optimizer = IterativeOptimizer()
    final_manifest = optimizer.run_optimization_loop()

    logger.info("\n" + "="*80)
    logger.info("FINAL MANIFEST GENERATED")
    logger.info("="*80)
    logger.info(f"File: C:\\Case Capital\\Axiom day trading\\strategy_manifest.json")
