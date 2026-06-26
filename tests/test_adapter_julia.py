"""Tests for the Julia language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.julia import JuliaAdapter


@pytest.fixture
def adapter():
    return JuliaAdapter()


@pytest.fixture
def julia_project(tmp_path):
    (tmp_path / "Project.toml").write_text('[deps]\nUnicode = "4ec0a83e-493e-50e2-b9ac-8f72acf5a8f5"\n')
    (tmp_path / "main.jl").write_text("println('hello')\n")
    return tmp_path


class TestJuliaDetect:
    def test_detect_with_project_toml(self, adapter, julia_project):
        detection = adapter.detect(julia_project)
        assert detection is not None
        assert detection.name == "julia"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestJuliaPlan:
    def test_plan(self, adapter, julia_project):
        plan = adapter.plan(julia_project)
        assert plan.adapter_name == "julia"
        assert len(plan.install_steps) > 0
        assert any("Pkg.instantiate" in s.command for s in plan.install_steps)


class TestJuliaProperties:
    def test_name(self, adapter):
        assert adapter.name == "julia"

    def test_display_name(self, adapter):
        assert adapter.display_name == "Julia"

    def test_requires_runtime(self, adapter):
        assert "julia" in adapter.requires_runtime
