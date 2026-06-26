"""Reproducibility DSL v1 schema definitions.

Defines the formal data structures for reproducibility.yml v1.
All fields use stable ordering and relative paths.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MetricKeySpec:
    """A single metric key to extract from a metrics file."""

    path: str
    keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "keys": sorted(self.keys)}


@dataclass(frozen=True)
class MetricSpec:
    """Expected metric range for validation."""

    key: str
    min: float | None = None
    max: float | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"key": self.key}
        if self.min is not None:
            d["min"] = self.min
        if self.max is not None:
            d["max"] = self.max
        return d


@dataclass(frozen=True)
class ExpectedSpec:
    """Expected outputs and metrics for the reproduction."""

    metrics: dict[str, MetricSpec] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        if not self.metrics:
            return {}
        return {"metrics": {k: v.to_dict() for k, v in sorted(self.metrics.items())}}


@dataclass(frozen=True)
class SafetySpec:
    """Safety constraints for reproduction execution."""

    network: bool = False
    allow_install: bool = False
    allow_gpu: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "network": self.network,
            "allow_install": self.allow_install,
            "allow_gpu": self.allow_gpu,
        }


@dataclass(frozen=True)
class ProjectSpec:
    """Project metadata."""

    name: str
    description: str = ""
    paper: str = ""
    repository: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name}
        if self.description:
            d["description"] = self.description
        if self.paper:
            d["paper"] = self.paper
        if self.repository:
            d["repository"] = self.repository
        return d


@dataclass(frozen=True)
class EnvironmentSpec:
    """Environment specification for a reproduction step."""

    adapter: str = ""
    runtime: str = ""
    python: str = ""
    install: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.adapter:
            d["adapter"] = self.adapter
        if self.runtime:
            d["runtime"] = self.runtime
        if self.python:
            d["python"] = self.python
        if self.install:
            d["install"] = sorted(self.install)
        return d


@dataclass(frozen=True)
class DatasetSpec:
    """Dataset declaration."""

    path: str
    required: bool = True
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"path": self.path, "required": self.required}
        if self.description:
            d["description"] = self.description
        return d


@dataclass(frozen=True)
class ArtifactSpec:
    """An artifact produced by a step or the overall reproduction."""

    path: str
    type: str = "file"

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "type": self.type}


@dataclass(frozen=True)
class StepSpec:
    """A single reproduction step in the DAG."""

    id: str
    command: str
    adapter: str = ""
    needs: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    timeout: int = 3600
    metrics: list[MetricKeySpec] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "command": self.command,
        }
        if self.adapter:
            d["adapter"] = self.adapter
        if self.needs:
            d["needs"] = sorted(self.needs)
        if self.produces:
            d["produces"] = sorted(self.produces)
        if self.timeout != 3600:
            d["timeout"] = self.timeout
        if self.metrics:
            d["metrics"] = [m.to_dict() for m in self.metrics]
        if self.description:
            d["description"] = self.description
        return d


@dataclass(frozen=True)
class ReproDSL:
    """Top-level Reproducibility DSL v1 specification."""

    version: int = 1
    project: ProjectSpec = field(default_factory=lambda: ProjectSpec(name="unnamed"))
    environments: dict[str, EnvironmentSpec] = field(default_factory=dict)
    datasets: dict[str, DatasetSpec] = field(default_factory=dict)
    steps: dict[str, StepSpec] = field(default_factory=dict)
    artifacts: list[ArtifactSpec] = field(default_factory=list)
    expected: ExpectedSpec = field(default_factory=ExpectedSpec)
    safety: SafetySpec = field(default_factory=SafetySpec)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a stable, sorted dictionary."""
        d: dict[str, Any] = {"version": self.version}
        d["project"] = self.project.to_dict()
        if self.environments:
            d["environments"] = {
                k: v.to_dict() for k, v in sorted(self.environments.items())
            }
        if self.datasets:
            d["datasets"] = {
                k: v.to_dict() for k, v in sorted(self.datasets.items())
            }
        if self.steps:
            d["steps"] = {k: v.to_dict() for k, v in sorted(self.steps.items())}
        if self.artifacts:
            d["artifacts"] = [a.to_dict() for a in self.artifacts]
        expected_dict = self.expected.to_dict()
        if expected_dict:
            d["expected"] = expected_dict
        d["safety"] = self.safety.to_dict()
        return d

    def to_json(self, indent: int = 2) -> str:
        """Serialize to stable JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False) + "\n"

    def dag_hash(self) -> str:
        """Compute a deterministic hash of the DAG structure (steps + dependencies)."""
        dag_data = {}
        for step_id in sorted(self.steps.keys()):
            step = self.steps[step_id]
            dag_data[step_id] = {
                "command": step.command,
                "needs": sorted(step.needs),
                "produces": sorted(step.produces),
            }
        canonical = json.dumps(dag_data, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
