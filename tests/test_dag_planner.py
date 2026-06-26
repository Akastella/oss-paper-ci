"""Tests for repro_dsl.dag and repro_dsl.planner -- build_dag, topo-sort, parallel groups, critical path."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.dag import build_dag, DAG, DAGNode
from oss_paper_ci.repro_dsl.planner import plan_execution, ExecutionPlan, PlanStep
from oss_paper_ci.repro_dsl.schema import (
    ReproDSL, ProjectSpec, StepSpec, SafetySpec,
)


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestBuildDagValid:
    def test_valid_python_pipeline_dag(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert dag.is_valid is True
        assert len(dag.cycles) == 0
        assert len(dag.missing_deps) == 0

    def test_valid_multistep_pipeline_dag(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert dag.is_valid is True
        assert len(dag.nodes) == 4

    def test_deterministic_topological_order(self):
        """Same input always produces the same topological order."""
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        dag1 = build_dag(dsl)
        dag2 = build_dag(dsl)
        assert dag1.topological_order == dag2.topological_order

    def test_topological_order_respects_dependencies(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        topo = dag.topological_order
        # train must come before evaluate
        assert topo.index("train") < topo.index("evaluate")

    def test_multistep_topological_order(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        topo = dag.topological_order
        # preprocess must come before feature-engineering and augment
        assert topo.index("preprocess") < topo.index("feature-engineering")
        assert topo.index("preprocess") < topo.index("augment")
        # feature-engineering and augment must come before train
        assert topo.index("feature-engineering") < topo.index("train")
        assert topo.index("augment") < topo.index("train")


class TestParallelGroups:
    def test_linear_pipeline_one_step_per_group(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        # train and evaluate are sequential, so 2 groups
        assert len(dag.parallel_groups) == 2

    def test_diamond_dag_has_parallel_steps(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        # preprocess -> {feature-engineering, augment} -> train
        # 3 depth levels, so 3 parallel groups
        assert len(dag.parallel_groups) == 3
        # The second group should have 2 parallel steps
        assert len(dag.parallel_groups[1]) == 2
        group1 = set(dag.parallel_groups[1])
        assert group1 == {"feature-engineering", "augment"}

    def test_parallel_groups_deterministic(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        dag1 = build_dag(dsl)
        dag2 = build_dag(dsl)
        assert dag1.parallel_groups == dag2.parallel_groups

    def test_parallel_groups_stable(self):
        """Groups should be the same across multiple invocations."""
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        groups_list = [build_dag(dsl).parallel_groups for _ in range(5)]
        assert all(g == groups_list[0] for g in groups_list)


class TestCriticalPath:
    def test_critical_path_non_empty(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert len(dag.critical_path) > 0

    def test_critical_path_duration_positive(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert dag.critical_path_duration > 0

    def test_critical_path_is_valid_path(self):
        """Every node in the critical path should be a valid step."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        for step_id in dag.critical_path:
            assert step_id in dag.nodes

    def test_critical_path_deterministic(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        cp1 = build_dag(dsl).critical_path
        cp2 = build_dag(dsl).critical_path
        assert cp1 == cp2

    def test_multistep_critical_path(self):
        """In the diamond DAG, critical path should go through the longest branch."""
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        # All steps have timeout 30 except train (60)
        # preprocess(30) -> feature-engineering(30) -> train(60) = 120
        # preprocess(30) -> augment(30) -> train(60) = 120
        # Both paths have same duration, so critical path length is 3
        assert len(dag.critical_path) == 3
        assert dag.critical_path_duration == 120


class TestDAGNode:
    def test_node_properties(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        train_node = dag.nodes["train"]
        assert train_node.step_id == "train"
        assert train_node.in_degree == 0
        assert train_node.out_degree == 1
        assert train_node.depth == 0  # root node

    def test_node_to_dict(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        d = dag.nodes["train"].to_dict()
        assert "step_id" in d
        assert "command" in d
        assert "needs" in d
        assert "produces" in d


class TestDAGToDict:
    def test_to_dict_structure(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        d = dag.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "topological_order" in d
        assert "parallel_groups" in d
        assert "critical_path" in d
        assert "cycles" in d
        assert "missing_deps" in d


class TestEdges:
    def test_edges_match_dependencies(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        # evaluate depends on train, so edge is (train, evaluate)
        assert ("train", "evaluate") in dag.edges

    def test_multistep_edges(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        assert ("preprocess", "feature-engineering") in dag.edges
        assert ("preprocess", "augment") in dag.edges
        assert ("feature-engineering", "train") in dag.edges
        assert ("augment", "train") in dag.edges


class TestPlanExecution:
    def test_valid_plan_is_executable(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.is_executable is True

    def test_plan_has_steps(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert len(plan.steps) == 2

    def test_plan_steps_in_topological_order(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        step_ids = [s.step_id for s in plan.steps]
        assert step_ids.index("train") < step_ids.index("evaluate")

    def test_plan_all_ready_for_valid_dsl(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert len(plan.ready_steps) == 2
        assert len(plan.blocked_steps) == 0
        assert len(plan.skipped_steps) == 0

    def test_plan_dry_run_default(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.dry_run is True

    def test_plan_total_timeout(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        # train=60 + evaluate=3600 (default) = 3660, but critical path is train->evaluate
        # Actually evaluate doesn't set timeout, so default 3600
        # But from the fixture: train timeout=60, evaluate has no explicit timeout -> 3600
        assert plan.total_timeout > 0

    def test_plan_to_dict(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        d = plan.to_dict()
        assert "steps" in d
        assert "dag_summary" in d
        assert "validation" in d
        assert "safety" in d

    def test_plan_parallel_group_count(self):
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        assert plan.parallel_group_count == 3

    def test_plan_step_to_dict(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        step = plan.steps[0]
        d = step.to_dict()
        assert "step_id" in d
        assert "status" in d
        assert "parallel_group" in d
