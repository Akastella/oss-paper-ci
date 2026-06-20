"""Tests for trust report generation."""

from __future__ import annotations

import json
from pathlib import Path

from oss_paper_ci.trust import build_trust_report, format_trust_report_html, format_trust_report_markdown


def test_trust_report_structure(tmp_path: Path) -> None:
    """Trust report has expected structure."""
    report = build_trust_report(tmp_path)
    d = report.to_dict()
    assert d["schema_version"] == "0.1"
    assert d["report_type"] == "oss-paper-ci-trust-report"
    assert "summary" in d
    assert "findings" in d
    assert "inventory" in d
    assert "workflow_audit" in d
    assert "provenance" in d
    assert "limitations" in d


def test_trust_report_summary(tmp_path: Path) -> None:
    """Trust report summary has severity counts."""
    report = build_trust_report(tmp_path)
    assert "high" in report.summary
    assert "medium" in report.summary
    assert "low" in report.summary
    assert "status" in report.summary


def test_trust_report_markdown(tmp_path: Path) -> None:
    """Trust report markdown output is readable."""
    report = build_trust_report(tmp_path)
    md = format_trust_report_markdown(report)
    assert "# Trust & Supply-Chain Security Report" in md
    assert "## Summary" in md
    assert "## Limitations" in md


def test_trust_report_html_no_cdn(tmp_path: Path) -> None:
    """Trust report HTML has no external CDN."""
    report = build_trust_report(tmp_path)
    html = format_trust_report_html(report)
    assert "<!DOCTYPE html>" in html
    # Check no external CDN URLs (not just the substring "cdn" in paths)
    assert "cdn." not in html.lower()
    assert "googleapis" not in html.lower()
    assert "cloudflare" not in html.lower()


def test_trust_report_json_serializable(tmp_path: Path) -> None:
    """Trust report JSON is serializable."""
    report = build_trust_report(tmp_path)
    text = json.dumps(report.to_dict(), indent=2)
    data = json.loads(text)
    assert data["schema_version"] == "0.1"
