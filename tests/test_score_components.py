"""Tests for score components."""

from __future__ import annotations

import pytest

from oss_paper_ci.models import CheckResult, Severity, Status
from oss_paper_ci.scoring import compute_score, compute_score_components


class TestScoreComponents:
    """Test compute_score_components function."""

    def test_returns_dict(self):
        checks = [
            CheckResult(id="META001", title="README", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        components = compute_score_components(checks)
        assert isinstance(components, dict)

    def test_has_readiness_score(self):
        checks = [
            CheckResult(id="META001", title="README", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        components = compute_score_components(checks)
        assert "readiness_score" in components

    def test_has_data_score(self):
        checks = [
            CheckResult(id="DATA001", title="Data", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        components = compute_score_components(checks)
        assert "data_evidence_score" in components

    def test_has_execution_score(self):
        checks = [
            CheckResult(id="EXP001", title="Script", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        components = compute_score_components(checks)
        assert "execution_evidence_score" in components

    def test_has_artifact_score(self):
        checks = [
            CheckResult(id="RES001", title="Results", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        components = compute_score_components(checks)
        assert "artifact_evidence_score" in components

    def test_has_provenance_score(self):
        checks = [
            CheckResult(id="META001", title="README", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        components = compute_score_components(checks)
        assert "provenance_evidence_score" in components

    def test_backward_compatible_score(self):
        """Old score field should still work."""
        checks = [
            CheckResult(id="META001", title="README", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        old_score, _, _ = compute_score(checks)
        components = compute_score_components(checks)
        assert components["readiness_score"] == old_score

    def test_missing_category_gives_negative(self):
        """Category with no checks should return -1."""
        checks = [
            CheckResult(id="META001", title="README", severity=Severity.INFO, status=Status.PASS, message="OK"),
        ]
        components = compute_score_components(checks)
        assert components["data_evidence_score"] == -1
