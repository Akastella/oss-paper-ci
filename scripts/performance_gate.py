#!/usr/bin/env python3
"""Performance gate for oss-paper-ci.

Measures scan runtime for test fixtures and reports results.
Used to detect performance regressions in CI.

Usage:
    python scripts/performance_gate.py --format markdown --output performance.md
    python scripts/performance_gate.py --format json --output performance.json
    python scripts/performance_gate.py --max-seconds 30
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
FIXTURES_DIR = ROOT / "tests" / "fixtures"

# Fixtures to benchmark
FIXTURES = [
    "minimal_bad_repo",
    "broken_paper_repo",
    "paper_ready_repo",
    "realistic_ml_repo",
]

# Default time budget per fixture (seconds)
DEFAULT_BUDGET_SECONDS = 30.0


def scan_fixture(fixture_path: Path) -> tuple[float, bool]:
    """Run a scan and measure runtime.

    Returns:
        Tuple of (runtime_seconds, success).
    """
    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "scan", str(fixture_path),
         "--format", "json"],
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    elapsed = time.monotonic() - start
    return elapsed, result.returncode <= 2


def run_benchmarks() -> list[dict]:
    """Run benchmarks on all fixtures."""
    results = []

    for name in FIXTURES:
        fixture_path = FIXTURES_DIR / name
        if not fixture_path.exists():
            results.append({
                "name": name,
                "runtime_seconds": 0,
                "status": "SKIP",
                "error": "Fixture not found",
            })
            continue

        runtime, success = scan_fixture(fixture_path)
        results.append({
            "name": name,
            "runtime_seconds": round(runtime, 3),
            "status": "PASS" if success else "FAIL",
        })

    return results


def format_markdown(results: list[dict], budget: float) -> str:
    """Format results as markdown."""
    lines = ["# Performance Gate Results\n"]
    lines.append("")
    lines.append("| Fixture | Runtime (s) | Status |")
    lines.append("|---------|-------------|--------|")

    total = 0.0
    for r in results:
        runtime = r["runtime_seconds"]
        total += runtime
        status = r["status"]
        if status == "SKIP":
            lines.append(f"| {r['name']} | - | SKIP |")
        else:
            budget_mark = " ⚠️" if runtime > budget else ""
            lines.append(f"| {r['name']} | {runtime:.3f} | {status}{budget_mark} |")

    lines.append("")
    lines.append(f"**Total:** {total:.3f}s")
    lines.append(f"**Budget per fixture:** {budget:.1f}s")
    any_fail = any(r["status"] == "FAIL" for r in results)
    any_over = any(r["runtime_seconds"] > budget and r["status"] != "SKIP" for r in results)
    passed = not any_fail and not any_over
    lines.append(f"**Result:** {'PASS' if passed else 'FAIL'}")
    lines.append("")

    return "\n".join(lines)


def format_json(results: list[dict], budget: float) -> str:
    """Format results as JSON."""
    total = sum(r["runtime_seconds"] for r in results)
    any_fail = any(r["status"] == "FAIL" for r in results)
    any_over = any(r["runtime_seconds"] > budget and r["status"] != "SKIP" for r in results)

    return json.dumps({
        "fixtures": results,
        "total_seconds": round(total, 3),
        "budget_seconds": budget,
        "passed": not any_fail and not any_over,
    }, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Performance gate for oss-paper-ci")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--max-seconds", type=float, default=DEFAULT_BUDGET_SECONDS,
                        help=f"Max seconds per fixture (default: {DEFAULT_BUDGET_SECONDS})")
    args = parser.parse_args()

    results = run_benchmarks()

    if args.format == "json":
        text = format_json(results, args.max_seconds)
    else:
        text = format_markdown(results, args.max_seconds)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Results written to {args.output}")
    else:
        print(text)

    # Exit non-zero if any fixture failed or exceeded budget
    any_fail = any(r["status"] == "FAIL" for r in results)
    any_over = any(r["runtime_seconds"] > args.max_seconds and r["status"] != "SKIP" for r in results)
    return 1 if any_fail or any_over else 0


if __name__ == "__main__":
    sys.exit(main())
