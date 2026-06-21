"""Sandbox management for the reproduction orchestrator.

Provides isolated working directory creation and optional Docker sandbox
support.  The sandbox ensures that reproduction runs do not modify the
original repository and that all outputs are captured in a known location.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SandboxInfo:
    """Information about a sandbox environment."""

    sandbox_type: str = "local"  # local | docker | none
    run_dir: str = ""
    repo_copy: str = ""
    output_dir: str = ""
    docker_image: str = ""
    docker_available: bool = False
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sandbox_type": self.sandbox_type,
            "run_dir": self.run_dir,
            "repo_copy": self.repo_copy,
            "output_dir": self.output_dir,
            "docker_image": self.docker_image,
            "docker_available": self.docker_available,
            "error": self.error,
            "warnings": self.warnings,
        }


def create_local_sandbox(
    repo_path: str,
    output_dir: str | None = None,
    copy_files: bool = False,
) -> SandboxInfo:
    """Create a local sandbox for reproduction.

    Args:
        repo_path: Path to the source repository.
        output_dir: Explicit output directory. If None, creates a temp dir.
        copy_files: If True, copy repo files to the sandbox. If False,
            the sandbox only provides an isolated output directory.

    Returns:
        SandboxInfo with paths to the sandbox directories.
    """
    info = SandboxInfo(sandbox_type="local")
    repo_root = Path(repo_path).resolve()

    if not repo_root.exists():
        info.error = f"Repository path does not exist: {repo_path}"
        return info

    # Create or use the output directory
    if output_dir:
        run_dir = Path(output_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = Path(tempfile.mkdtemp(prefix="oss-paper-ci-repro-"))

    info.run_dir = str(run_dir)
    info.output_dir = str(run_dir / "outputs")
    Path(info.output_dir).mkdir(parents=True, exist_ok=True)

    if copy_files:
        info.repo_copy = str(run_dir / "repo")
        shutil.copytree(
            str(repo_root),
            info.repo_copy,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "venv", ".venv",
                "node_modules", ".oss-paper-ci-repro",
            ),
        )

    return info


def create_docker_sandbox(
    repo_path: str,
    output_dir: str | None = None,
    image: str = "python:3.11-slim",
    timeout: int = 300,
) -> SandboxInfo:
    """Create a Docker sandbox for reproduction.

    If Docker is not available, returns an error in SandboxInfo.

    Args:
        repo_path: Path to the source repository.
        output_dir: Explicit output directory for results.
        image: Docker image to use.
        timeout: Container timeout in seconds.

    Returns:
        SandboxInfo with Docker sandbox details.
    """
    info = SandboxInfo(sandbox_type="docker", docker_image=image)
    repo_root = Path(repo_path).resolve()

    if not repo_root.exists():
        info.error = f"Repository path does not exist: {repo_path}"
        return info

    # Check Docker availability
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            info.error = "Docker is not available or not running"
            info.warnings.append(
                "Docker sandbox requested but Docker is not available. "
                "Falling back to local sandbox."
            )
            info.sandbox_type = "local"
            return create_local_sandbox(repo_path, output_dir)
        info.docker_available = True
    except FileNotFoundError:
        info.error = "Docker command not found"
        info.warnings.append(
            "Docker sandbox requested but Docker is not installed. "
            "Falling back to local sandbox."
        )
        info.sandbox_type = "local"
        return create_local_sandbox(repo_path, output_dir)
    except subprocess.TimeoutExpired:
        info.error = "Docker version check timed out"
        info.sandbox_type = "local"
        return create_local_sandbox(repo_path, output_dir)

    # Create output directory
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
    else:
        out = Path(tempfile.mkdtemp(prefix="oss-paper-ci-docker-"))

    info.run_dir = str(out)
    info.output_dir = str(out / "outputs")
    Path(info.output_dir).mkdir(parents=True, exist_ok=True)

    return info


def get_sandbox(
    repo_path: str,
    sandbox_type: str = "local",
    output_dir: str | None = None,
    docker_image: str = "python:3.11-slim",
) -> SandboxInfo:
    """Get a sandbox of the requested type.

    Args:
        repo_path: Path to the source repository.
        sandbox_type: "local" or "docker".
        output_dir: Explicit output directory.
        docker_image: Docker image for docker sandbox.

    Returns:
        SandboxInfo for the requested sandbox type.
    """
    if sandbox_type == "docker":
        return create_docker_sandbox(
            repo_path,
            output_dir=output_dir,
            image=docker_image,
        )
    return create_local_sandbox(repo_path, output_dir=output_dir)


def write_run_manifest(
    run_dir: str,
    manifest: dict[str, Any],
) -> str:
    """Write a run manifest to the sandbox directory.

    Returns the path to the manifest file.
    """
    manifest_path = Path(run_dir) / "run-manifest.json"
    # Redact any absolute paths in the manifest
    redacted = _redact_absolute_paths(manifest)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(redacted, f, indent=2, ensure_ascii=False)
    return str(manifest_path)


def _redact_absolute_paths(obj: Any) -> Any:
    """Recursively redact absolute paths in a data structure."""
    if isinstance(obj, str):
        # Redact Windows and Unix absolute paths
        if len(obj) > 2 and obj[1] == ":" and obj[0].isalpha():
            return "<redacted>/" + Path(obj).name
        if obj.startswith("/") and len(obj) > 1:
            return "<redacted>/" + Path(obj).name
        return obj
    if isinstance(obj, dict):
        return {k: _redact_absolute_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact_absolute_paths(item) for item in obj]
    return obj
