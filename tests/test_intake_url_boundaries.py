"""Tests for intake URL boundary handling."""

from __future__ import annotations

import pytest

from oss_paper_ci.repo_cloner import (
    is_github_url,
    is_arxiv_url,
    is_doi_url,
    is_paper_url,
    classify_input,
)


class TestURLClassification:
    """Test URL classification functions."""

    def test_github_url(self):
        """Recognizes GitHub URLs."""
        assert is_github_url("https://github.com/owner/repo")
        assert is_github_url("https://www.github.com/owner/repo")

    def test_not_github_url(self):
        """Rejects non-GitHub URLs."""
        assert not is_github_url("https://gitlab.com/owner/repo")
        assert not is_github_url("https://example.com")
        assert not is_github_url(".")

    def test_arxiv_url(self):
        """Recognizes arXiv URLs."""
        assert is_arxiv_url("https://arxiv.org/abs/2401.00001")
        assert is_arxiv_url("https://www.arxiv.org/abs/2401.00001")

    def test_doi_url(self):
        """Recognizes DOI URLs."""
        assert is_doi_url("https://doi.org/10.1234/example")
        assert is_doi_url("https://dx.doi.org/10.1234/example")

    def test_paper_url(self):
        """Recognizes paper URLs (arXiv and DOI)."""
        assert is_paper_url("https://arxiv.org/abs/2401.00001")
        assert is_paper_url("https://doi.org/10.1234/example")

    def test_classify_local(self):
        """Classifies local paths."""
        assert classify_input(".") == "local"
        assert classify_input("tests/fixtures/intake_python_repo") == "local"

    def test_classify_github(self):
        """Classifies GitHub URLs."""
        assert classify_input("https://github.com/owner/repo") == "github-url"

    def test_classify_paper(self):
        """Classifies paper URLs."""
        assert classify_input("https://arxiv.org/abs/2401.00001") == "paper-url"
        assert classify_input("https://doi.org/10.1234/example") == "paper-url"

    def test_classify_unknown(self):
        """Classifies unknown inputs."""
        assert classify_input("not-a-valid-input") == "unknown"
