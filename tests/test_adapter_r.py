"""Tests for the R language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.r import RAdapter


@pytest.fixture
def adapter():
    return RAdapter()


@pytest.fixture
def r_project(tmp_path):
    (tmp_path / "DESCRIPTION").write_text("Package: test\nVersion: 0.1\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "analysis.R").write_text("# analysis\n")
    return tmp_path


class TestRDetect:
    def test_detect_with_description(self, adapter, r_project):
        detection = adapter.detect(r_project)
        assert detection is not None
        assert detection.name == "r"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None

    def test_detect_evidence(self, adapter, r_project):
        detection = adapter.detect(r_project)
        assert any("DESCRIPTION" in e for e in detection.evidence)


class TestRPlan:
    def test_plan_with_description(self, adapter, r_project):
        plan = adapter.plan(r_project)
        assert plan.adapter_name == "r"

    def test_plan_has_run_steps(self, adapter, r_project):
        plan = adapter.plan(r_project)
        assert any("Rscript" in s.command for s in plan.run_steps)


class TestRProperties:
    def test_name(self, adapter):
        assert adapter.name == "r"

    def test_display_name(self, adapter):
        assert adapter.display_name == "R"

    def test_aliases(self, adapter):
        assert "rscript" in adapter.aliases

    def test_requires_runtime(self, adapter):
        assert "Rscript" in adapter.requires_runtime
