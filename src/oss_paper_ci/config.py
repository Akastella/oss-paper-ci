"""Configuration loading and defaults for oss-paper-ci.

Supports two config versions:
  - v0.1 (legacy): flat checks/project/ignore/output sections
  - v1   (current): adds profile, thresholds, severity, paths, reports, ci

Both are accepted; v0.1 fields are silently mapped to v1 equivalents.
"""

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
    enabled: list[str] = field(default_factory=list)   # empty = all enabled
    disabled: list[str] = field(default_factory=list)
    severity_overrides: dict[str, str] = field(default_factory=dict)


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
class ThresholdsConfig:
    """Scoring thresholds."""

    pass_score: int = 85
    warn_score: int = 60
    fail_under: int = 50


@dataclass
class PathsConfig:
    """Path include/exclude configuration."""

    include: list[str] = field(default_factory=lambda: ["."])
    exclude: list[str] = field(default_factory=lambda: [
        ".git/", "dist/", "build/", "__pycache__/", ".pytest_cache/",
    ])


@dataclass
class SeverityPolicy:
    """Severity classification policy."""

    fail_on: list[str] = field(default_factory=lambda: ["blocking"])
    treat_as_blocking: list[str] = field(default_factory=list)


@dataclass
class ReportsConfig:
    """Report output configuration."""

    default_format: str = "markdown"
    include_recommendations: bool = True
    max_findings: int = 50


@dataclass
class CIConfig:
    """CI integration configuration."""

    github_annotations: bool = True
    step_summary: bool = True


@dataclass
class SuppressionEntry:
    """A single finding suppression."""

    id: str = ""
    reason: str = ""
    until: str = ""


@dataclass
class SuppressionsConfig:
    """Suppression configuration."""

    paths: list[str] = field(default_factory=list)
    findings: list[SuppressionEntry] = field(default_factory=list)


