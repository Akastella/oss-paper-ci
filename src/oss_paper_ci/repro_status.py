"""Reproduction run status reader.

Reads a run directory and reports the status of a reproduction run.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RunStatus:
    """Status of a reproduction run."""

    run_dir: str = ""
    exists: bool = False
    has_manifest: bool = False
    overall_status: str = "unknown"
    started_at: str = ""
    finished_at: str = ""
    command_count: int = 0
    commands_succeeded: int = 0
    commands_failed: int = 0
    commands_blocked: int = 0
    artifact_count: int = 0
    artifacts_found: int = 0
    metrics_checked: int = 0
    metrics_in_range: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_dir": self.run_dir,
            "exists": self.exists,
            "has_manifest": self.has_manifest,
            "overall_status": self.overall_status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "command_count": self.command_count,
            "commands_succeeded": self.commands_succeeded,
            "commands_failed": self.commands_failed,
            "commands_blocked": self.commands_blocked,
            "artifact_count": self.artifact_count,
            "artifacts_found": self.artifacts_found,
            "metrics_checked": self.metrics_checked,
            "metrics_in_range": self.metrics_in_range,
            "warnings": self.warnings,
            "error": self.error,
        }


def read_run_status(run_dir: str) -> RunStatus:
    """Read the status of a reproduction run from its directory.

    Args:
        run_dir: Path to the run directory.

    Returns:
        RunStatus with details about the run.
    """
    status = RunStatus(run_dir=run_dir)
    run_path = Path(run_dir)

    if not run_path.exists():
        status.error = f"Run directory does not exist: {run_dir}"
        return status

    status.exists = True

    # Look for run manifest
    manifest_path = run_path / "run-manifest.json"
    if not manifest_path.exists():
        status.error = "No run-manifest.json found in run directory"
        return status

    status.has_manifest = True

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as exc:
        status.error = f"Failed to read manifest: {exc}"
        return status

    status.overall_status = manifest.get("overall_status", "unknown")
    status.started_at = manifest.get("started_at", "")
    status.finished_at = manifest.get("finished_at", "")

    # Command results
    cmd_results = manifest.get("command_results", [])
    status.command_count = len(cmd_results)
    for cr in cmd_results:
        s = cr.get("status", "")
        if s == "success":
            status.commands_succeeded += 1
        elif s in ("failed", "timeout"):
            status.commands_failed += 1
        elif s == "blocked":
            status.commands_blocked += 1

    # Artifact validation
    art_val = manifest.get("artifact_validation", {})
    if art_val:
        status.artifact_count = art_val.get("total", 0)
        status.artifacts_found = art_val.get("found", 0)

    # Metric validation
    met_val = manifest.get("metric_validation", {})
    if met_val:
        status.metrics_checked = met_val.get("total", 0)
        status.metrics_in_range = met_val.get("in_range", 0)

    status.warnings = manifest.get("warnings", [])
    return status


def format_status_markdown(status: RunStatus) -> str:
    """Format run status as Markdown."""
    lines = [
        "# Reproduction Run Status",
        "",
        f"**Run directory:** `{status.run_dir}`",
        f"**Status:** {status.overall_status}",
        "",
    ]

    if status.started_at:
        lines.append(f"**Started:** {status.started_at}")
    if status.finished_at:
        lines.append(f"**Finished:** {status.finished_at}")
    lines.append("")

    if status.command_count:
        lines.append("## Commands")
        lines.append("")
        lines.append(f"- Total: {status.command_count}")
        lines.append(f"- Succeeded: {status.commands_succeeded}")
        lines.append(f"- Failed: {status.commands_failed}")
        lines.append(f"- Blocked: {status.commands_blocked}")
        lines.append("")

    if status.artifact_count:
        lines.append("## Artifacts")
        lines.append("")
        lines.append(f"- Expected: {status.artifact_count}")
        lines.append(f"- Found: {status.artifacts_found}")
        lines.append("")

    if status.metrics_checked:
        lines.append("## Metrics")
        lines.append("")
        lines.append(f"- Checked: {status.metrics_checked}")
        lines.append(f"- In range: {status.metrics_in_range}")
        lines.append("")

    if status.warnings:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for w in status.warnings:
            lines.append(f"- {w}")
        lines.append("")

    if status.error:
        lines.append(f"**Error:** {status.error}")
        lines.append("")

    return "\n".join(lines)


def format_status_json(status: RunStatus) -> str:
    """Format run status as JSON."""
    return json.dumps(status.to_dict(), indent=2, ensure_ascii=False)
