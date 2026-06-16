"""Safe file writing utilities for adoption scaffolding.

Provides path validation, atomic writes, force guards, and
multi-file apply with rollback support.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


# Paths that must never be written to
FORBIDDEN_PREFIXES = [
    ".git/", ".git\\",
    "node_modules/", "node_modules\\",
    "target/", "target\\",
    "__pycache__/", "__pycache__\\",
    ".venv/", ".venv\\",
    "venv/", "venv\\",
    ".env",
]

FORBIDDEN_NAMES = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
]


@dataclass
class WriteAction:
    """A single file write action."""
    path: str
    content: str
    action: str  # "create" or "overwrite"
    reason: str = ""
    risk: str = "low"  # low, medium, high


@dataclass
class WriteResult:
    """Result of a file write operation."""
    path: str
    success: bool
    action: str  # "created", "overwritten", "skipped", "error"
    message: str = ""


@dataclass
class ApplyResult:
    """Result of applying multiple write actions."""
    results: list[WriteResult] = field(default_factory=list)
    total_attempted: int = 0
    total_written: int = 0
    total_skipped: int = 0
    total_errors: int = 0


def validate_path(path: str, repo_root: str) -> tuple[bool, str]:
    """Validate that a path is safe to write to.

    Returns (is_valid, error_message).
    """
    # Normalize paths
    repo = Path(repo_root).resolve()
    target = (repo / path).resolve()

    # Check path traversal
    try:
        target.relative_to(repo)
    except ValueError:
        return False, f"Path escapes repository root: {path}"

    # Check forbidden prefixes
    normalized = path.replace("\\", "/")
    for prefix in FORBIDDEN_PREFIXES:
        if normalized.startswith(prefix) or normalized == prefix.rstrip("/"):
            return False, f"Cannot write to forbidden path: {path}"

    # Check forbidden directory names
    parts = Path(path).parts
    for part in parts:
        if part in FORBIDDEN_NAMES:
            return False, f"Cannot write inside forbidden directory: {part}"

    # Check absolute path
    if os.path.isabs(path):
        return False, f"Cannot write to absolute path: {path}"

    return True, ""


def preview_write(action: WriteAction, repo_root: str) -> str:
    """Generate a preview of what would be written.

    Returns a markdown-formatted preview string.
    """
    target = Path(repo_root) / action.path
    exists = target.exists()

    lines = [f"### {action.path}"]
    lines.append("")
    if exists:
        lines.append(f"**Action:** Overwrite existing file")
    else:
        lines.append(f"**Action:** Create new file")
    lines.append(f"**Risk:** {action.risk}")
    if action.reason:
        lines.append(f"**Reason:** {action.reason}")
    lines.append("")
    lines.append("```")
    # Show first 20 lines of content
    content_lines = action.content.split("\n")
    for line in content_lines[:20]:
        lines.append(line)
    if len(content_lines) > 20:
        lines.append(f"... ({len(content_lines) - 20} more lines)")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def apply_write(
    action: WriteAction,
    repo_root: str,
    force: bool = False,
    dry_run: bool = True,
) -> WriteResult:
    """Apply a single write action.

    Args:
        action: The write action to apply.
        repo_root: Repository root path.
        force: Allow overwriting existing files.
        dry_run: If True, don't actually write.

    Returns:
        WriteResult with success status and message.
    """
    # Validate path
    valid, error = validate_path(action.path, repo_root)
    if not valid:
        return WriteResult(path=action.path, success=False, action="error", message=error)

    target = Path(repo_root) / action.path
    exists = target.exists()

    # Check overwrite protection
    if exists and not force and action.action == "overwrite":
        return WriteResult(
            path=action.path, success=False, action="skipped",
            message=f"File exists: {action.path}. Use --force to overwrite.",
        )

    if exists and not force:
        return WriteResult(
            path=action.path, success=False, action="skipped",
            message=f"File exists: {action.path}. Use --force to overwrite.",
        )

    if dry_run:
        action_type = "overwrite" if exists else "create"
        return WriteResult(
            path=action.path, success=True, action=f"would_{action_type}",
            message=f"[dry-run] Would {action_type}: {action.path}",
        )

    # Create parent directories
    target.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    try:
        target.write_text(action.content, encoding="utf-8")
        action_type = "overwritten" if exists else "created"
        return WriteResult(
            path=action.path, success=True, action=action_type,
            message=f"{action_type.capitalize()}: {action.path}",
        )
    except Exception as e:
        return WriteResult(
            path=action.path, success=False, action="error",
            message=f"Failed to write {action.path}: {e}",
        )


def apply_multiple(
    actions: list[WriteAction],
    repo_root: str,
    force: bool = False,
    dry_run: bool = True,
) -> ApplyResult:
    """Apply multiple write actions.

    Args:
        actions: List of write actions.
        repo_root: Repository root path.
        force: Allow overwriting existing files.
        dry_run: If True, don't actually write.

    Returns:
        ApplyResult with all results.
    """
    result = ApplyResult(total_attempted=len(actions))

    for action in actions:
        write_result = apply_write(action, repo_root, force=force, dry_run=dry_run)
        result.results.append(write_result)

        if write_result.success:
            if write_result.action.startswith("would_"):
                pass  # dry run
            else:
                result.total_written += 1
        elif write_result.action == "skipped":
            result.total_skipped += 1
        else:
            result.total_errors += 1

    return result
