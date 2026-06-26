"""Report formatters for Reproducibility DSL v1.

Generates markdown, JSON, HTML, and DOT reports.
HTML reports are self-contained with no external CDN.
"""

from __future__ import annotations

import html
import json
from typing import Any

from .schema import ReproDSL
from .validator import ValidationResult
from .dag import DAG
from .planner import ExecutionPlan
from .safety import SafetyReport
from .migration import MigrationReport


def _esc(value: Any) -> str:
    """HTML-escape any value for safe embedding."""
    return html.escape(str(value))


def _severity_icon(severity: str) -> str:
    """Return a text icon for a severity level."""
    icons = {
        "error": "[ERROR]",
        "warning": "[WARN]",
        "info": "[INFO]",
        "blocked": "[BLOCKED]",
    }
    return icons.get(severity, f"[{severity.upper()}]")


# ---------------------------------------------------------------------------
# Validation report
# ---------------------------------------------------------------------------


def format_validation_report(result: ValidationResult, fmt: str = "markdown") -> str:
    """Format a validation result as markdown or JSON."""
    if fmt == "json":
        return json.dumps(result.to_dict(), indent=2) + "\n"
    return _validation_markdown(result)


def _validation_markdown(result: ValidationResult) -> str:
    lines: list[str] = []
    lines.append("# Validation Report")
    lines.append("")

    status = "PASS" if result.is_valid else "FAIL"
    lines.append(f"**Status:** {status}")
    lines.append(f"**Fields checked:** {result.checked_fields}")
    lines.append(f"**Errors:** {len(result.errors)}")
    lines.append(f"**Warnings:** {len(result.warnings)}")
    lines.append("")

    if not result.findings:
        lines.append("No findings.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Findings")
    lines.append("")
    lines.append("| Severity | Category | Field | Message |")
    lines.append("|----------|----------|-------|---------|")
    for f in result.findings:
        sev = f.severity.upper()
        cat = f.category
        fp = f.field_path or "-"
        msg = f.message.replace("|", "\\|")
        lines.append(f"| {sev} | {cat} | `{fp}` | {msg} |")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Execution plan report
# ---------------------------------------------------------------------------


def format_plan_report(plan: ExecutionPlan, fmt: str = "markdown") -> str:
    """Format an execution plan as markdown or JSON."""
    if fmt == "json":
        return json.dumps(plan.to_dict(), indent=2) + "\n"
    return _plan_markdown(plan)


