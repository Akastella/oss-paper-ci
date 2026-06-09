"""Tests for the cache system."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from oss_paper_ci.cache import (
    CACHE_DIR_NAME,
    clean_cache,
    compute_cache_key,
    get_cache_dir,
    get_cache_info,
    get_project_cache_file,
    lookup_cache,
    store_cache,
)
from oss_paper_ci.workspace import load_workspace


@pytest.fixture
def project_dir(tmp_path):
    """Create a simple project directory."""
    proj = tmp_path / "project"
    proj.mkdir()
    (proj / "README.md").write_text("# Test\nMIT\n", encoding="utf-8")
    (proj / "LICENSE").write_text("MIT\n", encoding="utf-8")
    return proj


@pytest.fixture
def cache_dir(tmp_path):
    """Create a cache directory."""
    d = tmp_path / CACHE_DIR_NAME
    d.mkdir()
    return d


class TestCacheKey:
    """Test cache key computation."""

    def test_same_input_same_key(self, project_dir):
        k1 = compute_cache_key(str(project_dir), "default", "", [])
        k2 = compute_cache_key(str(project_dir), "default", "", [])
        assert k1 == k2

    def test_different_profile_different_key(self, project_dir):
        k1 = compute_cache_key(str(project_dir), "default", "", [])
        k2 = compute_cache_key(str(project_dir), "strict", "", [])
        assert k1 != k2

    def test_different_config_different_key(self, project_dir):
        k1 = compute_cache_key(str(project_dir), "default", "", [])
        k2 = compute_cache_key(str(project_dir), "default", "some config", [])
        assert k1 != k2

    def test_different_rules_different_key(self, project_dir):
        k1 = compute_cache_key(str(project_dir), "default", "", [])
        k2 = compute_cache_key(str(project_dir), "default", "", ["rule1"])
        assert k1 != k2

    def test_file_change_different_key(self, project_dir):
        k1 = compute_cache_key(str(project_dir), "default", "", [])
        (project_dir / "new_file.py").write_text("x = 1\n", encoding="utf-8")
        k2 = compute_cache_key(str(project_dir), "default", "", [])
        assert k1 != k2

    def test_content_change_different_key(self, project_dir):
        k1 = compute_cache_key(str(project_dir), "default", "", [])
        (project_dir / "README.md").write_text("# Changed\n", encoding="utf-8")
        k2 = compute_cache_key(str(project_dir), "default", "", [])
        assert k1 != k2


class TestCacheStorage:
    """Test cache store and lookup."""

    def test_store_and_lookup(self, cache_dir):
        report = {"summary": {"score": 90, "status": "pass"}}
        store_cache(cache_dir, "proj-a", "key123", report)

        result = lookup_cache(cache_dir, "proj-a", "key123")
        assert result is not None
        assert result["summary"]["score"] == 90

    def test_lookup_miss_wrong_key(self, cache_dir):
        report = {"summary": {"score": 90}}
        store_cache(cache_dir, "proj-a", "key123", report)

        result = lookup_cache(cache_dir, "proj-a", "wrong_key")
        assert result is None

    def test_lookup_miss_no_file(self, cache_dir):
        result = lookup_cache(cache_dir, "nonexistent", "key123")
        assert result is None

    def test_corrupt_cache_returns_none(self, cache_dir):
        cache_file = get_project_cache_file(cache_dir, "proj-a")
        cache_file.write_text("not valid json{{{", encoding="utf-8")

        result = lookup_cache(cache_dir, "proj-a", "key123")
        assert result is None

    def test_corrupt_cache_wrong_schema_version(self, cache_dir):
        cache_file = get_project_cache_file(cache_dir, "proj-a")
        cache_file.write_text(json.dumps({
            "schema_version": "999",
            "cache_key": "key123",
            "report": {},
        }), encoding="utf-8")

        result = lookup_cache(cache_dir, "proj-a", "key123")
        assert result is None


class TestCacheClean:
    """Test cache cleaning."""

    def test_clean_removes_files(self, cache_dir):
        store_cache(cache_dir, "a", "k1", {"x": 1})
        store_cache(cache_dir, "b", "k2", {"x": 2})
        assert len(list(cache_dir.glob("*.json"))) == 2

        count = clean_cache(cache_dir.parent)
        assert count == 2
        assert not cache_dir.exists()

    def test_clean_nonexistent_dir(self, tmp_path):
        count = clean_cache(tmp_path / "nonexistent")
        assert count == 0


class TestCacheInfo:
    """Test cache info."""

    def test_info_no_cache(self, tmp_path):
        info = get_cache_info(tmp_path)
        assert info["exists"] is False
        assert info["entries"] == 0

    def test_info_with_cache(self, cache_dir):
        store_cache(cache_dir, "a", "k1", {"x": 1})
        store_cache(cache_dir, "b", "k2", {"x": 2})

        info = get_cache_info(cache_dir.parent)
        assert info["exists"] is True
        assert info["entries"] == 2
        assert info["total_size_bytes"] > 0


class TestCacheIntegration:
    """Test cache integration with batch scan."""

    def test_cache_hit_on_second_scan(self, tmp_path):
        # Create project
        proj = tmp_path / "proj"
        proj.mkdir()
        (proj / "README.md").write_text("# Test\nMIT\n", encoding="utf-8")
        (proj / "LICENSE").write_text("MIT\n", encoding="utf-8")

        ws_data = {
            "version": 1,
            "projects": [{"id": "proj", "path": "proj"}],
        }
        ws_file = tmp_path / "workspace.yml"
        ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")

        from oss_paper_ci.batch import run_batch_scan
        ws = load_workspace(ws_file)

        # First run — cache miss
        result1 = run_batch_scan(ws, ws_file, jobs=1, use_cache=True)
        assert result1.projects[0].cache_hit is False

        # Second run — cache hit
        result2 = run_batch_scan(ws, ws_file, jobs=1, use_cache=True)
        assert result2.projects[0].cache_hit is True
        assert result2.projects[0].score == result1.projects[0].score

    def test_cache_miss_after_file_change(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        (proj / "README.md").write_text("# Test\nMIT\n", encoding="utf-8")
        (proj / "LICENSE").write_text("MIT\n", encoding="utf-8")

        ws_data = {
            "version": 1,
            "projects": [{"id": "proj", "path": "proj"}],
        }
        ws_file = tmp_path / "workspace.yml"
        ws_file.write_text(yaml.dump(ws_data), encoding="utf-8")

        from oss_paper_ci.batch import run_batch_scan
        ws = load_workspace(ws_file)

        # First run
        result1 = run_batch_scan(ws, ws_file, jobs=1, use_cache=True)
        assert result1.projects[0].cache_hit is False

        # Change a file
        (proj / "README.md").write_text("# Changed\nMIT\n", encoding="utf-8")

        # Second run — cache miss
        result2 = run_batch_scan(ws, ws_file, jobs=1, use_cache=True)
        assert result2.projects[0].cache_hit is False
