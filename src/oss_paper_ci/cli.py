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
    scan_parser.add_argument("--profile", dest="profile", help="Policy profile: lenient, default, strict, publication.")
    scan_parser.add_argument("--format", choices=["json", "markdown", "sarif", "html", "github"], default="markdown", help="Output format.")
    scan_parser.add_argument("--output", "-o", help="Write report to file instead of stdout.")
    scan_parser.add_argument("--fail-under", type=int, dest="fail_under", help="Exit with code 1 if score is below this threshold.")
    scan_parser.add_argument("--strict", action="store_true", help="Exit with code 1 if any warnings exist.")
    scan_parser.add_argument("--verbose", action="store_true", help="Show all check details with evidence in markdown report.")
    scan_parser.add_argument("--github-step-summary", dest="github_step_summary", help="Write Markdown summary to file (for $GITHUB_STEP_SUMMARY).")
    scan_parser.add_argument("--max-annotations", type=int, dest="max_annotations", default=50, help="Max annotations for github format (default: 50).")
    scan_parser.add_argument("--fail-on", dest="fail_on", help="Fail on severity level (e.g., major, error).")
    scan_parser.add_argument("--rules", dest="rules_path", help="Path to rule pack manifest YAML.")

    # init command
    init_parser = subparsers.add_parser("init", help="Generate a default config or contract file.")
    init_parser.add_argument("--contract", action="store_true", help="Generate reproducibility.yml template")
    init_parser.add_argument("--profile", dest="profile", help="Policy profile for generated config.")
    init_parser.add_argument("--template", choices=["ml", "simulation", "data-science", "default"], default="default")
    init_parser.add_argument("--output", "-o", help="Output file path")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing file.")
    init_parser.add_argument("--dry-run", action="store_true", help="Print config to stdout instead of writing.")

    # explain command — now supports "policy <name>" or a check ID
    explain_parser = subparsers.add_parser("explain", help="Explain a check ID or policy profile.")
    explain_parser.add_argument("target", help="Check ID (e.g., ENV001) or 'policy <name>'.")
    explain_parser.add_argument("extra", nargs="?", default=None, help="Profile name when target is 'policy'.")

    # list-checks command
    list_checks_parser = subparsers.add_parser("list-checks", help="List all available checks.")
    list_checks_parser.add_argument("--category", help="Filter by category (e.g., metadata, environment).")
    list_checks_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

    # config command group
    config_parser = subparsers.add_parser("config", help="Configuration management.")
    config_sub = config_parser.add_subparsers(dest="config_command")

    # config validate
    cv = config_sub.add_parser("validate", help="Validate a config file.")
    cv.add_argument("--config", dest="config_path", help="Path to config file.")

    # config init
    ci = config_sub.add_parser("init", help="Generate a default config file.")
    ci.add_argument("--profile", dest="profile", default="default", help="Policy profile.")
    ci.add_argument("--output", "-o", help="Output file path.")
    ci.add_argument("--force", action="store_true", help="Overwrite existing file.")
    ci.add_argument("--dry-run", action="store_true", help="Print to stdout.")

    # config explain
    ce = config_sub.add_parser("explain", help="Show the resolved configuration.")
    ce.add_argument("--config", dest="config_path", help="Path to config file.")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Compare two scan reports.")
    diff_parser.add_argument("--old", required=True, help="Path to old report JSON.")
    diff_parser.add_argument("--new", dest="new_report", required=True, help="Path to new report JSON.")
    diff_parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    diff_parser.add_argument("--output", "-o", help="Write output to file.")

    # rules command group
    rules_parser = subparsers.add_parser("rules", help="Rule pack management.")
    rules_sub = rules_parser.add_subparsers(dest="rules_command")

    # rules validate
    rv = rules_sub.add_parser("validate", help="Validate a rule pack manifest.")
    rv.add_argument("--rules", required=True, help="Path to rule pack YAML.")

    # rules list
    rl = rules_sub.add_parser("list", help="List rules in a rule pack.")
    rl.add_argument("--rules", required=True, help="Path to rule pack YAML.")
    rl.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

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

    # workspace command group
    workspace_parser = subparsers.add_parser("workspace", help="Workspace management.")
    workspace_sub = workspace_parser.add_subparsers(dest="workspace_command")

    # workspace validate
    wv = workspace_sub.add_parser("validate", help="Validate a workspace file.")
    wv.add_argument("--workspace", required=True, help="Path to workspace YAML file.")

    # workspace list
    wl = workspace_sub.add_parser("list", help="List projects in a workspace.")
    wl.add_argument("--workspace", required=True, help="Path to workspace YAML file.")
    wl.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

    # batch command group
    batch_parser = subparsers.add_parser("batch", help="Batch scanning.")
    batch_sub = batch_parser.add_subparsers(dest="batch_command")

    # batch scan
    bs = batch_sub.add_parser("scan", help="Scan all projects in a workspace.")
    bs.add_argument("--workspace", required=True, help="Path to workspace YAML file.")
    bs.add_argument("--format", choices=["json", "markdown", "html"], default="markdown", help="Output format.")
    bs.add_argument("--output", "-o", help="Write report to file.")
    bs.add_argument("--jobs", type=int, default=1, help="Parallel workers (default: 1).")
    bs.add_argument("--cache", action="store_true", help="Enable incremental cache.")

    # batch diff
    bd = batch_sub.add_parser("diff", help="Compare two batch reports.")
    bd.add_argument("--old", required=True, help="Path to old batch JSON.")
    bd.add_argument("--new", dest="new_report", required=True, help="Path to new batch JSON.")
    bd.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    bd.add_argument("--output", "-o", help="Write output to file.")

    # cache command group
    cache_parser = subparsers.add_parser("cache", help="Cache management.")
    cache_sub = cache_parser.add_subparsers(dest="cache_command")

    # cache clean
    cc = cache_sub.add_parser("clean", help="Remove all cached results.")
    cc.add_argument("--workspace", required=True, help="Path to workspace YAML file.")

    # cache info
    ci_cache = cache_sub.add_parser("info", help="Show cache statistics.")
    ci_cache.add_argument("--workspace", required=True, help="Path to workspace YAML file.")

    # reproduce command
    reproduce_parser = subparsers.add_parser("reproduce", help="Attempt to reproduce a paper repository.")
    reproduce_parser.add_argument("url", help="GitHub URL, local path, or paper URL.")
    reproduce_parser.add_argument("--repo", dest="repo_override", help="Explicit repository URL (for paper URLs).")
    reproduce_parser.add_argument("--dry-run", action="store_true", default=True, help="Show what would happen without executing (default).")
    reproduce_parser.add_argument("--execute", action="store_true", help="Actually run commands (required for execution).")
    reproduce_parser.add_argument("--install", action="store_true", help="Install dependencies into isolated venv.")
    reproduce_parser.add_argument("--no-install", action="store_true", help="Skip dependency installation.")
    reproduce_parser.add_argument("--command", dest="reproduce_command", help="Override the reproduction command.")
    reproduce_parser.add_argument("--workdir", help="Use a specific working directory.")
    reproduce_parser.add_argument("--keep-workdir", action="store_true", help="Preserve working directory after run.")
    reproduce_parser.add_argument("--timeout", type=int, default=300, help="Per-command timeout in seconds (default: 300).")
    reproduce_parser.add_argument("--format", choices=["markdown", "json", "html"], default="markdown", help="Output format (default: markdown).")
    reproduce_parser.add_argument("--output", "-o", help="Write report to file instead of stdout.")
    reproduce_parser.add_argument("--capsule", dest="capsule_path", help="Generate a reproduction capsule zip at this path.")
    reproduce_parser.add_argument("--capsule-include-artifacts", action="store_true", help="Include generated artifacts in capsule.")
    reproduce_parser.add_argument("--capsule-max-artifact-mb", type=float, default=10.0, help="Max artifact size in MB (default: 10).")

    # capsule command group
    capsule_parser = subparsers.add_parser("capsule", help="Capsule management.")
    capsule_sub = capsule_parser.add_subparsers(dest="capsule_command")

    # capsule verify
    cv = capsule_sub.add_parser("verify", help="Verify capsule integrity.")
    cv.add_argument("capsule", help="Path to capsule zip file.")
    cv.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Output format.")
    cv.add_argument("--output", "-o", help="Write output to file.")

    # capsule inspect
    ci = capsule_sub.add_parser("inspect", help="Inspect capsule contents.")
    ci.add_argument("capsule", help="Path to capsule zip file.")
    ci.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    ci.add_argument("--output", "-o", help="Write output to file.")

    # capsule diff
    cd = capsule_sub.add_parser("diff", help="Compare two capsules.")
    cd.add_argument("old_capsule", help="Path to old capsule zip.")
    cd.add_argument("new_capsule", help="Path to new capsule zip.")
    cd.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    cd.add_argument("--output", "-o", help="Write output to file.")

    # guide command
    guide_parser = subparsers.add_parser("guide", help="Get guided help for using oss-paper-ci.")
    guide_parser.add_argument("--role", choices=["author", "reviewer", "maintainer"], help="Your role.")
    guide_parser.add_argument("--topic", choices=["scan", "reproduce", "capsule"], help="Topic to learn about.")
    guide_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    guide_parser.add_argument("--output", "-o", help="Write output to file.")

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

    if args.command == "guide":
        return _cmd_guide(args)

    if args.command == "reproduce":
        return _cmd_reproduce(args)

    if args.command == "capsule":
        return _cmd_capsule(args)

    if args.command == "workspace":
        return _cmd_workspace(args)

    if args.command == "batch":
        return _cmd_batch(args)

    if args.command == "cache":
        return _cmd_cache(args)

    if args.command == "init":
        return _cmd_init(
            contract=getattr(args, "contract", False),
            profile=getattr(args, "profile", "default"),
            template=getattr(args, "template", "default"),
            output=getattr(args, "output", None),
            force=getattr(args, "force", False),
            dry_run=getattr(args, "dry_run", False),
        )

    if args.command == "validate-contract":
        return _cmd_validate_contract(args.path, getattr(args, "contract", None))

    if args.command == "explain":
        return _cmd_explain(args.target, getattr(args, "extra", None))

    if args.command == "list-checks":
        return _cmd_list_checks(args.category, args.format)

    if args.command == "config":
        return _cmd_config(args)

    if args.command == "diff":
        return _cmd_diff(
            args.old, args.new_report, args.format,
            output=getattr(args, "output", None),
        )

    if args.command == "rules":
        return _cmd_rules(args)

    if args.command == "scan":
        return _cmd_scan(
            args.path, args.config_path, args.format, args.output,
            profile=getattr(args, "profile", None),
            rules_path=getattr(args, "rules_path", None),
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


# ── Workspace command ─────────────────────────────────────────────────────────

def _cmd_workspace(args: argparse.Namespace) -> int:
    """Handle workspace subcommand group."""
    sub = getattr(args, "workspace_command", None)

    if sub == "validate":
        return _cmd_workspace_validate(getattr(args, "workspace", None))

    if sub == "list":
        return _cmd_workspace_list(
            getattr(args, "workspace", None),
            getattr(args, "format", "text"),
        )

    print("Usage: oss-paper-ci workspace {validate|list} --workspace PATH", file=sys.stderr)
    return 1


def _cmd_workspace_validate(workspace_path: str | None) -> int:
    """Validate a workspace file."""
    if not workspace_path:
        print("Error: --workspace is required.", file=sys.stderr)
        return 1

    from oss_paper_ci.workspace import validate_workspace

    result = validate_workspace(workspace_path)
    print(result.format_text())
    return 0 if result.valid else 1


def _cmd_workspace_list(workspace_path: str | None, fmt: str) -> int:
    """List projects in a workspace."""
    import json as json_mod

    if not workspace_path:
        print("Error: --workspace is required.", file=sys.stderr)
        return 1

    from oss_paper_ci.workspace import load_workspace, list_workspace_projects

    try:
        workspace = load_workspace(workspace_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    projects = list_workspace_projects(workspace)

    if fmt == "json":
        print(json_mod.dumps(projects, indent=2))
        return 0

    if not projects:
        print("No projects in workspace.")
        return 0

    # Text table
    print(f"Workspace: {workspace.name or '(unnamed)'}")
    print(f"Projects: {len(projects)}")
    print()
    print(f"{'ID':<20} {'Path':<40} {'Profile':<12} {'Allow Failure'}")
    print("-" * 84)
    for p in projects:
        print(f"{p['id']:<20} {p['path']:<40} {p['profile']:<12} {p['allow_failure']}")

    return 0


# ── Batch command ─────────────────────────────────────────────────────────────

def _cmd_batch(args: argparse.Namespace) -> int:
    """Handle batch subcommand group."""
    sub = getattr(args, "batch_command", None)

    if sub == "scan":
        return _cmd_batch_scan(
            workspace_path=getattr(args, "workspace", None),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
            jobs=getattr(args, "jobs", 1),
            use_cache=getattr(args, "cache", False),
        )

    if sub == "diff":
        return _cmd_batch_diff(
            old_path=getattr(args, "old", None),
            new_path=getattr(args, "new_report", None),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    print("Usage: oss-paper-ci batch {scan|diff} ...", file=sys.stderr)
    return 1


def _cmd_batch_scan(
    *,
    workspace_path: str | None,
    fmt: str,
    output: str | None,
    jobs: int,
    use_cache: bool,
) -> int:
    """Run batch scan over workspace projects."""
    if not workspace_path:
        print("Error: --workspace is required.", file=sys.stderr)
        return 1

    if jobs < 1:
        print("Error: --jobs must be >= 1.", file=sys.stderr)
        return 1

    from pathlib import Path

    from oss_paper_ci.batch import run_batch_scan
    from oss_paper_ci.reporting.aggregate_report import (
        generate_aggregate_html_report,
        generate_aggregate_json_report,
        generate_aggregate_markdown_report,
    )
    from oss_paper_ci.workspace import load_workspace

    ws_path = Path(workspace_path)
    if not ws_path.exists():
        print(f"Error: workspace file not found: {workspace_path}", file=sys.stderr)
        return 2

    try:
        workspace = load_workspace(workspace_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    batch_result = run_batch_scan(
        workspace, ws_path, jobs=jobs, use_cache=use_cache
    )
    result_dict = batch_result.to_dict()

    if fmt == "json":
        text = generate_aggregate_json_report(result_dict, output_path=output)
    elif fmt == "html":
        text = generate_aggregate_html_report(result_dict)
    else:
        text = generate_aggregate_markdown_report(result_dict)

    if output:
        from pathlib import Path as P
        P(output).write_text(text, encoding="utf-8")
        print(f"Report written to {output}")
    else:
        print(text)

    # Exit code based on batch status
    summary = batch_result.summary
    if summary.get("fail", 0) > 0 or summary.get("error", 0) > 0:
        return 2
    if summary.get("warn", 0) > 0:
        return 1
    return 0


def _cmd_batch_diff(
    *,
    old_path: str | None,
    new_path: str | None,
    fmt: str,
    output: str | None,
) -> int:
    """Compare two batch scan reports."""
    import json as json_mod
    from pathlib import Path

    if not old_path or not new_path:
        print("Error: --old and --new are required.", file=sys.stderr)
        return 1

    old_file = Path(old_path)
    new_file = Path(new_path)

    if not old_file.exists():
        print(f"Error: old report not found: {old_path}", file=sys.stderr)
        return 2
    if not new_file.exists():
        print(f"Error: new report not found: {new_path}", file=sys.stderr)
        return 2

    try:
        old_data = json_mod.loads(old_file.read_text(encoding="utf-8"))
        new_data = json_mod.loads(new_file.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error reading reports: {exc}", file=sys.stderr)
        return 2

    from oss_paper_ci.batch import compute_batch_diff, format_batch_diff_markdown

    diff = compute_batch_diff(old_data, new_data)

    if fmt == "json":
        text = json_mod.dumps(diff, indent=2, ensure_ascii=False)
    else:
        text = format_batch_diff_markdown(diff)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Diff written to {output}")
    else:
        print(text)

    return 0


# ── Cache command ─────────────────────────────────────────────────────────────

def _cmd_cache(args: argparse.Namespace) -> int:
    """Handle cache subcommand group."""
    sub = getattr(args, "cache_command", None)

    if sub == "clean":
        return _cmd_cache_clean(getattr(args, "workspace", None))

    if sub == "info":
        return _cmd_cache_info(getattr(args, "workspace", None))

    print("Usage: oss-paper-ci cache {clean|info} --workspace PATH", file=sys.stderr)
    return 1


def _cmd_cache_clean(workspace_path: str | None) -> int:
    """Clean cache for a workspace."""
    if not workspace_path:
        print("Error: --workspace is required.", file=sys.stderr)
        return 1

    from pathlib import Path

    from oss_paper_ci.cache import clean_cache

    ws_path = Path(workspace_path)
    if not ws_path.exists():
        print(f"Error: workspace file not found: {workspace_path}", file=sys.stderr)
        return 2

    count = clean_cache(ws_path.parent.resolve())
    print(f"Removed {count} cache entries.")
    return 0


def _cmd_cache_info(workspace_path: str | None) -> int:
    """Show cache information."""
    import json as json_mod

    if not workspace_path:
        print("Error: --workspace is required.", file=sys.stderr)
        return 1

    from pathlib import Path

    from oss_paper_ci.cache import get_cache_info

    ws_path = Path(workspace_path)
    if not ws_path.exists():
        print(f"Error: workspace file not found: {workspace_path}", file=sys.stderr)
        return 2

    info = get_cache_info(ws_path.parent.resolve())
    print(json_mod.dumps(info, indent=2))
    return 0


# ── Init command ──────────────────────────────────────────────────────────────

def _cmd_init(
    *,
    contract: bool = False,
    profile: str = "default",
    template: str = "default",
    output: str | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Generate default config file or contract template."""
    if contract:
        from oss_paper_ci.contract import generate_contract_template

        target = Path(output or "reproducibility.yml")
        if dry_run:
            print(generate_contract_template(template))
            return 0

        if target.exists() and not force:
            print(f"Contract file already exists: {target}", file=sys.stderr)
            print("Use --force to overwrite.", file=sys.stderr)
            return 1

        target.write_text(generate_contract_template(template), encoding="utf-8")
        print(f"Created {target}")
        return 0

    from oss_paper_ci.config import generate_default_config

    target = Path(output or ".oss-paper-ci.yml")
    if dry_run:
        print(generate_default_config(profile=profile))
        return 0

    if target.exists() and not force:
        print(f"Config file already exists: {target}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    target.write_text(generate_default_config(profile=profile), encoding="utf-8")
    print(f"Created {target}")
    return 0


# ── Validate contract ────────────────────────────────────────────────────────

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


# ── Explain command ──────────────────────────────────────────────────────────

def _cmd_explain(target: str, extra: str | None) -> int:
    """Explain a check ID or policy profile."""
    # Handle "explain policy <name>"
    if target.lower() == "policy":
        if extra is None:
            print("Usage: oss-paper-ci explain policy <name>", file=sys.stderr)
            print("Available profiles: lenient, default, strict, publication", file=sys.stderr)
            return 1
        from oss_paper_ci.policy import explain_profile
        try:
            print(explain_profile(extra))
            return 0
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    # Handle check ID
    from oss_paper_ci.checks.registry import get_checker_by_id, get_all_checkers

    check_id_upper = target.upper()
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
    print(f"Unknown check ID: {target}", file=sys.stderr)
    print(f"Available check IDs: {', '.join(all_ids)}", file=sys.stderr)
    return 1


# ── List checks ──────────────────────────────────────────────────────────────

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


# ── Config command group ─────────────────────────────────────────────────────

def _cmd_config(args: argparse.Namespace) -> int:
    """Handle config subcommand group."""
    sub = getattr(args, "config_command", None)

    if sub == "validate":
        return _cmd_config_validate(getattr(args, "config_path", None))

    if sub == "init":
        return _cmd_config_init(
            profile=getattr(args, "profile", "default"),
            output=getattr(args, "output", None),
            force=getattr(args, "force", False),
            dry_run=getattr(args, "dry_run", False),
        )

    if sub == "explain":
        return _cmd_config_explain(getattr(args, "config_path", None))

    print("Usage: oss-paper-ci config {validate|init|explain}", file=sys.stderr)
    return 1


def _cmd_config_validate(config_path: str | None) -> int:
    """Validate a config file."""
    from oss_paper_ci.schema import validate_config_file

    # Find the config file
    if config_path:
        path = Path(config_path)
    else:
        # Search default locations
        path = None
        for name in ("oss-paper-ci.yml", "oss-paper-ci.yaml", ".oss-paper-ci.yml"):
            candidate = Path(name)
            if candidate.exists():
                path = candidate
                break

    if path is None:
        print("No config file found.", file=sys.stderr)
        print("Run `oss-paper-ci config init` to create one.", file=sys.stderr)
        return 1

    result = validate_config_file(path)
    print(result.format_text())
    return 0 if result.valid else 1


def _cmd_config_init(
    *,
    profile: str = "default",
    output: str | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Generate a default config file."""
    from oss_paper_ci.config import generate_default_config

    content = generate_default_config(profile=profile)

    if dry_run:
        print(content)
        return 0

    target = Path(output or ".oss-paper-ci.yml")
    if target.exists() and not force:
        print(f"Config file already exists: {target}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    target.write_text(content, encoding="utf-8")
    print(f"Created {target}")
    return 0


def _cmd_config_explain(config_path: str | None) -> int:
    """Show the resolved configuration."""
    import json as json_mod

    from oss_paper_ci.config import load_config
    from oss_paper_ci.policy import get_profile

    config = load_config(config_path=config_path)

    try:
        profile = get_profile(config.profile)
    except ValueError:
        profile = get_profile("default")

    # Build resolved config summary
    resolved = {
        "config_path": config.config_path or "(defaults)",
        "profile": profile.name,
        "profile_description": profile.description,
        "thresholds": {
            "pass_score": profile.pass_score,
            "warn_score": profile.warn_score,
            "fail_under": profile.fail_under,
        },
        "checks": {
            "disabled": config.checks.disabled,
            "severity_overrides": config.checks.severity_overrides,
        },
        "ignore_paths": config.ignore.paths,
        "output_format": config.output.default_format,
    }

    print(json_mod.dumps(resolved, indent=2))
    return 0


# ── Diff command ─────────────────────────────────────────────────────────────

def _cmd_diff(
    old_path: str,
    new_path: str,
    fmt: str,
    output: str | None = None,
) -> int:
    """Compare two scan report JSON files."""
    import json as json_mod

    old_file = Path(old_path)
    new_file = Path(new_path)

    if not old_file.exists():
        print(f"Error: old report not found: {old_path}", file=sys.stderr)
        return 2
    if not new_file.exists():
        print(f"Error: new report not found: {new_path}", file=sys.stderr)
        return 2

    try:
        old_data = json_mod.loads(old_file.read_text(encoding="utf-8"))
        new_data = json_mod.loads(new_file.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error reading reports: {exc}", file=sys.stderr)
        return 2

    diff = _compute_diff(old_data, new_data)

    if fmt == "json":
        text = json_mod.dumps(diff, indent=2)
    else:
        text = _format_diff_markdown(diff, old_data, new_data)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Diff written to {output}")
    else:
        print(text)

    return 0


def _compute_diff(old_data: dict, new_data: dict) -> dict:
    """Compute diff between two report dicts."""
    old_summary = old_data.get("summary", {})
    new_summary = new_data.get("summary", {})

    old_score = old_summary.get("score", 0)
    new_score = new_summary.get("score", 0)
    old_status = old_summary.get("status", "unknown")
    new_status = new_summary.get("status", "unknown")

    # Index checks by ID
    old_checks = {c["id"]: c for c in old_data.get("checks", [])}
    new_checks = {c["id"]: c for c in new_data.get("checks", [])}

    all_ids = sorted(set(old_checks) | set(new_checks))

    new_findings = []
    resolved_findings = []
    severity_worsened = []
    severity_improved = []
    changed_categories = []

    for cid in all_ids:
        old_c = old_checks.get(cid)
        new_c = new_checks.get(cid)

        if old_c is None and new_c is not None:
            if new_c.get("status") in ("fail", "warn"):
                new_findings.append({
                    "id": cid,
                    "title": new_c.get("title", ""),
                    "severity": new_c.get("severity", ""),
                    "status": new_c.get("status", ""),
                    "message": new_c.get("message", ""),
                })
        elif old_c is not None and new_c is None:
            resolved_findings.append({
                "id": cid,
                "title": old_c.get("title", ""),
                "from_status": old_c.get("status", ""),
            })
        elif old_c is not None and new_c is not None:
            old_stat = old_c.get("status", "")
            new_stat = new_c.get("status", "")
            old_sev = old_c.get("severity", "")
            new_sev = new_c.get("severity", "")

            # Status changes
            _FAIL_ORDER = {"pass": 0, "warn": 1, "fail": 2, "unknown": 0}
            if _FAIL_ORDER.get(new_stat, 0) > _FAIL_ORDER.get(old_stat, 0):
                severity_worsened.append({
                    "id": cid,
                    "title": new_c.get("title", ""),
                    "from_status": old_stat,
                    "to_status": new_stat,
                })
            elif _FAIL_ORDER.get(new_stat, 0) < _FAIL_ORDER.get(old_stat, 0):
                severity_improved.append({
                    "id": cid,
                    "title": new_c.get("title", ""),
                    "from_status": old_stat,
                    "to_status": new_stat,
                })

    # Category-level changes
    old_cats: dict[str, dict] = {}
    new_cats: dict[str, dict] = {}
    for cid, c in old_checks.items():
        cat = cid[:3] if len(cid) >= 3 else cid
        if cat not in old_cats:
            old_cats[cat] = {"pass": 0, "warn": 0, "fail": 0}
        old_cats[cat][c.get("status", "unknown")] = old_cats[cat].get(c.get("status", "unknown"), 0) + 1
    for cid, c in new_checks.items():
        cat = cid[:3] if len(cid) >= 3 else cid
        if cat not in new_cats:
            new_cats[cat] = {"pass": 0, "warn": 0, "fail": 0}
        new_cats[cat][c.get("status", "unknown")] = new_cats[cat].get(c.get("status", "unknown"), 0) + 1

    for cat in sorted(set(old_cats) | set(new_cats)):
        if old_cats.get(cat) != new_cats.get(cat):
            changed_categories.append({
                "category": cat,
                "old": old_cats.get(cat, {}),
                "new": new_cats.get(cat, {}),
            })

    # Recommendation summary
    rec_parts = []
    if new_findings:
        rec_parts.append(f"{len(new_findings)} new finding(s)")
    if resolved_findings:
        rec_parts.append(f"{len(resolved_findings)} resolved")
    if severity_worsened:
        rec_parts.append(f"{len(severity_worsened)} worsened")
    if severity_improved:
        rec_parts.append(f"{len(severity_improved)} improved")
    if not rec_parts:
        recommendation = "No significant changes detected."
    else:
        recommendation = "Changes: " + ", ".join(rec_parts) + "."

    return {
        "old_report": old_data.get("version", "unknown"),
        "new_report": new_data.get("version", "unknown"),
        "score_delta": new_score - old_score,
        "old_score": old_score,
        "new_score": new_score,
        "old_status": old_status,
        "new_status": new_status,
        "status_changed": old_status != new_status,
        "new_findings": new_findings,
        "resolved_findings": resolved_findings,
        "severity_worsened": severity_worsened,
        "severity_improved": severity_improved,
        "changed_categories": changed_categories,
        "recommendation": recommendation,
    }


def _format_diff_markdown(diff: dict, old_data: dict, new_data: dict) -> str:
    """Format diff as markdown."""
    lines = ["# Report Diff\n"]

    # Score comparison
    lines.append("## Score Comparison\n")
    lines.append("| Metric | Old | New | Delta |")
    lines.append("|--------|-----|-----|-------|")
    lines.append(
        f"| Score | {diff['old_score']} | {diff['new_score']} | "
        f"{diff['score_delta']:+d} |"
    )
    lines.append(
        f"| Status | {diff['old_status']} | {diff['new_status']} | "
        f"{'changed' if diff['status_changed'] else 'same'} |"
    )
    lines.append("")

    # Policy info
    old_policy = old_data.get("policy", {})
    new_policy = new_data.get("policy", {})
    if old_policy or new_policy:
        lines.append("## Policy\n")
        lines.append(f"- Old profile: {old_policy.get('profile', 'n/a')}")
        lines.append(f"- New profile: {new_policy.get('profile', 'n/a')}")
        lines.append("")

    # New findings
    if diff["new_findings"]:
        lines.append(f"## New Findings ({len(diff['new_findings'])})\n")
        for f in diff["new_findings"]:
            lines.append(
                f"- **{f['id']}** ({f.get('title', '')}): "
                f"{f.get('severity', '?')} / {f.get('status', '?')} — "
                f"{f.get('message', '')}"
            )
        lines.append("")

    # Resolved findings
    if diff["resolved_findings"]:
        lines.append(f"## Resolved Findings ({len(diff['resolved_findings'])})\n")
        for f in diff["resolved_findings"]:
            lines.append(
                f"- **{f['id']}** ({f.get('title', '')}): "
                f"was {f.get('from_status', '?')}"
            )
        lines.append("")

    # Worsened
    if diff["severity_worsened"]:
        lines.append(f"## Worsened ({len(diff['severity_worsened'])})\n")
        for f in diff["severity_worsened"]:
            lines.append(
                f"- **{f['id']}** ({f.get('title', '')}): "
                f"{f['from_status']} → {f['to_status']}"
            )
        lines.append("")

    # Improved
    if diff["severity_improved"]:
        lines.append(f"## Improved ({len(diff['severity_improved'])})\n")
        for f in diff["severity_improved"]:
            lines.append(
                f"- **{f['id']}** ({f.get('title', '')}): "
                f"{f['from_status']} → {f['to_status']}"
            )
        lines.append("")

    # Changed categories
    if diff["changed_categories"]:
        lines.append(f"## Changed Categories ({len(diff['changed_categories'])})\n")
        for cat in diff["changed_categories"]:
            lines.append(f"- **{cat['category']}**: {cat['old']} → {cat['new']}")
        lines.append("")

    # Recommendation
    lines.append("## Summary\n")
    lines.append(diff["recommendation"])
    lines.append("")

    return "\n".join(lines)


# ── Rules command group ──────────────────────────────────────────────────────

def _cmd_rules(args: argparse.Namespace) -> int:
    """Handle rules subcommand group."""
    sub = getattr(args, "rules_command", None)

    if sub == "validate":
        return _cmd_rules_validate(args.rules)

    if sub == "list":
        return _cmd_rules_list(args.rules, getattr(args, "format", "text"))

    print("Usage: oss-paper-ci rules {validate|list} --rules PATH", file=sys.stderr)
    return 1


def _cmd_rules_validate(rules_path: str) -> int:
    """Validate a rule pack manifest."""
    from oss_paper_ci.checks.manifest import validate_manifest

    result = validate_manifest(rules_path)
    print(result.format_text())
    return 0 if result.valid else 1


def _cmd_rules_list(rules_path: str, fmt: str) -> int:
    """List rules in a rule pack."""
    import json as json_mod

    from oss_paper_ci.checks.manifest import parse_manifest

    try:
        manifest = parse_manifest(rules_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if fmt == "json":
        print(json_mod.dumps(manifest.to_dict(), indent=2))
        return 0

    # Text format
    print(f"Rule Pack: {manifest.name}")
    if manifest.description:
        print(f"Description: {manifest.description}")
    print(f"Rules: {len(manifest.rules)}")
    print()

    if not manifest.rules:
        print("No rules defined.")
        return 0

    # Table
    print(f"{'ID':<15} {'Name':<30} {'Severity':<12} {'Type':<20}")
    print("-" * 77)
    for rule in manifest.rules:
        print(f"{rule.id:<15} {rule.name:<30} {rule.severity:<12} {rule.rule_type:<20}")

    return 0


# ── Scan command ─────────────────────────────────────────────────────────────

def _cmd_scan(
    repo_path: str,
    config_path: str | None,
    fmt: str,
    output: str | None,
    *,
    profile: str | None = None,
    rules_path: str | None = None,
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

    # CLI --profile overrides config file profile
    if profile is not None:
        config.profile = profile

    # CLI --rules adds rule pack to config
    if rules_path is not None:
        config.rule_packs.append(rules_path)

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


# ── Graph command ────────────────────────────────────────────────────────────

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


# ── Baseline command ─────────────────────────────────────────────────────────

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


# ── Smoke command ────────────────────────────────────────────────────────────

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


# ── Doctor command ───────────────────────────────────────────────────────────

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


# ── Reproduce command ────────────────────────────────────────────────────────

def _cmd_reproduce(args: argparse.Namespace) -> int:
    """Handle the reproduce subcommand."""
    from oss_paper_ci.reproduce import run_reproduce
    from oss_paper_ci.reporting.reproduce_report import (
        generate_reproduce_html_report,
        generate_reproduce_json_report,
        generate_reproduce_markdown_report,
    )

    url = args.url
    if not url:
        print("Error: URL or path is required.", file=sys.stderr)
        return 1

    # --execute enables execution; without it, dry-run is forced
    execute = getattr(args, "execute", False)
    dry_run = not execute

    # --no-install overrides --install
    install = getattr(args, "install", False)
    if getattr(args, "no_install", False):
        install = False

    # For capsule generation, keep workdir so artifacts can be collected
    capsule_path = getattr(args, "capsule_path", None)
    keep_workdir = getattr(args, "keep_workdir", False) or bool(capsule_path)

    result = run_reproduce(
        url=url,
        repo_override=getattr(args, "repo_override", None),
        dry_run=dry_run,
        execute=execute,
        install=install,
        command=getattr(args, "reproduce_command", None),
        workdir=getattr(args, "workdir", None),
        timeout=getattr(args, "timeout", 300),
        keep_workdir=keep_workdir,
    )

    # Generate report
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    if fmt == "json":
        text = generate_reproduce_json_report(result, output_path=output)
    elif fmt == "html":
        text = generate_reproduce_html_report(result, output_path=output)
    else:
        text = generate_reproduce_markdown_report(result, output_path=output)

    if output:
        print(f"Report written to {output}")
    else:
        print(text)

    # Generate capsule if requested
    if capsule_path:
        from oss_paper_ci.capsule import build_capsule
        try:
            include_artifacts = getattr(args, "capsule_include_artifacts", False) or True
            max_mb = getattr(args, "capsule_max_artifact_mb", 10.0)
            build_capsule(
                result, capsule_path,
                include_artifacts=include_artifacts,
                max_artifact_mb=max_mb,
            )
            print(f"Capsule written to {capsule_path}")
        except Exception as exc:
            print(f"Error building capsule: {exc}", file=sys.stderr)
            return 2

    # Exit code
    if result.error:
        return 2
    if not result.ok:
        return 1
    return 0


# ── Capsule command ──────────────────────────────────────────────────────────

def _cmd_capsule(args: argparse.Namespace) -> int:
    """Handle the capsule subcommand group."""
    sub = getattr(args, "capsule_command", None)

    if sub == "verify":
        return _cmd_capsule_verify(
            capsule_path=getattr(args, "capsule", None),
            fmt=getattr(args, "format", "text"),
            output=getattr(args, "output", None),
        )

    if sub == "inspect":
        return _cmd_capsule_inspect(
            capsule_path=getattr(args, "capsule", None),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    if sub == "diff":
        return _cmd_capsule_diff(
            old_path=getattr(args, "old_capsule", None),
            new_path=getattr(args, "new_capsule", None),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    print("Usage: oss-paper-ci capsule {verify|inspect|diff} ...", file=sys.stderr)
    return 1


def _cmd_capsule_verify(
    capsule_path: str | None,
    fmt: str,
    output: str | None,
) -> int:
    """Verify a capsule's integrity."""
    import json as json_mod

    if not capsule_path:
        print("Error: capsule path is required.", file=sys.stderr)
        return 1

    from oss_paper_ci.capsule import verify_capsule

    result = verify_capsule(capsule_path)

    if fmt == "json":
        text = json_mod.dumps(result.to_dict(), indent=2)
    elif fmt == "markdown":
        text = result.format_text()
        # Add header for markdown
        text = "# Capsule Verification\n\n" + text + "\n"
    else:
        text = result.format_text()

    if output:
        from pathlib import Path
        Path(output).write_text(text, encoding="utf-8")
        print(f"Verification written to {output}")
    else:
        print(text)

    return 0 if result.ok else 1


def _cmd_capsule_inspect(
    capsule_path: str | None,
    fmt: str,
    output: str | None,
) -> int:
    """Inspect a capsule's contents."""
    import json as json_mod

    if not capsule_path:
        print("Error: capsule path is required.", file=sys.stderr)
        return 1

    from oss_paper_ci.capsule import inspect_capsule

    info = inspect_capsule(capsule_path)

    if "error" in info:
        print(f"Error: {info['error']}", file=sys.stderr)
        return 2

    if fmt == "json":
        text = json_mod.dumps(info, indent=2, ensure_ascii=False)
    else:
        text = _format_capsule_inspect_markdown(info)

    if output:
        from pathlib import Path
        Path(output).write_text(text, encoding="utf-8")
        print(f"Inspection written to {output}")
    else:
        print(text)

    return 0


def _format_capsule_inspect_markdown(info: dict) -> str:
    """Format capsule inspection as markdown."""
    lines = ["# Capsule Inspection\n"]

    lines.append("## Metadata\n")
    lines.append(f"- Schema version: {info.get('schema_version', '?')}")
    lines.append(f"- Capsule type: {info.get('capsule_type', '?')}")
    lines.append(f"- Created by: oss-paper-ci {info.get('oss_paper_ci_version', '?')}")
    lines.append("")

    source = info.get("source", {})
    lines.append("## Source\n")
    lines.append(f"- Input URL: `{source.get('input_url', '?')}`")
    if source.get("repo_url"):
        lines.append(f"- Repository: `{source.get('repo_url')}`")
    if source.get("paper_url"):
        lines.append(f"- Paper URL: `{source.get('paper_url')}`")
    if source.get("commit_sha"):
        lines.append(f"- Commit: `{source.get('commit_sha', '')[:12]}`")
    lines.append(f"- Source type: {source.get('source_type', '?')}")
    lines.append("")

    exec_info = info.get("execution", {})
    lines.append("## Execution\n")
    lines.append(f"- Mode: {exec_info.get('mode', '?')}")
    lines.append(f"- Install: {'yes' if exec_info.get('install') else 'no'}")
    lines.append(f"- Commands attempted: {exec_info.get('commands_attempted', 0)}")
    lines.append(f"- Commands succeeded: {exec_info.get('commands_succeeded', 0)}")
    lines.append(f"- Commands failed: {exec_info.get('commands_failed', 0)}")
    lines.append("")

    scan_score = info.get("scan_score")
    if scan_score is not None:
        lines.append("## Scan\n")
        lines.append(f"- Score: {scan_score}/100")
        lines.append(f"- Status: {info.get('scan_status', '?')}")
        lines.append("")

    lines.append("## Artifacts\n")
    lines.append(f"- Artifact count: {info.get('artifact_count', 0)}")
    lines.append(f"- Total files in capsule: {info.get('file_count', 0)}")
    lines.append("")

    limitations = info.get("limitations", [])
    if limitations:
        lines.append("## Limitations\n")
        for lim in limitations:
            lines.append(f"- {lim}")
        lines.append("")

    return "\n".join(lines)


# ── Guide command ────────────────────────────────────────────────────────────

def _cmd_guide(args: argparse.Namespace) -> int:
    """Handle the guide subcommand."""
    import json as json_mod

    from oss_paper_ci.guidance import format_guide_markdown, get_guide

    role = getattr(args, "role", None)
    topic = getattr(args, "topic", None)
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    guide = get_guide(role=role, topic=topic)

    if "error" in guide:
        print(f"Error: {guide['error']}", file=sys.stderr)
        return 1

    if fmt == "json":
        text = json_mod.dumps(guide, indent=2, ensure_ascii=False)
    else:
        text = format_guide_markdown(guide)

    if output:
        from pathlib import Path
        Path(output).write_text(text, encoding="utf-8")
        print(f"Guide written to {output}")
    else:
        print(text)

    return 0


def _cmd_capsule_diff(
    old_path: str | None,
    new_path: str | None,
    fmt: str,
    output: str | None,
) -> int:
    """Compare two capsules."""
    import json as json_mod

    if not old_path or not new_path:
        print("Error: both old and new capsule paths are required.", file=sys.stderr)
        return 1

    from oss_paper_ci.capsule import diff_capsules, format_diff_markdown

    diff = diff_capsules(old_path, new_path)

    if fmt == "json":
        text = json_mod.dumps(diff, indent=2, ensure_ascii=False)
    else:
        text = format_diff_markdown(diff)

    if output:
        from pathlib import Path
        Path(output).write_text(text, encoding="utf-8")
        print(f"Diff written to {output}")
    else:
        print(text)

    return 0


# ── Comment command ──────────────────────────────────────────────────────────

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

    # Policy info
    policy = data.get("policy", {})
    if policy:
        lines.append(f"**Profile:** {policy.get('profile', 'default')}")
        lines.append("")

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
