"""Reproduction plan generation.

Reads reproducibility.yml and produces a structured execution plan
without executing any code.  The plan describes what would happen if
the user ran `reproduce run --execute`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci.repro_schema import (
    ArtifactSpec,
    CommandSpec,
    OrchestratorContract,
    load_orchestrator_contract,
    validate_orchestrator_schema,
)


@dataclass
class PlanStep:
    """A single step in the reproduction plan."""

    command_id: str = ""
    run: str = ""
    timeout_seconds: int = 60
    depends_on: list[str] = field(default_factory=list)
    expected_artifacts: list[str] = field(default_factory=list)
    danger_check: str = "safe"  # safe | blocked

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "run": self.run,
            "timeout_seconds": self.timeout_seconds,
            "depends_on": self.depends_on,
            "expected_artifacts": self.expected_artifacts,
            "danger_check": self.danger_check,
        }


@dataclass
class ReproductionPlan:
    """Complete reproduction plan."""

    repo_path: str = ""
    contract_path: str = ""
    schema_version: str = ""
    project_name: str = ""
    project_type: str = ""
    environment: dict[str, Any] = field(default_factory=dict)
    steps: list[PlanStep] = field(default_factory=list)
    artifacts: list[dict[str, str]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)
    safety: dict[str, Any] = field(default_factory=dict)
    total_timeout: int = 0
    warnings: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_path": self.repo_path,
            "contract_path": self.contract_path,
            "schema_version": self.schema_version,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "environment": self.environment,
            "steps": [s.to_dict() for s in self.steps],
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "safety": self.safety,
            "total_timeout": self.total_timeout,
            "warnings": self.warnings,
            "generated_at": self.generated_at,
        }


def build_plan(
    repo_path: str,
    contract_path: str | None = None,
) -> ReproductionPlan:
    """Build a reproduction plan from reproducibility.yml.

    This function NEVER executes any code. It only reads the contract
    and produces a structured plan.

    Args:
        repo_path: Path to the repository root.
        contract_path: Explicit path to reproducibility.yml. If None,
            searches for it in the repo root.

    Returns:
        ReproductionPlan describing what would be executed.
    """
    root = Path(repo_path).resolve()
    plan = ReproductionPlan(
        repo_path=str(root),
        generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    # Find contract
    if contract_path:
        contract_file = Path(contract_path)
    else:
        from oss_paper_ci.contract import find_contract
        found = find_contract(str(root))
        if not found:
            plan.warnings.append(
                "No reproducibility.yml found. "
                "Run 'oss-paper-ci init --contract' to create one."
            )
            return plan
        contract_file = Path(found)

    plan.contract_path = str(contract_file)

    # Load contract
    try:
        contract = load_orchestrator_contract(str(contract_file))
    except Exception as exc:
        plan.warnings.append(f"Failed to load contract: {exc}")
        return plan

    plan.schema_version = contract.schema_version
    plan.project_name = contract.project_name
    plan.project_type = contract.project_type
    plan.environment = contract.environment

    # Validate schema
    import yaml
    try:
        with open(contract_file, encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
        schema_warnings = validate_orchestrator_schema(raw_data)
        plan.warnings.extend(schema_warnings)
    except Exception:
        pass

    # Build steps from commands
    from oss_paper_ci.command_safety import is_dangerous_command

    total_timeout = 0
    for cmd_spec in contract.commands:
        step = PlanStep(
            command_id=cmd_spec.id,
            run=cmd_spec.run,
            timeout_seconds=cmd_spec.timeout_seconds,
            depends_on=cmd_spec.depends_on,
            expected_artifacts=cmd_spec.expected_artifacts,
        )
        if is_dangerous_command(cmd_spec.run):
            step.danger_check = "blocked"
            plan.warnings.append(
                f"Command '{cmd_spec.id}' matches a dangerous pattern and "
                "would be blocked during execution."
            )
        total_timeout += cmd_spec.timeout_seconds
        plan.steps.append(step)

    # If no commands defined, try legacy experiments
    if not plan.steps and contract.experiments:
        for exp in contract.experiments:
            if isinstance(exp, dict) and exp.get("command"):
                step = PlanStep(
                    command_id=exp.get("id", ""),
                    run=exp.get("command", ""),
                    timeout_seconds=exp.get("timeout_seconds", 60),
                    expected_artifacts=exp.get("expected_outputs", []),
                )
                if is_dangerous_command(step.run):
                    step.danger_check = "blocked"
                total_timeout += step.timeout_seconds
                plan.steps.append(step)

    plan.total_timeout = total_timeout

    # Artifacts
    for art in contract.artifacts:
        plan.artifacts.append(art.to_dict())

    # Metrics
    for met in contract.metrics:
        plan.metrics.append(met.to_dict())

    # Safety
    plan.safety = contract.safety.to_dict()

    # Dependency validation
    step_ids = {s.command_id for s in plan.steps}
    for step in plan.steps:
        for dep in step.depends_on:
            if dep not in step_ids:
                plan.warnings.append(
                    f"Command '{step.command_id}' depends on '{dep}' "
                    "which is not defined."
                )

    return plan


def format_plan_markdown(plan: ReproductionPlan) -> str:
    """Format a reproduction plan as Markdown."""
    lines = [
        "# Reproduction Plan",
        "",
        f"**Project:** {plan.project_name or '(unnamed)'}",
        f"**Type:** {plan.project_type}",
        f"**Schema:** {plan.schema_version}",
        f"**Generated:** {plan.generated_at}",
        "",
    ]

    # Environment
    if plan.environment:
        lines.append("## Environment")
        lines.append("")
        env_type = plan.environment.get("type", "unknown")
        env_python = plan.environment.get("python", "")
        env_file = plan.environment.get("file", "")
        lines.append(f"- **Type:** {env_type}")
        if env_python:
            lines.append(f"- **Python:** {env_python}")
        if env_file:
            lines.append(f"- **File:** {env_file}")
        lines.append("")

    # Safety
    if plan.safety:
        lines.append("## Safety Constraints")
        lines.append("")
        lines.append(f"- **Network:** {'allowed' if plan.safety.get('network') else 'blocked'}")
        lines.append(f"- **Shell:** {'allowed' if plan.safety.get('allow_shell') else 'blocked'}")
        lines.append(f"- **Max runtime:** {plan.safety.get('max_runtime_seconds', 300)}s")
        lines.append(f"- **Max artifact size:** {plan.safety.get('max_artifact_mb', 20)} MB")
        lines.append("")

    # Steps
    if plan.steps:
        lines.append("## Execution Steps")
        lines.append("")
        lines.append("| # | ID | Command | Timeout | Dependencies | Artifacts | Status |")
        lines.append("|---|-----|---------|---------|--------------|-----------|--------|")
        for i, step in enumerate(plan.steps, 1):
            deps = ", ".join(step.depends_on) if step.depends_on else "—"
            arts = ", ".join(step.expected_artifacts) if step.expected_artifacts else "—"
            status = "🚫 blocked" if step.danger_check == "blocked" else "✅ safe"
            lines.append(
                f"| {i} | `{step.command_id}` | `{step.run}` | "
                f"{step.timeout_seconds}s | {deps} | {arts} | {status} |"
            )
        lines.append("")
        lines.append(f"**Total timeout:** {plan.total_timeout}s")
        lines.append("")

    # Artifacts
    if plan.artifacts:
        lines.append("## Expected Artifacts")
        lines.append("")
        lines.append("| Path | Type |")
        lines.append("|------|------|")
        for art in plan.artifacts:
            lines.append(f"| `{art.get('path', '')}` | {art.get('type', 'file')} |")
        lines.append("")

    # Metrics
    if plan.metrics:
        lines.append("## Expected Metrics")
        lines.append("")
        lines.append("| File | Key | Min | Max |")
        lines.append("|------|-----|-----|-----|")
        for m in plan.metrics:
            min_val = m.get("expected_min", "—")
            max_val = m.get("expected_max", "—")
            lines.append(f"| `{m.get('file', '')}` | `{m.get('key', '')}` | {min_val} | {max_val} |")
        lines.append("")

    # Warnings
    if plan.warnings:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for w in plan.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Disclaimer
    lines.append("---")
    lines.append("")
    lines.append(
        "*This plan describes declared reproduction steps. "
        "It does not execute code or verify scientific correctness.*"
    )

    return "\n".join(lines)


def format_plan_json(plan: ReproductionPlan) -> str:
    """Format a reproduction plan as JSON."""
    import json
    return json.dumps(plan.to_dict(), indent=2, ensure_ascii=False)
