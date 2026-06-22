"""Safe repository cloning with strict boundaries.

Only clones when explicitly requested via --clone flag.
Uses shallow clone, no submodules, timeout, and no code execution.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


@dataclass
class CloneResult:
    """Result of a clone operation."""

    success: bool = False
    url: str = ""
    local_path: str = ""
    shallow: bool = True
    depth: int = 1
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "url": self.url,
            "local_path": self.local_path,
            "shallow": self.shallow,
            "depth": self.depth,
            "error": self.error,
            "warnings": self.warnings,
        }


def is_github_url(text: str) -> bool:
    """Check if text is a GitHub URL."""
    try:
        parsed = urlparse(text)
        return parsed.hostname in ("github.com", "www.github.com") and bool(parsed.path.strip("/"))
    except Exception:
        return False


def is_arxiv_url(text: str) -> bool:
    """Check if text is an arXiv URL."""
    try:
        parsed = urlparse(text)
        return parsed.hostname in ("arxiv.org", "www.arxiv.org")
    except Exception:
        return False


def is_doi_url(text: str) -> bool:
    """Check if text is a DOI URL."""
    try:
        parsed = urlparse(text)
        return parsed.hostname in ("doi.org", "www.doi.org", "dx.doi.org")
    except Exception:
        return False


def is_paper_url(text: str) -> bool:
    """Check if text is a paper URL (arXiv, DOI, etc.)."""
    return is_arxiv_url(text) or is_doi_url(text)


def classify_input(text: str) -> str:
    """Classify an input string as local, github-url, paper-url, or unknown."""
    if os.path.isdir(text):
        return "local"
    if is_github_url(text):
        return "github-url"
    if is_paper_url(text):
        return "paper-url"
    if os.path.isfile(text):
        return "local"
    return "unknown"


def clone_repository(
    url: str,
    workdir: str | None = None,
    depth: int = 1,
    timeout: int = 120,
) -> CloneResult:
    """Clone a repository with safety constraints.

    Args:
        url: GitHub URL to clone.
        workdir: Working directory for the clone. If None, uses a temp directory.
        depth: Shallow clone depth (default: 1).
        timeout: Clone timeout in seconds (default: 120).

    Returns:
        CloneResult with success status and details.
    """
    result = CloneResult(url=url, shallow=True, depth=depth)

    if not is_github_url(url):
        result.error = f"Not a valid GitHub URL: {url}"
        return result

    # Determine target directory
    if workdir:
        target = Path(workdir)
    else:
        import tempfile
        target = Path(tempfile.mkdtemp(prefix="oss-paper-ci-intake-"))

    result.local_path = str(target)

    # Build clone command
    cmd = [
        "git", "clone",
        "--depth", str(depth),
        "--single-branch",
        "--no-tags",
        "--recurse-submodules=no",
        url,
        str(target),
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=None,
        )

        if proc.returncode != 0:
            result.error = f"git clone failed (exit {proc.returncode}): {proc.stderr.strip()}"
            return result

        result.success = True

    except subprocess.TimeoutExpired:
        result.error = f"git clone timed out after {timeout}s"
        return result
    except FileNotFoundError:
        result.error = "git command not found"
        return result
    except Exception as e:
        result.error = f"Unexpected error during clone: {e}"
        return result

    return result


def cleanup_clone(clone_path: str) -> None:
    """Clean up a cloned repository directory."""
    p = Path(clone_path)
    if p.exists() and p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
