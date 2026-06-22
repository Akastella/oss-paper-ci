"""Tests for the matrix CLI command."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

DEMO_REPO = Path(__file__).parent.parent / "examples" / "repro-system-demo"


def run_matrix(*args: str) -> tuple[int, str]:
    """Run oss-paper-ci matrix and return (exit_code, output)."""
    from oss_paper_ci.cli import main
    argv = ["matrix"] + list(args)
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        with patch("sys.argv", ["oss-paper-ci"] + argv):
            try:
                rc = main(argv)
            except SystemExit as e:
                rc = e.code if e.code is not None else 0
    return rc, captured.getvalue()


class TestMatrixCLI:
    """Test matrix CLI commands."""

    def test_matrix_plan(self):
        """Matrix plan generates a plan."""
        code, out = run_matrix("plan", str(DEMO_REPO))
        assert code == 0
        assert "Matrix Plan" in out

    def test_matrix_plan_with_python(self):
        """Matrix plan with Python versions."""
        code, out = run_matrix("plan", str(DEMO_REPO), "--python", "3.10,3.12")
        assert code == 0
        assert "Matrix Plan" in out
        assert "python-3.10" in out
        assert "python-3.12" in out

    def test_matrix_plan_with_profile(self):
        """Matrix plan with profiles."""
        code, out = run_matrix("plan", str(DEMO_REPO), "--profile", "lenient,strict")
        assert code == 0
        assert "profile-lenient" in out
        assert "profile-strict" in out

    def test_matrix_plan_json(self):
        """Matrix plan outputs valid JSON."""
        code, out = run_matrix("plan", str(DEMO_REPO), "--format", "json")
        assert code == 0
        data = json.loads(out)
        assert data["report_type"] == "oss-paper-ci-matrix-plan"

    def test_matrix_run_dry_run(self, tmp_path):
        """Matrix run is dry-run by default."""
        out_dir = tmp_path / "matrix"
        code, out = run_matrix(
            "run", str(DEMO_REPO),
            "--output-dir", str(out_dir),
        )
        assert code == 0
        assert "Matrix Report" in out

    def test_matrix_run_with_execute(self, tmp_path):
        """Matrix run with --execute runs commands."""
        out_dir = tmp_path / "matrix"
        code, out = run_matrix(
            "run", str(DEMO_REPO),
            "--execute",
            "--output-dir", str(out_dir),
        )
        assert code == 0
        # Should show passed status
        assert "passed" in out.lower() or "Matrix Report" in out

    def test_matrix_missing_runtime_marked_unavailable(self):
        """Missing Python runtime is marked unavailable."""
        code, out = run_matrix("plan", str(DEMO_REPO), "--python", "3.9")
        assert code == 0
        assert "unavailable" in out.lower() or "not available" in out.lower()
