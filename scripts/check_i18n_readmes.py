#!/usr/bin/env python3
"""Check internationalization consistency across multilingual READMEs.

Verifies:
1. All language versions exist
2. Language links are present
3. Core CLI commands are consistent
4. Safety warnings are present
5. No overclaiming language

Usage:
    python scripts/check_i18n_readmes.py
    python scripts/check_i18n_readmes.py --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

LANGUAGES = {
    "en": {"file": "README.md", "name": "English"},
    "zh-CN": {"file": "README.zh-CN.md", "name": "简体中文"},
    "ja": {"file": "README.ja.md", "name": "日本語"},
}

REQUIRED_COMMANDS = [
    "oss-paper-ci scan",
    "oss-paper-ci reproduce",
    "oss-paper-ci capsule",
]

OVERCLAIM_PATTERNS = [
    (r"(?<!not )guarantee.*reproduc", "Claims guaranteed reproduction"),
    (r"(?<!does not )prove.*paper.*correct", "Claims to prove paper correctness"),
    (r"paper.*reproduced.*successfully", "Claims successful reproduction"),
    (r"(?<!不是)保证复现", "Claims guaranteed reproduction (Chinese)"),
    (r"(?<!不)(?<!不会)证明.*论文.*正确", "Claims paper correctness (Chinese)"),
    (r"完全再現保証", "Claims guaranteed reproduction (Japanese)"),
    (r"(?<!正しくない)論文.*正しい", "Claims paper correctness (Japanese)"),
]


def check_file_exists(lang: str) -> tuple[bool, str]:
    """Check if a language README exists."""
    info = LANGUAGES[lang]
    path = ROOT / info["file"]
    if path.exists():
        return True, f"{info['file']} exists"
    return False, f"{info['file']} missing"


def check_language_links(lang: str) -> tuple[bool, str]:
    """Check if language links are present."""
    info = LANGUAGES[lang]
    path = ROOT / info["file"]
    if not path.exists():
        return False, f"{info['file']} not found"

    content = path.read_text(encoding="utf-8")

    # Check for links to other languages
    other_langs = [l for l in LANGUAGES if l != lang]
    missing = []
    for other in other_langs:
        other_info = LANGUAGES[other]
        if other_info["file"] not in content:
            missing.append(other_info["name"])

    if not missing:
        return True, "Language links present"
    return False, f"Missing links to: {', '.join(missing)}"


def check_commands_consistent(lang: str) -> tuple[bool, str]:
    """Check if core CLI commands are present."""
    info = LANGUAGES[lang]
    path = ROOT / info["file"]
    if not path.exists():
        return False, f"{info['file']} not found"

    content = path.read_text(encoding="utf-8")

    missing = []
    for cmd in REQUIRED_COMMANDS:
        if cmd not in content:
            missing.append(cmd)

    if not missing:
        return True, "All core commands present"
    return False, f"Missing commands: {', '.join(missing)}"


def check_safety_warning(lang: str) -> tuple[bool, str]:
    """Check if safety warnings are present."""
    info = LANGUAGES[lang]
    path = ROOT / info["file"]
    if not path.exists():
        return False, f"{info['file']} not found"

    content = path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Check for execute risk warning
    has_execute = "--execute" in content
    has_warning = (
        "trust" in content_lower or "risk" in content_lower or "danger" in content_lower or
        "风险" in content or "信任" in content or "危险" in content or "注意" in content or
        "リスク" in content or "注意" in content or "危険" in content
    )

    if has_execute and has_warning:
        return True, "Execute risk warning present"
    return False, "Missing --execute risk warning"


def check_no_overclaiming(lang: str) -> tuple[bool, str]:
    """Check for overclaiming language."""
    info = LANGUAGES[lang]
    path = ROOT / info["file"]
    if not path.exists():
        return False, f"{info['file']} not found"

    content = path.read_text(encoding="utf-8")

    for pattern, desc in OVERCLAIM_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return False, f"Overclaiming: {desc}"

    return True, "No overclaiming language"


ALL_CHECKS = [
    ("file_exists", check_file_exists),
    ("language_links", check_language_links),
    ("commands_consistent", check_commands_consistent),
    ("safety_warning", check_safety_warning),
    ("no_overclaiming", check_no_overclaiming),
]


def run_checks() -> list[dict]:
    """Run all i18n checks."""
    results = []
    for lang in LANGUAGES:
        for check_name, check_fn in ALL_CHECKS:
            ok, message = check_fn(lang)
            results.append({
                "language": lang,
                "check": check_name,
                "ok": ok,
                "message": message,
            })
    return results


def format_markdown(results: list[dict]) -> str:
    """Format results as markdown."""
    lines = ["# i18n Consistency Check\n"]
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    lines.append(f"**{passed}/{total} checks passed**\n")

    for lang in LANGUAGES:
        lang_results = [r for r in results if r["language"] == lang]
        lang_passed = sum(1 for r in lang_results if r["ok"])
        lines.append(f"## {LANGUAGES[lang]['name']} ({lang_passed}/{len(lang_results)})\n")
        for r in lang_results:
            status = "PASS" if r["ok"] else "FAIL"
            lines.append(f"- [{status}] **{r['check']}**: {r['message']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check i18n consistency")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o", help="Output file path")
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

    failures = [r for r in results if not r["ok"]]
    if failures:
        print(f"\nFAILED: {len(failures)} checks failed", file=sys.stderr)
        return 1
    print("\nPASSED: All i18n checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
