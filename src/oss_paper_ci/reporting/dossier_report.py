"""Dossier report generation.

Generates Markdown, JSON, HTML, issue, and PR comment formats
from a Dossier object.
"""

from __future__ import annotations

import html as html_mod
import json
from typing import TYPE_CHECKING, Any

from oss_paper_ci.i18n_templates import get_template

if TYPE_CHECKING:
    from oss_paper_ci.dossier import Dossier


def generate_dossier_json(dossier: Dossier, output_path: str | None = None) -> str:
    """Generate JSON dossier."""
    text = json.dumps(dossier.to_dict(), indent=2, ensure_ascii=False) + "\n"
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_dossier_markdown(dossier: Dossier, output_path: str | None = None) -> str:
    """Generate Markdown dossier."""
    tmpl_lang = dossier.language
    lines: list[str] = []

    lines.append(f"# {get_template(tmpl_lang, 'title')}\n")

    # Disclaimer
    lines.append(f"> {get_template(tmpl_lang, 'disclaimer')}\n")

    # Executive summary
    es = dossier.executive_summary
    lines.append(f"## {get_template(tmpl_lang, 'executive_summary')}\n")
    lines.append(f"{es.get('plain_language', '')}\n")
    if es.get("score") is not None:
        lines.append(f"**{get_template(tmpl_lang, 'status')}:** {es.get('status', '?')} | "
                     f"**Score:** {es.get('score', '?')}/100 | "
                     f"**{get_template(tmpl_lang, 'confidence_low')}:** {es.get('confidence', '?')}\n")

    # Audience notes
    if dossier.audience_notes:
        for note in dossier.audience_notes:
            lines.append(f"- {note}")
        lines.append("")

    # Evidence map
    if dossier.evidence_map:
        lines.append(f"## {get_template(tmpl_lang, 'evidence_map')}\n")
        lines.append(f"| {get_template(tmpl_lang, 'category')} | {get_template(tmpl_lang, 'item')} | "
                     f"{get_template(tmpl_lang, 'status')} | {get_template(tmpl_lang, 'why_it_matters')} |")
        lines.append("|------|------|--------|------------|")
        for e in dossier.evidence_map:
            status_label = get_template(tmpl_lang, e.status)
            lines.append(f"| {e.category} | {e.item} | {status_label} | {e.why_it_matters} |")
        lines.append("")

    # Risk register
    if dossier.risk_register:
        lines.append(f"## {get_template(tmpl_lang, 'risk_register')}\n")
        lines.append(f"| {get_template(tmpl_lang, 'severity')} | {get_template(tmpl_lang, 'item')} | "
                     f"{get_template(tmpl_lang, 'impact')} | {get_template(tmpl_lang, 'mitigation')} |")
        lines.append("|--------|------|--------|------------|")
        for r in dossier.risk_register:
            lines.append(f"| {r.severity} | {r.title} | {r.impact} | {r.mitigation} |")
        lines.append("")

    # Remediation plan
    if dossier.remediation_plan:
        lines.append(f"## {get_template(tmpl_lang, 'remediation_plan')}\n")
        for item in dossier.remediation_plan:
            blocking_tag = f" **[{get_template(tmpl_lang, 'blocking')}!]**" if item.blocking else ""
            lines.append(f"### [{item.priority}] {item.action}{blocking_tag}\n")
            lines.append(f"**{get_template(tmpl_lang, 'rationale')}:** {item.rationale}\n")
            if item.suggested_file:
                lines.append(f"**Suggested file:** `{item.suggested_file}`\n")
            if item.command_to_verify:
                lines.append(f"**Verify:** `{item.command_to_verify}`\n")
            lines.append(f"**{get_template(tmpl_lang, 'effort')}:** {item.estimated_effort}\n")

    # Next steps
    if dossier.next_steps:
        lines.append(f"## {get_template(tmpl_lang, 'next_steps')}\n")
        for step in dossier.next_steps:
            lines.append(f"- {step}")
        lines.append("")

    # Non-claims
    if dossier.non_claims:
        lines.append(f"## {get_template(tmpl_lang, 'non_claims')}\n")
        for claim in dossier.non_claims:
            lines.append(f"- {claim}")
        lines.append("")

    lines.append(f"---\n*{get_template(tmpl_lang, 'generated_by')}*\n")

    text = "\n".join(lines)
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_dossier_html(dossier: Dossier, output_path: str | None = None) -> str:
    """Generate HTML dossier."""
    tmpl_lang = dossier.language
    h = html_mod.escape

    es = dossier.executive_summary
    title = get_template(tmpl_lang, "title")

    # Evidence map rows
    evidence_rows = ""
    for e in dossier.evidence_map:
        status_label = get_template(tmpl_lang, e.status)
        evidence_rows += (
            f"<tr><td>{h(e.category)}</td><td>{h(e.item)}</td>"
            f"<td>{h(status_label)}</td><td>{h(e.why_it_matters)}</td></tr>\n"
        )

    # Risk register rows
    risk_rows = ""
    for r in dossier.risk_register:
        risk_rows += (
            f"<tr><td>{h(r.severity)}</td><td>{h(r.title)}</td>"
            f"<td>{h(r.impact)}</td><td>{h(r.mitigation)}</td></tr>\n"
        )

    # Remediation plan
    remediation_html = ""
    for item in dossier.remediation_plan:
        blocking = f" <strong>[{h(get_template(tmpl_lang, 'blocking'))}!]</strong>" if item.blocking else ""
        remediation_html += f"<h3>[{h(item.priority)}] {h(item.action)}{blocking}</h3>\n"
        remediation_html += f"<p><strong>{h(get_template(tmpl_lang, 'rationale'))}:</strong> {h(item.rationale)}</p>\n"
        if item.suggested_file:
            remediation_html += f"<p><strong>Suggested file:</strong> <code>{h(item.suggested_file)}</code></p>\n"
        if item.command_to_verify:
            remediation_html += f"<p><strong>Verify:</strong> <code>{h(item.command_to_verify)}</code></p>\n"

    # Audience notes
    audience_html = ""
    for note in dossier.audience_notes:
        audience_html += f"<li>{h(note)}</li>\n"

    # Next steps
    steps_html = ""
    for step in dossier.next_steps:
        steps_html += f"<li>{h(step)}</li>\n"

    # Non-claims
    claims_html = ""
    for claim in dossier.non_claims:
        claims_html += f"<li>{h(claim)}</li>\n"

    page = f"""<!DOCTYPE html>
<html lang="{h(tmpl_lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(title)}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; color: #1f2937; line-height: 1.6; }}
h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 0.3em; }}
h2 {{ margin-top: 1.5em; }}
h3 {{ margin-top: 1em; }}
table {{ width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 0.9em; }}
th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #e5e7eb; }}
th {{ background: #f3f4f6; }}
code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }}
.disclaimer {{ background: #f9fafb; padding: 1em; border-radius: 8px; font-size: 0.9em; color: #6b7280; margin: 1em 0; }}
.footer {{ margin-top: 2em; padding-top: 1em; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 0.85em; }}
</style>
</head>
<body>
<h1>{h(title)}</h1>

<div class="disclaimer">{h(get_template(tmpl_lang, 'disclaimer'))}</div>

<h2>{h(get_template(tmpl_lang, 'executive_summary'))}</h2>
<p>{h(es.get('plain_language', ''))}</p>
<p><strong>{h(get_template(tmpl_lang, 'status'))}:</strong> {h(str(es.get('status', '?')))} |
<strong>Score:</strong> {h(str(es.get('score', '?')))}/100</p>

{"<ul>" + audience_html + "</ul>" if audience_html else ""}

<h2>{h(get_template(tmpl_lang, 'evidence_map'))}</h2>
<table>
<tr><th>{h(get_template(tmpl_lang, 'category'))}</th><th>{h(get_template(tmpl_lang, 'item'))}</th>
<th>{h(get_template(tmpl_lang, 'status'))}</th><th>{h(get_template(tmpl_lang, 'why_it_matters'))}</th></tr>
{evidence_rows}
</table>

<h2>{h(get_template(tmpl_lang, 'risk_register'))}</h2>
<table>
<tr><th>{h(get_template(tmpl_lang, 'severity'))}</th><th>{h(get_template(tmpl_lang, 'item'))}</th>
<th>{h(get_template(tmpl_lang, 'impact'))}</th><th>{h(get_template(tmpl_lang, 'mitigation'))}</th></tr>
{risk_rows}
</table>

<h2>{h(get_template(tmpl_lang, 'remediation_plan'))}</h2>
{remediation_html}

<h2>{h(get_template(tmpl_lang, 'next_steps'))}</h2>
<ul>{steps_html}</ul>

<h2>{h(get_template(tmpl_lang, 'non_claims'))}</h2>
<ul>{claims_html}</ul>

<div class="footer">{h(get_template(tmpl_lang, 'generated_by'))}</div>
</body>
</html>"""

    if output_path:
        from pathlib import Path
        Path(output_path).write_text(page, encoding="utf-8")
    return page


