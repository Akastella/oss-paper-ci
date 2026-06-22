"""Autoplan engine: generate candidate reproducibility.yml from intake analysis.

Generates a candidate plan that must be reviewed by a human before execution.
Never executes commands or modifies the repository without explicit --write.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from oss_paper_ci.intake import IntakeReport, run_intake
from oss_paper_ci.readme_miner import CommandCandidate


@dataclass
class AutoplanResult:
    """Result of autoplan generation."""

    candidate_config: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    intake_report: IntakeReport | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_config": self.candidate_config,
            "warnings": self.warnings,
            "limitations": self.limitations,
        }


def run_autoplan(
    input_path: str,
    clone: bool = False,
    workdir: str | None = None,
) -> AutoplanResult:
    """Generate a candidate reproducibility.yml from repository analysis.

    Args:
        input_path: Local path, GitHub URL, or paper URL.
        clone: If True and input is a GitHub URL, clone.
        workdir: Working directory for clone.

    Returns:
        AutoplanResult with candidate config.
    """
    result = AutoplanResult()

    # Run intake first
    intake = run_intake(input_path, clone=clone, workdir=workdir)
    result.intake_report = intake
    result.warnings.extend(intake.warnings)

    # If intake didn't produce useful results, return early
    if not intake.detected.ecosystems and not intake.command_candidates:
        result.warnings.append("No ecosystems or commands detected; cannot generate plan.")
        return result

    # Check for existing config
    if intake.detected.has_existing_config:
        result.warnings.append(
            f"Existing config found at {intake.detected.existing_config_path}. "
            "Use --force to overwrite."
        )

    # Build candidate config
    result.candidate_config = _build_candidate_config(intake)

    # Add limitations
    result.limitations = [
        "Candidate plan inferred from repository files; review before execution.",
        "Command ordering may not reflect actual dependency requirements.",
        "Timeout values are defaults; adjust based on expected runtime.",
        "Not all detected commands may be needed for reproduction.",
        "Environment detection is based on file presence, not content analysis.",
    ]

    return result


def _build_candidate_config(intake: IntakeReport) -> dict[str, Any]:
    """Build a candidate reproducibility.yml from intake data."""
    config: dict[str, Any] = {
        "schema_version": "0.2",
        "generated_by": "oss-paper-ci",
        "generated_mode": "candidate",
        "confidence": intake.confidence.get("overall", 0.0),
    }

    # Environment section
    config["environment"] = _build_environment_section(intake)

    # Commands section
    config["commands"] = _build_commands_section(intake)

    # Artifacts section
    config["artifacts"] = _build_artifacts_section(intake)

    # Metrics section (empty by default)
    config["metrics"] = []

    # Safety section
    config["safety"] = {
        "network": False,
        "allow_shell": False,
        "max_runtime_seconds": 600,
        "max_artifact_mb": 20,
    }

    # Limitations
    config["limitations"] = [
        "Candidate plan inferred from repository files; review before execution.",
    ]

    return config


def _build_environment_section(intake: IntakeReport) -> dict[str, Any]:
    """Build the environment section of the candidate config."""
    env: dict[str, Any] = {}

    ecosystems = intake.detected.ecosystems
    env_files = intake.detected.environment_files

    # Determine primary ecosystem
    if not ecosystems:
        return env

    primary = ecosystems[0]
    eco_id = primary.get("id", "unknown")

    # Set environment type
    env["type"] = eco_id

    # Set Python version if Python ecosystem
    if eco_id == "python":
        env["python"] = ">=3.10"

    # Build install commands
    install_cmds: list[str] = []

    # Check for specific environment files
    if "requirements.txt" in env_files:
        install_cmds.append("python -m pip install -r requirements.txt")
    elif "pyproject.toml" in env_files:
        install_cmds.append("python -m pip install -e .")
    elif "setup.py" in env_files:
        install_cmds.append("python -m pip install -e .")
    elif "environment.yml" in env_files or "conda.yml" in env_files:
        env_file = "environment.yml" if "environment.yml" in env_files else "conda.yml"
        install_cmds.append(f"conda env create -f {env_file}")
    elif "package.json" in env_files:
        install_cmds.append("npm install")
    elif "Cargo.toml" in env_files:
        install_cmds.append("cargo build --release")
    elif "pom.xml" in env_files:
        install_cmds.append("mvn package")
    elif "renv.lock" in env_files:
        install_cmds.append("Rscript -e 'renv::restore()'")
    elif "Project.toml" in env_files:
        install_cmds.append("julia -e 'using Pkg; Pkg.instantiate()'")

    # Also check ecosystem install plans
    if not install_cmds:
        for eco in ecosystems:
            plans = eco.get("install_plan", [])
            if plans:
                install_cmds.extend(plans)
                break

    if install_cmds:
        env["install"] = install_cmds

    return env


def _build_commands_section(intake: IntakeReport) -> list[dict[str, Any]]:
    """Build the commands section of the candidate config."""
    commands: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Filter to safe, non-install commands
    run_candidates = [
        c for c in intake.command_candidates
        if not c.dangerous and c.kind != "install"
    ]

    # Sort by kind priority: data -> train -> evaluate -> figure -> unknown
    kind_order = {"data": 0, "train": 1, "evaluate": 2, "figure": 3, "test": 4, "unknown": 5}
    run_candidates.sort(key=lambda c: (kind_order.get(c.kind, 5), -c.confidence))

    # Take top commands (limit to reasonable number)
    for c in run_candidates[:10]:
        cmd_id = c.id
        if cmd_id in seen_ids:
            cmd_id = f"{cmd_id}_{len(commands)}"
        seen_ids.add(cmd_id)

        cmd: dict[str, Any] = {
            "id": cmd_id,
            "run": c.command,
            "timeout_seconds": 300,
        }

        # Add expected artifacts if we can infer them
        if c.kind == "train":
            cmd["expected_artifacts"] = _infer_train_artifacts(intake)
        elif c.kind == "evaluate":
            cmd["expected_artifacts"] = _infer_eval_artifacts(intake)
        elif c.kind == "figure":
            cmd["expected_artifacts"] = _infer_figure_artifacts(intake)

        commands.append(cmd)

    return commands


def _build_artifacts_section(intake: IntakeReport) -> list[dict[str, Any]]:
    """Build the artifacts section of the candidate config."""
    artifacts: list[dict[str, Any]] = []

    for path in intake.detected.artifact_paths:
        artifact_type = _classify_artifact(path)
        artifacts.append({
            "path": path,
            "type": artifact_type,
        })

    return artifacts


def _classify_artifact(path: str) -> str:
    """Classify an artifact by its path."""
    p = path.lower()
    if any(w in p for w in ["metric", "score", "result.json"]):
        return "metrics"
    if any(w in p for w in ["fig", "plot", "chart", ".png", ".pdf", ".svg"]):
        return "figure"
    if any(w in p for w in ["table", ".csv", ".tsv"]):
        return "table"
    if any(w in p for w in [".log"]):
        return "log"
    return "file"


def _infer_train_artifacts(intake: IntakeReport) -> list[str]:
    """Infer expected artifacts from training commands."""
    artifacts = []
    for p in intake.detected.artifact_paths:
        if any(w in p.lower() for w in ["model", "weight", "checkpoint", "metrics"]):
            artifacts.append(p)
    if not artifacts:
        for p in intake.detected.result_paths:
            artifacts.append(p.rstrip("/") + "/")
    return artifacts[:3]


def _infer_eval_artifacts(intake: IntakeReport) -> list[str]:
    """Infer expected artifacts from evaluation commands."""
    artifacts = []
    for p in intake.detected.artifact_paths:
        if any(w in p.lower() for w in ["metric", "score", "eval", "result"]):
            artifacts.append(p)
    return artifacts[:3]


def _infer_figure_artifacts(intake: IntakeReport) -> list[str]:
    """Infer expected artifacts from figure commands."""
    artifacts = []
    for p in intake.detected.artifact_paths:
        if any(w in p.lower() for w in ["fig", "plot", ".png", ".pdf", ".svg"]):
            artifacts.append(p)
    return artifacts[:3]


def validate_candidate_config(config_path: str) -> list[str]:
    """Validate a candidate reproducibility.yml file.

    Args:
        config_path: Path to the candidate config file.

    Returns:
        List of validation warnings/errors.
    """
    warnings: list[str] = []
    p = Path(config_path)

    if not p.exists():
        warnings.append(f"File not found: {config_path}")
        return warnings

    try:
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        warnings.append(f"Failed to parse YAML: {e}")
        return warnings

    # Check required fields
    if not data.get("schema_version"):
        warnings.append("Missing 'schema_version' field.")

    # Check generated_mode
    if data.get("generated_mode") != "candidate":
        warnings.append(
            "Config does not have 'generated_mode: candidate'. "
            "This may be a manually authored config."
        )

    # Validate commands
    commands = data.get("commands", [])
    if not isinstance(commands, list):
        warnings.append("'commands' must be a list.")
    else:
        cmd_ids = set()
        for i, cmd in enumerate(commands):
            if not isinstance(cmd, dict):
                warnings.append(f"commands[{i}] must be a mapping.")
                continue
            if not cmd.get("id"):
                warnings.append(f"commands[{i}].id is required.")
            elif cmd["id"] in cmd_ids:
                warnings.append(f"commands[{i}].id is not unique: {cmd['id']}")
            else:
                cmd_ids.add(cmd["id"])
            if not cmd.get("run"):
                warnings.append(f"commands[{i}].run is required.")

    # Validate environment
    env = data.get("environment")
    if env and not isinstance(env, dict):
        warnings.append("'environment' must be a mapping.")

    # Validate artifacts
    artifacts = data.get("artifacts", [])
    if not isinstance(artifacts, list):
        warnings.append("'artifacts' must be a list.")

    # Validate safety
    safety = data.get("safety")
    if safety and not isinstance(safety, dict):
        warnings.append("'safety' must be a mapping.")

    return warnings


def diff_configs(old_path: str, new_path: str) -> dict[str, Any]:
    """Compare two reproducibility.yml configs and produce a diff.

    Args:
        old_path: Path to the old config.
        new_path: Path to the new config.

    Returns:
        Dict with added, removed, changed sections.
    """
    result: dict[str, Any] = {
        "old_path": old_path,
        "new_path": new_path,
        "added": {},
        "removed": {},
        "changed": {},
    }

    try:
        with open(old_path, encoding="utf-8") as f:
            old_data = yaml.safe_load(f) or {}
    except Exception:
        result["error"] = f"Failed to read old config: {old_path}"
        return result

    try:
        with open(new_path, encoding="utf-8") as f:
            new_data = yaml.safe_load(f) or {}
    except Exception:
        result["error"] = f"Failed to read new config: {new_path}"
        return result

    # Compare top-level keys
    all_keys = set(list(old_data.keys()) + list(new_data.keys()))

    for key in sorted(all_keys):
        old_val = old_data.get(key)
        new_val = new_data.get(key)

        if old_val is None and new_val is not None:
            result["added"][key] = new_val
        elif old_val is not None and new_val is None:
            result["removed"][key] = old_val
        elif old_val != new_val:
            result["changed"][key] = {
                "old": old_val,
                "new": new_val,
            }

    return result


def format_diff_markdown(diff: dict[str, Any]) -> str:
    """Format a config diff as markdown."""
    lines: list[str] = []
    lines.append("# Autoplan Config Diff")
    lines.append("")

    if diff.get("error"):
        lines.append(f"**Error:** {diff['error']}")
        return "\n".join(lines)

    lines.append(f"**Old:** `{diff.get('old_path', '?')}`")
    lines.append(f"**New:** `{diff.get('new_path', '?')}`")
    lines.append("")

    added = diff.get("added", {})
    removed = diff.get("removed", {})
    changed = diff.get("changed", {})

    if not added and not removed and not changed:
        lines.append("No differences found.")
        return "\n".join(lines)

    if added:
        lines.append("## Added")
        for key, val in added.items():
            lines.append(f"- **{key}**: `{val}`")
        lines.append("")

    if removed:
        lines.append("## Removed")
        for key, val in removed.items():
            lines.append(f"- **{key}**: `{val}`")
        lines.append("")

    if changed:
        lines.append("## Changed")
        for key, val in changed.items():
            lines.append(f"- **{key}**")
            if isinstance(val, dict):
                lines.append(f"  - Old: `{val.get('old', '')}`")
                lines.append(f"  - New: `{val.get('new', '')}`")
        lines.append("")

    return "\n".join(lines)
