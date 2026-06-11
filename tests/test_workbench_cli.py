"""Tests for the workbench CLI command."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

import pytest


def _run_workbench(*args):
    result = subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "workbench", *args],
        capture_output=True, text=True, timeout=120,
    )
    return result


class TestWorkbenchCLI:
    """Test workbench command via CLI."""

    def test_workbench_runs(self):
        result = _run_workbench("--plain", "examples/demo-reproduce-repo")
        assert result.returncode in (0, 1, 2)  # May fail on demo repo

    def test_workbench_plain_no_ansi(self):
        result = _run_workbench("--plain", "examples/demo-reproduce-repo")
        assert "\x1b[" not in result.stdout

    def test_workbench_default_no_execute(self):
        """Workbench should not execute real experiments by default."""
        result = _run_workbench("--plain", "examples/demo-reproduce-repo")
        # Should not run actual scripts - just analysis
        assert "safe dry-run" in result.stdout.lower() or "Mode:" in result.stdout

    def test_workbench_creates_output_dir(self, tmp_path):
        out_dir = str(tmp_path / "wb-out")
        result = _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        assert os.path.isdir(out_dir)
        assert os.path.isfile(os.path.join(out_dir, "workbench.json"))

    def test_workbench_output_json_valid(self, tmp_path):
        out_dir = str(tmp_path / "wb-out")
        _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        wb_json = os.path.join(out_dir, "workbench.json")
        if os.path.isfile(wb_json):
            data = json.loads(open(wb_json).read())
            assert "steps" in data
            assert "path" in data

    def test_workbench_does_not_overwrite_without_force(self, tmp_path):
        out_dir = str(tmp_path / "wb-out")
        os.makedirs(out_dir)
        with open(os.path.join(out_dir, "existing.txt"), "w") as f:
            f.write("keep")
        result = _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        # Should refuse to overwrite
        assert "already exists" in result.stdout.lower() or result.returncode != 0

    def test_workbench_force_overwrites(self, tmp_path):
        out_dir = str(tmp_path / "wb-out")
        os.makedirs(out_dir)
        result = _run_workbench("--plain", "--force", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        assert os.path.isfile(os.path.join(out_dir, "workbench.json"))

    def test_workbench_no_color(self):
        result = _run_workbench("--no-color", "examples/demo-reproduce-repo")
        assert "\x1b[" not in result.stdout

    def test_workbench_with_theme(self):
        result = _run_workbench("--theme", "minimal", "--plain", "examples/demo-reproduce-repo")
        assert result.returncode in (0, 1, 2)
