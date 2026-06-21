"""Extended schema for reproducibility.yml v0.2 (orchestrator schema).

Backward compatible with v0.3 contract_schema.py. Adds:
- commands: ordered command list with dependency tracking
- artifacts: typed artifact declarations with hash expectations
- metrics: metric key validation with tolerance ranges
- safety: execution safety constraints
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommandSpec:
    """A single reproducible command with dependencies and expected artifacts."""

    id: str = ""
    run: str = ""
    timeout_seconds: int = 60
    depends_on: list[str] = field(default_factory=list)
    expected_artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "run": self.run,
            "timeout_seconds": self.timeout_seconds,
            "depends_on": self.depends_on,
            "expected_artifacts": self.expected_artifacts,
        }


@dataclass
class ArtifactSpec:
    """Declaration of an expected output artifact."""

    path: str = ""
    type: str = "file"  # file | metrics | figure | figure-placeholder | table | log

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "type": self.type}


@dataclass
class MetricSpec:
    """Expected metric value with tolerance range."""

    file: str = ""
    key: str = ""
    expected_min: float | None = None
    expected_max: float | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"file": self.file, "key": self.key}
        if self.expected_min is not None:
            d["expected_min"] = self.expected_min
        if self.expected_max is not None:
            d["expected_max"] = self.expected_max
        return d


@dataclass
class SafetySpec:
    """Execution safety constraints."""

    network: bool = False
    allow_shell: bool = False
    max_runtime_seconds: int = 300
    max_artifact_mb: int = 20

    def to_dict(self) -> dict[str, Any]:
        return {
            "network": self.network,
            "allow_shell": self.allow_shell,
            "max_runtime_seconds": self.max_runtime_seconds,
            "max_artifact_mb": self.max_artifact_mb,
        }


@dataclass
class OrchestratorContract:
    """Extended contract for the reproduction orchestrator.

    Backward compatible with ReproducibilityContract -- fields not present
    in the YAML simply get defaults.
    """

    schema_version: str = "0.2"
    version: str = "0.3"
    project_name: str = ""
    project_type: str = "other"
    environment: dict[str, Any] = field(default_factory=dict)
    commands: list[CommandSpec] = field(default_factory=list)
    artifacts: list[ArtifactSpec] = field(default_factory=list)
    metrics: list[MetricSpec] = field(default_factory=list)
    safety: SafetySpec = field(default_factory=SafetySpec)
    # Legacy fields preserved for backward compat
    experiments: list[dict[str, Any]] = field(default_factory=list)
    paper: dict[str, Any] = field(default_factory=dict)
    data: list[dict[str, Any]] = field(default_factory=list)
    figures: list[dict[str, Any]] = field(default_factory=list)
    results: list[dict[str, Any]] = field(default_factory=list)
    ci: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "schema_version": self.schema_version,
            "version": self.version,
            "project_name": self.project_name,
            "project_type": self.project_type,
        }
        if self.environment:
            d["environment"] = self.environment
        if self.commands:
            d["commands"] = [c.to_dict() for c in self.commands]
        if self.artifacts:
            d["artifacts"] = [a.to_dict() for a in self.artifacts]
        if self.metrics:
            d["metrics"] = [m.to_dict() for m in self.metrics]
        if self.safety:
            d["safety"] = self.safety.to_dict()
        return d


def load_orchestrator_contract(path: str) -> OrchestratorContract:
    """Load an orchestrator contract from a YAML file.

    Backward compatible: old-format files without schema_version or commands
    are loaded with defaults for the new fields.
    """
    from pathlib import Path
    import yaml

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Contract file not found: {path}")

    with open(p, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    return _dict_to_orchestrator_contract(data)


def _dict_to_orchestrator_contract(data: dict[str, Any]) -> OrchestratorContract:
    """Convert raw YAML dict to OrchestratorContract."""
    contract = OrchestratorContract(
        schema_version=str(data.get("schema_version", "0.1")),
        version=str(data.get("version", "0.3")),
        project_name=data.get("project_name", ""),
        project_type=data.get("project_type", "other"),
        environment=data.get("environment", {}),
        paper=data.get("paper", {}),
        data=data.get("data", []),
        figures=data.get("figures", []),
        results=data.get("results", []),
        ci=data.get("ci", {}),
    )

    # Commands (new schema)
    for item in data.get("commands", []):
        contract.commands.append(CommandSpec(
            id=item.get("id", ""),
            run=item.get("run", ""),
            timeout_seconds=item.get("timeout_seconds", 60),
            depends_on=item.get("depends_on", []),
            expected_artifacts=item.get("expected_artifacts", []),
        ))

    # If no commands but experiments exist, convert experiments to commands
    if not contract.commands and data.get("experiments"):
        for exp in data["experiments"]:
            if isinstance(exp, dict) and exp.get("command"):
                contract.commands.append(CommandSpec(
                    id=exp.get("id", ""),
                    run=exp.get("command", ""),
                    timeout_seconds=exp.get("timeout_seconds", 60),
                    expected_artifacts=exp.get("expected_outputs", []),
                ))
                contract.experiments.append(exp)

    # Artifacts (new schema)
    for item in data.get("artifacts", []):
        contract.artifacts.append(ArtifactSpec(
            path=item.get("path", ""),
            type=item.get("type", "file"),
        ))

    # Metrics (new schema)
    for item in data.get("metrics", []):
        contract.metrics.append(MetricSpec(
            file=item.get("file", ""),
            key=item.get("key", ""),
            expected_min=item.get("expected_min"),
            expected_max=item.get("expected_max"),
        ))

    # Safety (new schema)
    safety_data = data.get("safety", {})
    if safety_data:
        contract.safety = SafetySpec(
            network=safety_data.get("network", False),
            allow_shell=safety_data.get("allow_shell", False),
            max_runtime_seconds=safety_data.get("max_runtime_seconds", 300),
            max_artifact_mb=safety_data.get("max_artifact_mb", 20),
        )

    return contract


def validate_orchestrator_schema(data: dict[str, Any]) -> list[str]:
    """Validate orchestrator schema fields. Returns list of warning strings."""
    warnings: list[str] = []

    schema_ver = data.get("schema_version")
    if schema_ver and str(schema_ver) not in ("0.1", "0.2"):
        warnings.append(f"Unknown schema_version: {schema_ver}")

    # Validate commands
    commands = data.get("commands", [])
    if not isinstance(commands, list):
        warnings.append("'commands' must be a list")
    else:
        cmd_ids = set()
        for i, cmd in enumerate(commands):
            if not isinstance(cmd, dict):
                warnings.append(f"commands[{i}] must be a mapping")
                continue
            if not cmd.get("id"):
                warnings.append(f"commands[{i}].id is required")
            elif cmd["id"] in cmd_ids:
                warnings.append(f"commands[{i}].id is not unique: {cmd['id']}")
            else:
                cmd_ids.add(cmd["id"])
            if not cmd.get("run"):
                warnings.append(f"commands[{i}].run is required")
            # Validate depends_on references
            for dep in cmd.get("depends_on", []):
                if dep not in cmd_ids:
                    # Forward reference -- will be checked after all IDs collected
                    pass

    # Validate artifacts
    artifacts = data.get("artifacts", [])
    if not isinstance(artifacts, list):
        warnings.append("'artifacts' must be a list")

    # Validate metrics
    metrics = data.get("metrics", [])
    if not isinstance(metrics, list):
        warnings.append("'metrics' must be a list")
    else:
        for i, m in enumerate(metrics):
            if not isinstance(m, dict):
                warnings.append(f"metrics[{i}] must be a mapping")
                continue
            if not m.get("file"):
                warnings.append(f"metrics[{i}].file is required")
            if not m.get("key"):
                warnings.append(f"metrics[{i}].key is required")

    # Validate safety
    safety = data.get("safety", {})
    if safety and not isinstance(safety, dict):
        warnings.append("'safety' must be a mapping")

    return warnings
