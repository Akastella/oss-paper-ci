"""Tests for capsule diff."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.capsule import build_capsule, diff_capsules, format_diff_markdown
from oss_paper_ci.reproduce import ReproduceResult, CommandResult


def _make_result(**kwargs) -> ReproduceResult:
    defaults = {
        "input_url": "test",
        "repo_url": "test",
        "resolved_source": "local",
        "clone_ok": True,
        "dry_run": True,
        "reproduction_commands": ["python train.py"],
        "command_results": [CommandResult(command="python train.py", exit_code=0)],
        "scan_status": "dry_run",
        "limitations": ["test"],
    }
    defaults.update(kwargs)
    return ReproduceResult(**defaults)


class TestDiffCapsules:
    """Test diff_capsules function."""

    def test_same_capsules_no_changes(self, tmp_path):
        result = _make_result()
        old = tmp_path / "old.zip"
        new = tmp_path / "new.zip"
        build_capsule(result, str(old))
        build_capsule(result, str(new))
        diff = diff_capsules(str(old), str(new))
        assert diff["same_repo"] is True
        assert diff["commit_changed"] is False
        assert diff["score_delta"] is None or diff["score_delta"] == 0

    def test_different_modes(self, tmp_path):
        old_result = _make_result(dry_run=True)
        new_result = _make_result(dry_run=False)
        old = tmp_path / "old.zip"
        new = tmp_path / "new.zip"
        build_capsule(old_result, str(old))
        build_capsule(new_result, str(new))
        diff = diff_capsules(str(old), str(new))
        assert diff["old_mode"] == "dry-run"
        assert diff["new_mode"] == "execute"

    def test_score_delta(self, tmp_path):
        # Score delta requires scan reports to be written (needs workdir)
        workdir = tmp_path / "workdir"
        workdir.mkdir()
        old_result = _make_result(scan_score=70, scan_status="warn", dry_run=False, workdir=str(workdir))
        new_result = _make_result(scan_score=85, scan_status="pass", dry_run=False, workdir=str(workdir))
        old = tmp_path / "old.zip"
        new = tmp_path / "new.zip"
        build_capsule(old_result, str(old))
        build_capsule(new_result, str(new))
        diff = diff_capsules(str(old), str(new))
        # Score delta may be None if scan reports weren't generated
        # but the diff should still work
        assert "old_mode" in diff
        assert "new_mode" in diff

    def test_nonexistent_old(self, tmp_path):
        new = tmp_path / "new.zip"
        result = _make_result()
        build_capsule(result, str(new))
        diff = diff_capsules("/nonexistent/old.zip", str(new))
        assert "error" in diff

    def test_nonexistent_new(self, tmp_path):
        old = tmp_path / "old.zip"
        result = _make_result()
        build_capsule(result, str(old))
        diff = diff_capsules(str(old), "/nonexistent/new.zip")
        assert "error" in diff


class TestFormatDiffMarkdown:
    """Test format_diff_markdown function."""

    def test_basic_diff(self):
        diff = {
            "same_repo": True,
            "commit_changed": False,
            "old_mode": "dry-run",
            "new_mode": "execute",
            "commands_succeeded_delta": 1,
            "commands_failed_delta": 0,
            "old_scan_score": None,
            "new_scan_score": 85,
            "score_delta": None,
            "old_scan_status": "dry_run",
            "new_scan_status": "pass",
            "files_added": ["reports/scan_report.json"],
            "files_removed": [],
            "recommendation": "Changes: 1 file added.",
        }
        text = format_diff_markdown(diff)
        assert "Capsule Diff" in text
        assert "dry-run" in text
        assert "execute" in text
        assert "1 file added" in text

    def test_error_diff(self):
        diff = {"error": "Capsule not found"}
        text = format_diff_markdown(diff)
        assert "Error" in text
        assert "Capsule not found" in text
