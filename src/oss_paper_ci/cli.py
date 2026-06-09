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
    scan_parser.add_argument("--format", choices=["json", "markdown", "sarif", "html", "github"], default="markdown", help="Output format.")
    scan_parser.add_argument("--output", "-o", help="Write report to file instead of stdout.")
    scan_parser.add_argument("--fail-under", type=int, dest="fail_under", help="Exit with code 1 if score is below this threshold.")
    scan_parser.add_argument("--strict", action="store_true", help="Exit with code 1 if any warnings exist.")
    scan_parser.add_argument("--verbose", action="store_true", help="Show all check details with evidence in markdown report.")
    scan_parser.add_argument("--github-step-summary", dest="github_step_summary", help="Write Markdown summary to file (for $GITHUB_STEP_SUMMARY).")
    scan_parser.add_argument("--max-annotations", type=int, dest="max_annotations", default=50, help="Max annotations for github format (default: 50).")
    scan_parser.add_argument("--fail-on", dest="fail_on", help="Fail on severity level (e.g., major, error).")

    # init command
    init_parser = subparsers.add_parser("init", help="Generate a default config or contract file.")
    init_parser.add_argument("--contract", action="store_true", help="Generate reproducibility.yml template")
    init_parser.add_argument("--template", choices=["ml", "simulation", "data-science", "default"], default="default")
    init_parser.add_argument("--output", "-o", help="Output file path")

    # explain command
    explain_parser = subparsers.add_parser("explain", help="Explain a check ID.")
    explain_parser.add_argument("check_id", help="The check ID to explain (e.g., ENV001).")

    # list-checks command
    list_checks_parser = subparsers.add_parser("list-checks", help="List all available checks.")
    list_checks_parser.add_argument("--category", help="Filter by category (e.g., metadata, environment).")
    list_checks_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

    # validate-contract command
    validate_parser = subparsers.add_parser("validate-contract", help="Validate a reproducibility contract.")
    validate_parser.add_argument("path", nargs="?", default=".")
    validate_parser.add_argument("--contract", help="Path to reproducibility.yml")

    # graph command
    graph_parser = subparsers.add_parser("graph", help="Build and display evidence graph.")
    graph_parser.add_argument("path", nargs="?", default=".")
    graph_parser.add_argument("--format", choices=["json", "markdown", "dot"], default="markdown")
    graph_parser.add_argument("--output", "-o")
    graph_parser.add_argument("--show-orphans", action="store_true")
    graph_parser.add_argument("--show-conflicts", action="store_true")

    # version command
    subparsers.add_parser("version", help="Print version.")

    # baseline command
    baseline_parser = subparsers.add_parser("baseline", help="Baseline management.")
    baseline_sub = baseline_parser.add_subparsers(dest="baseline_command")

    # baseline create
    create_bl_parser = baseline_sub.add_parser("create", help="Create a baseline from current scan.")
    create_bl_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    create_bl_parser.add_argument("--output", "-o", default=".oss-paper-ci/baseline.json",
                                  help="Output baseline file (default: .oss-paper-ci/baseline.json)")

    # baseline compare
    compare_bl_parser = baseline_sub.add_parser("compare", help="Compare current scan against a baseline.")
    compare_bl_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    compare_bl_parser.add_argument("--baseline", required=True, help="Path to baseline JSON file.")
    compare_bl_parser.add_argument("--format", choices=["json", "markdown"], default="markdown",
                                   help="Output format (default: markdown)")
    compare_bl_parser.add_argument("--output", "-o", help="Write report to file instead of stdout.")
    compare_bl_parser.add_argument("--fail-on-regression", action="store_true",
                                   help="Exit with code 1 if any regressions are detected.")

    # smoke command
    smoke_parser = subparsers.add_parser("smoke", help="Run smoke tests safely.")
    smoke_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    smoke_parser.add_argument("--contract", help="Path to reproducibility.yml contract file.")
    smoke_parser.add_argument("--experiment", default="smoke",
                              help="Experiment ID to run (default: smoke)")
    smoke_parser.add_argument("--timeout", type=int, default=60,
                              help="Timeout in seconds (default: 60)")
    smoke_parser.add_argument("--dry-run", action="store_true",
                              help="Show the command without executing it.")
    smoke_parser.add_argument("--command", dest="smoke_command",
                              help="Override the smoke command (instead of reading from contract).")
    smoke_parser.add_argument("--format", choices=["json", "text"], default="text",
                              help="Output format (default: text)")

    # doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Diagnose repository and environment.")
    doctor_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    doctor_parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")

    # comment command
    comment_parser = subparsers.add_parser("comment", help="Generate PR comment from scan results.")
    comment_parser.add_argument("--input", required=True, help="Path to scan JSON report.")
    comment_parser.add_argument("--output", "-o", help="Write comment to file instead of stdout.")
    comment_parser.add_argument("--kind", choices=["scan", "baseline"], default="scan", help="Comment type.")
    comment_parser.add_argument("--max-findings", type=int, default=10, help="Max findings to show.")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "version":
        print(f"oss-paper-ci {__version__}")
        return 0

    if args.command == "init":
        return _cmd_init(
            contract=getattr(args, "contract", False),
            template=getattr(args, "template", "default"),
            output=getattr(args, "output", None),
        )

    if args.command == "validate-contract":
        return _cmd_validate_contract(args.path, getattr(args, "contract", None))

    if args.command == "explain":
        return _cmd_explain(args.check_id)

    if args.command == "list-checks":
        return _cmd_list_checks(args.category, args.format)

    if args.command == "scan":
        return _cmd_scan(
            args.path, args.config_path, args.format, args.output,
            fail_under=getattr(args, "fail_under", None),
            strict=getattr(args, "strict", False),
            verbose=getattr(args, "verbose", False),
            github_step_summary=getattr(args, "github_step_summary", None),
            max_annotations=getattr(args, "max_annotations", 50),
            fail_on=getattr(args, "fail_on", None),
        )

    if args.command == "graph":
        return _cmd_graph(
            args.path, args.format, args.output,
            show_orphans=getattr(args, "show_orphans", False),
            show_conflicts=getattr(args, "show_conflicts", False),
        )

    if args.command == "baseline":
        return _cmd_baseline(args)

    if args.command == "smoke":
        return _cmd_smoke(args)

    if args.command == "doctor":
        return _cmd_doctor(args.path, args.format)

    if args.command == "comment":
        return _cmd_comment(args.input, args.output, args.kind, args.max_findings)

    parser.print_help()
    return 0


