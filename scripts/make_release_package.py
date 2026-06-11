#!/usr/bin/env python3
"""Create a clean GitHub-ready release package.

Usage:
    python scripts/make_release_package.py --version 0.4.0rc1
    python scripts/make_release_package.py --version 0.4.0rc1 --check-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# Files/dirs that MUST be in the clean package
ALLOW_DIRS = {
    "src", "tests", "docs", "examples", "scripts", "dogfooding",
    ".github",
}

ALLOW_FILES = {
    "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md",
    "pyproject.toml", "oss-paper-ci.yml", "action.yml",
    ".pre-commit-hooks.yaml", ".gitignore",
}

# Files/dirs that MUST NOT be in the clean package
DENY_PATTERNS = [
    ".git",  # .git directory excluded; .gitignore is allowed and in ALLOW_FILES
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
    "*.sarif",  # SARIF outputs are build artifacts
    "release-artifacts",
    ".round4_tmp",
    "test.sarif", "test_rml.sarif",
    "release_truth_*", "release_quarantine_*",
    "dogfooding/results/dogfooding_summary.md",
    ".local_*",  # Local audit/taskboard files
    ".tmp-*",  # Temporary directories
    "v2_*_truthfulness.*",
    "v2_*_release_gate.*",
    "site",  # Generated docs site
    ".oss-paper-ci-repro",  # Reproduce workdir
    ".oss-paper-ci-cache",  # Cache directory
    ".oss-paper-ci-capsule-staging",  # Capsule staging
    "oss-paper-ci-out",  # Workbench output
]


def should_exclude(path: str) -> bool:
    """Check if a path should be excluded from the clean package."""
    import fnmatch
    parts = Path(path).parts

    # Check each part against simple deny patterns (directory names, extensions)
    for part in parts:
        for pattern in DENY_PATTERNS:
            if "/" in pattern:
                continue  # Full path patterns handled below
            if pattern.startswith("*"):
                if part.endswith(pattern[1:]):
                    return True
            elif part == pattern:
                return True

    # Check full path patterns (patterns containing / or complex globs)
    for pattern in DENY_PATTERNS:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True

    # Explicitly exclude old dogfooding round directories
    for part in parts:
        if part in ("round3", "round4", "round5", "round6", "round7", "round8", "round9"):
            if "dogfooding" in path:
                return True

    return False


def collect_files(root: Path) -> list[Path]:
    """Collect all files to include in the clean package."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""

        # Skip denied directories
        dirnames[:] = [d for d in dirnames if not should_exclude(os.path.join(rel_dir, d))]

        for fname in filenames:
            rel_path = os.path.join(rel_dir, fname)
            if not should_exclude(rel_path):
                files.append(Path(rel_path))

    return sorted(files)


def create_clean_zip(root: Path, version: str, output_dir: Path) -> Path:
    """Create a clean GitHub-ready ZIP package."""
    zip_name = f"oss-paper-ci-v{version}-github-clean.zip"
    zip_path = output_dir / zip_name

    files = collect_files(root)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            # Rootless: files go directly at zip root, no wrapper directory
            zf.write(root / f, str(f))

    return zip_path


def create_sha256(output_dir: Path) -> Path:
    """Create SHA256SUMS.txt for all files in output_dir."""
    sha_path = output_dir / "SHA256SUMS.txt"
    lines = []
    for f in sorted(output_dir.iterdir()):
        if f.name == "SHA256SUMS.txt":
            continue
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{h}  {f.name}")

    sha_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sha_path


def audit_package(zip_path: Path) -> dict:
    """Audit the clean ZIP for forbidden content."""
    issues = []
    files_in_zip = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            files_in_zip.append(name)

            # Check for forbidden patterns
            parts = name.split("/")
            for part in parts:
                if part == ".git":
                    issues.append(f"Contains .git: {name}")
                elif part == "__pycache__":
                    issues.append(f"Contains __pycache__: {name}")
                elif part.endswith(".egg-info"):
                    issues.append(f"Contains .egg-info: {name}")
                elif part == ".pytest_cache":
                    issues.append(f"Contains .pytest_cache: {name}")
                elif part == "dev-history":
                    issues.append(f"Contains dev-history: {name}")
                elif part.startswith("ROUND") and part.endswith(".md"):
                    issues.append(f"Contains round report: {name}")
                elif part.startswith("FINAL_DELIVERABLES"):
                    issues.append(f"Contains deliverables report: {name}")
                elif part.startswith("RED_TEAM_AUDIT"):
                    issues.append(f"Contains audit report: {name}")

            # Check for .pyc files
            if name.endswith(".pyc") or name.endswith(".pyo"):
                issues.append(f"Contains compiled Python: {name}")

    # Check required files exist (rootless paths)
    required = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "src/oss_paper_ci/__init__.py",
    ]
    for r in required:
        if r not in files_in_zip:
            issues.append(f"Missing required file: {r}")

    # Check for wrapped layout (all files under single directory)
    top_levels = set()
    for name in files_in_zip:
        parts = name.split("/")
        if len(parts) > 1:
            top_levels.add(parts[0])
    if len(top_levels) == 1 and "oss-paper-ci" in top_levels:
        issues.append("ZIP is wrapped in oss-paper-ci/ directory (not rootless)")

    return {
        "total_files": len(files_in_zip),
        "issues": issues,
        "clean": len(issues) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Create clean GitHub release package")
    parser.add_argument("--version", required=True, help="Version string (e.g., 0.4.0rc1)")
    parser.add_argument("--check-only", action="store_true", help="Only audit, don't create")
    parser.add_argument("--output-dir", default="release-artifacts", help="Output directory")
    args = parser.parse_args()

    root = Path(__file__).parent.parent.resolve()
    output_dir = root / args.output_dir
    output_dir.mkdir(exist_ok=True)

    print(f"Version: {args.version}")
    print(f"Root: {root}")
    print(f"Output: {output_dir}")

    if args.check_only:
        # Find existing zip
        zip_path = output_dir / f"oss-paper-ci-v{args.version}-github-clean.zip"
        if not zip_path.exists():
            print(f"ERROR: {zip_path} not found")
            return 1
    else:
        # Create clean zip
        print("\nCreating clean ZIP...")
        zip_path = create_clean_zip(root, args.version, output_dir)
        print(f"Created: {zip_path}")

    # Audit
    print("\nAuditing package...")
    audit = audit_package(zip_path)
    print(f"Files in package: {audit['total_files']}")

    if audit["clean"]:
        print("AUDIT PASSED: No forbidden content found")
    else:
        print("AUDIT FAILED:")
        for issue in audit["issues"]:
            print(f"  - {issue}")
        return 1

    # Create SHA256
    if not args.check_only:
        print("\nCreating SHA256SUMS...")
        sha_path = create_sha256(output_dir)
        print(f"Created: {sha_path}")

    # Generate audit report
    report_path = output_dir / "RELEASE_PACKAGE_AUDIT.md"
    report_lines = [
        "# Release Package Audit",
        f"\nVersion: {args.version}",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"\n## Results",
        f"\n- Files in package: {audit['total_files']}",
        f"- Audit: {'PASSED' if audit['clean'] else 'FAILED'}",
    ]
    if audit["issues"]:
        report_lines.append("\n## Issues")
        for issue in audit["issues"]:
            report_lines.append(f"- {issue}")
    else:
        report_lines.append("\nNo forbidden content found.")

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nAudit report: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
