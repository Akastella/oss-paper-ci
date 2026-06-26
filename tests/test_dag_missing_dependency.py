"""Tests for build_dag with missing dependencies."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.dag import build_dag
from oss_paper_ci.repro_dsl.planner import plan_execution
from oss_paper_ci.repro_dsl.schema import (
    ReproDSL, ProjectSpec, StepSpec, SafetySpec,
)


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestMissingDependencyDetection:
    def test_missing_dep_detected(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert len(dag.missing_deps) > 0

    def test_dag_is_not_valid(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert dag.is_valid is False

    def test_nonexistent_step_in_missing_deps(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert "evaluate" in dag.missing_deps
        assert "nonexistent-step" in dag.missing_deps["evaluate"]

    def test_warnings_present(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert any("non-existent" in w.lower() or "nonexistent" in w.lower() for w in dag.warnings)

    def test_valid_steps_still_in_topological_order(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        # train has no missing deps and should be in topo order
        assert "train" in dag.topological_order

    def test_plan_marks_missing_dep_step_blocked(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        plan = plan_execution(dsl)
        blocked_ids = {s.step_id for s in plan.blocked_steps}
        assert "evaluate" in blocked_ids

    def test_plan_not_executable_with_missing_deps(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.is_executable is False


class TestMissingDependencySynthetic:
    def test_single_missing_dep(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={
                "a": StepSpec(id="a", command="echo a"),
                "b": StepSpec(id="b", command="echo b", needs=["a", "nonexistent"]),
            },
            safety=SafetySpec(),
        )
        dag = build_dag(dsl)
        assert "b" in dag.missing_deps
        assert "nonexistent" in dag.missing_deps["b"]
        assert dag.is_valid is False

    def test_multiple_missing_deps(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={
                "a": StepSpec(id="a", command="echo a", needs=["x", "y"]),
            },
            safety=SafetySpec(),
        )
        dag = build_dag(dsl)
        assert "a" in dag.missing_deps
        assert set(dag.missing_deps["a"]) == {"x", "y"}

    def test_all_deps_missing(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="test"),
            steps={
                "a": StepSpec(id="a", command="echo a", needs=["x"]),
                "b": StepSpec(id="b", command="echo b", needs=["y"]),
            },
            safety=SafetySpec(),
        )
        dag = build_dag(dsl)
        assert len(dag.missing_deps) == 2
