"""Tests for safe file writing utilities."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from oss_paper_ci.safe_write import (
    validate_path, preview_write, apply_write, apply_multiple,
    WriteAction, WriteResult, ApplyResult,
)


class TestValidatePath:
    """Test path validation."""

    def test_valid_relative_path(self, tmp_path):
        valid, msg = validate_path("data/README.md", str(tmp_path))
        assert valid is True

    def test_rejects_path_traversal(self, tmp_path):
        valid, msg = validate_path("../evil.txt", str(tmp_path))
        assert valid is False
        assert "escapes" in msg.lower()

    def test_rejects_absolute_path(self, tmp_path):
        valid, msg = validate_path("/etc/passwd", str(tmp_path))
        assert valid is False
        # Absolute paths are caught by path traversal check
        assert "escapes" in msg.lower() or "absolute" in msg.lower()

    def test_rejects_git_directory(self, tmp_path):
        valid, msg = validate_path(".git/config", str(tmp_path))
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_rejects_node_modules(self, tmp_path):
        valid, msg = validate_path("node_modules/pkg/index.js", str(tmp_path))
        assert valid is False

    def test_rejects_venv(self, tmp_path):
        valid, msg = validate_path(".venv/lib/python.py", str(tmp_path))
        assert valid is False

    def test_rejects_pycache(self, tmp_path):
        valid, msg = validate_path("__pycache__/mod.pyc", str(tmp_path))
        assert valid is False


class TestPreviewWrite:
    """Test write preview generation."""

    def test_preview_new_file(self, tmp_path):
        action = WriteAction(
            path="data/README.md",
            content="# Data\n",
            action="create",
            reason="Missing data documentation",
        )
        preview = preview_write(action, str(tmp_path))
        assert "data/README.md" in preview
        assert "Create new file" in preview

    def test_preview_existing_file(self, tmp_path):
        (tmp_path / "existing.txt").write_text("old")
        action = WriteAction(
            path="existing.txt",
            content="new",
            action="overwrite",
        )
        preview = preview_write(action, str(tmp_path))
        assert "Overwrite" in preview


class TestApplyWrite:
    """Test single file write operations."""

    def test_dry_run_does_not_write(self, tmp_path):
        action = WriteAction(path="test.txt", content="hello", action="create")
        result = apply_write(action, str(tmp_path), dry_run=True)
        assert result.success is True
        assert "would_create" in result.action
        assert not (tmp_path / "test.txt").exists()

    def test_apply_creates_file(self, tmp_path):
        action = WriteAction(path="test.txt", content="hello", action="create")
        result = apply_write(action, str(tmp_path), dry_run=False)
        assert result.success is True
        assert result.action == "created"
        assert (tmp_path / "test.txt").read_text() == "hello"

    def test_apply_creates_parent_dirs(self, tmp_path):
        action = WriteAction(path="a/b/c.txt", content="deep", action="create")
        result = apply_write(action, str(tmp_path), dry_run=False)
        assert result.success is True
        assert (tmp_path / "a" / "b" / "c.txt").read_text() == "deep"

    def test_refuses_overwrite_without_force(self, tmp_path):
        (tmp_path / "existing.txt").write_text("old")
        action = WriteAction(path="existing.txt", content="new", action="create")
        result = apply_write(action, str(tmp_path), dry_run=False, force=False)
        assert result.success is False
        assert "skipped" in result.action
        assert (tmp_path / "existing.txt").read_text() == "old"

    def test_force_overwrites(self, tmp_path):
        (tmp_path / "existing.txt").write_text("old")
        action = WriteAction(path="existing.txt", content="new", action="overwrite")
        result = apply_write(action, str(tmp_path), dry_run=False, force=True)
        assert result.success is True
        assert (tmp_path / "existing.txt").read_text() == "new"

    def test_rejects_forbidden_path(self, tmp_path):
        action = WriteAction(path=".git/config", content="evil", action="create")
        result = apply_write(action, str(tmp_path), dry_run=False)
        assert result.success is False


class TestApplyMultiple:
    """Test multiple file write operations."""

    def test_dry_run_multiple(self, tmp_path):
        actions = [
            WriteAction(path="a.txt", content="a", action="create"),
            WriteAction(path="b.txt", content="b", action="create"),
        ]
        result = apply_multiple(actions, str(tmp_path), dry_run=True)
        assert result.total_attempted == 2
        assert result.total_written == 0

    def test_apply_multiple(self, tmp_path):
        actions = [
            WriteAction(path="a.txt", content="a", action="create"),
            WriteAction(path="b.txt", content="b", action="create"),
        ]
        result = apply_multiple(actions, str(tmp_path), dry_run=False)
        assert result.total_written == 2
        assert (tmp_path / "a.txt").read_text() == "a"
        assert (tmp_path / "b.txt").read_text() == "b"

    def test_partial_failure(self, tmp_path):
        (tmp_path / "existing.txt").write_text("old")
        actions = [
            WriteAction(path="new.txt", content="new", action="create"),
            WriteAction(path="existing.txt", content="overwrite", action="create"),
        ]
        result = apply_multiple(actions, str(tmp_path), dry_run=False, force=False)
        assert result.total_written == 1
        assert result.total_skipped == 1
