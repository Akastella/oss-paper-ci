"""Tests for reproduction report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.environment import EnvironmentPlan, EnvironmentFile, InstallStep
from oss_paper_ci.reproduce import CommandResult, ReproduceResult
from oss_paper_ci.reporting.reproduce_report import (
    generate_reproduce_html_report,
    generate_reproduce_json_report,
    generate_reproduce_markdown_report,
)


def _make_result(**kwargs) -> ReproduceResult:
    """Create a ReproduceResult with sensible defaults."""
    defaults = {
        "input_url": "https://github.com/owner/repo",
        "repo_url": "https://github.com/owner/repo",
        "resolved_source": "github",
        "clone_ok": True,
        "dry_run": True,
        "environment": EnvironmentPlan(
            environment_files=[EnvironmentFile("requirements.txt", "requirements.txt")],
            install_steps=[InstallStep("Install deps", "pip install -r requirements.txt", "pip")],
        ),
        "reproduction_commands": ["python scripts/train.py"],
        "command_results": [CommandResult(command="python scripts/train.py", exit_code=0, block_reason="dry_run")],
        "scan_status": "dry_run",
        "limitations": ["This is a test limitation."],
    }
    defaults.update(kwargs)
    return ReproduceResult(**defaults)


class TestJsonReport:
    """Test JSON report generation."""

    def test_valid_json(self):
        result = _make_result()
        text = generate_reproduce_json_report(result)
        data = json.loads(text)
        assert data["schema_version"] == "1.0"
        assert data["report_type"] == "reproduction"
        assert data["input_url"] == "https://github.com/owner/repo"

    def test_json_has_all_fields(self):
        result = _make_result()
        text = generate_reproduce_json_report(result)
        data = json.loads(text)
        assert "environment" in data
        assert "command_results" in data
        assert "limitations" in data

    def test_json_output_to_file(self, tmp_path):
        result = _make_result()
        out = tmp_path / "report.json"
        generate_reproduce_json_report(result, output_path=str(out))
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["report_type"] == "reproduction"


class TestMarkdownReport:
    """Test Markdown report generation."""

    def test_contains_title(self):
        result = _make_result()
        text = generate_reproduce_markdown_report(result)
        assert "Reproduction Attempt Report" in text

    def test_contains_disclaimer(self):
        result = _make_result()
        text = generate_reproduce_markdown_report(result)
        assert "Disclaimer" in text
        assert "attempted reproduction" in text.lower()

    def test_contains_input_url(self):
        result = _make_result()
        text = generate_reproduce_markdown_report(result)
        assert "https://github.com/owner/repo" in text

    def test_dry_run_mode_text(self):
        result = _make_result(dry_run=True)
        text = generate_reproduce_markdown_report(result)
        assert "dry-run" in text

    def test_contains_limitations(self):
        result = _make_result()
        text = generate_reproduce_markdown_report(result)
        assert "Limitations" in text
        assert "test limitation" in text

    def test_output_to_file(self, tmp_path):
        result = _make_result()
        out = tmp_path / "report.md"
        generate_reproduce_markdown_report(result, output_path=str(out))
        assert out.exists()
        assert "Reproduction Attempt Report" in out.read_text(encoding="utf-8")

    def test_rerun_section_for_local(self):
        result = _make_result(
            resolved_source="local",
            repo_url="/tmp/test-repo",
        )
        text = generate_reproduce_markdown_report(result)
        assert "cd /tmp/test-repo" in text


class TestHtmlReport:
    """Test HTML report generation."""

    def test_valid_html(self):
        result = _make_result()
        text = generate_reproduce_html_report(result)
        assert "<!DOCTYPE html>" in text
        assert "</html>" in text

    def test_no_external_cdn(self):
        result = _make_result()
        text = generate_reproduce_html_report(result)
        assert "cdn" not in text.lower()
        assert "googleapis" not in text.lower()
        assert "cloudflare" not in text.lower()

    def test_escapes_html_in_urls(self):
        result = _make_result(input_url="<script>alert('xss')</script>")
        text = generate_reproduce_html_report(result)
        assert "<script>" not in text
        assert "&lt;script&gt;" in text

    def test_contains_disclaimer(self):
        result = _make_result()
        text = generate_reproduce_html_report(result)
        assert "attempted reproduction" in text.lower()

    def test_output_to_file(self, tmp_path):
        result = _make_result()
        out = tmp_path / "report.html"
        generate_reproduce_html_report(result, output_path=str(out))
        assert out.exists()
        assert "<!DOCTYPE html>" in out.read_text()


class TestReportWithErrors:
    """Test report generation with error conditions."""

    def test_report_with_error(self):
        result = _make_result(error="Something went wrong")
        text = generate_reproduce_markdown_report(result)
        assert "Error" in text
        assert "Something went wrong" in text

    def test_report_with_warnings(self):
        result = _make_result(warnings=["Warning 1", "Warning 2"])
        text = generate_reproduce_markdown_report(result)
        assert "Warning 1" in text
        assert "Warning 2" in text

    def test_report_with_failed_command(self):
        result = _make_result(
            command_results=[
                CommandResult(command="python train.py", exit_code=1, stderr_excerpt="Error!")
            ],
            dry_run=False,
        )
        text = generate_reproduce_markdown_report(result)
        assert "FAILED" in text
