"""Tests that documentation is well-formed and commands are valid."""

import re
from pathlib import Path

import pytest


DOCS = Path("docs")


class TestDocsExistence:
    """Test that expected documentation files exist."""

    def test_readme_exists(self):
        assert Path("README.md").exists()

    def test_docs_directory_exists(self):
        assert DOCS.is_dir()

    def test_usage_doc_exists(self):
        assert (DOCS / "usage.md").exists()

    def test_checks_doc_exists(self):
        assert (DOCS / "checks.md").exists()

    def test_configuration_doc_exists(self):
        assert (DOCS / "configuration.md").exists()

    def test_github_actions_doc_exists(self):
        assert (DOCS / "github-actions.md").exists()


class TestDocsContent:
    """Test documentation content quality."""

    def test_readme_has_quickstart(self):
        readme = Path("README.md")
        content = readme.read_text(encoding="utf-8")
        assert "quickstart" in content.lower() or "installation" in content.lower()

    def test_readme_mentions_scan_command(self):
        readme = Path("README.md")
        content = readme.read_text(encoding="utf-8")
        assert "scan" in content.lower()

    def test_usage_doc_has_scan_section(self):
        content = (DOCS / "usage.md").read_text(encoding="utf-8")
        assert "scan" in content.lower()

    def test_checks_doc_lists_check_ids(self):
        content = (DOCS / "checks.md").read_text(encoding="utf-8")
        assert "META001" in content

    def test_config_doc_has_yaml(self):
        content = (DOCS / "configuration.md").read_text(encoding="utf-8")
        assert "yaml" in content.lower() or "yml" in content.lower()

    def test_github_actions_doc_mentions_action(self):
        content = (DOCS / "github-actions.md").read_text(encoding="utf-8")
        assert "action" in content.lower()


class TestDocsFormatting:
    """Test documentation formatting quality."""

    def test_all_md_files_parse_utf8(self):
        """All .md files should be valid UTF-8."""
        for md_file in Path(".").glob("**/*.md"):
            if "dev-history" in str(md_file) or ".git" in str(md_file):
                continue
            try:
                md_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"File is not valid UTF-8: {md_file}")

    def test_docs_have_headings(self):
        """Doc files should have at least one heading."""
        for md_file in DOCS.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            assert re.search(r"^#+\s", content, re.MULTILINE), f"{md_file} has no headings"


class TestNoExternalPlanWording:
    """Check that docs don't contain application-oriented wording."""

    def test_no_forbidden_phrases(self):
        """Check that docs don't contain application-oriented wording."""
        forbidden = ["codex for oss", "credits", "pro plan", "application material"]
        for md_file in Path(".").glob("**/*.md"):
            if "dev-history" in str(md_file):
                continue
            content = md_file.read_text(encoding="utf-8", errors="replace").lower()
            for phrase in forbidden:
                assert phrase not in content, f"{phrase} found in {md_file}"
