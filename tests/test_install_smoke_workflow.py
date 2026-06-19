"""Tests for install-smoke workflow."""

import yaml
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent


class TestInstallSmokeWorkflow:
    """Test install-smoke.yml workflow."""

    def test_workflow_exists(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        assert workflow.exists()

    def test_workflow_parseable(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        content = workflow.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "jobs" in data

    def test_workflow_has_matrix(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        jobs = data.get("jobs", {})
        for job_name, job_config in jobs.items():
            if "strategy" in job_config:
                assert "matrix" in job_config["strategy"]
                matrix = job_config["strategy"]["matrix"]
                assert "python-version" in matrix

    def test_workflow_builds_package(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        content = workflow.read_text(encoding="utf-8")
        assert "python -m build" in content

    def test_workflow_installs_wheel(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        content = workflow.read_text(encoding="utf-8")
        assert "pip install" in content

    def test_workflow_verifies_version(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        content = workflow.read_text(encoding="utf-8")
        assert "oss-paper-ci version" in content

    def test_workflow_runs_quickstart(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        content = workflow.read_text(encoding="utf-8")
        assert "quickstart" in content

    def test_workflow_runs_try_demo(self):
        workflow = ROOT / ".github" / "workflows" / "install-smoke.yml"
        content = workflow.read_text(encoding="utf-8")
        assert "try-demo" in content or "try_demo" in content
