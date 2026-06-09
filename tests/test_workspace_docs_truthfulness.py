"""Tests for documentation truthfulness — workspace/batch/cache features."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent


class TestWorkspaceExamplesExist:
    """Test that workspace examples referenced in docs exist."""

    def test_demo_workspace_exists(self):
        ws = ROOT / "examples" / "workspaces" / "demo-workspace.yml"
        assert ws.exists(), f"Missing: {ws}"

    def test_strict_publication_workspace_exists(self):
        ws = ROOT / "examples" / "workspaces" / "strict-publication-workspace.yml"
        assert ws.exists(), f"Missing: {ws}"

    def test_mixed_fixtures_workspace_exists(self):
        ws = ROOT / "examples" / "workspaces" / "mixed-fixtures-workspace.yml"
        assert ws.exists(), f"Missing: {ws}"

    def test_workspaces_readme_exists(self):
        readme = ROOT / "examples" / "workspaces" / "README.md"
        assert readme.exists(), f"Missing: {readme}"


class TestWorkspaceExamplesValid:
    """Test that workspace examples pass validation."""

    def _validate(self, ws_path: Path):
        from oss_paper_ci.workspace import validate_workspace
        result = validate_workspace(ws_path)
        assert result.valid, f"Invalid {ws_path}: {result.format_text()}"

    def test_demo_workspace_valid(self):
        self._validate(ROOT / "examples" / "workspaces" / "demo-workspace.yml")

    def test_strict_publication_valid(self):
        self._validate(ROOT / "examples" / "workspaces" / "strict-publication-workspace.yml")

    def test_mixed_fixtures_valid(self):
        self._validate(ROOT / "examples" / "workspaces" / "mixed-fixtures-workspace.yml")


class TestDocsExist:
    """Test that required documentation files exist."""

    def test_workspace_md(self):
        assert (ROOT / "docs" / "workspace.md").exists()

    def test_batch_scan_md(self):
        assert (ROOT / "docs" / "batch-scan.md").exists()

    def test_cache_md(self):
        assert (ROOT / "docs" / "cache.md").exists()

    def test_parallelism_md(self):
        assert (ROOT / "docs" / "parallelism.md").exists()

    def test_batch_diff_md(self):
        assert (ROOT / "docs" / "batch-diff.md").exists()

    def test_scale_gate_md(self):
        assert (ROOT / "docs" / "scale-gate.md").exists()


class TestDocsHonesty:
    """Test that docs don't make false claims."""

    def _read_docs(self, name: str) -> str:
        return (ROOT / "docs" / name).read_text(encoding="utf-8")

    def test_batch_does_not_judge_paper_quality(self):
        text = self._read_docs("batch-scan.md")
        lower = text.lower()
        # Should not claim the tool CAN judge quality
        assert "can judge paper quality" not in lower
        assert "can determine paper quality" not in lower
        assert "evaluates paper quality" not in lower

    def test_scale_gate_not_academic_benchmark(self):
        text = self._read_docs("scale-gate.md")
        assert "not an academic" in text.lower() or "not a performance benchmark" in text.lower()

    def test_workspace_not_cloud_platform(self):
        text = self._read_docs("workspace.md")
        assert "not a cloud" in text.lower() or "local" in text.lower()


class TestGitHubActionExamples:
    """Test that GitHub Action examples exist and are valid YAML."""

    def _load_yaml(self, path: Path):
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_workspace_batch_yml(self):
        p = ROOT / "examples" / "github-actions" / "workspace-batch.yml"
        assert p.exists()
        data = self._load_yaml(p)
        # YAML parses 'on' as True (boolean)
        assert True in data or "on" in data
        assert "jobs" in data

    def test_workspace_cache_yml(self):
        p = ROOT / "examples" / "github-actions" / "workspace-cache.yml"
        assert p.exists()
        data = self._load_yaml(p)
        assert True in data or "on" in data

    def test_workspace_publication_gate_yml(self):
        p = ROOT / "examples" / "github-actions" / "workspace-publication-gate.yml"
        assert p.exists()
        data = self._load_yaml(p)
        assert True in data or "on" in data


class TestGitignore:
    """Test that .gitignore excludes cache directory."""

    def test_cache_dir_ignored(self):
        gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert ".oss-paper-ci-cache/" in gi

    def test_audit_files_ignored(self):
        gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert ".local_" in gi
