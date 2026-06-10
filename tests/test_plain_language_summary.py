"""Tests for plain-language summary generation."""

from __future__ import annotations

import pytest

from oss_paper_ci.guidance import get_plain_language_summary


class TestPlainLanguageSummary:
    """Test plain-language summary generation."""

    def test_dry_run_summary(self):
        summary = get_plain_language_summary(
            mode="dry-run", commands_attempted=0,
            commands_succeeded=0, commands_failed=0,
        )
        assert "dry-run" in summary.lower()
        assert "no commands were executed" in summary.lower()

    def test_no_commands_summary(self):
        summary = get_plain_language_summary(
            mode="execute", commands_attempted=0,
            commands_succeeded=0, commands_failed=0,
        )
        assert "no reproduction commands" in summary.lower()

    def test_success_summary(self):
        summary = get_plain_language_summary(
            mode="execute", commands_attempted=3,
            commands_succeeded=3, commands_failed=0,
        )
        assert "completed successfully" in summary.lower()
        assert "does not prove" in summary.lower()

    def test_failure_summary(self):
        summary = get_plain_language_summary(
            mode="execute", commands_attempted=3,
            commands_succeeded=1, commands_failed=2,
        )
        assert "failed" in summary.lower()
        assert "does not necessarily mean" in summary.lower()

    def test_success_with_scan_score(self):
        summary = get_plain_language_summary(
            mode="execute", commands_attempted=1,
            commands_succeeded=1, commands_failed=0,
            scan_score=85, scan_status="pass",
        )
        assert "85" in summary
        assert "does not prove" in summary.lower()

    def test_no_overclaiming(self):
        summary = get_plain_language_summary(
            mode="execute", commands_attempted=1,
            commands_succeeded=1, commands_failed=0,
        )
        # Should not claim paper is correct
        assert "correct" not in summary.lower() or "does not" in summary.lower()
        assert "prove" not in summary.lower() or "does not prove" in summary.lower()
