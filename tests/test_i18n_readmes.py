"""Tests for i18n README consistency."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestI18nFilesExist:
    """Test that multilingual READMEs exist."""

    def test_english_readme(self):
        assert (ROOT / "README.md").exists()

    def test_chinese_readme(self):
        assert (ROOT / "README.zh-CN.md").exists()

    def test_japanese_readme(self):
        assert (ROOT / "README.ja.md").exists()


class TestLanguageLinks:
    """Test that language links are present."""

    def test_english_has_chinese_link(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "README.zh-CN.md" in content

    def test_english_has_japanese_link(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "README.ja.md" in content

    def test_chinese_has_english_link(self):
        content = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        assert "README.md" in content

    def test_chinese_has_japanese_link(self):
        content = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        assert "README.ja.md" in content

    def test_japanese_has_english_link(self):
        content = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        assert "README.md" in content

    def test_japanese_has_chinese_link(self):
        content = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        assert "README.zh-CN.md" in content


class TestCommandConsistency:
    """Test that core commands are present in all READMEs."""

    REQUIRED_COMMANDS = [
        "oss-paper-ci scan",
        "oss-paper-ci reproduce",
        "oss-paper-ci capsule",
    ]

    def test_english_has_commands(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        for cmd in self.REQUIRED_COMMANDS:
            assert cmd in content, f"English README missing: {cmd}"

    def test_chinese_has_commands(self):
        content = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        for cmd in self.REQUIRED_COMMANDS:
            assert cmd in content, f"Chinese README missing: {cmd}"

    def test_japanese_has_commands(self):
        content = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        for cmd in self.REQUIRED_COMMANDS:
            assert cmd in content, f"Japanese README missing: {cmd}"


class TestSafetyWarnings:
    """Test that safety warnings are present."""

    def test_english_has_execute_warning(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        assert "--execute" in content

    def test_chinese_has_execute_warning(self):
        content = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        assert "--execute" in content

    def test_japanese_has_execute_warning(self):
        content = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        assert "--execute" in content


class TestNoOverclaiming:
    """Test that no README claims guaranteed reproduction."""

    def test_english_no_guarantee(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        # Should not claim guaranteed reproduction as a positive statement
        if "guarantee" in content:
            assert "not" in content or "does not" in content

    def test_chinese_no_guarantee(self):
        content = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        # Should not claim "保证复现" without negation
        if "保证复现" in content:
            assert "不是" in content or "不保证" in content

    def test_japanese_no_guarantee(self):
        content = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        # Should not claim guaranteed reproduction
        assert "完全再現保証" not in content


class TestI18nChecker:
    """Test the i18n checker script."""

    def test_checker_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_i18n_readmes.py")],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=str(ROOT), timeout=30,
        )
        assert result.returncode == 0, f"i18n checker failed: {result.stdout}"

    def test_checker_json_format(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_i18n_readmes.py"),
             "--format", "json"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=str(ROOT), timeout=30,
        )
        assert result.returncode == 0
