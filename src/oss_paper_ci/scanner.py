"""Scanner orchestrator — runs all checks and produces a Report."""

from __future__ import annotations

from pathlib import Path

from oss_paper_ci import __version__
from oss_paper_ci.checks import run_all_checks
from oss_paper_ci.config import Config, load_config
from oss_paper_ci.models import Report, RepoInfo, Summary
from oss_paper_ci.scoring import compute_score
from oss_paper_ci.utils.fs import find_files_by_extension


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

    # Compute score
    score, status, counts = compute_score(checks)

    summary = Summary(score=score, status=status, counts=counts)

    return Report(
        schema_version="0.1",
        tool="oss-paper-ci",
        version=__version__,
        repository=repo_info,
        summary=summary,
        checks=checks,
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
