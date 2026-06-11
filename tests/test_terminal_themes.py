"""Tests for terminal theme system."""

from __future__ import annotations

import subprocess
import sys
import io

import pytest

from oss_paper_ci.themes import get_theme, list_themes, THEMES
from oss_paper_ci.terminal import OutputMode
from oss_paper_ci.ui import render_title, render_step, render_steps, render_score


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True, text=True, timeout=30,
    )


class TestThemeListCommand:
    """Test 'oss-paper-ci theme list'."""

    def test_theme_list_runs(self):
        result = _run("theme", "list")
        assert result.returncode == 0
        assert "classic" in result.stdout

    def test_theme_list_shows_all_themes(self):
        result = _run("theme", "list")
        assert "minimal" in result.stdout
        assert "contrast" in result.stdout

    def test_theme_list_plain_no_ansi(self):
        result = _run("theme", "list", "--plain")
        assert "\x1b[" not in result.stdout


class TestThemePreviewCommand:
    """Test 'oss-paper-ci theme preview'."""

    def test_theme_preview_classic(self):
        result = _run("theme", "preview", "--theme", "classic", "--plain")
        assert result.returncode == 0
        assert "Theme" in result.stdout

    def test_theme_preview_minimal(self):
        result = _run("theme", "preview", "--theme", "minimal", "--plain")
        assert result.returncode == 0

    def test_theme_preview_contrast(self):
        result = _run("theme", "preview", "--theme", "contrast", "--plain")
        assert result.returncode == 0

    def test_theme_preview_default(self):
        result = _run("theme", "preview", "--plain")
        assert result.returncode == 0


class TestThemeRendering:
    """Test theme-aware rendering."""

    def test_render_with_minimal_theme(self):
        s = io.StringIO()
        mode = OutputMode(plain=True)
        theme = get_theme("minimal")
        render_title("Test", mode=mode, theme=theme, stream=s)
        output = s.getvalue()
        assert "Test" in output

    def test_render_with_contrast_theme(self):
        s = io.StringIO()
        mode = OutputMode(plain=True)
        theme = get_theme("contrast")
        render_score(85, mode=mode, theme=theme, stream=s)
        output = s.getvalue()
        assert "85" in output

    def test_render_steps_with_all_themes(self):
        for name in THEMES:
            s = io.StringIO()
            mode = OutputMode(plain=True)
            theme = get_theme(name)
            render_steps(
                [{"name": "Step", "status": "pass"}],
                mode=mode, theme=theme, stream=s,
            )
            output = s.getvalue()
            assert "Step" in output
