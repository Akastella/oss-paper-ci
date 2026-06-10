#!/usr/bin/env python3
"""Check documentation and examples for truthfulness issues.

Scans README, docs, examples, action.yml, pyproject.toml, src/, and scripts/ for:
- Unqualified pip install of oss-paper-ci (no PyPI publication qualifier)
- Fake GitHub URLs (unconfirmed repository addresses)
- Composite action using pip install .
- Docs referencing non-existent files
- Workflow referencing non-existent CLI commands
- External program/benefit-oriented language
- Exaggerated claims (production-ready, perfect, fully supports)
- Old round file references
- Old dogfooding references

Usage:
    python scripts/check_docs_truthfulness.py --format markdown --output report.md
    python scripts/check_docs_truthfulness.py --format json --output report.json
    python scripts/check_docs_truthfulness.py --check  # exit non-zero on issues
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Patterns that indicate problems
# Construct fake URL pattern dynamically to avoid self-detection
_FAKE_OWNER = "oss-paper-ci"
FAKE_GITHUB_URL = re.compile(r"github\.com/" + re.escape(_FAKE_OWNER) + r"/" + re.escape(_FAKE_OWNER))
UNQUALIFIED_PIP_INSTALL = re.compile(
    r"(?:python\s+-m\s+)?pip\s+install\s+oss-paper-ci(?![^#\n]*#\s*after\s+PyPI)", re.IGNORECASE
)
PIP_INSTALL_DOT = re.compile(r"pip\s+install\s+\.")
EXAGGERATED_CLAIMS = re.compile(
    r"(production[- ]ready|production[- ]grade|perfect\s+score|"
    r"fully\s+supports\s+all|comprehensive\s+support|"
    r"enterprise[- ]grade|world[- ]class)",
    re.IGNORECASE,
)
EXTERNAL_PROGRAM = re.compile(
    r"(credits?\s+program|Pro\s+plan|account\s+benefit|"
    r"apply\s+for\s+(?:GitHub|Google|AWS|Azure)|"
    r"(?:GitHub|Google|AWS|Azure)\s+(?:credits?|benefits?|program))",
    re.IGNORECASE,
)
OLD_ROUND_REFERENCE = re.compile(
    r"(round[3-7]|ROUND[3-7]|FINAL_DELIVERABLES_ROUND|RED_TEAM_AUDIT_ROUND)"
)

# CLI commands that oss-paper-ci supports
VALID_CLI_COMMANDS = {
    "scan", "init", "explain", "version", "list-checks",
    "graph", "baseline", "smoke", "doctor", "comment",
    "config", "diff", "rules", "validate-contract",
    "reproduce", "capsule",
}

# Files that exist in the project
VALID_DOCS = set()
VALID_EXAMPLES = set()


def discover_valid_files(root: Path) -> None:
    """Discover valid doc and example files."""
    docs_dir = root / "docs"
    if docs_dir.exists():
        for f in docs_dir.rglob("*.md"):
            VALID_DOCS.add(f"docs/{f.relative_to(docs_dir)}")
            VALID_DOCS.add(str(f.relative_to(root)))

    examples_dir = root / "examples"
    if examples_dir.exists():
        for f in examples_dir.rglob("*"):
            if f.is_file():
                VALID_EXAMPLES.add(str(f.relative_to(root)))


def check_file_for_issues(filepath: Path, root: Path) -> list[dict]:
    """Check a single file for truthfulness issues."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return issues

    rel_path = str(filepath.relative_to(root))

    # Skip release infrastructure scripts (they contain patterns as deny rules)
    skip_scripts = {"check_docs_truthfulness.py", "verify_clean_package.py", "make_release_package.py"}
    if filepath.name in skip_scripts:
        return issues
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Skip code comments that qualify the install
        stripped = line.strip()

        # Check for fake GitHub URL
        if FAKE_GITHUB_URL.search(line):
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "blocker",
                "rule": "fake-github-url",
                "message": f"Fake GitHub URL: {FAKE_GITHUB_URL.search(line).group()}",
            })

        # Check for unqualified pip install oss-paper-ci
        # Skip lines that have "after PyPI" or "After PyPI" qualifier
        if UNQUALIFIED_PIP_INSTALL.search(line):
            if "after PyPI" not in line.lower() and "After PyPI" not in line:
                issues.append({
                    "file": rel_path,
                    "line": line_num,
                    "severity": "blocker",
                    "rule": "unqualified-pip-install",
                    "message": f"Unqualified 'pip install oss-paper-ci': {stripped}",
                })

        # Check for pip install . in composite action context
        if rel_path == "action.yml" and PIP_INSTALL_DOT.search(line):
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "blocker",
                "rule": "action-pip-install-dot",
                "message": f"Composite action uses 'pip install .': {stripped}",
            })

        # Check for exaggerated claims
        match = EXAGGERATED_CLAIMS.search(line)
        if match:
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "major",
                "rule": "exaggerated-claim",
                "message": f"Exaggerated claim: '{match.group()}'",
            })

        # Check for external program references
        match = EXTERNAL_PROGRAM.search(line)
        if match:
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "blocker",
                "rule": "external-program",
                "message": f"External program reference: '{match.group()}'",
            })

        # Check for old round references
        match = OLD_ROUND_REFERENCE.search(line)
        if match:
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "major",
                "rule": "old-round-reference",
                "message": f"Old round reference: '{match.group()}'",
            })

    # Check for referenced docs files
    doc_refs = re.findall(r"\[.*?\]\((docs/[^)]+)\)", content)
    for ref in doc_refs:
        if ref not in VALID_DOCS and ref.replace(".md", "") + ".md" not in VALID_DOCS:
            # Check if file actually exists
            ref_path = root / ref
            if not ref_path.exists():
                issues.append({
                    "file": rel_path,
                    "line": 0,
                    "severity": "major",
                    "rule": "missing-doc-reference",
                    "message": f"References non-existent doc: {ref}",
                })

    return issues


