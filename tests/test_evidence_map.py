"""Tests for evidence map."""

from __future__ import annotations

import pytest

from oss_paper_ci.evidence_map import (
    EvidenceItem,
    build_evidence_map_from_reproduce,
    build_evidence_map_from_scan,
)


class TestEvidenceItem:
    """Test EvidenceItem dataclass."""

    def test_to_dict(self):
        item = EvidenceItem(
            category="metadata",
            item="README",
            status="present",
            source="check META001",
            why_it_matters="Helps others understand the project.",
        )
        d = item.to_dict()
        assert d["category"] == "metadata"
        assert d["status"] == "present"


class TestBuildFromScan:
    """Test evidence map from scan data."""

    def test_basic_scan(self):
        scan_data = {
            "checks": [
                {"id": "META001", "title": "README", "severity": "info", "status": "pass", "message": "OK"},
                {"id": "ENV001", "title": "Deps", "severity": "error", "status": "fail", "message": "Missing"},
            ],
        }
        items = build_evidence_map_from_scan(scan_data)
        assert len(items) >= 2
        categories = {i.category for i in items}
        assert "metadata" in categories
        assert "environment" in categories

    def test_empty_scan(self):
        items = build_evidence_map_from_scan({"checks": []})
        assert items == []


class TestBuildFromReproduce:
    """Test evidence map from reproduce data."""

    def test_with_env_files(self):
        data = {
            "environment": {
                "environment_files": [{"type": "requirements.txt", "path": "requirements.txt"}],
            },
            "reproduction_commands": ["python train.py"],
            "generated_artifacts": ["results/metrics.json"],
            "commit_sha": "abc123def456",
        }
        items = build_evidence_map_from_reproduce(data)
        assert len(items) >= 3
        categories = {i.category for i in items}
        assert "environment" in categories
        assert "execution" in categories

    def test_without_env_files(self):
        data = {"environment": None, "reproduction_commands": []}
        items = build_evidence_map_from_reproduce(data)
        assert any(i.status == "missing" for i in items)
