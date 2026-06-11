"""Tests for the dossier data model."""

from __future__ import annotations

import pytest

from oss_paper_ci.dossier import Dossier, build_dossier
from oss_paper_ci.evidence_map import EvidenceItem
from oss_paper_ci.remediation import RemediationItem, RiskItem


class TestDossierModel:
    """Test Dossier dataclass."""

    def test_default_values(self):
        d = Dossier()
        assert d.schema_version == "0.1"
        assert d.dossier_type == "oss-paper-ci-reproducibility-dossier"
        assert d.audience == "author"
        assert d.language == "en"

    def test_to_dict(self):
        d = Dossier(audience="reviewer", language="zh-CN")
        result = d.to_dict()
        assert result["audience"] == "reviewer"
        assert result["language"] == "zh-CN"
        assert "evidence_map" in result
        assert "risk_register" in result
        assert "remediation_plan" in result


class TestBuildDossier:
    """Test build_dossier function."""

    def test_build_from_scan(self, tmp_path):
        scan_data = {
            "summary": {"score": 75, "status": "warn"},
            "checks": [
                {"id": "META001", "title": "README", "severity": "info", "status": "pass", "message": "OK"},
                {"id": "ENV001", "title": "Deps", "severity": "error", "status": "fail", "message": "Missing"},
            ],
        }
        scan_file = tmp_path / "scan.json"
        scan_file.write_text(
            __import__("json").dumps(scan_data), encoding="utf-8"
        )

        d = build_dossier(scan_report=str(scan_file), audience="author")
        assert d.audience == "author"
        assert len(d.evidence_map) > 0
        assert d.executive_summary.get("score") == 75

    def test_build_with_audience(self, tmp_path):
        scan_data = {"summary": {"score": 90, "status": "pass"}, "checks": []}
        scan_file = tmp_path / "scan.json"
        scan_file.write_text(
            __import__("json").dumps(scan_data), encoding="utf-8"
        )

        for audience in ("author", "reviewer", "maintainer"):
            d = build_dossier(scan_report=str(scan_file), audience=audience)
            assert d.audience == audience
            assert len(d.audience_notes) > 0

    def test_build_with_language(self, tmp_path):
        scan_data = {"summary": {"score": 50, "status": "fail"}, "checks": []}
        scan_file = tmp_path / "scan.json"
        scan_file.write_text(
            __import__("json").dumps(scan_data), encoding="utf-8"
        )

        for lang in ("en", "zh-CN", "ja"):
            d = build_dossier(scan_report=str(scan_file), language=lang)
            assert d.language == lang
            assert len(d.non_claims) > 0

    def test_build_no_input(self):
        d = build_dossier()
        assert d.evidence_map == []
