"""Tests for --plain, --no-color, --no-animate flags and NO_COLOR support."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest


def _run(*args, env_extra=None):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True, text=True, timeout=30, env=env,
    )


class TestPlainMode:
    """Test --plain flag."""

    def test_wizard_plain_no_ansi(self):
        result = _run("wizard", "--plain", ".")
        assert "\x1b[" not in result.stdout

    def test_theme_preview_plain_no_ansi(self):
        result = _run("theme", "preview", "--plain")
        assert "\x1b[" not in result.stdout

    def test_workbench_plain_no_ansi(self):
        result = _run("workbench", "--plain", "examples/demo-reproduce-repo")
        assert "\x1b[" not in result.stdout

    def test_version_no_ansi(self):
        result = _run("version")
        assert "\x1b[" not in result.stdout


class TestNoColorEnv:
    """Test NO_COLOR environment variable."""

    def test_no_color_wizard(self):
        result = _run("wizard", ".", env_extra={"NO_COLOR": "1"})
        assert "\x1b[" not in result.stdout

    def test_no_color_theme_preview(self):
        result = _run("theme", "preview", env_extra={"NO_COLOR": "1"})
        assert "\x1b[" not in result.stdout


class TestNoAnimateEnv:
    """Test OSS_PAPER_CI_NO_ANIMATE environment variable."""

    def test_no_animate_wizard(self):
        result = _run("wizard", ".", env_extra={"OSS_PAPER_CI_NO_ANIMATE": "1"})
        assert result.returncode == 0

    def test_no_animate_workbench(self):
        result = _run("workbench", "examples/demo-reproduce-repo",
                       env_extra={"OSS_PAPER_CI_NO_ANIMATE": "1"})
        assert result.returncode in (0, 1, 2)


class TestPlainEnv:
    """Test OSS_PAPER_CI_PLAIN environment variable."""

    def test_plain_env_wizard(self):
        result = _run("wizard", ".", env_extra={"OSS_PAPER_CI_PLAIN": "1"})
        assert "\x1b[" not in result.stdout


class TestNoColorFlag:
    """Test --no-color flag."""

    def test_no_color_flag_wizard(self):
        result = _run("wizard", "--no-color", ".")
        assert "\x1b[" not in result.stdout

    def test_no_color_flag_theme_preview(self):
        result = _run("theme", "preview", "--no-color")
        assert "\x1b[" not in result.stdout


class TestNoAnimateFlag:
    """Test --no-animate flag."""

    def test_no_animate_flag_wizard(self):
        result = _run("wizard", "--no-animate", ".")
        assert result.returncode == 0
