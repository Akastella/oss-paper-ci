"""Tests for session resume functionality."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.session import create_session, execute_session, get_commands_to_resume
from oss_paper_ci.session_store import save_session, load_session

DEMO_REPO = str(Path(__file__).parent.parent / "examples" / "repro-system-demo")


class TestSessionResume:
    """Test session resume."""

    def test_get_commands_to_resume(self):
        """Get commands that need to be resumed."""
        manifest = create_session(DEMO_REPO, name="test")
        to_resume = get_commands_to_resume(manifest)
        assert len(to_resume) > 0  # All pending commands

    def test_get_commands_to_resume_empty_after_pass(self, tmp_path):
        """No commands to resume after all pass."""
        manifest = create_session(DEMO_REPO, name="test")
        # Mark all as passed
        for cmd in manifest.commands:
            cmd.status = "passed"
        to_resume = get_commands_to_resume(manifest)
        assert len(to_resume) == 0

    def test_resume_skips_passed(self, tmp_path):
        """Resume skips already passed commands."""
        manifest = create_session(DEMO_REPO, name="test")
        if manifest.commands:
            manifest.commands[0].status = "passed"
            to_resume = get_commands_to_resume(manifest)
            assert manifest.commands[0] not in to_resume

    def test_resume_includes_failed(self):
        """Resume includes failed commands."""
        manifest = create_session(DEMO_REPO, name="test")
        if manifest.commands:
            manifest.commands[0].status = "failed"
            to_resume = get_commands_to_resume(manifest)
            assert manifest.commands[0] in to_resume
