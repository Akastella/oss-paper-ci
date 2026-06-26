"""Tests for the Nextflow language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.nextflow import NextflowAdapter


@pytest.fixture
def adapter():
    return NextflowAdapter()


@pytest.fixture
def nextflow_project(tmp_path):
    (tmp_path / "main.nf").write_text("process hello {\n  script:\n  'echo hello'\n}\n")
    (tmp_path / "nextflow.config").write_text("process.executor = 'local'\n")
    return tmp_path


class TestNextflowDetect:
    def test_detect_with_main_nf(self, adapter, nextflow_project):
        detection = adapter.detect(nextflow_project)
        assert detection is not None
        assert detection.name == "nextflow"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestNextflowPlan:
    def test_plan_preview(self, adapter, nextflow_project):
        plan = adapter.plan(nextflow_project)
        assert plan.adapter_name == "nextflow"
        assert any("preview" in s.command.lower() or "-preview" in s.command for s in plan.run_steps)


class TestNextflowProperties:
    def test_name(self, adapter):
        assert adapter.name == "nextflow"

    def test_supports_execute_false(self, adapter):
        assert adapter.supports_execute is False

    def test_supports_dry_run(self, adapter):
        assert adapter.supports_dry_run is True
