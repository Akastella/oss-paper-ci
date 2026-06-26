"""Tests for the intake CLI command."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def run_intake(*args: str) -> tuple[int, str]:
    """Run oss-paper-ci intake and return (exit_code, output)."""
    # Use direct import to avoid Windows subprocess stdout reconfiguration issues
    import io
    from unittest.mock import patch
    from oss_paper_ci.cli import main

    argv = ["intake"] + list(args)
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        with patch("sys.argv", ["oss-paper-ci"] + argv):
            try:
                rc = main(argv)
            except SystemExit as e:
                rc = e.code if e.code is not None else 0
    return rc, captured.getvalue()


class TestIntakeCLI:
    """Test intake CLI command."""

    def test_intake_markdown(self):
        """Intake outputs markdown by default."""
        code, out = run_intake(str(FIXTURES / "intake_python_repo"))
        assert code == 0
        assert "Repository Intake Report" in out
        assert "Python" in out

    def test_intake_json(self):
        """Intake outputs valid JSON."""
        code, out = run_intake(str(FIXTURES / "intake_python_repo"), "--format", "json")
        assert code == 0
        data = json.loads(out)
        assert data["report_type"] == "oss-paper-ci-intake-report"
        assert data["tool_version"] == "3.6.0rc1"

    def test_intake_html(self):
        """Intake outputs self-contained HTML."""
        code, out = run_intake(str(FIXTURES / "intake_python_repo"), "--format", "html")
        assert code == 0
        assert "<!DOCTYPE html>" in out
        assert "oss-paper-ci" in out

    def test_intake_output_file(self, tmp_path):
        """Intake writes to file with --output."""
        out_file = tmp_path / "report.md"
        code, _ = run_intake(
            str(FIXTURES / "intake_python_repo"),
            "--format", "markdown",
            "--output", str(out_file),
        )
        assert code == 0
        assert out_file.exists()
        text = out_file.read_text(encoding="utf-8")
        assert "Repository Intake Report" in text

    def test_intake_paper_url_warning(self):
        """Intake warns about paper URL."""
        code, out = run_intake("https://arxiv.org/abs/2401.00001")
        assert code == 0
        assert "Paper URL alone is not enough" in out

    def test_intake_github_url_no_clone(self):
        """Intake warns about GitHub URL without --clone."""
        code, out = run_intake("https://github.com/owner/repo")
        assert code == 0
        assert "Use --clone" in out

    def test_intake_detects_ecosystems(self):
        """Intake detects language ecosystems."""
        code, out = run_intake(str(FIXTURES / "intake_python_repo"), "--format", "json")
        assert code == 0
        data = json.loads(out)
        assert "python" in data["detected"]["languages"]

    def test_intake_detects_commands(self):
        """Intake detects command candidates."""
        code, out = run_intake(str(FIXTURES / "intake_python_repo"), "--format", "json")
        assert code == 0
        data = json.loads(out)
        assert len(data["command_candidates"]) > 0

    def test_intake_detects_dangerous(self):
        """Intake flags dangerous commands."""
        code, out = run_intake(str(FIXTURES / "intake_unsafe_commands_repo"), "--format", "json")
        assert code == 0
        data = json.loads(out)
        dangerous = [c for c in data["command_candidates"] if c.get("dangerous")]
        assert len(dangerous) >= 1

    def test_intake_existing_config(self):
        """Intake detects existing reproducibility.yml."""
        code, out = run_intake(str(FIXTURES / "intake_existing_reproducibility_repo"), "--format", "json")
        assert code == 0
        data = json.loads(out)
        assert data["detected"]["has_existing_config"] is True
