"""Incremental scan cache for oss-paper-ci.

Caches scan results keyed by file content hashes, config, rules, profile,
and tool version.  Cache is stored in .oss-paper-ci-cache/ and is safe to
delete at any time.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci import __version__

CACHE_DIR_NAME = ".oss-paper-ci-cache"
SCHEMA_VERSION = "1"


@dataclass
class CacheEntry:
    """A single cached scan result."""

    project_id: str
    cache_key: str
    report: dict[str, Any]
    hit: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "cache_key": self.cache_key,
            "report": self.report,
        }


@dataclass
class CacheStats:
    """Cache operation statistics."""

    total: int = 0
    hits: int = 0
    misses: int = 0
    errors: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
        }


def compute_cache_key(
    project_path: str,
    profile: str,
    config_content: str,
    rules_contents: list[str],
) -> str:
    """Compute a cache key from project files, config, rules, and version.

    The key changes when any file in the project changes, or when
    config/rules/profile/version change.

    Args:
        project_path: Path to the project root directory.
        profile: Active policy profile name.
        config_content: Content of the config file (empty string if none).
        rules_contents: List of rule pack file contents.

    Returns:
        Hex digest string.
    """
    hasher = hashlib.sha256()

    # Tool version
    hasher.update(__version__.encode("utf-8"))
    hasher.update(b"\x00")

    # Schema version
    hasher.update(SCHEMA_VERSION.encode("utf-8"))
    hasher.update(b"\x00")

    # Profile
    hasher.update(profile.encode("utf-8"))
    hasher.update(b"\x00")

    # Config content
    hasher.update(config_content.encode("utf-8"))
    hasher.update(b"\x00")

    # Rules contents
    for rc in sorted(rules_contents):
        hasher.update(rc.encode("utf-8"))
        hasher.update(b"\x00")

    # Project file hashes
    root = Path(project_path)
    if root.is_dir():
        for file_path in sorted(_iter_files(root)):
            try:
                rel = file_path.relative_to(root)
                hasher.update(str(rel).encode("utf-8"))
                hasher.update(b"\x00")
                content = file_path.read_bytes()
                hasher.update(content)
                hasher.update(b"\x00")
            except (OSError, UnicodeDecodeError):
                # Skip unreadable files
                continue

    return hasher.hexdigest()


def _iter_files(root: Path):
    """Iterate over all files in a directory, skipping common ignore dirs."""
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules",
                 ".oss-paper-ci-cache", ".pytest_cache", "dist", "build"}
    for entry in sorted(root.rglob("*")):
        if entry.is_file():
            # Check if any parent is a skip dir
            parts = entry.relative_to(root).parts
            if any(p in skip_dirs for p in parts):
                continue
            yield entry


def get_cache_dir(workspace_dir: Path) -> Path:
    """Get the cache directory path."""
    return workspace_dir / CACHE_DIR_NAME


def get_project_cache_file(cache_dir: Path, project_id: str) -> Path:
    """Get the cache file path for a project."""
    safe_id = project_id.replace("/", "_").replace("\\", "_").replace(":", "_")
    return cache_dir / f"{safe_id}.json"


def lookup_cache(
    cache_dir: Path,
    project_id: str,
    cache_key: str,
) -> dict[str, Any] | None:
    """Look up a cached result.

    Args:
        cache_dir: Path to cache directory.
        project_id: Project identifier.
        cache_key: Expected cache key.

    Returns:
        Cached report dict if hit, None if miss or corrupt.
    """
    cache_file = get_project_cache_file(cache_dir, project_id)
    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        if data.get("cache_key") != cache_key:
            return None
        if data.get("schema_version") != SCHEMA_VERSION:
            return None
        return data.get("report")
    except (json.JSONDecodeError, OSError, KeyError):
        # Corrupt cache — treat as miss
        return None


def store_cache(
    cache_dir: Path,
    project_id: str,
    cache_key: str,
    report: dict[str, Any],
) -> None:
    """Store a scan result in cache.

    Args:
        cache_dir: Path to cache directory.
        project_id: Project identifier.
        cache_key: Cache key for this result.
        report: Report dict to cache.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = get_project_cache_file(cache_dir, project_id)

    data = {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "cache_key": cache_key,
        "report": report,
    }

    cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean_cache(workspace_dir: Path) -> int:
    """Remove all cache files.

    Args:
        workspace_dir: Directory containing .oss-paper-ci-cache/.

    Returns:
        Number of files removed.
    """
    cache_dir = get_cache_dir(workspace_dir)
    if not cache_dir.exists():
        return 0

    count = 0
    for entry in cache_dir.iterdir():
        if entry.is_file() and entry.suffix == ".json":
            entry.unlink()
            count += 1

    # Remove directory if empty
    try:
        cache_dir.rmdir()
    except OSError:
        pass

    return count


def get_cache_info(workspace_dir: Path) -> dict[str, Any]:
    """Get information about the cache.

    Args:
        workspace_dir: Directory containing .oss-paper-ci-cache/.

    Returns:
        Dict with cache info.
    """
    cache_dir = get_cache_dir(workspace_dir)
    if not cache_dir.exists():
        return {
            "exists": False,
            "path": str(cache_dir),
            "entries": 0,
            "total_size_bytes": 0,
        }

    entries = 0
    total_size = 0
    for entry in cache_dir.iterdir():
        if entry.is_file() and entry.suffix == ".json":
            entries += 1
            try:
                total_size += entry.stat().st_size
            except OSError:
                pass

    return {
        "exists": True,
        "path": str(cache_dir),
        "entries": entries,
        "total_size_bytes": total_size,
    }
