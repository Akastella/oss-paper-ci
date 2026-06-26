"""Tests that GitHub Actions YAML files are valid YAML."""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml


WORKFLOWS_DIR = Path(__file__).parent.parent / ".github" / "workflows"


def _get_workflow_files():
    if not WORKFLOWS_DIR.exists():
        return []
    return list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))


class TestGitHubActionsYaml:
    @pytest.mark.parametrize("wf_file", _get_workflow_files(), ids=lambda p: p.name)
    def test_valid_yaml(self, wf_file):
        """Every .yml file under .github/workflows/ should parse as valid YAML."""
        with open(wf_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert isinstance(data, dict)

    @pytest.mark.parametrize("wf_file", _get_workflow_files(), ids=lambda p: p.name)
    def test_has_name(self, wf_file):
        with open(wf_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "name" in data

    @pytest.mark.parametrize("wf_file", _get_workflow_files(), ids=lambda p: p.name)
    def test_has_on_trigger(self, wf_file):
        with open(wf_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "on" in data or True in data  # YAML parses `on` as True

    @pytest.mark.parametrize("wf_file", _get_workflow_files(), ids=lambda p: p.name)
    def test_has_jobs(self, wf_file):
        with open(wf_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "jobs" in data

    @pytest.mark.parametrize("wf_file", _get_workflow_files(), ids=lambda p: p.name)
    def test_jobs_have_steps(self, wf_file):
        with open(wf_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for job_name, job in data.get("jobs", {}).items():
            assert "steps" in job, f"Job '{job_name}' has no steps"


class TestCiWorkflowSpecific:
    @pytest.fixture
    def ci_data(self):
        path = WORKFLOWS_DIR / "ci.yml"
        if not path.exists():
            pytest.skip("ci.yml not found")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_ci_runs_tests(self, ci_data):
        """CI should run pytest."""
        steps = []
        for job in ci_data.get("jobs", {}).values():
            steps.extend(job.get("steps", []))
        step_names = [s.get("name", "") or s.get("run", "") for s in steps]
        assert any("pytest" in s or "test" in s.lower() for s in step_names)

    def test_ci_tests_on_multiple_python_versions(self, ci_data):
        """CI should test on multiple Python versions."""
        test_job = ci_data.get("jobs", {}).get("test", {})
        matrix = test_job.get("strategy", {}).get("matrix", {})
        versions = matrix.get("python-version", [])
        assert len(versions) >= 2
