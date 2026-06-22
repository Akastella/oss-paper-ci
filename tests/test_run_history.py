"""Tests for run history tracking."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.run_history import record_attempt, load_command_history


class TestRunHistory:
    """Test run history tracking."""

    def test_record_attempt(self, tmp_path):
        """Record a run attempt."""
        history_dir = str(tmp_path / "history" / "train")
        attempt = record_attempt(
            history_dir, "train", "python scripts/train.py",
            status="passed", exit_code=0, duration_seconds=1.5,
        )
        assert attempt.attempt_number == 1
        assert attempt.status == "passed"

    def test_load_history(self, tmp_path):
        """Load command history."""
        history_dir = str(tmp_path / "history" / "train")
        record_attempt(
            history_dir, "train", "python scripts/train.py",
            status="passed", exit_code=0, duration_seconds=1.5,
        )
        history = load_command_history(history_dir)
        assert history.command_id == "train"
        assert history.total_attempts == 1

    def test_multiple_attempts(self, tmp_path):
        """Record multiple attempts."""
        history_dir = str(tmp_path / "history" / "train")
        record_attempt(
            history_dir, "train", "python scripts/train.py",
            status="failed", exit_code=1, duration_seconds=0.5,
        )
        record_attempt(
            history_dir, "train", "python scripts/train.py",
            status="passed", exit_code=0, duration_seconds=1.5,
        )
        history = load_command_history(history_dir)
        assert history.total_attempts == 2
        assert history.current_status == "passed"

    def test_best_duration(self, tmp_path):
        """Best duration returns fastest passed attempt."""
        history_dir = str(tmp_path / "history" / "train")
        record_attempt(
            history_dir, "train", "python scripts/train.py",
            status="passed", exit_code=0, duration_seconds=2.0,
        )
        record_attempt(
            history_dir, "train", "python scripts/train.py",
            status="passed", exit_code=0, duration_seconds=1.0,
        )
        history = load_command_history(history_dir)
        assert history.best_duration == 1.0

    def test_empty_history(self, tmp_path):
        """Empty history has no attempts."""
        history = load_command_history(str(tmp_path / "nonexistent"))
        assert history.total_attempts == 0
