"""Tests for environment detection module."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.environment import EnvironmentPlan, detect_environment


class TestRequirementsTxt:
    """Test requirements.txt detection."""

    def test_detects_requirements_txt(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("numpy>=1.24\n")
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 1
        assert plan.environment_files[0].file_type == "requirements.txt"
        assert len(plan.install_steps) == 1
        assert "pip install -r requirements.txt" in plan.install_steps[0].command

    def test_empty_requirements_txt(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("")
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 1
        assert len(plan.install_steps) == 1


class TestPyprojectToml:
    """Test pyproject.toml detection."""

    def test_detects_pyproject_toml(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 1
        assert plan.environment_files[0].file_type == "pyproject.toml"
        assert len(plan.install_steps) == 1
        assert "pip install -e ." in plan.install_steps[0].command


class TestSetupPy:
    """Test setup.py detection."""

    def test_detects_setup_py(self, tmp_path):
        (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()\n")
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 1
        assert plan.environment_files[0].file_type == "setup.py"


class TestCondaEnvironments:
    """Test conda environment detection."""

    def test_detects_environment_yml(self, tmp_path):
        (tmp_path / "environment.yml").write_text(
            "name: test\ndependencies:\n  - python=3.11\n  - numpy\n"
        )
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 1
        assert plan.environment_files[0].file_type == "environment.yml"
        assert plan.python_version == "3.11"
        assert len(plan.warnings) > 0
        assert "Conda" in plan.warnings[0]

    def test_conda_with_requirements_fallback(self, tmp_path):
        (tmp_path / "environment.yml").write_text("name: test\ndependencies:\n  - numpy\n")
        (tmp_path / "requirements.txt").write_text("numpy\n")
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 2
        # Should have pip install step as fallback
        assert len(plan.install_steps) == 1
        assert "pip install" in plan.install_steps[0].command

    def test_conda_without_fallback(self, tmp_path):
        (tmp_path / "environment.yml").write_text("name: test\ndependencies:\n  - numpy\n")
        plan = detect_environment(str(tmp_path))
        assert not plan.supported
        assert len(plan.warnings) > 0


class TestPipfile:
    """Test Pipfile detection."""

    def test_detects_pipfile(self, tmp_path):
        (tmp_path / "Pipfile").write_text("[packages]\nnumpy = \"*\"\n")
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 1
        assert plan.environment_files[0].file_type == "Pipfile"


class TestPoetryLock:
    """Test poetry.lock detection."""

    def test_detects_poetry_lock(self, tmp_path):
        (tmp_path / "poetry.lock").write_text("")
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 1
        assert plan.environment_files[0].file_type == "poetry.lock"
        assert not plan.supported

    def test_poetry_with_pyproject_fallback(self, tmp_path):
        (tmp_path / "poetry.lock").write_text("")
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 2
        assert len(plan.install_steps) == 1


class TestNoEnvironmentFiles:
    """Test when no environment files exist."""

    def test_empty_repo(self, tmp_path):
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 0
        assert len(plan.install_steps) == 0
        assert len(plan.warnings) > 0
        assert "No environment files" in plan.warnings[0]


class TestMultipleFiles:
    """Test priority when multiple files exist."""

    def test_requirements_takes_priority(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("numpy\n")
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
        plan = detect_environment(str(tmp_path))
        assert len(plan.environment_files) == 2
        # First install step should be for requirements.txt
        assert "requirements.txt" in plan.install_steps[0].command


class TestSerialization:
    """Test to_dict serialization."""

    def test_to_dict(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("numpy\n")
        plan = detect_environment(str(tmp_path))
        d = plan.to_dict()
        assert "environment_files" in d
        assert "install_steps" in d
        assert isinstance(d["environment_files"], list)
        assert isinstance(d["install_steps"], list)
