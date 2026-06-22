"""Reproduction session manager.

Manages reproduction sessions: planning, execution tracking, resume,
rerun-failed, and session-level reporting. Sessions group multiple
reproduction runs into a trackable, resumable unit.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci import __version__


@dataclass
class SessionCommand:
    """A command within a reproduction session."""

    command_id: str = ""
    command: str = ""
    status: str = "pending"  # pending | running | passed | failed | blocked | timeout | skipped | unavailable
    exit_code: int = -1
    duration_seconds: float = 0.0
    block_reason: str = ""
    attempts: int = 0
    artifacts: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command": self.command,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "block_reason": self.block_reason,
            "attempts": self.attempts,
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "warnings": self.warnings,
        }


@dataclass
class SessionSummary:
    """Summary statistics for a session."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    blocked: int = 0
    timeout: int = 0
    skipped: int = 0
    unavailable: int = 0
    pending: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "blocked": self.blocked,
            "timeout": self.timeout,
            "skipped": self.skipped,
            "unavailable": self.unavailable,
            "pending": self.pending,
        }


@dataclass
class SessionManifest:
    """Complete session manifest."""

    schema_version: str = "0.1"
    report_type: str = "oss-paper-ci-reproduction-session"
    tool_version: str = ""
    session_id: str = ""
    name: str = ""
    repo: str = ""
    config: str = ""
    status: str = "planned"  # planned | running | passed | failed | partial
    commands: list[SessionCommand] = field(default_factory=list)
    summary: SessionSummary = field(default_factory=SessionSummary)
    limitations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_type": self.report_type,
            "tool_version": self.tool_version,
            "session_id": self.session_id,
            "name": self.name,
            "repo": self.repo,
            "config": self.config,
            "status": self.status,
            "commands": [c.to_dict() for c in self.commands],
            "summary": self.summary.to_dict(),
            "limitations": self.limitations,
            "warnings": self.warnings,
        }


def generate_session_id(name: str, repo: str, config: str) -> str:
    """Generate a deterministic session ID from name, repo, and config."""
    content = f"{name}:{repo}:{config}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def create_session(
    repo_path: str,
    config_path: str | None = None,
    name: str | None = None,
) -> SessionManifest:
    """Create a new reproduction session from a reproducibility config.

    Args:
        repo_path: Path to the repository.
        config_path: Path to reproducibility.yml. If None, searches default locations.
        name: Session name. If None, uses 'default'.

    Returns:
        SessionManifest with commands from the config.
    """
    from oss_paper_ci.repro_schema import load_orchestrator_contract

    repo = Path(repo_path)
    session_name = name or "default"

    # Find config
    if config_path:
        config = Path(config_path)
    else:
        for candidate in ["reproducibility.yml", "reproducibility.yaml"]:
            if (repo / candidate).exists():
                config = repo / candidate
                break
        else:
            manifest = SessionManifest(
                tool_version=__version__,
                name=session_name,
                repo=str(repo),
                config="",
                status="planned",
                warnings=["No reproducibility.yml found. Session has no commands."],
                limitations=[
                    "Session created without a reproducibility config.",
                    "Add a reproducibility.yml to define reproduction commands.",
                ],
            )
            manifest.session_id = generate_session_id(session_name, str(repo), "")
            return manifest

    # Load contract
    try:
        contract = load_orchestrator_contract(str(config))
    except Exception as e:
        manifest = SessionManifest(
            tool_version=__version__,
            name=session_name,
            repo=str(repo),
            config=str(config),
            status="planned",
            warnings=[f"Failed to load config: {e}"],
        )
        manifest.session_id = generate_session_id(session_name, str(repo), str(config))
        return manifest

    # Build commands from contract
    commands: list[SessionCommand] = []
    for cmd_spec in contract.commands:
        # Check if command is dangerous
        from oss_paper_ci.command_safety import is_dangerous_command, get_block_reason
        blocked = is_dangerous_command(cmd_spec.run)
        block_reason = get_block_reason(cmd_spec.run) if blocked else ""

        sc = SessionCommand(
            command_id=cmd_spec.id,
            command=cmd_spec.run,
            status="blocked" if blocked else "pending",
            block_reason=block_reason,
        )
        commands.append(sc)

    # Compute summary
    summary = _compute_summary(commands)

    manifest = SessionManifest(
        tool_version=__version__,
        name=session_name,
        repo=str(repo),
        config=str(config),
        status="planned",
        commands=commands,
        summary=summary,
        limitations=[
            "Session commands are declared in reproducibility.yml.",
            "Default mode is dry-run; use --execute to run commands.",
            "Blocked dangerous commands are not executed.",
        ],
    )
    manifest.session_id = generate_session_id(session_name, str(repo), str(config))

    return manifest


