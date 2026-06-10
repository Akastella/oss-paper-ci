"""Tests for capsule format definitions."""

from __future__ import annotations

import pytest

from oss_paper_ci.capsule_format import (
    CAPSULE_DIRS,
    CAPSULE_ROOT_DIR,
    CAPSULE_SCHEMA_VERSION,
    CAPSULE_TYPE,
    EXCLUDED_PATTERNS,
    MAX_ARTIFACT_FILES,
    MAX_ARTIFACT_SIZE_BYTES,
    MAX_CAPSULE_SIZE_BYTES,
    MAX_LOG_SIZE_BYTES,
    REQUIRED_FILES,
    create_capsule_manifest,
)


class TestConstants:
    """Test format constants."""

    def test_schema_version(self):
        assert CAPSULE_SCHEMA_VERSION == "0.1"

    def test_capsule_type(self):
        assert CAPSULE_TYPE == "oss-paper-ci-reproduction-capsule"

    def test_root_dir(self):
        assert CAPSULE_ROOT_DIR == "oss-paper-ci-capsule"

    def test_required_files_not_empty(self):
        assert len(REQUIRED_FILES) > 0
        assert "capsule.json" in REQUIRED_FILES
        assert "SHA256SUMS" in REQUIRED_FILES

    def test_capsule_dirs_not_empty(self):
        assert len(CAPSULE_DIRS) > 0
        assert "reports" in CAPSULE_DIRS
        assert "logs" in CAPSULE_DIRS
        assert "metadata" in CAPSULE_DIRS

    def test_excluded_patterns(self):
        assert ".git" in EXCLUDED_PATTERNS
        assert "__pycache__" in EXCLUDED_PATTERNS
        assert "venv" in EXCLUDED_PATTERNS

    def test_size_limits(self):
        assert MAX_ARTIFACT_SIZE_BYTES > 0
        assert MAX_CAPSULE_SIZE_BYTES > MAX_ARTIFACT_SIZE_BYTES
        assert MAX_ARTIFACT_FILES > 0
        assert MAX_LOG_SIZE_BYTES > 0


class TestCreateManifest:
    """Test create_capsule_manifest function."""

    def test_basic_manifest(self):
        manifest = create_capsule_manifest(
            oss_paper_ci_version="1.9.0rc1",
            source={"input_url": "test", "repo_url": "test", "commit_sha": "abc123", "source_type": "local"},
            execution={"mode": "dry-run", "install": False, "commands_attempted": 0, "commands_succeeded": 0, "commands_failed": 0, "timeout_seconds": 300},
            reports={"reproduce_json": "reports/reproduce_report.json"},
            limitations=["Test limitation"],
        )
        assert manifest["schema_version"] == "0.1"
        assert manifest["capsule_type"] == CAPSULE_TYPE
        assert manifest["created_by"] == "oss-paper-ci"
        assert manifest["oss_paper_ci_version"] == "1.9.0rc1"
        assert manifest["source"]["input_url"] == "test"
        assert manifest["execution"]["mode"] == "dry-run"
        assert manifest["limitations"] == ["Test limitation"]

    def test_manifest_has_integrity(self):
        manifest = create_capsule_manifest(
            oss_paper_ci_version="1.9.0rc1",
            source={},
            execution={},
            reports={},
            limitations=[],
        )
        assert "integrity" in manifest
        assert manifest["integrity"]["sha256sums"] == "SHA256SUMS"
