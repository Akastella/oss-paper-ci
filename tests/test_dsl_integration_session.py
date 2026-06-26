"""Tests that session can record DSL metadata."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.schema import ReproDSL


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestSessionDslMetadata:
    def test_dsl_provides_project_name(self):
        """DSL project name can be used as session name."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert dsl.project.name == "demo-pipeline"

    def test_dsl_provides_step_list(self):
        """DSL steps can be used to create session commands."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        step_ids = list(dsl.steps.keys())
        assert len(step_ids) > 0
        assert all(isinstance(sid, str) for sid in step_ids)

    def test_dsl_provides_commands(self):
        """Each DSL step has a command that can be executed in a session."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        for step_id, step in dsl.steps.items():
            assert step.command, f"Step '{step_id}' has no command"
            assert isinstance(step.command, str)

    def test_dsl_provides_timeout(self):
        """Each DSL step has a timeout for session execution."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        for step_id, step in dsl.steps.items():
            assert step.timeout > 0

    def test_dsl_serializable_for_session_storage(self):
        """DSL can be serialized to JSON for session metadata storage."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        j = dsl.to_json()
        assert isinstance(j, str)
        assert len(j) > 0

    def test_dsl_hash_for_session_identity(self):
        """DSL dag_hash can be used to identify the pipeline version."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        h = dsl.dag_hash()
        assert isinstance(h, str)
        assert len(h) == 16

    def test_dsl_to_dict_for_session_manifest(self):
        """DSL to_dict() output can be embedded in a session manifest."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        d = dsl.to_dict()
        assert isinstance(d, dict)
        assert "version" in d
        assert "steps" in d