def execute_session(
    manifest: SessionManifest,
    sandbox_type: str = "local",
    timeout_multiplier: float = 1.0,
) -> SessionManifest:
    """Execute pending commands in a session.

    Args:
        manifest: The session manifest to execute.
        sandbox_type: Sandbox type (local or docker).
        timeout_multiplier: Multiplier for command timeouts.

    Returns:
        Updated SessionManifest with execution results.
    """
    import subprocess
    from oss_paper_ci.command_safety import is_dangerous_command

    manifest.status = "running"

    for cmd in manifest.commands:
        # Skip non-pending commands
        if cmd.status not in ("pending",):
            continue

        # Double-check dangerous
        if is_dangerous_command(cmd.command):
            cmd.status = "blocked"
            cmd.block_reason = "Blocked: dangerous command"
            continue

        # Execute
        cmd.status = "running"
        cmd.attempts += 1
        start_time = time.time()

        try:
            proc = subprocess.run(
                cmd.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=int(300 * timeout_multiplier),
                cwd=manifest.repo,
            )
            duration = time.time() - start_time

            cmd.exit_code = proc.returncode
            cmd.duration_seconds = duration
            cmd.status = "passed" if proc.returncode == 0 else "failed"

        except subprocess.TimeoutExpired:
            cmd.duration_seconds = time.time() - start_time
            cmd.status = "timeout"
            cmd.exit_code = -1
        except Exception as e:
            cmd.duration_seconds = time.time() - start_time
            cmd.status = "failed"
            cmd.exit_code = -1
            cmd.warnings.append(str(e))

    # Update summary and status
    manifest.summary = _compute_summary(manifest.commands)
    manifest.status = _compute_overall_status(manifest.summary)

    return manifest


def get_commands_to_resume(manifest: SessionManifest) -> list[SessionCommand]:
    """Get commands that need to be resumed (pending, failed, timeout)."""
    return [c for c in manifest.commands if c.status in ("pending", "failed", "timeout")]


def get_commands_to_rerun_failed(manifest: SessionManifest) -> list[SessionCommand]:
    """Get commands that failed or timed out (not blocked)."""
    return [c for c in manifest.commands if c.status in ("failed", "timeout")]


def _compute_summary(commands: list[SessionCommand]) -> SessionSummary:
    """Compute summary statistics from commands."""
    summary = SessionSummary(total=len(commands))
    for cmd in commands:
        if cmd.status == "passed":
            summary.passed += 1
        elif cmd.status == "failed":
            summary.failed += 1
        elif cmd.status == "blocked":
            summary.blocked += 1
        elif cmd.status == "timeout":
            summary.timeout += 1
        elif cmd.status == "skipped":
            summary.skipped += 1
        elif cmd.status == "unavailable":
            summary.unavailable += 1
        elif cmd.status == "pending":
            summary.pending += 1
    return summary


def _compute_overall_status(summary: SessionSummary) -> str:
    """Compute overall session status from summary."""
    if summary.failed > 0 or summary.timeout > 0:
        return "failed"
    if summary.pending > 0:
        return "partial"
    if summary.passed > 0 and summary.failed == 0:
        return "passed"
    return "planned"
