"""HTML report generation for oss-paper-ci scan results."""

from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Any

from ..models import Report


def _escape(text: str) -> str:
    """HTML-escape text and truncate if too long."""
    escaped = html.escape(text)
    if len(escaped) > 500:
        return escaped[:497] + "..."
    return escaped


def _score_color(score: int) -> str:
    """Return CSS color for score."""
    if score >= 80:
        return "#22c55e"
    if score >= 50:
        return "#eab308"
    return "#ef4444"


def _status_badge(status: str) -> str:
    """Return HTML badge for status."""
    colors = {"pass": "#22c55e", "warn": "#eab308", "fail": "#ef4444"}
    color = colors.get(status, "#6b7280")
    return f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:0.85em">{html.escape(status)}</span>'


def generate_html_report(report: Report) -> str:
    """Generate a single-file HTML report from a scan Report."""
    checks = report.checks or []
    summary = report.summary

    # Group by severity
    blocking = [c for c in checks if c.severity.value == "error" and c.status.value == "fail"]
    important = [c for c in checks if c.severity.value == "warning" and c.status.value == "fail"]
    advisory = [c for c in checks if c.status.value == "warn"]
    passed = [c for c in checks if c.status.value == "pass"]

    score = summary.score if summary else 0
    status = summary.status if summary else "unknown"
    tool_version = report.version or "unknown"
    profile_name = report.policy.profile if report.policy else "default"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Build findings table rows
    rows = ""
    for c in checks:
        status_cls = {"pass": "pass", "fail": "fail", "warn": "warn"}.get(c.status.value, "")
        rows += f"""<tr class="{status_cls}" data-severity="{html.escape(c.severity.value)}">
<td><code>{_escape(c.id)}</code></td>
<td>{_escape(c.title)}</td>
<td>{_escape(c.severity.value)}</td>
<td>{_status_badge(c.status.value)}</td>
<td>{_escape(c.message)}</td>
</tr>
"""

    # Build recommendations
    recommendations = ""
    for c in checks:
        if c.recommendation and c.status.value != "pass":
            recommendations += f"<li><strong>{_escape(c.id)}</strong>: {_escape(c.recommendation)}</li>\n"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>oss-paper-ci report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; color: #1f2937; line-height: 1.5; }}
h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 0.3em; }}
h2 {{ margin-top: 1.5em; }}
.score {{ font-size: 3em; font-weight: bold; color: {_score_color(score)}; }}
.summary {{ display: flex; gap: 2em; margin: 1em 0; flex-wrap: wrap; }}
.summary div {{ background: #f9fafb; padding: 1em; border-radius: 8px; min-width: 120px; text-align: center; }}
.summary .label {{ font-size: 0.85em; color: #6b7280; }}
table {{ width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 0.9em; }}
th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #e5e7eb; }}
th {{ background: #f3f4f6; }}
tr.fail td {{ background: #fef2f2; }}
tr.warn td {{ background: #fffbeb; }}
code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }}
.recs {{ background: #f9fafb; padding: 1em; border-radius: 8px; }}
.recs li {{ margin: 0.3em 0; }}
.metadata {{ color: #6b7280; font-size: 0.85em; margin-top: 2em; }}
.metadata p {{ margin: 0.2em 0; }}
.footer {{ margin-top: 2em; padding-top: 1em; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 0.85em; }}
.anchor {{ scroll-margin-top: 1em; }}
</style>
</head>
<body>
<h1 id="top">Reproducibility Report</h1>

<div class="metadata">
<p><strong>Tool:</strong> oss-paper-ci {html.escape(tool_version)}</p>
<p><strong>Profile:</strong> {html.escape(profile_name)}</p>
<p><strong>Generated:</strong> {html.escape(timestamp)}</p>
</div>

<div class="summary" id="summary">
<div><div class="label">Score</div><div class="score">{score}</div></div>
<div><div class="label">Status</div>{_status_badge(status)}</div>
<div><div class="label">Checks</div><div>{len(checks)}</div></div>
<div><div class="label"><a href="#blocking">Blocking</a></div><div style="color:#ef4444;font-weight:bold">{len(blocking)}</div></div>
<div><div class="label"><a href="#important">Important</a></div><div style="color:#eab308;font-weight:bold">{len(important)}</div></div>
<div><div class="label"><a href="#advisory">Advisory</a></div><div style="color:#6b7280">{len(advisory)}</div></div>
</div>

<h2 id="findings" class="anchor">Findings</h2>
<table>
<tr><th>ID</th><th>Title</th><th>Severity</th><th>Status</th><th>Message</th></tr>
{rows}
</table>

{"<h2 id='recommendations' class='anchor'>Recommendations</h2><div class='recs'><ol>" + recommendations + "</ol></div>" if recommendations else ""}

<div class="footer">
Generated by <a href="https://github.com/Akastella/oss-paper-ci">oss-paper-ci</a> {html.escape(tool_version)}
&mdash; {html.escape(timestamp)}
</div>
</body>
</html>"""
