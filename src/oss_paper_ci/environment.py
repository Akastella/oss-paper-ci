"""Environment detection and installation planning for reproduce command.

Detects Python environment files in a repository and generates an
installation plan. Does NOT execute installation — that is the runner's job.

Detection priority:
1. requirements.txt
2. pyproject.toml
3. setup.py
4. setup.cfg
5. environment.yml
6. conda.yml
7. Pipfile
8. poetry.lock
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EnvironmentFile:
    """A detected environment file."""

    file_type: str  # "requirements.txt", "pyproject.toml", etc.
    path: str  # relative path from repo root
    exists: bool = True


@dataclass
class InstallStep:
    """A single installation step."""

    description: str
    command: str
    env_type: str  # "pip", "conda", "unsupported"
    timeout: int = 300


@dataclass
class EnvironmentPlan:
    """Result of environment detection."""

    environment_files: list[EnvironmentFile] = field(default_factory=list)
    install_steps: list[InstallStep] = field(default_factory=list)
    python_version: str = ""
    warnings: list[str] = field(default_factory=list)
    supported: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "environment_files": [
                {"type": f.file_type, "path": f.path, "exists": f.exists}
                for f in self.environment_files
            ],
            "install_steps": [
                {
                    "description": s.description,
                    "command": s.command,
                    "env_type": s.env_type,
                    "timeout": s.timeout,
                }
                for s in self.install_steps
            ],
            "python_version": self.python_version,
            "warnings": self.warnings,
            "supported": self.supported,
        }


# Priority order for environment file detection
_ENV_FILE_PRIORITY = [
    ("requirements.txt", "pip"),
    ("pyproject.toml", "pip"),
    ("setup.py", "pip"),
    ("setup.cfg", "pip"),
    ("environment.yml", "conda"),
    ("conda.yml", "conda"),
    ("Pipfile", "pip"),
    ("poetry.lock", "poetry"),
]


def detect_environment(repo_path: str) -> EnvironmentPlan:
    """Detect environment files and generate an installation plan.

    Args:
        repo_path: Path to the repository root.

    Returns:
        EnvironmentPlan with detected files and install steps.
    """
    root = Path(repo_path)
    plan = EnvironmentPlan()

    # Detect all environment files
    for filename, env_type in _ENV_FILE_PRIORITY:
        fpath = root / filename
        if fpath.exists():
            plan.environment_files.append(EnvironmentFile(
                file_type=filename,
                path=filename,
                exists=True,
            ))

    # If no environment files found
    if not plan.environment_files:
        plan.warnings.append("No environment files detected in the repository.")
        return plan

    # Generate install steps based on detected files
    primary = plan.environment_files[0]

    if primary.file_type == "requirements.txt":
        plan.install_steps.append(InstallStep(
            description="Install dependencies from requirements.txt",
            command="python -m pip install -r requirements.txt",
            env_type="pip",
        ))
    elif primary.file_type == "pyproject.toml":
        plan.install_steps.append(InstallStep(
            description="Install package in editable mode from pyproject.toml",
            command="python -m pip install -e .",
            env_type="pip",
        ))
    elif primary.file_type == "setup.py":
        plan.install_steps.append(InstallStep(
            description="Install package from setup.py",
            command="python -m pip install -e .",
            env_type="pip",
        ))
    elif primary.file_type == "setup.cfg":
        plan.install_steps.append(InstallStep(
            description="Install package from setup.cfg",
            command="python -m pip install -e .",
            env_type="pip",
        ))
    elif primary.file_type in ("environment.yml", "conda.yml"):
        plan.warnings.append(
            f"Detected {primary.file_type} (Conda environment). "
            f"Conda installation is not automated by oss-paper-ci. "
            f"The reproduce command will attempt pip-based installation "
            f"if a requirements.txt is also present."
        )
        # Check if requirements.txt also exists as fallback
        req_path = root / "requirements.txt"
        if req_path.exists():
            plan.install_steps.append(InstallStep(
                description="Install dependencies from requirements.txt (Conda fallback)",
                command="python -m pip install -r requirements.txt",
                env_type="pip",
            ))
        else:
            plan.supported = False
            plan.warnings.append(
                "No pip-compatible installation method available. "
                "Install dependencies manually with conda."
            )
    elif primary.file_type == "Pipfile":
        plan.install_steps.append(InstallStep(
            description="Install dependencies from Pipfile",
            command="pip install pipenv && pipenv install --system",
            env_type="pip",
        ))
    elif primary.file_type == "poetry.lock":
        plan.warnings.append(
            "Detected poetry.lock. Poetry installation is not automated. "
            "Attempting pip-based installation if possible."
        )
        # Check for pyproject.toml as fallback
        if (root / "pyproject.toml").exists():
            plan.install_steps.append(InstallStep(
                description="Install package from pyproject.toml (Poetry fallback)",
                command="python -m pip install -e .",
                env_type="pip",
            ))
        else:
            plan.supported = False

    # Detect Python version from environment.yml if present
    env_yml = root / "environment.yml"
    if env_yml.exists():
        plan.python_version = _extract_python_version(env_yml)
    conda_yml = root / "conda.yml"
    if conda_yml.exists() and not plan.python_version:
        plan.python_version = _extract_python_version(conda_yml)

    return plan


def _extract_python_version(yml_path: Path) -> str:
    """Extract Python version from an environment.yml file."""
    import yaml

    try:
        data = yaml.safe_load(yml_path.read_text(encoding="utf-8"))
    except Exception:
        return ""

    if not isinstance(data, dict):
        return ""

    deps = data.get("dependencies", [])
    for dep in deps:
        if isinstance(dep, str) and dep.startswith("python="):
            return dep.split("=", 1)[1]
        if isinstance(dep, str) and dep.startswith("python>="):
            return dep.split(">=", 1)[1]

    return ""