@dataclass
class Config:
    """Top-level configuration."""

    version: str = "0.1"
    profile: str = "default"
    project: ProjectConfig = field(default_factory=ProjectConfig)
    checks: ChecksConfig = field(default_factory=ChecksConfig)
    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    thresholds: ThresholdsConfig = field(default_factory=ThresholdsConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    severity: SeverityPolicy = field(default_factory=SeverityPolicy)
    reports: ReportsConfig = field(default_factory=ReportsConfig)
    ci: CIConfig = field(default_factory=CIConfig)
    rule_packs: list[str] = field(default_factory=list)
    suppressions: SuppressionsConfig = field(default_factory=SuppressionsConfig)
    # Path to the config file that was loaded (empty = defaults)
    config_path: str = ""


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
    config.config_path = str(path)

    if "version" in data:
        config.version = str(data["version"])

    # ── Profile ───────────────────────────────────────────────────────────
    if "profile" in data:
        config.profile = str(data["profile"])

    # ── Project ───────────────────────────────────────────────────────────
    if "project" in data and isinstance(data["project"], dict):
        p = data["project"]
        config.project = ProjectConfig(
            name=p.get("name", ""),
            paper_dir=p.get("paper_dir", "paper"),
            code_dirs=p.get("code_dirs", ["src", "scripts"]),
            data_dirs=p.get("data_dirs", ["data"]),
            results_dirs=p.get("results_dirs", ["results", "figures"]),
        )

    # ── Checks (v0.1 compat) ──────────────────────────────────────────────
    if "checks" in data and isinstance(data["checks"], dict):
        c = data["checks"]
        config.checks = ChecksConfig(
            min_score=c.get("min_score", 70),
            require_license=c.get("require_license", True),
            require_citation=c.get("require_citation", True),
            require_environment=c.get("require_environment", True),
            require_quickstart=c.get("require_quickstart", True),
            enabled=c.get("enabled", []),
            disabled=c.get("disabled", []),
            severity_overrides=c.get("severity_overrides", {}),
        )

    # ── Ignore (v0.1 compat) ──────────────────────────────────────────────
    if "ignore" in data and isinstance(data["ignore"], dict):
        i = data["ignore"]
        config.ignore = IgnoreConfig(
            paths=i.get("paths", [".git", ".venv", "node_modules"]),
        )

    # ── Output (v0.1 compat) ──────────────────────────────────────────────
    if "output" in data and isinstance(data["output"], dict):
        o = data["output"]
        config.output = OutputConfig(
            default_format=o.get("default_format", "markdown"),
        )

    # ── Thresholds (v1) ───────────────────────────────────────────────────
    if "thresholds" in data and isinstance(data["thresholds"], dict):
        t = data["thresholds"]
        config.thresholds = ThresholdsConfig(
            pass_score=t.get("pass_score", 85),
            warn_score=t.get("warn_score", 60),
            fail_under=t.get("fail_under", 50),
        )

    # ── Paths (v1) ────────────────────────────────────────────────────────
    if "paths" in data and isinstance(data["paths"], dict):
        p = data["paths"]
        config.paths = PathsConfig(
            include=p.get("include", ["."]),
            exclude=p.get("exclude", [
                ".git/", "dist/", "build/", "__pycache__/", ".pytest_cache/",
            ]),
        )

    # ── Severity (v1) ─────────────────────────────────────────────────────
    if "severity" in data and isinstance(data["severity"], dict):
        s = data["severity"]
        config.severity = SeverityPolicy(
            fail_on=s.get("fail_on", ["blocking"]),
            treat_as_blocking=s.get("treat_as_blocking", []),
        )

    # ── Reports (v1) ──────────────────────────────────────────────────────
    if "reports" in data and isinstance(data["reports"], dict):
        r = data["reports"]
        config.reports = ReportsConfig(
            default_format=r.get("default_format", "markdown"),
            include_recommendations=r.get("include_recommendations", True),
            max_findings=r.get("max_findings", 50),
        )

    # ── CI (v1) ───────────────────────────────────────────────────────────
    if "ci" in data and isinstance(data["ci"], dict):
        ci = data["ci"]
        config.ci = CIConfig(
            github_annotations=ci.get("github_annotations", True),
            step_summary=ci.get("step_summary", True),
        )

    # ── Rule Packs (v1) ─────────────────────────────────────────────────
    if "rule_packs" in data and isinstance(data["rule_packs"], list):
        config.rule_packs = [str(p) for p in data["rule_packs"]]

    # ── Suppressions (v1) ───────────────────────────────────────────────
    if "suppressions" in data and isinstance(data["suppressions"], dict):
        supp = data["suppressions"]
        paths = supp.get("paths", [])
        findings = []
        for f in supp.get("findings", []):
            if isinstance(f, dict):
                findings.append(SuppressionEntry(
                    id=f.get("id", ""),
                    reason=f.get("reason", ""),
                    until=f.get("until", ""),
                ))
        config.suppressions = SuppressionsConfig(
            paths=paths if isinstance(paths, list) else [],
            findings=findings,
        )

    return config


def generate_default_config(*, profile: str = "default") -> str:
    """Generate a default .oss-paper-ci.yml content.

    Args:
        profile: Profile name to embed in the generated config.

    Returns:
        YAML string.
    """
    return f"""\
version: 1
profile: {profile}

paths:
  include:
    - "."
  exclude:
    - ".git/"
    - "dist/"
    - "build/"
    - "__pycache__/"
    - ".pytest_cache/"

thresholds:
  pass_score: 85
  warn_score: 60
  fail_under: 50

severity:
  fail_on:
    - blocking
  treat_as_blocking: []

checks:
  disabled: []
  severity_overrides: {{}}

reports:
  default_format: markdown
  include_recommendations: true
  max_findings: 50

ci:
  github_annotations: true
  step_summary: true

rule_packs: []

suppressions:
  paths: []
  findings: []

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

ignore:
  paths:
    - ".git"
    - ".venv"
    - "node_modules"
    - "__pycache__"
"""
