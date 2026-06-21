"""Report generation for the reproduction orchestrator.

Generates Markdown, JSON, and HTML reports from ReproductionRun data.
"""

from __future__ import annotations

import json
from typing import Any

from oss_paper_ci import __version__


def generate_repro_run_markdown(run: Any) -> str:
    """Generate a Markdown report from a ReproductionRun."""
    lines = [
        "# Reproduction Run Report",
        "",
        f"**Version:** {__version__}",
        f"**Status:** {run.overall_status}",
        f"**Dry run:** {'Yes' if run.dry_run else 'No'}",
        f"**Started:** {run.started_at}",
        f"**Finished:** {run.finished_at}",
        f"**Sandbox:** {run.sandbox_type}",
        "",
    ]

    if run.error:
        lines.append(f"**Error:** {run.error}")
        lines.append("")

    # Commands
    if run.command_results:
        lines.append("## Command Results")
        lines.append("")
        lines.append("| ID | Command | Status | Exit | Duration |")
        lines.append("|-----|---------|--------|------|----------|")
        for cr in run.command_results:
            status_icon = {
                "success": "✅",
                "failed": "❌",
                "blocked": "🚫",
                "timeout": "⏱️",
            }.get(cr.status, "❓")
            exit_str = str(cr.exit_code) if cr.exit_code >= 0 else "—"
            dur_str = f"{cr.duration_seconds:.1f}s" if cr.duration_seconds else "—"
            cmd_display = cr.command[:50] + "..." if len(cr.command) > 50 else cr.command
            lines.append(
                f"| `{cr.command_id}` | `{cmd_display}` | "
                f"{status_icon} {cr.status} | {exit_str} | {dur_str} |"
            )
        lines.append("")

        # Command details
        for cr in run.command_results:
            if cr.status not in ("success",) or cr.stdout_excerpt or cr.stderr_excerpt:
                lines.append(f"### {cr.command_id}")
                lines.append("")
                if cr.block_reason:
                    lines.append(f"**Block reason:** {cr.block_reason}")
                if cr.stdout_excerpt:
                    lines.append("<details><summary>stdout</summary>")
                    lines.append("")
                    lines.append("```")
                    lines.append(cr.stdout_excerpt)
                    lines.append("```")
                    lines.append("</details>")
                    lines.append("")
                if cr.stderr_excerpt:
                    lines.append("<details><summary>stderr</summary>")
                    lines.append("")
                    lines.append("```")
                    lines.append(cr.stderr_excerpt)
                    lines.append("```")
                    lines.append("</details>")
                    lines.append("")

    # Artifacts
    if run.artifact_validation:
        av = run.artifact_validation
        lines.append("## Artifacts")
        lines.append("")
        lines.append(f"- **Expected:** {av.total}")
        lines.append(f"- **Found:** {av.found}")
        lines.append(f"- **Missing:** {av.missing}")
        lines.append("")
        if av.artifacts:
            lines.append("| Path | Exists | Size | SHA256 |")
            lines.append("|------|--------|------|--------|")
            for a in av.artifacts:
                exists = "✅" if a.exists else "❌"
                size = f"{a.size_bytes:,}" if a.exists else "—"
                sha = a.sha256[:16] + "..." if a.sha256 else "—"
                lines.append(f"| `{a.path}` | {exists} | {size} | {sha} |")
            lines.append("")

    # Metrics
    if run.metric_validation:
        mv = run.metric_validation
        lines.append("## Metrics")
        lines.append("")
        lines.append(f"- **Checked:** {mv.total}")
        lines.append(f"- **In range:** {mv.in_range}")
        lines.append(f"- **Out of range:** {mv.out_of_range}")
        lines.append(f"- **Errors:** {mv.errors}")
        lines.append("")
        if mv.checks:
            lines.append("| Key | Value | Min | Max | Status |")
            lines.append("|-----|-------|-----|-----|--------|")
            for c in mv.checks:
                status = "✅" if c.in_range else "❌"
                min_val = c.expected_min if c.expected_min is not None else "—"
                max_val = c.expected_max if c.expected_max is not None else "—"
                val = c.actual_value if c.actual_value is not None else "—"
                lines.append(
                    f"| `{c.key}` | {val} | {min_val} | {max_val} | {status} |"
                )
            lines.append("")

    # Warnings
    if run.warnings:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for w in run.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Disclaimer
    lines.append("---")
    lines.append("")
    lines.append(
        "*This report documents an attempted reproduction run. "
        "It does not prove scientific correctness or guarantee reproducibility.*"
    )

    return "\n".join(lines)


def generate_repro_run_json(run: Any) -> str:
    """Generate a JSON report from a ReproductionRun."""
    return json.dumps(run.to_dict(), indent=2, ensure_ascii=False)


