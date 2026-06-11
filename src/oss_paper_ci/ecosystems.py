"""Language ecosystem detection for multi-language research repositories.

Detects programming language ecosystems, their environment files,
entrypoint candidates, runtime availability, and support levels.

Support levels:
- native: fully supported (Python)
- execute-if-runtime-present: can execute if runtime is installed (R, Julia, etc.)
- dry-run: can detect and plan, but cannot execute (MATLAB, specialized tools)
- detect-only: can only detect presence (unsupported combinations)
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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


# Ecosystem definitions
ECOSYSTEMS: dict[str, dict[str, Any]] = {
    "python": {
        "display_name": "Python",
        "environment_files": ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
                              "environment.yml", "conda.yml", "Pipfile", "poetry.lock"],
        "entrypoint_candidates": ["scripts/*.py", "main.py", "run.py", "train.py",
                                  "evaluate.py", "analyze.py", "reproduce.py"],
        "runtime_required": "python3",
        "support_level": "native",
        "limitations": [],
        "safety_notes": ["Uses isolated virtual environment for installation."],
    },
    "r": {
        "display_name": "R",
        "environment_files": ["renv.lock", "DESCRIPTION", "install.R", ".Rprofile"],
        "entrypoint_candidates": ["scripts/*.R", "scripts/*.r", "analysis.R", "run.R",
                                  "main.R", "reproduce.R"],
        "runtime_required": "Rscript",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "R runtime (Rscript) must be installed separately.",
            "renv restoration requires renv package.",
            "Some R packages may require system libraries.",
        ],
        "safety_notes": ["R scripts are executed in the repository directory."],
    },
    "julia": {
        "display_name": "Julia",
        "environment_files": ["Project.toml", "Manifest.toml"],
        "entrypoint_candidates": ["scripts/*.jl", "main.jl", "run.jl", "analyze.jl",
                                  "reproduce.jl"],
        "runtime_required": "julia",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "Julia runtime must be installed separately.",
            "Package installation may take significant time.",
            "Some Julia packages may require system libraries.",
        ],
        "safety_notes": ["Julia scripts are executed in the repository directory."],
    },
    "matlab": {
        "display_name": "MATLAB/Octave",
        "environment_files": [],
        "entrypoint_candidates": ["*.m", "startup.m", "run.m", "main.m", "scripts/*.m"],
        "runtime_required": "matlab",
        "support_level": "dry-run",
        "limitations": [
            "MATLAB requires a commercial license.",
            "Octave can be used as a fallback but is not fully compatible.",
            "MATLAB runtime detection is limited.",
        ],
        "safety_notes": ["MATLAB scripts are not automatically executed."],
    },
    "octave": {
        "display_name": "GNU Octave",
        "environment_files": [],
        "entrypoint_candidates": ["*.m", "startup.m", "run.m", "main.m", "scripts/*.m"],
        "runtime_required": "octave",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "Octave is not fully compatible with MATLAB.",
            "Some MATLAB-specific functions may not work.",
        ],
        "safety_notes": ["Octave scripts are executed in the repository directory."],
    },
    "node": {
        "display_name": "Node.js/JavaScript",
        "environment_files": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
        "entrypoint_candidates": ["scripts/*.js", "index.js", "main.js", "analyze.js"],
        "runtime_required": "node",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "Node.js runtime must be installed separately.",
            "npm install may download many packages.",
        ],
        "safety_notes": ["Node scripts are executed in the repository directory."],
    },
    "rust": {
        "display_name": "Rust",
        "environment_files": ["Cargo.toml", "Cargo.lock"],
        "entrypoint_candidates": ["src/main.rs", "src/bin/*.rs"],
        "runtime_required": "cargo",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "Rust toolchain must be installed separately.",
            "Compilation may take significant time.",
        ],
        "safety_notes": ["Rust projects are compiled before execution."],
    },
    "java": {
        "display_name": "Java",
        "environment_files": ["pom.xml", "build.gradle", "gradlew"],
        "entrypoint_candidates": ["src/main/java/**/*.java"],
        "runtime_required": "java",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "Java runtime must be installed separately.",
            "Maven/Gradle build may download many dependencies.",
        ],
        "safety_notes": ["Java projects are compiled before execution."],
    },
    "cpp": {
        "display_name": "C/C++",
        "environment_files": ["CMakeLists.txt", "Makefile"],
        "entrypoint_candidates": ["src/*.cpp", "src/*.c", "main.cpp", "main.c"],
        "runtime_required": "g++",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "C/C++ compiler must be installed separately.",
            "Build process varies by project.",
            "Some projects may require specific libraries.",
        ],
        "safety_notes": ["C/C++ projects are compiled before execution."],
    },
    "make": {
        "display_name": "Make",
        "environment_files": ["Makefile"],
        "entrypoint_candidates": ["Makefile"],
        "runtime_required": "make",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "Make targets vary by project.",
            "Default target may not be the reproduction target.",
        ],
        "safety_notes": ["Only explicit make targets are executed."],
    },
    "snakemake": {
        "display_name": "Snakemake",
        "environment_files": ["Snakefile", "workflow/Snakefile"],
        "entrypoint_candidates": ["Snakefile", "workflow/Snakefile"],
        "runtime_required": "snakemake",
        "support_level": "dry-run",
        "limitations": [
            "Snakemake runtime must be installed separately.",
            "Workflow execution may require significant resources.",
            "Data dependencies may not be available.",
        ],
        "safety_notes": ["Snakemake workflows are not automatically executed."],
    },
    "nextflow": {
        "display_name": "Nextflow",
        "environment_files": ["nextflow.config", "main.nf"],
        "entrypoint_candidates": ["main.nf"],
        "runtime_required": "nextflow",
        "support_level": "dry-run",
        "limitations": [
            "Nextflow runtime must be installed separately.",
            "Workflow execution may require significant resources.",
            "Container/singularity support may be needed.",
        ],
        "safety_notes": ["Nextflow workflows are not automatically executed."],
    },
    "shell": {
        "display_name": "Shell Scripts",
        "environment_files": [],
        "entrypoint_candidates": ["reproduce.sh", "run.sh", "scripts/*.sh"],
        "runtime_required": "bash",
        "support_level": "execute-if-runtime-present",
        "limitations": [
            "Shell scripts may have system-specific dependencies.",
            "Scripts may require specific tools to be installed.",
        ],
        "safety_notes": ["Shell scripts are executed with bash."],
    },
}


def detect_ecosystems(repo_path: str) -> list[LanguageEcosystem]:
    """Detect all language ecosystems in a repository.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of detected LanguageEcosystem objects.
    """
    root = Path(repo_path)
    detected: list[LanguageEcosystem] = []

    for eco_id, eco_def in ECOSYSTEMS.items():
        found_files = _find_ecosystem_files(root, eco_def)
        if not found_files:
            continue

        env_files = _find_environment_files(root, eco_def)
        entrypoints = _find_entrypoints(root, eco_def)

        # Check runtime availability
        runtime_available = _check_runtime(eco_def.get("runtime_required", ""))

        # Determine support level
        support_level = eco_def.get("support_level", "detect-only")

        # Build install and run plans
        install_plan = _build_install_plan(eco_id, env_files, root)
        run_plan = _build_run_plan(eco_id, entrypoints)

        eco = LanguageEcosystem(
            id=eco_id,
            display_name=eco_def["display_name"],
            detected_files=[str(f.relative_to(root)) for f in found_files],
            environment_files=[str(f.relative_to(root)) for f in env_files],
            entrypoint_candidates=[str(f.relative_to(root)) for f in entrypoints],
            install_plan=install_plan,
            run_plan=run_plan,
            runtime_required=eco_def.get("runtime_required", ""),
            runtime_available=runtime_available,
            support_level=support_level,
            limitations=eco_def.get("limitations", []),
            safety_notes=eco_def.get("safety_notes", []),
        )
        detected.append(eco)

    return detected


def get_ecosystem_info(eco_id: str) -> dict[str, Any] | None:
    """Get information about a specific ecosystem."""
    eco_def = ECOSYSTEMS.get(eco_id)
    if not eco_def:
        return None

    return {
        "id": eco_id,
        "display_name": eco_def["display_name"],
        "environment_files": eco_def["environment_files"],
        "entrypoint_candidates": eco_def["entrypoint_candidates"],
        "runtime_required": eco_def.get("runtime_required", ""),
        "runtime_available": _check_runtime(eco_def.get("runtime_required", "")),
        "support_level": eco_def.get("support_level", "detect-only"),
        "limitations": eco_def.get("limitations", []),
        "safety_notes": eco_def.get("safety_notes", []),
    }


def list_ecosystems() -> list[dict[str, str]]:
    """List all known ecosystems."""
    return [
        {"id": eco_id, "display_name": eco_def["display_name"],
         "support_level": eco_def.get("support_level", "detect-only")}
        for eco_id, eco_def in ECOSYSTEMS.items()
    ]


def _find_ecosystem_files(root: Path, eco_def: dict) -> list[Path]:
    """Find files that indicate this ecosystem."""
    found = []
    for pattern in eco_def.get("environment_files", []):
        for f in root.glob(pattern):
            if f.is_file():
                found.append(f)
    for pattern in eco_def.get("entrypoint_candidates", []):
        for f in root.glob(pattern):
            if f.is_file():
                found.append(f)
    return found


def _find_environment_files(root: Path, eco_def: dict) -> list[Path]:
    """Find environment files for this ecosystem."""
    found = []
    for pattern in eco_def.get("environment_files", []):
        for f in root.glob(pattern):
            if f.is_file():
                found.append(f)
    return found


def _find_entrypoints(root: Path, eco_def: dict) -> list[Path]:
    """Find entrypoint scripts for this ecosystem."""
    found = []
    for pattern in eco_def.get("entrypoint_candidates", []):
        for f in root.glob(pattern):
            if f.is_file():
                found.append(f)
    return found


def _check_runtime(runtime_cmd: str) -> bool:
    """Check if a runtime is available."""
    if not runtime_cmd:
        return False
    return shutil.which(runtime_cmd) is not None


def _build_install_plan(eco_id: str, env_files: list[Path], root: Path) -> list[str]:
    """Build installation plan for an ecosystem."""
    plans = []
    env_names = [f.name for f in env_files]

    if eco_id == "python":
        if "requirements.txt" in env_names:
            plans.append("python -m pip install -r requirements.txt")
        elif "pyproject.toml" in env_names:
            plans.append("python -m pip install -e .")
        elif "setup.py" in env_names:
            plans.append("python -m pip install -e .")
    elif eco_id == "r":
        if "renv.lock" in env_names:
            plans.append("Rscript -e 'renv::restore()'")
        elif "DESCRIPTION" in env_names:
            plans.append("Rscript -e 'devtools::install_deps()'")
    elif eco_id == "julia":
        if "Project.toml" in env_names:
            plans.append("julia -e 'using Pkg; Pkg.instantiate()'")
    elif eco_id == "node":
        if "package-lock.json" in env_names:
            plans.append("npm ci")
        elif "package.json" in env_names:
            plans.append("npm install")
    elif eco_id == "rust":
        if "Cargo.toml" in env_names:
            plans.append("cargo build --release")
    elif eco_id == "java":
        if "pom.xml" in env_names:
            plans.append("mvn package")
        elif "build.gradle" in env_names:
            plans.append("./gradlew build")
    elif eco_id == "cpp":
        if "CMakeLists.txt" in env_names:
            plans.append("cmake -B build && cmake --build build")
        elif "Makefile" in env_names:
            plans.append("make")

    return plans


def _build_run_plan(eco_id: str, entrypoints: list[Path]) -> list[str]:
    """Build run plan for an ecosystem."""
    plans = []
    for ep in entrypoints[:3]:  # Limit to first 3
        name = ep.name
        if eco_id == "python":
            plans.append(f"python {name}")
        elif eco_id == "r":
            plans.append(f"Rscript {name}")
        elif eco_id == "julia":
            plans.append(f"julia {name}")
        elif eco_id == "matlab" or eco_id == "octave":
            plans.append(f"octave --no-gui {name}")
        elif eco_id == "node":
            plans.append(f"node {name}")
        elif eco_id == "rust":
            plans.append("cargo run --release")
        elif eco_id == "java":
            plans.append("java -jar target/*.jar")
        elif eco_id == "cpp":
            plans.append("./build/main")
        elif eco_id == "make":
            plans.append("make reproduce")
        elif eco_id == "snakemake":
            plans.append("snakemake --cores 1")
        elif eco_id == "nextflow":
            plans.append("nextflow run main.nf")
        elif eco_id == "shell":
            plans.append(f"bash {name}")

    return plans
