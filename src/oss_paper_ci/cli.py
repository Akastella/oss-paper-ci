"""CLI entry point for oss-paper-ci."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from oss_paper_ci import __version__

# Module-level output mode and theme, resolved in main()
from oss_paper_ci.terminal import OutputMode as _OutputMode
from oss_paper_ci.themes import get_theme as _default_theme_fn
_mode = _OutputMode()
_theme = _default_theme_fn()
_debug = False


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
    parser.add_argument("--plain", action="store_true",
                        help="Force plain text output (no color, no animation).")
    parser.add_argument("--no-color", action="store_true", dest="no_color",
                        help="Disable color output.")
    parser.add_argument("--no-animate", action="store_true", dest="no_animate",
                        help="Disable animation (spinners, progress).")
    parser.add_argument("--theme", choices=["classic", "minimal", "contrast"],
                        default="classic", help="Terminal theme (default: classic).")
    parser.add_argument("--debug", action="store_true",
                        help="Show debug information and tracebacks on error.")

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

    # reproduce command group
    reproduce_parser = subparsers.add_parser("reproduce", help="Reproduction orchestrator: plan, run, report, compare, bundle.")
    reproduce_sub = reproduce_parser.add_subparsers(dest="reproduce_command")

    # reproduce plan
    rp = reproduce_sub.add_parser("plan", help="Generate a reproduction plan (never executes code).")
    rp.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    rp.add_argument("--contract", dest="contract_path", help="Path to reproducibility.yml")
    rp.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format (default: markdown).")
    rp.add_argument("--output", "-o", help="Write plan to file instead of stdout.")

    # reproduce run
    rr = reproduce_sub.add_parser("run", help="Execute reproduction commands (requires --execute).")
    rr.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    rr.add_argument("--contract", dest="contract_path", help="Path to reproducibility.yml")
    rr.add_argument("--execute", action="store_true", help="Actually run commands (required for execution).")
    rr.add_argument("--sandbox", choices=["local", "docker"], default="local", help="Sandbox type (default: local).")
    rr.add_argument("--timeout", type=int, help="Override per-command timeout in seconds.")
    rr.add_argument("--output-dir", dest="output_dir", help="Explicit output directory for run results.")
    rr.add_argument("--format", choices=["markdown", "json", "html"], default="markdown", help="Output format (default: markdown).")
    rr.add_argument("--output", "-o", help="Write report to file instead of stdout.")
    rr.add_argument("--fail-on", dest="fail_on", choices=["failed-command", "missing-artifact", "out-of-range"],
                    help="Exit non-zero on specific failure type.")
    # Legacy flags for backward compat
    rr.add_argument("--repo", dest="repo_override", help=argparse.SUPPRESS)
    rr.add_argument("--url", dest="legacy_url", help=argparse.SUPPRESS)
    rr.add_argument("--dry-run", action="store_true", default=False, help=argparse.SUPPRESS)
    rr.add_argument("--install", action="store_true", help=argparse.SUPPRESS)
    rr.add_argument("--no-install", action="store_true", help=argparse.SUPPRESS)
    rr.add_argument("--command", dest="reproduce_command_legacy", help=argparse.SUPPRESS)
    rr.add_argument("--workdir", help=argparse.SUPPRESS)
    rr.add_argument("--keep-workdir", action="store_true", help=argparse.SUPPRESS)
    rr.add_argument("--ecosystem", help=argparse.SUPPRESS)
    rr.add_argument("--capsule", dest="capsule_path", help=argparse.SUPPRESS)
    rr.add_argument("--capsule-include-artifacts", action="store_true", help=argparse.SUPPRESS)
    rr.add_argument("--capsule-max-artifact-mb", type=float, default=10.0, help=argparse.SUPPRESS)

    # reproduce status
    rs = reproduce_sub.add_parser("status", help="Show status of a reproduction run.")
    rs.add_argument("run_dir", help="Path to the run directory.")
    rs.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format (default: markdown).")
    rs.add_argument("--output", "-o", help="Write output to file instead of stdout.")

    # reproduce report
    rre = reproduce_sub.add_parser("report", help="Generate a reproduction report.")
    rre.add_argument("run_dir", help="Path to the run directory.")
    rre.add_argument("--format", choices=["markdown", "json", "html"], default="markdown", help="Output format (default: markdown).")
    rre.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # reproduce compare
    rc = reproduce_sub.add_parser("compare", help="Compare run against expected values.")
    rc.add_argument("run_dir", help="Path to the run directory.")
    rc.add_argument("--expected", required=True, help="Path to reproducibility.yml with expected values.")
    rc.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format (default: markdown).")
    rc.add_argument("--output", "-o", help="Write output to file instead of stdout.")

    # reproduce bundle
    rb = reproduce_sub.add_parser("bundle", help="Create reproduction evidence bundle.")
    rb.add_argument("run_dir", help="Path to the run directory.")
    rb.add_argument("--output", "-o", default="reproduction-evidence.zip", help="Output ZIP path (default: reproduction-evidence.zip).")

    # reproduce inspect
    ri = reproduce_sub.add_parser("inspect", help="Inspect reproduction evidence bundle.")
    ri.add_argument("bundle", help="Path to the bundle ZIP file.")
    ri.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format (default: markdown).")
    ri.add_argument("--output", "-o", help="Write output to file instead of stdout.")

    # reproduce verify-bundle
    rvb = reproduce_sub.add_parser("verify-bundle", help="Verify reproduction evidence bundle integrity.")
    rvb.add_argument("bundle", help="Path to the bundle ZIP file.")
    rvb.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format (default: markdown).")
    rvb.add_argument("--output", "-o", help="Write output to file instead of stdout.")

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

    # dossier command
    dossier_parser = subparsers.add_parser("dossier", help="Generate a reproducibility dossier.")
    dossier_parser.add_argument("--scan-report", help="Path to scan JSON report.")
    dossier_parser.add_argument("--reproduce-report", help="Path to reproduce JSON report.")
    dossier_parser.add_argument("--capsule", help="Path to capsule zip.")
    dossier_parser.add_argument("--workspace-report", help="Path to workspace/batch JSON report.")
    dossier_parser.add_argument("--repo", help="Path to repository (runs scan internally).")
    dossier_parser.add_argument("--audience", choices=["author", "reviewer", "maintainer"], default="author", help="Target audience.")
    dossier_parser.add_argument("--language", choices=["en", "zh-CN", "ja"], default="en", help="Output language.")
    dossier_parser.add_argument("--format", choices=["markdown", "json", "html", "issue", "pr-comment"], default="markdown", help="Output format.")
    dossier_parser.add_argument("--output", "-o", help="Write output to file.")

    # ecosystems command group
    ecosystems_parser = subparsers.add_parser("ecosystems", help="Language ecosystem management.")
    ecosystems_sub = ecosystems_parser.add_subparsers(dest="ecosystems_command")

    # ecosystems detect
    ed = ecosystems_sub.add_parser("detect", help="Detect language ecosystems in a repository.")
    ed.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    ed.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    ed.add_argument("--output", "-o", help="Write output to file.")

    # ecosystems explain
    ee = ecosystems_sub.add_parser("explain", help="Explain a language ecosystem.")
    ee.add_argument("ecosystem", help="Ecosystem ID (e.g., r, julia, snakemake).")
    ee.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")

    # data command group
    data_parser = subparsers.add_parser("data", help="Data diagnostics.")
    data_sub = data_parser.add_subparsers(dest="data_command")

    # data diagnose
    dd = data_sub.add_parser("diagnose", help="Diagnose data availability and documentation.")
    dd.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    dd.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    dd.add_argument("--output", "-o", help="Write output to file.")

    # results command group
    results_parser = subparsers.add_parser("results", help="Result and artifact validation.")
    results_sub = results_parser.add_subparsers(dest="results_command")

    # results validate
    rv = results_sub.add_parser("validate", help="Validate result artifacts.")
    rv.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    rv.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    rv.add_argument("--output", "-o", help="Write output to file.")

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

    # wizard command
    wizard_parser = subparsers.add_parser("wizard", help="Guided setup for new users.")
    wizard_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")

    # workbench command
    workbench_parser = subparsers.add_parser("workbench", help="Run a multi-step reproducibility pipeline.")
    workbench_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    workbench_parser.add_argument("--output-dir", dest="output_dir", default="",
                                  help="Output directory for results (default: no files).")
    workbench_parser.add_argument("--with-reproduce-dry-run", action="store_true",
                                  help="Include reproduce dry-run step.")
    workbench_parser.add_argument("--force", action="store_true",
                                  help="Overwrite existing output directory.")

    # theme command group
    theme_parser = subparsers.add_parser("theme", help="Theme management.")
    theme_sub = theme_parser.add_subparsers(dest="theme_command")
    theme_sub.add_parser("list", help="List available themes.")
    theme_preview = theme_sub.add_parser("preview", help="Preview the current theme.")
    theme_preview.add_argument("--theme", choices=["classic", "minimal", "contrast"],
                               default="classic", help="Theme to preview.")

    # adopt command
    adopt_parser = subparsers.add_parser("adopt", help="Generate an adoption plan for a repository.")
    adopt_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    adopt_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    adopt_parser.add_argument("--output", "-o", help="Write plan to file.")

    # scaffold command
    scaffold_parser = subparsers.add_parser("scaffold", help="Scaffold missing reproducibility files.")
    scaffold_parser.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    scaffold_parser.add_argument("--ecosystem", help="Target ecosystem (python, r, julia, node, make, snakemake).")
    scaffold_parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default).")
    scaffold_parser.add_argument("--apply", action="store_true", help="Apply scaffold (write files).")
    scaffold_parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    scaffold_parser.add_argument("--output", "-o", help="Write patch preview to file.")
    scaffold_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")

    # eval command group
    eval_parser = subparsers.add_parser("eval", help="Benchmark evaluation.")
    eval_sub = eval_parser.add_subparsers(dest="eval_command")

    # eval run
    er = eval_sub.add_parser("run", help="Run evaluation on a benchmark corpus.")
    er.add_argument("corpus_dir", help="Path to corpus directory.")
    er.add_argument("--format", choices=["json", "markdown", "html"], default="markdown",
                    help="Output format (default: markdown).")
    er.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # eval compare
    ec = eval_sub.add_parser("compare", help="Compare two evaluation results.")
    ec.add_argument("--baseline", required=True, help="Path to baseline evaluation JSON.")
    ec.add_argument("--current", required=True, help="Path to current evaluation JSON.")
    ec.add_argument("--format", choices=["json", "markdown"], default="markdown",
                    help="Output format (default: markdown).")
    ec.add_argument("--output", "-o", help="Write output to file instead of stdout.")

    # fix command group
    fix_parser = subparsers.add_parser("fix", help="Preview and apply safe fixes.")
    fix_sub = fix_parser.add_subparsers(dest="fix_command")

    # fix preview
    fix_preview = fix_sub.add_parser("preview", help="Preview recommended fixes.")
    fix_preview.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    fix_preview.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    fix_preview.add_argument("--output", "-o", help="Write preview to file.")

    # fix apply
    fix_apply = fix_sub.add_parser("apply", help="Apply safe fixes.")
    fix_apply.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    fix_apply.add_argument("--yes", action="store_true", help="Confirm apply without prompt.")
    fix_apply.add_argument("--force", action="store_true", help="Overwrite existing files.")

    # quickstart command
    qs = subparsers.add_parser(
        "quickstart",
        help="Show recommended first steps for new users.",
    )
    qs.add_argument(
        "--format",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text).",
    )
    qs.add_argument(
        "--topic",
        choices=["install", "github-action", "reproduce", "eval"],
        help="Show topic-specific guidance.",
    )

    # try-demo command
    td = subparsers.add_parser(
        "try-demo",
        help="Run a self-contained demo using built-in examples.",
    )
    td.add_argument(
        "--format",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text).",
    )
    td.add_argument(
        "--output",
        help="Write output to file.",
    )
    td.add_argument(
        "--plain",
        action="store_true",
        help="Plain text output (no colors).",
    )

    # trust command group
    trust_parser = subparsers.add_parser("trust", help="Trust & supply-chain security.")
    trust_sub = trust_parser.add_subparsers(dest="trust_command")

    # trust audit
    ta = trust_sub.add_parser("audit", help="Run trust audit.")
    ta.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    ta.add_argument("--format", choices=["json", "markdown", "html"], default="markdown", help="Output format.")
    ta.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # trust inventory
    ti = trust_sub.add_parser("inventory", help="Build dependency inventory.")
    ti.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    ti.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    ti.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # trust provenance
    tp = trust_sub.add_parser("provenance", help="Generate provenance manifest.")
    tp.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    tp.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format.")
    tp.add_argument("--output", "-o", help="Write manifest to file instead of stdout.")
    tp.add_argument("--include-timestamp", action="store_true", help="Include UTC timestamp.")

    # trust verify-artifacts
    tv = trust_sub.add_parser("verify-artifacts", help="Verify artifacts against SHA256SUMS.")
    tv.add_argument("artifact_dir", help="Path to artifact directory.")
    tv.add_argument("--checksums", help="Path to SHA256SUMS file (default: auto-detect).")
    tv.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    tv.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # security command group
    security_parser = subparsers.add_parser("security", help="Security scanning.")
    security_sub = security_parser.add_subparsers(dest="security_command")

    # security scan
    ss = security_sub.add_parser("scan", help="Run security scan.")
    ss.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    ss.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format.")
    ss.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # evidence command group
    evidence_parser = subparsers.add_parser("evidence", help="Unified evidence report.")
    evidence_sub = evidence_parser.add_subparsers(dest="evidence_command")

    # evidence report (default subcommand)
    ev = evidence_sub.add_parser("report", help="Generate unified evidence report.")
    ev.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    ev.add_argument("--profile", choices=["reviewer", "author", "maintainer"], default="reviewer",
                     help="Report profile (default: reviewer).")
    ev.add_argument("--format", choices=["json", "markdown", "html"], default="markdown",
                     help="Output format (default: markdown).")
    ev.add_argument("--output", "-o", help="Write report to file instead of stdout.")
    ev.add_argument("--include", action="append",
                     help="Include specific sections (can be repeated). Default: all.")

    # evidence bundle
    eb = evidence_sub.add_parser("bundle", help="Create evidence bundle ZIP.")
    eb.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    eb.add_argument("--profile", choices=["reviewer", "author", "maintainer"], default="reviewer",
                     help="Report profile (default: reviewer).")
    eb.add_argument("--output", "-o", default="evidence-bundle.zip",
                     help="Output ZIP path (default: evidence-bundle.zip).")
    eb.add_argument("--include", action="append",
                     help="Include specific sections (can be repeated). Default: all.")

    # evidence inspect
    ei = evidence_sub.add_parser("inspect", help="Inspect evidence bundle.")
    ei.add_argument("bundle", help="Path to evidence bundle ZIP.")
    ei.add_argument("--format", choices=["json", "markdown"], default="markdown",
                     help="Output format (default: markdown).")
    ei.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # evidence verify
    evf = evidence_sub.add_parser("verify", help="Verify evidence bundle integrity.")
    evf.add_argument("bundle", help="Path to evidence bundle ZIP.")
    evf.add_argument("--format", choices=["json", "markdown"], default="markdown",
                      help="Output format (default: markdown).")
    evf.add_argument("--output", "-o", help="Write report to file instead of stdout.")

    # intake command
    intake_parser = subparsers.add_parser("intake", help="Repository intake analysis (read-only).")
    intake_parser.add_argument("input", help="Local path, GitHub URL, or paper URL.")
    intake_parser.add_argument("--format", choices=["json", "markdown", "html"], default="markdown",
                               help="Output format (default: markdown).")
    intake_parser.add_argument("--output", "-o", help="Write report to file instead of stdout.")
    intake_parser.add_argument("--clone", action="store_true",
                               help="Clone GitHub URL (only if input is a GitHub URL).")

    # autoplan command group
    autoplan_parser = subparsers.add_parser("autoplan", help="Generate candidate reproducibility plan.")
    autoplan_sub = autoplan_parser.add_subparsers(dest="autoplan_command")

    # autoplan (default: generate)
    ap = autoplan_sub.add_parser("generate", help="Generate candidate reproducibility.yml.")
    ap.add_argument("path", nargs="?", default=".", help="Path to repository root (default: .)")
    ap.add_argument("--format", choices=["yaml", "json", "markdown"], default="yaml",
                    help="Output format (default: yaml).")
    ap.add_argument("--output", "-o", help="Write candidate config to file.")
    ap.add_argument("--write", action="store_true",
                    help="Write candidate config (requires --output or writes to default path).")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing file (only with --write).")
    ap.add_argument("--clone", action="store_true",
                    help="Clone GitHub URL if input is a URL.")

    # autoplan validate
    av = autoplan_sub.add_parser("validate", help="Validate a candidate reproducibility.yml.")
    av.add_argument("config", help="Path to candidate reproducibility.yml.")
    av.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

    # autoplan diff
    ad = autoplan_sub.add_parser("diff", help="Compare two reproducibility.yml files.")
    ad.add_argument("--old", required=True, help="Path to old config.")
    ad.add_argument("--new", dest="new_config", required=True, help="Path to new config.")
    ad.add_argument("--format", choices=["markdown", "json"], default="markdown",
                    help="Output format (default: markdown).")
    ad.add_argument("--output", "-o", help="Write diff to file.")

    # autoplan explain
    ae = autoplan_sub.add_parser("explain", help="Explain a candidate reproducibility.yml.")
    ae.add_argument("config", help="Path to candidate reproducibility.yml.")
    ae.add_argument("--format", choices=["markdown", "json"], default="markdown",
                    help="Output format (default: markdown).")

    # Handle `evidence .` as shorthand for `evidence report .`
    # Insert "report" before parsing if evidence is followed by a path, not a subcommand
    _ev_subcmds = {"report", "bundle", "inspect", "verify"}
    if argv is None:
        _argv_list = sys.argv[1:]
    else:
        _argv_list = list(argv)

    if "evidence" in _argv_list:
        _ev_idx = _argv_list.index("evidence")
        if _ev_idx + 1 < len(_argv_list) and _argv_list[_ev_idx + 1] not in _ev_subcmds and not _argv_list[_ev_idx + 1].startswith("-"):
            _argv_list.insert(_ev_idx + 1, "report")

    # Handle `reproduce <path>` as shorthand for `reproduce run <path>`
    # for backward compatibility with the flat reproduce command.
    _repro_subcmds = {"plan", "run", "status", "report", "compare", "bundle", "inspect", "verify-bundle"}
    if "reproduce" in _argv_list:
        _rp_idx = _argv_list.index("reproduce")
        if _rp_idx + 1 < len(_argv_list) and _argv_list[_rp_idx + 1] not in _repro_subcmds and not _argv_list[_rp_idx + 1].startswith("-"):
            _argv_list.insert(_rp_idx + 1, "run")

    # Handle `autoplan .` as shorthand for `autoplan generate .`
    _ap_subcmds = {"generate", "validate", "diff", "explain"}
    if "autoplan" in _argv_list:
        _ap_idx = _argv_list.index("autoplan")
        if _ap_idx + 1 < len(_argv_list) and _argv_list[_ap_idx + 1] not in _ap_subcmds and not _argv_list[_ap_idx + 1].startswith("-"):
            _argv_list.insert(_ap_idx + 1, "generate")

    args, remaining = parser.parse_known_args(_argv_list)

    # Resolve output mode from global flags
    from oss_paper_ci.terminal import OutputMode
    from oss_paper_ci.themes import get_theme as _get_theme_fn

    # Handle global flags that may appear after the subcommand
    global _mode, _theme, _debug
    plain = getattr(args, "plain", False) or "--plain" in (remaining or [])
    no_color = getattr(args, "no_color", False) or "--no-color" in (remaining or [])
    no_animate = getattr(args, "no_animate", False) or "--no-animate" in (remaining or [])
    debug = getattr(args, "debug", False) or "--debug" in (remaining or [])
    theme_name = getattr(args, "theme", "classic")
    for i, arg in enumerate(remaining or []):
        if arg == "--theme" and i + 1 < len(remaining):
            theme_name = remaining[i + 1]

    _mode = OutputMode(plain=plain, no_color=no_color, no_animate=no_animate)
    _theme = _get_theme_fn(theme_name)
    _debug = debug

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "version":
        print(f"oss-paper-ci {__version__}")
        return 0

    if args.command == "guide":
        return _cmd_guide(args)

    if args.command == "dossier":
        return _cmd_dossier(args)

    if args.command == "ecosystems":
        return _cmd_ecosystems(args)

    if args.command == "data":
        return _cmd_data(args)

    if args.command == "results":
        return _cmd_results(args)

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

    if args.command == "wizard":
        return _cmd_wizard(args)

    if args.command == "workbench":
        return _cmd_workbench(args)

    if args.command == "theme":
        return _cmd_theme(args)

    if args.command == "adopt":
        return _cmd_adopt(args)

    if args.command == "scaffold":
        return _cmd_scaffold(args)

    if args.command == "fix":
        return _cmd_fix(args)

    if args.command == "eval":
        return _cmd_eval(args)

    if args.command == "quickstart":
        return _cmd_quickstart(args)

    if args.command == "try-demo":
        return _cmd_try_demo(args)

    if args.command == "trust":
        return _cmd_trust(args)

    if args.command == "security":
        return _cmd_security(args)

    if args.command == "evidence":
        return _cmd_evidence(args)

    if args.command == "intake":
        return _cmd_intake(args)

    if args.command == "autoplan":
        return _cmd_autoplan(args)

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


# ── Reproduce command group ──────────────────────────────────────────────────

def _cmd_reproduce(args: argparse.Namespace) -> int:
    """Handle the reproduce subcommand group."""
    sub = getattr(args, "reproduce_command", None)

    if sub == "plan":
        return _cmd_reproduce_plan(args)
    if sub == "run":
        return _cmd_reproduce_run(args)
    if sub == "status":
        return _cmd_reproduce_status(args)
    if sub == "report":
        return _cmd_reproduce_report(args)
    if sub == "compare":
        return _cmd_reproduce_compare(args)
    if sub == "bundle":
        return _cmd_reproduce_bundle(args)
    if sub == "inspect":
        return _cmd_reproduce_inspect(args)
    if sub == "verify-bundle":
        return _cmd_reproduce_verify_bundle(args)

    # No subcommand — show help
    print("Usage: oss-paper-ci reproduce <subcommand>", file=sys.stderr)
    print("Subcommands: plan, run, status, report, compare, bundle, inspect, verify-bundle", file=sys.stderr)
    return 1


def _cmd_reproduce_plan(args: argparse.Namespace) -> int:
    """Handle reproduce plan subcommand."""
    from oss_paper_ci.repro_plan import build_plan, format_plan_json, format_plan_markdown

    path = getattr(args, "path", ".")
    contract_path = getattr(args, "contract_path", None)
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    plan = build_plan(path, contract_path=contract_path)

    if fmt == "json":
        text = format_plan_json(plan)
    else:
        text = format_plan_markdown(plan)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Plan written to {output}")
    else:
        print(text)

    if plan.warnings:
        return 1
    return 0


def _cmd_reproduce_run(args: argparse.Namespace) -> int:
    """Handle reproduce run subcommand."""
    from oss_paper_ci.repro_runner import run_reproduction
    from oss_paper_ci.reporting.repro_report import (
        generate_repro_run_html,
        generate_repro_run_json,
        generate_repro_run_markdown,
    )

    path = getattr(args, "path", ".")
    contract_path = getattr(args, "contract_path", None)
    execute = getattr(args, "execute", False)
    sandbox_type = getattr(args, "sandbox", "local")
    timeout = getattr(args, "timeout", None)
    output_dir = getattr(args, "output_dir", None)
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)
    fail_on = getattr(args, "fail_on", None)

    result = run_reproduction(
        path,
        contract_path=contract_path,
        execute=execute,
        sandbox_type=sandbox_type,
        output_dir=output_dir,
        timeout=timeout,
    )

    if fmt == "json":
        text = generate_repro_run_json(result)
    elif fmt == "html":
        text = generate_repro_run_html(result)
    else:
        text = generate_repro_run_markdown(result)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Report written to {output}")
    else:
        print(text)

    # Exit code logic
    if result.error:
        return 2
    if fail_on == "failed-command" and any(
        cr.status in ("failed", "timeout", "blocked") for cr in result.command_results
    ):
        return 1
    if fail_on == "missing-artifact" and result.artifact_validation and result.artifact_validation.missing > 0:
        return 1
    if fail_on == "out-of-range" and result.metric_validation and not result.metric_validation.ok:
        return 1
    if not result.ok and result.overall_status not in ("dry_run",):
        return 1
    return 0


def _cmd_reproduce_status(args: argparse.Namespace) -> int:
    """Handle reproduce status subcommand."""
    from oss_paper_ci.repro_status import (
        format_status_json,
        format_status_markdown,
        read_run_status,
    )

    run_dir = getattr(args, "run_dir", None)
    if not run_dir:
        print("Error: run_dir is required.", file=sys.stderr)
        return 1

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    status = read_run_status(run_dir)

    if fmt == "json":
        text = format_status_json(status)
    else:
        text = format_status_markdown(status)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Status written to {output}")
    else:
        print(text)

    if status.error:
        return 1
    return 0


def _cmd_reproduce_report(args: argparse.Namespace) -> int:
    """Handle reproduce report subcommand."""
    import json as _json
    from oss_paper_ci.repro_runner import ReproductionRun
    from oss_paper_ci.reporting.repro_report import (
        generate_repro_run_html,
        generate_repro_run_json,
        generate_repro_run_markdown,
    )

    run_dir = getattr(args, "run_dir", None)
    if not run_dir:
        print("Error: run_dir is required.", file=sys.stderr)
        return 1

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    # Load run manifest
    manifest_path = Path(run_dir) / "run-manifest.json"
    if not manifest_path.exists():
        print(f"Error: No run-manifest.json found in {run_dir}", file=sys.stderr)
        return 1

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = _json.load(f)
    except Exception as exc:
        print(f"Error reading manifest: {exc}", file=sys.stderr)
        return 1

    # Create a minimal ReproductionRun-like object for the report generator
    class _RunProxy:
        pass

    run = _RunProxy()
    for key, val in manifest.items():
        setattr(run, key, val)
    # Ensure required attributes exist
    run.overall_status = manifest.get("overall_status", "unknown")
    run.dry_run = manifest.get("dry_run", True)
    run.started_at = manifest.get("started_at", "")
    run.finished_at = manifest.get("finished_at", "")
    run.sandbox_type = manifest.get("sandbox_type", "unknown")
    run.error = manifest.get("error", "")
    run.warnings = manifest.get("warnings", [])
    run.command_results = [_CmdResultProxy(cr) for cr in manifest.get("command_results", [])]
    run.artifact_validation = _ArtValProxy(manifest.get("artifact_validation")) if manifest.get("artifact_validation") else None
    run.metric_validation = _MetValProxy(manifest.get("metric_validation")) if manifest.get("metric_validation") else None

    if fmt == "json":
        text = generate_repro_run_json(run)
    elif fmt == "html":
        text = generate_repro_run_html(run)
    else:
        text = generate_repro_run_markdown(run)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Report written to {output}")
    else:
        print(text)

    return 0


class _CmdResultProxy:
    """Proxy for command result dicts."""
    def __init__(self, d: dict):
        self.command_id = d.get("command_id", "")
        self.command = d.get("command", "")
        self.exit_code = d.get("exit_code", -1)
        self.duration_seconds = d.get("duration_seconds", 0.0)
        self.timed_out = d.get("timed_out", False)
        self.blocked = d.get("blocked", False)
        self.block_reason = d.get("block_reason", "")
        self.stdout_excerpt = d.get("stdout_excerpt", "")
        self.stderr_excerpt = d.get("stderr_excerpt", "")
        self.status = d.get("status", "unknown")


class _ArtResultProxy:
    """Proxy for artifact result dicts."""
    def __init__(self, d: dict):
        self.path = d.get("path", "")
        self.exists = d.get("exists", False)
        self.size_bytes = d.get("size_bytes", 0)
        self.sha256 = d.get("sha256", "")
        self.type = d.get("type", "file")


class _ArtValProxy:
    """Proxy for artifact validation dicts."""
    def __init__(self, d: dict):
        self.total = d.get("total", 0)
        self.found = d.get("found", 0)
        self.missing = d.get("missing", 0)
        self.artifacts = [_ArtResultProxy(a) for a in d.get("artifacts", [])]


class _MetCheckProxy:
    """Proxy for metric check dicts."""
    def __init__(self, d: dict):
        self.key = d.get("key", "")
        self.actual_value = d.get("actual_value")
        self.expected_min = d.get("expected_min")
        self.expected_max = d.get("expected_max")
        self.in_range = d.get("in_range", True)
        self.file = d.get("file", "")


class _MetValProxy:
    """Proxy for metric validation dicts."""
    def __init__(self, d: dict):
        self.total = d.get("total", 0)
        self.in_range = d.get("in_range", 0)
        self.out_of_range = d.get("out_of_range", 0)
        self.errors = d.get("errors", 0)
        self.checks = [_MetCheckProxy(c) for c in d.get("checks", [])]
        self.ok = self.out_of_range == 0 and self.errors == 0


def _cmd_reproduce_compare(args: argparse.Namespace) -> int:
    """Handle reproduce compare subcommand."""
    from oss_paper_ci.repro_compare import (
        compare_run,
        format_compare_json,
        format_compare_markdown,
    )

    run_dir = getattr(args, "run_dir", None)
    expected = getattr(args, "expected", None)
    if not run_dir or not expected:
        print("Error: run_dir and --expected are required.", file=sys.stderr)
        return 1

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    report = compare_run(run_dir, expected)

    if fmt == "json":
        text = format_compare_json(report)
    else:
        text = format_compare_markdown(report)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Comparison written to {output}")
    else:
        print(text)

    if report.error:
        return 2
    if not report.ok:
        return 1
    return 0


def _cmd_reproduce_bundle(args: argparse.Namespace) -> int:
    """Handle reproduce bundle subcommand."""
    from oss_paper_ci.repro_bundle import create_bundle

    run_dir = getattr(args, "run_dir", None)
    output = getattr(args, "output", "reproduction-evidence.zip")
    if not run_dir:
        print("Error: run_dir is required.", file=sys.stderr)
        return 1

    try:
        path = create_bundle(run_dir, output)
        print(f"Bundle created: {path}")
    except Exception as exc:
        print(f"Error creating bundle: {exc}", file=sys.stderr)
        return 2

    return 0


def _cmd_reproduce_inspect(args: argparse.Namespace) -> int:
    """Handle reproduce inspect subcommand."""
    from oss_paper_ci.repro_bundle import (
        format_bundle_inspect_markdown,
        inspect_bundle,
    )

    bundle = getattr(args, "bundle", None)
    if not bundle:
        print("Error: bundle path is required.", file=sys.stderr)
        return 1

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    info = inspect_bundle(bundle)

    if fmt == "json":
        import json as _json
        text = _json.dumps(info.to_dict(), indent=2)
    else:
        text = format_bundle_inspect_markdown(info)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Inspection written to {output}")
    else:
        print(text)

    return 0


def _cmd_reproduce_verify_bundle(args: argparse.Namespace) -> int:
    """Handle reproduce verify-bundle subcommand."""
    from oss_paper_ci.repro_bundle import (
        format_bundle_verify_markdown,
        verify_bundle,
    )

    bundle = getattr(args, "bundle", None)
    if not bundle:
        print("Error: bundle path is required.", file=sys.stderr)
        return 1

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    result = verify_bundle(bundle)

    if fmt == "json":
        import json as _json
        text = _json.dumps(result.to_dict(), indent=2)
    else:
        text = format_bundle_verify_markdown(result)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Verification written to {output}")
    else:
        print(text)

    if not result.valid:
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


# ── Ecosystems command ───────────────────────────────────────────────────────

def _cmd_ecosystems(args: argparse.Namespace) -> int:
    """Handle the ecosystems subcommand group."""
    sub = getattr(args, "ecosystems_command", None)

    if sub == "detect":
        return _cmd_ecosystems_detect(
            path=getattr(args, "path", "."),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    if sub == "explain":
        return _cmd_ecosystems_explain(
            ecosystem=getattr(args, "ecosystem", None),
            fmt=getattr(args, "format", "markdown"),
        )

    print("Usage: oss-paper-ci ecosystems {detect|explain} ...", file=sys.stderr)
    return 1


def _cmd_ecosystems_detect(path: str, fmt: str, output: str | None) -> int:
    """Detect language ecosystems in a repository."""
    import json as json_mod

    from oss_paper_ci.ecosystems import detect_ecosystems

    repo_path = Path(path).resolve()
    if not repo_path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    ecosystems = detect_ecosystems(str(repo_path))

    if fmt == "json":
        data = {
            "repo_path": str(repo_path),
            "ecosystems": [e.to_dict() for e in ecosystems],
            "total_detected": len(ecosystems),
        }
        text = json_mod.dumps(data, indent=2, ensure_ascii=False)
    else:
        lines = ["# Detected Ecosystems\n"]
        if not ecosystems:
            lines.append("No language ecosystems detected.\n")
        else:
            lines.append(f"**{len(ecosystems)} ecosystem(s) detected** in `{repo_path}`\n")
            for eco in ecosystems:
                lines.append(f"## {eco.display_name} (`{eco.id}`)\n")
                lines.append(f"- **Support level:** {eco.support_level}")
                lines.append(f"- **Runtime required:** `{eco.runtime_required}`")
                lines.append(f"- **Runtime available:** {'yes' if eco.runtime_available else 'no'}")
                if eco.environment_files:
                    lines.append(f"- **Environment files:** {', '.join(f'`{f}`' for f in eco.environment_files)}")
                if eco.entrypoint_candidates:
                    lines.append(f"- **Entrypoints:** {', '.join(f'`{f}`' for f in eco.entrypoint_candidates[:5])}")
                if eco.install_plan:
                    lines.append(f"- **Install plan:** {'; '.join(f'`{c}`' for c in eco.install_plan)}")
                if eco.run_plan:
                    lines.append(f"- **Run plan:** {'; '.join(f'`{c}`' for c in eco.run_plan[:3])}")
                if eco.limitations:
                    lines.append("- **Limitations:**")
                    for lim in eco.limitations:
                        lines.append(f"  - {lim}")
                lines.append("")

        text = "\n".join(lines)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Ecosystem detection written to {output}")
    else:
        print(text)

    return 0


def _cmd_ecosystems_explain(ecosystem: str, fmt: str) -> int:
    """Explain a language ecosystem."""
    import json as json_mod

    from oss_paper_ci.ecosystems import get_ecosystem_info, list_ecosystems

    if not ecosystem:
        print("Available ecosystems:", file=sys.stderr)
        for eco in list_ecosystems():
            print(f"  {eco['id']}: {eco['display_name']} ({eco['support_level']})")
        return 1

    info = get_ecosystem_info(ecosystem)
    if not info:
        print(f"Unknown ecosystem: {ecosystem}", file=sys.stderr)
        print(f"Available: {', '.join(e['id'] for e in list_ecosystems())}", file=sys.stderr)
        return 1

    if fmt == "json":
        print(json_mod.dumps(info, indent=2, ensure_ascii=False))
    else:
        lines = [f"# {info['display_name']} (`{info['id']}`)\n"]
        lines.append(f"- **Support level:** {info['support_level']}")
        lines.append(f"- **Runtime required:** `{info['runtime_required']}`")
        lines.append(f"- **Runtime available:** {'yes' if info['runtime_available'] else 'no'}")
        if info.get("environment_files"):
            lines.append(f"- **Environment files:** {', '.join(f'`{f}`' for f in info['environment_files'])}")
        if info.get("entrypoint_candidates"):
            lines.append(f"- **Entrypoints:** {', '.join(f'`{f}`' for f in info['entrypoint_candidates'][:5])}")
        if info.get("limitations"):
            lines.append("- **Limitations:**")
            for lim in info["limitations"]:
                lines.append(f"  - {lim}")
        if info.get("safety_notes"):
            lines.append("- **Safety notes:**")
            for note in info["safety_notes"]:
                lines.append(f"  - {note}")
        print("\n".join(lines))

    return 0


# ── Data command ─────────────────────────────────────────────────────────────

def _cmd_data(args: argparse.Namespace) -> int:
    """Handle the data subcommand group."""
    sub = getattr(args, "data_command", None)

    if sub == "diagnose":
        return _cmd_data_diagnose(
            path=getattr(args, "path", "."),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    print("Usage: oss-paper-ci data diagnose [PATH]", file=sys.stderr)
    return 1


def _cmd_data_diagnose(path: str, fmt: str, output: str | None) -> int:
    """Run data diagnostics."""
    import json as json_mod

    from oss_paper_ci.data_diagnostics import run_data_diagnostics

    repo_path = Path(path).resolve()
    if not repo_path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    diagnostics = run_data_diagnostics(str(repo_path))

    if fmt == "json":
        data = {
            "repo_path": str(repo_path),
            "diagnostics": [d.to_dict() for d in diagnostics],
            "total_checks": len(diagnostics),
            "missing": sum(1 for d in diagnostics if d.status == "missing"),
        }
        text = json_mod.dumps(data, indent=2, ensure_ascii=False)
    else:
        lines = ["# Data Diagnostics\n"]
        lines.append(f"**Repository:** `{repo_path}`\n")
        missing = sum(1 for d in diagnostics if d.status == "missing")
        lines.append(f"**{len(diagnostics)} checks:** {missing} missing\n")

        for d in diagnostics:
            status_icon = {"present": "✅", "missing": "❌", "partial": "⚠️", "unknown": "❓"}.get(d.status, "?")
            lines.append(f"- {status_icon} **{d.title}**: {d.message}")
            if d.recommendation:
                lines.append(f"  - *Recommendation:* {d.recommendation}")
        lines.append("")
        text = "\n".join(lines)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Data diagnostics written to {output}")
    else:
        print(text)

    return 0


# ── Results command ──────────────────────────────────────────────────────────

def _cmd_results(args: argparse.Namespace) -> int:
    """Handle the results subcommand group."""
    sub = getattr(args, "results_command", None)

    if sub == "validate":
        return _cmd_results_validate(
            path=getattr(args, "path", "."),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    print("Usage: oss-paper-ci results validate [PATH]", file=sys.stderr)
    return 1


def _cmd_results_validate(path: str, fmt: str, output: str | None) -> int:
    """Run result validation."""
    import json as json_mod

    from oss_paper_ci.result_validation import run_result_validation

    repo_path = Path(path).resolve()
    if not repo_path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    validations = run_result_validation(str(repo_path))

    if fmt == "json":
        data = {
            "repo_path": str(repo_path),
            "validations": [v.to_dict() for v in validations],
            "total_checks": len(validations),
            "missing": sum(1 for v in validations if v.status == "missing"),
            "invalid": sum(1 for v in validations if v.status == "invalid"),
        }
        text = json_mod.dumps(data, indent=2, ensure_ascii=False)
    else:
        lines = ["# Result Validation\n"]
        lines.append(f"**Repository:** `{repo_path}`\n")
        missing = sum(1 for v in validations if v.status == "missing")
        invalid = sum(1 for v in validations if v.status == "invalid")
        lines.append(f"**{len(validations)} checks:** {missing} missing, {invalid} invalid\n")

        for v in validations:
            status_icon = {"present": "✅", "missing": "❌", "invalid": "⚠️", "unknown": "❓"}.get(v.status, "?")
            lines.append(f"- {status_icon} **{v.title}**: {v.message}")
            if v.recommendation:
                lines.append(f"  - *Recommendation:* {v.recommendation}")
        lines.append("")
        text = "\n".join(lines)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Result validation written to {output}")
    else:
        print(text)

    return 0


# ── Dossier command ──────────────────────────────────────────────────────────

def _cmd_dossier(args: argparse.Namespace) -> int:
    """Handle the dossier subcommand."""
    from oss_paper_ci.dossier import build_dossier
    from oss_paper_ci.reporting.dossier_report import (
        generate_dossier_html,
        generate_dossier_issue,
        generate_dossier_json,
        generate_dossier_markdown,
        generate_dossier_pr_comment,
    )

    scan_report = getattr(args, "scan_report", None)
    reproduce_report = getattr(args, "reproduce_report", None)
    capsule = getattr(args, "capsule", None)
    workspace_report = getattr(args, "workspace_report", None)
    repo_path = getattr(args, "repo", None)
    audience = getattr(args, "audience", "author")
    language = getattr(args, "language", "en")
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    if not any([scan_report, reproduce_report, capsule, workspace_report, repo_path]):
        print("Error: provide at least one input (--scan-report, --reproduce-report, "
              "--capsule, --workspace-report, or --repo).", file=sys.stderr)
        return 1

    dossier = build_dossier(
        scan_report=scan_report,
        reproduce_report=reproduce_report,
        capsule=capsule,
        workspace_report=workspace_report,
        repo_path=repo_path,
        audience=audience,
        language=language,
    )

    if fmt == "json":
        text = generate_dossier_json(dossier, output_path=output)
    elif fmt == "html":
        text = generate_dossier_html(dossier, output_path=output)
    elif fmt == "issue":
        text = generate_dossier_issue(dossier, output_path=output)
    elif fmt == "pr-comment":
        text = generate_dossier_pr_comment(dossier, output_path=output)
    else:
        text = generate_dossier_markdown(dossier, output_path=output)

    if output:
        print(f"Dossier written to {output}")
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


# ── Wizard command ──────────────────────────────────────────────────────────

def _cmd_wizard(args: argparse.Namespace) -> int:
    """Handle wizard command."""
    from oss_paper_ci.wizard import run_wizard
    return run_wizard(
        path=getattr(args, "path", "."),
        mode=_mode,
        theme=_theme,
    )


# ── Workbench command ───────────────────────────────────────────────────────

def _cmd_workbench(args: argparse.Namespace) -> int:
    """Handle workbench command."""
    from oss_paper_ci.workbench import run_workbench
    result = run_workbench(
        path=getattr(args, "path", "."),
        output_dir=getattr(args, "output_dir", ""),
        with_reproduce_dry_run=getattr(args, "with_reproduce_dry_run", False),
        force=getattr(args, "force", False),
        mode=_mode,
        theme=_theme,
    )
    # Only return non-zero on actual program errors, not on scan findings.
    # Scan "fail" means low score (expected for many repos), not a crash.
    if any(s.status == "error" for s in result.steps):
        return 2
    return 0


# ── Theme command ───────────────────────────────────────────────────────────

def _cmd_theme(args: argparse.Namespace) -> int:
    """Handle theme command group."""
    sub = getattr(args, "theme_command", None)

    if sub == "list":
        return _cmd_theme_list()
    if sub == "preview":
        return _cmd_theme_preview(getattr(args, "theme", "classic"))

    print("Usage: oss-paper-ci theme {list|preview}", file=sys.stderr)
    return 1


def _cmd_theme_list() -> int:
    """List available themes."""
    from oss_paper_ci.themes import list_themes, get_theme, THEMES
    from oss_paper_ci.ui import render_table

    themes = list_themes()
    headers = ["Name", "Description"]
    rows = [[t["name"], t["description"]] for t in themes]
    render_table(headers, rows, mode=_mode, theme=_theme)
    return 0


def _cmd_theme_preview(theme_name: str) -> int:
    """Preview a theme with sample output."""
    from oss_paper_ci.themes import get_theme
    from oss_paper_ci.ui import (
        render_title, render_step, render_steps, render_panel, render_score,
        render_summary, render_next_actions, render_warning,
    )

    theme = get_theme(theme_name)

    render_title("Theme Preview", f"Theme: {theme_name}", _mode, theme)

    # Sample steps
    steps = [
        {"name": "Detecting ecosystems", "status": "pass"},
        {"name": "Scanning repository", "status": "warn"},
        {"name": "Checking data evidence", "status": "fail"},
        {"name": "Validating results", "status": "pass"},
        {"name": "Preparing dossier", "status": "skip"},
    ]
    render_steps(steps, _mode, theme)

    print()
    render_score(72, {"metadata": 85, "environment": 60, "experiments": 70, "data": 55, "results": 80}, _mode, theme)

    render_summary([
        {"label": "Overall readiness", "value": "needs work", "status": "warn"},
        {"label": "Data evidence", "value": "missing data README", "status": "fail"},
    ], _mode, theme)

    render_next_actions([
        "Add data/README.md documenting your datasets.",
        "Run 'oss-paper-ci scan . --verbose' for details.",
    ], _mode, theme)

    render_warning("This is a sample warning message.", _mode, theme)

    return 0


# ── Adopt command ──────────────────────────────────────────────────────────

def _cmd_adopt(args: argparse.Namespace) -> int:
    """Handle adopt command."""
    import json as json_mod
    from oss_paper_ci.adoption import build_adoption_plan, format_adoption_plan_markdown

    path = getattr(args, "path", ".")
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    # Detect ecosystems
    ecosystems = None
    try:
        from oss_paper_ci.ecosystems import detect_ecosystems
        eco_list = detect_ecosystems(path)
        ecosystems = [e.to_dict() for e in eco_list] if eco_list else []
    except Exception:
        pass

    plan = build_adoption_plan(repo_path=path, ecosystems=ecosystems)

    if fmt == "json":
        text = plan.to_json()
    else:
        text = format_adoption_plan_markdown(plan)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Adoption plan written to {output}")
    else:
        print(text)

    return 0


# ── Scaffold command ───────────────────────────────────────────────────────

def _cmd_scaffold(args: argparse.Namespace) -> int:
    """Handle scaffold command."""
    import json as json_mod
    from oss_paper_ci.scaffold import run_scaffold, generate_scaffold_patch

    path = getattr(args, "path", ".")
    apply_mode = getattr(args, "apply", False)
    force = getattr(args, "force", False)
    output = getattr(args, "output", None)
    fmt = getattr(args, "format", "markdown")

    # Detect ecosystems
    ecosystems = None
    try:
        from oss_paper_ci.ecosystems import detect_ecosystems
        eco_list = detect_ecosystems(path)
        ecosystems = [e.to_dict() for e in eco_list] if eco_list else []
    except Exception:
        pass

    dry_run = not apply_mode

    if dry_run:
        # Generate patch preview
        patch = generate_scaffold_patch(repo_path=path, ecosystems=ecosystems)
        if output:
            Path(output).write_text(patch, encoding="utf-8")
            print(f"Scaffold preview written to {output}")
        else:
            print(patch)
    else:
        # Apply scaffold
        result = run_scaffold(
            repo_path=path,
            ecosystems=ecosystems,
            dry_run=False,
            force=force,
        )

        if fmt == "json":
            text = json_mod.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        else:
            # Format as markdown summary
            lines = ["# Scaffold Apply Results", ""]
            if result.apply_result:
                lines.append(f"- Attempted: {result.apply_result.total_attempted}")
                lines.append(f"- Written: {result.apply_result.total_written}")
                lines.append(f"- Skipped: {result.apply_result.total_skipped}")
                lines.append(f"- Errors: {result.apply_result.total_errors}")
                lines.append("")
                for r in result.apply_result.results:
                    icon = "OK" if r.success else "X"
                    lines.append(f"- [{icon}] {r.message}")
            text = "\n".join(lines)

        if output:
            Path(output).write_text(text, encoding="utf-8")
            print(f"Scaffold results written to {output}")
        else:
            print(text)

    return 0


# ── Fix command ────────────────────────────────────────────────────────────

def _cmd_fix(args: argparse.Namespace) -> int:
    """Handle fix command group."""
    sub = getattr(args, "fix_command", None)

    if sub == "preview":
        return _cmd_fix_preview(args)
    if sub == "apply":
        return _cmd_fix_apply(args)

    print("Usage: oss-paper-ci fix {preview|apply}", file=sys.stderr)
    return 1


def _cmd_fix_preview(args: argparse.Namespace) -> int:
    """Handle fix preview command."""
    from oss_paper_ci.scaffold import run_scaffold, generate_scaffold_patch

    path = getattr(args, "path", ".")
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    # Detect ecosystems
    ecosystems = None
    try:
        from oss_paper_ci.ecosystems import detect_ecosystems
        eco_list = detect_ecosystems(path)
        ecosystems = [e.to_dict() for e in eco_list] if eco_list else []
    except Exception:
        pass

    # Generate adoption plan as fix preview
    from oss_paper_ci.adoption import build_adoption_plan, format_adoption_plan_markdown
    plan = build_adoption_plan(repo_path=path, ecosystems=ecosystems)

    if fmt == "json":
        text = plan.to_json()
    else:
        text = format_adoption_plan_markdown(plan)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Fix preview written to {output}")
    else:
        print(text)

    return 0


def _cmd_fix_apply(args: argparse.Namespace) -> int:
    """Handle fix apply command."""
    yes = getattr(args, "yes", False)
    force = getattr(args, "force", False)
    path = getattr(args, "path", ".")

    if not yes:
        print("Fix apply requires --yes to confirm.", file=sys.stderr)
        print("This will write files to your repository.", file=sys.stderr)
        print("Use 'oss-paper-ci fix preview .' first to see what would be written.", file=sys.stderr)
        return 1

    # Detect ecosystems
    ecosystems = None
    try:
        from oss_paper_ci.ecosystems import detect_ecosystems
        eco_list = detect_ecosystems(path)
        ecosystems = [e.to_dict() for e in eco_list] if eco_list else []
    except Exception:
        pass

    from oss_paper_ci.scaffold import run_scaffold
    result = run_scaffold(
        repo_path=path,
        ecosystems=ecosystems,
        dry_run=False,
        force=force,
    )

    if result.apply_result:
        print(f"Applied {result.apply_result.total_written} file(s).")
        if result.apply_result.total_skipped > 0:
            print(f"Skipped {result.apply_result.total_skipped} existing file(s).")
        if result.apply_result.total_errors > 0:
            print(f"Errors: {result.apply_result.total_errors}")
            return 2

    return 0


# ── Eval command ────────────────────────────────────────────────────────────

def _cmd_eval(args: argparse.Namespace) -> int:
    """Handle eval subcommand group."""
    sub = getattr(args, "eval_command", None)

    if sub == "run":
        return _cmd_eval_run(
            corpus_dir=getattr(args, "corpus_dir", None),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    if sub == "compare":
        return _cmd_eval_compare(
            baseline_path=getattr(args, "baseline", None),
            current_path=getattr(args, "current", None),
            fmt=getattr(args, "format", "markdown"),
            output=getattr(args, "output", None),
        )

    print("Usage: oss-paper-ci eval {run|compare} ...", file=sys.stderr)
    return 1


def _cmd_eval_run(
    *,
    corpus_dir: str | None,
    fmt: str,
    output: str | None,
) -> int:
    """Run evaluation on a benchmark corpus."""
    import json as json_mod

    if not corpus_dir:
        print("Error: corpus directory is required.", file=sys.stderr)
        return 1

    corpus_path = Path(corpus_dir).resolve()
    if not corpus_path.is_dir():
        print(f"Error: corpus directory not found: {corpus_dir}", file=sys.stderr)
        return 2

    from oss_paper_ci.eval_runner import (
        format_html,
        format_json,
        format_markdown,
        run_evaluation,
    )

    results = run_evaluation(corpus_path)

    if fmt == "json":
        text = format_json(results)
    elif fmt == "html":
        text = format_html(results)
    else:
        text = format_markdown(results)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Evaluation written to {output}")
    else:
        print(text)

    return 0


def _cmd_eval_compare(
    *,
    baseline_path: str | None,
    current_path: str | None,
    fmt: str,
    output: str | None,
) -> int:
    """Compare two evaluation results."""
    import json as json_mod

    if not baseline_path or not current_path:
        print("Error: --baseline and --current are required.", file=sys.stderr)
        return 1

    baseline_file = Path(baseline_path)
    current_file = Path(current_path)

    if not baseline_file.exists():
        print(f"Error: baseline file not found: {baseline_path}", file=sys.stderr)
        return 2
    if not current_file.exists():
        print(f"Error: current file not found: {current_path}", file=sys.stderr)
        return 2

    try:
        baseline = json_mod.loads(baseline_file.read_text(encoding="utf-8"))
        current = json_mod.loads(current_file.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error reading evaluation files: {exc}", file=sys.stderr)
        return 2

    from oss_paper_ci.eval_runner import compare_results, format_compare_json, format_compare_markdown

    comparison = compare_results(baseline, current)

    if fmt == "json":
        text = format_compare_json(comparison)
    else:
        text = format_compare_markdown(comparison)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Comparison written to {output}")
    else:
        print(text)

    return 0


# ── Quickstart command ─────────────────────────────────────────────────────

def _cmd_quickstart(args: argparse.Namespace) -> int:
    """Handle quickstart command."""
    topic = getattr(args, "topic", None)
    fmt = getattr(args, "format", "text")

    # Detect current directory state
    cwd = Path.cwd()
    has_git = (cwd / ".git").exists()
    has_readme = (cwd / "README.md").exists()
    has_scripts = (cwd / "scripts").exists()
    has_pyproject = (cwd / "pyproject.toml").exists()
    has_requirements = (cwd / "requirements.txt").exists()

    is_repo = has_git and has_readme
    is_empty = not any([has_git, has_readme, has_scripts, has_pyproject])

    if topic == "install":
        lines = _quickstart_install()
    elif topic == "github-action":
        lines = _quickstart_github_action()
    elif topic == "reproduce":
        lines = _quickstart_reproduce()
    elif topic == "eval":
        lines = _quickstart_eval()
    elif is_empty:
        lines = _quickstart_empty_dir()
    elif is_repo:
        lines = _quickstart_repo()
    else:
        lines = _quickstart_general()

    if fmt == "json":
        import json
        output = {"topic": topic, "recommendations": lines}
        print(json.dumps(output, indent=2))
    elif fmt == "markdown":
        print("\n".join(lines))
    else:
        print("\n".join(lines))

    return 0


def _quickstart_install() -> list[str]:
    """Installation quickstart."""
    return [
        "# Installation",
        "",
        "## From GitHub (recommended)",
        "",
        "```bash",
        "git clone https://github.com/Akastella/oss-paper-ci.git",
        "cd oss-paper-ci",
        "pip install -e .",
        "```",
        "",
        "## From wheel (if you have a .whl file)",
        "",
        "```bash",
        "# After building: python -m build",
        "pip install dist/oss_paper_ci-*.whl",
        "```",
        "",
        "## Verify installation",
        "",
        "```bash",
        "oss-paper-ci version",
        "oss-paper-ci quickstart",
        "```",
        "",
        "See docs/installation.md for pipx, uv, and more options.",
    ]


def _quickstart_github_action() -> list[str]:
    """GitHub Action quickstart."""
    return [
        "# GitHub Actions Integration",
        "",
        "Add to your workflow (.github/workflows/ci.yml):",
        "",
        "```yaml",
        "name: Reproducibility Check",
        "on: [push, pull_request]",
        "jobs:",
        "  check:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "      - uses: actions/checkout@v4",
        "      - uses: Akastella/oss-paper-ci@v2",
        "        with:",
        "          profile: default",
        "```",
        "",
        "See docs/github-actions.md for more options.",
    ]


def _quickstart_reproduce() -> list[str]:
    """Reproduction quickstart."""
    return [
        "# Reproduction",
        "",
        "## Dry-run (safe, no code executed)",
        "",
        "```bash",
        "oss-paper-ci reproduce . --dry-run",
        "```",
        "",
        "## Execute with capsule",
        "",
        "```bash",
        "oss-paper-ci reproduce . --execute --capsule out.zip",
        "```",
        "",
        "See docs/reproduce.md for details.",
    ]


def _quickstart_eval() -> list[str]:
    """Evaluation quickstart."""
    return [
        "# Evaluation",
        "",
        "Run the built-in evaluation corpus:",
        "",
        "```bash",
        "oss-paper-ci eval run examples/evaluation-corpus --format markdown",
        "```",
        "",
        "Compare against baseline:",
        "",
        "```bash",
        "oss-paper-ci eval compare \\",
        "  --baseline tests/golden/evaluation_summary.json \\",
        "  --current result.json",
        "```",
        "",
        "See docs/evaluation.md for details.",
    ]


def _quickstart_empty_dir() -> list[str]:
    """Quickstart for empty directory."""
    return [
        "# Welcome to oss-paper-ci!",
        "",
        "This directory appears to be empty. Here's how to get started:",
        "",
        "## 1. Try the built-in demo",
        "",
        "```bash",
        "oss-paper-ci try-demo",
        "```",
        "",
        "## 2. Create a new reproducible project",
        "",
        "```bash",
        "oss-paper-ci scaffold .",
        "```",
        "",
        "## 3. Scan an existing repository",
        "",
        "```bash",
        "oss-paper-ci scan /path/to/your/repo",
        "```",
        "",
        "Run `oss-paper-ci quickstart --topic install` for installation help.",
    ]


def _quickstart_repo() -> list[str]:
    """Quickstart for existing repo."""
    return [
        "# Quick Start for This Repository",
        "",
        "This looks like a scientific repository. Here's what to try:",
        "",
        "## 1. Scan for reproducibility",
        "",
        "```bash",
        "oss-paper-ci scan .",
        "```",
        "",
        "## 2. Full pipeline with progress",
        "",
        "```bash",
        "oss-paper-ci workbench .",
        "```",
        "",
        "## 3. Get an adoption plan",
        "",
        "```bash",
        "oss-paper-ci adopt .",
        "```",
        "",
        "## 4. Safe reproduction attempt",
        "",
        "```bash",
        "oss-paper-ci reproduce . --dry-run",
        "```",
        "",
        "Run `oss-paper-ci wizard` for guided recommendations.",
    ]


def _quickstart_general() -> list[str]:
    """General quickstart."""
    return [
        "# Quick Start",
        "",
        "## 1. Try the built-in demo",
        "",
        "```bash",
        "oss-paper-ci try-demo",
        "```",
        "",
        "## 2. Scan a repository",
        "",
        "```bash",
        "oss-paper-ci scan .",
        "```",
        "",
        "## 3. Get guided help",
        "",
        "```bash",
        "oss-paper-ci wizard",
        "oss-paper-ci guide --role author",
        "```",
        "",
        "Run `oss-paper-ci quickstart --topic` for specific guidance.",
    ]


# ── Try-demo command ───────────────────────────────────────────────────────

def _cmd_try_demo(args: argparse.Namespace) -> int:
    """Handle try-demo command."""
    import json
    import subprocess

    fmt = getattr(args, "format", "text")
    output_file = getattr(args, "output", None)
    plain = getattr(args, "plain", False)

    # Find built-in demos
    root = Path(__file__).parent.parent.parent
    demo_paper = root / "examples" / "demo-paper-repo"
    demo_reproduce = root / "demo-reproduce-repo"
    eval_corpus = root / "examples" / "evaluation-corpus"

    results = []
    results.append("# oss-paper-ci Demo")
    results.append("")
    results.append("Running built-in demos...")
    results.append("")

    # Step 1: Scan demo-paper-repo
    if demo_paper.exists():
        results.append("## Step 1: Scan demo-paper-repo")
        results.append("")
        try:
            scan_result = subprocess.run(
                ["oss-paper-ci", "scan", str(demo_paper), "--format", "json", "--no-color"],
                capture_output=True, text=True, timeout=60,
            )
            if scan_result.returncode in (0, 2):
                data = json.loads(scan_result.stdout)
                score = data.get("summary", {}).get("score", "N/A")
                status = data.get("summary", {}).get("status", "N/A")
                results.append(f"Score: {score}, Status: {status}")
            else:
                results.append("Scan completed (check output for details)")
        except Exception as e:
            results.append(f"Scan note: {e}")
        results.append("")

    # Step 2: Reproduce demo-reproduce-repo (dry-run)
    if demo_reproduce.exists():
        results.append("## Step 2: Reproduce demo-reproduce-repo (dry-run)")
        results.append("")
        try:
            repro_result = subprocess.run(
                ["oss-paper-ci", "reproduce", str(demo_reproduce), "--dry-run", "--format", "json", "--no-color"],
                capture_output=True, text=True, timeout=60,
            )
            if repro_result.returncode == 0:
                results.append("Dry-run reproduction completed successfully")
            else:
                results.append("Reproduction dry-run completed (check output for details)")
        except Exception as e:
            results.append(f"Reproduction note: {e}")
        results.append("")

    # Step 3: Eval run
    if eval_corpus.exists():
        results.append("## Step 3: Evaluation corpus")
        results.append("")
        try:
            eval_result = subprocess.run(
                ["oss-paper-ci", "eval", "run", str(eval_corpus), "--format", "json", "--no-color"],
                capture_output=True, text=True, timeout=120,
            )
            if eval_result.returncode == 0:
                data = json.loads(eval_result.stdout)
                total = data.get("total_repos", 0)
                summary = data.get("summary", {})
                results.append(f"Evaluated {total} repos: {summary}")
            else:
                results.append("Evaluation completed (check output for details)")
        except Exception as e:
            results.append(f"Evaluation note: {e}")
        results.append("")

    # Next steps
    results.append("## Next Steps")
    results.append("")
    results.append("- `oss-paper-ci scan .` - scan your own repository")
    results.append("- `oss-paper-ci wizard` - guided recommendations")
    results.append("- `oss-paper-ci quickstart --topic install` - installation help")
    results.append("- See docs/ for full documentation")

    output_text = "\n".join(results)

    # Write to file if requested
    if output_file:
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        if fmt == "text" and not plain:
            print(f"Demo output written to {output_file}")
        else:
            print(output_text)
    else:
        print(output_text)

    return 0


# ── Trust command ─────────────────────────────────────────────────────────

def _cmd_trust(args: argparse.Namespace) -> int:
    """Handle trust subcommand group."""
    sub = getattr(args, "trust_command", None)

    if sub == "audit":
        return _cmd_trust_audit(args)

    if sub == "inventory":
        return _cmd_trust_inventory(args)

    if sub == "provenance":
        return _cmd_trust_provenance(args)

    if sub == "verify-artifacts":
        return _cmd_trust_verify_artifacts(args)

    print("Usage: oss-paper-ci trust {audit|inventory|provenance|verify-artifacts}", file=sys.stderr)
    return 1


def _cmd_trust_audit(args: argparse.Namespace) -> int:
    """Run trust audit."""
    import json as json_mod

    from oss_paper_ci.trust import build_trust_report, format_trust_report_html, format_trust_report_markdown

    path = Path(getattr(args, "path", ".")).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    report = build_trust_report(path)

    if fmt == "json":
        text = json_mod.dumps(report.to_dict(), indent=2, ensure_ascii=False)
    elif fmt == "html":
        text = format_trust_report_html(report)
    else:
        text = format_trust_report_markdown(report)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Trust report written to {output}")
    else:
        print(text)
    sys.stdout.flush()

    return 0


def _cmd_trust_inventory(args: argparse.Namespace) -> int:
    """Build dependency inventory."""
    import json as json_mod

    from oss_paper_ci.inventory import build_inventory, format_inventory_markdown

    path = Path(getattr(args, "path", ".")).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    inv = build_inventory(path)

    if fmt == "json":
        text = json_mod.dumps(inv.to_dict(), indent=2, ensure_ascii=False)
    else:
        text = format_inventory_markdown(inv)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Inventory written to {output}")
    else:
        print(text)

    return 0


def _cmd_trust_provenance(args: argparse.Namespace) -> int:
    """Generate provenance manifest."""
    import json as json_mod

    from oss_paper_ci.provenance import build_provenance, format_provenance_markdown

    path = Path(getattr(args, "path", ".")).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    fmt = getattr(args, "format", "json")
    output = getattr(args, "output", None)
    include_timestamp = getattr(args, "include_timestamp", False)

    manifest = build_provenance(path, include_timestamp=include_timestamp)

    if fmt == "json":
        text = json_mod.dumps(manifest.to_dict(), indent=2, ensure_ascii=False)
    else:
        text = format_provenance_markdown(manifest)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Provenance manifest written to {output}")
    else:
        print(text)

    return 0


def _cmd_trust_verify_artifacts(args: argparse.Namespace) -> int:
    """Verify artifacts against SHA256SUMS."""
    import json as json_mod

    from oss_paper_ci.provenance import format_verification_markdown, verify_artifacts

    artifact_dir = Path(getattr(args, "artifact_dir", "")).resolve()
    if not artifact_dir.exists():
        print(f"Error: artifact directory not found: {artifact_dir}", file=sys.stderr)
        return 2

    checksums = getattr(args, "checksums", None)
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    result = verify_artifacts(artifact_dir, checksums_file=checksums)

    if fmt == "json":
        text = json_mod.dumps(result, indent=2, ensure_ascii=False)
    else:
        text = format_verification_markdown(result)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Verification written to {output}")
    else:
        print(text)

    return 0 if result["ok"] else 1


# ── Security command ─────────────────────────────────────────────────────

def _cmd_security(args: argparse.Namespace) -> int:
    """Handle security subcommand group."""
    sub = getattr(args, "security_command", None)

    if sub == "scan":
        return _cmd_security_scan(args)

    print("Usage: oss-paper-ci security scan [PATH]", file=sys.stderr)
    return 1


def _cmd_security_scan(args: argparse.Namespace) -> int:
    """Run security scan."""
    import json as json_mod

    from oss_paper_ci.security import format_security_scan_markdown, run_security_scan

    path = Path(getattr(args, "path", ".")).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    result = run_security_scan(path)

    if fmt == "json":
        text = json_mod.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    else:
        text = format_security_scan_markdown(result)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Security scan written to {output}")
    else:
        print(text)

    # Finding security issues is not a program error
    return 0


# ── Evidence command ────────────────────────────────────────────────────────

def _cmd_evidence(args: argparse.Namespace) -> int:
    """Handle evidence subcommand group."""
    sub = getattr(args, "evidence_command", None)

    if sub == "report":
        return _cmd_evidence_report(args)

    if sub == "bundle":
        return _cmd_evidence_bundle(args)

    if sub == "inspect":
        return _cmd_evidence_inspect(args)

    if sub == "verify":
        return _cmd_evidence_verify(args)

    # Default: treat `evidence .` as `evidence report .`
    if sub is None:
        # If a path was given, run report
        return _cmd_evidence_report(args)

    print("Usage: oss-paper-ci evidence {report|bundle|inspect|verify}", file=sys.stderr)
    return 1


def _cmd_evidence_report(args: argparse.Namespace) -> int:
    """Generate unified evidence report."""
    import json as json_mod

    from oss_paper_ci.evidence import (
        build_evidence_report,
        format_evidence_html,
        format_evidence_markdown,
    )

    path = Path(getattr(args, "path", ".")).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    profile = getattr(args, "profile", "reviewer")
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)
    include = getattr(args, "include", None)

    report = build_evidence_report(path, profile=profile, include_sections=include)

    if fmt == "json":
        text = json_mod.dumps(report.to_dict(), indent=2, ensure_ascii=False)
    elif fmt == "html":
        text = format_evidence_html(report)
    else:
        text = format_evidence_markdown(report)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Evidence report written to {output}")
    else:
        print(text)

    return 0


def _cmd_evidence_bundle(args: argparse.Namespace) -> int:
    """Create evidence bundle."""
    from oss_paper_ci.evidence_bundle import create_evidence_bundle

    path = Path(getattr(args, "path", ".")).resolve()
    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2

    profile = getattr(args, "profile", "reviewer")
    output = getattr(args, "output", "evidence-bundle.zip")
    include = getattr(args, "include", None)

    result = create_evidence_bundle(path, output, profile=profile, include_sections=include)

    if result.get("ok"):
        print(f"Evidence bundle created: {result['output']}")
        print(f"  Profile: {result['profile']}")
        print(f"  Files: {result['files_count']}")
        return 0
    else:
        print(f"Error creating bundle: {result}", file=sys.stderr)
        return 2


def _cmd_evidence_inspect(args: argparse.Namespace) -> int:
    """Inspect evidence bundle."""
    import json as json_mod

    from oss_paper_ci.evidence_bundle import (
        format_bundle_inspect_markdown,
        inspect_evidence_bundle,
    )

    bundle_path = Path(getattr(args, "bundle", "")).resolve()
    if not bundle_path.exists():
        print(f"Error: bundle not found: {bundle_path}", file=sys.stderr)
        return 2

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    info = inspect_evidence_bundle(bundle_path)

    if fmt == "json":
        text = json_mod.dumps(info, indent=2, ensure_ascii=False)
    else:
        text = format_bundle_inspect_markdown(info)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Inspection written to {output}")
    else:
        print(text)

    return 0


def _cmd_evidence_verify(args: argparse.Namespace) -> int:
    """Verify evidence bundle."""
    import json as json_mod

    from oss_paper_ci.evidence_bundle import (
        format_bundle_verify_markdown,
        verify_evidence_bundle,
    )

    bundle_path = Path(getattr(args, "bundle", "")).resolve()
    if not bundle_path.exists():
        print(f"Error: bundle not found: {bundle_path}", file=sys.stderr)
        return 2

    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    vr = verify_evidence_bundle(bundle_path)

    if fmt == "json":
        text = json_mod.dumps(vr.to_dict(), indent=2, ensure_ascii=False)
    else:
        text = format_bundle_verify_markdown(vr)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Verification written to {output}")
    else:
        print(text)

    return 0 if vr.ok else 1


# ── Intake command ─────────────────────────────────────────────────────────

def _cmd_intake(args: argparse.Namespace) -> int:
    """Handle intake command: repository intake analysis (read-only)."""
    from oss_paper_ci.intake import run_intake
    from oss_paper_ci.reporting.intake_report import (
        generate_intake_json,
        generate_intake_markdown,
        generate_intake_html,
    )

    input_path = getattr(args, "input", ".")
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)
    clone = getattr(args, "clone", False)

    report = run_intake(input_path, clone=clone)

    if fmt == "json":
        text = generate_intake_json(report)
    elif fmt == "html":
        text = generate_intake_html(report)
    else:
        text = generate_intake_markdown(report)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Intake report written to {output}")
    else:
        print(text)

    return 0


# ── Autoplan command ───────────────────────────────────────────────────────

def _cmd_autoplan(args: argparse.Namespace) -> int:
    """Handle autoplan command group."""
    sub = getattr(args, "autoplan_command", None)

    if sub == "generate" or sub is None:
        return _cmd_autoplan_generate(args)
    if sub == "validate":
        return _cmd_autoplan_validate(args)
    if sub == "diff":
        return _cmd_autoplan_diff(args)
    if sub == "explain":
        return _cmd_autoplan_explain(args)

    print("Usage: oss-paper-ci autoplan {generate|validate|diff|explain}", file=sys.stderr)
    return 1


def _cmd_autoplan_generate(args: argparse.Namespace) -> int:
    """Handle autoplan generate command."""
    import yaml as yaml_mod
    import json as json_mod
    from oss_paper_ci.autoplan import run_autoplan
    from oss_paper_ci.reporting.intake_report import generate_intake_markdown

    path = getattr(args, "path", ".")
    fmt = getattr(args, "format", "yaml")
    output = getattr(args, "output", None)
    write = getattr(args, "write", False)
    force = getattr(args, "force", False)
    clone = getattr(args, "clone", False)

    result = run_autoplan(path, clone=clone)

    # Show warnings
    for w in result.warnings:
        print(f"Warning: {w}", file=sys.stderr)

    if not result.candidate_config:
        print("Error: Could not generate candidate plan.", file=sys.stderr)
        return 1

    # Format output
    if fmt == "json":
        text = json_mod.dumps(result.candidate_config, indent=2, ensure_ascii=False)
    elif fmt == "markdown":
        text = _format_autoplan_markdown(result)
    else:
        text = yaml_mod.dump(result.candidate_config, default_flow_style=False, allow_unicode=True)

    # Handle --write
    if write:
        target = output or "reproducibility.yml"
        target_path = Path(target)
        if target_path.exists() and not force:
            print(f"Error: {target} already exists. Use --force to overwrite.", file=sys.stderr)
            return 1
        target_path.write_text(text, encoding="utf-8")
        print(f"Candidate config written to {target}")
    elif output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Candidate config written to {output}")
    else:
        print(text)

    return 0


def _cmd_autoplan_validate(args: argparse.Namespace) -> int:
    """Handle autoplan validate command."""
    import json as json_mod
    from oss_paper_ci.autoplan import validate_candidate_config

    config_path = getattr(args, "config", "")
    fmt = getattr(args, "format", "text")

    warnings = validate_candidate_config(config_path)

    if fmt == "json":
        print(json_mod.dumps({"valid": len(warnings) == 0, "warnings": warnings}, indent=2))
    else:
        if not warnings:
            print(f"✅ {config_path} is valid.")
        else:
            print(f"⚠️ {config_path} has {len(warnings)} issue(s):")
            for w in warnings:
                print(f"  - {w}")

    return 0 if not warnings else 1


def _cmd_autoplan_diff(args: argparse.Namespace) -> int:
    """Handle autoplan diff command."""
    import json as json_mod
    from oss_paper_ci.autoplan import diff_configs, format_diff_markdown

    old_path = getattr(args, "old", "")
    new_path = getattr(args, "new_config", "")
    fmt = getattr(args, "format", "markdown")
    output = getattr(args, "output", None)

    diff = diff_configs(old_path, new_path)

    if fmt == "json":
        text = json_mod.dumps(diff, indent=2, ensure_ascii=False)
    else:
        text = format_diff_markdown(diff)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Diff written to {output}")
    else:
        print(text)

    return 0


def _cmd_autoplan_explain(args: argparse.Namespace) -> int:
    """Handle autoplan explain command."""
    import yaml as yaml_mod
    import json as json_mod

    config_path = getattr(args, "config", "")
    fmt = getattr(args, "format", "markdown")

    p = Path(config_path)
    if not p.exists():
        print(f"Error: File not found: {config_path}", file=sys.stderr)
        return 1

    try:
        with open(p, encoding="utf-8") as f:
            data = yaml_mod.safe_load(f) or {}
    except Exception as e:
        print(f"Error: Failed to parse YAML: {e}", file=sys.stderr)
        return 1

    if fmt == "json":
        print(json_mod.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(_format_explain_markdown(data))

    return 0


def _format_autoplan_markdown(result) -> str:
    """Format autoplan result as markdown."""
    import yaml as yaml_mod
    lines: list[str] = []
    lines.append("# Candidate Reproducibility Plan")
    lines.append("")
    lines.append("⚠️ **This is an auto-generated candidate plan. Review before execution.**")
    lines.append("")

    if result.intake_report:
        conf = result.intake_report.confidence
        if conf:
            lines.append(f"**Overall Confidence:** {conf.get('overall', 0):.2f}")
            lines.append("")

    lines.append("## Candidate Config")
    lines.append("")
    lines.append("```yaml")
    lines.append(yaml_mod.dump(result.candidate_config, default_flow_style=False, allow_unicode=True).strip())
    lines.append("```")
    lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        for w in result.warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    if result.limitations:
        lines.append("## Limitations")
        for lim in result.limitations:
            lines.append(f"- {lim}")
        lines.append("")

    return "\n".join(lines)


def _format_explain_markdown(data: dict) -> str:
    """Format explain output as markdown."""
    lines: list[str] = []
    lines.append("# Reproducibility Config Explanation")
    lines.append("")

    gen = data.get("generated_by", "unknown")
    mode = data.get("generated_mode", "unknown")
    conf = data.get("confidence", "?")
    lines.append(f"- **Generated by:** {gen}")
    lines.append(f"- **Mode:** {mode}")
    lines.append(f"- **Confidence:** {conf}")
    lines.append("")

    env = data.get("environment", {})
    if env:
        lines.append("## Environment")
        lines.append(f"- **Type:** {env.get('type', '?')}")
        if env.get("install"):
            lines.append("- **Install:**")
            for cmd in env["install"]:
                lines.append(f"  - `{cmd}`")
        lines.append("")

    commands = data.get("commands", [])
    if commands:
        lines.append(f"## Commands ({len(commands)})")
        for cmd in commands:
            lines.append(f"- **{cmd.get('id', '?')}:** `{cmd.get('run', '?')}`")
        lines.append("")

    artifacts = data.get("artifacts", [])
    if artifacts:
        lines.append(f"## Artifacts ({len(artifacts)})")
        for a in artifacts:
            lines.append(f"- `{a.get('path', '?')}` ({a.get('type', '?')})")
        lines.append("")

    safety = data.get("safety", {})
    if safety:
        lines.append("## Safety")
        lines.append(f"- Network: {'allowed' if safety.get('network') else 'blocked'}")
        lines.append(f"- Shell: {'allowed' if safety.get('allow_shell') else 'blocked'}")
        lines.append(f"- Max runtime: {safety.get('max_runtime_seconds', '?')}s")
        lines.append("")

    limitations = data.get("limitations", [])
    if limitations:
        lines.append("## Limitations")
        for lim in limitations:
            lines.append(f"- {lim}")
        lines.append("")

    return "\n".join(lines)
