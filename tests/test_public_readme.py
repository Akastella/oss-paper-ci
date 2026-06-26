"""Tests for the public README."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestReadmeStructure:
    """Test README structure for public release."""

    def test_readme_has_one_liner(self):
        """README should have a one-line description near the top."""
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        # First non-empty, non-badge line should be the description
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.strip().startswith("[![")]
        assert any("CLI toolkit" in l or "oss-paper-ci" in l for l in lines[:10])

    def test_readme_has_quickstart(self):
        """README should have a quickstart section."""
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "## Install" in content or "## Quickstart" in content or "## Quick start" in content

    def test_readme_has_three_commands(self):
        """README should show three useful commands."""
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "oss-paper-ci scan" in content
        assert "oss-paper-ci reproduce" in content
        assert "oss-paper-ci capsule" in content

    def test_readme_has_limitations(self):
        """README should have a limitations section."""
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "## Limitations" in content

    def test_readme_no_guarantee_reproduction(self):
        """README should not claim guaranteed reproduction."""
        content = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        # Should not have "guarantee" near "reproduction"
        if "guarantee" in content:
            assert "does not" in content or "not guarantee" in content

    def test_readme_docs_links_exist(self):
        """README doc links should point to existing files."""
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        doc_links = re.findall(r"\[.*?\]\((docs/[^)]+)\)", content)
        for link in doc_links:
            path = ROOT / link
            if not path.exists():
                # Check without .md
                alt = ROOT / (link + ".md") if not link.endswith(".md") else None
                assert alt and alt.exists(), f"Missing doc link: {link}"

    def test_readme_not_too_long(self):
        """README should be concise for public release."""
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        line_count = len(content.split("\n"))
        assert line_count < 400, f"README is {line_count} lines, should be under 400"
