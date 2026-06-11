"""Tests for dossier report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.dossier import Dossier, build_dossier
from oss_paper_ci.evidence_map import EvidenceItem
from oss_paper_ci.remediation import RemediationItem, RiskItem
from oss_paper_ci.reporting.dossier_report import (
    generate_dossier_html,
    generate_dossier_issue,
    generate_dossier_json,
    generate_dossier_markdown,
    generate_dossier_pr_comment,
)


def _make_dossier(**kwargs) -> Dossier:
    defaults = {
        "audience": "author",
        "language": "en",
        "evidence_map": [
            EvidenceItem("metadata", "README", "present", "check", "Helps understanding"),
        ],
        "risk_register": [
            RiskItem("r1", "Missing env", "high", "high", "Cannot install", "ENV001 failed", "Add deps"),
        ],
        "remediation_plan": [
            RemediationItem("P0", "Add requirements.txt", "No deps", "low", blocking=True),
        ],
        "executive_summary": {
            "plain_language": "Test summary.",
            "status": "Needs Work",
            "confidence": "Medium",
            "score": 50,
        },
        "audience_notes": ["Author intro."],
        "next_steps": ["Fix P0 items."],
        "non_claims": ["Does not prove correctness."],
    }
    defaults.update(kwargs)
    return Dossier(**defaults)


class TestJsonReport:
    """Test JSON report generation."""

    def test_valid_json(self):
        d = _make_dossier()
        text = generate_dossier_json(d)
        data = json.loads(text)
        assert data["schema_version"] == "0.1"

    def test_has_all_sections(self):
        d = _make_dossier()
        text = generate_dossier_json(d)
        data = json.loads(text)
        assert "evidence_map" in data
        assert "risk_register" in data
        assert "remediation_plan" in data


class TestMarkdownReport:
    """Test Markdown report generation."""

    def test_has_title(self):
        d = _make_dossier()
        text = generate_dossier_markdown(d)
        assert "Dossier" in text

    def test_has_disclaimer(self):
        d = _make_dossier()
        text = generate_dossier_markdown(d)
        assert "not" in text.lower()

    def test_has_evidence_section(self):
        d = _make_dossier()
        text = generate_dossier_markdown(d)
        assert "Evidence" in text

    def test_has_risk_section(self):
        d = _make_dossier()
        text = generate_dossier_markdown(d)
        assert "Risk" in text


class TestHtmlReport:
    """Test HTML report generation."""

    def test_valid_html(self):
        d = _make_dossier()
        text = generate_dossier_html(d)
        assert "<!DOCTYPE html>" in text
        assert "</html>" in text

    def test_no_cdn(self):
        d = _make_dossier()
        text = generate_dossier_html(d)
        assert "cdn" not in text.lower()

    def test_lang_attribute(self):
        d = _make_dossier(language="zh-CN")
        text = generate_dossier_html(d)
        assert 'lang="zh-CN"' in text


class TestIssueReport:
    """Test issue text generation."""

    def test_has_checklist(self):
        d = _make_dossier()
        text = generate_dossier_issue(d)
        assert "- [ ]" in text

    def test_no_auto_posting(self):
        d = _make_dossier()
        text = generate_dossier_issue(d)
        # Should be plain text, not API call
        assert "curl" not in text.lower()


class TestPrCommentReport:
    """Test PR comment text generation."""

    def test_has_summary(self):
        d = _make_dossier()
        text = generate_dossier_pr_comment(d)
        assert "Summary" in text or "summary" in text.lower()


class TestI18nReports:
    """Test i18n in reports."""

    def test_zh_cn_markdown(self):
        d = _make_dossier(language="zh-CN")
        text = generate_dossier_markdown(d)
        assert any("一" <= c <= "鿿" for c in text)

    def test_ja_markdown(self):
        d = _make_dossier(language="ja")
        text = generate_dossier_markdown(d)
        assert any("぀" <= c <= "ヿ" for c in text) or \
               any("一" <= c <= "鿿" for c in text)
