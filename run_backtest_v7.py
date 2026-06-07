from backtest_engine_v7_final import HybridBacktester


def main() -> None:
    backtester = HybridBacktester()
    backtester.test_all()
    manifest = backtester.save_manifest()

    print("")
    print("=" * 80)
    print("V7 FINAL RESULTS")
    print("=" * 80)
    passing = manifest["summary"]["robust"] + manifest["summary"]["moderate"]
    print(f"ROBUST: {manifest['summary']['robust']}/10")
    print(f"MODERATE: {manifest['summary']['moderate']}/10")
    print(f"PASSING: {passing}/10")
    print("=" * 80)


if __name__ == "__main__":
    main()
