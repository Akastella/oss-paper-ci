"""Tests for evaluation report generation."""

import json
from pathlib import Path

import pytest


REPORTS_DIR = Path(__file__).parent.parent / "examples" / "reports"


class TestEvaluationReports:
    """Test evaluation report files."""

    def test_json_report_exists(self):
        report = REPORTS_DIR / "evaluation_summary.json"
        assert report.exists(), "Run eval to generate report"

    def test_md_report_exists(self):
        report = REPORTS_DIR / "evaluation_summary.md"
        assert report.exists(), "Run eval to generate report"

    def test_html_report_exists(self):
        report = REPORTS_DIR / "evaluation_summary.html"
        assert report.exists(), "Run eval to generate report"

    def test_json_report_valid(self):
        report = REPORTS_DIR / "evaluation_summary.json"
        data = json.loads(report.read_text())
        assert "version" in data
        assert "repos" in data

    def test_html_no_external_cdn(self):
        """HTML should be self-contained."""
        report = REPORTS_DIR / "evaluation_summary.html"
        content = report.read_text()
        assert "cdn." not in content.lower()
        assert "https://cdnjs" not in content
        assert "https://unpkg" not in content

    def test_reports_no_absolute_paths(self):
        """Reports should not contain absolute paths."""
        for report_file in REPORTS_DIR.glob("evaluation_*"):
            content = report_file.read_text()
            assert "C:\\" not in content, f"{report_file.name} has absolute path"
            assert "/home/" not in content
            assert "/Users/" not in content
