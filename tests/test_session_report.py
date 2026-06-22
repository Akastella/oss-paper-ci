"""Tests for session report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.session import create_session
from oss_paper_ci.session_report import (
    generate_session_json,
    generate_session_markdown,
    generate_session_html,
)

DEMO_REPO = str(Path(__file__).parent.parent / "examples" / "repro-system-demo")


class TestSessionReport:
    """Test session report generation."""

    def test_json_report_valid(self):
        """JSON report is valid JSON."""
        manifest = create_session(DEMO_REPO, name="test")
        text = generate_session_json(manifest)
        data = json.loads(text)
        assert data["report_type"] == "oss-paper-ci-reproduction-session"

    def test_json_has_session_id(self):
        """JSON report has session_id."""
        manifest = create_session(DEMO_REPO, name="test")
        data = json.loads(generate_session_json(manifest))
        assert "session_id" in data
        assert data["session_id"]

    def test_json_has_commands(self):
        """JSON report has commands."""
        manifest = create_session(DEMO_REPO, name="test")
        data = json.loads(generate_session_json(manifest))
        assert "commands" in data
        assert isinstance(data["commands"], list)

    def test_json_has_summary(self):
        """JSON report has summary."""
        manifest = create_session(DEMO_REPO, name="test")
        data = json.loads(generate_session_json(manifest))
        assert "summary" in data
        assert "total" in data["summary"]

    def test_markdown_has_header(self):
        """Markdown report has header."""
        manifest = create_session(DEMO_REPO, name="test")
        text = generate_session_markdown(manifest)
        assert "Reproduction Session Report" in text

    def test_markdown_has_commands_table(self):
        """Markdown report has commands table."""
        manifest = create_session(DEMO_REPO, name="test")
        text = generate_session_markdown(manifest)
        assert "Commands" in text
        assert "train" in text

    def test_html_self_contained(self):
        """HTML report is self-contained."""
        manifest = create_session(DEMO_REPO, name="test")
        text = generate_session_html(manifest)
        assert "<!DOCTYPE html>" in text
        assert "cdn" not in text.lower()

    def test_json_output_file(self, tmp_path):
        """JSON report writes to file."""
        manifest = create_session(DEMO_REPO, name="test")
        out = tmp_path / "report.json"
        generate_session_json(manifest, str(out))
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["report_type"] == "oss-paper-ci-reproduction-session"

    def test_markdown_output_file(self, tmp_path):
        """Markdown report writes to file."""
        manifest = create_session(DEMO_REPO, name="test")
        out = tmp_path / "report.md"
        generate_session_markdown(manifest, str(out))
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert "Reproduction Session Report" in text

    def test_html_output_file(self, tmp_path):
        """HTML report writes to file."""
        manifest = create_session(DEMO_REPO, name="test")
        out = tmp_path / "report.html"
        generate_session_html(manifest, str(out))
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in text
