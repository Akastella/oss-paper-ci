"""Confidence scoring for autoplan candidates.

Computes confidence scores for environment, commands, artifacts, and metrics
based on what was detected during intake.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConfidenceScores:
    """Confidence scores for an autoplan."""

    overall: float = 0.0
    environment: float = 0.0
    commands: float = 0.0
    artifacts: float = 0.0
    metrics: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "overall": round(self.overall, 2),
            "environment": round(self.environment, 2),
            "commands": round(self.commands, 2),
            "artifacts": round(self.artifacts, 2),
            "metrics": round(self.metrics, 2),
        }


def compute_confidence(
    ecosystems: list[dict[str, Any]],
    env_files: list[str],
    command_candidates: list[dict[str, Any]],
    artifact_paths: list[str],
    has_metrics_file: bool = False,
    has_existing_config: bool = False,
) -> ConfidenceScores:
    """Compute confidence scores based on detected information.

    Args:
        ecosystems: Detected ecosystem dicts.
        env_files: Found environment file paths.
        command_candidates: Extracted command candidate dicts.
        artifact_paths: Detected artifact paths.
        has_metrics_file: Whether a metrics file was found.
        has_existing_config: Whether an existing reproducibility.yml exists.

    Returns:
        ConfidenceScores object.
    """
    scores = ConfidenceScores()

    # Environment confidence
    scores.environment = _score_environment(ecosystems, env_files)

    # Commands confidence
    scores.commands = _score_commands(command_candidates)

    # Artifacts confidence
    scores.artifacts = _score_artifacts(artifact_paths)

    # Metrics confidence
    scores.metrics = _score_metrics(has_metrics_file, artifact_paths)

    # Overall is weighted average
    weights = {
        "environment": 0.3,
        "commands": 0.4,
        "artifacts": 0.2,
        "metrics": 0.1,
    }
    scores.overall = (
        scores.environment * weights["environment"]
        + scores.commands * weights["commands"]
        + scores.artifacts * weights["artifacts"]
        + scores.metrics * weights["metrics"]
    )

    # Boost if existing config found
    if has_existing_config:
        scores.overall = min(1.0, scores.overall + 0.1)

    return scores


def _score_environment(ecosystems: list[dict[str, Any]], env_files: list[str]) -> float:
    """Score environment detection confidence."""
    if not ecosystems:
        return 0.1

    score = 0.0

    # Base score for detecting any ecosystem
    score += 0.3

    # Bonus for environment files
    if env_files:
        score += 0.3

    # Bonus for native support level
    for eco in ecosystems:
        if eco.get("support_level") == "native":
            score += 0.2
            break

    # Bonus for having install plan
    for eco in ecosystems:
        if eco.get("install_plan"):
            score += 0.1
            break

    # Bonus for runtime availability
    for eco in ecosystems:
        if eco.get("runtime_available"):
            score += 0.1
            break

    return min(1.0, score)


def _score_commands(command_candidates: list[dict[str, Any]]) -> float:
    """Score command detection confidence."""
    if not command_candidates:
        return 0.1

    score = 0.0

    # Base score for finding any commands
    score += 0.2

    # Count non-dangerous commands
    safe_commands = [c for c in command_candidates if not c.get("dangerous", False)]
    if safe_commands:
        score += 0.2

    # Bonus for high-confidence commands
    high_conf = [c for c in safe_commands if c.get("confidence", 0) >= 0.6]
    if high_conf:
        score += 0.2

    # Bonus for classified commands (not "unknown")
    classified = [c for c in safe_commands if c.get("kind", "unknown") != "unknown"]
    if classified:
        score += 0.2

    # Bonus for multiple command kinds
    kinds = set(c.get("kind") for c in classified)
    if len(kinds) >= 2:
        score += 0.1

    # Penalty for all dangerous
    if not safe_commands and command_candidates:
        score = 0.1

    return min(1.0, score)


def _score_artifacts(artifact_paths: list[str]) -> float:
    """Score artifact detection confidence."""
    if not artifact_paths:
        return 0.1

    score = 0.3  # Base for finding artifacts

    # Bonus for structured directories
    has_results = any("result" in p.lower() for p in artifact_paths)
    has_figures = any("fig" in p.lower() or "plot" in p.lower() for p in artifact_paths)
    has_metrics = any("metric" in p.lower() for p in artifact_paths)

    if has_results:
        score += 0.2
    if has_figures:
        score += 0.2
    if has_metrics:
        score += 0.2

    # Bonus for multiple artifacts
    if len(artifact_paths) >= 3:
        score += 0.1

    return min(1.0, score)


def _score_metrics(has_metrics_file: bool, artifact_paths: list[str]) -> float:
    """Score metrics detection confidence."""
    if not has_metrics_file:
        # Check if any artifact looks like metrics
        if any("metric" in p.lower() or "score" in p.lower() for p in artifact_paths):
            return 0.3
        return 0.1

    return 0.7
