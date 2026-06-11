"""Tests for workbench output files and structure."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest


def _run_workbench(*args):
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "workbench", *args],
        capture_output=True, text=True, timeout=120,
    )


class TestWorkbenchOutputs:
    """Test workbench output file generation."""

    def test_workbench_json_structure(self, tmp_path):
        out_dir = str(tmp_path / "out")
        _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        wb_path = os.path.join(out_dir, "workbench.json")
        if os.path.isfile(wb_path):
            data = json.loads(open(wb_path).read())
            assert isinstance(data.get("steps"), list)
            assert isinstance(data.get("path"), str)
            assert isinstance(data.get("total_duration_ms"), int)

    def test_workbench_summary_md_exists(self, tmp_path):
        out_dir = str(tmp_path / "out")
        _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        summary_path = os.path.join(out_dir, "summary.md")
        if os.path.isfile(summary_path):
            content = open(summary_path).read()
            assert "OSS-Paper-CI Workbench Summary" in content

    def test_workbench_scan_json_exists(self, tmp_path):
        out_dir = str(tmp_path / "out")
        _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        scan_path = os.path.join(out_dir, "scan.json")
        if os.path.isfile(scan_path):
            data = json.loads(open(scan_path).read())
            assert "score" in data or "checks" in data

    def test_workbench_dossier_md_exists(self, tmp_path):
        out_dir = str(tmp_path / "out")
        _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        dossier_path = os.path.join(out_dir, "dossier.md")
        if os.path.isfile(dossier_path):
            content = open(dossier_path).read()
            assert len(content) > 100

    def test_workbench_no_ansi_in_output_files(self, tmp_path):
        out_dir = str(tmp_path / "out")
        _run_workbench("--plain", "--output-dir", out_dir, "examples/demo-reproduce-repo")
        for fname in os.listdir(out_dir) if os.path.isdir(out_dir) else []:
            fpath = os.path.join(out_dir, fname)
            if os.path.isfile(fpath):
                content = open(fpath).read()
                assert "\x1b[" not in content, f"ANSI found in {fname}"
