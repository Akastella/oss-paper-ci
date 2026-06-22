"""Session report generation: Markdown, JSON, HTML."""

from __future__ import annotations

import json
from typing import Any

from oss_paper_ci.session import SessionManifest

_STATUS_EMOJI = {
    "passed": "✅",
    "failed": "❌",
    "blocked": "🚫",
    "timeout": "⏱️",
    "skipped": "⏭️",
    "unavailable": "❓",
    "pending": "⏳",
    "running": "🔄",
    "planned": "📋",
    "partial": "⚠️",
}


def generate_session_json(manifest: SessionManifest, output_path: str | None = None) -> str:
    """Generate session report as JSON."""
    data = manifest.to_dict()
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_session_markdown(manifest: SessionManifest, output_path: str | None = None) -> str:
    """Generate session report as Markdown."""
    lines: list[str] = []
    status_emoji = _STATUS_EMOJI.get(manifest.status, "")

    lines.append(f"# Reproduction Session Report {status_emoji}")
    lines.append("")
    lines.append(f"**Tool:** oss-paper-ci {manifest.tool_version}")
    lines.append(f"**Session ID:** `{manifest.session_id}`")
    lines.append(f"**Name:** {manifest.name}")
    lines.append(f"**Status:** {manifest.status}")
    lines.append("")

    # Summary
    s = manifest.summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total | {s.total} |")
    lines.append(f"| Passed | {s.passed} |")
    lines.append(f"| Failed | {s.failed} |")
    lines.append(f"| Blocked | {s.blocked} |")
    lines.append(f"| Timeout | {s.timeout} |")
    lines.append(f"| Pending | {s.pending} |")
    lines.append("")

    # Commands
    if manifest.commands:
        lines.append("## Commands")
        lines.append("")
        lines.append("| ID | Status | Duration | Exit | Command |")
        lines.append("|-----|--------|----------|------|---------|")
        for cmd in manifest.commands:
            emoji = _STATUS_EMOJI.get(cmd.status, "")
            dur = f"{cmd.duration_seconds:.1f}s" if cmd.duration_seconds > 0 else "-"
            exit_str = str(cmd.exit_code) if cmd.exit_code >= 0 else "-"
            cmd_display = cmd.command[:40] + ("..." if len(cmd.command) > 40 else "")
            lines.append(f"| {cmd.command_id} | {emoji} {cmd.status} | {dur} | {exit_str} | `{cmd_display}` |")
        lines.append("")

    # Warnings
    if manifest.warnings:
        lines.append("## Warnings")
        for w in manifest.warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    # Limitations
    if manifest.limitations:
        lines.append("## Limitations")
        for lim in manifest.limitations:
            lines.append(f"- {lim}")
        lines.append("")

    text = "\n".join(lines)
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_session_html(manifest: SessionManifest, output_path: str | None = None) -> str:
    """Generate session report as self-contained HTML."""
    status_emoji = _STATUS_EMOJI.get(manifest.status, "")
    s = manifest.summary

    # Build commands table rows
    cmd_rows = ""
    for cmd in manifest.commands:
        emoji = _STATUS_EMOJI.get(cmd.status, "")
        dur = f"{cmd.duration_seconds:.1f}s" if cmd.duration_seconds > 0 else "-"
        exit_str = str(cmd.exit_code) if cmd.exit_code >= 0 else "-"
        cmd_display = cmd.command[:50]
        cmd_rows += f"<tr><td>{cmd.command_id}</td><td>{emoji} {cmd.status}</td><td>{dur}</td><td>{exit_str}</td><td><code>{cmd_display}</code></td></tr>\n"

    # Build warnings list
    warnings_html = ""
    if manifest.warnings:
        warnings_html = "<h2>Warnings</h2><ul>\n"
        for w in manifest.warnings:
            warnings_html += f"<li class=\"warning\">⚠️ {w}</li>\n"
        warnings_html += "</ul>\n"

    # Build limitations list
    limitations_html = ""
    if manifest.limitations:
        limitations_html = "<h2>Limitations</h2><ul>\n"
        for lim in manifest.limitations:
            limitations_html += f"<li>{lim}</li>\n"
        limitations_html += "</ul>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session Report - {manifest.name}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
h2 {{ color: #2980b9; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background-color: #f2f2f2; }}
tr:nth-child(even) {{ background-color: #f9f9f9; }}
.warning {{ color: #e67e22; }}
code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
</style>
</head>
<body>
<h1>Reproduction Session Report {status_emoji}</h1>
<p><strong>Tool:</strong> oss-paper-ci {manifest.tool_version} |
   <strong>Session ID:</strong> <code>{manifest.session_id}</code> |
   <strong>Name:</strong> {manifest.name} |
   <strong>Status:</strong> {manifest.status}</p>

<h2>Summary</h2>
<table>
<tr><th>Metric</th><th>Count</th></tr>
<tr><td>Total</td><td>{s.total}</td></tr>
<tr><td>Passed</td><td>{s.passed}</td></tr>
<tr><td>Failed</td><td>{s.failed}</td></tr>
<tr><td>Blocked</td><td>{s.blocked}</td></tr>
<tr><td>Timeout</td><td>{s.timeout}</td></tr>
<tr><td>Pending</td><td>{s.pending}</td></tr>
</table>

<h2>Commands</h2>
<table>
<tr><th>ID</th><th>Status</th><th>Duration</th><th>Exit</th><th>Command</th></tr>
{cmd_rows}
</table>

{warnings_html}
{limitations_html}
</body>
</html>"""

    if output_path:
        from pathlib import Path
        Path(output_path).write_text(html, encoding="utf-8")
    return html
