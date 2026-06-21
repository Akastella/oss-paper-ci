"""Unified evidence report builder.

Aggregates scan, data diagnostics, results validation, ecosystems,
trust/security, and adoption into a single shareable report.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import __version__


# ── Data model ──────────────────────────────────────────────────────────────


@dataclass
class EvidenceFinding:
    """A single finding in the evidence report."""

    id: str = ""
    severity: str = "info"  # info, warning, error, high, medium, low
    category: str = ""  # metadata, environment, data, results, trust, security, execution
    title: str = ""
    message: str = ""
    recommendation: str = ""
    path: str = ""  # always relative
    source_section: str = ""  # which section produced this

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "message": self.message,
        }
        if self.recommendation:
            d["recommendation"] = self.recommendation
        if self.path:
            d["path"] = self.path
        if self.source_section:
            d["source_section"] = self.source_section
        return d


@dataclass
class EvidenceReport:
    """Unified evidence report."""

    schema_version: str = "0.1"
    report_type: str = "oss-paper-ci-evidence-report"
    tool_version: str = __version__
    profile: str = "reviewer"  # reviewer, author, maintainer
    repo: str = "."
    summary: dict[str, Any] = field(default_factory=dict)
    sections: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    recommended_next_steps: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_type": self.report_type,
            "tool_version": self.tool_version,
            "profile": self.profile,
            "repo": self.repo,
            "summary": self.summary,
            "sections": self.sections,
            "findings": self.findings,
            "recommended_next_steps": self.recommended_next_steps,
            "limitations": self.limitations,
        }


# ── Helpers ─────────────────────────────────────────────────────────────────

def _relativize(path_str: str, repo_root: Path) -> str:
    """Convert absolute path to relative, or return as-is."""
    if not path_str:
        return path_str
    try:
        p = Path(path_str)
        if p.is_absolute():
            return str(p.relative_to(repo_root))
    except (ValueError, OSError):
        pass
    return path_str


def _strip_absolute_paths(obj: Any, repo_root: Path) -> Any:
    """Recursively strip absolute paths from a dict/list."""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if k in ("repo", "repo_path", "path", "workdir", "output_dir") and isinstance(v, str):
                result[k] = _relativize(v, repo_root)
            elif k == "output_file" and isinstance(v, str):
                result[k] = _relativize(v, repo_root)
            else:
                result[k] = _strip_absolute_paths(v, repo_root)
        return result
    elif isinstance(obj, list):
        return [_strip_absolute_paths(item, repo_root) for item in obj]
    elif isinstance(obj, str):
        # Check if it looks like an absolute path
        if len(obj) > 3 and (obj[1] == ":" or obj.startswith("/home") or obj.startswith("/Users")):
            return _relativize(obj, repo_root)
        return obj
    return obj


# ── Section builders ────────────────────────────────────────────────────────


def _build_repository_section(repo_path: Path) -> dict[str, Any]:
    """Build repository metadata section."""
    import subprocess

    section: dict[str, Any] = {
        "path": repo_path.name,
    }

    # Git info
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            section["commit"] = result.stdout.strip()
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            section["dirty"] = bool(result.stdout.strip())
    except Exception:
        pass

    return section


def _build_reproducibility_section(repo_path: Path) -> dict[str, Any]:
    """Build reproducibility scan section."""
    from .config import load_config
    from .scanner import scan as run_scan

    config = load_config(repo_root=str(repo_path))
    report = run_scan(str(repo_path), config)

    scan_dict = report.to_dict()
    scan_dict = _strip_absolute_paths(scan_dict, repo_path)

    section: dict[str, Any] = {
        "score": report.summary.score,
        "status": report.summary.status,
        "checks_total": len(report.checks),
        "checks_pass": sum(1 for c in report.checks if c.status.value == "pass"),
        "checks_warn": sum(1 for c in report.checks if c.status.value in ("warn", "warning")),
        "checks_fail": sum(1 for c in report.checks if c.status.value == "fail"),
        "policy": {
            "profile": config.profile,
        },
        "score_components": scan_dict.get("summary", {}).get("score_components", {}),
    }

    # Top findings (fail/warn only)
    top_findings = []
    for c in report.checks:
        status_val = c.status.value if hasattr(c.status, "value") else str(c.status)
        if status_val in ("fail", "warn", "warning"):
            top_findings.append({
                "id": c.id,
                "title": c.title,
                "severity": c.severity.value if hasattr(c.severity, "value") else str(c.severity),
                "status": status_val,
                "message": c.message,
                "recommendation": getattr(c, "recommendation", ""),
            })
    section["findings"] = top_findings

    return section


def _build_data_section(repo_path: Path) -> dict[str, Any]:
    """Build data diagnostics section."""
    from .data_diagnostics import run_data_diagnostics

    diagnostics = run_data_diagnostics(str(repo_path))

    checks = []
    missing_count = 0
    for d in diagnostics:
        checks.append({
            "check_id": d.check_id,
            "title": d.title,
            "status": d.status,
            "message": d.message,
            "recommendation": getattr(d, "recommendation", ""),
        })
        if d.status == "missing":
            missing_count += 1

    return {
        "checks_total": len(diagnostics),
        "checks_missing": missing_count,
        "checks": checks,
    }


def _build_results_section(repo_path: Path) -> dict[str, Any]:
    """Build results validation section."""
    from .result_validation import run_result_validation

    validations = run_result_validation(str(repo_path))

    checks = []
    missing_count = 0
    invalid_count = 0
    for v in validations:
        checks.append({
            "check_id": v.check_id,
            "title": v.title,
            "status": v.status,
            "message": v.message,
            "recommendation": getattr(v, "recommendation", ""),
        })
        if v.status == "missing":
            missing_count += 1
        elif v.status == "invalid":
            invalid_count += 1

    return {
        "checks_total": len(validations),
        "checks_missing": missing_count,
        "checks_invalid": invalid_count,
        "checks": checks,
    }


def _build_ecosystems_section(repo_path: Path) -> dict[str, Any]:
    """Build ecosystems section."""
    from .ecosystems import detect_ecosystems

    ecosystems = detect_ecosystems(str(repo_path))

    detected = []
    for eco in ecosystems:
        detected.append({
            "id": eco.id,
            "display_name": eco.display_name,
            "support_level": eco.support_level,
            "runtime_available": eco.runtime_available,
        })

    return {
        "detected": detected,
        "total": len(detected),
    }


def _build_trust_section(repo_path: Path) -> dict[str, Any]:
    """Build trust/security section."""
    from .trust import build_trust_report

    report = build_trust_report(repo_path)
    report_dict = report.to_dict()
    report_dict = _strip_absolute_paths(report_dict, repo_path)

    return {
        "summary": report_dict.get("summary", {}),
        "findings_count": len(report_dict.get("findings", [])),
        "findings_high": report.summary.get("high", 0),
        "findings_medium": report.summary.get("medium", 0),
        "findings_low": report.summary.get("low", 0),
        "findings": report_dict.get("findings", []),
    }


def _build_adoption_section(repo_path: Path) -> dict[str, Any]:
    """Build adoption/suggestions section."""
    from .adoption import build_adoption_plan
    from .ecosystems import detect_ecosystems

    ecosystems = detect_ecosystems(str(repo_path))
    eco_dicts = [e.to_dict() for e in ecosystems] if ecosystems else []
    plan = build_adoption_plan(repo_path=str(repo_path), ecosystems=eco_dicts)

    return {
        "missing_files": plan.missing_files[:10],
        "recommended_files": plan.recommended_files[:10],
        "manual_steps": plan.manual_steps[:10],
    }


# ── Report builder ──────────────────────────────────────────────────────────


def build_evidence_report(
    repo_path: str | Path,
    profile: str = "reviewer",
    include_sections: list[str] | None = None,
) -> EvidenceReport:
    """Build a unified evidence report.

    Args:
        repo_path: Path to the repository.
        profile: One of 'reviewer', 'author', 'maintainer'.
        include_sections: Sections to include. None = all default sections.
    """
    root = Path(repo_path).resolve()

    if include_sections is None:
        include_sections = [
            "repository", "reproducibility", "data", "results",
            "ecosystems", "trust", "adoption",
        ]

    report = EvidenceReport(
        profile=profile,
        repo=root.name,
    )

    # Build sections
    sections: dict[str, Any] = {}

    if "repository" in include_sections:
        sections["repository"] = _build_repository_section(root)

    if "reproducibility" in include_sections:
        sections["reproducibility"] = _build_reproducibility_section(root)

    if "data" in include_sections:
        sections["data"] = _build_data_section(root)

    if "results" in include_sections:
        sections["results"] = _build_results_section(root)

    if "ecosystems" in include_sections:
        sections["ecosystems"] = _build_ecosystems_section(root)

    if "trust" in include_sections:
        sections["trust"] = _build_trust_section(root)

    if "adoption" in include_sections:
        sections["adoption"] = _build_adoption_section(root)

    report.sections = sections

    # Aggregate findings
    all_findings: list[dict[str, Any]] = []

    # From reproducibility
    repro = sections.get("reproducibility", {})
    for f in repro.get("findings", []):
        all_findings.append({
            **f,
            "source_section": "reproducibility",
            "category": "reproducibility",
        })

    # From data
    data_sec = sections.get("data", {})
    for c in data_sec.get("checks", []):
        if c.get("status") in ("missing", "partial"):
            all_findings.append({
                "id": c.get("check_id", ""),
                "severity": "warning",
                "category": "data",
                "title": c.get("title", ""),
                "message": c.get("message", ""),
                "recommendation": c.get("recommendation", ""),
                "source_section": "data",
            })

    # From results
    results_sec = sections.get("results", {})
    for c in results_sec.get("checks", []):
        if c.get("status") in ("missing", "invalid"):
            all_findings.append({
                "id": c.get("check_id", ""),
                "severity": "warning",
                "category": "results",
                "title": c.get("title", ""),
                "message": c.get("message", ""),
                "recommendation": c.get("recommendation", ""),
                "source_section": "results",
            })

    # From trust
    trust_sec = sections.get("trust", {})
    for f in trust_sec.get("findings", []):
        all_findings.append({
            **f,
            "source_section": "trust",
        })

    report.findings = all_findings

    # Build summary
    score = repro.get("score", 0)
    status = repro.get("status", "unknown")
    high = trust_sec.get("findings_high", 0)
    medium = trust_sec.get("findings_medium", 0)

    if high > 0 or status == "fail":
        risk_level = "high"
    elif medium > 0 or status == "warn":
        risk_level = "medium"
    else:
        risk_level = "low"

    report.summary = {
        "status": status,
        "readiness_score": score,
        "risk_level": risk_level,
        "total_findings": len(all_findings),
        "findings_high": high,
        "findings_medium": medium,
    }

    # Build plain-language summary based on profile
    report.summary["plain_language_summary"] = _build_plain_summary(
        score, status, risk_level, len(all_findings), profile,
        data_sec, results_sec, trust_sec,
    )

    # Build recommended next steps based on profile
    report.recommended_next_steps = _build_next_steps(profile, all_findings, sections)

    # Limitations
    report.limitations = [
        "This report is an engineering completeness assessment, not a scientific correctness proof.",
        "A high score does not guarantee the research is correct or reproducible.",
        "A low score does not mean the research is flawed.",
        "This tool does not execute experiments unless explicitly requested with --execute.",
        "Trust and security checks are local static analysis only.",
        "Dependency inventory is based on declared metadata, not resolved lockfiles.",
        "This report does not predict paper acceptance or rejection.",
    ]

    return report


# ── Profile-specific content ────────────────────────────────────────────────


def _build_plain_summary(
    score: int, status: str, risk_level: str, finding_count: int,
    profile: str, data_sec: dict, results_sec: dict, trust_sec: dict,
) -> str:
    """Build a plain-language summary appropriate for the profile."""
    parts = []

    if profile == "reviewer":
        parts.append(
            f"The repository scores {score}/100 on reproducibility readiness "
            f"(status: {status})."
        )
        if finding_count > 0:
            parts.append(f"{finding_count} finding(s) were identified.")
        data_missing = data_sec.get("checks_missing", 0)
        if data_missing > 0:
            parts.append(f"{data_missing} data documentation check(s) are missing.")
        results_missing = results_sec.get("checks_missing", 0)
        if results_missing > 0:
            parts.append(f"{results_missing} result artifact check(s) are missing.")
        parts.append(
            "This is an engineering completeness indicator. "
            "It does not judge scientific correctness."
        )

    elif profile == "author":
        parts.append(
            f"Your repository scores {score}/100 on reproducibility readiness."
        )
        if status == "pass":
            parts.append("The basic reproducibility checks are passing.")
        elif status == "warn":
            parts.append("Some reproducibility checks need attention.")
        else:
            parts.append("Several reproducibility checks are failing.")
        if finding_count > 0:
            parts.append(f"See the {finding_count} finding(s) below for specific actions.")

    elif profile == "maintainer":
        parts.append(
            f"Repository readiness: {score}/100 ({status}). "
            f"Trust risk level: {risk_level}."
        )
        trust_high = trust_sec.get("findings_high", 0)
        if trust_high > 0:
            parts.append(f"{trust_high} high-severity trust/security finding(s) require review.")

    return " ".join(parts)


def _build_next_steps(
    profile: str,
    findings: list[dict[str, Any]],
    sections: dict[str, Any],
) -> list[str]:
    """Build recommended next steps based on profile."""
    steps: list[str] = []

    if profile == "reviewer":
        steps.append("Review the evidence map to understand what documentation is present or missing.")
        steps.append("Check the risk register for known gaps in the repository.")
        steps.append("Verify that the claimed results trace to data and code.")

    elif profile == "author":
        # From adoption section
        adoption = sections.get("adoption", {})
        missing = adoption.get("missing_files", [])
        if missing:
            steps.append(f"Add missing files: {', '.join(missing[:3])}")
        manual = adoption.get("manual_steps", [])
        if manual:
            steps.append(f"Address: {manual[0]}")
        repro = sections.get("reproducibility", {})
        if repro.get("status") != "pass":
            steps.append("Run `oss-paper-ci scan . --verbose` for detailed recommendations.")

    elif profile == "maintainer":
        steps.append("Review GitHub Actions workflow permissions and action pinning.")
        steps.append("Verify that the release process generates SHA256SUMS.")
        steps.append("Check dependency inventory for unexpected or outdated dependencies.")

    return steps


# ── Report formatters ───────────────────────────────────────────────────────


def format_evidence_markdown(report: EvidenceReport) -> str:
    """Format evidence report as Markdown."""
    lines = [
        "# Unified Evidence Report",
        "",
        f"**Repository:** `{report.repo}`",
        f"**Profile:** {report.profile}",
        f"**Tool:** oss-paper-ci v{report.tool_version}",
        "",
    ]

    # Summary
    summary = report.summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Readiness Score | {summary.get('readiness_score', 'N/A')}/100 |")
    lines.append(f"| Status | {summary.get('status', 'unknown').upper()} |")
    lines.append(f"| Risk Level | {summary.get('risk_level', 'unknown').upper()} |")
    lines.append(f"| Total Findings | {summary.get('total_findings', 0)} |")
    lines.append("")

    plain = summary.get("plain_language_summary", "")
    if plain:
        lines.append(f"> {plain}")
        lines.append("")

    # Sections
    sections = report.sections

    # Reproducibility
    repro = sections.get("reproducibility", {})
    if repro:
        lines.append("## Reproducibility Scan")
        lines.append("")
        lines.append(f"- **Score:** {repro.get('score', 'N/A')}/100")
        lines.append(f"- **Status:** {repro.get('status', 'unknown')}")
        lines.append(f"- **Checks:** {repro.get('checks_pass', 0)} pass, "
                      f"{repro.get('checks_warn', 0)} warn, "
                      f"{repro.get('checks_fail', 0)} fail")
        lines.append("")

    # Data
    data_sec = sections.get("data", {})
    if data_sec:
        lines.append("## Data Diagnostics")
        lines.append("")
        lines.append(f"- **Total checks:** {data_sec.get('checks_total', 0)}")
        lines.append(f"- **Missing:** {data_sec.get('checks_missing', 0)}")
        lines.append("")

    # Results
    results_sec = sections.get("results", {})
    if results_sec:
        lines.append("## Result Validation")
        lines.append("")
        lines.append(f"- **Total checks:** {results_sec.get('checks_total', 0)}")
        lines.append(f"- **Missing:** {results_sec.get('checks_missing', 0)}")
        lines.append(f"- **Invalid:** {results_sec.get('checks_invalid', 0)}")
        lines.append("")

    # Ecosystems
    eco_sec = sections.get("ecosystems", {})
    if eco_sec:
        lines.append("## Ecosystems")
        lines.append("")
        for eco in eco_sec.get("detected", []):
            lines.append(f"- **{eco.get('display_name', '?')}** ({eco.get('id', '?')}): "
                          f"{eco.get('support_level', '?')}")
        lines.append("")

    # Trust
    trust_sec = sections.get("trust", {})
    if trust_sec:
        ts = trust_sec.get("summary", {})
        lines.append("## Trust & Security")
        lines.append("")
        lines.append(f"- **High findings:** {trust_sec.get('findings_high', 0)}")
        lines.append(f"- **Medium findings:** {trust_sec.get('findings_medium', 0)}")
        lines.append(f"- **Low findings:** {trust_sec.get('findings_low', 0)}")
        lines.append("")

    # Adoption
    adoption_sec = sections.get("adoption", {})
    if adoption_sec:
        missing = adoption_sec.get("missing_files", [])
        if missing:
            lines.append("## Adoption Suggestions")
            lines.append("")
            for f in missing[:5]:
                lines.append(f"- `{f}`")
            lines.append("")

    # Findings
    if report.findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("| ID | Severity | Category | Title |")
        lines.append("|----|----------|----------|-------|")
        for f in report.findings[:20]:
            fid = f.get("id", "?")
            sev = f.get("severity", "?")
            cat = f.get("category", "?")
            title = f.get("title", "?")
            if len(title) > 60:
                title = title[:57] + "..."
            lines.append(f"| `{fid}` | {sev} | {cat} | {title} |")
        if len(report.findings) > 20:
            lines.append(f"| ... | ... | ... | *{len(report.findings) - 20} more* |")
        lines.append("")

    # Next steps
    if report.recommended_next_steps:
        lines.append("## Recommended Next Steps")
        lines.append("")
        for i, step in enumerate(report.recommended_next_steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    # Limitations
    lines.append("## Limitations")
    lines.append("")
    for lim in report.limitations:
        lines.append(f"- {lim}")
    lines.append("")

    return "\n".join(lines)


def format_evidence_html(report: EvidenceReport) -> str:
    """Format evidence report as self-contained HTML."""
    summary = report.summary
    sections = report.sections

    # Findings table rows
    findings_rows = ""
    for f in report.findings[:50]:
        sev = f.get("severity", "?")
        sev_class = {"high": "sev-high", "error": "sev-high", "medium": "sev-medium",
                     "warning": "sev-medium", "low": "sev-low", "info": "sev-info"}.get(sev, "")
        findings_rows += f"""
        <tr class="{sev_class}">
            <td><code>{f.get('id', '?')}</code></td>
            <td>{sev}</td>
            <td>{f.get('category', '?')}</td>
            <td>{f.get('title', '?')}</td>
        </tr>"""

    # Data checks
    data_rows = ""
    for c in sections.get("data", {}).get("checks", []):
        status = c.get("status", "?")
        icon = "✅" if status == "present" else "❌" if status == "missing" else "⚠️"
        data_rows += f"<tr><td>{icon}</td><td>{c.get('title', '?')}</td><td>{status}</td></tr>"

    # Results checks
    results_rows = ""
    for c in sections.get("results", {}).get("checks", []):
        status = c.get("status", "?")
        icon = "✅" if status == "present" else "❌" if status in ("missing", "invalid") else "⚠️"
        results_rows += f"<tr><td>{icon}</td><td>{c.get('title', '?')}</td><td>{status}</td></tr>"

    # Next steps
    next_steps_html = ""
    for i, step in enumerate(report.recommended_next_steps, 1):
        next_steps_html += f"<li>{step}</li>"

    # Limitations
    limitations_html = ""
    for lim in report.limitations:
        limitations_html += f"<li>{lim}</li>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Evidence Report - {report.repo}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       max-width: 900px; margin: 0 auto; padding: 20px; color: #333; line-height: 1.6; }}
h1, h2, h3 {{ color: #2c3e50; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0 20px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
.summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                 gap: 10px; margin: 15px 0; }}
.summary-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px;
                 padding: 15px; text-align: center; }}
.summary-card .value {{ font-size: 2em; font-weight: bold; }}
.summary-card .label {{ color: #666; font-size: 0.9em; }}
blockquote {{ border-left: 4px solid #3498db; margin: 15px 0; padding: 10px 20px;
              background: #ecf0f1; }}
.sev-high {{ background: #ffeaea; }}
.sev-medium {{ background: #fff3e0; }}
.sev-low {{ background: #e8f5e9; }}
code {{ background: #f8f8f8; padding: 2px 6px; border-radius: 3px; }}
.limitations {{ background: #f8f8f8; padding: 15px; border-radius: 6px; }}
</style>
</head>
<body>

<h1>Unified Evidence Report</h1>
<p><strong>Repository:</strong> <code>{report.repo}</code> |
   <strong>Profile:</strong> {report.profile} |
   <strong>Tool:</strong> oss-paper-ci v{report.tool_version}</p>

<h2>Summary</h2>
<div class="summary-grid">
    <div class="summary-card">
        <div class="value">{summary.get('readiness_score', 'N/A')}</div>
        <div class="label">Readiness Score</div>
    </div>
    <div class="summary-card">
        <div class="value">{summary.get('status', 'unknown').upper()}</div>
        <div class="label">Status</div>
    </div>
    <div class="summary-card">
        <div class="value">{summary.get('risk_level', 'unknown').upper()}</div>
        <div class="label">Risk Level</div>
    </div>
    <div class="summary-card">
        <div class="value">{summary.get('total_findings', 0)}</div>
        <div class="label">Findings</div>
    </div>
</div>

<blockquote>{summary.get('plain_language_summary', '')}</blockquote>

<h2>Data Diagnostics</h2>
<table>
<tr><th></th><th>Check</th><th>Status</th></tr>
{data_rows if data_rows else '<tr><td colspan="3">No data checks available</td></tr>'}
</table>

<h2>Result Validation</h2>
<table>
<tr><th></th><th>Check</th><th>Status</th></tr>
{results_rows if results_rows else '<tr><td colspan="3">No result checks available</td></tr>'}
</table>

<h2>Findings</h2>
{'<table><tr><th>ID</th><th>Severity</th><th>Category</th><th>Title</th></tr>' + findings_rows + '</table>' if findings_rows else '<p>No findings.</p>'}

<h2>Recommended Next Steps</h2>
<ol>{next_steps_html if next_steps_html else '<li>No specific recommendations.</li>'}</ol>

<h2>Limitations</h2>
<div class="limitations"><ul>{limitations_html}</ul></div>

</body>
</html>"""
