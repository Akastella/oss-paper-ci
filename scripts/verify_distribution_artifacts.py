#!/usr/bin/env python3
"""Verify distribution artifacts for oss-paper-ci.

Checks that the built wheel and sdist are valid, installable, and contain
the expected files without local path pollution or forbidden content.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).parent.parent

# Files that must NOT appear in distribution artifacts
FORBIDDEN_PATTERNS = [
    ".local_",
    "v2_8_truthfulness",
    "v2_8_release_gate",
    "release-artifacts/",
    "site/",
    ".tmp-",
    "oss-paper-ci-out/",
    ".oss-paper-ci-repro/",
    ".oss-paper-ci-cache/",
    ".oss-paper-ci-capsule-staging/",
    "*.capsule.zip",
]

# Files that MUST be present
REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "pyproject.toml",
]


def check_sdist(sdist_path: Path) -> list[str]:
    """Check sdist can be extracted and contains required files."""
    issues = []

    if not sdist_path.exists():
        issues.append(f"SDist not found: {sdist_path}")
        return issues

    try:
        with zipfile.ZipFile(sdist_path) as zf:
            names = zf.namelist()

            # Check for required files
            for req in REQUIRED_FILES:
                found = any(req in n for n in names)
                if not found:
                    issues.append(f"SDist missing required file: {req}")

            # Check for forbidden files
            for pattern in FORBIDDEN_PATTERNS:
                found = any(pattern in n for n in names)
                if found:
                    issues.append(f"SDist contains forbidden pattern: {pattern}")

            # Check for local paths
            for name in names:
                if name.endswith((".py", ".md", ".yml", ".yaml", ".json")):
                    try:
                        content = zf.read(name).decode("utf-8", errors="ignore")
                        if "/home/" in content or "C:\\" in content:
                            issues.append(f"SDist file contains local path: {name}")
                    except Exception:
                        pass

    except Exception as e:
        issues.append(f"Failed to read SDist: {e}")

    return issues


def check_wheel(wheel_path: Path) -> list[str]:
    """Check wheel can be installed and entry point works."""
    issues = []

    if not wheel_path.exists():
        issues.append(f"Wheel not found: {wheel_path}")
        return issues

    # Create temp venv and install
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_path = Path(tmpdir) / "venv"

        try:
            # Create venv
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True, capture_output=True,
            )

            # Install wheel
            pip_path = venv_path / "bin" / "pip"
            if sys.platform == "win32":
                pip_path = venv_path / "Scripts" / "pip.exe"

            subprocess.run(
                [str(pip_path), "install", str(wheel_path)],
                check=True, capture_output=True,
            )

            # Verify entry point
            cli_path = venv_path / "bin" / "oss-paper-ci"
            if sys.platform == "win32":
                cli_path = venv_path / "Scripts" / "oss-paper-ci.exe"

            result = subprocess.run(
                [str(cli_path), "version"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                issues.append(f"Entry point failed: {result.stderr}")

            # Verify quickstart
            result = subprocess.run(
                [str(cli_path), "quickstart", "--format", "json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                issues.append(f"Quickstart failed: {result.stderr}")

            # Verify try-demo
            result = subprocess.run(
                [str(cli_path), "try-demo", "--format", "json"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                issues.append(f"Try-demo failed: {result.stderr}")

            # Check for local path pollution in output
            result = subprocess.run(
                [str(cli_path), "try-demo", "--format", "json"],
                capture_output=True, text=True, timeout=60,
            )
            if "/home/" in result.stdout or "C:\\" in result.stdout:
                issues.append("Try-demo output contains local paths")

        except subprocess.CalledProcessError as e:
            issues.append(f"Subprocess failed: {e}")
        except Exception as e:
            issues.append(f"Wheel check failed: {e}")

    return issues


def check_version(expected_version: str) -> list[str]:
    """Check version matches expected."""
    issues = []

    init_path = ROOT / "src" / "oss_paper_ci" / "__init__.py"
    if init_path.exists():
        content = init_path.read_text(encoding="utf-8")
        if expected_version not in content:
            issues.append(f"Version mismatch in __init__.py: expected {expected_version}")

    pyproject_path = ROOT / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        if expected_version not in content:
            issues.append(f"Version mismatch in pyproject.toml: expected {expected_version}")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Verify distribution artifacts")
    parser.add_argument("--version", required=True, help="Expected version string")
    parser.add_argument("--dist-dir", default=str(ROOT / "dist"), help="Distribution directory")
    parser.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir)
    all_issues = []

    # Find artifacts
    sdists = list(dist_dir.glob("*.tar.gz"))
    wheels = list(dist_dir.glob("*.whl"))

    if not sdists:
        all_issues.append("No sdist found in dist/")
    if not wheels:
        all_issues.append("No wheel found in dist/")

    # Check version
    version_issues = check_version(args.version)
    all_issues.extend(version_issues)

    # Check sdist
    for sdist in sdists:
        sdist_issues = check_sdist(sdist)
        all_issues.extend(sdist_issues)

    # Check wheel
    for wheel in wheels:
        wheel_issues = check_wheel(wheel)
        all_issues.extend(wheel_issues)

    # Output results
    if args.format == "json":
        print(json.dumps({
            "version": args.version,
            "issues": all_issues,
            "passed": len(all_issues) == 0,
        }, indent=2))
    elif args.format == "markdown":
        print("# Distribution Verification")
        print(f"\n**Version:** {args.version}")
        print(f"\n**Issues:** {len(all_issues)}")
        if all_issues:
            print("\n## Issues Found\n")
            for issue in all_issues:
                print(f"- {issue}")
        else:
            print("\n✅ All checks passed!")
    else:
        if all_issues:
            print(f"FAIL: {len(all_issues)} issues found:")
            for issue in all_issues:
                print(f"  - {issue}")
        else:
            print(f"PASS: Distribution artifacts for {args.version} verified successfully")

    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
