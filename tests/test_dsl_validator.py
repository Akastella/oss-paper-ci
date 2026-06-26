"""Tests for repro_dsl.validator -- validate_dsl with valid and invalid DSLs."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.validator import validate_dsl, ValidationResult, ValidationFinding
from oss_paper_ci.repro_dsl.schema import (
    ReproDSL, ProjectSpec, StepSpec, DatasetSpec, SafetySpec,
    EnvironmentSpec, MetricSpec, ExpectedSpec, ArtifactSpec,
)


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


def _make_dsl(**overrides) -> ReproDSL:
    """Helper to create a minimal valid DSL with optional overrides."""
    defaults = dict(
        project=ProjectSpec(name="test"),
        steps={"s1": StepSpec(id="s1", command="echo hello")},
        safety=SafetySpec(),
    )
    defaults.update(overrides)
    return ReproDSL(**defaults)


class TestValidateValidDsl:
    def test_valid_python_pipeline(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = validate_dsl(dsl)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_valid_multistep_pipeline(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        result = validate_dsl(dsl)
        assert result.is_valid is True

    def test_valid_multilanguage_pipeline(self):
        dsl = load_dsl(FIXTURES / "valid_multilanguage_pipeline" / "reproducibility.yml")
        result = validate_dsl(dsl)
        assert result.is_valid is True

    def test_matrix_environments(self):
        dsl = load_dsl(FIXTURES / "matrix_environments" / "reproducibility.yml")
        result = validate_dsl(dsl)
        assert result.is_valid is True

    def test_optional_artifacts(self):
        dsl = load_dsl(FIXTURES / "optional_artifacts" / "reproducibility.yml")
        result = validate_dsl(dsl)
        assert result.is_valid is True

    def test_minimal_valid_dsl(self):
        dsl = _make_dsl()
        result = validate_dsl(dsl)
        assert result.is_valid is True


class TestValidateInvalidDsl:
    def test_missing_dependency_detected(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        result = validate_dsl(dsl)
        assert result.is_valid is False
        dep_errors = [f for f in result.errors if f.category == "dependency"]
        assert len(dep_errors) > 0
        assert any("nonexistent-step" in f.message for f in dep_errors)

    def test_wrong_version_detected(self):
        dsl = _make_dsl()
        # Manually set wrong version (frozen, so create new)
        dsl_wrong = ReproDSL(
            version=2,
            project=ProjectSpec(name="test"),
            steps={"s1": StepSpec(id="s1", command="echo")},
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl_wrong)
        assert result.is_valid is False
        version_errors = [f for f in result.errors if "version" in f.message.lower()]
        assert len(version_errors) > 0

    def test_empty_command_detected(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={"s1": StepSpec(id="s1", command="")},
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl)
        assert result.is_valid is False
        cmd_errors = [f for f in result.errors if "command" in f.message.lower()]
        assert len(cmd_errors) > 0

    def test_self_dependency_detected(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={"s1": StepSpec(id="s1", command="echo", needs=["s1"])},
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl)
        assert result.is_valid is False
        self_dep = [f for f in result.errors if "itself" in f.message.lower()]
        assert len(self_dep) > 0

    def test_invalid_timeout_detected(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={"s1": StepSpec(id="s1", command="echo", timeout=-1)},
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl)
        assert result.is_valid is False
        timeout_errors = [f for f in result.errors if "timeout" in f.message.lower()]
        assert len(timeout_errors) > 0

    def test_metric_min_greater_than_max_detected(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={"s1": StepSpec(id="s1", command="echo")},
            expected=ExpectedSpec(metrics={"loss": MetricSpec(key="loss", min=1.0, max=0.0)}),
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl)
        assert result.is_valid is False
        metric_errors = [f for f in result.errors if f.category == "metric"]
        assert len(metric_errors) > 0


class TestValidateWarnings:
    def test_missing_project_name_warns(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="unnamed"),
            steps={"s1": StepSpec(id="s1", command="echo")},
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl)
        name_warnings = [f for f in result.warnings if "project name" in f.message.lower()]
        assert len(name_warnings) > 0

    def test_empty_steps_warns(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={},
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl)
        empty_warnings = [f for f in result.warnings if "no steps" in f.message.lower()]
        assert len(empty_warnings) > 0

    def test_duplicate_needs_warns(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={
                "s1": StepSpec(id="s1", command="echo"),
                "s2": StepSpec(id="s2", command="echo", needs=["s1", "s1"]),
            },
            safety=SafetySpec(),
        )
        result = validate_dsl(dsl)
        dup_warnings = [f for f in result.warnings if "duplicate" in f.message.lower()]
        assert len(dup_warnings) > 0


class TestValidationResult:
    def test_errors_property(self):
        findings = [
            ValidationFinding(severity="error", category="schema", message="err"),
            ValidationFinding(severity="warning", category="path", message="warn"),
        ]
        result = ValidationResult(findings=findings, is_valid=False, checked_fields=2)
        assert len(result.errors) == 1
        assert result.errors[0].severity == "error"

    def test_warnings_property(self):
        findings = [
            ValidationFinding(severity="error", category="schema", message="err"),
            ValidationFinding(severity="warning", category="path", message="warn"),
        ]
        result = ValidationResult(findings=findings, is_valid=False, checked_fields=2)
        assert len(result.warnings) == 1
        assert result.warnings[0].severity == "warning"

    def test_to_dict(self):
        result = ValidationResult(findings=[], is_valid=True, checked_fields=5)
        d = result.to_dict()
        assert d["is_valid"] is True
        assert d["checked_fields"] == 5
        assert d["findings"] == []


class TestValidationFinding:
    def test_to_dict(self):
        f = ValidationFinding(severity="error", category="dependency", message="missing", field_path="steps.x.needs")
        d = f.to_dict()
        assert d["severity"] == "error"
        assert d["category"] == "dependency"
        assert d["field_path"] == "steps.x.needs"

    def test_to_dict_no_field_path(self):
        f = ValidationFinding(severity="warning", category="schema", message="msg")
        d = f.to_dict()
        assert "field_path" not in d
