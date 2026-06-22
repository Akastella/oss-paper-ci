"""Session persistence: save and load session manifests.

Manages the session directory layout:
  .oss-paper-ci-sessions/<name>/
    session.json
    plan.json
    runs/<command_id>/
      stdout.txt
      stderr.txt
      command.json
    reports/
      session.md
      session.json
      session.html
    SHA256SUMS
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from oss_paper_ci.session import SessionManifest, SessionCommand, SessionSummary


def save_session(manifest: SessionManifest, output_dir: str) -> str:
    """Save a session manifest to a directory.

    Args:
        manifest: The session manifest to save.
        output_dir: Directory to save the session.

    Returns:
        Path to the saved session directory.
    """
    session_dir = Path(output_dir)
    session_dir.mkdir(parents=True, exist_ok=True)

    # Save session manifest
    session_path = session_dir / "session.json"
    session_path.write_text(
        json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Save plan (commands to execute)
    plan_dir = session_dir / "plan.json"
    plan_data = {
        "schema_version": "0.1",
        "session_id": manifest.session_id,
        "commands": [
            {
                "command_id": c.command_id,
                "command": c.command,
                "status": c.status,
                "block_reason": c.block_reason,
            }
            for c in manifest.commands
        ],
    }
    plan_dir.write_text(
        json.dumps(plan_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Create runs directory
    runs_dir = session_dir / "runs"
    runs_dir.mkdir(exist_ok=True)

    # Create per-command directories
    for cmd in manifest.commands:
        cmd_dir = runs_dir / cmd.command_id
        cmd_dir.mkdir(exist_ok=True)

        # Save command metadata
        cmd_json = cmd_dir / "command.json"
        cmd_json.write_text(
            json.dumps(cmd.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Create empty stdout/stderr if not exists
        stdout_file = cmd_dir / "stdout.txt"
        stderr_file = cmd_dir / "stderr.txt"
        if not stdout_file.exists():
            stdout_file.write_text("", encoding="utf-8")
        if not stderr_file.exists():
            stderr_file.write_text("", encoding="utf-8")

    return str(session_dir)


def load_session(session_dir: str) -> SessionManifest:
    """Load a session manifest from a directory.

    Args:
        session_dir: Path to the session directory.

    Returns:
        SessionManifest loaded from the directory.

    Raises:
        FileNotFoundError: If session.json not found.
    """
    session_path = Path(session_dir) / "session.json"
    if not session_path.exists():
        raise FileNotFoundError(f"Session not found: {session_path}")

    data = json.loads(session_path.read_text(encoding="utf-8"))
    return _dict_to_manifest(data)


def list_sessions(base_dir: str) -> list[dict[str, Any]]:
    """List all sessions in a base directory.

    Args:
        base_dir: Base sessions directory.

    Returns:
        List of session info dicts.
    """
    sessions: list[dict[str, Any]] = []
    base = Path(base_dir)

    if not base.exists():
        return sessions

    for d in sorted(base.iterdir()):
        if d.is_dir():
            session_json = d / "session.json"
            if session_json.exists():
                try:
                    data = json.loads(session_json.read_text(encoding="utf-8"))
                    sessions.append({
                        "name": data.get("name", d.name),
                        "session_id": data.get("session_id", ""),
                        "status": data.get("status", "unknown"),
                        "path": str(d),
                        "command_count": len(data.get("commands", [])),
                        "summary": data.get("summary", {}),
                    })
                except Exception:
                    sessions.append({
                        "name": d.name,
                        "status": "error",
                        "path": str(d),
                    })

    return sessions


def update_command_status(
    session_dir: str,
    command_id: str,
    status: str,
    exit_code: int = -1,
    duration_seconds: float = 0.0,
    stdout: str = "",
    stderr: str = "",
    artifacts: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
) -> None:
    """Update the status of a command in a session.

    Args:
        session_dir: Path to the session directory.
        command_id: ID of the command to update.
        status: New status.
        exit_code: Exit code.
        duration_seconds: Duration in seconds.
        stdout: Standard output.
        stderr: Standard error.
        artifacts: List of artifact paths.
        metrics: Metrics dict.
        warnings: List of warnings.
    """
    session_path = Path(session_dir) / "session.json"
    if not session_path.exists():
        return

    data = json.loads(session_path.read_text(encoding="utf-8"))

    # Update command in commands list
    for cmd in data.get("commands", []):
        if cmd.get("command_id") == command_id:
            cmd["status"] = status
            cmd["exit_code"] = exit_code
            cmd["duration_seconds"] = round(duration_seconds, 3)
            if artifacts is not None:
                cmd["artifacts"] = artifacts
            if metrics is not None:
                cmd["metrics"] = metrics
            if warnings is not None:
                cmd["warnings"] = warnings
            cmd["attempts"] = cmd.get("attempts", 0) + (1 if status in ("passed", "failed", "timeout") else 0)
            break

    # Update summary
    commands = data.get("commands", [])
    summary = {"total": len(commands)}
    for key in ("passed", "failed", "blocked", "timeout", "skipped", "unavailable", "pending"):
        summary[key] = sum(1 for c in commands if c.get("status") == key)
    data["summary"] = summary

    # Update overall status
    if summary["failed"] > 0 or summary["timeout"] > 0:
        data["status"] = "failed"
    elif summary["pending"] > 0:
        data["status"] = "partial"
    elif summary["passed"] > 0:
        data["status"] = "passed"

    # Save
    session_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Save stdout/stderr
    cmd_dir = Path(session_dir) / "runs" / command_id
    cmd_dir.mkdir(parents=True, exist_ok=True)
    if stdout:
        (cmd_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
    if stderr:
        (cmd_dir / "stderr.txt").write_text(stderr, encoding="utf-8")

    # Save command metadata
    cmd_data = next((c for c in commands if c.get("command_id") == command_id), None)
    if cmd_data:
        (cmd_dir / "command.json").write_text(
            json.dumps(cmd_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def compute_session_checksums(session_dir: str) -> dict[str, str]:
    """Compute SHA256 checksums for all files in a session directory.

    Args:
        session_dir: Path to the session directory.

    Returns:
        Dict mapping relative paths to SHA256 hex digests.
    """
    checksums: dict[str, str] = {}
    base = Path(session_dir)

    for f in sorted(base.rglob("*")):
        if f.is_file() and f.name != "SHA256SUMS":
            rel = str(f.relative_to(base))
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            checksums[rel] = h

    return checksums


def save_checksums(session_dir: str) -> str:
    """Save SHA256SUMS file for a session directory.

    Args:
        session_dir: Path to the session directory.

    Returns:
        Path to the SHA256SUMS file.
    """
    checksums = compute_session_checksums(session_dir)
    lines = [f"{hash}  {path}" for path, hash in sorted(checksums.items())]
    checksum_path = Path(session_dir) / "SHA256SUMS"
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(checksum_path)


def _dict_to_manifest(data: dict[str, Any]) -> SessionManifest:
    """Convert a dict to a SessionManifest."""
    commands = []
    for c in data.get("commands", []):
        commands.append(SessionCommand(
            command_id=c.get("command_id", ""),
            command=c.get("command", ""),
            status=c.get("status", "pending"),
            exit_code=c.get("exit_code", -1),
            duration_seconds=c.get("duration_seconds", 0.0),
            block_reason=c.get("block_reason", ""),
            attempts=c.get("attempts", 0),
            artifacts=c.get("artifacts", []),
            metrics=c.get("metrics", {}),
            warnings=c.get("warnings", []),
        ))

    summary_data = data.get("summary", {})
    summary = SessionSummary(
        total=summary_data.get("total", 0),
        passed=summary_data.get("passed", 0),
        failed=summary_data.get("failed", 0),
        blocked=summary_data.get("blocked", 0),
        timeout=summary_data.get("timeout", 0),
        skipped=summary_data.get("skipped", 0),
        unavailable=summary_data.get("unavailable", 0),
        pending=summary_data.get("pending", 0),
    )

    return SessionManifest(
        schema_version=data.get("schema_version", "0.1"),
        report_type=data.get("report_type", "oss-paper-ci-reproduction-session"),
        tool_version=data.get("tool_version", ""),
        session_id=data.get("session_id", ""),
        name=data.get("name", ""),
        repo=data.get("repo", ""),
        config=data.get("config", ""),
        status=data.get("status", "planned"),
        commands=commands,
        summary=summary,
        limitations=data.get("limitations", []),
        warnings=data.get("warnings", []),
    )
