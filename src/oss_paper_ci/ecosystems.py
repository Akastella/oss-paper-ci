"""Language ecosystem detection for multi-language research repositories.

Delegates to the AdapterRegistry for language detection and planning.
Provides backward-compatible API for existing callers (evidence.py, etc.).

Support levels:
- native: fully supported (Python)
- execute-if-runtime-present: can execute if runtime is installed (R, Julia, etc.)
- dry-run: can detect and plan, but cannot execute (MATLAB, Snakemake, Nextflow)
- detect-only: can only detect presence (unsupported combinations)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .adapters.registry import get_registry


# Mapping from adapter ecosystem to support level
_SUPPORT_LEVEL_MAP = {
    "native": "native",
    "scripting": "execute-if-runtime-present",
    "compiled": "execute-if-runtime-present",
    "workflow": "dry-run",
    "numerical": "dry-run",
}


# Backward-compatible ECOSYSTEMS dict (deprecated: use AdapterRegistry instead)
def _build_ecosystems_dict() -> dict[str, dict[str, Any]]:
    """Build backward-compatible ECOSYSTEMS dict from adapter registry."""
    registry = get_registry()
    result = {}
    for adapter_info in registry.list_adapters():
        name = adapter_info["name"]
        adapter = registry.get(name)
        if adapter:
            result[name] = {
                "display_name": adapter.display_name,
                "environment_files": [],
                "entrypoint_candidates": [],
                "runtime_required": adapter.requires_runtime[0] if adapter.requires_runtime else "",
                "support_level": _SUPPORT_LEVEL_MAP.get(adapter.ecosystem, "detect-only"),
                "limitations": [],
                "safety_notes": [],
            }
    return result


ECOSYSTEMS: dict[str, dict[str, Any]] = _build_ecosystems_dict()


@dataclass
class LanguageEcosystem:
    """A detected language ecosystem."""

    id: str
    display_name: str
    detected_files: list[str] = field(default_factory=list)
    environment_files: list[str] = field(default_factory=list)
    entrypoint_candidates: list[str] = field(default_factory=list)
    install_plan: list[str] = field(default_factory=list)
    run_plan: list[str] = field(default_factory=list)
    runtime_required: str = ""
    runtime_available: bool = False
    support_level: str = "detect-only"  # native, execute-if-runtime-present, dry-run, detect-only
    limitations: list[str] = field(default_factory=list)
    safety_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "detected_files": self.detected_files,
            "environment_files": self.environment_files,
            "entrypoint_candidates": self.entrypoint_candidates,
            "install_plan": self.install_plan,
            "run_plan": self.run_plan,
            "runtime_required": self.runtime_required,
            "runtime_available": self.runtime_available,
            "support_level": self.support_level,
            "limitations": self.limitations,
            "safety_notes": self.safety_notes,
        }


def _adapter_to_ecosystem(detection, adapter) -> LanguageEcosystem:
    """Convert an AdapterDetection to a LanguageEcosystem for backward compatibility."""
    # Get the adapter's plan for install/run steps
    install_plan = []
    run_plan = []
    try:
        plan = adapter.plan(Path("."))  # dummy path for plan extraction
        install_plan = [s.command for s in plan.install_steps]
        run_plan = [s.command for s in plan.run_steps]
    except Exception:
        pass

    # Determine support level from adapter properties
    eco_type = adapter.ecosystem
    support_level = _SUPPORT_LEVEL_MAP.get(eco_type, "detect-only")
    if adapter.supports_execute and detection.runtime and detection.runtime.available:
        support_level = "native" if eco_type == "scripting" and adapter.name == "python" else "execute-if-runtime-present"

    # Get runtime names
    runtimes = adapter.requires_runtime
    runtime_required = runtimes[0] if runtimes else ""

    # Build safety notes from adapter
    safety_notes = []
    try:
        rules = adapter.safety_rules(Path("."))
        for rule in rules[:3]:
            safety_notes.append(rule.message)
    except Exception:
        pass

    return LanguageEcosystem(
        id=adapter.name,
        display_name=adapter.display_name,
        detected_files=list(detection.evidence),
        environment_files=[e for e in detection.evidence if any(
            kw in e for kw in ["requirements", "pyproject", "setup", "Pipfile", "poetry",
                               "DESCRIPTION", "renv", "Project.toml", "Manifest.toml",
                               "package.json", "Cargo.toml", "pom.xml", "build.gradle",
                               "CMakeLists", "Makefile", "Snakefile", "nextflow"]
        )],
        entrypoint_candidates=[e for e in detection.evidence if any(
            kw in e for kw in [".py", ".R", ".jl", ".js", ".ts", ".rs", ".java", ".cpp", ".c", ".sh", ".m", ".nf"]
        )],
        install_plan=install_plan,
        run_plan=run_plan,
        runtime_required=runtime_required,
        runtime_available=detection.runtime.available if detection.runtime else False,
        support_level=support_level,
        limitations=list(detection.limitations),
        safety_notes=safety_notes,
    )


def detect_ecosystems(repo_path: str) -> list[LanguageEcosystem]:
    """Detect all language ecosystems in a repository.

    Delegates to the AdapterRegistry for detection.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of detected LanguageEcosystem objects.
    """
    root = Path(repo_path)
    registry = get_registry()
    detections = registry.detect(root)

    ecosystems = []
    for detection in detections:
        adapter = registry.get(detection.name)
        if adapter:
            eco = _adapter_to_ecosystem(detection, adapter)
            ecosystems.append(eco)

    return ecosystems


def get_ecosystem_info(eco_id: str) -> dict[str, Any] | None:
    """Get information about a specific ecosystem."""
    registry = get_registry()
    adapter = registry.get(eco_id)
    if not adapter:
        return None

    # Get runtime info
    runtimes = adapter.requires_runtime
    runtime_available = False
    for rt in runtimes:
        info = adapter._check_runtime_available(rt)
        if info.available:
            runtime_available = True
            break

    # Python is the native ecosystem
    support_level = _SUPPORT_LEVEL_MAP.get(adapter.ecosystem, "detect-only")
    if adapter.name == "python":
        support_level = "native"

    return {
        "id": adapter.name,
        "display_name": adapter.display_name,
        "environment_files": [],
        "entrypoint_candidates": [],
        "runtime_required": runtimes[0] if runtimes else "",
        "runtime_available": runtime_available,
        "support_level": support_level,
        "limitations": [],
        "safety_notes": [],
    }


def list_ecosystems() -> list[dict[str, str]]:
    """List all known ecosystems."""
    registry = get_registry()
    adapters = registry.list_adapters()
    return [
        {
            "id": a["name"],
            "display_name": a["display_name"],
            "support_level": _SUPPORT_LEVEL_MAP.get(a["ecosystem"], "detect-only"),
        }
        for a in adapters
    ]
