#!/usr/bin/env python3
"""Update golden reports for compatibility testing.

Regenerates golden JSON reports from test fixtures.
Use --check to verify without updating (for CI).

Usage:
    python scripts/update_golden_reports.py          # Update golden reports
    python scripts/update_golden_reports.py --check   # Check only (CI mode)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
GOLDEN_DIR = ROOT / "tests" / "golden"
FIXTURES_DIR = ROOT / "tests" / "fixtures"
DEMO_REPO = ROOT / "examples" / "demo-paper-repo"

# Golden reports to generate
GOLDEN_REPORTS = [
    {
        "name": "realistic_ml_default",
        "fixture": FIXTURES_DIR / "realistic_ml_repo",
        "profile": "default",
    },
    {
        "name": "realistic_ml_strict",
        "fixture": FIXTURES_DIR / "realistic_ml_repo",
        "profile": "strict",
    },
    {
        "name": "demo_paper_publication",
        "fixture": DEMO_REPO,
        "profile": "publication",
    },
]


def normalize_report(data: dict) -> dict:
    """Normalize a report for golden comparison.

    Removes or normalizes unstable fields.
    """
    # Normalize timestamp
    if "metadata" in data and "generated_at" in data["metadata"]:
        data["metadata"]["generated_at"] = "NORMALIZED"

    # Normalize absolute path
    if "repository" in data and "path" in data["repository"]:
        data["repository"]["path"] = "NORMALIZED"

    # Normalize evidence paths (make relative)
    for check in data.get("checks", []):
        if "evidence" in check:
            normalized = []
            for ev in check["evidence"]:
                # Remove absolute path prefix
                if "/" in ev or "\\" in ev:
                    parts = ev.replace("\\", "/").split("/")
                    # Keep last few meaningful parts
                    normalized.append("/".join(parts[-3:]) if len(parts) > 3 else ev)
                else:
                    normalized.append(ev)
            check["evidence"] = normalized

    return data


def scan_fixture(fixture_path: Path, profile: str) -> dict | None:
    """Scan a fixture and return normalized JSON."""
    result = subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "scan", str(fixture_path),
         "--profile", profile, "--format", "json"],
        capture_output=True, text=True, cwd=ROOT, timeout=30,
    )
    if result.returncode > 2:
        print(f"  ERROR: Scan failed: {result.stderr[:200]}", file=sys.stderr)
        return None

    try:
        data = json.loads(result.stdout)
        return normalize_report(data)
    except json.JSONDecodeError:
        print(f"  ERROR: Invalid JSON output", file=sys.stderr)
        return None


def generate_golden(name: str, fixture_path: Path, profile: str) -> dict | None:
    """Generate a golden report."""
    print(f"  Generating {name} ({fixture_path.name}, {profile})...")
    return scan_fixture(fixture_path, profile)


def check_golden(golden_path: Path, new_data: dict) -> tuple[bool, str]:
    """Check if a golden report matches new data.

    Returns:
        Tuple of (matches, diff_message).
    """
    if not golden_path.exists():
        return False, f"Golden file missing: {golden_path}"

    try:
        old_data = json.loads(golden_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"Cannot read golden file: {exc}"

    # Compare as JSON strings (sorted keys for stability)
    old_str = json.dumps(old_data, sort_keys=True, indent=2)
    new_str = json.dumps(new_data, sort_keys=True, indent=2)

    if old_str == new_str:
        return True, ""

    # Find first difference
    old_lines = old_str.split("\n")
    new_lines = new_str.split("\n")
    for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
        if old_line != new_line:
            return False, f"Line {i+1}:\n  old: {old_line}\n  new: {new_line}"

    return False, "Files differ in length"


def main() -> int:
    parser = argparse.ArgumentParser(description="Update golden reports")
    parser.add_argument("--check", action="store_true",
                        help="Check only, don't update (for CI)")
    parser.add_argument("--root", default=".",
                        help="Project root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    golden_dir = root / "tests" / "golden"

    if args.check:
        print("Checking golden reports...")
    else:
        print("Updating golden reports...")
        golden_dir.mkdir(parents=True, exist_ok=True)

    all_match = True
    mismatches = []

    for entry in GOLDEN_REPORTS:
        name = entry["name"]
        fixture = entry["fixture"]
        profile = entry["profile"]

        if not fixture.exists():
            print(f"  SKIP: {name} (fixture not found)")
            continue

        new_data = generate_golden(name, fixture, profile)
        if new_data is None:
            all_match = False
            mismatches.append(name)
            continue

        golden_path = golden_dir / f"{name}.json"

        if args.check:
            matches, msg = check_golden(golden_path, new_data)
            if matches:
                print(f"  OK: {name}")
            else:
                print(f"  MISMATCH: {name}")
                print(f"    {msg}")
                all_match = False
                mismatches.append(name)
        else:
            golden_path.write_text(
                json.dumps(new_data, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"  Wrote: {golden_path.relative_to(root)}")

    print()
    if args.check:
        if all_match:
            print("All golden reports match.")
            return 0
        else:
            print(f"MISMATCH in: {', '.join(mismatches)}")
            print("Run `python scripts/update_golden_reports.py` to update.")
            return 1
    else:
        print("Done.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
