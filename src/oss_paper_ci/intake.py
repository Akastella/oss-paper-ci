"""Repository intake engine: analyze a repository and produce an intake report.

Read-only operation: scans README, environment files, scripts, notebooks,
workflow files, and result directories to produce a structured intake report.
Does NOT execute any commands or modify the repository.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci.readme_miner import CommandCandidate, mine_readme_commands
from oss_paper_ci.command_extractor import extract_commands_from_build_files
from oss_paper_ci.repo_cloner import classify_input, is_github_url, is_paper_url


@dataclass
class DetectedInfo:
    """Information detected from a repository."""

    languages: list[str] = field(default_factory=list)
    ecosystems: list[dict[str, Any]] = field(default_factory=list)
    environment_files: list[str] = field(default_factory=list)
    workflow_files: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    notebooks: list[str] = field(default_factory=list)
    data_paths: list[str] = field(default_factory=list)
    result_paths: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    has_existing_config: bool = False
    existing_config_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "languages": self.languages,
            "ecosystems": self.ecosystems,
            "environment_files": self.environment_files,
            "workflow_files": self.workflow_files,
            "scripts": self.scripts,
            "notebooks": self.notebooks,
            "data_paths": self.data_paths,
            "result_paths": self.result_paths,
            "artifact_paths": self.artifact_paths,
            "has_existing_config": self.has_existing_config,
            "existing_config_path": self.existing_config_path,
        }


@dataclass
class IntakeReport:
    """Complete intake report for a repository."""

    schema_version: str = "0.1"
    report_type: str = "oss-paper-ci-intake-report"
    tool_version: str = "3.2.0rc1"
    source: dict[str, Any] = field(default_factory=dict)
    detected: DetectedInfo = field(default_factory=DetectedInfo)
    command_candidates: list[CommandCandidate] = field(default_factory=list)
    confidence: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_type": self.report_type,
            "tool_version": self.tool_version,
            "source": self.source,
            "detected": self.detected.to_dict(),
            "command_candidates": [c.to_dict() for c in self.command_candidates],
            "confidence": self.confidence,
            "warnings": self.warnings,
            "limitations": self.limitations,
        }


def run_intake(
    input_path: str,
    clone: bool = False,
    workdir: str | None = None,
) -> IntakeReport:
    """Run repository intake analysis.

    Args:
        input_path: Local path, GitHub URL, or paper URL.
        clone: If True and input is a GitHub URL, clone the repository.
        workdir: Working directory for clone.

    Returns:
        IntakeReport with all detected information.
    """
    from oss_paper_ci.autoplan_score import compute_confidence

    report = IntakeReport()
    report.source = {
        "input": input_path,
        "kind": classify_input(input_path),
        "cloned": False,
    }

    # Add limitations
    report.limitations = [
        "Intake analysis is read-only; no commands are executed.",
        "Command candidates are inferred from documentation and config files.",
        "Confidence scores indicate detection quality, not correctness.",
        "Review all candidates before using them in a reproducibility plan.",
        "Paper URLs are recognized but not fetched; provide a repository path.",
    ]

    # Handle different input types
    source_kind = report.source["kind"]

    if source_kind == "paper-url":
        report.warnings.append(
            "Paper URL alone is not enough to reproduce; "
            "provide --repo or a local repository path."
        )
        return report

    if source_kind == "github-url":
        if not clone:
            report.warnings.append(
                f"GitHub URL detected ({input_path}). "
                "Use --clone to download the repository for analysis."
            )
            return report
        else:
            # Clone the repository
            from oss_paper_ci.repo_cloner import clone_repository
            clone_result = clone_repository(input_path, workdir=workdir)
            if not clone_result.success:
                report.warnings.append(f"Clone failed: {clone_result.error}")
                return report
            report.source["cloned"] = True
            report.source["clone_path"] = clone_result.local_path
            repo_path = clone_result.local_path
    elif source_kind == "local":
        repo_path = input_path
    else:
        report.warnings.append(f"Unknown input type: {input_path}")
        return report

    # Verify path exists
    if not os.path.isdir(repo_path):
        report.warnings.append(f"Path does not exist or is not a directory: {repo_path}")
        return report

    # Run detection
    report.detected = _detect_repository(repo_path)

    # Mine commands from README
    readme_commands = mine_readme_commands(repo_path)
    report.command_candidates.extend(readme_commands)

    # Extract commands from build files
    build_commands = extract_commands_from_build_files(repo_path)
    report.command_candidates.extend(build_commands)

    # Deduplicate commands
    report.command_candidates = _deduplicate_commands(report.command_candidates)

    # Compute confidence
    eco_dicts = report.detected.ecosystems
    cmd_dicts = [c.to_dict() for c in report.command_candidates]
    scores = compute_confidence(
        ecosystems=eco_dicts,
        env_files=report.detected.environment_files,
        command_candidates=cmd_dicts,
        artifact_paths=report.detected.artifact_paths,
        has_metrics_file=any("metric" in p.lower() for p in report.detected.artifact_paths),
        has_existing_config=report.detected.has_existing_config,
    )
    report.confidence = scores.to_dict()

    return report


def _detect_repository(repo_path: str) -> DetectedInfo:
    """Detect repository structure and contents."""
    root = Path(repo_path)
    info = DetectedInfo()

    # Detect ecosystems
    try:
        from oss_paper_ci.ecosystems import detect_ecosystems
        eco_list = detect_ecosystems(repo_path)
        info.ecosystems = [e.to_dict() for e in eco_list]
        info.languages = [e.id for e in eco_list]
    except Exception:
        pass

    # Detect environment files
    env_patterns = [
        "requirements*.txt", "pyproject.toml", "setup.py", "setup.cfg",
        "environment.yml", "conda.yml", "Pipfile",
        "renv.lock", "DESCRIPTION", "install.R",
        "Project.toml", "Manifest.toml",
        "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "Cargo.toml", "Cargo.lock",
        "pom.xml", "build.gradle",
        "CMakeLists.txt",
        "Dockerfile", "docker-compose.yml",
        ".python-version", "runtime.txt",
    ]
    for pattern in env_patterns:
        for f in root.glob(pattern):
            if f.is_file():
                info.environment_files.append(str(f.relative_to(root)))

    # Detect workflow files
    workflow_patterns = [
        "Makefile", "Snakefile", "workflow/Snakefile",
        "Justfile", "Taskfile.yml",
        "nextflow.config", "main.nf",
        ".github/workflows/*.yml", ".github/workflows/*.yaml",
        ".gitlab-ci.yml",
        "Jenkinsfile",
    ]
    for pattern in workflow_patterns:
        for f in root.glob(pattern):
            if f.is_file():
                info.workflow_files.append(str(f.relative_to(root)))

    # Detect scripts
    script_patterns = [
        "scripts/*.py", "scripts/*.sh", "scripts/*.R", "scripts/*.r",
        "scripts/*.jl", "scripts/*.js",
        "bin/*", "tools/*",
        "*.py", "*.sh", "*.R",
    ]
    for pattern in script_patterns:
        for f in root.glob(pattern):
            if f.is_file() and not f.name.startswith("."):
                rel = str(f.relative_to(root))
                if rel not in info.scripts:
                    info.scripts.append(rel)

    # Detect notebooks
    for f in root.glob("**/*.ipynb"):
        if f.is_file() and ".ipynb_checkpoints" not in str(f):
            info.notebooks.append(str(f.relative_to(root)))

    # Detect data paths
    data_dir_names = ["data", "dataset", "datasets", "input", "inputs", "raw"]
    for name in data_dir_names:
        d = root / name
        if d.is_dir():
            info.data_paths.append(name + "/")

    # Detect result paths
    result_dir_names = ["results", "output", "outputs", "figures", "plots", "tables"]
    for name in result_dir_names:
        d = root / name
        if d.is_dir():
            info.result_paths.append(name + "/")

    # Detect artifact paths
    artifact_patterns = [
        "results/**/*.json", "results/**/*.csv", "results/**/*.tsv",
        "output/**/*.json", "output/**/*.csv",
        "figures/**/*.png", "figures/**/*.pdf", "figures/**/*.svg",
        "plots/**/*.png", "plots/**/*.pdf",
        "tables/**/*.csv", "tables/**/*.tex",
        "**/*.metrics.json", "**/metrics.json",
    ]
    seen_artifacts: set[str] = set()
    for pattern in artifact_patterns:
        for f in root.glob(pattern):
            if f.is_file():
                rel = str(f.relative_to(root))
                if rel not in seen_artifacts:
                    seen_artifacts.add(rel)
                    info.artifact_paths.append(rel)

    # Detect existing reproducibility config
    config_names = [
        "reproducibility.yml", "reproducibility.yaml",
        ".oss-paper-ci.yml", ".oss-paper-ci.yaml",
    ]
    for name in config_names:
        if (root / name).is_file():
            info.has_existing_config = True
            info.existing_config_path = name
            break

    return info


def _deduplicate_commands(
    candidates: list[CommandCandidate],
) -> list[CommandCandidate]:
    """Remove duplicate commands, keeping the one with highest confidence."""
    seen: dict[str, CommandCandidate] = {}

    for c in candidates:
        key = c.command
        if key in seen:
            if c.confidence > seen[key].confidence:
                seen[key] = c
        else:
            seen[key] = c

    return list(seen.values())
