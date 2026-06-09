"""Scanner orchestrator — runs all checks and produces a Report."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from oss_paper_ci import __version__
from oss_paper_ci.checks import run_all_checks
from oss_paper_ci.config import Config, load_config
from oss_paper_ci.models import (
    PolicyInfo, Report, ReportMetadata, RepoInfo, Severity, Status, Summary,
)
from oss_paper_ci.scoring import compute_score, get_score_breakdown
from oss_paper_ci.utils.fs import find_files_by_extension, list_files


def scan(repo_path: str, config: Config | None = None) -> Report:
    """Scan a repository and produce a Report.

    Args:
        repo_path: Path to the repository root.
        config: Optional configuration. If None, loads from repo_path.

    Returns:
        Complete Report object.
    """
    repo_path = str(Path(repo_path).resolve())

    if config is None:
        config = load_config(repo_root=repo_path)

    # Resolve policy profile
    from oss_paper_ci.policy import get_profile
    try:
        profile = get_profile(config.profile)
    except ValueError:
        profile = get_profile("default")

    # Apply profile check overrides to config severity_overrides
    merged_overrides = dict(profile.check_overrides)
    merged_overrides.update(config.checks.severity_overrides)

    # Detect languages
    detected_languages = _detect_languages(repo_path, config)
    detected_project_types = _detect_project_types(repo_path, config)

    repo_info = RepoInfo(
        path=repo_path,
        detected_languages=detected_languages,
        detected_project_types=detected_project_types,
    )

    # Run all checks
    checks = run_all_checks(repo_path, config)

    # Apply severity overrides from profile + config
    for check in checks:
        if check.id in merged_overrides:
            new_sev = merged_overrides[check.id]
            try:
                check.severity = Severity(new_sev)
            except ValueError:
                pass  # ignore invalid severity values

    # Compute score with profile thresholds
    score, status, counts = compute_score(checks, profile)
    breakdown = get_score_breakdown(checks, profile)

    summary = Summary(score=score, status=status, counts=counts, score_breakdown=breakdown)

    # Populate metadata
    all_files = list_files(repo_path, config.ignore.paths)
    metadata = ReportMetadata(
        generated_at=datetime.now(timezone.utc).isoformat(),
        scanned_files=len(all_files),
        ignored_paths=list(config.ignore.paths) if config.ignore.paths else [],
    )

    # Collect recommendations and blocking issues from checks
    recommendations = []
    blocking_issues = []
    for check in checks:
        if check.recommendation and check.status != Status.PASS:
            recommendations.append(check.recommendation)
        if check.status == Status.FAIL:
            blocking_issues.append(f"{check.id}: {check.message}")

    # Policy info
    policy_info = PolicyInfo(
        profile=profile.name,
        pass_score=profile.pass_score,
        warn_score=profile.warn_score,
        fail_under=profile.fail_under,
        config_path=config.config_path,
    )

    return Report(
        schema_version="0.3",
        tool="oss-paper-ci",
        version=__version__,
        repository=repo_info,
        summary=summary,
        checks=checks,
        metadata=metadata,
        recommendations=recommendations,
        blocking_issues=blocking_issues,
        policy=policy_info,
    )


def _detect_languages(repo_path: str, config: Config) -> list[str]:
    """Detect programming languages present in the repo."""
    from oss_paper_ci.utils.fs import list_files

    files = list_files(repo_path, config.ignore.paths)
    ext_map = {
        ".py": "Python",
        ".r": "R",
        ".R": "R",
        ".jl": "Julia",
        ".m": "MATLAB",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".rs": "Rust",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tex": "LaTeX",
    }
    found = set()
    for f in files:
        lang = ext_map.get(f.suffix)
        if lang:
            found.add(lang)
    return sorted(found)


def _detect_project_types(repo_path: str, config: Config) -> list[str]:
    """Detect project types (e.g., Python package, Jupyter, LaTeX)."""
    from oss_paper_ci.utils.fs import find_files_by_name

    types = []
    names = {f.name for f in find_files_by_name(repo_path, "", config.ignore.paths)}
    file_names = set()

    from oss_paper_ci.utils.fs import list_files
    all_files = list_files(repo_path, config.ignore.paths)
    file_names = {f.name for f in all_files}

    if "pyproject.toml" in file_names or "setup.py" in file_names or "setup.cfg" in file_names:
        types.append("Python package")
    if "requirements.txt" in file_names:
        types.append("Python (pip)")
    if "environment.yml" in file_names:
        types.append("Conda")
    if "Dockerfile" in file_names:
        types.append("Docker")
    if any(f.suffix == ".ipynb" for f in all_files):
        types.append("Jupyter")
    if any(f.suffix == ".tex" for f in all_files):
        types.append("LaTeX")
    if "Makefile" in file_names:
        types.append("Make")
    if any(f.suffix == ".R" or f.suffix == ".r" for f in all_files):
        types.append("R")

    return types
