"""Tests for intake report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.intake import run_intake
from oss_paper_ci.reporting.intake_report import (
    generate_intake_json,
    generate_intake_markdown,
    generate_intake_html,
)


FIXTURES = Path(__file__).parent / "fixtures"


class TestIntakeReports:
    """Test intake report generation."""

    def test_json_report_valid(self):
        """JSON report is valid JSON."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        text = generate_intake_json(report)
        data = json.loads(text)
        assert data["report_type"] == "oss-paper-ci-intake-report"

    def test_json_report_has_schema_version(self):
        """JSON report has schema_version."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        data = json.loads(generate_intake_json(report))
        assert "schema_version" in data

    def test_json_report_has_source(self):
        """JSON report has source section."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        data = json.loads(generate_intake_json(report))
        assert "source" in data
        assert data["source"]["kind"] == "local"

    def test_json_report_has_detected(self):
        """JSON report has detected section."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        data = json.loads(generate_intake_json(report))
        assert "detected" in data
        assert "ecosystems" in data["detected"]

    def test_json_report_has_confidence(self):
        """JSON report has confidence section."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        data = json.loads(generate_intake_json(report))
        assert "confidence" in data
        assert "overall" in data["confidence"]

    def test_markdown_report_has_header(self):
        """Markdown report has header."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        text = generate_intake_markdown(report)
        assert "Repository Intake Report" in text

    def test_markdown_report_has_ecosystems(self):
        """Markdown report lists ecosystems."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        text = generate_intake_markdown(report)
        assert "Python" in text

    def test_markdown_report_has_commands(self):
        """Markdown report lists command candidates."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        text = generate_intake_markdown(report)
        assert "Command Candidates" in text

    def test_markdown_report_has_confidence(self):
        """Markdown report shows confidence scores."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        text = generate_intake_markdown(report)
        assert "Confidence Scores" in text

    def test_html_report_self_contained(self):
        """HTML report is self-contained (no external CDN)."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        text = generate_intake_html(report)
        assert "<!DOCTYPE html>" in text
        assert "cdn" not in text.lower()
        assert "googleapis" not in text.lower()

    def test_html_report_has_styles(self):
        """HTML report has inline styles."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        text = generate_intake_html(report)
        assert "<style>" in text

    def test_json_report_output_file(self, tmp_path):
        """JSON report writes to file."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        out_file = tmp_path / "report.json"
        generate_intake_json(report, str(out_file))
        assert out_file.exists()
        data = json.loads(out_file.read_text(encoding="utf-8"))
        assert data["report_type"] == "oss-paper-ci-intake-report"

    def test_markdown_report_output_file(self, tmp_path):
        """Markdown report writes to file."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        out_file = tmp_path / "report.md"
        generate_intake_markdown(report, str(out_file))
        assert out_file.exists()
        text = out_file.read_text(encoding="utf-8")
        assert "Repository Intake Report" in text

    def test_html_report_output_file(self, tmp_path):
        """HTML report writes to file."""
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        out_file = tmp_path / "report.html"
        generate_intake_html(report, str(out_file))
        assert out_file.exists()
        text = out_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in text
