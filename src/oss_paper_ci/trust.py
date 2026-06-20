"""Trust & Supply-Chain Security Audit Module."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import __version__
from .inventory import build_inventory
from .provenance import build_provenance
from .security import run_security_scan
from .workflow_audit import audit_workflows


@dataclass
class TrustReport:
    """Aggregated trust report."""

    schema_version: str = "0.1"
    report_type: str = "oss-paper-ci-trust-report"
    repo: str = "."
    summary: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    inventory: dict[str, Any] = field(default_factory=dict)
    workflow_audit: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_type": self.report_type,
            "repo": self.repo,
            "summary": self.summary,
            "findings": self.findings,
            "inventory": self.inventory,
            "workflow_audit": self.workflow_audit,
            "provenance": self.provenance,
            "limitations": self.limitations,
        }


def build_trust_report(repo_path: str | Path, include_timestamp: bool = False) -> TrustReport:
    """Build a comprehensive trust report for the repository."""
    repo = Path(repo_path).resolve()

    # Run sub-components
    security_result = run_security_scan(repo)
    inventory_result = build_inventory(repo)
    workflow_result = audit_workflows(repo)
    provenance_result = build_provenance(repo, include_timestamp=include_timestamp)

    # Aggregate findings
    all_findings = security_result.findings + workflow_result.findings

    # Compute summary
    high = sum(1 for f in all_findings if f.get("severity") == "high")
    medium = sum(1 for f in all_findings if f.get("severity") == "medium")
    low = sum(1 for f in all_findings if f.get("severity") == "low")

    if high > 0:
        status = "fail"
    elif medium > 0:
        status = "warn"
    else:
        status = "pass"

    limitations = [
        "Local static analysis only; no runtime verification.",
        "No cryptographic signing or attestation.",
        "Secret detection uses pattern matching; may produce false positives/negatives.",
        "Workflow audit is static; does not verify runtime behavior.",
        "Dependency inventory is based on declared metadata, not resolved lockfiles.",
        "Provenance manifest is locally generated; not a signed SLSA attestation.",
        "Does not verify the integrity of third-party dependencies.",
    ]

    return TrustReport(
        repo=str(repo),
        summary={"status": status, "high": high, "medium": medium, "low": low},
        findings=all_findings,
        inventory=inventory_result.to_dict(),
        workflow_audit=workflow_result.to_dict(),
        provenance=provenance_result.to_dict(),
        limitations=limitations,
    )


def format_trust_report_markdown(report: TrustReport) -> str:
    """Format trust report as Markdown."""
    lines = [
        "# Trust & Supply-Chain Security Report",
        "",
        f"**Repository:** `{report.repo}`",
        f"**Schema Version:** {report.schema_version}",
        "",
        "## Summary",
        "",
        f"| Severity | Count |",
        f"|----------|-------|",
        f"| High     | {report.summary.get('high', 0)} |",
        f"| Medium   | {report.summary.get('medium', 0)} |",
        f"| Low      | {report.summary.get('low', 0)} |",
        f"",
        f"**Overall Status:** {report.summary.get('status', 'unknown').upper()}",
        "",
    ]

    if report.findings:
        lines.append("## Findings")
        lines.append("")
        for i, finding in enumerate(report.findings, 1):
            lines.append(f"### {i}. {finding.get('title', 'Untitled')}")
            lines.append("")
            lines.append(f"- **ID:** {finding.get('id', 'n/a')}")
            lines.append(f"- **Severity:** {finding.get('severity', 'n/a')}")
            lines.append(f"- **Category:** {finding.get('category', 'n/a')}")
            if finding.get("path"):
                lines.append(f"- **Path:** `{finding['path']}`")
            if finding.get("line"):
                lines.append(f"- **Line:** {finding['line']}")
            lines.append(f"- **Message:** {finding.get('message', '')}")
            if finding.get("recommendation"):
                lines.append(f"- **Recommendation:** {finding['recommendation']}")
            lines.append("")

    lines.append("## Limitations")
    lines.append("")
    for lim in report.limitations:
        lines.append(f"- {lim}")
    lines.append("")

    return "\n".join(lines)


def format_trust_report_html(report: TrustReport) -> str:
    """Format trust report as HTML (self-contained, no external CDN)."""
    findings_html = ""
    for i, f in enumerate(report.findings, 1):
        findings_html += f"""
        <div class="finding severity-{f.get('severity', 'low')}">
            <h3>{i}. {f.get('title', 'Untitled')}</h3>
            <ul>
                <li><strong>ID:</strong> {f.get('id', 'n/a')}</li>
                <li><strong>Severity:</strong> {f.get('severity', 'n/a')}</li>
                <li><strong>Category:</strong> {f.get('category', 'n/a')}</li>
                <li><strong>Path:</strong> <code>{f.get('path', 'n/a')}</code></li>
                <li><strong>Message:</strong> {f.get('message', '')}</li>
                <li><strong>Recommendation:</strong> {f.get('recommendation', '')}</li>
            </ul>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trust Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .severity-high {{ border-left: 4px solid #e74c3c; padding-left: 10px; }}
        .severity-medium {{ border-left: 4px solid #f1c40f; padding-left: 10px; }}
        .severity-low {{ border-left: 4px solid #2ecc71; padding-left: 10px; }}
        code {{ background: #f8f8f8; padding: 2px 6px; border-radius: 4px; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Trust & Supply-Chain Security Report</h1>
    <p><strong>Repository:</strong> <code>{report.repo}</code></p>

    <h2>Summary</h2>
    <table>
        <tr><th>Severity</th><th>Count</th></tr>
        <tr><td>High</td><td>{report.summary.get('high', 0)}</td></tr>
        <tr><td>Medium</td><td>{report.summary.get('medium', 0)}</td></tr>
        <tr><td>Low</td><td>{report.summary.get('low', 0)}</td></tr>
    </table>
    <p><strong>Overall Status:</strong> {report.summary.get('status', 'unknown').upper()}</p>

    <h2>Findings</h2>
    {findings_html if findings_html else "<p>No findings.</p>"}

    <h2>Limitations</h2>
    <ul>
        {"".join(f"<li>{l}</li>" for l in report.limitations)}
    </ul>
</body>
</html>"""
