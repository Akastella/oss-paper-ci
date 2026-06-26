"""Tests for the Snakemake language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.snakemake import SnakemakeAdapter


@pytest.fixture
def adapter():
    return SnakemakeAdapter()


@pytest.fixture
def snakemake_project(tmp_path):
    (tmp_path / "Snakefile").write_text("rule all:\n\tinput: 'output.txt'\n")
    return tmp_path


class TestSnakemakeDetect:
    def test_detect_with_snakefile(self, adapter, snakemake_project):
        detection = adapter.detect(snakemake_project)
        assert detection is not None
        assert detection.name == "snakemake"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestSnakemakePlan:
    def test_plan_dry_run_only(self, adapter, snakemake_project):
        plan = adapter.plan(snakemake_project)
        assert plan.adapter_name == "snakemake"
        # Snakemake is dry-run only
        assert any("-n" in s.command or "dry" in s.description.lower() for s in plan.run_steps)


class TestSnakemakeProperties:
    def test_name(self, adapter):
        assert adapter.name == "snakemake"

    def test_supports_execute_false(self, adapter):
        assert adapter.supports_execute is False

    def test_supports_dry_run(self, adapter):
        assert adapter.supports_dry_run is True
