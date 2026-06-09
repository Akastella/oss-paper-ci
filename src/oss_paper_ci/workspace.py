"""Workspace configuration for multi-project batch scanning.

A workspace defines multiple projects to scan in a single run.
Each project can override profile, config, rules, and fail_under.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class WorkspaceProject:
    """A single project entry in a workspace."""

    id: str
    path: str
    profile: str = ""
    config: str = ""
    rules: list[str] = field(default_factory=list)
    fail_under: int = 0
    allow_failure: bool = False

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "path": self.path,
        }
        if self.profile:
            result["profile"] = self.profile
        if self.config:
            result["config"] = self.config
        if self.rules:
            result["rules"] = self.rules
        if self.fail_under:
            result["fail_under"] = self.fail_under
        if self.allow_failure:
            result["allow_failure"] = True
        return result


@dataclass
class WorkspaceDefaults:
    """Default values for workspace projects."""

    profile: str = "default"
    config: str = ""
    rules: list[str] = field(default_factory=list)
    fail_under: int = 0

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"profile": self.profile}
        if self.config:
            result["config"] = self.config
        if self.rules:
            result["rules"] = self.rules
        if self.fail_under:
            result["fail_under"] = self.fail_under
        return result


@dataclass
class WorkspaceConfig:
    """Top-level workspace configuration."""

    version: int = 1
    name: str = ""
    defaults: WorkspaceDefaults = field(default_factory=WorkspaceDefaults)
    projects: list[WorkspaceProject] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "defaults": self.defaults.to_dict(),
            "projects": [p.to_dict() for p in self.projects],
        }


@dataclass
class WorkspaceValidationError:
    """A single validation error."""

    field: str
    message: str


@dataclass
class WorkspaceValidationResult:
    """Result of workspace validation."""

    valid: bool
    errors: list[WorkspaceValidationError] = field(default_factory=list)

    def format_text(self) -> str:
        if self.valid:
            return "Workspace configuration is valid."
        lines = ["Workspace validation errors:"]
        for err in self.errors:
            lines.append(f"  - {err.field}: {err.message}")
        return "\n".join(lines)


def load_workspace(workspace_path: str | Path) -> WorkspaceConfig:
    """Load and validate a workspace configuration file.

    Args:
        workspace_path: Path to oss-paper-ci-workspace.yml.

    Returns:
        WorkspaceConfig with defaults applied to each project.

    Raises:
        FileNotFoundError: If workspace file does not exist.
        ValueError: If workspace is invalid.
    """
    path = Path(workspace_path)
    if not path.exists():
        raise FileNotFoundError(f"Workspace file not found: {workspace_path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("Workspace file must be a YAML mapping.")

    result = validate_workspace_data(data)
    if not result.valid:
        errors = "; ".join(f"{e.field}: {e.message}" for e in result.errors)
        raise ValueError(f"Invalid workspace: {errors}")

    return _parse_workspace(data, path.parent)


def validate_workspace(workspace_path: str | Path) -> WorkspaceValidationResult:
    """Validate a workspace file without loading it fully.

    Args:
        workspace_path: Path to workspace YAML file.

    Returns:
        WorkspaceValidationResult with errors if any.
    """
    path = Path(workspace_path)
    if not path.exists():
        return WorkspaceValidationResult(
            valid=False,
            errors=[WorkspaceValidationError("file", f"File not found: {workspace_path}")],
        )

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as exc:
        return WorkspaceValidationResult(
            valid=False,
            errors=[WorkspaceValidationError("file", f"YAML parse error: {exc}")],
        )

    if not isinstance(data, dict):
        return WorkspaceValidationResult(
            valid=False,
            errors=[WorkspaceValidationError("file", "Workspace file must be a YAML mapping.")],
        )

    return validate_workspace_data(data)


def validate_workspace_data(data: dict[str, Any]) -> WorkspaceValidationResult:
    """Validate workspace data dict.

    Args:
        data: Parsed YAML dict.

    Returns:
        WorkspaceValidationResult.
    """
    errors: list[WorkspaceValidationError] = []

    # Version
    version = data.get("version")
    if version is None:
        errors.append(WorkspaceValidationError("version", "Missing required field 'version'."))
    elif version != 1:
        errors.append(WorkspaceValidationError("version", f"Unsupported version: {version}. Must be 1."))

    # Projects
    projects = data.get("projects")
    if not projects:
        errors.append(WorkspaceValidationError("projects", "Missing or empty 'projects' list."))
    elif not isinstance(projects, list):
        errors.append(WorkspaceValidationError("projects", "'projects' must be a list."))
    else:
        # Check duplicate IDs
        seen_ids: set[str] = set()
        for i, proj in enumerate(projects):
            if not isinstance(proj, dict):
                errors.append(WorkspaceValidationError(f"projects[{i}]", "Each project must be a mapping."))
                continue

            pid = proj.get("id")
            if not pid:
                errors.append(WorkspaceValidationError(f"projects[{i}].id", "Missing required field 'id'."))
            elif not isinstance(pid, str):
                errors.append(WorkspaceValidationError(f"projects[{i}].id", "'id' must be a string."))
            elif pid in seen_ids:
                errors.append(WorkspaceValidationError(f"projects[{i}].id", f"Duplicate project id: {pid}"))
            else:
                seen_ids.add(pid)

            ppath = proj.get("path")
            if not ppath:
                errors.append(WorkspaceValidationError(f"projects[{i}].path", "Missing required field 'path'."))
            elif not isinstance(ppath, str):
                errors.append(WorkspaceValidationError(f"projects[{i}].path", "'path' must be a string."))

            # Validate allow_failure is boolean if present
            if "allow_failure" in proj and not isinstance(proj["allow_failure"], bool):
                errors.append(WorkspaceValidationError(
                    f"projects[{i}].allow_failure", "'allow_failure' must be a boolean."
                ))

            # Validate fail_under is int if present
            if "fail_under" in proj:
                fu = proj["fail_under"]
                if not isinstance(fu, int) or isinstance(fu, bool):
                    errors.append(WorkspaceValidationError(
                        f"projects[{i}].fail_under", "'fail_under' must be an integer."
                    ))

            # Validate rules is list if present
            if "rules" in proj and not isinstance(proj["rules"], list):
                errors.append(WorkspaceValidationError(
                    f"projects[{i}].rules", "'rules' must be a list."
                ))

    # Defaults validation
    defaults = data.get("defaults")
    if defaults is not None:
        if not isinstance(defaults, dict):
            errors.append(WorkspaceValidationError("defaults", "'defaults' must be a mapping."))
        else:
            if "fail_under" in defaults:
                fu = defaults["fail_under"]
                if not isinstance(fu, int) or isinstance(fu, bool):
                    errors.append(WorkspaceValidationError(
                        "defaults.fail_under", "'fail_under' must be an integer."
                    ))
            if "rules" in defaults and not isinstance(defaults["rules"], list):
                errors.append(WorkspaceValidationError(
                    "defaults.rules", "'rules' must be a list."
                ))

    return WorkspaceValidationResult(valid=len(errors) == 0, errors=errors)


def _parse_workspace(data: dict[str, Any], base_dir: Path) -> WorkspaceConfig:
    """Parse workspace data into WorkspaceConfig with defaults applied."""
    version = data.get("version", 1)
    name = data.get("name", "")

    # Parse defaults
    defaults_data = data.get("defaults", {})
    defaults = WorkspaceDefaults(
        profile=defaults_data.get("profile", "default"),
        config=defaults_data.get("config", ""),
        rules=list(defaults_data.get("rules", [])),
        fail_under=defaults_data.get("fail_under", 0),
    )

    # Parse projects with defaults applied
    projects = []
    for proj_data in data.get("projects", []):
        proj = WorkspaceProject(
            id=proj_data["id"],
            path=proj_data["path"],
            profile=proj_data.get("profile", defaults.profile),
            config=proj_data.get("config", defaults.config),
            rules=list(proj_data.get("rules", defaults.rules)),
            fail_under=proj_data.get("fail_under", defaults.fail_under),
            allow_failure=proj_data.get("allow_failure", False),
        )
        projects.append(proj)

    return WorkspaceConfig(
        version=version,
        name=name,
        defaults=defaults,
        projects=projects,
    )


def resolve_project_path(project: WorkspaceProject, workspace_dir: Path) -> Path:
    """Resolve a project path relative to the workspace file directory.

    Args:
        project: The workspace project entry.
        workspace_dir: Directory containing the workspace file.

    Returns:
        Resolved absolute path.
    """
    p = Path(project.path)
    if p.is_absolute():
        return p
    return (workspace_dir / p).resolve()


def list_workspace_projects(workspace: WorkspaceConfig) -> list[dict[str, str]]:
    """Return a summary list of workspace projects.

    Returns:
        List of dicts with id, path, profile, status.
    """
    result = []
    for proj in workspace.projects:
        result.append({
            "id": proj.id,
            "path": proj.path,
            "profile": proj.profile or "default",
            "allow_failure": "true" if proj.allow_failure else "false",
        })
    return result
