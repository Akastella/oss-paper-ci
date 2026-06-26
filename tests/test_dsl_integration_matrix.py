"""Tests that matrix can use DSL environments."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.schema import ReproDSL


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestMatrixDslEnvironments:
    def test_matrix_environments_load(self):
        dsl = load_dsl(FIXTURES / "matrix_environments" / "reproducibility.yml")
        assert len(dsl.environments) == 3

    def test_environments_have_python_versions(self):
        dsl = load_dsl(FIXTURES / "matrix_environments" / "reproducibility.yml")
        versions = []
        for env_name, env in dsl.environments.items():
            if env.python:
                versions.append(env.python)
        assert "3.10" in versions
        assert "3.11" in versions
        assert "3.12" in versions

    def test_environments_have_adapters(self):
        dsl = load_dsl(FIXTURES / "matrix_environments" / "reproducibility.yml")
        for env_name, env in dsl.environments.items():
            assert env.adapter, f"Environment '{env_name}' has no adapter"

    def test_environments_have_install(self):
        dsl = load_dsl(FIXTURES / "matrix_environments" / "reproducibility.yml")
        for env_name, env in dsl.environments.items():
            assert len(env.install) > 0, f"Environment '{env_name}' has no install"

    def test_multilanguage_environments(self):
        dsl = load_dsl(FIXTURES / "valid_multilanguage_pipeline" / "reproducibility.yml")
        adapters = {env.adapter for env in dsl.environments.values()}
        assert "python" in adapters
        assert "r" in adapters

    def test_environments_serializable(self):
        """Environment specs can be serialized for matrix planning."""
        dsl = load_dsl(FIXTURES / "matrix_environments" / "reproducibility.yml")
        d = dsl.to_dict()
        assert "environments" in d
        for env_name, env_data in d["environments"].items():
            assert isinstance(env_data, dict)

    def test_steps_reference_environments(self):
        """Steps reference adapters that correspond to environments."""
        dsl = load_dsl(FIXTURES / "valid_multilanguage_pipeline" / "reproducibility.yml")
        env_names = set(dsl.environments.keys())
        for step_id, step in dsl.steps.items():
            # Step adapter should be either an env name or a well-known adapter
            well_known = {"python", "r", "julia", "node", "rust", "java", "cpp", "make", "snakemake", "nextflow", "shell"}
            assert step.adapter in env_names or step.adapter in well_known, \
                f"Step '{step_id}' adapter '{step.adapter}' not in environments or well-known adapters"
