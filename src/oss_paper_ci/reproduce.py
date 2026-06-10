"""One-command reproduction runner for oss-paper-ci.

Orchestrates the full reproduce workflow:
1. Resolve URL to source
2. Clone (if GitHub) or use local path
3. Detect environment and plan installation
4. Detect reproduction entry commands
5. Optionally create venv and install
6. Optionally run reproduction command(s)
7. Run oss-paper-ci scan on the repo
8. Generate reproduction report

Safety rules:
- Default to dry-run (no code execution)
- --execute required to run any commands
- --install required to install dependencies
- Dangerous command detection
- Timeout enforcement
- Workdir isolation
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci.environment import EnvironmentPlan, detect_environment
from oss_paper_ci.resolver import ResolvedSource, get_commit_sha, resolve_source
from oss_paper_ci.runner import DANGEROUS_PATTERNS, is_dangerous_command


@dataclass
class CommandResult:
    """Result of executing a single command."""

    command: str = ""
    exit_code: int = -1
    duration_seconds: float = 0.0
    timed_out: bool = False
    blocked: bool = False
    block_reason: str = ""
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "timed_out": self.timed_out,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
            "stdout_excerpt": self.stdout_excerpt,
            "stderr_excerpt": self.stderr_excerpt,
        }


@dataclass
class ReproduceResult:
    """Complete result of a reproduce attempt."""

    input_url: str = ""
    repo_url: str = ""
    paper_url: str = ""
    resolved_source: str = ""
    commit_sha: str = ""
    clone_ok: bool = False
    clone_error: str = ""
    environment: EnvironmentPlan | None = None
    install_results: list[CommandResult] = field(default_factory=list)
    reproduction_commands: list[str] = field(default_factory=list)
    command_results: list[CommandResult] = field(default_factory=list)
    generated_artifacts: list[str] = field(default_factory=list)
    scan_score: int = -1
    scan_status: str = "not_run"
    scan_findings_summary: str = ""
    limitations: list[str] = field(default_factory=list)
    dry_run: bool = True
    workdir: str = ""
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "input_url": self.input_url,
            "repo_url": self.repo_url,
            "paper_url": self.paper_url,
            "resolved_source": self.resolved_source,
            "commit_sha": self.commit_sha,
            "clone_ok": self.clone_ok,
            "clone_error": self.clone_error,
            "environment": self.environment.to_dict() if self.environment else None,
            "install_results": [r.to_dict() for r in self.install_results],
            "reproduction_commands": self.reproduction_commands,
            "command_results": [r.to_dict() for r in self.command_results],
            "generated_artifacts": self.generated_artifacts,
            "scan_score": self.scan_score,
            "scan_status": self.scan_status,
            "scan_findings_summary": self.scan_findings_summary,
            "limitations": self.limitations,
            "dry_run": self.dry_run,
            "workdir": self.workdir,
            "error": self.error,
            "warnings": self.warnings,
        }
        return result

    @property
    def ok(self) -> bool:
        """True if the reproduce attempt completed without fatal errors."""
        if self.error:
            return False
        if not self.clone_ok:
            return False
        if self.command_results:
            return all(r.exit_code == 0 for r in self.command_results)
        return True


_MAX_EXCERPT = 4000


def _truncate(text: str, limit: int = _MAX_EXCERPT) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... ({len(text) - limit} chars truncated)"


# ---------------------------------------------------------------------------
# Reproduction entry detection
# ---------------------------------------------------------------------------

def detect_reproduction_commands(
    repo_path: str,
    contract_path: str | None = None,
    config_path: str | None = None,
) -> list[str]:
    """Detect reproduction commands from various sources.

    Priority:
    1. reproducibility.yml experiments
    2. .oss-paper-ci.yml reproduce.commands
    3. Common script paths

    Returns:
        List of command strings (may be empty).
    """
    root = Path(repo_path)
    commands: list[str] = []

    # 1. Check reproducibility.yml
    from oss_paper_ci.runner import load_smoke_command

    contract_cmd = load_smoke_command(repo_path, contract_path=contract_path)
    if contract_cmd:
        commands.append(contract_cmd)
        return commands

    # 2. Check .oss-paper-ci.yml for reproduce.commands
    config_file = config_path
    if not config_file:
        for name in (".oss-paper-ci.yml", "oss-paper-ci.yml", ".oss-paper-ci.yaml"):
            candidate = root / name
            if candidate.exists():
                config_file = str(candidate)
                break

    if config_file:
        import yaml
        try:
            data = yaml.safe_load(Path(config_file).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                repro = data.get("reproduce", {})
                if isinstance(repro, dict):
                    cmds = repro.get("commands", [])
                    if isinstance(cmds, list) and cmds:
                        commands.extend(str(c) for c in cmds)
                        return commands
        except Exception:
            pass

    # 3. Common script paths
    common_scripts = [
        "scripts/run.sh",
        "scripts/reproduce.sh",
        "scripts/train.py",
        "scripts/evaluate.py",
        "scripts/make_figures.py",
    ]
    for script in common_scripts:
        if (root / script).exists():
            if script.endswith(".py"):
                commands.append(f"python {script}")
            else:
                commands.append(f"bash {script}")

    return commands


# ---------------------------------------------------------------------------
# Main reproduce function
# ---------------------------------------------------------------------------

def run_reproduce(
    url: str,
    *,
    repo_override: str | None = None,
    dry_run: bool = True,
    execute: bool = False,
    install: bool = False,
    command: str | None = None,
    workdir: str | None = None,
    timeout: int = 300,
    keep_workdir: bool = False,
) -> ReproduceResult:
    """Run the full reproduce workflow.

    Args:
        url: User-provided URL or path.
        repo_override: Explicit repo URL (--repo flag).
        dry_run: If True, show what would happen without executing.
        execute: If True, actually run commands (requires explicit opt-in).
        install: If True, install dependencies.
        command: Explicit reproduction command (--command flag).
        workdir: Explicit working directory.
        timeout: Per-command timeout in seconds.
        keep_workdir: If True, preserve working directory after run.

    Returns:
        ReproduceResult with full audit trail.
    """
    result = ReproduceResult(input_url=url, dry_run=dry_run)

    # Safety: if --execute is not set, force dry_run
    if not execute:
        dry_run = True
        result.dry_run = True

    # Step 1: Resolve source
    source = resolve_source(url, repo_override=repo_override)
    if not source.ok:
        result.error = source.error
        result.warnings = source.warnings
        return result

    result.repo_url = source.repo_url
    result.paper_url = source.paper_url
    result.resolved_source = source.source_type

    # Step 2: Prepare working directory
    temp_dir = None
    if workdir:
        repo_root = Path(workdir)
        repo_root.mkdir(parents=True, exist_ok=True)
    elif source.source_type == "local":
        repo_root = Path(source.local_path)
    else:
        # Create temp directory for clone
        temp_dir = tempfile.mkdtemp(prefix="oss-paper-ci-repro-")
        repo_root = Path(temp_dir)
        result.workdir = str(repo_root)

    if not result.workdir:
        result.workdir = str(repo_root)

    try:
        # Step 3: Clone if needed
        if source.source_type == "github" and source.clone_url:
            if dry_run:
                result.clone_ok = True
                result.warnings.append(
                    f"[dry-run] Would clone: {source.clone_url} -> {repo_root}"
                )
            else:
                clone_result = _run_command(
                    f"git clone --depth 1 {source.clone_url} {repo_root}",
                    cwd=str(repo_root.parent) if temp_dir else None,
                    timeout=120,
                )
                if clone_result.exit_code != 0:
                    result.clone_error = clone_result.stderr_excerpt or clone_result.block_reason
                    result.error = f"Failed to clone repository: {result.clone_error}"
                    return result
                result.clone_ok = True
        elif source.source_type == "local":
            result.clone_ok = True
        else:
            result.error = f"Unsupported source type: {source.source_type}"
            return result

        # Get commit SHA
        if result.clone_ok and not dry_run:
            result.commit_sha = get_commit_sha(str(repo_root))

        # Step 4: Detect environment
        result.environment = detect_environment(str(repo_root))

        # Step 5: Detect reproduction commands
        detected_cmds = detect_reproduction_commands(str(repo_root))
        if command:
            # User-specified command takes priority
            result.reproduction_commands = [command]
        elif detected_cmds:
            result.reproduction_commands = detected_cmds
        else:
            result.warnings.append(
                "No executable reproduction command detected. "
                "Use --command to specify one."
            )

        # Add limitations
        result.limitations = [
            "This report documents an attempted reproduction, not a successful one.",
            "Reproduction success does not guarantee correctness of results.",
            "Numerical results may differ due to hardware, software, or randomness.",
            "This tool does not verify scientific claims or paper quality.",
        ]

        # Step 6: Install (if requested and not dry-run)
        if install and result.environment and result.environment.install_steps:
            if dry_run:
                for step in result.environment.install_steps:
                    result.install_results.append(CommandResult(
                        command=step.command,
                        exit_code=0,
                        block_reason="dry_run",
                    ))
            else:
                # Create venv
                venv_path = repo_root / ".oss-paper-ci-repro" / "venv"
                venv_cmd = f"{sys.executable} -m venv {venv_path}"
                venv_result = _run_command(venv_cmd, cwd=str(repo_root), timeout=60)
                if venv_result.exit_code != 0:
                    result.warnings.append(
                        f"Failed to create virtual environment: {venv_result.stderr_excerpt}"
                    )
                else:
                    # Get pip path in venv
                    if sys.platform == "win32":
                        pip_exe = str(venv_path / "Scripts" / "pip.exe")
                        python_exe = str(venv_path / "Scripts" / "python.exe")
                    else:
                        pip_exe = str(venv_path / "bin" / "pip")
                        python_exe = str(venv_path / "bin" / "python")

                    for step in result.environment.install_steps:
                        # Build command using venv python
                        # Replace "python -m pip" or "pip" with venv equivalents
                        cmd = step.command
                        if "python -m pip" in cmd:
                            cmd = cmd.replace("python -m pip", f'"{python_exe}" -m pip')
                        elif cmd.startswith("pip "):
                            cmd = f'"{pip_exe}"' + cmd[3:]
                        install_result = _run_command(
                            cmd, cwd=str(repo_root), timeout=step.timeout
                        )
                        result.install_results.append(install_result)

        # Step 7: Run reproduction command(s)
        if result.reproduction_commands:
            if dry_run:
                for cmd in result.reproduction_commands:
                    result.command_results.append(CommandResult(
                        command=cmd,
                        exit_code=0,
                        block_reason="dry_run",
                    ))
            elif execute:
                for cmd in result.reproduction_commands:
                    if is_dangerous_command(cmd):
                        result.command_results.append(CommandResult(
                            command=cmd,
                            blocked=True,
                            block_reason="Command matches a dangerous pattern and was blocked.",
                        ))
                    else:
                        cmd_result = _run_command(
                            cmd, cwd=str(repo_root), timeout=timeout
                        )
                        result.command_results.append(cmd_result)

                        # Record generated artifacts
                        _record_artifacts(repo_root, result)

        # Step 8: Run oss-paper-ci scan
        if not dry_run and result.clone_ok:
            try:
                from oss_paper_ci.scanner import scan as run_scan
                from oss_paper_ci.reporting.json_report import generate_json_report

                scan_report = run_scan(str(repo_root))
                result.scan_score = scan_report.summary.score
                result.scan_status = scan_report.summary.status
                findings = scan_report.checks
                errors = sum(1 for c in findings if c.status.value == "fail")
                warnings = sum(1 for c in findings if c.status.value == "warn")
                passed = sum(1 for c in findings if c.status.value == "pass")
                result.scan_findings_summary = (
                    f"{passed} passed, {warnings} warnings, {errors} errors"
                )
            except Exception as exc:
                result.warnings.append(f"Scan failed: {exc}")
        elif dry_run:
            result.scan_status = "dry_run"

    finally:
        # Cleanup
        if temp_dir and not keep_workdir:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    return result


def _run_command(
    command: str,
    cwd: str | None = None,
    timeout: int = 300,
) -> CommandResult:
    """Run a shell command with timeout and output capture."""
    result = CommandResult(command=command)

    if is_dangerous_command(command):
        result.blocked = True
        result.block_reason = "Command matches a dangerous pattern and was blocked."
        return result

    start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result.exit_code = proc.returncode
        result.stdout_excerpt = _truncate(proc.stdout)
        result.stderr_excerpt = _truncate(proc.stderr)
    except subprocess.TimeoutExpired as exc:
        result.exit_code = -1
        result.timed_out = True
        result.block_reason = f"Command timed out after {timeout}s"
        if exc.stdout:
            result.stdout_excerpt = _truncate(
                exc.stdout.decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes) else exc.stdout
            )
        if exc.stderr:
            result.stderr_excerpt = _truncate(
                exc.stderr.decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes) else exc.stderr
            )
    except Exception as exc:
        result.exit_code = -1
        result.block_reason = f"Execution error: {exc}"

    result.duration_seconds = time.monotonic() - start
    return result


def _record_artifacts(repo_root: Path, result: ReproduceResult) -> None:
    """Record files generated during reproduction."""
    artifact_patterns = [
        "results/*.json",
        "results/*.csv",
        "figures/*.png",
        "figures/*.pdf",
        "figures/*.svg",
        "metrics.json",
        "output.*",
    ]
    seen = set(result.generated_artifacts)
    for pattern in artifact_patterns:
        for f in repo_root.glob(pattern):
            rel = str(f.relative_to(repo_root))
            if rel not in seen:
                result.generated_artifacts.append(rel)
                seen.add(rel)
