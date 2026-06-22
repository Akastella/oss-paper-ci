"""Tests for the session CLI command."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

FIXTURES = Path(__file__).parent / "fixtures"
DEMO_REPO = Path(__file__).parent.parent / "examples" / "repro-system-demo"


def run_session(*args: str) -> tuple[int, str]:
    """Run oss-paper-ci session and return (exit_code, output)."""
    from oss_paper_ci.cli import main
    argv = ["session"] + list(args)
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        with patch("sys.argv", ["oss-paper-ci"] + argv):
            try:
                rc = main(argv)
            except SystemExit as e:
                rc = e.code if e.code is not None else 0
    return rc, captured.getvalue()


class TestSessionCLI:
    """Test session CLI commands."""

    def test_session_start_creates_session(self, tmp_path):
        """Session start creates a session directory."""
        out_dir = tmp_path / "session"
        code, out = run_session(
            "start", str(DEMO_REPO),
            "--name", "test",
            "--output-dir", str(out_dir),
        )
        assert code == 0
        assert (out_dir / "session.json").exists()
        assert "Reproduction Session Report" in out

    def test_session_start_json(self, tmp_path):
        """Session start outputs valid JSON."""
        out_dir = tmp_path / "session"
        code, out = run_session(
            "start", str(DEMO_REPO),
            "--name", "test",
            "--output-dir", str(out_dir),
            "--format", "json",
        )
        assert code == 0
        data = json.loads(out)
        assert data["report_type"] == "oss-paper-ci-reproduction-session"

    def test_session_start_has_commands(self, tmp_path):
        """Session start includes commands from config."""
        out_dir = tmp_path / "session"
        code, out = run_session(
            "start", str(DEMO_REPO),
            "--name", "test",
            "--output-dir", str(out_dir),
            "--format", "json",
        )
        assert code == 0
        data = json.loads(out)
        assert len(data["commands"]) > 0

    def test_session_start_default_dry_run(self, tmp_path):
        """Session start is dry-run by default."""
        out_dir = tmp_path / "session"
        code, out = run_session(
            "start", str(DEMO_REPO),
            "--name", "test",
            "--output-dir", str(out_dir),
            "--format", "json",
        )
        assert code == 0
        data = json.loads(out)
        assert data["status"] == "planned"
        assert all(c["status"] == "pending" for c in data["commands"])

    def test_session_status(self, tmp_path):
        """Session status shows session info."""
        out_dir = tmp_path / "session"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        code, out = run_session("status", str(out_dir))
        assert code == 0
        assert "Session:" in out
        assert "Status:" in out

    def test_session_report_markdown(self, tmp_path):
        """Session report generates markdown."""
        out_dir = tmp_path / "session"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        code, out = run_session("report", str(out_dir))
        assert code == 0
        assert "Reproduction Session Report" in out

    def test_session_report_json(self, tmp_path):
        """Session report generates JSON."""
        out_dir = tmp_path / "session"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        code, out = run_session("report", str(out_dir), "--format", "json")
        assert code == 0
        data = json.loads(out)
        assert "session_id" in data

    def test_session_report_html(self, tmp_path):
        """Session report generates self-contained HTML."""
        out_dir = tmp_path / "session"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        code, out = run_session("report", str(out_dir), "--format", "html")
        assert code == 0
        assert "<!DOCTYPE html>" in out

    def test_session_resume_dry_run(self, tmp_path):
        """Session resume is dry-run by default."""
        out_dir = tmp_path / "session"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        code, out = run_session("resume", str(out_dir))
        assert code == 0
        assert "Commands to resume" in out

    def test_session_rerun_failed_dry_run(self, tmp_path):
        """Session rerun-failed is dry-run by default."""
        out_dir = tmp_path / "session"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        code, out = run_session("rerun-failed", str(out_dir))
        assert code == 0
        # No failed commands yet
        assert "No failed commands" in out

    def test_session_bundle(self, tmp_path):
        """Session bundle creates a ZIP."""
        out_dir = tmp_path / "session"
        bundle = tmp_path / "evidence.zip"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        code, out = run_session("bundle", str(out_dir), "--output", str(bundle))
        assert code == 0
        assert bundle.exists()

    def test_session_verify_bundle(self, tmp_path):
        """Session verify-bundle verifies a bundle."""
        out_dir = tmp_path / "session"
        bundle = tmp_path / "evidence.zip"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        run_session("bundle", str(out_dir), "--output", str(bundle))
        code, out = run_session("verify-bundle", str(bundle))
        assert code == 0
        assert "Valid" in out

    def test_session_inspect(self, tmp_path):
        """Session inspect shows bundle contents."""
        out_dir = tmp_path / "session"
        bundle = tmp_path / "evidence.zip"
        run_session("start", str(DEMO_REPO), "--name", "test", "--output-dir", str(out_dir))
        run_session("bundle", str(out_dir), "--output", str(bundle))
        code, out = run_session("inspect", str(bundle))
        assert code == 0
        assert "Session Bundle Inspection" in out
