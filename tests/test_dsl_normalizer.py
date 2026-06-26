"""Tests for repro_dsl.normalizer -- normalize_dsl, normalize_dsl_json."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.normalizer import normalize_dsl, normalize_dsl_json
from oss_paper_ci.repro_dsl.schema import (
    ReproDSL, ProjectSpec, StepSpec, DatasetSpec, SafetySpec,
    EnvironmentSpec, ArtifactSpec,
)


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestNormalizeDsl:
    def test_returns_dict(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = normalize_dsl(dsl)
        assert isinstance(result, dict)

    def test_has_version(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = normalize_dsl(dsl)
        assert result["version"] == 1

    def test_deterministic(self):
        """Same DSL always produces the same normalized output."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        r1 = normalize_dsl(dsl)
        r2 = normalize_dsl(dsl)
        assert r1 == r2

    def test_keys_present(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = normalize_dsl(dsl)
        assert "version" in result
        assert "project" in result
        assert "steps" in result
        assert "safety" in result

    def test_step_keys_sorted(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="p"),
            steps={
                "z_step": StepSpec(id="z_step", command="echo z"),
                "a_step": StepSpec(id="a_step", command="echo a"),
                "m_step": StepSpec(id="m_step", command="echo m"),
            },
            safety=SafetySpec(),
        )
        result = normalize_dsl(dsl)
        step_keys = list(result["steps"].keys())
        assert step_keys == ["a_step", "m_step", "z_step"]

    def test_clean_paths_removes_dot_slash(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="p"),
            datasets={"d": DatasetSpec(path="./data/")},
            artifacts=[ArtifactSpec(path="./figures/")],
            safety=SafetySpec(),
        )
        result = normalize_dsl(dsl)
        # _clean_paths cleans "path" keys in dicts
        assert result["datasets"]["d"]["path"] == "data/"
        assert result["artifacts"][0]["path"] == "figures/"

    def test_clean_paths_preserves_non_dot_slash(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="p"),
            datasets={"d": DatasetSpec(path="data/input.csv")},
            safety=SafetySpec(),
        )
        result = normalize_dsl(dsl)
        assert result["datasets"]["d"]["path"] == "data/input.csv"


class TestNormalizeDslJson:
    def test_returns_string(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = normalize_dsl_json(dsl)
        assert isinstance(result, str)

    def test_is_valid_json(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = normalize_dsl_json(dsl)
        parsed = json.loads(result)
        assert parsed["version"] == 1

    def test_ends_with_newline(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = normalize_dsl_json(dsl)
        assert result.endswith("\n")

    def test_deterministic(self):
        """Same DSL always produces the same JSON string."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        j1 = normalize_dsl_json(dsl)
        j2 = normalize_dsl_json(dsl)
        assert j1 == j2

    def test_indent_parameter(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        j2 = normalize_dsl_json(dsl, indent=2)
        j4 = normalize_dsl_json(dsl, indent=4)
        # Both valid JSON, but different indentation
        assert json.loads(j2) == json.loads(j4)
        assert j2 != j4

    def test_multistep_pipeline_json(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        result = normalize_dsl_json(dsl)
        parsed = json.loads(result)
        assert len(parsed["steps"]) == 4