def generate_repro_run_html(run: Any) -> str:
    """Generate an HTML report from a ReproductionRun."""
    status_color = {
        "success": "#10b981",
        "partial": "#f59e0b",
        "failed": "#ef4444",
        "error": "#ef4444",
        "dry_run": "#6b7280",
    }.get(run.overall_status, "#6b7280")

    cmd_rows = ""
    for cr in run.command_results:
        bg = "#f0fdf4" if cr.status == "success" else (
            "#fef2f2" if cr.status in ("failed", "timeout", "blocked") else "#fff"
        )
        cmd_rows += f"""
        <tr style="background:{bg}">
            <td><code>{_escape(cr.command_id)}</code></td>
            <td><code>{_escape(cr.command[:60])}</code></td>
            <td>{cr.status}</td>
            <td>{cr.exit_code}</td>
            <td>{cr.duration_seconds:.1f}s</td>
        </tr>"""

    art_rows = ""
    if run.artifact_validation:
        for a in run.artifact_validation.artifacts:
            exists = "✅" if a.exists else "❌"
            art_rows += f"""
            <tr>
                <td><code>{_escape(a.path)}</code></td>
                <td>{exists}</td>
                <td>{a.size_bytes:,}</td>
                <td><code>{a.sha256[:16]}...</code></td>
            </tr>"""

    met_rows = ""
    if run.metric_validation:
        for c in run.metric_validation.checks:
            status = "✅" if c.in_range else "❌"
            met_rows += f"""
            <tr>
                <td><code>{_escape(c.key)}</code></td>
                <td>{c.actual_value}</td>
                <td>{c.expected_min if c.expected_min is not None else '—'}</td>
                <td>{c.expected_max if c.expected_max is not None else '—'}</td>
                <td>{status}</td>
            </tr>"""

    warnings_html = ""
    if run.warnings:
        items = "".join(f"<li>{_escape(w)}</li>" for w in run.warnings)
        warnings_html = f"<h2>⚠️ Warnings</h2><ul>{items}</ul>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reproduction Run Report</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  max-width:900px;margin:0 auto;padding:24px;background:#f9fafb;color:#111}}
h1{{font-size:1.5rem;margin-bottom:16px}}
h2{{font-size:1.2rem;margin:24px 0 12px;color:#374151}}
.status{{display:inline-block;padding:4px 12px;border-radius:4px;
  color:#fff;font-weight:600;background:{status_color}}}
table{{width:100%;border-collapse:collapse;margin:8px 0 16px;font-size:0.85rem}}
th,td{{padding:6px 8px;border:1px solid #e5e7eb;text-align:left}}
th{{background:#f3f4f6}}
code{{background:#f3f4f6;padding:1px 4px;border-radius:3px;font-size:0.85rem}}
.disclaimer{{margin-top:32px;padding:12px;background:#fffbeb;border:1px solid #fcd34d;
  border-radius:6px;font-size:0.85rem;color:#92400e}}
ul{{margin:8px 0 8px 24px}}
</style>
</head>
<body>
<h1>Reproduction Run Report</h1>
<p><span class="status">{run.overall_status}</span></p>
<p><strong>Dry run:</strong> {'Yes' if run.dry_run else 'No'}</p>
<p><strong>Started:</strong> {_escape(run.started_at)}</p>
<p><strong>Finished:</strong> {_escape(run.finished_at)}</p>
<p><strong>Sandbox:</strong> {_escape(run.sandbox_type)}</p>

{"<p><strong>Error:</strong> " + _escape(run.error) + "</p>" if run.error else ""}

{"<h2>Command Results</h2><table><tr><th>ID</th><th>Command</th><th>Status</th><th>Exit</th><th>Duration</th></tr>" + cmd_rows + "</table>" if run.command_results else ""}

{"<h2>Artifacts</h2><p>Expected: " + str(run.artifact_validation.total) + " | Found: " + str(run.artifact_validation.found) + " | Missing: " + str(run.artifact_validation.missing) + "</p><table><tr><th>Path</th><th>Exists</th><th>Size</th><th>SHA256</th></tr>" + art_rows + "</table>" if run.artifact_validation else ""}

{"<h2>Metrics</h2><p>Checked: " + str(run.metric_validation.total) + " | In range: " + str(run.metric_validation.in_range) + "</p><table><tr><th>Key</th><th>Value</th><th>Min</th><th>Max</th><th>Status</th></tr>" + met_rows + "</table>" if run.metric_validation else ""}

{warnings_html}

<div class="disclaimer">
This report documents an attempted reproduction run. It does not prove
scientific correctness or guarantee reproducibility.
</div>
</body>
</html>"""


def _escape(s: str) -> str:
    """Escape HTML special characters."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
