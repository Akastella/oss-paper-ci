"""Tests for evidence report schema."""

from __future__ import annotations

import json
from pathlib import Path

from oss_paper_ci.evidence import EvidenceReport, build_evidence_report

DEMO_REPO = Path(__file__).parent.parent / "examples" / "demo-paper-repo"


class TestEvidenceSchema:
    """Test evidence report schema structure."""

    def test_report_structure(self):
        report = build_evidence_report(DEMO_REPO)
        d = report.to_dict()
        assert d["schema_version"] == "0.1"
        assert d["report_type"] == "oss-paper-ci-evidence-report"
        assert d["tool_version"] is not None
        assert "summary" in d
        assert "sections" in d
        assert "findings" in d
        assert "recommended_next_steps" in d
        assert "limitations" in d

    def test_summary_fields(self):
        report = build_evidence_report(DEMO_REPO)
        s = report.summary
        assert "status" in s
        assert "readiness_score" in s
        assert "risk_level" in s
        assert "total_findings" in s
        assert "plain_language_summary" in s

    def test_sections_present(self):
        report = build_evidence_report(DEMO_REPO)
        assert "repository" in report.sections
        assert "reproducibility" in report.sections
        assert "data" in report.sections
        assert "results" in report.sections
        assert "ecosystems" in report.sections

    def test_findings_have_required_fields(self):
        report = build_evidence_report(DEMO_REPO)
        for f in report.findings:
            assert "id" in f
            assert "severity" in f
            assert "category" in f
            assert "title" in f
            assert "message" in f

    def test_json_serializable(self):
        report = build_evidence_report(DEMO_REPO)
        text = json.dumps(report.to_dict(), indent=2)
        data = json.loads(text)
        assert data["schema_version"] == "0.1"

    def test_repo_name_not_absolute(self):
        report = build_evidence_report(DEMO_REPO)
        # repo should be just the name, not an absolute path
        assert "/" not in report.repo
        assert "\\" not in report.repo
