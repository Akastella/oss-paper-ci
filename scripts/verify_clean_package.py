#!/usr/bin/env python3
"""Verify a clean release package by extracting and testing in a temporary directory.

Usage:
    python scripts/verify_clean_package.py --zip release-artifacts/oss-paper-ci-v0.5.0rc1-github-clean.zip
    python scripts/verify_clean_package.py --zip release-artifacts/oss-paper-ci-v0.5.0rc1-github-clean.zip --keep-temp
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# Files that must NOT be in the clean package
FORBIDDEN = [
    ".git",  # .git directory excluded; .gitignore is allowed
    "__pycache__", "*.pyc", "*.pyo", "*.egg-info",
    ".pytest_cache", ".coverage", "htmlcov",
    "dist", "build", ".eggs",
    "dev-history", ".claude",
    "round*.json", "round*.md", "round*.sarif",
    "ROUND*.md", "FINAL*.md", "RED_TEAM*.md",
    "RELEASE_*_AUDIT.md", "RELEASE_*_TASKBOARD.md", "RELEASE_*_DELIVERABLES.md",
    "*_AUDIT.md", "*_TASKBOARD.md", "*_DELIVERABLES.md",
    "OSS_PAPER_CI_REPORT*.md", "OSS_PAPER_CI_REPORT*.sarif",
    "SECOND_ROUND_PLAN.md", "DECISIONS.md",
    "release-artifacts",
    ".round4_tmp", ".round5_tmp",
    "test.sarif", "test_rml.sarif",
    "oss-paper-ci-v*.zip",
    "release_truth_*", "release_quarantine_*",
    "dogfooding/results/dogfooding_summary.md",
    "*.capsule.zip",
    ".oss-paper-ci-capsule-staging",
    ".oss-paper-ci-repro",
    ".local_*_audit*.md",
    ".local_*_taskboard*.md",
]

# Files that must be in the clean package
REQUIRED = [
    "README.md", "LICENSE", "pyproject.toml",
    "src/oss_paper_ci/__init__.py",
    "src/oss_paper_ci/cli.py",
    "tests/test_cli.py",
    "docs/usage.md",
    "action.yml",
]


def check_rootless(zip_path: Path) -> list[str]:
    """Check that ZIP is rootless (no wrapper directory)."""
    issues = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [info.filename for info in zf.infolist()]
        top_levels = set()
        for name in names:
            parts = name.split("/")
            if len(parts) > 1:
                top_levels.add(parts[0])
        if len(top_levels) == 1 and "oss-paper-ci" in top_levels:
            issues.append("ZIP is wrapped in oss-paper-ci/ directory (not rootless)")
        # Check README.md is at root
        if "README.md" not in names:
            issues.append("README.md not found at ZIP root")
    return issues


def check_old_dogfooding(zip_path: Path) -> list[str]:
    """Check that old dogfooding rounds are not in the ZIP."""
    issues = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            if "dogfooding" in name:
                for pattern in ["round3", "round4", "round5", "round6", "round7", "round8"]:
                    if pattern in name:
                        issues.append(f"Old dogfooding found: {name}")
                # Check for stale root-level dogfooding_summary.md
                if name.endswith("dogfooding/results/dogfooding_summary.md"):
                    issues.append(f"Stale dogfooding summary: {name}")
    return issues


def check_fake_urls(zip_path: Path) -> list[str]:
    """Check that fake GitHub URLs are not in the ZIP."""
    issues = []
    # Construct the fake URL pattern dynamically to avoid self-detection
    fake_url = "github.com/" + "oss-paper-ci/oss-paper-ci"
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            # Only check text files
            if not any(name.endswith(ext) for ext in
                       [".py", ".md", ".yml", ".yaml", ".toml", ".txt", ".cfg", ".json"]):
                continue
            try:
                content = zf.read(info).decode("utf-8", errors="replace")
                if fake_url in content:
                    issues.append(f"Fake GitHub URL in: {name}")
            except Exception:
                pass
    return issues


def check_stage_files(zip_path: Path) -> list[str]:
    """Check that stage report files are not in the ZIP."""
    issues = []
    stage_patterns = [
        "RELEASE_TRUTH_", "RELEASE_QUARANTINE_",
        "ROUND", "FINAL_", "RED_TEAM_",
        "_AUDIT.md", "_TASKBOARD.md", "_DELIVERABLES.md",
    ]
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            basename = name.split("/")[-1]
            for pattern in stage_patterns:
                if basename.startswith(pattern) or basename.endswith(pattern):
                    issues.append(f"Stage file found: {name}")
                    break
    return issues


def check_forbidden(zip_path: Path) -> list[str]:
    """Check that forbidden files are not in the ZIP."""
    issues = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            parts = name.split("/")
            for part in parts:
                for pattern in FORBIDDEN:
                    if pattern.startswith("*"):
                        if part.endswith(pattern[1:]):
                            issues.append(f"Forbidden: {name} (matches {pattern})")
                    elif part == pattern:
                        issues.append(f"Forbidden: {name} (matches {pattern})")
    return issues


def check_required(zip_path: Path) -> list[str]:
    """Check that required files are in the ZIP."""
    issues = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = {info.filename for info in zf.infolist()}
        for req in REQUIRED:
            found = any(req in n for n in names)
            if not found:
                issues.append(f"Missing required: {req}")
    return issues


def extract_and_test(zip_path: Path, temp_dir: Path) -> dict:
    """Extract ZIP and run verification commands."""
    result = {
        "extracted": False,
        "install_ok": False,
        "version_ok": False,
        "list_checks_ok": False,
        "scan_ok": False,
        "graph_ok": False,
        "baseline_ok": False,
        "smoke_ok": False,
        "pytest_ok": False,
        "errors": [],
    }

    # Extract
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(temp_dir)
        result["extracted"] = True
    except Exception as e:
        result["errors"].append(f"Extract failed: {e}")
        return result

    # Find the extracted directory
    # For rootless zip, files are directly in temp_dir
    # For wrapped zip, files are in a subdirectory
    if (temp_dir / "pyproject.toml").exists():
        # Rootless: files directly in temp_dir
        repo_dir = temp_dir
    else:
        # Wrapped: find the subdirectory
        extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
        if not extracted_dirs:
            result["errors"].append("No directory found after extraction")
            return result
        repo_dir = extracted_dirs[0]

    def run_cmd(cmd: str, cwd: Path = repo_dir) -> tuple[int, str, str]:
        try:
            proc = subprocess.run(
                cmd, shell=True, cwd=cwd, capture_output=True, text=True,
                timeout=600, encoding="utf-8", errors="replace",
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)

    # Install
    code, out, err = run_cmd(f'"{sys.executable}" -m pip install -e ".[dev]"')
    result["install_ok"] = code == 0
    if code != 0:
        result["errors"].append(f"Install failed: {err[:200]}")
        return result

    # Version
    code, out, err = run_cmd(f'"{sys.executable}" -m oss_paper_ci version')
    # Check version matches expected (from pyproject.toml or __init__.py)
    import re
    version_match = re.search(r'(\d+\.\d+\.\d+\w*)', out) if out else None
    result["version_ok"] = code == 0 and version_match is not None
    if not result["version_ok"]:
        result["errors"].append(f"Version check failed: {out} {err}")

    # List checks
    code, out, err = run_cmd(f'"{sys.executable}" -m oss_paper_ci list-checks')
    result["list_checks_ok"] = code == 0 and "META001" in out
    if not result["list_checks_ok"]:
        result["errors"].append(f"List-checks failed: {err[:200]}")

    # Scan
    fixture = repo_dir / "tests" / "fixtures" / "realistic_ml_repo"
    if fixture.exists():
        code, out, err = run_cmd(f'"{sys.executable}" -m oss_paper_ci scan tests/fixtures/realistic_ml_repo --format markdown')
        result["scan_ok"] = code in (0, 1) and "oss-paper-ci" in out
        if not result["scan_ok"]:
            result["errors"].append(f"Scan failed: {err[:200]}")
    else:
        result["errors"].append("realistic_ml_repo fixture not found")

    # Graph
    if fixture.exists():
        code, out, err = run_cmd(f'"{sys.executable}" -m oss_paper_ci graph tests/fixtures/realistic_ml_repo --format json')
        result["graph_ok"] = code == 0 and "nodes" in out
        if not result["graph_ok"]:
            result["errors"].append(f"Graph failed: {err[:200]}")

    # Baseline
    if fixture.exists():
        code, out, err = run_cmd(f'"{sys.executable}" -m oss_paper_ci baseline create tests/fixtures/realistic_ml_repo --output .tmp_baseline.json')
        result["baseline_ok"] = code == 0
        if not result["baseline_ok"]:
            result["errors"].append(f"Baseline failed: {err[:200]}")

    # Smoke dry-run
    if fixture.exists():
        code, out, err = run_cmd(f'"{sys.executable}" -m oss_paper_ci smoke tests/fixtures/realistic_ml_repo --dry-run')
        result["smoke_ok"] = code == 0
        if not result["smoke_ok"]:
            result["errors"].append(f"Smoke failed: {err[:200]}")

    # Pytest
    code, out, err = run_cmd(f'"{sys.executable}" -m pytest tests/ -q')
    result["pytest_ok"] = code == 0
    if code != 0:
        # pytest outputs to stdout, not stderr
        detail = err[:200] if err else out[-500:] if out else "unknown failure"
        result["errors"].append(f"Pytest failed: {detail}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Verify clean release package")
    parser.add_argument("--zip", required=True, help="Path to clean ZIP")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temp directory")
    parser.add_argument("--output-dir", default="release-artifacts", help="Output directory")
    args = parser.parse_args()

    zip_path = Path(args.zip).resolve()
    if not zip_path.exists():
        print(f"ERROR: {zip_path} not found")
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Verifying: {zip_path}")

    # Step 1: Check forbidden files
    print("\n1. Checking for forbidden files...")
    forbidden_issues = check_forbidden(zip_path)
    if forbidden_issues:
        print("FAILED:")
        for issue in forbidden_issues:
            print(f"  - {issue}")
    else:
        print("PASSED: No forbidden files found")

    # Step 1b: Check rootless layout
    print("\n1b. Checking rootless layout...")
    rootless_issues = check_rootless(zip_path)
    if rootless_issues:
        print("FAILED:")
        for issue in rootless_issues:
            print(f"  - {issue}")
    else:
        print("PASSED: ZIP is rootless")

    # Step 1c: Check old dogfooding
    print("\n1c. Checking for old dogfooding...")
    dogfooding_issues = check_old_dogfooding(zip_path)
    if dogfooding_issues:
        print("FAILED:")
        for issue in dogfooding_issues:
            print(f"  - {issue}")
    else:
        print("PASSED: No old dogfooding found")

    # Step 1d: Check stage files
    print("\n1d. Checking for stage report files...")
    stage_issues = check_stage_files(zip_path)
    if stage_issues:
        print("FAILED:")
        for issue in stage_issues:
            print(f"  - {issue}")
    else:
        print("PASSED: No stage files found")

    # Step 1e: Check fake URLs
    print("\n1e. Checking for fake GitHub URLs...")
    fake_url_issues = check_fake_urls(zip_path)
    if fake_url_issues:
        print("FAILED:")
        for issue in fake_url_issues:
            print(f"  - {issue}")
    else:
        print("PASSED: No fake GitHub URLs found")

    # Combine all issues
    all_structural_issues = forbidden_issues + rootless_issues + dogfooding_issues + stage_issues + fake_url_issues
    if not all_structural_issues:
        print("PASSED: No forbidden files found")

    # Step 2: Check required files
    print("\n2. Checking for required files...")
    required_issues = check_required(zip_path)
    if required_issues:
        print("FAILED:")
        for issue in required_issues:
            print(f"  - {issue}")
    else:
        print("PASSED: All required files present")

    # Step 3: Extract and test
    print("\n3. Extracting and testing in clean environment...")
    temp_dir = Path(tempfile.mkdtemp(prefix="oss-paper-ci-verify-"))
    try:
        result = extract_and_test(zip_path, temp_dir)

        tests = [
            ("extract", result["extracted"]),
            ("install", result["install_ok"]),
            ("version", result["version_ok"]),
            ("list-checks", result["list_checks_ok"]),
            ("scan", result["scan_ok"]),
            ("graph", result["graph_ok"]),
            ("baseline", result["baseline_ok"]),
            ("smoke", result["smoke_ok"]),
            ("pytest", result["pytest_ok"]),
        ]

        all_passed = True
        for name, passed in tests:
            status = "PASSED" if passed else "FAILED"
            print(f"  {name}: {status}")
            if not passed:
                all_passed = False

        if result["errors"]:
            print("\nErrors:")
            for err in result["errors"]:
                print(f"  - {err}")

    finally:
        if not args.keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            print(f"\nTemp directory kept: {temp_dir}")

    # Generate report
    all_clean = len(forbidden_issues) == 0 and len(required_issues) == 0
    all_tests_passed = all_clean and result.get("extracted", False) and result.get("pytest_ok", False)

    report_lines = [
        "# Clean Room Verification Report",
        f"\nZIP: {zip_path.name}",
        f"Verified: {datetime.now(timezone.utc).isoformat()}",
        f"\n## Summary",
        f"\n- Forbidden files: {'PASSED' if all_clean else 'FAILED'}",
        f"- Required files: {'PASSED' if not required_issues else 'FAILED'}",
        f"- Install: {'PASSED' if result.get('install_ok') else 'FAILED'}",
        f"- Version: {'PASSED' if result.get('version_ok') else 'FAILED'}",
        f"- Pytest: {'PASSED' if result.get('pytest_ok') else 'FAILED'}",
        f"\n## Overall: {'PASSED' if all_tests_passed else 'FAILED'}",
    ]

    report_path = output_dir / "CLEAN_ROOM_VERIFY.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    # Generate JSON result
    json_result = {
        "zip": zip_path.name,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "forbidden_check": "passed" if all_clean else "failed",
        "required_check": "passed" if not required_issues else "failed",
        "tests": {
            "extract": result.get("extracted", False),
            "install": result.get("install_ok", False),
            "version": result.get("version_ok", False),
            "list_checks": result.get("list_checks_ok", False),
            "scan": result.get("scan_ok", False),
            "graph": result.get("graph_ok", False),
            "baseline": result.get("baseline_ok", False),
            "smoke": result.get("smoke_ok", False),
            "pytest": result.get("pytest_ok", False),
        },
        "overall": "passed" if all_tests_passed else "failed",
        "errors": result.get("errors", []),
    }
    json_path = output_dir / "clean-room-result.json"
    json_path.write_text(json.dumps(json_result, indent=2) + "\n", encoding="utf-8")

    print(f"\nReport: {report_path}")
    print(f"Result: {json_path}")
    print(f"\nOverall: {'PASSED' if all_tests_passed else 'FAILED'}")

    return 0 if all_tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())
