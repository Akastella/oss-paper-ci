"""Tests for the C/C++ language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.cpp import CppAdapter


@pytest.fixture
def adapter():
    return CppAdapter()


@pytest.fixture
def cmake_project(tmp_path):
    (tmp_path / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.10)\nproject(test)\n")
    (tmp_path / "main.cpp").write_text('#include <iostream>\nint main() { std::cout << "hello"; }\n')
    return tmp_path


class TestCppDetect:
    def test_detect_with_cmake(self, adapter, cmake_project):
        detection = adapter.detect(cmake_project)
        assert detection is not None
        assert detection.name == "cpp"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestCppPlan:
    def test_plan_cmake(self, adapter, cmake_project):
        plan = adapter.plan(cmake_project)
        assert plan.adapter_name == "cpp"
        assert len(plan.install_steps) > 0
        assert any("cmake" in s.command for s in plan.install_steps)


class TestCppProperties:
    def test_name(self, adapter):
        assert adapter.name == "cpp"

    def test_display_name(self, adapter):
        assert adapter.display_name == "C/C++"

    def test_aliases(self, adapter):
        assert "c" in adapter.aliases
        assert "cmake" in adapter.aliases
