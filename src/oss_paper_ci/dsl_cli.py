"""CLI implementation for oss-paper-ci dsl subcommand.

Provides: validate, normalize, graph, plan, explain, migrate
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _write_output(content: str, output: str | None) -> None:
    """Write content to file or stdout."""
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content)


def cmd_dsl_validate(path: str, fmt: str = "markdown", output: str | None = None) -> int:
    """Validate a reproducibility.yml file."""
    from oss_paper_ci.repro_dsl import load_dsl, validate_dsl, format_validation_report

    try:
        dsl = load_dsl(path)
    except Exception as e:
        print(f"Error loading DSL: {e}", file=sys.stderr)
        return 2

    result = validate_dsl(dsl)
    report = format_validation_report(result, fmt)
    _write_output(report, output)

    if not result.is_valid:
        return 2
    return 0


def cmd_dsl_normalize(path: str, fmt: str = "json", output: str | None = None) -> int:
    """Normalize a reproducibility.yml to canonical v1 JSON."""
    from oss_paper_ci.repro_dsl import load_dsl, normalize_dsl_json

    try:
        dsl = load_dsl(path)
    except Exception as e:
        print(f"Error loading DSL: {e}", file=sys.stderr)
        return 2

    if fmt == "json":
        report = normalize_dsl_json(dsl)
    else:
        report = normalize_dsl_json(dsl)

    _write_output(report, output)
    return 0


def cmd_dsl_graph(path: str, output: str | None = None) -> int:
    """Output DAG in DOT format."""
    from oss_paper_ci.repro_dsl import load_dsl, build_dag, format_dag_dot

    try:
        dsl = load_dsl(path)
    except Exception as e:
        print(f"Error loading DSL: {e}", file=sys.stderr)
        return 2

    dag = build_dsl_dag_safe(dsl)
    dot = format_dag_dot(dag)
    _write_output(dot, output)
    return 0


def cmd_dsl_plan(path: str, fmt: str = "markdown", output: str | None = None) -> int:
    """Generate execution plan from DSL."""
    from oss_paper_ci.repro_dsl import load_dsl, plan_execution, format_plan_report

    try:
        dsl = load_dsl(path)
    except Exception as e:
        print(f"Error loading DSL: {e}", file=sys.stderr)
        return 2

    plan = plan_execution(dsl, dry_run=True)

    if fmt == "json":
        report = json.dumps(plan.to_dict(), indent=2, sort_keys=False) + "\n"
    elif fmt == "html":
        from oss_paper_ci.repro_dsl import format_dag_html
        report = format_dag_html(plan.dag, title="DAG Plan")
    else:
        report = format_plan_report(plan, fmt)

    _write_output(report, output)
    return 0 if plan.is_executable else 1


def cmd_dsl_explain(path: str, fmt: str = "markdown", output: str | None = None) -> int:
    """Generate human-readable DAG report."""
    from oss_paper_ci.repro_dsl import (
        load_dsl, plan_execution, format_plan_report,
        format_dag_html, format_dag_dot,
    )

    try:
        dsl = load_dsl(path)
    except Exception as e:
        print(f"Error loading DSL: {e}", file=sys.stderr)
        return 2

    plan = plan_execution(dsl, dry_run=True)

    if fmt == "html":
        report = format_dag_html(plan.dag, title="DAG Explanation")
    elif fmt == "json":
        report = json.dumps(plan.to_dict(), indent=2, sort_keys=False) + "\n"
    else:
        report = format_plan_report(plan, "markdown")

    _write_output(report, output)
    return 0


def cmd_dsl_migrate(
    path: str,
    output: str | None = None,
    fmt: str = "json",
) -> int:
    """Migrate legacy reproducibility.yml to v1."""
    from oss_paper_ci.repro_dsl import (
        load_dsl_raw, migrate_legacy, migrate_legacy_with_report,
        normalize_dsl_json, format_migration_report,
    )

    try:
        data, version = load_dsl_raw(path)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        return 2

    if version == "v1":
        print("File is already v1 format.", file=sys.stderr)
        return 0

    if version == "unknown":
        print(f"Error: unrecognized schema version in {path}", file=sys.stderr)
        return 2

    try:
        dsl, report = migrate_legacy_with_report(data, version)
    except Exception as e:
        print(f"Error migrating: {e}", file=sys.stderr)
        return 2

    if fmt == "json":
        result = normalize_dsl_json(dsl)
    elif fmt == "markdown":
        result = format_migration_report(report, "markdown")
    else:
        result = normalize_dsl_json(dsl)

    _write_output(result, output)
    return 0


def build_dsl_dag_safe(dsl):
    """Build DAG, returning it even if invalid."""
    from oss_paper_ci.repro_dsl import build_dag
    return build_dag(dsl)
