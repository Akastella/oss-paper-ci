"""Tests for the wizard CLI command."""

from __future__ import annotations

import subprocess
import sys

import pytest


def _run_wizard(*args):
    result = subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "wizard", *args],
        capture_output=True, text=True, timeout=30,
        encoding="utf-8", errors="replace",
    )
    return result


class TestWizardCLI:
    """Test wizard command via CLI."""

    def test_wizard_runs(self):
        result = _run_wizard("--plain", ".")
        assert result.returncode == 0
        assert "Wizard" in result.stdout or "wizard" in result.stdout.lower()

    def test_wizard_plain_no_ansi(self):
        result = _run_wizard("--plain", ".")
        # No ANSI escape codes in plain mode
        assert "\x1b[" not in result.stdout

    def test_wizard_non_interactive_no_block(self):
        """Wizard should not block waiting for input in non-TTY."""
        result = _run_wizard("--plain", ".")
        assert result.returncode == 0
        # Should complete within timeout (not hang)

    def test_wizard_shows_repo_info(self):
        result = _run_wizard("--plain", ".")
        # Wizard should show repo info (Git, Config, Path, etc.)
        # Git detection depends on .git directory existing
        assert "Path:" in result.stdout or "Repository" in result.stdout

    def test_wizard_shows_recommendations(self):
        result = _run_wizard("--plain", ".")
        assert "oss-paper-ci" in result.stdout

    def test_wizard_with_no_color(self):
        result = _run_wizard("--no-color", ".")
        assert result.returncode == 0
        assert "\x1b[" not in result.stdout

    def test_wizard_with_no_animate(self):
        result = _run_wizard("--no-animate", ".")
        assert result.returncode == 0

    def test_wizard_version_shows_current(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "version"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
        )
        assert "2.6.0rc1" in result.stdout