def _cmd_init(
    *,
    contract: bool = False,
    template: str = "default",
    output: str | None = None,
) -> int:
    """Generate default config file or contract template."""
    if contract:
        from oss_paper_ci.contract import generate_contract_template

        target = Path(output or "reproducibility.yml")
        if target.exists():
            print(f"Contract file already exists: {target}", file=sys.stderr)
            return 1

        target.write_text(generate_contract_template(template), encoding="utf-8")
        print(f"Created {target}")
        return 0

    from oss_paper_ci.config import generate_default_config

    target = Path("oss-paper-ci.yml")
    if target.exists():
        print(f"Config file already exists: {target}", file=sys.stderr)
        return 1

    target.write_text(generate_default_config(), encoding="utf-8")
    print(f"Created {target}")
    return 0


def _cmd_validate_contract(repo_path: str, contract_path: str | None) -> int:
    """Validate a reproducibility contract."""
    from oss_paper_ci.contract import find_contract, load_contract, validate_contract

    path = Path(repo_path).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        return 2

    # Find the contract file.
    if contract_path:
        cpath = Path(contract_path)
        if not cpath.exists():
            print(f"Error: contract file not found: {contract_path}", file=sys.stderr)
            return 2
        cpath = str(cpath.resolve())
    else:
        cpath = find_contract(str(path))

    if cpath is None:
        print("No reproducibility contract found.", file=sys.stderr)
        print("Run `oss-paper-ci init --contract` to create one.", file=sys.stderr)
        return 1

    # Parse the contract.
    try:
        contract = load_contract(cpath)
    except Exception as exc:
        print(f"Error parsing contract: {exc}", file=sys.stderr)
        return 2

    print(f"Contract: {cpath}")
    print(f"Version:  {contract.version}")
    print(f"Project:  {contract.project_name or '(unnamed)'}")
    print(f"Type:     {contract.project_type}")
    print()

    # Validate.
    issues = validate_contract(contract, str(path))

    if not issues:
        print("All checks passed. Contract is valid.")
        return 0

    warnings = [i for i in issues if i.severity.value == "warning"]
    infos = [i for i in issues if i.severity.value == "info"]

    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w.message}")

    if infos:
        print(f"Info ({len(infos)}):")
        for i in infos:
            print(f"  - {i.message}")

    if warnings:
        return 1
    return 0


