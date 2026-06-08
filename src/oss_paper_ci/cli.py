"""CLI entry point for oss-paper-ci."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from oss_paper_ci import __version__


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point.

    Returns:
        Exit code: 0 for pass, 1 for warnings, 2 for errors.
    """
    # Ensure stdout/stderr handle UTF-8 on Windows
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        prog="oss-paper-ci",
        description="Check reproducibility readiness of scientific paper repositories.",
    )
    parser.add_argument("--version", action="version", version=f"oss-paper-ci {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a repository for reproducibility checks.")
    scan_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    scan_parser.add_argument("--config", dest="config_path", help="Path to oss-paper-ci.yml config file.")
    scan_parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    scan_parser.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # init command
    subparsers.add_parser("init", help="Generate a default oss-paper-ci.yml config file.")

    # explain command
    explain_parser = subparsers.add_parser("explain", help="Explain a check ID.")
    explain_parser.add_argument("check_id", help="The check ID to explain (e.g., ENV001).")

    # version command
    subparsers.add_parser("version", help="Print version.")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "version":
        print(f"oss-paper-ci {__version__}")
        return 0

    if args.command == "init":
        return _cmd_init()

    if args.command == "explain":
        return _cmd_explain(args.check_id)

    if args.command == "scan":
        return _cmd_scan(args.path, args.config_path, args.format, args.output)

    parser.print_help()
    return 0


def _cmd_init() -> int:
    """Generate default config file."""
    from oss_paper_ci.config import generate_default_config

    target = Path("oss-paper-ci.yml")
    if target.exists():
        print(f"Config file already exists: {target}", file=sys.stderr)
        return 1

    target.write_text(generate_default_config(), encoding="utf-8")
    print(f"Created {target}")
    return 0


def _cmd_explain(check_id: str) -> int:
    """Explain a check ID."""
    from oss_paper_ci.checks import get_all_checkers
    from oss_paper_ci.checks.base import BaseChecker, CheckContext
    from oss_paper_ci.config import Config

    # Build a lookup of all check IDs
    _ensure_checkers_loaded()
    explanations = _get_check_explanations()

    check_id_upper = check_id.upper()
    if check_id_upper in explanations:
        info = explanations[check_id_upper]
        print(f"Check: {info['id']}")
        print(f"Title: {info['title']}")
        print(f"Severity: {info['severity']}")
        print(f"Description: {info['description']}")
        return 0

    print(f"Unknown check ID: {check_id}", file=sys.stderr)
    print(f"Available check IDs: {', '.join(sorted(explanations.keys()))}", file=sys.stderr)
    return 1


def _ensure_checkers_loaded() -> None:
    """Ensure all checker modules are imported."""
    from oss_paper_ci.checks import _ensure_loaded
    _ensure_loaded()


def _get_check_explanations() -> dict[str, dict[str, str]]:
    """Build a lookup table of check ID -> explanation."""
    from oss_paper_ci.checks import get_all_checkers

    explanations = {}
    for cls in get_all_checkers():
        checker = cls()
        if hasattr(checker, 'check_id') and checker.check_id:
            explanations[checker.check_id] = {
                "id": checker.check_id,
                "title": getattr(checker, 'title', ''),
                "severity": getattr(checker, 'severity', 'info'),
                "description": getattr(checker, 'description', getattr(checker, 'title', '')),
            }
    return explanations


def _cmd_scan(
    repo_path: str,
    config_path: str | None,
    fmt: str,
    output: str | None,
) -> int:
    """Run the scan command."""
    from oss_paper_ci.config import load_config
    from oss_paper_ci.reporting import generate_json_report, generate_markdown_report
    from oss_paper_ci.scanner import scan as run_scan

    path = Path(repo_path).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        return 2

    config = load_config(config_path=config_path, repo_root=str(path))
    report = run_scan(str(path), config)

    if fmt == "json":
        text = generate_json_report(report, output_path=output)
    else:
        text = generate_markdown_report(report, output_path=output)

    if output:
        print(f"Report written to {output}")
    else:
        print(text)

    # Exit code based on status
    if report.summary.status == "fail":
        return 2
    elif report.summary.status == "warn":
        return 1
    return 0
