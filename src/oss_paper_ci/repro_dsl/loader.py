"""DSL loader for reproducibility.yml files.

Supports loading v1 schema directly and detecting legacy formats.
Does NOT execute any code. Only reads and parses YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schema import (
    ReproDSL,
    ProjectSpec,
    EnvironmentSpec,
    DatasetSpec,
    StepSpec,
    ArtifactSpec,
    MetricSpec,
    MetricKeySpec,
    ExpectedSpec,
    SafetySpec,
)


def _detect_version(data: dict[str, Any]) -> str:
    """Detect the schema version of a reproducibility.yml.

    Returns:
        "v1" for DSL v1 (has version: 1 and steps as dict)
        "v0.2" for orchestrator schema (has schema_version: "0.2" and commands)
        "v0.3" for legacy contract (has version: "0.3" and experiments)
        "unknown" if unrecognized
    """
    # v1: version is int 1 and steps is a dict
    if data.get("version") == 1 and isinstance(data.get("steps"), dict):
        return "v1"
    # v0.2: has schema_version "0.2" and commands list
    if data.get("schema_version") == "0.2" and isinstance(data.get("commands"), list):
        return "v0.2"
    # v0.3: has version "0.3" and experiments list
    if data.get("version") == "0.3" and isinstance(data.get("experiments"), list):
        return "v0.3"
    # Also check for version "0.3" with environment key
    if data.get("version") == "0.3" and isinstance(data.get("environment"), dict):
        return "v0.3"
    return "unknown"


def _parse_v1(data: dict[str, Any]) -> ReproDSL:
    """Parse a v1 schema dict into ReproDSL."""
    # Parse project
    proj_data = data.get("project", {})
    project = ProjectSpec(
        name=proj_data.get("name", "unnamed"),
        description=proj_data.get("description", ""),
        paper=proj_data.get("paper", ""),
        repository=proj_data.get("repository", ""),
    )

    # Parse environments
    environments: dict[str, EnvironmentSpec] = {}
    for env_name, env_data in data.get("environments", {}).items():
        if not isinstance(env_data, dict):
            continue
        environments[env_name] = EnvironmentSpec(
            adapter=env_data.get("adapter", ""),
            runtime=env_data.get("runtime", ""),
            python=env_data.get("python", ""),
            install=list(env_data.get("install", [])),
        )

    # Parse datasets
    datasets: dict[str, DatasetSpec] = {}
    for ds_name, ds_data in data.get("datasets", {}).items():
        if not isinstance(ds_data, dict):
            continue
        datasets[ds_name] = DatasetSpec(
            path=ds_data.get("path", ""),
            required=ds_data.get("required", True),
            description=ds_data.get("description", ""),
        )

    # Parse steps
    steps: dict[str, StepSpec] = {}
    for step_id, step_data in data.get("steps", {}).items():
        if not isinstance(step_data, dict):
            continue
        metrics: list[MetricKeySpec] = []
        for m in step_data.get("metrics", []):
            if isinstance(m, dict):
                metrics.append(
                    MetricKeySpec(
                        path=m.get("path", ""),
                        keys=list(m.get("keys", [])),
                    )
                )
        steps[step_id] = StepSpec(
            id=step_id,
            command=step_data.get("command", ""),
            adapter=step_data.get("adapter", ""),
            needs=list(step_data.get("needs", [])),
            produces=list(step_data.get("produces", [])),
            timeout=int(step_data.get("timeout", 3600)),
            metrics=metrics,
            description=step_data.get("description", ""),
        )

    # Parse artifacts
    artifacts: list[ArtifactSpec] = []
    for a in data.get("artifacts", []):
        if isinstance(a, str):
            artifacts.append(ArtifactSpec(path=a))
        elif isinstance(a, dict):
            artifacts.append(
                ArtifactSpec(
                    path=a.get("path", ""),
                    type=a.get("type", "file"),
                )
            )

    # Parse expected
    expected_metrics: dict[str, MetricSpec] = {}
    expected_data = data.get("expected", {})
    if isinstance(expected_data, dict):
        for key, val in expected_data.get("metrics", {}).items():
            if isinstance(val, dict):
                expected_metrics[key] = MetricSpec(
                    key=key,
                    min=val.get("min"),
                    max=val.get("max"),
                )
    expected = ExpectedSpec(metrics=expected_metrics)

    # Parse safety
    safety_data = data.get("safety", {})
    if not isinstance(safety_data, dict):
        safety_data = {}
    safety = SafetySpec(
        network=bool(safety_data.get("network", False)),
        allow_install=bool(safety_data.get("allow_install", False)),
        allow_gpu=bool(safety_data.get("allow_gpu", False)),
    )

    return ReproDSL(
        version=1,
        project=project,
        environments=environments,
        datasets=datasets,
        steps=steps,
        artifacts=artifacts,
        expected=expected,
        safety=safety,
    )


def _convert_v0_2(data: dict[str, Any]) -> ReproDSL:
    """Convert a v0.2 orchestrator schema to v1 ReproDSL.

    v0.2 structure:
        schema_version: "0.2"
        project: {name, description, paper_url, repo_url}
        environment: {python_version, requirements_file, ...}
        commands: [{id, cmd, needs, produces, timeout, description}]
        outputs: [{path, type}]
    """
    # Project
    proj_data = data.get("project", {})
    project = ProjectSpec(
        name=proj_data.get("name", proj_data.get("title", "unnamed")),
        description=proj_data.get("description", ""),
        paper=proj_data.get("paper_url", proj_data.get("paper", "")),
        repository=proj_data.get("repo_url", proj_data.get("repository", "")),
    )

    # Environment
    env_data = data.get("environment", {})
    install: list[str] = []
    req_file = env_data.get("requirements_file", "")
    if req_file:
        install.append(f"pip install -r {req_file}")
    pip_packages = env_data.get("pip_packages", env_data.get("packages", []))
    if isinstance(pip_packages, list):
        install.extend(str(p) for p in pip_packages)

    environments: dict[str, EnvironmentSpec] = {}
    if env_data:
        environments["default"] = EnvironmentSpec(
            adapter=env_data.get("adapter", ""),
            runtime=env_data.get("runtime", ""),
            python=env_data.get("python_version", env_data.get("python", "")),
            install=install,
        )

    # Steps from commands list
    steps: dict[str, StepSpec] = {}
    for cmd in data.get("commands", []):
        if not isinstance(cmd, dict):
            continue
        step_id = cmd.get("id", cmd.get("name", ""))
        if not step_id:
            continue
        steps[step_id] = StepSpec(
            id=step_id,
            command=cmd.get("cmd", cmd.get("command", "")),
            adapter=cmd.get("adapter", ""),
            needs=list(cmd.get("needs", [])),
            produces=list(cmd.get("produces", [])),
            timeout=int(cmd.get("timeout", 3600)),
            metrics=[],
            description=cmd.get("description", ""),
        )

    # Artifacts from outputs
    artifacts: list[ArtifactSpec] = []
    for out in data.get("outputs", data.get("artifacts", [])):
        if isinstance(out, str):
            artifacts.append(ArtifactSpec(path=out))
        elif isinstance(out, dict):
            artifacts.append(
                ArtifactSpec(
                    path=out.get("path", ""),
                    type=out.get("type", "file"),
                )
            )

    return ReproDSL(
        version=1,
        project=project,
        environments=environments,
        datasets={},
        steps=steps,
        artifacts=artifacts,
        expected=ExpectedSpec(),
        safety=SafetySpec(),
    )


def _convert_v0_3(data: dict[str, Any]) -> ReproDSL:
    """Convert a v0.3 legacy contract to v1 ReproDSL.

    v0.3 structure:
        version: "0.3"
        project: {name, description, paper, repository}
        environment: {adapter, runtime, python, requirements}
        datasets: [{name, path, required, description}]
        experiments: [{id, command, adapter, dependencies, outputs, timeout, description}]
        artifacts: [{path, type}]
        metrics: [{key, min, max}]
    """
    # Project
    proj_data = data.get("project", {})
    project = ProjectSpec(
        name=proj_data.get("name", "unnamed"),
        description=proj_data.get("description", ""),
        paper=proj_data.get("paper", ""),
        repository=proj_data.get("repository", ""),
    )

    # Environment
    env_data = data.get("environment", {})
    if isinstance(env_data, dict):
        req = env_data.get("requirements", [])
        if isinstance(req, str):
            install = [f"pip install -r {req}"] if req else []
        elif isinstance(req, list):
            install = list(req)
        else:
            install = []
        environments: dict[str, EnvironmentSpec] = {
            "default": EnvironmentSpec(
                adapter=env_data.get("adapter", ""),
                runtime=env_data.get("runtime", ""),
                python=env_data.get("python", ""),
                install=install,
            )
        }
    else:
        environments = {}

    # Datasets
    datasets: dict[str, DatasetSpec] = {}
    for ds in data.get("datasets", []):
        if not isinstance(ds, dict):
            continue
        ds_name = ds.get("name", ds.get("id", ""))
        if not ds_name:
            continue
        datasets[ds_name] = DatasetSpec(
            path=ds.get("path", ""),
            required=ds.get("required", True),
            description=ds.get("description", ""),
        )

    # Steps from experiments list
    steps: dict[str, StepSpec] = {}
    for exp in data.get("experiments", []):
        if not isinstance(exp, dict):
            continue
        step_id = exp.get("id", exp.get("name", ""))
        if not step_id:
            continue
        steps[step_id] = StepSpec(
            id=step_id,
            command=exp.get("command", exp.get("cmd", "")),
            adapter=exp.get("adapter", ""),
            needs=list(exp.get("dependencies", exp.get("needs", []))),
            produces=list(exp.get("outputs", exp.get("produces", []))),
            timeout=int(exp.get("timeout", 3600)),
            metrics=[],
            description=exp.get("description", ""),
        )

    # Artifacts
    artifacts: list[ArtifactSpec] = []
    for a in data.get("artifacts", []):
        if isinstance(a, str):
            artifacts.append(ArtifactSpec(path=a))
        elif isinstance(a, dict):
            artifacts.append(
                ArtifactSpec(
                    path=a.get("path", ""),
                    type=a.get("type", "file"),
                )
            )

    # Metrics
    expected_metrics: dict[str, MetricSpec] = {}
    for m in data.get("metrics", []):
        if not isinstance(m, dict):
            continue
        key = m.get("key", m.get("name", ""))
        if not key:
            continue
        expected_metrics[key] = MetricSpec(
            key=key,
            min=m.get("min"),
            max=m.get("max"),
        )

    return ReproDSL(
        version=1,
        project=project,
        environments=environments,
        datasets=datasets,
        steps=steps,
        artifacts=artifacts,
        expected=ExpectedSpec(metrics=expected_metrics),
        safety=SafetySpec(),
    )


def load_dsl_raw(path: str | Path) -> tuple[dict[str, Any], str]:
    """Load raw YAML data and detect version.

    Returns:
        Tuple of (raw_dict, version_string)
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    version = _detect_version(data)
    return data, version


def load_dsl(path: str | Path) -> ReproDSL:
    """Load a reproducibility.yml and return a normalized ReproDSL.

    Supports v1, v0.2, and v0.3 formats. For legacy formats,
    uses built-in conversion to produce a v1 ReproDSL.
    """
    path = Path(path)
    data, version = load_dsl_raw(path)

    if version == "v1":
        return _parse_v1(data)
    elif version == "v0.2":
        return _convert_v0_2(data)
    elif version == "v0.3":
        return _convert_v0_3(data)
    else:
        # Try to parse as v1 anyway, with best effort
        return _parse_v1(data)
