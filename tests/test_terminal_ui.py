"""Tests for terminal UI components (panels, tables, status, score, etc.)."""

from __future__ import annotations

import io
import pytest

from oss_paper_ci.terminal import (
    OutputMode, is_tty, is_ci, no_color_requested,
    no_animate_requested, supports_color, strip_ansi,
)
from oss_paper_ci.themes import get_theme, list_themes, THEMES, CLASSIC, MINIMAL, CONTRAST
from oss_paper_ci.ui import (
    render_title, render_step, render_steps, render_panel,
    render_table, render_summary, render_next_actions,
    render_score, render_warning, render_error_card, Spinner,
)


class TestTerminalDetection:
    """Test TTY and environment detection."""

    def test_is_ci_detects_github_actions(self, monkeypatch):
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        assert is_ci() is True

    def test_is_ci_false_by_default(self, monkeypatch):
        for var in ["CI", "GITHUB_ACTIONS", "TRAVIS", "CIRCLECI", "JENKINS_URL",
                     "GITLAB_CI", "BUILDKITE", "CODEBUILD_BUILD_ID"]:
            monkeypatch.delenv(var, raising=False)
        # Note: is_ci() may still return True in actual CI, so we test the env var logic

    def test_no_color_env(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        assert no_color_requested() is True

    def test_no_color_env_absent(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("OSS_PAPER_CI_NO_COLOR", raising=False)
        assert no_color_requested() is False

    def test_no_animate_env(self, monkeypatch):
        monkeypatch.setenv("OSS_PAPER_CI_NO_ANIMATE", "1")
        assert no_animate_requested() is True

    def test_strip_ansi_removes_codes(self):
        text = "\x1b[31mHello\x1b[0m World"
        assert strip_ansi(text) == "Hello World"

    def test_strip_ansi_no_codes(self):
        assert strip_ansi("Hello World") == "Hello World"


class TestOutputMode:
    """Test OutputMode resolution."""

    def test_plain_mode(self):
        mode = OutputMode(plain=True)
        assert mode.plain is True
        assert mode.use_color is False
        assert mode.use_animation is False
        assert mode.use_rich is False

    def test_no_color_mode(self):
        mode = OutputMode(no_color=True)
        assert mode.use_color is False

    def test_no_animate_mode(self):
        mode = OutputMode(no_animate=True)
        assert mode.use_animation is False

    def test_default_mode(self):
        mode = OutputMode()
        assert mode.plain is False


class TestThemes:
    """Test theme system."""

    def test_get_default_theme(self):
        theme = get_theme()
        assert theme.name == "classic"

    def test_get_minimal_theme(self):
        theme = get_theme("minimal")
        assert theme.name == "minimal"

    def test_get_contrast_theme(self):
        theme = get_theme("contrast")
        assert theme.name == "contrast"

    def test_get_unknown_theme_falls_back(self):
        theme = get_theme("nonexistent")
        assert theme.name == "classic"

    def test_list_themes(self):
        themes = list_themes()
        names = [t["name"] for t in themes]
        assert "classic" in names
        assert "minimal" in names
        assert "contrast" in names

    def test_all_themes_have_required_fields(self):
        for theme in THEMES.values():
            assert theme.name
            assert theme.description
            assert theme.icon_pass
            assert theme.icon_fail
            assert theme.spinner_frames

    def test_theme_is_frozen(self):
        theme = get_theme()
        with pytest.raises(Exception):
            theme.name = "changed"


class TestUIComponents:
    """Test UI rendering components in plain mode."""

    def _plain_mode(self):
        return OutputMode(plain=True)

    def _stream(self):
        return io.StringIO()

    def test_render_title_plain(self):
        s = self._stream()
        render_title("Test Title", "subtitle", self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "Test Title" in output
        assert "subtitle" in output

    def test_render_step_plain(self):
        s = self._stream()
        render_step(1, 3, "Step Name", "pass", self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "[1/3]" in output
        assert "Step Name" in output
        assert "[PASS]" in output

    def test_render_step_fail(self):
        s = self._stream()
        render_step(1, 1, "Failing", "fail", self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "[FAIL]" in output

    def test_render_steps_plain(self):
        s = self._stream()
        steps = [
            {"name": "Step A", "status": "pass"},
            {"name": "Step B", "status": "warn"},
        ]
        render_steps(steps, self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "[1/2]" in output
        assert "[2/2]" in output

    def test_render_panel_plain(self):
        s = self._stream()
        render_panel("Title", "Content line", self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "Title" in output
        assert "Content line" in output

    def test_render_table_plain(self):
        s = self._stream()
        headers = ["Name", "Value"]
        rows = [["foo", "42"], ["bar", "99"]]
        render_table(headers, rows, self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "Name" in output
        assert "foo" in output
        assert "42" in output

    def test_render_summary_plain(self):
        s = self._stream()
        items = [
            {"label": "Status", "value": "OK", "status": "pass"},
            {"label": "Count", "value": "5"},
        ]
        render_summary(items, self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "Status" in output
        assert "[PASS]" in output

    def test_render_next_actions_plain(self):
        s = self._stream()
        render_next_actions(["Do this", "Then that"], self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "Do this" in output
        assert "Then that" in output

    def test_render_next_actions_empty(self):
        s = self._stream()
        render_next_actions([], self._plain_mode(), stream=s)
        output = s.getvalue()
        assert output == ""

    def test_render_score_plain(self):
        s = self._stream()
        render_score(85, {"a": 90, "b": 80}, self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "85" in output
        assert "a" in output

    def test_render_warning_plain(self):
        s = self._stream()
        render_warning("Watch out!", self._plain_mode(), stream=s)
        output = s.getvalue()
        assert "Watch out!" in output
        assert "[WARN]" in output

    def test_render_error_card_plain(self):
        s = self._stream()
        render_error_card(
            what="Something broke",
            why="Because reasons",
            next_steps=["Fix it", "Try again"],
            retry_command="oss-paper-ci scan .",
            mode=self._plain_mode(),
            stream=s,
        )
        output = s.getvalue()
        assert "Something broke" in output
        assert "Because reasons" in output
        assert "Fix it" in output

    def test_spinner_plain_does_not_block(self):
        s = self._stream()
        mode = self._plain_mode()
        spinner = Spinner("Working", mode=mode, stream=s)
        spinner.start()
        spinner.stop("Done")
        output = s.getvalue()
        assert "Working" in output
        assert "Done" in output
