"""Tests for the Java language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.java import JavaAdapter


@pytest.fixture
def adapter():
    return JavaAdapter()


@pytest.fixture
def java_project(tmp_path):
    (tmp_path / "pom.xml").write_text('<project><modelVersion>4.0.0</modelVersion></project>\n')
    return tmp_path


class TestJavaDetect:
    def test_detect_with_pom(self, adapter, java_project):
        detection = adapter.detect(java_project)
        assert detection is not None
        assert detection.name == "java"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestJavaPlan:
    def test_plan_maven(self, adapter, java_project):
        plan = adapter.plan(java_project)
        assert plan.adapter_name == "java"
        assert len(plan.install_steps) > 0
        assert any("mvn" in s.command for s in plan.install_steps)


class TestJavaProperties:
    def test_name(self, adapter):
        assert adapter.name == "java"

    def test_display_name(self, adapter):
        assert adapter.display_name == "Java"

    def test_aliases(self, adapter):
        assert "maven" in adapter.aliases
        assert "gradle" in adapter.aliases

    def test_requires_runtime(self, adapter):
        assert "java" in adapter.requires_runtime
