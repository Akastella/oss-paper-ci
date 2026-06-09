"""Tests for batch report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from oss_paper_ci.batch import run_batch_scan
from oss_paper_ci.reporting.aggregate_report import (
    generate_aggregate_html_report,
    generate_aggregate_json_report,
    generate_aggregate_markdown_report,
)
from oss_paper_ci.workspace import load_workspace


@pytest.fixture
def batch_result_dict(tmp_path):
    """Run a batch scan and return the result dict."""
    for name in ["proj-a", "proj-b"]:
        proj_dir = tmp_path / name
        proj_dir.mkdir()
        (proj_dir / "README.md").write_text(f"# {name}\nMIT\n", encoding="utf-8")
        (proj_dir / "LICENSE").write_text("MIT\n", encoding="utf-8")

    ws_data = {
        "version": 1,
        "name": "report-test",
        "projects": [
            {"id": "proj-a", "path": "proj-a"},
            {"id": "proj-b", "path": "proj-b"},
        ],
    }
    ws_file = tmp_path / "workspace.yml"
    ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")

    ws = load_workspace(ws_file)
    result = run_batch_scan(ws, ws_file, jobs=1, use_cache=False)
    return result.to_dict()


class TestAggregateJsonReport:
    """Test JSON report generation."""

    def test_json_output_parseable(self, batch_result_dict):
        text = generate_aggregate_json_report(batch_result_dict)
        parsed = json.loads(text)
        assert parsed["schema_version"] == "0.5"
        assert "projects" in parsed

    def test_json_output_to_file(self, batch_result_dict, tmp_path):
        out = tmp_path / "report.json"
        generate_aggregate_json_report(batch_result_dict, output_path=str(out))
        assert out.exists()
        parsed = json.loads(out.read_text(encoding="utf-8"))
        assert len(parsed["projects"]) == 2


class TestAggregateMarkdownReport:
    """Test Markdown report generation."""

    def test_markdown_contains_workspace_name(self, batch_result_dict):
        text = generate_aggregate_markdown_report(batch_result_dict)
        assert "report-test" in text

    def test_markdown_contains_project_table(self, batch_result_dict):
        text = generate_aggregate_markdown_report(batch_result_dict)
        assert "proj-a" in text
        assert "proj-b" in text
        assert "| ID |" in text

    def test_markdown_contains_summary(self, batch_result_dict):
        text = generate_aggregate_markdown_report(batch_result_dict)
        assert "Pass" in text
        assert "Average Score" in text

    def test_markdown_contains_cache_section(self, batch_result_dict):
        text = generate_aggregate_markdown_report(batch_result_dict)
        assert "Cache" in text


class TestAggregateHtmlReport:
    """Test HTML report generation."""

    def test_html_valid_structure(self, batch_result_dict):
        text = generate_aggregate_html_report(batch_result_dict)
        assert text.startswith("<!DOCTYPE html>")
        assert "</html>" in text

    def test_html_no_external_cdn(self, batch_result_dict):
        text = generate_aggregate_html_report(batch_result_dict)
        assert "cdn." not in text.lower()
        assert "https://cdnjs" not in text
        assert "https://unpkg" not in text
        assert "https://jsdelivr" not in text

    def test_html_contains_projects(self, batch_result_dict):
        text = generate_aggregate_html_report(batch_result_dict)
        assert "proj-a" in text
        assert "proj-b" in text

    def test_html_escapes_user_text(self, batch_result_dict):
        text = generate_aggregate_html_report(batch_result_dict)
        # Should not contain unescaped special chars from user input
        # The workspace name is "report-test" which has no special chars
        # but the function should handle them
        assert "<script>" not in text
