"""GitHub Actions annotation output for oss-paper-ci scan results."""

from __future__ import annotations

import re
from typing import Any

from ..models import Report


def _escape_github(s: str) -> str:
    """Escape special characters for GitHub workflow commands."""
    # GitHub workflow commands use % as escape character
    s = s.replace("%", "%25")
    s = s.replace("\r", "%0D")
    s = s.replace("\n", "%0A")
    s = s.replace(":", "%3A")
    s = s.replace(",", "%2C")
    return s


def _severity_to_annotation_level(severity: str) -> str:
    """Map check severity to GitHub annotation level."""
    mapping = {
        "error": "error",
        "warning": "warning",
        "info": "notice",
        "blocker": "error",
        "critical": "error",
        "major": "warning",
        "minor": "notice",
    }
    return mapping.get(severity.lower(), "notice")


def generate_github_annotations(
    report: Report,
    *,
    max_annotations: int = 50,
    fail_on: str | None = None,
) -> str:
    """Generate GitHub Actions workflow command annotations.

    Args:
        report: The scan report.
        max_annotations: Maximum number of annotations to emit.
        fail_on: Severity level to fail on (e.g., "major", "error").

    Returns:
        String of GitHub workflow commands.
    """
    checks = report.checks or []
    lines: list[str] = []
    count = 0

    for check in checks:
        if check.status.value == "pass":
            continue

        if count >= max_annotations:
            remaining = sum(1 for c in checks if c.status.value != "pass") - count
            if remaining > 0:
                lines.append(f"::notice title=Truncated::{remaining} more findings not shown")
            break

        level = _severity_to_annotation_level(check.severity.value)
        title = _escape_github(f"{check.id}: {check.title}")
        message = _escape_github(check.message)

        # Try to extract file and line from evidence
        file_path = None
        line_num = None
        if check.evidence:
            # Look for file paths in evidence
            for ev in check.evidence:
                if isinstance(ev, dict):
                    fp = ev.get("file") or ev.get("path")
                    if fp:
                        file_path = fp
                        line_num = ev.get("line")
                        break
                elif isinstance(ev, str):
                    # Try to extract path:line from string
                    m = re.match(r"^([^\s:]+):(\d+)", ev)
                    if m:
                        file_path = m.group(1)
                        line_num = int(m.group(2))
                        break

        if file_path:
            # Normalize path separators
            file_path = file_path.replace("\\", "/")
            # Make repository-relative
            if file_path.startswith("/"):
                # Try to make it relative
                parts = file_path.split("/")
                for i, part in enumerate(parts):
                    if part == "src" or part == "tests" or part == "docs":
                        file_path = "/".join(parts[i:])
                        break

            loc = f"file={_escape_github(file_path)}"
            if line_num:
                loc += f",line={line_num}"
            lines.append(f"::{level} {loc} title={title}::{message}")
        else:
            lines.append(f"::{level} title={title}::{message}")

        count += 1

    return "\n".join(lines)


def generate_step_summary(report: Report) -> str:
    """Generate Markdown summary for GitHub Step Summary.

    Args:
        report: The scan report.

    Returns:
        Markdown string for step summary.
    """
    checks = report.checks or []
    summary = report.summary
    score = summary.score if summary else 0
    status = summary.status if summary else "unknown"

    # Status badge
    badge_colors = {"pass": "green", "warn": "yellow", "fail": "red"}
    badge = badge_colors.get(status, "lightgrey")

    lines = [
        f"# OSS Paper CI Report",
        "",
        f"![Score](https://img.shields.io/badge/Score-{score}%2F100-{badge})",
        f"![Status](https://img.shields.io/badge/Status-{status}-{badge})",
        "",
        f"**Checks:** {len(checks)} total",
        "",
    ]

    # Summary table
    blocking = [c for c in checks if c.severity.value == "error" and c.status.value == "fail"]
    important = [c for c in checks if c.severity.value == "warning" and c.status.value == "fail"]
    advisory = [c for c in checks if c.status.value == "warn"]
    passed = [c for c in checks if c.status.value == "pass"]

    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Blocking | {len(blocking)} |")
    lines.append(f"| Important | {len(important)} |")
    lines.append(f"| Advisory | {len(advisory)} |")
    lines.append(f"| Passed | {len(passed)} |")
    lines.append("")

    # Findings
    failing = [c for c in checks if c.status.value != "pass"]
    if failing:
        lines.append("## Findings")
        lines.append("")
        lines.append("| ID | Severity | Status | Message |")
        lines.append("|----|----------|--------|---------|")
        for c in failing[:20]:
            sev = c.severity.value
            msg = c.message[:100] + "..." if len(c.message) > 100 else c.message
            msg = msg.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| `{c.id}` | {sev} | {c.status.value} | {msg} |")
        if len(failing) > 20:
            lines.append(f"| ... | ... | ... | *{len(failing) - 20} more* |")
        lines.append("")

    # Recommendations
    recs = [c for c in checks if c.recommendation and c.status.value != "pass"]
    if recs:
        lines.append("<details>")
        lines.append("<summary>Recommendations</summary>")
        lines.append("")
        for c in recs[:10]:
            lines.append(f"- **{c.id}**: {c.recommendation}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by [oss-paper-ci](https://github.com/Akastella/oss-paper-ci)*")

    return "\n".join(lines)
