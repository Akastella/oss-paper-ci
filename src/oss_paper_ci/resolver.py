"""URL and source resolver for reproduce command.

Resolves user-provided URLs to clonable repositories or local paths.
Supports: GitHub repo URLs, local paths, file:// URIs.
Paper URLs (arXiv, DOI) are detected but require --repo to provide the code link.

Design principles:
- No network calls (no HTTP fetching, no search engines)
- No assumptions about paper having code
- Conservative: prefer clear error over wrong guess
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class ResolvedSource:
    """Result of resolving a user-provided URL or path."""

    input_url: str = ""
    repo_url: str = ""
    paper_url: str = ""
    source_type: str = ""  # "github", "local", "paper", "unknown"
    local_path: str = ""
    clone_url: str = ""
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.error


# Patterns for GitHub URLs
_GITHUB_HTTPS = re.compile(
    r"^https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:/.*)?$"
)
_GITHUB_SSH = re.compile(
    r"^git@github\.com:([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?$"
)

# Patterns for paper URLs (detected but not fetched)
_ARXIV_PATTERN = re.compile(r"^https?://arxiv\.org/(?:abs|pdf)/(\d+\.\d+)")
_DOI_PATTERN = re.compile(r"^https?://doi\.org/")
_PAPER_DOMAINS = re.compile(
    r"^https?://(?:"
    r"arxiv\.org|"
    r"doi\.org|"
    r"papers\.nips\.cc|"
    r"openreview\.net|"
    r"proceedings\.mlr\.press|"
    r"aclanthology\.org|"
    r"ieeexplore\.ieee\.org|"
    r"springer\.com|"
    r"sciencedirect\.com"
    r")"
)


def resolve_source(
    url: str,
    repo_override: str | None = None,
) -> ResolvedSource:
    """Resolve a user-provided URL to a clonable source.

    Args:
        url: User-provided URL or path.
        repo_override: Explicit repo URL (--repo flag). Takes precedence.

    Returns:
        ResolvedSource with clone_url, local_path, or error set.
    """
    result = ResolvedSource(input_url=url)

    # If --repo is provided, use it directly
    if repo_override:
        return _resolve_repo_url(repo_override, result, is_primary=False)

    # Strip whitespace
    url = url.strip()
    if not url:
        result.error = "Empty URL or path provided."
        return result

    # Check if it's a local path
    if _is_local_path(url):
        return _resolve_local_path(url, result)

    # Check if it's a file:// URI
    if url.startswith("file://"):
        path = urlparse(url).path
        # On Windows, file:///C:/path -> C:/path
        if len(path) >= 3 and path[0] == "/" and path[2] == ":":
            path = path[1:]
        return _resolve_local_path(path, result)

    # Check if it's a GitHub URL
    github_match = _GITHUB_HTTPS.match(url) or _GITHUB_SSH.match(url)
    if github_match:
        owner, repo = github_match.group(1), github_match.group(2)
        result.repo_url = f"https://github.com/{owner}/{repo}"
        result.clone_url = result.repo_url
        result.source_type = "github"
        return result

    # Check if it's a paper URL
    if _is_paper_url(url):
        result.paper_url = url
        result.source_type = "paper"
        result.error = (
            f"Paper URL detected, but no repository URL was provided. "
            f"Use --repo <github-url> to specify the code repository."
        )
        return result

    # Unknown URL format
    result.source_type = "unknown"
    result.error = (
        f"Could not resolve URL: {url}\n"
        f"Supported formats:\n"
        f"  - GitHub: https://github.com/owner/repo\n"
        f"  - Local: ./path/to/repo or /absolute/path\n"
        f"  - file:///path/to/repo\n"
        f"For paper URLs, use --repo <github-url> to specify the code."
    )
    return result


def _is_local_path(url: str) -> bool:
    """Check if the string looks like a local filesystem path."""
    # Starts with ./ or ../ or / or C:\ etc.
    if url.startswith((".", "/", "\\")):
        return True
    # Windows drive letter
    if len(url) >= 2 and url[1] == ":":
        return True
    # Relative path that exists
    if Path(url).exists():
        return True
    return False


def _is_paper_url(url: str) -> bool:
    """Check if the URL looks like a paper URL."""
    return bool(_PAPER_DOMAINS.match(url) or _ARXIV_PATTERN.match(url))


def _resolve_local_path(path_str: str, result: ResolvedSource) -> ResolvedSource:
    """Resolve a local path to a repository."""
    p = Path(path_str).resolve()
    result.local_path = str(p)

    if not p.exists():
        result.error = f"Local path does not exist: {path_str}"
        return result

    if not p.is_dir():
        result.error = f"Local path is not a directory: {path_str}"
        return result

    result.source_type = "local"
    result.repo_url = str(p)
    return result


def _resolve_repo_url(
    url: str, result: ResolvedSource, is_primary: bool = True
) -> ResolvedSource:
    """Resolve a repo URL (--repo override or primary input)."""
    url = url.strip()

    # Check if it's a local path
    if _is_local_path(url):
        return _resolve_local_path(url, result)

    # Check if it's a GitHub URL
    github_match = _GITHUB_HTTPS.match(url) or _GITHUB_SSH.match(url)
    if github_match:
        owner, repo = github_match.group(1), github_match.group(2)
        result.repo_url = f"https://github.com/{owner}/{repo}"
        result.clone_url = result.repo_url
        result.source_type = "github"
        if not is_primary:
            # Keep the original paper_url from input
            result.paper_url = result.input_url
            result.input_url = url
        return result

    # file:// URI
    if url.startswith("file://"):
        path = urlparse(url).path
        if len(path) >= 3 and path[0] == "/" and path[2] == ":":
            path = path[1:]
        return _resolve_local_path(path, result)

    result.error = f"Could not resolve repository URL: {url}"
    return result


def get_commit_sha(repo_path: str) -> str:
    """Get the current git commit SHA of a local repository.

    Returns empty string if not a git repo or git is unavailable.
    """
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""
