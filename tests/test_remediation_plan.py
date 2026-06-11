"""Tests for remediation plan."""

from __future__ import annotations

import pytest

from oss_paper_ci.remediation import (
    RemediationItem,
    build_remediation_from_reproduce,
    build_remediation_from_scan,
)


class TestRemediationItem:
    """Test RemediationItem dataclass."""

    def test_to_dict(self):
        item = RemediationItem(
            priority="P0",
            action="Add requirements.txt",
            rationale="No deps declared",
            estimated_effort="low",
            blocking=True,
        )
        d = item.to_dict()
        assert d["priority"] == "P0"
        assert d["blocking"] is True


class TestBuildFromScan:
    """Test remediation from scan data."""

    def test_error_gives_p0(self):
        scan_data = {
            "checks": [
                {"id": "ENV001", "title": "Deps", "severity": "error", "status": "fail",
                 "message": "Missing", "recommendation": "Add requirements.txt"},
            ],
        }
        items = build_remediation_from_scan(scan_data)
        assert len(items) >= 1
        assert items[0].priority == "P0"
        assert items[0].blocking is True

    def test_warning_gives_p1(self):
        scan_data = {
            "checks": [
                {"id": "META003", "title": "Citation", "severity": "warning", "status": "warn",
                 "message": "No citation", "recommendation": "Add CITATION.cff"},
            ],
        }
        items = build_remediation_from_scan(scan_data)
        assert len(items) >= 1
        assert items[0].priority == "P1"


class TestBuildFromReproduce:
    """Test remediation from reproduce data."""

    def test_missing_env_gives_p0(self):
        data = {"environment": None, "reproduction_commands": [], "command_results": []}
        items = build_remediation_from_reproduce(data)
        assert any(i.priority == "P0" for i in items)
