"""Tests that the reproduce plan can use DSL when available."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.planner import plan_execution
from oss_paper_ci.repro_dsl.dag import build_dag


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestReproducePlanUsesDsl:
    def test_dsl_loads_for_reproduction(self):
        """A valid DSL file can be loaded and used to create a reproduction plan."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.is_executable is True

    def test_plan_contains_execution_steps(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        step_ids = [s.step_id for s in plan.steps]
        assert "train" in step_ids
        assert "evaluate" in step_ids

    def test_plan_commands_match_dsl(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        for plan_step in plan.steps:
            dsl_step = dsl.steps[plan_step.step_id]
            assert plan_step.command == dsl_step.command

    def test_plan_dependencies_match_dsl(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        for plan_step in plan.steps:
            dsl_step = dsl.steps[plan_step.step_id]
            assert set(plan_step.needs) == set(dsl_step.needs)

    def test_multistep_plan_execution_order(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        step_ids = [s.step_id for s in plan.steps]
        # preprocess must come before its dependents
        assert step_ids.index("preprocess") < step_ids.index("feature-engineering")
        assert step_ids.index("preprocess") < step_ids.index("augment")
        assert step_ids.index("feature-engineering") < step_ids.index("train")
        assert step_ids.index("augment") < step_ids.index("train")

    def test_dag_available_from_plan(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.dag is not None
        assert plan.dag.is_valid is True

    def test_validation_available_from_plan(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.validation is not None
        assert plan.validation.is_valid is True

    def test_safety_available_from_plan(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.safety is not None
        assert plan.safety.safety_level == "safe"
