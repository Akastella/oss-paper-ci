"""Run history tracking for reproduction sessions.

Tracks attempts, durations, and status changes across session runs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RunAttempt:
    """A single attempt at running a command."""

    attempt_number: int = 0
    status: str = "pending"
    exit_code: int = -1
    duration_seconds: float = 0.0
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_number": self.attempt_number,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "stdout_excerpt": self.stdout_excerpt[:500],
            "stderr_excerpt": self.stderr_excerpt[:500],
        }


@dataclass
class CommandHistory:
    """History of attempts for a single command."""

    command_id: str = ""
    command: str = ""
    attempts: list[RunAttempt] = field(default_factory=list)
    current_status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command": self.command,
            "attempts": [a.to_dict() for a in self.attempts],
            "current_status": self.current_status,
        }

    @property
    def total_attempts(self) -> int:
        return len(self.attempts)

    @property
    def last_attempt(self) -> RunAttempt | None:
        return self.attempts[-1] if self.attempts else None

    @property
    def best_duration(self) -> float:
        passed = [a for a in self.attempts if a.status == "passed"]
        return min(a.duration_seconds for a in passed) if passed else 0.0


def record_attempt(
    history_dir: str,
    command_id: str,
    command: str,
    status: str,
    exit_code: int = -1,
    duration_seconds: float = 0.0,
    stdout: str = "",
    stderr: str = "",
) -> RunAttempt:
    """Record a run attempt in the history.

    Args:
        history_dir: Path to the command's history directory.
        command_id: ID of the command.
        command: The command string.
        status: Result status.
        exit_code: Exit code.
        duration_seconds: Duration in seconds.
        stdout: Standard output.
        stderr: Standard error.

    Returns:
        The recorded RunAttempt.
    """
    history_path = Path(history_dir)
    history_path.mkdir(parents=True, exist_ok=True)

    # Load existing history
    history_file = history_path / "history.json"
    if history_file.exists():
        data = json.loads(history_file.read_text(encoding="utf-8"))
        history = CommandHistory(
            command_id=data.get("command_id", command_id),
            command=data.get("command", command),
            attempts=[
                RunAttempt(
                    attempt_number=a.get("attempt_number", 0),
                    status=a.get("status", "pending"),
                    exit_code=a.get("exit_code", -1),
                    duration_seconds=a.get("duration_seconds", 0.0),
                    stdout_excerpt=a.get("stdout_excerpt", ""),
                    stderr_excerpt=a.get("stderr_excerpt", ""),
                )
                for a in data.get("attempts", [])
            ],
            current_status=data.get("current_status", "pending"),
        )
    else:
        history = CommandHistory(command_id=command_id, command=command)

    # Create new attempt
    attempt = RunAttempt(
        attempt_number=len(history.attempts) + 1,
        status=status,
        exit_code=exit_code,
        duration_seconds=duration_seconds,
        stdout_excerpt=stdout[:500],
        stderr_excerpt=stderr[:500],
    )

    history.attempts.append(attempt)
    history.current_status = status

    # Save
    history_file.write_text(
        json.dumps(history.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return attempt


def load_command_history(history_dir: str) -> CommandHistory:
    """Load command history from a directory.

    Args:
        history_dir: Path to the command's history directory.

    Returns:
        CommandHistory object.
    """
    history_file = Path(history_dir) / "history.json"
    if not history_file.exists():
        return CommandHistory()

    data = json.loads(history_file.read_text(encoding="utf-8"))
    return CommandHistory(
        command_id=data.get("command_id", ""),
        command=data.get("command", ""),
        attempts=[
            RunAttempt(
                attempt_number=a.get("attempt_number", 0),
                status=a.get("status", "pending"),
                exit_code=a.get("exit_code", -1),
                duration_seconds=a.get("duration_seconds", 0.0),
                stdout_excerpt=a.get("stdout_excerpt", ""),
                stderr_excerpt=a.get("stderr_excerpt", ""),
            )
            for a in data.get("attempts", [])
        ],
        current_status=data.get("current_status", "pending"),
    )
