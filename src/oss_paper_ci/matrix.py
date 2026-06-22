"""Matrix execution: run reproduction across multiple configurations.

Supports environment matrix (Python versions), profile matrix (lenient/strict),
and config matrix. Does not auto-install runtimes; marks missing runtimes as
unavailable.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci import __version__
from oss_paper_ci.session import SessionManifest, create_session, execute_session


@dataclass
class MatrixVariant:
    """A single variant in a matrix run."""

    variant_id: str = ""
    python_version: str = ""
    profile: str = ""
    config: str = ""
    available: bool = True
    session_dir: str = ""
    status: str = "pending"  # pending | running | passed | failed | unavailable

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant_id": self.variant_id,
            "python_version": self.python_version,
            "profile": self.profile,
            "config": self.config,
            "available": self.available,
            "session_dir": self.session_dir,
            "status": self.status,
        }


@dataclass
class MatrixPlan:
    """Plan for a matrix execution."""

    schema_version: str = "0.1"
    report_type: str = "oss-paper-ci-matrix-plan"
    tool_version: str = ""
    repo: str = ""
    config: str = ""
    variants: list[MatrixVariant] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_type": self.report_type,
            "tool_version": self.tool_version,
            "repo": self.repo,
            "config": self.config,
            "variants": [v.to_dict() for v in self.variants],
            "warnings": self.warnings,
        }


@dataclass
class MatrixResult:
    """Result of a matrix execution."""

    schema_version: str = "0.1"
    report_type: str = "oss-paper-ci-matrix-result"
    tool_version: str = ""
    repo: str = ""
    config: str = ""
    variants: list[MatrixVariant] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_type": self.report_type,
            "tool_version": self.tool_version,
            "repo": self.repo,
            "config": self.config,
            "variants": [v.to_dict() for v in self.variants],
            "summary": self.summary,
            "warnings": self.warnings,
        }


def plan_matrix(
    repo_path: str,
    config_path: str | None = None,
    python_versions: list[str] | None = None,
    profiles: list[str] | None = None,
) -> MatrixPlan:
    """Plan a matrix execution.

    Args:
        repo_path: Path to the repository.
        config_path: Path to reproducibility.yml.
        python_versions: List of Python versions to test.
        profiles: List of profiles to test.

    Returns:
        MatrixPlan with variants.
    """
    plan = MatrixPlan(
        tool_version=__version__,
        repo=repo_path,
        config=config_path or "",
    )

    # Default to current Python version
    if not python_versions and not profiles:
        python_versions = [f"{sys.version_info.major}.{sys.version_info.minor}"]

    # Generate variants
    if python_versions:
        for ver in python_versions:
            available = _check_python_available(ver)
            variant = MatrixVariant(
                variant_id=f"python-{ver}",
                python_version=ver,
                available=available,
                status="unavailable" if not available else "pending",
            )
            if not available:
                plan.warnings.append(f"Python {ver} not available on this system")
            plan.variants.append(variant)

    if profiles:
        for profile in profiles:
            variant = MatrixVariant(
                variant_id=f"profile-{profile}",
                profile=profile,
                available=True,
                status="pending",
            )
            plan.variants.append(variant)

    return plan


def run_matrix(
    plan: MatrixPlan,
    output_dir: str | None = None,
    execute: bool = False,
) -> MatrixResult:
    """Execute a matrix plan.

    Args:
        plan: The matrix plan to execute.
        output_dir: Base output directory for matrix results.
        execute: If True, actually run commands. If False, dry-run only.

    Returns:
        MatrixResult with execution results.
    """
    base_dir = Path(output_dir) if output_dir else Path(".oss-paper-ci-matrix")
    base_dir.mkdir(parents=True, exist_ok=True)

    result = MatrixResult(
        tool_version=plan.tool_version,
        repo=plan.repo,
        config=plan.config,
    )

    for variant in plan.variants:
        if not variant.available:
            variant.status = "unavailable"
            result.variants.append(variant)
            continue

        # Create session for this variant
        session_name = f"matrix-{variant.variant_id}"
        session_dir = base_dir / variant.variant_id

        manifest = create_session(
            repo_path=plan.repo,
            config_path=plan.config or None,
            name=session_name,
        )

        variant.session_dir = str(session_dir)

        if execute:
            manifest = execute_session(manifest)
            variant.status = manifest.status
        else:
            variant.status = "planned"

        # Save session
        from oss_paper_ci.session_store import save_session
        save_session(manifest, str(session_dir))

        result.variants.append(variant)

    # Compute summary
    result.summary = {
        "total": len(result.variants),
        "passed": sum(1 for v in result.variants if v.status == "passed"),
        "failed": sum(1 for v in result.variants if v.status == "failed"),
        "unavailable": sum(1 for v in result.variants if v.status == "unavailable"),
        "planned": sum(1 for v in result.variants if v.status == "planned"),
    }

    return result


def _check_python_available(version: str) -> bool:
    """Check if a Python version is available on this system."""
    # Try common Python commands
    for cmd in [f"python{version}", f"python{version}.exe"]:
        if shutil.which(cmd):
            return True
    # Check if current python matches
    current = f"{sys.version_info.major}.{sys.version_info.minor}"
    if current == version:
        return True
    return False
