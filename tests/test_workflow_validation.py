"""Tests for workflow YAML validation."""

import yaml
from pathlib import Path

import pytest

EXAMPLES = Path("examples/github-actions")


class TestWorkflowValidation:
    """Test that example workflow YAML files are valid."""

    def test_all_workflows_parseable(self):
        if not EXAMPLES.exists():
            pytest.skip("examples/github-actions not found")
        for f in EXAMPLES.glob("*.yml"):
            with open(f, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
                assert data is not None, f"Failed to parse {f}"

    def test_workflows_have_jobs(self):
        if not EXAMPLES.exists():
            pytest.skip("examples/github-actions not found")
        for f in EXAMPLES.glob("*.yml"):
            with open(f, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
                # YAML parses `on` as True, so check jobs key
                assert "jobs" in data, f"{f.name} missing jobs"

    def test_workflows_have_on_trigger(self):
        if not EXAMPLES.exists():
            pytest.skip("examples/github-actions not found")
        for f in EXAMPLES.glob("*.yml"):
            with open(f, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
                # `on:` is parsed as True by PyYAML
                assert True in data or "on" in data, f"{f.name} missing on trigger"

    def test_oss_paper_ci_workflow_has_steps(self):
        if not EXAMPLES.exists():
            pytest.skip("examples/github-actions not found")
        wf = EXAMPLES / "oss-paper-ci.yml"
        if not wf.exists():
            pytest.skip("oss-paper-ci.yml not found")
        with open(wf, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        jobs = data.get("jobs", {})
        for job_name, job_def in jobs.items():
            assert "steps" in job_def, f"Job {job_name} missing steps"

    def test_workflow_names_are_strings(self):
        if not EXAMPLES.exists():
            pytest.skip("examples/github-actions not found")
        for f in EXAMPLES.glob("*.yml"):
            with open(f, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
                if "name" in data:
                    assert isinstance(data["name"], str), f"{f.name} name is not a string"


class TestActionYmlValidation:
    """Test that action.yml is well-formed."""

    def test_action_yml_valid(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "name" in data
        assert "inputs" in data
        assert "runs" in data

    def test_action_name(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["name"] == "oss-paper-ci"

    def test_action_has_description(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "description" in data

    def test_action_has_branding(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "branding" in data

    def test_action_inputs_have_descriptions(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        inputs = data.get("inputs", {})
        for name, inp in inputs.items():
            assert "description" in inp, f"Input {name} missing description"

    def test_action_runs_is_composite(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["runs"]["using"] == "composite"

    def test_action_runs_has_steps(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        steps = data["runs"]["steps"]
        assert len(steps) >= 3  # setup-python, install, run

    def test_action_steps_have_names(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for step in data["runs"]["steps"]:
            assert "name" in step, "Step missing name"

    def test_action_steps_have_shell(self):
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for step in data["runs"]["steps"]:
            if "uses" not in step:
                assert "shell" in step, f"Step '{step.get('name')}' missing shell"
