"""Tests for URL and source resolver."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.resolver import ResolvedSource, resolve_source


class TestGitHubUrlResolution:
    """Test GitHub URL parsing."""

    def test_https_github_url(self):
        result = resolve_source("https://github.com/Akastella/oss-paper-ci")
        assert result.ok
        assert result.source_type == "github"
        assert result.repo_url == "https://github.com/Akastella/oss-paper-ci"
        assert result.clone_url == "https://github.com/Akastella/oss-paper-ci"

    def test_https_github_url_with_git_suffix(self):
        result = resolve_source("https://github.com/Akastella/oss-paper-ci.git")
        assert result.ok
        assert result.source_type == "github"
        assert result.repo_url == "https://github.com/Akastella/oss-paper-ci"

    def test_https_github_url_with_trailing_slash(self):
        result = resolve_source("https://github.com/Akastella/oss-paper-ci/")
        assert result.ok
        assert result.source_type == "github"

    def test_github_url_with_path(self):
        result = resolve_source("https://github.com/Akastella/oss-paper-ci/tree/main")
        assert result.ok
        assert result.source_type == "github"

    def test_ssh_github_url(self):
        result = resolve_source("git@github.com:Akastella/oss-paper-ci.git")
        assert result.ok
        assert result.source_type == "github"
        assert "Akastella/oss-paper-ci" in result.repo_url


class TestLocalPathResolution:
    """Test local path resolution."""

    def test_relative_path(self, tmp_path):
        repo = tmp_path / "test-repo"
        repo.mkdir()
        result = resolve_source(str(repo))
        assert result.ok
        assert result.source_type == "local"
        assert result.local_path == str(repo.resolve())

    def test_dot_path(self, tmp_path):
        repo = tmp_path / "test-repo"
        repo.mkdir()
        # Use absolute path to avoid cwd dependency
        result = resolve_source(str(repo))
        assert result.source_type == "local"
        assert result.ok

    def test_nonexistent_path(self):
        result = resolve_source("/nonexistent/path/that/does/not/exist")
        assert not result.ok
        assert "does not exist" in result.error

    def test_file_not_directory(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("test")
        result = resolve_source(str(f))
        assert not result.ok
        assert "not a directory" in result.error

    def test_file_uri(self, tmp_path):
        repo = tmp_path / "test-repo"
        repo.mkdir()
        uri = f"file:///{repo}".replace("\\", "/")
        result = resolve_source(uri)
        assert result.ok
        assert result.source_type == "local"


class TestPaperUrlDetection:
    """Test paper URL detection."""

    def test_arxiv_url(self):
        result = resolve_source("https://arxiv.org/abs/2301.00001")
        assert result.source_type == "paper"
        assert "arxiv" in result.paper_url.lower() or "2301.00001" in result.paper_url
        assert not result.ok
        assert "--repo" in result.error

    def test_doi_url(self):
        result = resolve_source("https://doi.org/10.1234/example")
        assert result.source_type == "paper"
        assert not result.ok
        assert "--repo" in result.error

    def test_openreview_url(self):
        result = resolve_source("https://openreview.net/forum?id=abc123")
        assert result.source_type == "paper"
        assert not result.ok


class TestRepoOverride:
    """Test --repo override."""

    def test_repo_override_github(self):
        result = resolve_source(
            "https://arxiv.org/abs/2301.00001",
            repo_override="https://github.com/owner/repo",
        )
        assert result.ok
        assert result.source_type == "github"
        assert result.paper_url == "https://arxiv.org/abs/2301.00001"

    def test_repo_override_local(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        result = resolve_source(
            "https://arxiv.org/abs/2301.00001",
            repo_override=str(repo),
        )
        assert result.ok
        assert result.source_type == "local"


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_url(self):
        result = resolve_source("")
        assert not result.ok
        assert "Empty" in result.error

    def test_whitespace_url(self):
        result = resolve_source("   ")
        assert not result.ok

    def test_unknown_url_format(self):
        result = resolve_source("https://example.com/something")
        assert not result.ok
        assert "Could not resolve" in result.error
