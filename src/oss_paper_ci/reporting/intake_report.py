"""Intake report generation in JSON, Markdown, and HTML formats."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oss_paper_ci.intake import IntakeReport


def generate_intake_json(report: IntakeReport, output_path: str | None = None) -> str:
    """Generate an intake report as JSON.

    Args:
        report: The IntakeReport object.
        output_path: If provided, write to this file.

    Returns:
        JSON string.
    """
    data = report.to_dict()
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
    return text


def generate_intake_markdown(report: IntakeReport, output_path: str | None = None) -> str:
    """Generate an intake report as Markdown.

    Args:
        report: The IntakeReport object.
        output_path: If provided, write to this file.

    Returns:
        Markdown string.
    """
    lines: list[str] = []
    lines.append("# Repository Intake Report")
    lines.append("")
    lines.append(f"**Tool:** oss-paper-ci {report.tool_version}")
    lines.append(f"**Schema:** {report.schema_version}")
    lines.append("")

    # Source
    src = report.source
    lines.append("## Source")
    lines.append("")
    lines.append(f"- **Input:** `{src.get('input', '?')}`")
    lines.append(f"- **Kind:** {src.get('kind', '?')}")
    lines.append(f"- **Cloned:** {'yes' if src.get('cloned') else 'no'}")
    lines.append("")

    # Detected information
    det = report.detected
    lines.append("## Detected Information")
    lines.append("")

    if det.languages:
        lines.append(f"**Languages:** {', '.join(det.languages)}")
        lines.append("")

    if det.ecosystems:
        lines.append("### Ecosystems")
        lines.append("")
        for eco in det.ecosystems:
            lines.append(f"- **{eco.get('display_name', eco.get('id', '?'))}**"
                         f" ({eco.get('support_level', '?')})")
        lines.append("")

    if det.environment_files:
        lines.append("### Environment Files")
        lines.append("")
        for f in det.environment_files:
            lines.append(f"- `{f}`")
        lines.append("")

    if det.workflow_files:
        lines.append("### Workflow Files")
        lines.append("")
        for f in det.workflow_files:
            lines.append(f"- `{f}`")
        lines.append("")

    if det.scripts:
        lines.append("### Scripts")
        lines.append("")
        for s in det.scripts[:20]:  # Limit display
            lines.append(f"- `{s}`")
        if len(det.scripts) > 20:
            lines.append(f"- ... and {len(det.scripts) - 20} more")
        lines.append("")

    if det.notebooks:
        lines.append("### Notebooks")
        lines.append("")
        for n in det.notebooks:
            lines.append(f"- `{n}`")
        lines.append("")

    if det.data_paths:
        lines.append("### Data Paths")
        lines.append("")
        for d in det.data_paths:
            lines.append(f"- `{d}`")
        lines.append("")

    if det.result_paths:
        lines.append("### Result Paths")
        lines.append("")
        for r in det.result_paths:
            lines.append(f"- `{r}`")
        lines.append("")

    if det.has_existing_config:
        lines.append(f"**Existing Config:** `{det.existing_config_path}`")
        lines.append("")

    # Command candidates
    if report.command_candidates:
        lines.append("## Command Candidates")
        lines.append("")
        lines.append(f"Found **{len(report.command_candidates)}** candidate command(s).")
        lines.append("")
        lines.append("| ID | Kind | Command | Source | Confidence |")
        lines.append("|-----|------|---------|--------|------------|")
        for c in report.command_candidates:
            danger = " ⚠️" if c.dangerous else ""
            cmd_display = c.command[:50] + ("..." if len(c.command) > 50 else "")
            lines.append(
                f"| {c.id} | {c.kind} | `{cmd_display}`{danger} "
                f"| {c.source}:{c.line} | {c.confidence:.2f} |"
            )
        lines.append("")

    # Confidence
    if report.confidence:
        lines.append("## Confidence Scores")
        lines.append("")
        lines.append("| Dimension | Score |")
        lines.append("|-----------|-------|")
        for k, v in report.confidence.items():
            lines.append(f"| {k} | {v:.2f} |")
        lines.append("")

    # Warnings
    if report.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in report.warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    # Limitations
    if report.limitations:
        lines.append("## Limitations")
        lines.append("")
        for lim in report.limitations:
            lines.append(f"- {lim}")
        lines.append("")

    text = "\n".join(lines)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
    return text


def generate_intake_html(report: IntakeReport, output_path: str | None = None) -> str:
    """Generate an intake report as self-contained HTML.

    Args:
        report: The IntakeReport object.
        output_path: If provided, write to this file.

    Returns:
        HTML string.
    """
    data = report.to_dict()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Intake Report - oss-paper-ci {report.tool_version}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
h2 {{ color: #2980b9; margin-top: 30px; }}
h3 {{ color: #7f8c8d; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background-color: #f2f2f2; }}
tr:nth-child(even) {{ background-color: #f9f9f9; }}
.warning {{ color: #e67e22; }}
.limitation {{ color: #7f8c8d; }}
code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
.score-table td:nth-child(2) {{ text-align: right; }}
</style>
</head>
<body>
<h1>Repository Intake Report</h1>
<p><strong>Tool:</strong> oss-paper-ci {report.tool_version} |
   <strong>Schema:</strong> {report.schema_version}</p>

<h2>Source</h2>
<ul>
<li><strong>Input:</strong> <code>{data['source'].get('input', '?')}</code></li>
<li><strong>Kind:</strong> {data['source'].get('kind', '?')}</li>
<li><strong>Cloned:</strong> {'yes' if data['source'].get('cloned') else 'no'}</li>
</ul>

<h2>Detected Information</h2>
"""

    det = data.get("detected", {})

    if det.get("languages"):
        html += f"<p><strong>Languages:</strong> {', '.join(det['languages'])}</p>\n"

    if det.get("ecosystems"):
        html += "<h3>Ecosystems</h3><ul>\n"
        for eco in det["ecosystems"]:
            html += f"<li><strong>{eco.get('display_name', eco.get('id', '?'))}</strong> ({eco.get('support_level', '?')})</li>\n"
        html += "</ul>\n"

    if det.get("environment_files"):
        html += "<h3>Environment Files</h3><ul>\n"
        for f in det["environment_files"]:
            html += f"<li><code>{f}</code></li>\n"
        html += "</ul>\n"

    if det.get("scripts"):
        html += "<h3>Scripts</h3><ul>\n"
        for s in det["scripts"][:20]:
            html += f"<li><code>{s}</code></li>\n"
        if len(det["scripts"]) > 20:
            html += f"<li>... and {len(det['scripts']) - 20} more</li>\n"
        html += "</ul>\n"

    if det.get("notebooks"):
        html += "<h3>Notebooks</h3><ul>\n"
        for n in det["notebooks"]:
            html += f"<li><code>{n}</code></li>\n"
        html += "</ul>\n"

    # Command candidates
    cmds = data.get("command_candidates", [])
    if cmds:
        html += f"<h2>Command Candidates ({len(cmds)})</h2>\n"
        html += "<table>\n<tr><th>ID</th><th>Kind</th><th>Command</th><th>Source</th><th>Confidence</th></tr>\n"
        for c in cmds:
            danger = " ⚠️" if c.get("dangerous") else ""
            cmd_display = c.get("command", "")[:50]
            html += (f"<tr><td>{c.get('id', '?')}</td><td>{c.get('kind', '?')}</td>"
                     f"<td><code>{cmd_display}</code>{danger}</td>"
                     f"<td>{c.get('source', '?')}:{c.get('line', 0)}</td>"
                     f"<td>{c.get('confidence', 0):.2f}</td></tr>\n")
        html += "</table>\n"

    # Confidence
    conf = data.get("confidence", {})
    if conf:
        html += "<h2>Confidence Scores</h2>\n"
        html += "<table class=\"score-table\">\n<tr><th>Dimension</th><th>Score</th></tr>\n"
        for k, v in conf.items():
            html += f"<tr><td>{k}</td><td>{v:.2f}</td></tr>\n"
        html += "</table>\n"

    # Warnings
    warnings = data.get("warnings", [])
    if warnings:
        html += "<h2>Warnings</h2>\n<ul>\n"
        for w in warnings:
            html += f"<li class=\"warning\">⚠️ {w}</li>\n"
        html += "</ul>\n"

    # Limitations
    limitations = data.get("limitations", [])
    if limitations:
        html += "<h2>Limitations</h2>\n<ul>\n"
        for lim in limitations:
            html += f"<li class=\"limitation\">{lim}</li>\n"
        html += "</ul>\n"

    html += "</body>\n</html>"

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
    return html
