"""Integration tests for adapter registry with evidence system."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.evidence import build_evidence_report


class TestEvidenceWithAdapters:
    """Test evidence report generation with adapter-based ecosystem detection."""

    def test_evidence_report_includes_ecosystems(self, tmp_path):
        """Test that evidence reports include ecosystem section from adapters."""
        # Create a minimal repo
        (tmp_path / "pyproject.toml").write_text('[project]\nname="test"\nversion="0.1"\n')
        (tmp_path / "main.py").write_text("print('hello')\n")
        (tmp_path / "README.md").write_text("# Test\n")

        report = build_evidence_report(str(tmp_path), profile="reviewer")
        assert report is not None
        assert "ecosystems" in report.sections

    def test_evidence_report_ecosystem_format(self, tmp_path):
        """Test ecosystem section format in evidence report."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname="test"\n')
        (tmp_path / "README.md").write_text("# Test\n")

        report = build_evidence_report(str(tmp_path))
        eco_section = report.sections.get("ecosystems", {})
        assert "detected" in eco_section
        assert "total" in eco_section
