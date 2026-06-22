"""Tests for session store persistence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.session import create_session, SessionManifest
from oss_paper_ci.session_store import (
    save_session, load_session, list_sessions,
    update_command_status, compute_session_checksums, save_checksums,
)

DEMO_REPO = str(Path(__file__).parent.parent / "examples" / "repro-system-demo")


class TestSessionStore:
    """Test session persistence."""

    def test_save_and_load_session(self, tmp_path):
        """Save and load a session."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        loaded = load_session(session_dir)
        assert loaded.session_id == manifest.session_id
        assert loaded.name == "test"

    def test_save_creates_directory_structure(self, tmp_path):
        """Save creates expected directory structure."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = tmp_path / "session"
        save_session(manifest, str(session_dir))

        assert (session_dir / "session.json").exists()
        assert (session_dir / "plan.json").exists()
        assert (session_dir / "runs").exists()

    def test_save_creates_command_dirs(self, tmp_path):
        """Save creates per-command directories."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = tmp_path / "session"
        save_session(manifest, str(session_dir))

        for cmd in manifest.commands:
            cmd_dir = session_dir / "runs" / cmd.command_id
            assert cmd_dir.exists()
            assert (cmd_dir / "command.json").exists()

    def test_list_sessions(self, tmp_path):
        """List sessions in a directory."""
        manifest1 = create_session(DEMO_REPO, name="session1")
        manifest2 = create_session(DEMO_REPO, name="session2")

        base_dir = tmp_path / "sessions"
        save_session(manifest1, str(base_dir / "session1"))
        save_session(manifest2, str(base_dir / "session2"))

        sessions = list_sessions(str(base_dir))
        assert len(sessions) == 2
        names = {s["name"] for s in sessions}
        assert "session1" in names
        assert "session2" in names

    def test_update_command_status(self, tmp_path):
        """Update command status in a session."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        if manifest.commands:
            cmd_id = manifest.commands[0].command_id
            update_command_status(
                session_dir, cmd_id,
                status="passed", exit_code=0, duration_seconds=1.5,
            )
            loaded = load_session(session_dir)
            cmd = next(c for c in loaded.commands if c.command_id == cmd_id)
            assert cmd.status == "passed"
            assert cmd.exit_code == 0

    def test_checksums(self, tmp_path):
        """Compute and save checksums."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        checksums = compute_session_checksums(session_dir)
        assert len(checksums) > 0
        assert "session.json" in checksums

        sha_path = save_checksums(session_dir)
        assert Path(sha_path).exists()

    def test_load_nonexistent_raises(self):
        """Loading nonexistent session raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_session("/nonexistent/path")
