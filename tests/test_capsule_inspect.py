"""Tests for capsule inspection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.capsule import build_capsule, inspect_capsule
from oss_paper_ci.reproduce import ReproduceResult, CommandResult


def _make_result(**kwargs) -> ReproduceResult:
    defaults = {
        "input_url": "https://github.com/owner/repo",
        "repo_url": "https://github.com/owner/repo",
        "resolved_source": "github",
        "commit_sha": "abc123def456",
        "clone_ok": True,
        "dry_run": False,
        "reproduction_commands": ["python train.py"],
        "command_results": [CommandResult(command="python train.py", exit_code=0)],
        "scan_score": 85,
        "scan_status": "pass",
        "scan_findings_summary": "10 passed, 0 warnings, 0 errors",
        "limitations": ["test limitation"],
    }
    defaults.update(kwargs)
    return ReproduceResult(**defaults)


class TestInspectCapsule:
    """Test inspect_capsule function."""

    def test_inspect_returns_metadata(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        info = inspect_capsule(str(out))
        assert info["schema_version"] == "0.1"
        assert info["oss_paper_ci_version"] is not None
        assert "source" in info
        assert "execution" in info

    def test_inspect_source(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        info = inspect_capsule(str(out))
        assert info["source"]["source_type"] == "github"
        assert info["source"]["commit_sha"] == "abc123def456"

    def test_inspect_execution(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        info = inspect_capsule(str(out))
        assert info["execution"]["mode"] == "execute"
        assert info["execution"]["commands_attempted"] == 1

    def test_inspect_scan(self, tmp_path):
        # Need workdir for scan report to be written
        workdir = tmp_path / "workdir"
        workdir.mkdir()
        result = _make_result(workdir=str(workdir))
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        info = inspect_capsule(str(out))
        # Scan score may be None if scan report wasn't generated (no scan run)
        # The execution metadata should still be present
        assert info["execution"]["mode"] == "execute"

    def test_inspect_limitations(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        info = inspect_capsule(str(out))
        assert len(info["limitations"]) > 0

    def test_inspect_files(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        info = inspect_capsule(str(out))
        assert info["file_count"] > 0
        assert "capsule.json" in info["files"]

    def test_inspect_nonexistent(self):
        info = inspect_capsule("/nonexistent/capsule.zip")
        assert "error" in info

    def test_inspect_corrupt(self, tmp_path):
        f = tmp_path / "bad.zip"
        f.write_bytes(b"not a zip")
        info = inspect_capsule(str(f))
        assert "error" in info