def check_workflow_cli_commands(filepath: Path, root: Path) -> list[dict]:
    """Check workflow files for references to non-existent CLI commands."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return issues

    rel_path = str(filepath.relative_to(root))

    # Only match oss-paper-ci when it appears as an actual command invocation
    # Must be preceded by run: |, && |, or at start of a bash-like line
    cmd_pattern = re.compile(
        r"(?:run:\s*\|?\s*|&&\s*|\|\s*|^)oss-paper-ci\s+([a-z][a-z-]*)",
        re.MULTILINE,
    )
    for match in cmd_pattern.finditer(content):
        cmd = match.group(1)
        if cmd not in VALID_CLI_COMMANDS and not cmd.startswith("-"):
            issues.append({
                "file": rel_path,
                "line": 0,
                "severity": "major",
                "rule": "invalid-cli-command",
                "message": f"References non-existent CLI command: oss-paper-ci {cmd}",
            })

    return issues


def scan_project(root: Path) -> list[dict]:
    """Scan the entire project for truthfulness issues."""
    discover_valid_files(root)
    all_issues = []

    # Files to scan
    scan_targets = []

    # README
    readme = root / "README.md"
    if readme.exists():
        scan_targets.append(readme)

    # docs/
    docs_dir = root / "docs"
    if docs_dir.exists():
        scan_targets.extend(docs_dir.rglob("*.md"))

    # examples/
    examples_dir = root / "examples"
    if examples_dir.exists():
        scan_targets.extend(examples_dir.rglob("*.yml"))
        scan_targets.extend(examples_dir.rglob("*.yaml"))

    # action.yml
    action_yml = root / "action.yml"
    if action_yml.exists():
        scan_targets.append(action_yml)

    # pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        scan_targets.append(pyproject)

    # CONTRIBUTING.md, SECURITY.md
    for name in ["CONTRIBUTING.md", "SECURITY.md"]:
        p = root / name
        if p.exists():
            scan_targets.append(p)

    # .pre-commit-hooks.yaml
    precommit = root / ".pre-commit-hooks.yaml"
    if precommit.exists():
        scan_targets.append(precommit)

    # src/ (Python source files)
    src_dir = root / "src"
    if src_dir.exists():
        scan_targets.extend(src_dir.rglob("*.py"))

    # scripts/
    scripts_dir = root / "scripts"
    if scripts_dir.exists():
        scan_targets.extend(scripts_dir.rglob("*.py"))

    # Scan each file
    for filepath in scan_targets:
        all_issues.extend(check_file_for_issues(filepath, root))

    # Check workflow CLI commands
    for filepath in scan_targets:
        if filepath.suffix in (".yml", ".yaml"):
            all_issues.extend(check_workflow_cli_commands(filepath, root))

    return all_issues


def format_markdown(issues: list[dict]) -> str:
    """Format issues as markdown."""
    lines = [
        "# Documentation Truthfulness Report",
        "",
        f"**Total issues:** {len(issues)}",
        "",
    ]

    if not issues:
        lines.append("No issues found. Documentation is truthful.")
        return "\n".join(lines)

    blockers = [i for i in issues if i["severity"] == "blocker"]
    majors = [i for i in issues if i["severity"] == "major"]
    minors = [i for i in issues if i["severity"] == "minor"]

    if blockers:
        lines.append(f"## BLOCKER ({len(blockers)})")
        lines.append("")
        for issue in blockers:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            lines.append(f"- **[{issue['rule']}]** `{loc}`: {issue['message']}")
        lines.append("")

    if majors:
        lines.append(f"## MAJOR ({len(majors)})")
        lines.append("")
        for issue in majors:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            lines.append(f"- **[{issue['rule']}]** `{loc}`: {issue['message']}")
        lines.append("")

    if minors:
        lines.append(f"## MINOR ({len(minors)})")
        lines.append("")
        for issue in minors:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            lines.append(f"- **[{issue['rule']}]** `{loc}`: {issue['message']}")
        lines.append("")

    return "\n".join(lines)


def format_json(issues: list[dict]) -> str:
    """Format issues as JSON."""
    result = {
        "total_issues": len(issues),
        "blockers": len([i for i in issues if i["severity"] == "blocker"]),
        "majors": len([i for i in issues if i["severity"] == "major"]),
        "minors": len([i for i in issues if i["severity"] == "minor"]),
        "issues": issues,
        "passed": len([i for i in issues if i["severity"] == "blocker"]) == 0,
    }
    return json.dumps(result, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Check documentation truthfulness")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Output format",
    )
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument(
        "--check", action="store_true",
        help="Exit non-zero if any blocker issues found",
    )
    parser.add_argument(
        "--root", default=".",
        help="Project root directory (default: current directory)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issues = scan_project(root)

    if args.format == "markdown":
        output = format_markdown(issues)
    else:
        output = format_json(issues)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output)

    if args.check:
        blockers = [i for i in issues if i["severity"] == "blocker"]
        if blockers:
            print(f"\nFAILED: {len(blockers)} blocker issues found", file=sys.stderr)
            return 1
        print("\nPASSED: No blocker issues found")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
