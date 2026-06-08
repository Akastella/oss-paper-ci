"""Configuration loading and defaults for oss-paper-ci."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ChecksConfig:
    """Configuration for which checks to run and thresholds."""

    min_score: int = 70
    require_license: bool = True
    require_citation: bool = True
    require_environment: bool = True
    require_quickstart: bool = True


@dataclass
class ProjectConfig:
    """Project-specific configuration."""

    name: str = ""
    paper_dir: str = "paper"
    code_dirs: list[str] = field(default_factory=lambda: ["src", "scripts"])
    data_dirs: list[str] = field(default_factory=lambda: ["data"])
    results_dirs: list[str] = field(default_factory=lambda: ["results", "figures"])


@dataclass
class IgnoreConfig:
    """Paths to ignore during scanning."""

    paths: list[str] = field(default_factory=lambda: [".git", ".venv", "node_modules", "__pycache__"])


@dataclass
class OutputConfig:
    """Output configuration."""

    default_format: str = "markdown"


@dataclass
class Config:
    """Top-level configuration."""

    version: str = "0.1"
    project: ProjectConfig = field(default_factory=ProjectConfig)
    checks: ChecksConfig = field(default_factory=ChecksConfig)
    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


DEFAULT_CONFIG = Config()


def load_config(config_path: str | Path | None = None, repo_root: str | Path = ".") -> Config:
    """Load configuration from file, falling back to defaults.

    Args:
        config_path: Explicit path to config file. If None, searches repo_root.
        repo_root: Root directory of the repository.

    Returns:
        Config object with values from file merged over defaults.
    """
    if config_path is not None:
        path = Path(config_path)
        if not path.exists():
            return Config()
        return _parse_config_file(path)

    # Search for config file in repo root
    root = Path(repo_root)
    for name in ("oss-paper-ci.yml", "oss-paper-ci.yaml", ".oss-paper-ci.yml"):
        candidate = root / name
        if candidate.exists():
            return _parse_config_file(candidate)

    return Config()


def _parse_config_file(path: Path) -> Config:
    """Parse a YAML config file into a Config object."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return Config()

    if not isinstance(data, dict):
        return Config()

    config = Config()

    if "version" in data:
        config.version = str(data["version"])

    if "project" in data and isinstance(data["project"], dict):
        p = data["project"]
        config.project = ProjectConfig(
            name=p.get("name", ""),
            paper_dir=p.get("paper_dir", "paper"),
            code_dirs=p.get("code_dirs", ["src", "scripts"]),
            data_dirs=p.get("data_dirs", ["data"]),
            results_dirs=p.get("results_dirs", ["results", "figures"]),
        )

    if "checks" in data and isinstance(data["checks"], dict):
        c = data["checks"]
        config.checks = ChecksConfig(
            min_score=c.get("min_score", 70),
            require_license=c.get("require_license", True),
            require_citation=c.get("require_citation", True),
            require_environment=c.get("require_environment", True),
            require_quickstart=c.get("require_quickstart", True),
        )

    if "ignore" in data and isinstance(data["ignore"], dict):
        i = data["ignore"]
        config.ignore = IgnoreConfig(
            paths=i.get("paths", [".git", ".venv", "node_modules"]),
        )

    if "output" in data and isinstance(data["output"], dict):
        o = data["output"]
        config.output = OutputConfig(
            default_format=o.get("default_format", "markdown"),
        )

    return config


def generate_default_config() -> str:
    """Generate the default oss-paper-ci.yml content."""
    return """\
version: 0.1
project:
  name: ""
  paper_dir: "paper"
  code_dirs:
    - "src"
    - "scripts"
  data_dirs:
    - "data"
  results_dirs:
    - "results"
    - "figures"
checks:
  min_score: 70
  require_license: true
  require_citation: true
  require_environment: true
  require_quickstart: true
ignore:
  paths:
    - ".git"
    - ".venv"
    - "node_modules"
    - "__pycache__"
output:
  default_format: "markdown"
"""
