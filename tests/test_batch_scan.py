"""Tests for batch scanning."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from oss_paper_ci.batch import run_batch_scan, BatchResult
from oss_paper_ci.workspace import load_workspace


@pytest.fixture
def batch_workspace(tmp_path):
    """Create a workspace with multiple fixture projects."""
    # Create project dirs
    for name in ["proj-a", "proj-b"]:
        proj_dir = tmp_path / name
        proj_dir.mkdir()
        (proj_dir / "README.md").write_text(f"# {name}\nMIT License\n", encoding="utf-8")
        (proj_dir / "LICENSE").write_text("MIT\n", encoding="utf-8")
        (proj_dir / "requirements.txt").write_text("numpy>=1.24\n", encoding="utf-8")

    # Create workspace file
    ws_data = {
        "version": 1,
        "name": "test-batch",
        "projects": [
            {"id": "proj-a", "path": "proj-a"},
            {"id": "proj-b", "path": "proj-b", "profile": "strict"},
        ],
    }
    ws_file = tmp_path / "workspace.yml"
    ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")

    return ws_file


class TestBatchScan:
    """Test batch scan functionality."""

    def test_batch_scan_returns_result(self, batch_workspace):
        ws = load_workspace(batch_workspace)
        result = run_batch_scan(ws, batch_workspace, jobs=1, use_cache=False)

        assert isinstance(result, BatchResult)
        assert result.project_count == 2
        assert len(result.projects) == 2
        assert result.workspace_name == "test-batch"

    def test_batch_scan_json_serializable(self, batch_workspace):
        ws = load_workspace(batch_workspace)
        result = run_batch_scan(ws, batch_workspace, jobs=1, use_cache=False)
        d = result.to_dict()

        # Should be JSON serializable
        text = json.dumps(d)
        parsed = json.loads(text)
        assert parsed["schema_version"] == "0.5"
        assert len(parsed["projects"]) == 2

    def test_batch_scan_project_order(self, batch_workspace):
        ws = load_workspace(batch_workspace)
        result = run_batch_scan(ws, batch_workspace, jobs=1, use_cache=False)

        ids = [p.id for p in result.projects]
        assert ids == ["proj-a", "proj-b"]

    def test_batch_scan_summary(self, batch_workspace):
        ws = load_workspace(batch_workspace)
        result = run_batch_scan(ws, batch_workspace, jobs=1, use_cache=False)
        summary = result.summary

        assert "pass" in summary
        assert "warn" in summary
        assert "fail" in summary
        assert "error" in summary
        assert "average_score" in summary

    def test_batch_scan_missing_path(self, tmp_path):
        ws_data = {
            "version": 1,
            "projects": [
                {"id": "missing", "path": "nonexistent"},
            ],
        }
        ws_file = tmp_path / "workspace.yml"
        ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")

        ws = load_workspace(ws_file)
        result = run_batch_scan(ws, ws_file, jobs=1, use_cache=False)

        assert result.projects[0].error != ""
        assert result.projects[0].status == "unknown"

    def test_batch_scan_error_isolation(self, tmp_path):
        """One project error should not crash the batch."""
        # proj-a is valid
        proj_a = tmp_path / "proj-a"
        proj_a.mkdir()
        (proj_a / "README.md").write_text("# A\nMIT\n", encoding="utf-8")
        (proj_a / "LICENSE").write_text("MIT\n", encoding="utf-8")

        ws_data = {
            "version": 1,
            "projects": [
                {"id": "good", "path": "proj-a"},
                {"id": "bad", "path": "nonexistent"},
            ],
        }
        ws_file = tmp_path / "workspace.yml"
        ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")

        ws = load_workspace(ws_file)
        result = run_batch_scan(ws, ws_file, jobs=1, use_cache=False)

        assert len(result.projects) == 2
        # Good project should have scanned
        good = result.projects[0]
        assert good.error == ""
        assert good.score >= 0
        # Bad project should have error
        bad = result.projects[1]
        assert bad.error != ""

    def test_batch_scan_finding_counts(self, batch_workspace):
        ws = load_workspace(batch_workspace)
        result = run_batch_scan(ws, batch_workspace, jobs=1, use_cache=False)

        for proj in result.projects:
            if not proj.error:
                assert "blocking" in proj.finding_counts
                assert "important" in proj.finding_counts
                assert "advisory" in proj.finding_counts
