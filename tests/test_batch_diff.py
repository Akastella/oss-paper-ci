"""Tests for batch diff functionality."""

from __future__ import annotations

import json

import pytest

from oss_paper_ci.batch import compute_batch_diff, format_batch_diff_markdown


def _make_batch(projects, average_score=80.0):
    """Helper to create a batch result dict."""
    return {
        "workspace": {"name": "test", "project_count": len(projects)},
        "summary": {"average_score": average_score},
        "projects": projects,
    }


class TestBatchDiff:
    """Test batch diff computation."""

    def test_identical_batches(self):
        batch = _make_batch([
            {"id": "a", "score": 90, "status": "pass"},
            {"id": "b", "score": 70, "status": "warn"},
        ])
        diff = compute_batch_diff(batch, batch)

        assert diff["project_added"] == []
        assert diff["project_removed"] == []
        assert diff["average_score_delta"] == 0
        assert diff["new_failures"] == []
        assert diff["resolved_failures"] == []

    def test_project_added(self):
        old = _make_batch([{"id": "a", "score": 90, "status": "pass"}])
        new = _make_batch([
            {"id": "a", "score": 90, "status": "pass"},
            {"id": "b", "score": 80, "status": "pass"},
        ])
        diff = compute_batch_diff(old, new)

        assert diff["project_added"] == ["b"]
        assert diff["project_removed"] == []

    def test_project_removed(self):
        old = _make_batch([
            {"id": "a", "score": 90, "status": "pass"},
            {"id": "b", "score": 80, "status": "pass"},
        ])
        new = _make_batch([{"id": "a", "score": 90, "status": "pass"}])
        diff = compute_batch_diff(old, new)

        assert diff["project_added"] == []
        assert diff["project_removed"] == ["b"]

    def test_score_delta(self):
        old = _make_batch([{"id": "a", "score": 70, "status": "warn"}])
        new = _make_batch([{"id": "a", "score": 90, "status": "pass"}])
        diff = compute_batch_diff(old, new)

        assert diff["project_diffs"][0]["score_delta"] == 20
        assert diff["project_diffs"][0]["status_changed"] is True

    def test_new_failure(self):
        old = _make_batch([{"id": "a", "score": 80, "status": "pass"}])
        new = _make_batch([{"id": "a", "score": 40, "status": "fail"}])
        diff = compute_batch_diff(old, new)

        assert diff["new_failures"] == ["a"]
        assert diff["resolved_failures"] == []

    def test_resolved_failure(self):
        old = _make_batch([{"id": "a", "score": 40, "status": "fail"}])
        new = _make_batch([{"id": "a", "score": 80, "status": "pass"}])
        diff = compute_batch_diff(old, new)

        assert diff["new_failures"] == []
        assert diff["resolved_failures"] == ["a"]

    def test_average_score_delta(self):
        old = _make_batch([{"id": "a", "score": 70, "status": "warn"}], average_score=70.0)
        new = _make_batch([{"id": "a", "score": 90, "status": "pass"}], average_score=90.0)
        diff = compute_batch_diff(old, new)

        assert diff["average_score_delta"] == 20.0


class TestBatchDiffMarkdown:
    """Test batch diff markdown formatting."""

    def test_markdown_contains_summary(self):
        diff = {
            "old_workspace": "old", "new_workspace": "new",
            "old_project_count": 2, "new_project_count": 3,
            "project_added": ["c"], "project_removed": [],
            "project_diffs": [],
            "new_failures": [], "resolved_failures": [],
            "old_average_score": 80.0, "new_average_score": 85.0,
            "average_score_delta": 5.0,
        }
        text = format_batch_diff_markdown(diff)
        assert "Projects Added" in text
        assert "c" in text
        assert "85.0" in text

    def test_markdown_contains_project_changes(self):
        diff = {
            "old_workspace": "", "new_workspace": "",
            "old_project_count": 1, "new_project_count": 1,
            "project_added": [], "project_removed": [],
            "project_diffs": [
                {"id": "a", "old_score": 70, "new_score": 90,
                 "score_delta": 20, "old_status": "warn", "new_status": "pass",
                 "status_changed": True},
            ],
            "new_failures": [], "resolved_failures": [],
            "old_average_score": 70.0, "new_average_score": 90.0,
            "average_score_delta": 20.0,
        }
        text = format_batch_diff_markdown(diff)
        assert "Project Changes" in text
        assert "a" in text
        assert "+20" in text

    def test_markdown_json_serializable(self):
        diff = compute_batch_diff(
            _make_batch([{"id": "a", "score": 70, "status": "warn"}]),
            _make_batch([{"id": "a", "score": 90, "status": "pass"}]),
        )
        # Should be JSON serializable
        text = json.dumps(diff)
        assert "score_delta" in text
