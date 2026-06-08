"""Safe smoke-test runner for oss-paper-ci.

Executes experiment smoke-test commands in a controlled manner with
dangerous-command detection, timeouts, and structured results.  The runner
is never invoked automatically -- it must be explicitly called.
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------

DANGEROUS_PATTERNS: list[str] = [
    "rm -rf /",
    "rm -rf /*",
    "format ",
    "del /s",
    "sudo ",
    "shutdown",
    "curl | sh",
    "curl |bash",
    "wget | sh",
    "wget | bash",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",   # fork bomb
    "> /dev/sd",
]

# Compiled once at import time for fast matching.
_DANGEROUS_RE = re.compile(
    "|".join(re.escape(p) for p in DANGEROUS_PATTERNS),
    re.IGNORECASE,
)


def is_dangerous_command(command: str) -> bool:
    """Return True if *command* matches any known dangerous pattern.

    The check is intentionally conservative -- false positives are preferred
    over false negatives.
    """
    return bool(_DANGEROUS_RE.search(command))


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

_MAX_EXCERPT = 2000  # characters kept from stdout/stderr


@dataclass
class SmokeResult:
    """Structured result of a single smoke-test run."""

    experiment_id: str = ""
    command: str = ""
    exit_code: int = -1
    duration_seconds: float = 0.0
    timed_out: bool = False
    blocked: bool = False
    block_reason: str = ""
    expected_outputs: list[dict[str, Any]] = field(default_factory=list)
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "command": self.command,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "timed_out": self.timed_out,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
            "expected_outputs": self.expected_outputs,
            "stdout_excerpt": self.stdout_excerpt,
            "stderr_excerpt": self.stderr_excerpt,
        }


def _truncate(text: str, limit: int = _MAX_EXCERPT) -> str:
    """Truncate *text* to at most *limit* characters."""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... ({len(text) - limit} chars truncated)"


# ---------------------------------------------------------------------------
# Contract loading
# ---------------------------------------------------------------------------

def load_smoke_command(
    repo_path: str,
    contract_path: str | None = None,
    experiment_id: str = "smoke",
) -> str | None:
    """Load the smoke command from a reproducibility contract YAML file.

    Args:
        repo_path: Repository root.
        contract_path: Explicit path to ``reproducibility.yml``.  If None,
            the runner looks for ``reproducibility.yml`` / ``.yml`` in the
            repo root.
        experiment_id: Which experiment entry to extract.

    Returns:
        The command string, or None if not found.
    """
    import yaml  # stdlib-ish; guaranteed by project deps

    root = Path(repo_path)

    if contract_path:
        candidates = [Path(contract_path)]
    else:
        candidates = [
            root / "reproducibility.yml",
            root / "reproducibility.yaml",
        ]

    for p in candidates:
        if not p.exists():
            continue
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue

        experiments = data.get("experiments")

        # If no explicit experiment_id, use ci.smoke_experiment
        actual_id = experiment_id
        if experiment_id == "smoke":
            ci_section = data.get("ci", {})
            if isinstance(ci_section, dict) and ci_section.get("smoke_experiment"):
                actual_id = ci_section["smoke_experiment"]

        # Handle both list and dict formats
        if isinstance(experiments, list):
            for exp in experiments:
                if isinstance(exp, dict) and exp.get("id") == actual_id and "command" in exp:
                    return str(exp["command"])
        elif isinstance(experiments, dict):
            exp = experiments.get(actual_id)
            if isinstance(exp, dict) and "command" in exp:
                return str(exp["command"])

    return None


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_smoke(
    repo_path: str,
    command: str,
    experiment_id: str = "smoke",
    timeout: int = 60,
    expected_outputs: list[str] | None = None,
    dry_run: bool = False,
) -> SmokeResult:
    """Run a smoke-test command safely.

    Safety rules:
    - Checks for dangerous patterns before execution.
    - Enforces a wall-clock timeout.
    - Sets working directory to the repo root.
    - Truncates captured stdout/stderr.
    - Always returns a structured result (never raises).

    Args:
        repo_path: Working directory for the command.
        command: Shell command string to execute.
        experiment_id: Label for this experiment run.
        timeout: Maximum seconds to wait (default 60).
        expected_outputs: Optional list of file paths (relative to repo root)
            that should exist after the command succeeds.
        dry_run: If True, report the command without executing it.

    Returns:
        SmokeResult with exit code, timing, and output excerpts.
    """
    result = SmokeResult(experiment_id=experiment_id, command=command)

    # --- Dry run ----------------------------------------------------------
    if dry_run:
        result.exit_code = 0
        result.block_reason = "dry_run"
        return result

    # --- Dangerous command check ------------------------------------------
    if is_dangerous_command(command):
        result.blocked = True
        result.block_reason = "Command matches a dangerous pattern and was blocked."
        result.exit_code = -1
        return result

    # --- Execute ----------------------------------------------------------
    repo_root = Path(repo_path).resolve()
    if not repo_root.exists():
        result.blocked = True
        result.block_reason = f"Repository path does not exist: {repo_path}"
        result.exit_code = -1
        return result

    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result.exit_code = proc.returncode
        result.stdout_excerpt = _truncate(proc.stdout)
        result.stderr_excerpt = _truncate(proc.stderr)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        result.exit_code = -1
        result.timed_out = True
        result.block_reason = f"Command timed out after {timeout}s"
        if exc.stdout:
            result.stdout_excerpt = _truncate(
                exc.stdout.decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else exc.stdout
            )
        if exc.stderr:
            result.stderr_excerpt = _truncate(
                exc.stderr.decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else exc.stderr
            )
    except Exception as exc:
        result.exit_code = -1
        result.block_reason = f"Execution error: {exc}"
    result.duration_seconds = time.monotonic() - start

    # --- Expected outputs check -------------------------------------------
    if expected_outputs:
        for rel_path in expected_outputs:
            output_path = repo_root / rel_path
            result.expected_outputs.append({
                "path": rel_path,
                "exists": output_path.exists(),
            })

    return result