def _cmd_explain(check_id: str) -> int:
    """Explain a check ID."""
    from oss_paper_ci.checks.registry import get_checker_by_id, get_all_checkers

    check_id_upper = check_id.upper()
    cls = get_checker_by_id(check_id_upper)
    if cls is not None:
        checker = cls()
        print(f"Check: {checker.check_id}")
        print(f"Title: {checker.title}")
        print(f"Severity: {checker.severity.value if hasattr(checker.severity, 'value') else checker.severity}")
        if checker.category:
            print(f"Category: {checker.category}")
        desc = checker.description or checker.title
        print(f"Description: {desc}")
        return 0

    # Fallback: show available IDs
    all_ids = sorted(
        c.check_id for c in (cls() for cls in get_all_checkers())
        if c.check_id
    )
    print(f"Unknown check ID: {check_id}", file=sys.stderr)
    print(f"Available check IDs: {', '.join(all_ids)}", file=sys.stderr)
    return 1


def _cmd_list_checks(category: str | None, fmt: str) -> int:
    """List all available checks."""
    import json as json_mod

    from oss_paper_ci.checks.registry import get_all_checkers, get_checkers_by_category

    if category:
        checker_classes = get_checkers_by_category(category)
    else:
        checker_classes = get_all_checkers()

    entries = []
    for cls in checker_classes:
        checker = cls()
        sev = checker.severity.value if hasattr(checker.severity, "value") else str(checker.severity)
        desc = checker.description or checker.title
        if len(desc) > 80:
            desc = desc[:77] + "..."
        entries.append({
            "id": checker.check_id,
            "title": checker.title,
            "severity": sev,
            "category": checker.category,
            "default_enabled": checker.default_enabled,
            "description": desc,
        })

    # Sort by check_id
    entries.sort(key=lambda e: e["id"])

    if fmt == "json":
        print(json_mod.dumps(entries, indent=2))
        return 0

    # Text format
    if not entries:
        print("No checks found.")
        return 0

    # Determine column widths
    headers = ("ID", "Title", "Severity", "Category", "Enabled", "Description")
    rows = []
    for e in entries:
        rows.append((
            e["id"],
            e["title"],
            e["severity"],
            e["category"],
            "yes" if e["default_enabled"] else "no",
            e["description"],
        ))

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Print header
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))

    return 0


def _cmd_scan(
    repo_path: str,
    config_path: str | None,
    fmt: str,
    output: str | None,
    *,
    fail_under: int | None = None,
    strict: bool = False,
    verbose: bool = False,
    github_step_summary: str | None = None,
    max_annotations: int = 50,
    fail_on: str | None = None,
) -> int:
    """Run the scan command."""
    from oss_paper_ci.config import load_config
    from oss_paper_ci.reporting import generate_json_report, generate_markdown_report, generate_sarif_report
    from oss_paper_ci.scanner import scan as run_scan

    path = Path(repo_path).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        return 2

    config = load_config(config_path=config_path, repo_root=str(path))
    report = run_scan(str(path), config)

    if fmt == "json":
        text = generate_json_report(report, output_path=output)
    elif fmt == "sarif":
        text = generate_sarif_report(report, output_path=output)
    elif fmt == "html":
        from oss_paper_ci.reporting.html_report import generate_html_report
        text = generate_html_report(report)
    elif fmt == "github":
        from oss_paper_ci.reporting.github_annotations import generate_github_annotations, generate_step_summary
        text = generate_github_annotations(report, max_annotations=max_annotations, fail_on=fail_on)
        # Also generate step summary if requested
        if github_step_summary:
            summary_text = generate_step_summary(report)
            Path(github_step_summary).write_text(summary_text, encoding="utf-8")
    else:
        text = generate_markdown_report(report, output_path=output, verbose=verbose)

    if output:
        print(f"Report written to {output}")
    else:
        print(text)

    # --fail-under: exit 1 if score below threshold
    if fail_under is not None and report.summary.score < fail_under:
        return 1

    # --strict: exit 1 if any warnings exist
    if strict and report.summary.counts.get("warning", 0) > 0:
        return 1

    # Exit code based on status
    if report.summary.status == "fail":
        return 2
    elif report.summary.status == "warn":
        return 1
    return 0


