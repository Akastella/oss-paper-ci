"""Filesystem utilities for repository scanning."""

from __future__ import annotations

import os
from pathlib import Path


def list_files(root: str | Path, ignore_paths: list[str] | None = None) -> list[Path]:
    """List all files under root, respecting ignore patterns.

    Args:
        root: Root directory to scan.
        ignore_paths: Directory/file names to skip (e.g., ['.git', 'node_modules']).

    Returns:
        Sorted list of relative paths from root.
    """
    root = Path(root).resolve()
    ignore = set(ignore_paths or [])
    result: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter ignored directories in-place so os.walk skips them
        dirnames[:] = [d for d in dirnames if d not in ignore]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            result.append(fpath.relative_to(root))

    result.sort()
    return result


def file_exists(root: str | Path, *parts: str) -> bool:
    """Check if a file exists relative to root."""
    return (Path(root).joinpath(*parts)).exists()


def find_files_by_name(root: str | Path, name: str, ignore_paths: list[str] | None = None) -> list[Path]:
    """Find all files with a given name under root."""
    files = list_files(root, ignore_paths)
    return [f for f in files if f.name == name]


def find_files_by_extension(root: str | Path, ext: str, ignore_paths: list[str] | None = None) -> list[Path]:
    """Find all files with a given extension under root.

    Args:
        root: Root directory.
        ext: Extension including dot, e.g., '.py'.
        ignore_paths: Paths to ignore.
    """
    files = list_files(root, ignore_paths)
    return [f for f in files if f.suffix == ext]


def find_files_by_extensions(root: str | Path, exts: list[str], ignore_paths: list[str] | None = None) -> list[Path]:
    """Find all files matching any of the given extensions."""
    files = list_files(root, ignore_paths)
    ext_set = set(exts)
    return [f for f in files if f.suffix in ext_set]


def dir_has_any_file(root: str | Path, patterns: list[str]) -> bool:
    """Check if root contains any file matching the given name patterns."""
    root = Path(root)
    for pattern in patterns:
        if (root / pattern).exists():
            return True
    return False


def read_text_file(path: str | Path, max_bytes: int = 500_000) -> str | None:
    """Read a text file, returning None on failure."""
    try:
        p = Path(path)
        if not p.exists() or not p.is_file():
            return None
        if p.stat().st_size > max_bytes:
            return None
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
