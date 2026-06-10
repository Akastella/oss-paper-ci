"""Reproduce report generation for oss-paper-ci.

Generates Markdown, JSON, and HTML reports from ReproduceResult.
HTML reports are single-file with no external CDN.
All user-provided content is HTML-escaped.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from oss_paper_ci.reproduce import ReproduceResult


# ---------------------------------------------------------------------------
# JSON report
# ---------------------------------------------------------------------------

def generate_reproduce_json_report(
    result: ReproduceResult,
    output_path: str | None = None,
) -> str:
    """Generate a JSON reproduction report."""
    data = {
        "schema_version": "1.0",
        "tool": "oss-paper-ci",
        "report_type": "reproduction",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **result.to_dict(),
    }
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def generate_reproduce_markdown_report(
    result: ReproduceResult,
    output_path: str | None = None,
) -> str:
    """Generate a Markdown reproduction report."""
    lines: list[str] = []
    lines.append("# Reproduction Attempt Report")
    lines.append("")

    # Summary
    if result.dry_run:
        lines.append("**Mode:** dry-run (no commands were executed)")
    else:
        if result.ok:
            lines.append("**Mode:** executed — configured commands completed successfully")
        else:
            lines.append("**Mode:** executed — one or more commands failed")
    lines.append("")

    # Input info
    lines.append("## Input")
    lines.append("")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Input URL | `{result.input_url}` |")
    if result.repo_url:
        lines.append(f"| Repository | `{result.repo_url}` |")
    if result.paper_url:
        lines.append(f"| Paper URL | `{result.paper_url}` |")
    lines.append(f"| Source type | {result.resolved_source} |")
    if result.commit_sha:
        lines.append(f"| Commit | `{result.commit_sha[:12]}` |")
    lines.append("")

    # Clone status
    lines.append("## Clone")
    lines.append("")
    if result.clone_ok:
        lines.append("Repository cloned successfully.")
    elif result.clone_error:
        lines.append(f"Clone failed: {result.clone_error}")
    else:
        lines.append("[dry-run] Clone would be performed.")
    lines.append("")

    # Environment
    lines.append("## Environment")
    lines.append("")
    if result.environment:
        env = result.environment
        if env.environment_files:
            lines.append("Detected environment files:")
            for ef in env.environment_files:
                lines.append(f"- `{ef.path}` ({ef.file_type})")
            lines.append("")
        if env.install_steps:
            lines.append("Installation plan:")
            for step in env.install_steps:
                lines.append(f"- {step.description}: `{step.command}`")
            lines.append("")
        if env.warnings:
            for w in env.warnings:
                lines.append(f"> **Note:** {w}")
            lines.append("")
    else:
        lines.append("No environment detected.")
        lines.append("")

    # Install results
    if result.install_results:
        lines.append("## Installation")
        lines.append("")
        for r in result.install_results:
            status = "blocked" if r.blocked else ("dry-run" if r.block_reason == "dry_run" else ("ok" if r.exit_code == 0 else "FAILED"))
            lines.append(f"- `{r.command}` → {status}")
            if r.exit_code != 0 and not r.blocked and r.block_reason != "dry_run":
                if r.stderr_excerpt:
                    lines.append(f"  ```")
                    lines.append(f"  {r.stderr_excerpt[:500]}")
                    lines.append(f"  ```")
        lines.append("")

    # Reproduction commands
    lines.append("## Reproduction Commands")
    lines.append("")
    if result.reproduction_commands:
        for i, cmd in enumerate(result.reproduction_commands):
            cmd_result = result.command_results[i] if i < len(result.command_results) else None
            if cmd_result:
                if cmd_result.blocked:
                    status = f"BLOCKED: {cmd_result.block_reason}"
                elif cmd_result.block_reason == "dry_run":
                    status = "dry-run"
                elif cmd_result.exit_code == 0:
                    status = f"ok ({cmd_result.duration_seconds:.1f}s)"
                else:
                    status = f"FAILED (exit code {cmd_result.exit_code})"
                lines.append(f"- `{cmd}` → {status}")
            else:
                lines.append(f"- `{cmd}`")
        lines.append("")
    else:
        lines.append("No executable reproduction command detected.")
        lines.append("")
        if result.dry_run:
            lines.append("> Use `--command` to specify a reproduction command.")
            lines.append("")

    # Command output details
    if result.command_results and not result.dry_run:
        lines.append("## Command Output")
        lines.append("")
        for r in result.command_results:
            if r.blocked or r.block_reason == "dry_run":
                continue
            lines.append(f"### `{r.command}`")
            lines.append("")
            lines.append(f"- Exit code: {r.exit_code}")
            lines.append(f"- Duration: {r.duration_seconds:.3f}s")
            if r.timed_out:
                lines.append(f"- **Timed out**")
            lines.append("")
            if r.stdout_excerpt:
                lines.append("<details>")
                lines.append("<summary>stdout</summary>")
                lines.append("")
                lines.append("```")
                lines.append(r.stdout_excerpt)
                lines.append("```")
                lines.append("")
                lines.append("</details>")
                lines.append("")
            if r.stderr_excerpt:
                lines.append("<details>")
                lines.append("<summary>stderr</summary>")
                lines.append("")
                lines.append("```")
                lines.append(r.stderr_excerpt)
                lines.append("```")
                lines.append("")
                lines.append("</details>")
                lines.append("")

    # Generated artifacts
    if result.generated_artifacts:
        lines.append("## Generated Artifacts")
        lines.append("")
        for a in result.generated_artifacts:
            lines.append(f"- `{a}`")
        lines.append("")

    # Scan results
    lines.append("## Scan Results")
    lines.append("")
    if result.scan_status == "dry_run":
        lines.append("[dry-run] Scan would be performed on the repository.")
    elif result.scan_status == "not_run":
        lines.append("Scan was not run.")
    else:
        lines.append(f"- Score: {result.scan_score}/100")
        lines.append(f"- Status: {result.scan_status}")
        if result.scan_findings_summary:
            lines.append(f"- Findings: {result.scan_findings_summary}")
    lines.append("")

    # Limitations
    if result.limitations:
        lines.append("## Limitations")
        lines.append("")
        for lim in result.limitations:
            lines.append(f"- {lim}")
        lines.append("")

    # Warnings
    if result.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Error
    if result.error:
        lines.append("## Error")
        lines.append("")
        lines.append(f"```")
        lines.append(result.error)
        lines.append(f"```")
        lines.append("")

    # Rerun commands
    lines.append("## Rerun")
    lines.append("")
    lines.append("To reproduce this attempt locally:")
    lines.append("")
    lines.append("```bash")
    if result.resolved_source == "github" and result.repo_url:
        lines.append(f"# Clone the repository")
        lines.append(f"git clone {result.repo_url}")
        repo_name = result.repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        lines.append(f"cd {repo_name}")
    elif result.resolved_source == "local" and result.repo_url:
        lines.append(f"# Navigate to the repository")
        lines.append(f"cd {result.repo_url}")
    if result.reproduction_commands:
        for cmd in result.reproduction_commands:
            lines.append(f"{cmd}")
    lines.append("```")
    lines.append("")

    # Disclaimer
    lines.append("---")
    lines.append("")
    lines.append(
        "> **Disclaimer:** This is an *attempted reproduction report*. "
        "It documents what commands were run (or would be run), not whether the "
        "paper's claims are correct. Successful command execution does not mean "
        "the paper's results are valid or reproducible."
    )
    lines.append("")
    lines.append("*Generated by oss-paper-ci*")

    text = "\n".join(lines)
    if output_path:
        from pathlib import Path
        Path(output_path).write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """HTML-escape text."""
    return html.escape(str(text))


def _score_color(score: int) -> str:
    if score >= 80:
        return "#22c55e"
    if score >= 50:
        return "#eab308"
    return "#ef4444"


def _status_badge(status: str) -> str:
    colors = {"pass": "#22c55e", "warn": "#eab308", "fail": "#ef4444", "dry_run": "#6b7280", "not_run": "#9ca3af"}
    color = colors.get(status, "#6b7280")
    return f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:0.85em">{_esc(status)}</span>'


def generate_reproduce_html_report(
    result: ReproduceResult,
    output_path: str | None = None,
) -> str:
    """Generate a single-file HTML reproduction report."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Build environment files list
    env_files_html = ""
    if result.environment and result.environment.environment_files:
        items = "".join(
            f"<li><code>{_esc(ef.path)}</code> ({_esc(ef.file_type)})</li>"
            for ef in result.environment.environment_files
        )
        env_files_html = f"<ul>{items}</ul>"
    else:
        env_files_html = "<p>No environment files detected.</p>"

    # Build install results
    install_html = ""
    if result.install_results:
        rows = ""
        for r in result.install_results:
            if r.blocked:
                status = "BLOCKED"
            elif r.block_reason == "dry_run":
                status = "dry-run"
            elif r.exit_code == 0:
                status = "ok"
            else:
                status = f"FAILED ({r.exit_code})"
            rows += f"<tr><td><code>{_esc(r.command)}</code></td><td>{_esc(status)}</td></tr>"
        install_html = f"<table><tr><th>Command</th><th>Status</th></tr>{rows}</table>"

    # Build command results
    cmd_html = ""
    if result.command_results:
        rows = ""
        for r in result.command_results:
            if r.blocked:
                status = f"BLOCKED: {_esc(r.block_reason)}"
            elif r.block_reason == "dry_run":
                status = "dry-run"
            elif r.exit_code == 0:
                status = f"ok ({r.duration_seconds:.1f}s)"
            else:
                status = f"FAILED (exit {r.exit_code})"
            rows += f"<tr><td><code>{_esc(r.command)}</code></td><td>{_esc(status)}</td></tr>"
        cmd_html = f"<table><tr><th>Command</th><th>Status</th></tr>{rows}</table>"
    elif not result.reproduction_commands:
        cmd_html = "<p>No executable reproduction command detected.</p>"

    # Artifacts
    artifacts_html = ""
    if result.generated_artifacts:
        items = "".join(f"<li><code>{_esc(a)}</code></li>" for a in result.generated_artifacts)
        artifacts_html = f"<ul>{items}</ul>"

    # Warnings
    warnings_html = ""
    if result.warnings:
        items = "".join(f"<li>{_esc(w)}</li>" for w in result.warnings)
        warnings_html = f"<div class='warnings'><h3>Warnings</h3><ul>{items}</ul></div>"

    # Error
    error_html = ""
    if result.error:
        error_html = f"<div class='error'><h3>Error</h3><pre>{_esc(result.error)}</pre></div>"

    # Limitations
    limits_html = ""
    if result.limitations:
        items = "".join(f"<li>{_esc(l)}</li>" for l in result.limitations)
        limits_html = f"<ul>{items}</ul>"

    mode_text = "dry-run" if result.dry_run else "executed"
    ok_text = "configured commands completed successfully" if result.ok else "one or more commands failed"

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reproduction Attempt Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; color: #1f2937; line-height: 1.5; }}
h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 0.3em; }}
h2 {{ margin-top: 1.5em; color: #374151; }}
h3 {{ margin-top: 1em; }}
table {{ width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 0.9em; }}
th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #e5e7eb; }}
th {{ background: #f3f4f6; }}
code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }}
pre {{ background: #f3f4f6; padding: 1em; border-radius: 8px; overflow-x: auto; font-size: 0.85em; }}
.meta {{ color: #6b7280; font-size: 0.85em; }}
.warnings {{ background: #fffbeb; border: 1px solid #fbbf24; padding: 1em; border-radius: 8px; margin: 1em 0; }}
.error {{ background: #fef2f2; border: 1px solid #ef4444; padding: 1em; border-radius: 8px; margin: 1em 0; }}
.disclaimer {{ margin-top: 2em; padding: 1em; background: #f9fafb; border-radius: 8px; font-size: 0.9em; color: #6b7280; }}
.footer {{ margin-top: 2em; padding-top: 1em; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 0.85em; }}
</style>
</head>
<body>
<h1>Reproduction Attempt Report</h1>

<p class="meta">
<strong>Mode:</strong> {_esc(mode_text)} &mdash;
<strong>Result:</strong> {_esc(ok_text)} &mdash;
<strong>Generated:</strong> {_esc(timestamp)}
</p>

<h2>Input</h2>
<table>
<tr><td><strong>Input URL</strong></td><td><code>{_esc(result.input_url)}</code></td></tr>
{"<tr><td><strong>Repository</strong></td><td><code>" + _esc(result.repo_url) + "</code></td></tr>" if result.repo_url else ""}
{"<tr><td><strong>Paper URL</strong></td><td><code>" + _esc(result.paper_url) + "</code></td></tr>" if result.paper_url else ""}
<tr><td><strong>Source type</strong></td><td>{_esc(result.resolved_source)}</td></tr>
{"<tr><td><strong>Commit</strong></td><td><code>" + _esc(result.commit_sha[:12]) + "</code></td></tr>" if result.commit_sha else ""}
</table>

<h2>Environment</h2>
{env_files_html}

<h2>Installation</h2>
{install_html if install_html else "<p>No installation performed.</p>"}

<h2>Reproduction Commands</h2>
{cmd_html}

{"<h2>Generated Artifacts</h2>" + artifacts_html if artifacts_html else ""}

<h2>Scan Results</h2>
{"<p>[dry-run] Scan would be performed.</p>" if result.scan_status == "dry_run" else ""}
{"<p>Scan was not run.</p>" if result.scan_status == "not_run" else ""}
{"" if result.scan_status in ("dry_run", "not_run") else "<p>Score: " + str(result.scan_score) + "/100 &mdash; " + _status_badge(result.scan_status) + "</p>"}
{"" if result.scan_status in ("dry_run", "not_run") or not result.scan_findings_summary else "<p>" + _esc(result.scan_findings_summary) + "</p>"}

<h2>Limitations</h2>
{limits_html if limits_html else "<p>None noted.</p>"}

{warnings_html}
{error_html}

<div class="disclaimer">
<strong>Disclaimer:</strong> This is an <em>attempted reproduction report</em>.
It documents what commands were run (or would be run), not whether the
paper's claims are correct. Successful command execution does not mean
the paper's results are valid or reproducible.
</div>

<div class="footer">
Generated by <a href="https://github.com/Akastella/oss-paper-ci">oss-paper-ci</a>
&mdash; {_esc(timestamp)}
</div>
</body>
</html>"""

    if output_path:
        from pathlib import Path
        Path(output_path).write_text(report, encoding="utf-8")
    return report
