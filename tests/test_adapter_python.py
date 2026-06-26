"""Tests for the Python language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.python import PythonAdapter


@pytest.fixture
def adapter():
    return PythonAdapter()


@pytest.fixture
def python_project(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="test"\nversion="0.1"\n')
    (tmp_path / "main.py").write_text("print('hello')\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "train.py").write_text("# train\n")
    return tmp_path


@pytest.fixture
def requirements_project(tmp_path):
    (tmp_path / "requirements.txt").write_text("numpy>=1.20\npandas\n")
    (tmp_path / "run.py").write_text("# run\n")
    return tmp_path


class TestPythonDetect:
    """Test Python adapter detection."""

    def test_detect_with_pyproject(self, adapter, python_project):
        detection = adapter.detect(python_project)
        assert detection is not None
        assert detection.name == "python"
        assert detection.confidence > 0

    def test_detect_with_requirements(self, adapter, requirements_project):
        detection = adapter.detect(requirements_project)
        assert detection is not None
        assert detection.name == "python"

    def test_detect_empty_returns_none(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None

    def test_detect_includes_evidence(self, adapter, python_project):
        detection = adapter.detect(python_project)
        assert len(detection.evidence) > 0
        assert any("pyproject.toml" in e for e in detection.evidence)

    def test_detect_supports_dry_run(self, adapter, python_project):
        detection = adapter.detect(python_project)
        assert detection.supports_dry_run is True
        assert detection.supports_execute is True


class TestPythonPlan:
    """Test Python adapter planning."""

    def test_plan_with_requirements(self, adapter, requirements_project):
        plan = adapter.plan(requirements_project)
        assert plan.adapter_name == "python"
        assert len(plan.install_steps) > 0
        assert any("pip install" in s.command for s in plan.install_steps)

    def test_plan_with_pyproject(self, adapter, python_project):
        plan = adapter.plan(python_project)
        assert plan.adapter_name == "python"
        assert len(plan.run_steps) > 0

    def test_plan_has_run_steps(self, adapter, python_project):
        plan = adapter.plan(python_project)
        assert any("python" in s.command for s in plan.run_steps)


class TestPythonProperties:
    """Test Python adapter properties."""

    def test_name(self, adapter):
        assert adapter.name == "python"

    def test_display_name(self, adapter):
        assert adapter.display_name == "Python"

    def test_aliases(self, adapter):
        assert "py" in adapter.aliases
        assert "python3" in adapter.aliases

    def test_ecosystem(self, adapter):
        assert adapter.ecosystem == "scripting"

    def test_requires_runtime(self, adapter):
        assert "python3" in adapter.requires_runtime or "python" in adapter.requires_runtime


class TestPythonSafety:
    """Test Python adapter safety rules."""

    def test_has_safety_rules(self, adapter, tmp_path):
        rules = adapter.safety_rules(tmp_path)
        assert len(rules) > 0
