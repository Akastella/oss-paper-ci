"""Tests for parallel batch scanning."""

from __future__ import annotations

import pytest
import yaml

from oss_paper_ci.batch import run_batch_scan
from oss_paper_ci.workspace import load_workspace


@pytest.fixture
def parallel_workspace(tmp_path):
    """Create workspace with multiple small projects."""
    for i in range(4):
        proj_dir = tmp_path / f"proj-{i}"
        proj_dir.mkdir()
        (proj_dir / "README.md").write_text(f"# Project {i}\nMIT\n", encoding="utf-8")
        (proj_dir / "LICENSE").write_text("MIT\n", encoding="utf-8")

    ws_data = {
        "version": 1,
        "name": "parallel-test",
        "projects": [
            {"id": f"proj-{i}", "path": f"proj-{i}"}
            for i in range(4)
        ],
    }
    ws_file = tmp_path / "workspace.yml"
    ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")
    return ws_file


class TestParallelBatch:
    """Test parallel batch scanning."""

    def test_jobs_1_works(self, parallel_workspace):
        ws = load_workspace(parallel_workspace)
        result = run_batch_scan(ws, parallel_workspace, jobs=1, use_cache=False)

        assert result.project_count == 4
        ids = [p.id for p in result.projects]
        assert ids == ["proj-0", "proj-1", "proj-2", "proj-3"]

    def test_jobs_2_works(self, parallel_workspace):
        ws = load_workspace(parallel_workspace)
        result = run_batch_scan(ws, parallel_workspace, jobs=2, use_cache=False)

        assert result.project_count == 4
        ids = [p.id for p in result.projects]
        assert ids == ["proj-0", "proj-1", "proj-2", "proj-3"]

    def test_output_order_deterministic(self, parallel_workspace):
        """Multiple runs with jobs=2 should produce same order."""
        ws = load_workspace(parallel_workspace)

        results = []
        for _ in range(3):
            result = run_batch_scan(ws, parallel_workspace, jobs=2, use_cache=False)
            results.append([p.id for p in result.projects])

        # All runs should have same order
        assert all(r == results[0] for r in results)

    def test_parallel_scores_match_sequential(self, parallel_workspace):
        """Scores should be identical regardless of job count."""
        ws = load_workspace(parallel_workspace)

        result_1 = run_batch_scan(ws, parallel_workspace, jobs=1, use_cache=False)
        result_2 = run_batch_scan(ws, parallel_workspace, jobs=2, use_cache=False)

        scores_1 = [p.score for p in result_1.projects]
        scores_2 = [p.score for p in result_2.projects]
        assert scores_1 == scores_2

    def test_parallel_error_isolation(self, tmp_path):
        """One failing project should not crash parallel scan."""
        proj_a = tmp_path / "good"
        proj_a.mkdir()
        (proj_a / "README.md").write_text("# Good\nMIT\n", encoding="utf-8")
        (proj_a / "LICENSE").write_text("MIT\n", encoding="utf-8")

        ws_data = {
            "version": 1,
            "projects": [
                {"id": "good", "path": "good"},
                {"id": "bad", "path": "nonexistent"},
                {"id": "good2", "path": "good"},
            ],
        }
        ws_file = tmp_path / "workspace.yml"
        ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")

        ws = load_workspace(ws_file)
        result = run_batch_scan(ws, ws_file, jobs=2, use_cache=False)

        assert len(result.projects) == 3
        assert result.projects[0].error == ""
        assert result.projects[1].error != ""
        assert result.projects[2].error == ""
