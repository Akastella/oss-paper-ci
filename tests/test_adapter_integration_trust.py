"""Integration tests for adapter registry with trust system."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.trust import build_trust_report


class TestTrustWithAdapters:
    """Test trust report generation still works after adapter migration."""

    def test_trust_report_generates(self, tmp_path):
        """Test that trust reports generate without errors."""
        (tmp_path / "README.md").write_text("# Test\n")
        report = build_trust_report(str(tmp_path))
        assert report is not None
        assert report.schema_version == "0.1"
        assert "status" in report.summary

    def test_trust_report_has_findings_list(self, tmp_path):
        """Test trust report has findings list."""
        (tmp_path / "README.md").write_text("# Test\n")
        report = build_trust_report(str(tmp_path))
        assert isinstance(report.findings, list)