def _cmd_graph(
    repo_path: str,
    fmt: str,
    output: str | None,
    *,
    show_orphans: bool = False,
    show_conflicts: bool = False,
) -> int:
    """Run the graph command."""
    from oss_paper_ci.config import load_config
    from oss_paper_ci.graph import build_evidence_graph
    from oss_paper_ci.reporting.graph_report import (
        generate_graph_dot,
        generate_graph_json,
        generate_graph_markdown,
    )

    path = Path(repo_path).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        return 2

    config = load_config(repo_root=str(path))
    graph = build_evidence_graph(str(path), config)

    # --show-orphans: display orphan nodes
    if show_orphans:
        orphans = graph.find_orphan_nodes()
        if orphans:
            print(f"Orphan nodes ({len(orphans)}):")
            for n in orphans:
                print(f"  [{n.type}] {n.path or n.id}")
        else:
            print("No orphan nodes found.")
        print()

    # --show-conflicts: show contract-declared vs inferred edges
    if show_conflicts:
        declared = {(e.source, e.target) for e in graph.edges if e.confidence == "explicit"}
        inferred = {(e.source, e.target) for e in graph.edges if e.confidence == "inferred"}
        conflicts = declared & inferred
        if conflicts:
            print(f"Contract vs inferred conflicts ({len(conflicts)}):")
            for src, tgt in sorted(conflicts):
                src_node = graph.get_node(src)
                tgt_node = graph.get_node(tgt)
                src_label = src_node.path if src_node else src
                tgt_label = tgt_node.path if tgt_node else tgt
                print(f"  {src_label} -> {tgt_label}")
        else:
            print("No contract vs inferred conflicts found.")
        print()

    if fmt == "json":
        text = generate_graph_json(graph, output_path=output)
    elif fmt == "dot":
        text = generate_graph_dot(graph, output_path=output)
    else:
        text = generate_graph_markdown(graph, output_path=output)

    if output:
        print(f"Graph report written to {output}")
    else:
        print(text)

    return 0


def _cmd_baseline(args: argparse.Namespace) -> int:
    """Handle the ``baseline`` subcommand."""
    sub = getattr(args, "baseline_command", None)

    if sub == "create":
        return _cmd_baseline_create(args.path, args.output)

    if sub == "compare":
        return _cmd_baseline_compare(
            args.path,
            args.baseline,
            args.format,
            args.output,
            fail_on_regression=getattr(args, "fail_on_regression", False),
        )

    # No subcommand given -- show help for baseline.
    print("Usage: oss-paper-ci baseline {create|compare} ...", file=sys.stderr)
    return 1


def _cmd_baseline_create(repo_path: str, output: str) -> int:
    """Create a baseline snapshot."""
    from oss_paper_ci.baseline import create_baseline

    path = Path(repo_path).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        return 2

    baseline = create_baseline(str(path))
    baseline.save(output)
    print(f"Baseline created: {output}")
    print(f"  Score:  {baseline.score}")
    print(f"  Status: {baseline.status}")
    print(f"  Checks: {len(baseline.check_results)}")
    return 0


