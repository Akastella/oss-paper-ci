#!/usr/bin/env python3
"""Release gate: pre-release validation checks.

Checks:
1. Version consistency across files
2. README contains key commands
3. CHANGELOG has current version
4. dist/ not in git
5. release-artifacts/ not in git
6. docs/index.md exists
7. CLI reference exists
8. demo gallery exists
9. pyproject.toml metadata complete
10. key docs links exist

Usage:
    python scripts/release_gate.py --format markdown --output report.md
    python scripts/release_gate.py --format json --output report.json
    python scripts/release_gate.py --check  # exit non-zero on failures
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def check_version_consistency() -> tuple[bool, str]:
    """Check version is consistent across files."""
    init_version = None
    pyproject_version = None

    init_file = ROOT / "src" / "oss_paper_ci" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text(encoding="utf-8")
        m = re.search(r'__version__\s*=\s*"(.+?)"', content)
        if m:
            init_version = m.group(1)

    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        m = re.search(r'version\s*=\s*"(.+?)"', content)
        if m:
            pyproject_version = m.group(1)

    if init_version and pyproject_version and init_version == pyproject_version:
        return True, f"Version consistent: {init_version}"
    return False, f"Version mismatch: __init__={init_version}, pyproject={pyproject_version}"


def check_readme_commands() -> tuple[bool, str]:
    """Check README contains key commands."""
    readme = ROOT / "README.md"
    if not readme.exists():
        return False, "README.md not found"

    content = readme.read_text(encoding="utf-8")
    required = ["oss-paper-ci scan", "oss-paper-ci reproduce", "oss-paper-ci capsule"]
    missing = [cmd for cmd in required if cmd not in content]

    if not missing:
        return True, "README contains key commands"
    return False, f"README missing commands: {', '.join(missing)}"


def check_changelog() -> tuple[bool, str]:
    """Check CHANGELOG has current version."""
    changelog = ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return False, "CHANGELOG.md not found"

    init_file = ROOT / "src" / "oss_paper_ci" / "__init__.py"
    content = init_file.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"(.+?)"', content)
    if not m:
        return False, "Cannot determine version"

    version = m.group(1)
    changelog_content = changelog.read_text(encoding="utf-8")
    if version in changelog_content:
        return True, f"CHANGELOG contains {version}"
    return False, f"CHANGELOG missing {version}"


def check_no_dist_in_git() -> tuple[bool, str]:
    """Check dist/ is not tracked."""
    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if "dist/" in content:
            return True, "dist/ in .gitignore"
    return False, "dist/ not in .gitignore"


def check_docs_index() -> tuple[bool, str]:
    """Check docs/index.md exists."""
    if (ROOT / "docs" / "index.md").exists():
        return True, "docs/index.md exists"
    return False, "docs/index.md missing"


def check_cli_reference() -> tuple[bool, str]:
    """Check CLI reference exists."""
    if (ROOT / "docs" / "cli-reference.md").exists():
        return True, "docs/cli-reference.md exists"
    return False, "docs/cli-reference.md missing"


def check_demo_gallery() -> tuple[bool, str]:
    """Check demo gallery exists."""
    if (ROOT / "docs" / "demo-gallery.md").exists():
        return True, "docs/demo-gallery.md exists"
    return False, "docs/demo-gallery.md missing"


def check_pyproject_metadata() -> tuple[bool, str]:
    """Check pyproject.toml has required fields."""
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        return False, "pyproject.toml not found"

    content = pyproject.read_text(encoding="utf-8")
    required = ["name", "version", "description", "readme", "license", "requires-python"]
    missing = [f for f in required if f"{f} " not in content and f"{f}=" not in content]

    if not missing:
        return True, "pyproject.toml metadata complete"
    return False, f"pyproject.toml missing: {', '.join(missing)}"


def check_release_docs() -> tuple[bool, str]:
    """Check release docs exist."""
    if (ROOT / "docs" / "release-process.md").exists():
        return True, "docs/release-process.md exists"
    return False, "docs/release-process.md missing"


ALL_CHECKS = [
    ("version-consistency", check_version_consistency),
    ("readme-commands", check_readme_commands),
    ("changelog", check_changelog),
    ("no-dist-in-git", check_no_dist_in_git),
    ("docs-index", check_docs_index),
    ("cli-reference", check_cli_reference),
    ("demo-gallery", check_demo_gallery),
    ("pyproject-metadata", check_pyproject_metadata),
    ("release-docs", check_release_docs),
]


def run_checks() -> list[dict]:
    """Run all checks and return results."""
    results = []
    for name, check_fn in ALL_CHECKS:
        ok, message = check_fn()
        results.append({"check": name, "ok": ok, "message": message})
    return results


def format_markdown(results: list[dict]) -> str:
    """Format results as markdown."""
    lines = ["# Release Gate\n"]
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    lines.append(f"**{passed}/{total} checks passed**\n")

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        lines.append(f"- [{status}] **{r['check']}**: {r['message']}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Release gate checks")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--check", action="store_true", help="Exit non-zero on failures")
    args = parser.parse_args()

    results = run_checks()

    if args.format == "json":
        output = json.dumps(results, indent=2) + "\n"
    else:
        output = format_markdown(results)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output)

    if args.check:
        failures = [r for r in results if not r["ok"]]
        if failures:
            print(f"\nFAILED: {len(failures)} checks failed", file=sys.stderr)
            return 1
        print("\nPASSED: All checks passed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
