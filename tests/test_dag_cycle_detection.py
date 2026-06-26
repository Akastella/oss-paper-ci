"""Tests for build_dag with cyclic dependencies."""
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


class TestCyclicDependencyDetection:
    def test_cycle_detected(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert len(dag.cycles) > 0

    def test_dag_is_not_valid(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert dag.is_valid is False

    def test_cycle_involves_all_three_steps(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        # A->B->C->A cycle: all 3 steps are in cycles
        cycle_nodes = set()
        for cycle in dag.cycles:
            cycle_nodes.update(cycle)
        assert "step-a" in cycle_nodes
        assert "step-b" in cycle_nodes
        assert "step-c" in cycle_nodes

    def test_topological_order_excludes_cycle_nodes(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        # With a full cycle, no nodes can be topologically sorted
        assert len(dag.topological_order) == 0

    def test_critical_path_empty_for_full_cycle(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert dag.critical_path == []
        assert dag.critical_path_duration == 0

    def test_cycle_warnings_present(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert len(dag.warnings) > 0
        assert any("cycle" in w.lower() for w in dag.warnings)

    def test_plan_has_no_executable_steps_for_full_cycle(self):
        """With a full cycle, topological order is empty, so no PlanSteps are created."""
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        plan = plan_execution(dsl)
        # Full cycle means topological_order is empty, so plan.steps is empty
        assert len(plan.steps) == 0
        assert len(plan.ready_steps) == 0
        # The cycle is still detected in the DAG
        assert len(plan.dag.cycles) > 0

    def test_plan_not_executable_with_cycle(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.is_executable is False


class TestSelfLoopDetection:
    def test_self_loop_detected(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="self-loop"),
            steps={"s1": StepSpec(id="s1", command="echo", needs=["s1"])},
            safety=SafetySpec(),
        )
        dag = build_dag(dsl)
        assert len(dag.cycles) > 0
        assert dag.is_valid is False


class TestPartialCycle:
    def test_partial_cycle_with_acyclic_nodes(self):
        """A cycle among some nodes, with other nodes depending on acyclic ones."""
        dsl = ReproDSL(
            project=ProjectSpec(name="partial-cycle"),
            steps={
                "a": StepSpec(id="a", command="echo a", needs=["c"]),
                "b": StepSpec(id="b", command="echo b", needs=["a"]),
                "c": StepSpec(id="c", command="echo c", needs=["b"]),
                "d": StepSpec(id="d", command="echo d"),  # independent, no cycle
            },
            safety=SafetySpec(),
        )
        dag = build_dag(dsl)
        assert len(dag.cycles) > 0
        # d should still be in topological order
        assert "d" in dag.topological_order
        # a, b, c should be in cycle
        cycle_nodes = set()
        for cycle in dag.cycles:
            cycle_nodes.update(cycle)
        assert cycle_nodes == {"a", "b", "c"}
