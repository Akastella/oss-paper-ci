"""Tests for PyPI/package metadata."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestPyprojectMetadata:
    """Test pyproject.toml metadata completeness."""

    def test_has_name(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'name = "oss-paper-ci"' in content

    def test_has_version(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert re.search(r'version = "\d+\.\d+\.\d+', content)

    def test_has_description(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "description" in content

    def test_has_readme(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "readme" in content

    def test_has_license(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "license" in content

    def test_has_requires_python(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "requires-python" in content

    def test_has_urls(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "[project.urls]" in content
        assert "Homepage" in content
        assert "Repository" in content

    def test_has_scripts(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "[project.scripts]" in content
        assert "oss-paper-ci" in content

    def test_has_classifiers(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "classifiers" in content
        assert "Python :: 3" in content

    def test_version_consistent_with_init(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        init = (ROOT / "src" / "oss_paper_ci" / "__init__.py").read_text(encoding="utf-8")

        m1 = re.search(r'version = "(.+?)"', pyproject)
        m2 = re.search(r'__version__ = "(.+?)"', init)
        assert m1 and m2
        assert m1.group(1) == m2.group(1)