def generate_dossier_issue(dossier: Dossier, output_path: str | None = None) -> str:
    """Generate GitHub issue text."""
    tmpl_lang = dossier.language
    lines: list[str] = []

    lines.append(get_template(tmpl_lang, "issue_header"))
    lines.append(f"> {get_template(tmpl_lang, 'disclaimer')}\n")

    es = dossier.executive_summary
    lines.append(f"{es.get('plain_language', '')}\n")

    if dossier.remediation_plan:
        lines.append("### Checklist\n")
        for item in dossier.remediation_plan:
            lines.append(f"- [ ] [{item.priority}] {item.action}")
        lines.append("")

    lines.append(f"---\n*{get_template(tmpl_lang, 'generated_by')}*\n")

    text = "\n".join(lines)
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_dossier_pr_comment(dossier: Dossier, output_path: str | None = None) -> str:
    """Generate PR comment text."""
    tmpl_lang = dossier.language
    lines: list[str] = []

    lines.append(get_template(tmpl_lang, "pr_comment_header"))
    lines.append(f"> {get_template(tmpl_lang, 'disclaimer')}\n")

    es = dossier.executive_summary
    lines.append(f"{es.get('plain_language', '')}\n")

    if es.get("score") is not None:
        lines.append(f"**Score:** {es.get('score', '?')}/100 | **Status:** {es.get('status', '?')}\n")

    if dossier.remediation_plan:
        blocking = [r for r in dossier.remediation_plan if r.blocking]
        if blocking:
            lines.append(f"**Blocking issues:** {len(blocking)}\n")
            for item in blocking[:3]:
                lines.append(f"- [{item.priority}] {item.action}")
            lines.append("")

    lines.append(f"---\n*{get_template(tmpl_lang, 'generated_by')}*\n")

    text = "\n".join(lines)
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text
