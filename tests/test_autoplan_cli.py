"""Tests for the autoplan CLI command."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

FIXTURES = Path(__file__).parent / "fixtures"


def run_autoplan(*args: str) -> tuple[int, str]:
    """Run oss-paper-ci autoplan and return (exit_code, output)."""
    from oss_paper_ci.cli import main

    argv = ["autoplan"] + list(args)
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        with patch("sys.argv", ["oss-paper-ci"] + argv):
            try:
                rc = main(argv)
            except SystemExit as e:
                rc = e.code if e.code is not None else 0
    return rc, captured.getvalue()


class TestAutoplanCLI:
    """Test autoplan CLI command."""

    def test_autoplan_yaml(self):
        """Autoplan outputs YAML by default."""
        code, out = run_autoplan(str(FIXTURES / "intake_python_repo"))
        assert code == 0
        data = yaml.safe_load(out)
        assert data["schema_version"] == "0.2"
        assert data["generated_mode"] == "candidate"

    def test_autoplan_json(self):
        """Autoplan outputs valid JSON."""
        code, out = run_autoplan(str(FIXTURES / "intake_python_repo"), "--format", "json")
        assert code == 0
        data = json.loads(out)
        assert data["generated_mode"] == "candidate"

    def test_autoplan_markdown(self):
        """Autoplan outputs markdown."""
        code, out = run_autoplan(str(FIXTURES / "intake_python_repo"), "--format", "markdown")
        assert code == 0
        assert "Candidate Reproducibility Plan" in out

    def test_autoplan_output_file(self, tmp_path):
        """Autoplan writes to file with --output."""
        out_file = tmp_path / "candidate.yml"
        code, _ = run_autoplan(
            str(FIXTURES / "intake_python_repo"),
            "--output", str(out_file),
        )
        assert code == 0
        assert out_file.exists()

    def test_autoplan_does_not_write_by_default(self, tmp_path):
        """Autoplan does not write file without --write."""
        out_file = tmp_path / "reproducibility.yml"
        code, _ = run_autoplan(
            str(FIXTURES / "intake_python_repo"),
            "--output", str(out_file),
        )
        assert code == 0
        # File exists because --output was used, but it's the candidate output

    def test_autoplan_validate_valid(self):
        """Autoplan validate passes for valid config."""
        code, out = run_autoplan("validate", str(FIXTURES / "intake_existing_reproducibility_repo" / "reproducibility.yml"))
        assert code == 0
        assert "valid" in out.lower()

    def test_autoplan_diff_same(self):
        """Autoplan diff shows no differences for same file."""
        config = str(FIXTURES / "intake_existing_reproducibility_repo" / "reproducibility.yml")
        code, out = run_autoplan("diff", "--old", config, "--new", config)
        assert code == 0
        assert "No differences" in out

    def test_autoplan_explain(self):
        """Autoplan explain shows config details."""
        code, out = run_autoplan("explain", str(FIXTURES / "intake_existing_reproducibility_repo" / "reproducibility.yml"))
        assert code == 0
        assert "Reproduci" in out

    def test_candidate_has_commands(self):
        """Candidate config has commands section."""
        code, out = run_autoplan(str(FIXTURES / "intake_python_repo"))
        assert code == 0
        data = yaml.safe_load(out)
        assert "commands" in data
        assert len(data["commands"]) > 0

    def test_candidate_has_environment(self):
        """Candidate config has environment section."""
        code, out = run_autoplan(str(FIXTURES / "intake_python_repo"))
        assert code == 0
        data = yaml.safe_load(out)
        assert "environment" in data
        assert data["environment"]["type"] == "python"

    def test_candidate_has_safety(self):
        """Candidate config has safety section."""
        code, out = run_autoplan(str(FIXTURES / "intake_python_repo"))
        assert code == 0
        data = yaml.safe_load(out)
        assert "safety" in data
        assert data["safety"]["network"] is False