def _plan_markdown(plan: ExecutionPlan) -> str:
    lines: list[str] = []
    lines.append("# Execution Plan")
    lines.append("")

    executable = "Yes" if plan.is_executable else "No"
    lines.append(f"**Executable:** {executable}")
    lines.append(f"**Dry run:** {plan.dry_run}")
    lines.append(f"**Total timeout:** {plan.total_timeout}s")
    lines.append(f"**Parallel groups:** {plan.parallel_group_count}")
    lines.append(f"**Steps:** {len(plan.steps)}")
    lines.append("")

    # Summary counts
    ready = len(plan.ready_steps)
    blocked = len(plan.blocked_steps)
    skipped = len(plan.skipped_steps)
    lines.append(f"- Ready: {ready}")
    lines.append(f"- Blocked: {blocked}")
    lines.append(f"- Skipped: {skipped}")
    lines.append("")

    # Warnings
    if plan.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in sorted(plan.warnings):
            lines.append(f"- {w}")
        lines.append("")

    # DAG summary
    lines.append("## DAG Summary")
    lines.append("")
    lines.append(f"- **Topological order:** `{' -> '.join(plan.dag.topological_order)}`")
    lines.append(f"- **Critical path:** `{' -> '.join(plan.dag.critical_path)}`")
    lines.append(f"- **Critical path duration:** {plan.dag.critical_path_duration}s")
    if plan.dag.cycles:
        lines.append(f"- **Cycles:** {len(plan.dag.cycles)} detected")
    if plan.dag.missing_deps:
        lines.append(f"- **Missing deps:** {len(plan.dag.missing_deps)} step(s)")
    lines.append("")

    # Steps table
    lines.append("## Steps")
    lines.append("")
    lines.append("| # | Step ID | Status | Parallel Group | Timeout | Dependencies |")
    lines.append("|---|---------|--------|----------------|---------|--------------|")
    for i, s in enumerate(plan.steps):
        deps = ", ".join(sorted(s.needs)) if s.needs else "-"
        extra = ""
        if s.skip_reason:
            extra = f" ({s.skip_reason})"
        lines.append(
            f"| {i + 1} | `{s.step_id}` | {s.status}{extra} | {s.parallel_group} | {s.timeout}s | `{deps}` |"
        )
    lines.append("")

    # Safety summary
    lines.append("## Safety")
    lines.append("")
    lines.append(f"- **Level:** {plan.safety.safety_level}")
    lines.append(f"- **Blocked commands:** {len(plan.safety.blocked_commands)}")
    lines.append(f"- **Requires network:** {plan.safety.requires_network}")
    lines.append(f"- **Requires install:** {plan.safety.requires_install}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DAG DOT format
# ---------------------------------------------------------------------------


def format_dag_dot(dag: DAG) -> str:
    """Format a DAG as DOT graph language."""
    lines: list[str] = []
    lines.append("digraph DAG {")
    lines.append("    rankdir=TB;")
    lines.append("    node [shape=box, style=\"filled,rounded\", fontname=\"Helvetica\"];")
    lines.append("    edge [fontname=\"Helvetica\", fontsize=10];")
    lines.append("")

    # Nodes -- sorted for determinism
    critical_set = set(dag.critical_path)
    for node_id in sorted(dag.nodes):
        node = dag.nodes[node_id]
        label = f"{node_id}\\n{node.timeout}s"
        attrs = [f'label="{_dot_escape(label)}"']
        if node_id in critical_set:
            attrs.append("fillcolor=\"#ffcccc\"")
        elif node.level >= 0:
            attrs.append("fillcolor=\"#ccffcc\"")
        else:
            attrs.append("fillcolor=\"#cccccc\"")
        lines.append(f"    {_dot_id(node_id)} [{', '.join(attrs)}];")
    lines.append("")

    # Edges -- sorted for determinism
    for src, dst in sorted(dag.edges):
        edge_attrs: list[str] = []
        if src in critical_set and dst in critical_set:
            edge_attrs.append("color=\"red\"")
            edge_attrs.append("penwidth=2")
        attr_str = ""
        if edge_attrs:
            attr_str = f" [{', '.join(edge_attrs)}]"
        lines.append(f"    {_dot_id(src)} -> {_dot_id(dst)}{attr_str};")

    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _dot_escape(value: str) -> str:
    """Escape a string for DOT labels."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _dot_id(value: str) -> str:
    """Quote a node ID for DOT."""
    if value.isalnum() or all(c.isalnum() or c == "_" for c in value):
        return value
    return f'"{_dot_escape(value)}"'


# ---------------------------------------------------------------------------
# DAG HTML report
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,sans-serif;background:#f5f5f5;color:#222;padding:24px;line-height:1.5}}
h1{{font-size:1.5rem;margin-bottom:8px}}
h2{{font-size:1.1rem;margin:16px 0 8px;border-bottom:1px solid #ccc;padding-bottom:4px}}
table{{border-collapse:collapse;width:100%;margin:8px 0 16px;font-size:0.9rem}}
th,td{{border:1px solid #ccc;padding:6px 10px;text-align:left}}
th{{background:#e8e8e8;font-weight:600}}
tr:nth-child(even){{background:#fafafa}}
.code{{font-family:monospace;font-size:0.85rem;background:#f0f0f0;padding:2px 5px;border-radius:3px}}
.badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.78rem;font-weight:600}}
.badge-error{{background:#fdd;color:#900}}
.badge-warning{{background:#ffd;color:#660}}
.badge-ok{{background:#dfd;color:#060}}
.badge-blocked{{background:#fdd;color:#900}}
.summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:12px 0}}
.summary-card{{background:#fff;border:1px solid #ddd;border-radius:6px;padding:12px;text-align:center}}
.summary-card .value{{font-size:1.4rem;font-weight:700}}
.summary-card .label{{font-size:0.8rem;color:#666}}
.critical{{background:#ffecec}}
.graph-container{{background:#fff;border:1px solid #ddd;border-radius:6px;padding:16px;margin:12px 0;overflow-x:auto}}
.graph-container svg{{max-width:100%;height:auto}}
</style>
</head>
<body>
<h1>{title_escaped}</h1>
{body}
</body>
</html>
"""


def format_dag_html(dag: DAG, title: str = "DAG Report") -> str:
    """Format a DAG as a self-contained HTML report.

    Requirements satisfied:
    - Single file, no external CDN
    - All user content HTML-escaped
    - CSS inline, JS inline
    - No absolute paths
    """
    parts: list[str] = []

    # Summary cards
    parts.append(_html_summary_cards(dag))

    # Parallel groups table
    parts.append(_html_parallel_groups(dag))

    # Critical path
    parts.append(_html_critical_path(dag))

    # Nodes table
    parts.append(_html_nodes_table(dag))

    # Edges table
    parts.append(_html_edges_table(dag))

    # Cycles / missing deps warnings
    if dag.cycles or dag.missing_deps or dag.warnings:
        parts.append(_html_warnings(dag))

    body = "\n".join(parts)
    return _HTML_TEMPLATE.format(title=_esc(title), title_escaped=_esc(title), body=body)


def _html_summary_cards(dag: DAG) -> str:
    valid_icon = "&#10003;" if dag.is_valid else "&#10007;"
    valid_cls = "badge-ok" if dag.is_valid else "badge-error"
    valid_text = "Valid" if dag.is_valid else "Invalid"

    cards = [
        ("Nodes", str(len(dag.nodes))),
        ("Edges", str(len(dag.edges))),
        ("Parallel Groups", str(len(dag.parallel_groups))),
        ("Critical Path Duration", f"{dag.critical_path_duration}s"),
        (
            "DAG Status",
            f'<span class="badge {valid_cls}">{valid_icon} {_esc(valid_text)}</span>',
        ),
    ]

    inner = ""
    for label, value in cards:
        inner += (
            f'<div class="summary-card">'
            f'<div class="value">{value}</div>'
            f'<div class="label">{_esc(label)}</div>'
            f"</div>\n"
        )
    return f'<div class="summary-grid">\n{inner}</div>\n'


def _html_parallel_groups(dag: DAG) -> str:
    if not dag.parallel_groups:
        return ""
    parts = ["<h2>Parallel Groups</h2>\n<table>\n"]
    parts.append("<tr><th>Group</th><th>Steps</th></tr>\n")
    for i, group in enumerate(dag.parallel_groups):
        steps_str = ", ".join(f'<span class="code">{_esc(s)}</span>' for s in group)
        parts.append(f"<tr><td>{i}</td><td>{steps_str}</td></tr>\n")
    parts.append("</table>\n")
    return "".join(parts)


def _html_critical_path(dag: DAG) -> str:
    parts = ["<h2>Critical Path</h2>\n"]
    if not dag.critical_path:
        parts.append("<p>No critical path (empty DAG or all nodes in cycles).</p>\n")
        return "".join(parts)
    steps_str = " &rarr; ".join(
        f'<span class="code">{_esc(s)}</span>' for s in dag.critical_path
    )
    parts.append(f"<p>{steps_str}</p>\n")
    parts.append(f'<p><strong>Total duration:</strong> {dag.critical_path_duration}s</p>\n')
    return "".join(parts)


def _html_nodes_table(dag: DAG) -> str:
    critical_set = set(dag.critical_path)
    parts = ["<h2>Nodes</h2>\n<table>\n"]
    parts.append(
        "<tr><th>Step ID</th><th>Command</th><th>In</th>"
        "<th>Out</th><th>Depth</th><th>Level</th><th>Timeout</th></tr>\n"
    )
    for node_id in sorted(dag.nodes):
        n = dag.nodes[node_id]
        row_cls = ' class="critical"' if node_id in critical_set else ""
        parts.append(
            f"<tr{row_cls}>"
            f'<td class="code">{_esc(n.step_id)}</td>'
            f"<td>{_esc(n.command)}</td>"
            f"<td>{n.in_degree}</td>"
            f"<td>{n.out_degree}</td>"
            f"<td>{n.depth}</td>"
            f"<td>{n.level}</td>"
            f"<td>{n.timeout}s</td>"
            f"</tr>\n"
        )
    parts.append("</table>\n")
    return "".join(parts)


def _html_edges_table(dag: DAG) -> str:
    if not dag.edges:
        return ""
    parts = ["<h2>Edges</h2>\n<table>\n"]
    parts.append("<tr><th>#</th><th>From</th><th>To</th></tr>\n")
    for i, (src, dst) in enumerate(sorted(dag.edges)):
        parts.append(
            f"<tr>"
            f"<td>{i + 1}</td>"
            f'<td class="code">{_esc(src)}</td>'
            f'<td class="code">{_esc(dst)}</td>'
            f"</tr>\n"
        )
    parts.append("</table>\n")
    return "".join(parts)


def _html_warnings(dag: DAG) -> str:
    parts = ["<h2>Warnings</h2>\n"]
    items: list[str] = []
    for cycle in dag.cycles:
        cycle_str = " &rarr; ".join(_esc(c) for c in cycle)
        items.append(f"<li>Cycle: {cycle_str}</li>")
    for step_id in sorted(dag.missing_deps):
        deps = ", ".join(
            f'<span class="code">{_esc(d)}</span>'
            for d in sorted(dag.missing_deps[step_id])
        )
        items.append(
            f"<li>Missing dependencies for "
            f'<span class="code">{_esc(step_id)}</span>: {deps}</li>'
        )
    for w in sorted(dag.warnings):
        items.append(f"<li>{_esc(w)}</li>")
    if items:
        parts.append("<ul>\n" + "\n".join(items) + "\n</ul>\n")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Normalized JSON
# ---------------------------------------------------------------------------


def format_normalized_json(dsl: ReproDSL, indent: int = 2) -> str:
    """Format normalized DSL as JSON."""
    return json.dumps(dsl.to_dict(), indent=indent, sort_keys=False) + "\n"


# ---------------------------------------------------------------------------
# Migration report
# ---------------------------------------------------------------------------


def format_migration_report(report: MigrationReport, fmt: str = "markdown") -> str:
    """Format a migration report as markdown or JSON."""
    if fmt == "json":
        return json.dumps(report.to_dict(), indent=2) + "\n"
    return _migration_markdown(report)


def _migration_markdown(report: MigrationReport) -> str:
    lines: list[str] = []
    lines.append("# Migration Report")
    lines.append("")
    lines.append(f"**Source version:** {report.source_version}")
    lines.append(f"**Target version:** v{report.target_version}")
    lines.append("")
    lines.append("## Converted")
    lines.append("")
    lines.append(f"- Steps: {report.steps_converted}")
    lines.append(f"- Datasets: {report.datasets_converted}")
    lines.append(f"- Metrics: {report.metrics_converted}")
    lines.append(f"- Artifacts: {report.artifacts_converted}")
    lines.append("")

    if report.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in sorted(report.warnings):
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Safety report
# ---------------------------------------------------------------------------


def format_safety_report(report: SafetyReport, fmt: str = "markdown") -> str:
    """Format a safety report as markdown or JSON."""
    if fmt == "json":
        return json.dumps(report.to_dict(), indent=2) + "\n"
    return _safety_markdown(report)


def _safety_markdown(report: SafetyReport) -> str:
    lines: list[str] = []
    lines.append("# Safety Report")
    lines.append("")
    lines.append(f"**Safety level:** {report.safety_level}")
    lines.append(f"**Blocked commands:** {len(report.blocked_commands)}")
    lines.append(f"**Requires explicit execute:** {report.requires_explicit_execute}")
    lines.append(f"**Requires network:** {report.requires_network}")
    lines.append(f"**Requires install:** {report.requires_install}")
    lines.append("")

    if report.blocked_commands:
        lines.append("## Blocked Commands")
        lines.append("")
        for cmd in sorted(report.blocked_commands):
            lines.append(f"- `{cmd}`")
        lines.append("")

    if report.findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("| Severity | Category | Step | Message |")
        lines.append("|----------|----------|------|---------|")
        for f in report.findings:
            sev = f.severity.upper()
            cat = f.category
            sid = f.step_id or "-"
            msg = f.message.replace("|", "\\|")
            lines.append(f"| {sev} | {cat} | `{sid}` | {msg} |")
        lines.append("")

    return "\n".join(lines)
