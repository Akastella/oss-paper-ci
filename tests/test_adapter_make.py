"""Tests for the Make language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.make import MakeAdapter


@pytest.fixture
def adapter():
    return MakeAdapter()


@pytest.fixture
def make_project(tmp_path):
    (tmp_path / "Makefile").write_text("all:\n\techo hello\n\nreproduce:\n\techo reproduce\n")
    return tmp_path


class TestMakeDetect:
    def test_detect_with_makefile(self, adapter, make_project):
        detection = adapter.detect(make_project)
        assert detection is not None
        assert detection.name == "make"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestMakePlan:
    def test_plan_with_reproduce_target(self, adapter, make_project):
        plan = adapter.plan(make_project)
        assert plan.adapter_name == "make"
        assert len(plan.run_steps) > 0
        assert any("make reproduce" in s.command for s in plan.run_steps)


class TestMakeProperties:
    def test_name(self, adapter):
        assert adapter.name == "make"

    def test_display_name(self, adapter):
        assert adapter.display_name == "Make"

    def test_requires_runtime(self, adapter):
        assert "make" in adapter.requires_runtime


class TestMakeTargetParsing:
    def test_parses_targets(self, adapter, make_project):
        targets = adapter._parse_makefile_targets(make_project)
        assert "all" in targets
        assert "reproduce" in targets
