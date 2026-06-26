"""Execution planner for Reproducibility DSL v1.

Creates ordered execution plans from a DAG, with dependency resolution,
parallel group identification, and dry-run/execute modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .schema import ReproDSL
from .dag import DAG, DAGNode, build_dag
from .validator import validate_dsl, ValidationResult
from .safety import check_dsl_safety, SafetyReport


@dataclass
class PlanStep:
    """A single step in an execution plan."""

    step_id: str
    command: str
    needs: list[str]
    produces: list[str]
    timeout: int
    depth: int
    parallel_group: int
    status: str  # "ready", "blocked", "skipped", "pending"
    skip_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "step_id": self.step_id,
            "command": self.command,
            "needs": sorted(self.needs),
            "produces": sorted(self.produces),
            "timeout": self.timeout,
            "depth": self.depth,
            "parallel_group": self.parallel_group,
            "status": self.status,
        }
        if self.skip_reason:
            d["skip_reason"] = self.skip_reason
        return d


@dataclass
class ExecutionPlan:
    """Complete execution plan for a DSL specification."""

    steps: list[PlanStep]
    dag: DAG
    validation: ValidationResult
    safety: SafetyReport
    total_timeout: int
    parallel_group_count: int
    dry_run: bool = True
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "dag_summary": {
                "topological_order": self.dag.topological_order,
                "parallel_groups": self.dag.parallel_groups,
                "critical_path": self.dag.critical_path,
                "critical_path_duration": self.dag.critical_path_duration,
                "cycles": self.dag.cycles,
                "missing_deps": {
                    k: sorted(v)
                    for k, v in sorted(self.dag.missing_deps.items())
                },
            },
            "validation": self.validation.to_dict(),
            "safety": self.safety.to_dict(),
            "total_timeout": self.total_timeout,
            "parallel_group_count": self.parallel_group_count,
            "dry_run": self.dry_run,
            "warnings": sorted(self.warnings),
        }

    @property
    def is_executable(self) -> bool:
        """True when validation passes, DAG is valid, and no safety blocks exist."""
        return (
            self.validation.is_valid
            and self.dag.is_valid
            and not self.safety.has_blocks
        )

    @property
    def ready_steps(self) -> list[PlanStep]:
        """Steps whose dependencies are all satisfied."""
        return [s for s in self.steps if s.status == "ready"]

    @property
    def blocked_steps(self) -> list[PlanStep]:
        """Steps that are blocked (e.g., in a cycle or missing dependency)."""
        return [s for s in self.steps if s.status == "blocked"]

    @property
    def skipped_steps(self) -> list[PlanStep]:
        """Steps skipped because one of their dependencies is blocked."""
        return [s for s in self.steps if s.status == "skipped"]


def plan_execution(dsl: ReproDSL, dry_run: bool = True) -> ExecutionPlan:
    """Create an execution plan from a DSL specification.

    Steps:
    1. Validate the DSL
    2. Build the DAG
    3. Check safety
    4. Propagate blocked/skipped status (if cycle or missing dep, mark as blocked)
    5. Create PlanSteps in topological order
    6. Assign parallel groups
    7. Compute total timeout

    Args:
        dsl: The DSL specification
        dry_run: If True, plan only (no execution)

    Returns:
        ExecutionPlan with all steps ordered and annotated
    """
    # 1. Validate
    validation = validate_dsl(dsl)

    # 2. Build DAG
    dag = build_dag(dsl)

    # 3. Safety check
    safety = check_dsl_safety(dsl)

    # 4. Determine which steps are blocked/skipped
    blocked_ids: set[str] = set()
    skipped_ids: set[str] = set()

    # Steps in cycles are blocked
    cycle_nodes: set[str] = set()
    for cycle in dag.cycles:
        cycle_nodes.update(cycle)
    blocked_ids.update(cycle_nodes)

    # Steps with missing deps are blocked
    blocked_ids.update(dag.missing_deps.keys())

    # Safety-blocked steps
    safety_blocked = set(safety.blocked_commands)
    blocked_ids.update(safety_blocked)

    # Steps that depend on blocked steps are skipped
    for step_id in dag.topological_order:
        if step_id in blocked_ids:
            continue
        step = dsl.steps.get(step_id)
        if step:
            for dep in step.needs:
                if dep in blocked_ids:
                    skipped_ids.add(step_id)
                    break

    # 5. Create PlanSteps in topological order
    steps: list[PlanStep] = []
    for step_id in dag.topological_order:
        node = dag.nodes[step_id]
        step = dsl.steps.get(step_id)
        if not step:
            continue

        if step_id in blocked_ids:
            if step_id in cycle_nodes:
                reason = "in cycle"
            elif step_id in dag.missing_deps:
                reason = "missing dependency"
            else:
                reason = "safety block"
            status = "blocked"
        elif step_id in skipped_ids:
            status = "skipped"
            reason = "dependency blocked"
        else:
            status = "ready"
            reason = ""

        steps.append(
            PlanStep(
                step_id=step_id,
                command=node.command,
                needs=list(node.needs),
                produces=list(node.produces),
                timeout=node.timeout,
                depth=node.depth,
                parallel_group=node.level,
                status=status,
                skip_reason=reason,
            )
        )

    # 6. Parallel group count
    parallel_group_count = len(dag.parallel_groups) if dag.parallel_groups else 1

    # 7. Total timeout (sum of all steps on the critical path)
    total_timeout = sum(
        dsl.steps[s].timeout for s in dag.critical_path if s in dsl.steps
    )

    # Collect warnings
    warnings = list(dag.warnings)
    if not validation.is_valid:
        warnings.append(f"DSL has {len(validation.errors)} validation error(s)")
    if safety.has_warnings:
        warnings.append(f"Safety: {len(safety.findings)} finding(s)")

    return ExecutionPlan(
        steps=steps,
        dag=dag,
        validation=validation,
        safety=safety,
        total_timeout=total_timeout,
        parallel_group_count=parallel_group_count,
        dry_run=dry_run,
        warnings=warnings,
    )
