"""Migration from legacy reproducibility.yml formats to DSL v1.

Converts v0.2 (orchestrator schema) and v0.3 (contract schema) to v1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .schema import (
    ReproDSL, ProjectSpec, EnvironmentSpec, DatasetSpec,
    StepSpec, ArtifactSpec, MetricSpec, MetricKeySpec,
    ExpectedSpec, SafetySpec,
)


@dataclass
class MigrationReport:
    """Report of migration from legacy format to v1."""
    source_version: str
    target_version: int = 1
    warnings: list[str] = field(default_factory=list)
    steps_converted: int = 0
    datasets_converted: int = 0
    metrics_converted: int = 0
    artifacts_converted: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_version": self.source_version,
            "target_version": self.target_version,
            "warnings": sorted(self.warnings),
            "steps_converted": self.steps_converted,
            "datasets_converted": self.datasets_converted,
            "metrics_converted": self.metrics_converted,
            "artifacts_converted": self.artifacts_converted,
        }


def migrate_legacy(data: dict[str, Any], version: str) -> ReproDSL:
    """Migrate a legacy reproducibility.yml to DSL v1.

    Args:
        data: Raw YAML dict
        version: "v0.2" or "v0.3"

    Returns:
        ReproDSL v1 specification
    """
    if version == "v0.2":
        return _migrate_v02(data)
    elif version == "v0.3":
        return _migrate_v03(data)
    else:
        raise ValueError(f"Unsupported legacy version: {version}")


def migrate_legacy_with_report(data: dict[str, Any], version: str) -> tuple[ReproDSL, MigrationReport]:
    """Migrate and return both the DSL and a migration report."""
    report = MigrationReport(source_version=version)

    if version == "v0.2":
        dsl = _migrate_v02(data, report)
    elif version == "v0.3":
        dsl = _migrate_v03(data, report)
    else:
        raise ValueError(f"Unsupported legacy version: {version}")

    return dsl, report


def _migrate_v02(data: dict[str, Any], report: MigrationReport | None = None) -> ReproDSL:
    """Migrate v0.2 orchestrator schema to v1.

    v0.2 has: schema_version, commands[{id, run, timeout_seconds, depends_on, expected_artifacts}],
              artifacts[{path, type}], metrics[{file, key, expected_min, expected_max}],
              safety{network, allow_shell, max_runtime_seconds, max_artifact_mb}
    """
    # Project
    project = ProjectSpec(name=data.get("project_name", "migrated"))

    # Steps from commands
    steps = {}
    for cmd in data.get("commands", []):
        step_id = cmd.get("id", f"step_{len(steps)}")
        metrics = []
        for art in cmd.get("expected_artifacts", []):
            # Can't know metric keys from artifacts alone
            pass

        steps[step_id] = StepSpec(
            id=step_id,
            command=cmd.get("run", ""),
            needs=list(cmd.get("depends_on", [])),
            produces=list(cmd.get("expected_artifacts", [])),
            timeout=int(cmd.get("timeout_seconds", 3600)),
        )
        if report:
            report.steps_converted += 1

    # Artifacts
    artifacts = []
    for art in data.get("artifacts", []):
        if isinstance(art, dict):
            artifacts.append(ArtifactSpec(
                path=art.get("path", ""),
                type=art.get("type", "file"),
            ))
        if report:
            report.artifacts_converted += 1

    # Metrics -> expected
    expected_metrics = {}
    for m in data.get("metrics", []):
        key = m.get("key", "")
        if key:
            expected_metrics[key] = MetricSpec(
                key=key,
                min=m.get("expected_min"),
                max=m.get("expected_max"),
            )
            if report:
                report.metrics_converted += 1

    # Safety
    safety_data = data.get("safety", {})
    safety = SafetySpec(
        network=safety_data.get("network", False),
        allow_install=False,  # v0.2 doesn't have allow_install
    )

    if report and safety_data.get("allow_shell"):
        report.warnings.append("v0.2 allow_shell=true not directly mapped; review safety settings")

    return ReproDSL(
        version=1,
        project=project,
        steps=steps,
        artifacts=artifacts,
        expected=ExpectedSpec(metrics=expected_metrics),
        safety=safety,
    )


def _migrate_v03(data: dict[str, Any], report: MigrationReport | None = None) -> ReproDSL:
    """Migrate v0.3 contract schema to v1.

    v0.3 has: version, project_name, project_type, paper{}, environment{},
              data[{id, path, availability, source, license}],
              experiments[{id, description, command, timeout_seconds, safe_to_run, expected_outputs}],
              figures[{id, path, generated_by, referenced_by}],
              results[{id, path, generated_by}],
              ci{smoke_experiment, min_score, fail_on_regression}
    """
    # Project
    project = ProjectSpec(
        name=data.get("project_name", "migrated"),
        description=f"Type: {data.get('project_type', 'unknown')}",
    )

    # Environment
    env_data = data.get("environment", {})
    environments = {}
    if env_data:
        env_name = env_data.get("type", "default")
        environments[env_name] = EnvironmentSpec(
            adapter=env_data.get("type", ""),
            python=env_data.get("python", ""),
            install=[env_data["file"]] if env_data.get("file") else [],
        )

    # Datasets
    datasets = {}
    for d in data.get("data", []):
        ds_id = d.get("id", f"dataset_{len(datasets)}")
        datasets[ds_id] = DatasetSpec(
            path=d.get("path", ""),
            required=d.get("availability") not in ("not-required", "synthetic"),
            description=d.get("source", ""),
        )
        if report:
            report.datasets_converted += 1

    # Steps from experiments
    steps = {}
    for exp in data.get("experiments", []):
        step_id = exp.get("id", f"step_{len(steps)}")
        steps[step_id] = StepSpec(
            id=step_id,
            command=exp.get("command", ""),
            description=exp.get("description", ""),
            produces=list(exp.get("expected_outputs", [])),
            timeout=int(exp.get("timeout_seconds", 3600)),
        )
        if report:
            report.steps_converted += 1

    # Artifacts from figures and results
    artifacts = []
    for fig in data.get("figures", []):
        artifacts.append(ArtifactSpec(path=fig.get("path", ""), type="figure"))
        if report:
            report.artifacts_converted += 1
    for res in data.get("results", []):
        artifacts.append(ArtifactSpec(path=res.get("path", ""), type="metrics"))
        if report:
            report.artifacts_converted += 1

    # Safety (v0.3 doesn't have explicit safety, use safe_to_run from experiments)
    has_unsafe = any(not exp.get("safe_to_run", True) for exp in data.get("experiments", []))
    if has_unsafe and report:
        report.warnings.append("Some experiments marked safe_to_run=false; review safety settings")

    safety = SafetySpec(network=False, allow_install=False)

    return ReproDSL(
        version=1,
        project=project,
        environments=environments,
        datasets=datasets,
        steps=steps,
        artifacts=artifacts,
        safety=safety,
    )
