"""Tests for risk register."""

from __future__ import annotations

import pytest

from oss_paper_ci.remediation import RiskItem, build_risk_register_from_scan


class TestRiskItem:
    """Test RiskItem dataclass."""

    def test_to_dict(self):
        risk = RiskItem(
            risk_id="missing_env",
            title="Missing environment",
            severity="high",
            likelihood="high",
            impact="Cannot install deps",
            evidence="ENV001 failed",
            mitigation="Add requirements.txt",
            does_not_mean="Code is broken",
        )
        d = risk.to_dict()
        assert d["risk_id"] == "missing_env"
        assert d["severity"] == "high"
        assert d["does_not_mean"] != ""


class TestBuildFromScan:
    """Test risk register from scan data."""

    def test_missing_env_risk(self):
        scan_data = {
            "checks": [
                {"id": "ENV001", "title": "Deps", "severity": "error", "status": "fail", "message": "No requirements.txt"},
            ],
        }
        risks = build_risk_register_from_scan(scan_data)
        assert len(risks) >= 1
        assert risks[0].risk_id == "missing_environment"
        assert risks[0].does_not_mean != ""

    def test_no_risks_when_passing(self):
        scan_data = {
            "checks": [
                {"id": "ENV001", "title": "Deps", "severity": "info", "status": "pass", "message": "OK"},
            ],
        }
        risks = build_risk_register_from_scan(scan_data)
        assert len(risks) == 0
