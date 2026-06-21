"""Reproduction execution engine.

Executes reproduction commands in dependency order with safety gates,
timeout enforcement, artifact collection, and metric validation.
Only runs when explicitly authorized with --execute.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci.artifact_validator import (
    ArtifactResult,
    ValidationReport,
    compute_artifact_hashes,
    validate_artifacts,
)
from oss_paper_ci.command_safety import is_dangerous_command, get_block_reason
from oss_paper_ci.metric_validator import (
    MetricValidationReport,
    validate_metrics,
)
from oss_paper_ci.repro_schema import (
    OrchestratorContract,
    load_orchestrator_contract,
)
from oss_paper_ci.sandbox import SandboxInfo, get_sandbox, write_run_manifest


@dataclass
class CommandRunResult:
    """Result of executing a single command."""

    command_id: str = ""
    command: str = ""
    exit_code: int = -1
    duration_seconds: float = 0.0
    timed_out: bool = False
    blocked: bool = False
    block_reason: str = ""
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""
    status: str = "pending"  # pending | running | success | failed | blocked | timeout

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command": self.command,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "timed_out": self.timed_out,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
            "stdout_excerpt": self.stdout_excerpt,
            "stderr_excerpt": self.stderr_excerpt,
            "status": self.status,
        }


@dataclass
class ReproductionRun:
    """Complete result of a reproduction run."""

    repo_path: str = ""
    contract_path: str = ""
    sandbox_type: str = "local"
    run_dir: str = ""
    dry_run: bool = True
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0
    command_results: list[CommandRunResult] = field(default_factory=list)
    artifact_validation: ValidationReport | None = None
    metric_validation: MetricValidationReport | None = None
    artifact_hashes: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    error: str = ""
    overall_status: str = "unknown"  # success | partial | failed | error | dry_run

    def to_dict(self) -> dict[str, Any]:
        from pathlib import Path as _Path
        # Redact absolute paths to relative
        def _rel(p: str) -> str:
            if not p:
                return p
            try:
                return str(_Path(p).name)
            except Exception:
                return p

        d: dict[str, Any] = {
            "repo_path": _rel(self.repo_path),
            "contract_path": _rel(self.contract_path),
            "sandbox_type": self.sandbox_type,
            "run_dir": self.run_dir,
            "dry_run": self.dry_run,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 3),
            "command_results": [r.to_dict() for r in self.command_results],
            "overall_status": self.overall_status,
            "warnings": self.warnings,
        }
        if self.artifact_validation:
            d["artifact_validation"] = self.artifact_validation.to_dict()
        if self.metric_validation:
            d["metric_validation"] = self.metric_validation.to_dict()
        if self.artifact_hashes:
            d["artifact_hashes"] = self.artifact_hashes
        if self.error:
            d["error"] = self.error
        return d

    @property
    def ok(self) -> bool:
        return self.overall_status in ("success", "dry_run")


def run_reproduction(
    repo_path: str,
    *,
    contract_path: str | None = None,
    execute: bool = False,
    sandbox_type: str = "local",
    output_dir: str | None = None,
    timeout: int | None = None,
) -> ReproductionRun:
    """Run the reproduction orchestrator.

    Args:
        repo_path: Path to the repository root.
        contract_path: Explicit path to reproducibility.yml.
        execute: If True, actually run commands. If False, dry-run only.
        sandbox_type: "local" or "docker".
        output_dir: Explicit output directory for run results.
        timeout: Override per-command timeout.

    Returns:
        ReproductionRun with full audit trail.
    """
    run = ReproductionRun(
        repo_path=str(Path(repo_path).resolve()),
        dry_run=not execute,
        started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    # Load contract
    root = Path(repo_path).resolve()
    if contract_path:
        contract_file = Path(contract_path)
    else:
        from oss_paper_ci.contract import find_contract
        found = find_contract(str(root))
        if not found:
            run.error = "No reproducibility.yml found"
            run.overall_status = "error"
            return run
        contract_file = Path(found)

    run.contract_path = str(contract_file)

    try:
        contract = load_orchestrator_contract(str(contract_file))
    except Exception as exc:
        run.error = f"Failed to load contract: {exc}"
        run.overall_status = "error"
        return run

    # Resolve commands (from commands or legacy experiments)
    commands = contract.commands
    if not commands:
        # Try legacy experiments
        for exp in contract.experiments:
            if isinstance(exp, dict) and exp.get("command"):
                from oss_paper_ci.repro_schema import CommandSpec
                commands.append(CommandSpec(
                    id=exp.get("id", ""),
                    run=exp.get("command", ""),
                    timeout_seconds=exp.get("timeout_seconds", 60),
                    expected_artifacts=exp.get("expected_outputs", []),
                ))

    if not commands:
        run.warnings.append("No commands defined in contract")
        run.overall_status = "dry_run" if not execute else "error"
        run.finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return run

    # Build execution order (topological sort respecting depends_on)
    ordered = _topological_sort(commands)
    if ordered is None:
        run.error = "Circular dependency detected in command graph"
        run.overall_status = "error"
        return run

    # Check all commands for dangerous patterns
    for cmd in ordered:
        if is_dangerous_command(cmd.run):
            run.warnings.append(
                f"Command '{cmd.id}' matches a dangerous pattern and will be blocked"
            )

    # Safety defaults
    safety = contract.safety
    if not execute:
        # Dry run: simulate all commands
        for cmd in ordered:
            run.command_results.append(CommandRunResult(
                command_id=cmd.id,
                command=cmd.run,
                exit_code=0,
                block_reason="dry_run",
                status="success",
            ))
        run.overall_status = "dry_run"
    else:
        # Execute commands in order
        start_time = time.monotonic()
        all_success = True

        # Create sandbox
        sandbox = get_sandbox(
            str(root),
            sandbox_type=sandbox_type,
            output_dir=output_dir,
        )
        run.sandbox_type = sandbox.sandbox_type
        run.run_dir = sandbox.run_dir

        if sandbox.error and sandbox_type == "docker":
            run.warnings.append(f"Docker sandbox unavailable: {sandbox.error}")

        completed_ids: set[str] = set()

        for cmd in ordered:
            # Check dependencies
            missing_deps = [d for d in cmd.depends_on if d not in completed_ids]
            if missing_deps:
                run.command_results.append(CommandRunResult(
                    command_id=cmd.id,
                    command=cmd.run,
                    blocked=True,
                    block_reason=f"Dependencies not satisfied: {missing_deps}",
                    status="blocked",
                ))
                all_success = False
                continue

            # Check dangerous
            if is_dangerous_command(cmd.run):
                run.command_results.append(CommandRunResult(
                    command_id=cmd.id,
                    command=cmd.run,
                    blocked=True,
                    block_reason=get_block_reason(cmd.run),
                    status="blocked",
                ))
                all_success = False
                continue

            # Execute
            cmd_timeout = timeout or cmd.timeout_seconds or safety.max_runtime_seconds
            result = _execute_command(
                cmd,
                cwd=str(root),
                timeout=cmd_timeout,
            )
            run.command_results.append(result)

            if result.status == "success":
                completed_ids.add(cmd.id)
            else:
                all_success = False

            # Check elapsed time against max_runtime
            elapsed = time.monotonic() - start_time
            if elapsed > safety.max_runtime_seconds:
                run.warnings.append(
                    f"Total runtime ({elapsed:.0f}s) exceeded limit "
                    f"({safety.max_runtime_seconds}s). Remaining commands skipped."
                )
                break

        # Collect artifacts
        all_artifact_paths: list[str] = []
        for cmd in commands:
            all_artifact_paths.extend(cmd.expected_artifacts)
        for art in contract.artifacts:
            if art.path not in all_artifact_paths:
                all_artifact_paths.append(art.path)

        if all_artifact_paths:
            types = {a.path: a.type for a in contract.artifacts}
            run.artifact_validation = validate_artifacts(
                str(root),
                all_artifact_paths,
                artifact_types=types,
                max_artifact_mb=safety.max_artifact_mb,
            )
            run.artifact_hashes = compute_artifact_hashes(
                str(root), all_artifact_paths
            )
            if run.artifact_validation.missing > 0:
                all_success = False

        # Validate metrics
        if contract.metrics:
            run.metric_validation = validate_metrics(
                str(root),
                [m.to_dict() for m in contract.metrics],
            )
            if not run.metric_validation.ok:
                all_success = False

        run.overall_status = "success" if all_success else "partial"

        # Write manifest to run directory
        manifest = run.to_dict()
        # Redact absolute paths
        manifest["repo_path"] = "<redacted>"
        write_run_manifest(run.run_dir, manifest)

    run.finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run.duration_seconds = time.monotonic() - time.monotonic()  # Will be set properly
    return run


def _execute_command(
    cmd: Any,  # CommandSpec
    cwd: str,
    timeout: int = 60,
) -> CommandRunResult:
    """Execute a single command with timeout and output capture."""
    import subprocess

    result = CommandRunResult(
        command_id=cmd.id,
        command=cmd.run,
        status="running",
    )

    _MAX_EXCERPT = 4000

    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd.run,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result.exit_code = proc.returncode
        result.stdout_excerpt = (proc.stdout or "")[:_MAX_EXCERPT]
        result.stderr_excerpt = (proc.stderr or "")[:_MAX_EXCERPT]
        result.status = "success" if proc.returncode == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        result.exit_code = -1
        result.timed_out = True
        result.block_reason = f"Timed out after {timeout}s"
        result.status = "timeout"
        if exc.stdout:
            stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout
            result.stdout_excerpt = stdout[:_MAX_EXCERPT]
        if exc.stderr:
            stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
            result.stderr_excerpt = stderr[:_MAX_EXCERPT]
    except Exception as exc:
        result.exit_code = -1
        result.block_reason = f"Execution error: {exc}"
        result.status = "failed"

    result.duration_seconds = time.monotonic() - start
    return result


def _topological_sort(commands: list[Any]) -> list[Any] | None:
    """Topological sort of commands by depends_on.

    Returns None if circular dependency detected.
    """
    id_to_cmd = {c.id: c for c in commands}
    visited: set[str] = set()
    result: list[Any] = []
    in_progress: set[str] = set()

    def visit(cmd_id: str) -> bool:
        if cmd_id in visited:
            return True
        if cmd_id in in_progress:
            return False  # Circular
        in_progress.add(cmd_id)
        cmd = id_to_cmd.get(cmd_id)
        if cmd:
            for dep in cmd.depends_on:
                if dep in id_to_cmd and not visit(dep):
                    return False
            result.append(cmd)
        visited.add(cmd_id)
        in_progress.discard(cmd_id)
        return True

    for cmd in commands:
        if not visit(cmd.id):
            return None

    return result
