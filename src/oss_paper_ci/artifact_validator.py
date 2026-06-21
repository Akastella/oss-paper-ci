"""Artifact validation for the reproduction orchestrator.

Validates that expected artifacts exist after command execution,
computes SHA256 hashes for integrity verification, and checks
artifact sizes against safety limits.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ArtifactResult:
    """Result of validating a single artifact."""

    path: str = ""
    exists: bool = False
    size_bytes: int = 0
    sha256: str = ""
    type: str = "file"
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "path": self.path,
            "exists": self.exists,
            "size_bytes": self.size_bytes,
            "type": self.type,
        }
        if self.sha256:
            d["sha256"] = self.sha256
        if self.error:
            d["error"] = self.error
        return d


@dataclass
class ValidationReport:
    """Report of artifact validation."""

    total: int = 0
    found: int = 0
    missing: int = 0
    artifacts: list[ArtifactResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "found": self.found,
            "missing": self.missing,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "warnings": self.warnings,
        }

    @property
    def ok(self) -> bool:
        return self.missing == 0 and not self.warnings


def validate_artifacts(
    repo_path: str,
    expected_paths: list[str],
    artifact_types: dict[str, str] | None = None,
    max_artifact_mb: int = 20,
) -> ValidationReport:
    """Validate that expected artifacts exist in the repository.

    Args:
        repo_path: Root directory of the repository.
        expected_paths: List of expected artifact paths (relative to repo root).
        artifact_types: Optional mapping of path -> type string.
        max_artifact_mb: Maximum artifact size in MB.

    Returns:
        ValidationReport with per-artifact results.
    """
    root = Path(repo_path)
    report = ValidationReport(total=len(expected_paths))
    types = artifact_types or {}

    for rel_path in expected_paths:
        artifact = ArtifactResult(
            path=rel_path,
            type=types.get(rel_path, "file"),
        )
        full_path = root / rel_path

        if full_path.exists():
            artifact.exists = True
            try:
                stat = full_path.stat()
                artifact.size_bytes = stat.st_size
                artifact.sha256 = _hash_file(full_path)

                size_mb = stat.st_size / (1024 * 1024)
                if size_mb > max_artifact_mb:
                    report.warnings.append(
                        f"Artifact '{rel_path}' is {size_mb:.1f} MB "
                        f"(limit: {max_artifact_mb} MB)"
                    )
            except Exception as exc:
                artifact.error = f"Failed to stat/hash: {exc}"
            report.found += 1
        else:
            report.missing += 1

        report.artifacts.append(artifact)

    return report


def compute_artifact_hashes(
    repo_path: str,
    artifact_paths: list[str],
) -> dict[str, str]:
    """Compute SHA256 hashes for a list of artifacts.

    Returns:
        Dict mapping relative path to hex digest. Missing files are omitted.
    """
    root = Path(repo_path)
    hashes: dict[str, str] = {}
    for rel_path in artifact_paths:
        full_path = root / rel_path
        if full_path.exists() and full_path.is_file():
            hashes[rel_path] = _hash_file(full_path)
    return hashes


def _hash_file(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
