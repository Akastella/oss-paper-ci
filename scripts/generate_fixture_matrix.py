#!/usr/bin/env python3
"""Generate the benchmark fixture matrix.

Runs oss-paper-ci scan against each test fixture and records the results.
Outputs a markdown or JSON matrix of expected scores and statuses.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
FIXTURES_DIR = ROOT / "tests" / "fixtures"
DEMO_REPO = ROOT / "examples" / "demo-paper-repo"

# Fixtures to include in the matrix
FIXTURES = [
    ("minimal_bad_repo", "Python", "Minimal repo with almost nothing"),
    ("broken_paper_repo", "Python", "Paper repo with broken structure"),
    ("paper_ready_repo", "Python", "Well-structured paper repo"),
    ("realistic_ml_repo", "Python", "Realistic ML project"),
    ("r_ready_repo", "R", "R-based paper repo"),
    ("julia_ready_repo", "Julia", "Julia-based paper repo"),
    ("matlab_minimal_repo", "MATLAB", "MATLAB-based paper repo"),
    ("make_snakemake_repo", "Python/Snakemake", "Snakemake workflow repo"),
    ("demo-paper-repo", "Python", "Example paper repo"),
]


def get_fixture_path(name: str) -> Path:
    """Get the path to a fixture directory."""
    if name == "demo-paper-repo":
        return DEMO_REPO
    return FIXTURES_DIR / name


def scan_fixture(fixture_path: Path) -> dict:
    """Run oss-paper-ci scan on a fixture and return the JSON result."""
    result = subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "scan", str(fixture_path),
         "--format", "json"],
        capture_output=True, text=True, cwd=ROOT, timeout=30,
    )
    if result.returncode > 2:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON: {result.stdout[:200]}"}


def generate_matrix() -> list[dict]:
    """Generate the fixture matrix."""
    matrix = []
    for name, language, description in FIXTURES:
        fixture_path = get_fixture_path(name)
        if not fixture_path.exists():
            matrix.append({
                "fixture": name,
                "language": language,
                "description": description,
                "error": "Fixture not found",
            })
            continue

        report = scan_fixture(fixture_path)
        if "error" in report:
            matrix.append({
                "fixture": name,
                "language": language,
                "description": description,
                "error": report["error"],
            })
            continue

        summary = report.get("summary", {})
        checks = report.get("checks", [])

        # Count by classification
        blocking = sum(1 for c in checks
                       if c.get("severity") == "error" and c.get("status") == "fail")
        important = sum(1 for c in checks
                        if (c.get("severity") == "warning" and c.get("status") == "fail")
                        or (c.get("severity") == "error" and c.get("status") == "warn"))
        advisory = len(checks) - blocking - important

        matrix.append({
            "fixture": name,
            "language": language,
            "description": description,
            "expected_status": summary.get("status", "unknown"),
            "score": summary.get("score", 0),
            "blocking_count": blocking,
            "important_count": important,
            "advisory_count": advisory,
            "total_checks": len(checks),
        })

    return matrix


def format_markdown(matrix: list[dict]) -> str:
    """Format the matrix as markdown."""
    lines = ["# Benchmark Fixture Matrix\n"]
    lines.append("Generated from test fixtures using the `default` profile.\n")
    lines.append("")
    lines.append("| Fixture | Language | Status | Score | Blocking | Important | Advisory | Description |")
    lines.append("|---------|----------|--------|-------|----------|-----------|----------|-------------|")

    for entry in matrix:
        if "error" in entry:
            lines.append(
                f"| {entry['fixture']} | {entry['language']} | ERROR | - | - | - | - | {entry.get('error', '')[:50]} |"
            )
        else:
            lines.append(
                f"| {entry['fixture']} | {entry['language']} | "
                f"{entry['expected_status']} | {entry['score']} | "
                f"{entry['blocking_count']} | {entry['important_count']} | "
                f"{entry['advisory_count']} | {entry['description']} |"
            )

    lines.append("")
    lines.append("## Notes\n")
    lines.append("- Scores and statuses are from the `default` profile")
    lines.append("- Different profiles will produce different results")
    lines.append("- The matrix verifies scoring consistency across releases")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate benchmark fixture matrix")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    matrix = generate_matrix()

    if args.format == "json":
        text = json.dumps(matrix, indent=2)
    else:
        text = format_markdown(matrix)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Matrix written to {args.output}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
