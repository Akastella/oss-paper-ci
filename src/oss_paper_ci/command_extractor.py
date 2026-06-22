"""Command extraction from build files and package managers.

Extracts commands from Makefile targets, Snakemake rules, package.json scripts,
pyproject.toml scripts, and other build configuration files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci.readme_miner import CommandCandidate


def extract_commands_from_build_files(repo_path: str) -> list[CommandCandidate]:
    """Extract commands from build files in a repository.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of CommandCandidate objects.
    """
    root = Path(repo_path)
    candidates: list[CommandCandidate] = []

    # Makefile targets
    makefile = root / "Makefile"
    if makefile.is_file():
        candidates.extend(_extract_makefile_targets(makefile, root))

    # Snakemake rules
    for snake_name in ["Snakefile", "workflow/Snakefile"]:
        snakefile = root / snake_name
        if snakefile.is_file():
            candidates.extend(_extract_snakemake_rules(snakefile, root))

    # package.json scripts
    pkg_json = root / "package.json"
    if pkg_json.is_file():
        candidates.extend(_extract_package_json_scripts(pkg_json, root))

    # pyproject.toml scripts
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        candidates.extend(_extract_pyproject_scripts(pyproject, root))

    # Justfile
    justfile = root / "Justfile"
    if justfile.is_file():
        candidates.extend(_extract_justfile_targets(justfile, root))

    # Shell scripts in scripts/ directory
    scripts_dir = root / "scripts"
    if scripts_dir.is_dir():
        candidates.extend(_extract_shell_scripts(scripts_dir, root))

    # Dockerfile
    dockerfile = root / "Dockerfile"
    if dockerfile.is_file():
        candidates.extend(_extract_dockerfile_commands(dockerfile, root))

    # environment.yml / conda.yml
    for env_name in ["environment.yml", "conda.yml"]:
        env_file = root / env_name
        if env_file.is_file():
            candidates.extend(_extract_conda_env(env_file, root))

    # Assign IDs
    _assign_ids(candidates)

    return candidates


def _extract_makefile_targets(makefile: Path, root: Path) -> list[CommandCandidate]:
    """Extract targets from a Makefile."""
    candidates: list[CommandCandidate] = []
    try:
        text = makefile.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return candidates

    rel_path = str(makefile.relative_to(root))
    lines = text.split("\n")

    for i, line in enumerate(lines):
        # Match target: dependencies pattern
        m = re.match(r"^([a-zA-Z_][\w.-]*)\s*:", line)
        if m:
            target = m.group(1)
            # Skip common non-repro targets
            if target in (".PHONY", ".DEFAULT", ".SILENT", ".SUFFIXES", "clean",
                          "help", ".DELETE_ON_ERROR"):
                continue

            kind = _classify_makefile_target(target)
            candidates.append(CommandCandidate(
                command=f"make {target}",
                source=rel_path,
                line=i + 1,
                kind=kind,
                confidence=0.6,
                dangerous=False,
                reason=f"Makefile target '{target}' at {rel_path}:{i+1}",
            ))

    return candidates


def _extract_snakemake_rules(snakefile: Path, root: Path) -> list[CommandCandidate]:
    """Extract rules from a Snakemake file."""
    candidates: list[CommandCandidate] = []
    try:
        text = snakefile.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return candidates

    rel_path = str(snakefile.relative_to(root))

    for m in re.finditer(r"^rule\s+(\w+)", text, re.MULTILINE):
        rule_name = m.group(1)
        if rule_name == "all":
            continue

        line_num = text[:m.start()].count("\n") + 1
        candidates.append(CommandCandidate(
            command=f"snakemake --cores 1 {rule_name}",
            source=rel_path,
            line=line_num,
            kind="train",
            confidence=0.5,
            dangerous=False,
            reason=f"Snakemake rule '{rule_name}' at {rel_path}:{line_num}",
        ))

    return candidates


def _extract_package_json_scripts(pkg_json: Path, root: Path) -> list[CommandCandidate]:
    """Extract scripts from package.json."""
    candidates: list[CommandCandidate] = []
    try:
        import json
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
    except Exception:
        return candidates

    rel_path = str(pkg_json.relative_to(root))
    scripts = data.get("scripts", {})

    for name, cmd in scripts.items():
        if not isinstance(cmd, str):
            continue
        kind = _classify_npm_script(name)
        candidates.append(CommandCandidate(
            command=f"npm run {name}",
            source=rel_path,
            line=0,
            kind=kind,
            confidence=0.6,
            dangerous=False,
            reason=f"package.json script '{name}'",
        ))

    return candidates


def _extract_pyproject_scripts(pyproject: Path, root: Path) -> list[CommandCandidate]:
    """Extract scripts from pyproject.toml."""
    candidates: list[CommandCandidate] = []
    try:
        text = pyproject.read_text(encoding="utf-8")
    except Exception:
        return candidates

    rel_path = str(pyproject.relative_to(root))

    # Look for [project.scripts] section
    in_scripts = False
    for i, line in enumerate(text.split("\n")):
        if line.strip() == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts and line.strip().startswith("["):
            in_scripts = False
            continue
        if in_scripts and "=" in line:
            name = line.split("=")[0].strip()
            if name:
                candidates.append(CommandCandidate(
                    command=name,
                    source=rel_path,
                    line=i + 1,
                    kind="unknown",
                    confidence=0.5,
                    dangerous=False,
                    reason=f"pyproject.toml script entry '{name}'",
                ))

    return candidates


def _extract_justfile_targets(justfile: Path, root: Path) -> list[CommandCandidate]:
    """Extract targets from a Justfile."""
    candidates: list[CommandCandidate] = []
    try:
        text = justfile.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return candidates

    rel_path = str(justfile.relative_to(root))

    for i, line in enumerate(text.split("\n")):
        m = re.match(r"^([a-zA-Z_][\w-]*)\s*:", line)
        if m:
            target = m.group(1)
            candidates.append(CommandCandidate(
                command=f"just {target}",
                source=rel_path,
                line=i + 1,
                kind="unknown",
                confidence=0.5,
                dangerous=False,
                reason=f"Justfile target '{target}' at {rel_path}:{i+1}",
            ))

    return candidates


def _extract_shell_scripts(scripts_dir: Path, root: Path) -> list[CommandCandidate]:
    """Extract shell scripts from a scripts/ directory."""
    candidates: list[CommandCandidate] = []

    for script in sorted(scripts_dir.glob("*.sh")):
        rel_path = str(script.relative_to(root))
        candidates.append(CommandCandidate(
            command=f"bash {rel_path}",
            source=rel_path,
            line=1,
            kind="unknown",
            confidence=0.4,
            dangerous=False,
            reason=f"Shell script at {rel_path}",
        ))

    return candidates


def _extract_dockerfile_commands(dockerfile: Path, root: Path) -> list[CommandCandidate]:
    """Extract relevant commands from a Dockerfile."""
    candidates: list[CommandCandidate] = []
    try:
        text = dockerfile.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return candidates

    rel_path = str(dockerfile.relative_to(root))

    for i, line in enumerate(text.split("\n")):
        line = line.strip()
        if line.upper().startswith("RUN "):
            cmd = line[4:].strip()
            candidates.append(CommandCandidate(
                command=cmd,
                source=rel_path,
                line=i + 1,
                kind="install",
                confidence=0.4,
                dangerous=False,
                reason=f"Dockerfile RUN instruction at {rel_path}:{i+1}",
            ))

    return candidates


def _extract_conda_env(env_file: Path, root: Path) -> list[CommandCandidate]:
    """Extract install command from conda environment file."""
    candidates: list[CommandCandidate] = []
    rel_path = str(env_file.relative_to(root))

    candidates.append(CommandCandidate(
        command=f"conda env create -f {env_file.name}",
        source=rel_path,
        line=1,
        kind="install",
        confidence=0.7,
        dangerous=False,
        reason=f"Conda environment file at {rel_path}",
    ))

    return candidates


def _classify_makefile_target(target: str) -> str:
    """Classify a Makefile target by name."""
    t = target.lower()
    if any(w in t for w in ["train", "fit", "learn"]):
        return "train"
    if any(w in t for w in ["eval", "test", "check", "benchmark"]):
        return "evaluate"
    if any(w in t for w in ["install", "setup", "dep", "require"]):
        return "install"
    if any(w in t for w in ["figure", "plot", "chart", "visual"]):
        return "figure"
    if any(w in t for w in ["data", "download", "fetch", "preprocess"]):
        return "data"
    if any(w in t for w in ["reproduce", "run", "all", "paper"]):
        return "train"
    return "unknown"


def _classify_npm_script(name: str) -> str:
    """Classify an npm script by name."""
    n = name.lower()
    if any(w in n for w in ["test", "lint", "check"]):
        return "test"
    if any(w in n for w in ["build", "compile"]):
        return "train"
    if any(w in n for w in ["start", "run", "dev"]):
        return "train"
    return "unknown"


def _assign_ids(candidates: list[CommandCandidate]) -> None:
    """Assign stable IDs to candidates."""
    counters: dict[str, int] = {}
    for c in candidates:
        kind = c.kind if c.kind != "unknown" else "cmd"
        count = counters.get(kind, 0) + 1
        counters[kind] = count
        if count == 1:
            c.id = kind
        else:
            c.id = f"{kind}_{count}"
