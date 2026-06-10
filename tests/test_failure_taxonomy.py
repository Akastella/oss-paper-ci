"""Tests for failure taxonomy."""

from __future__ import annotations

import pytest

from oss_paper_ci.failure_taxonomy import (
    FAILURE_TYPES,
    FAILURE_TYPE_INDEX,
    format_failure_guidance,
    get_all_failure_types,
    get_failure_type,
)


class TestFailureTypes:
    """Test failure type definitions."""

    def test_all_types_have_required_fields(self):
        for ft in FAILURE_TYPES:
            assert ft.id, f"Missing id"
            assert ft.short_explanation, f"{ft.id}: missing short_explanation"
            assert ft.likely_causes, f"{ft.id}: missing likely_causes"
            assert ft.suggested_next_steps, f"{ft.id}: missing suggested_next_steps"
            assert ft.what_this_does_not_mean, f"{ft.id}: missing what_this_does_not_mean"
            assert ft.severity in ("info", "warning", "error"), f"{ft.id}: invalid severity"

    def test_all_types_have_role_guidance(self):
        for ft in FAILURE_TYPES:
            assert "author" in ft.role_guidance, f"{ft.id}: missing author guidance"
            assert "reviewer" in ft.role_guidance, f"{ft.id}: missing reviewer guidance"

    def test_index_matches_list(self):
        assert len(FAILURE_TYPE_INDEX) == len(FAILURE_TYPES)
        for ft in FAILURE_TYPES:
            assert ft.id in FAILURE_TYPE_INDEX

    def test_required_types_exist(self):
        required = [
            "source_resolution_failed",
            "environment_missing",
            "dependency_install_failed",
            "command_not_declared",
            "command_timeout",
            "command_failed",
            "artifact_missing",
            "scan_blocking_findings",
            "capsule_integrity_failed",
            "unsupported_environment",
        ]
        for type_id in required:
            assert type_id in FAILURE_TYPE_INDEX, f"Missing required type: {type_id}"


class TestGetFailureType:
    """Test failure type lookup."""

    def test_get_existing_type(self):
        ft = get_failure_type("command_failed")
        assert ft is not None
        assert ft.id == "command_failed"

    def test_get_nonexistent_type(self):
        ft = get_failure_type("nonexistent")
        assert ft is None


class TestFormatGuidance:
    """Test guidance formatting."""

    def test_format_existing_type(self):
        text = format_failure_guidance("command_failed")
        assert "command_failed" in text
        assert "Likely causes" in text
        assert "Suggested next steps" in text

    def test_format_with_role(self):
        text = format_failure_guidance("command_failed", role="author")
        assert "For authors" in text

    def test_format_unknown_type(self):
        text = format_failure_guidance("nonexistent")
        assert "Unknown" in text

    def test_to_dict(self):
        ft = get_failure_type("command_failed")
        d = ft.to_dict()
        assert d["id"] == "command_failed"
        assert isinstance(d["likely_causes"], list)