def _cmd_baseline_compare(
    repo_path: str,
    baseline_path: str,
    fmt: str,
    output: str | None,
    *,
    fail_on_regression: bool = False,
) -> int:
    """Compare current scan against a saved baseline."""
    from oss_paper_ci.baseline import Baseline, compare_baseline, create_baseline

    path = Path(repo_path).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        return 2

    try:
        baseline = Baseline.load(baseline_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    current = create_baseline(str(path))
    diff = compare_baseline(current, baseline)

    if fmt == "json":
        import json as json_mod
        text = json_mod.dumps(diff, indent=2)
    else:
        text = _format_baseline_markdown(current, baseline, diff)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Comparison written to {output}")
    else:
        print(text)

    if fail_on_regression and (diff["regressions"] or diff["new_findings"]):
        return 1

    return 0


def _format_baseline_markdown(
    current: "Baseline",
    baseline: "Baseline",
    diff: dict,
) -> str:
    """Render a baseline comparison as a markdown report."""
    lines: list[str] = []
    lines.append("# Baseline Comparison\n")
    lines.append(f"| Metric | Baseline | Current | Delta |")
    lines.append(f"|--------|----------|---------|-------|")
    lines.append(f"| Score | {baseline.score} | {current.score} | {diff['score_delta']:+d} |")
    lines.append(f"| Status | {baseline.status} | {current.status} | |")
    lines.append("")

    if diff["regressions"]:
        lines.append(f"## Regressions ({len(diff['regressions'])})\n")
        for r in diff["regressions"]:
            lines.append(f"- **{r['id']}** ({r.get('title', '')}): {r.get('message', '')}")
        lines.append("")

    if diff["new_findings"]:
        lines.append(f"## Worsened ({len(diff['new_findings'])})\n")
        for f in diff["new_findings"]:
            lines.append(
                f"- **{f['id']}** ({f.get('title', '')}): "
                f"{f['from_status']} -> {f['to_status']}"
            )
        lines.append("")

    if diff["improvements"]:
        lines.append(f"## Improvements ({len(diff['improvements'])})\n")
        for i in diff["improvements"]:
            lines.append(f"- **{i['id']}** ({i.get('title', '')}): now passing")
        lines.append("")

    if diff["resolved_findings"]:
        lines.append(f"## Resolved ({len(diff['resolved_findings'])})\n")
        for r in diff["resolved_findings"]:
            lines.append(
                f"- **{r['id']}** ({r.get('title', '')}): "
                f"{r.get('from_status', '?')} -> {r.get('to_status', '?')}"
            )
        lines.append("")

    if not any([diff["regressions"], diff["new_findings"],
                diff["improvements"], diff["resolved_findings"]]):
        lines.append("No changes detected.\n")

    return "\n".join(lines)


def _cmd_smoke(args: argparse.Namespace) -> int:
    """Handle the ``smoke`` subcommand."""
    from oss_paper_ci.runner import load_smoke_command, run_smoke

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {args.path}", file=sys.stderr)
        return 2

    # Determine the command to run.
    command: str | None = args.smoke_command

    if command is None:
        command = load_smoke_command(
            str(path),
            contract_path=args.contract,
            experiment_id=args.experiment,
        )

    if command is None:
        print(
            "Error: No smoke command found. Provide --command or a "
            "reproducibility.yml with a matching experiment entry.",
            file=sys.stderr,
        )
        return 2

    result = run_smoke(
        repo_path=str(path),
        command=command,
        experiment_id=args.experiment,
        timeout=args.timeout,
        dry_run=args.dry_run,
    )

    if args.format == "json":
        import json as json_mod
        print(json_mod.dumps(result.to_dict(), indent=2))
    else:
        _print_smoke_text(result)

    if result.blocked or result.timed_out or result.exit_code != 0:
        return 1
    return 0


def _print_smoke_text(result: "SmokeResult") -> None:
    """Pretty-print a SmokeResult as text."""
    print(f"Experiment: {result.experiment_id}")
    print(f"Command:    {result.command}")
    if result.blocked:
        print(f"BLOCKED:    {result.block_reason}")
        return
    print(f"Exit code:  {result.exit_code}")
    print(f"Duration:   {result.duration_seconds:.3f}s")
    if result.timed_out:
        print(f"Timed out:  yes ({result.block_reason})")
    if result.stdout_excerpt:
        print(f"\n--- stdout ---\n{result.stdout_excerpt}")
    if result.stderr_excerpt:
        print(f"\n--- stderr ---\n{result.stderr_excerpt}")
    if result.expected_outputs:
        print("\n--- expected outputs ---")
        for o in result.expected_outputs:
            status = "OK" if o["exists"] else "MISSING"
            print(f"  [{status}] {o['path']}")


def _cmd_doctor(repo_path: str, fmt: str) -> int:
    """Diagnose repository and environment."""
    import json as json_mod

    path = Path(repo_path).resolve()
    checks = []

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append({"name": "Python version", "status": "ok", "detail": py_ver})

    # oss-paper-ci version
    checks.append({"name": "oss-paper-ci version", "status": "ok", "detail": __version__})

    # README
    readme = path / "README.md"
    checks.append({"name": "README.md", "status": "ok" if readme.exists() else "missing", "detail": str(readme)})

    # LICENSE
    license_file = path / "LICENSE"
    checks.append({"name": "LICENSE", "status": "ok" if license_file.exists() else "missing", "detail": str(license_file)})

    # Environment files
    env_files = ["requirements.txt", "pyproject.toml", "environment.yml", "Pipfile", "renv.lock", "Project.toml"]
    env_found = [f for f in env_files if (path / f).exists()]
    checks.append({"name": "Environment file", "status": "ok" if env_found else "missing", "detail": ", ".join(env_found) if env_found else "none found"})

    # Reproducibility contract
    contract = path / "reproducibility.yml"
    checks.append({"name": "reproducibility.yml", "status": "ok" if contract.exists() else "missing", "detail": str(contract)})

    # GitHub workflows
    workflows = path / ".github" / "workflows"
    wf_exists = workflows.exists() and any(workflows.glob("*.yml"))
    checks.append({"name": "GitHub workflows", "status": "ok" if wf_exists else "missing", "detail": str(workflows)})

    # Common directories
    for dirname in ["results", "figures", "data", "scripts"]:
        d = path / dirname
        checks.append({"name": f"{dirname}/", "status": "ok" if d.exists() else "missing", "detail": str(d)})

    # Suggestions
    suggestions = []
    if not readme.exists():
        suggestions.append("Add a README.md")
    if not license_file.exists():
        suggestions.append("Add a LICENSE file")
    if not env_found:
        suggestions.append("Add an environment file (requirements.txt, pyproject.toml, etc.)")
    if not contract.exists():
        suggestions.append("Run `oss-paper-ci init --contract` to create reproducibility.yml")
    if not wf_exists:
        suggestions.append("Run `oss-paper-ci init --workflow` to create a GitHub Actions workflow")

    if fmt == "json":
        result = {"checks": checks, "suggestions": suggestions}
        print(json_mod.dumps(result, indent=2))
    else:
        for c in checks:
            status_icon = {"ok": "ok", "missing": "MISSING", "warn": "warn"}.get(c["status"], "?")
            print(f"  [{status_icon}] {c['name']}: {c['detail']}")
        if suggestions:
            print("\nSuggested next steps:")
            for s in suggestions:
                print(f"  - {s}")

    # Return 0 if all ok, 1 if any missing
    if any(c["status"] != "ok" for c in checks):
        return 1
    return 0


def _cmd_comment(input_path: str, output: str | None, kind: str, max_findings: int) -> int:
    """Generate PR comment from scan results."""
    import json as json_mod

    inp = Path(input_path)
    if not inp.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        data = json_mod.loads(inp.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        return 1

    summary = data.get("summary", {})
    score = summary.get("score", 0)
    status = summary.get("status", "unknown")
    counts = summary.get("counts", {})

    # Status badge
    badge_colors = {"pass": "green", "warn": "yellow", "fail": "red"}
    badge = badge_colors.get(status, "lightgrey")

    lines = [
        "## Reproducibility Report",
        "",
        f"![Score](https://img.shields.io/badge/Score-{score}%2F100-{badge})",
        f"![Status](https://img.shields.io/badge/Status-{status}-{badge})",
        "",
        f"**Checks:** {counts.get('pass', 0)} pass, {counts.get('warning', 0)} warn, {counts.get('error', 0)} fail",
        "",
    ]

    checks = data.get("checks", [])
    failing = [c for c in checks if c.get("status") in ("fail", "warn")]

    if failing:
        shown = min(len(failing), max_findings)
        lines.append(f"### Findings ({shown} of {len(failing)})")
        lines.append("")
        lines.append("| ID | Severity | Message |")
        lines.append("|----|----------|---------|")
        for c in failing[:max_findings]:
            sev = c.get("severity", "?")
            cid = c.get("id", "?")
            msg = c.get("message", "")
            # Truncate and escape for table
            if len(msg) > 80:
                msg = msg[:77] + "..."
            msg = msg.replace("|", "\\|").replace("\n", " ")
            icon = "!!" if sev == "error" else "!"
            lines.append(f"| `{cid}` | {icon} {sev} | {msg} |")
        if len(failing) > max_findings:
            lines.append(f"| ... | ... | *{len(failing) - max_findings} more* |")
        lines.append("")

    # Recommendations in collapsible section
    recs = [c for c in checks if c.get("recommendation") and c.get("status") in ("fail", "warn")]
    if recs:
        lines.append("<details>")
        lines.append("<summary>Recommendations</summary>")
        lines.append("")
        for c in recs[:max_findings]:
            cid = c.get("id", "?")
            rec = c.get("recommendation", "")
            lines.append(f"- **{cid}**: {rec}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    if kind == "baseline":
        lines.append("> Baseline comparison mode")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by [oss-paper-ci](https://github.com/Akastella/oss-paper-ci)*")

    text = "\n".join(lines)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Comment written to {output}")
    else:
        print(text)

    return 0
