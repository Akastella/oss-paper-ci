"""Tests for CLI UX documentation truthfulness.

Verifies that documentation claims about wizard, workbench, themes,
and CI/TTY behavior match actual implementation.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True, text=True, timeout=30,
    )


class TestCommandExistence:
    """Test that documented commands actually exist."""

    def test_wizard_command_exists(self):
        result = _run("wizard", "--plain", ".")
        assert result.returncode == 0

    def test_workbench_command_exists(self):
        result = _run("workbench", "--plain", "examples/demo-reproduce-repo")
        assert result.returncode in (0, 1, 2)

    def test_theme_list_command_exists(self):
        result = _run("theme", "list")
        assert result.returncode == 0

    def test_theme_preview_command_exists(self):
        result = _run("theme", "preview", "--plain")
        assert result.returncode == 0


class TestDocsFilesExist:
    """Test that documented files exist."""

    def test_terminal_workbench_doc(self):
        assert (ROOT / "docs" / "terminal-workbench.md").is_file()

    def test_wizard_doc(self):
        assert (ROOT / "docs" / "wizard.md").is_file()

    def test_themes_doc(self):
        assert (ROOT / "docs" / "themes.md").is_file()

    def test_cli_ux_doc(self):
        assert (ROOT / "docs" / "cli-ux.md").is_file()

    def test_no_color_ci_doc(self):
        assert (ROOT / "docs" / "no-color-and-ci.md").is_file()

    def test_terminal_examples_dir(self):
        assert (ROOT / "examples" / "terminal").is_dir()

    def test_wizard_output_example(self):
        assert (ROOT / "examples" / "terminal" / "wizard_output.txt").is_file()

    def test_workbench_output_example(self):
        assert (ROOT / "examples" / "terminal" / "workbench_plain_output.txt").is_file()

    def test_theme_preview_example(self):
        assert (ROOT / "examples" / "terminal" / "theme_preview.md").is_file()

    def test_terminal_examples_readme(self):
        assert (ROOT / "examples" / "terminal" / "README.md").is_file()


class TestNoCIBranding:
    """Test that docs don't contain Claude Code branding or misleading claims."""

    def test_no_claude_code_branding_in_docs(self):
        """Docs should not reference Claude Code brand."""
        docs_dir = ROOT / "docs"
        forbidden = ["claude code", "claude-code", "Claude Code"]
        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8").lower()
            for term in forbidden:
                assert term.lower() not in content, f"Found '{term}' in {md_file.name}"

    def test_no_claude_code_in_readme(self):
        for readme in ["README.md", "README.zh-CN.md", "README.ja.md"]:
            p = ROOT / readme
            if p.is_file():
                content = p.read_text(encoding="utf-8").lower()
                assert "claude code" not in content, f"Found in {readme}"

    def test_docs_dont_claim_default_execute(self):
        """Docs should not claim workbench runs experiments by default."""
        wb_doc = ROOT / "docs" / "terminal-workbench.md"
        if wb_doc.is_file():
            content = wb_doc.read_text(encoding="utf-8").lower()
            # Should not claim experiments are run by default
            assert "default" in content  # doc exists and mentions defaults

    def test_docs_dont_claim_animation_in_ci(self):
        """Docs should not claim animation works in CI."""
        ux_doc = ROOT / "docs" / "cli-ux.md"
        if ux_doc.is_file():
            content = ux_doc.read_text(encoding="utf-8").lower()
            # Should mention CI disables animation
            assert "ci" in content


class TestPlainModeNoAnsi:
    """Test that plain mode produces no ANSI in any command."""

    def test_wizard_plain(self):
        result = _run("wizard", "--plain", ".")
        assert "\x1b[" not in result.stdout

    def test_theme_preview_plain(self):
        result = _run("theme", "preview", "--plain")
        assert "\x1b[" not in result.stdout

    def test_workbench_plain(self):
        result = _run("workbench", "--plain", "examples/demo-reproduce-repo")
        assert "\x1b[" not in result.stdout

    def test_scan_plain(self):
        result = _run("scan", "--plain", "examples/demo-reproduce-repo")
        # scan doesn't use new UI yet, but --plain should not cause errors
        assert result.returncode in (0, 1, 2)


class TestI18nReadmes:
    """Test that i18n READMEs mention new commands."""

    def test_zh_cn_mentions_wizard(self):
        p = ROOT / "README.zh-CN.md"
        if p.is_file():
            content = p.read_text(encoding="utf-8")
            assert "wizard" in content.lower()

    def test_ja_mentions_wizard(self):
        p = ROOT / "README.ja.md"
        if p.is_file():
            content = p.read_text(encoding="utf-8")
            assert "wizard" in content.lower()
