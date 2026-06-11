"""Scanner orchestrator — runs all checks and produces a Report."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from oss_paper_ci import __version__
from oss_paper_ci.checks import run_all_checks
from oss_paper_ci.config import Config, SuppressionEntry, load_config
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

    # Run all built-in checks
    checks = run_all_checks(repo_path, config)

    # Load and evaluate rule packs
    custom_checks, rule_pack_names = _load_rule_packs(config, repo_path)
    checks.extend(custom_checks)

    # Apply severity overrides from profile + config
    for check in checks:
        if check.id in merged_overrides:
            new_sev = merged_overrides[check.id]
            try:
                check.severity = Severity(new_sev)
            except ValueError:
                pass  # ignore invalid severity values

    # Apply suppressions
    checks, suppressed_findings = _apply_suppressions(checks, config)

    # Compute score with profile thresholds
    from oss_paper_ci.scoring import compute_score_components
    score, status, counts = compute_score(checks, profile)
    breakdown = get_score_breakdown(checks, profile)
    score_components = compute_score_components(checks, profile)

    summary = Summary(score=score, status=status, counts=counts, score_breakdown=breakdown, score_components=score_components)

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
        schema_version="0.4",
        tool="oss-paper-ci",
        version=__version__,
        repository=repo_info,
        summary=summary,
        checks=checks,
        metadata=metadata,
        recommendations=recommendations,
        blocking_issues=blocking_issues,
        policy=policy_info,
        suppressed_findings=suppressed_findings,
        rule_packs=rule_pack_names,
    )


def _load_rule_packs(
    config: Config, repo_path: str
) -> tuple[list, list[str]]:
    """Load and evaluate rule packs from config.

    Returns:
        Tuple of (list of CheckResult, list of rule pack names).
    """
    from oss_paper_ci.checks.loader import evaluate_rules, load_rule_pack

    all_results = []
    pack_names = []

    for pack_path in config.rule_packs:
        # Resolve relative to config file directory or repo root
        resolved = Path(pack_path)
        if not resolved.is_absolute():
            if config.config_path:
                resolved = Path(config.config_path).parent / pack_path
            else:
                resolved = Path(repo_path) / pack_path

        if not resolved.exists():
            # Add an error finding for missing rule pack
            from oss_paper_ci.models import CheckResult
            all_results.append(CheckResult(
                id="RULE_PACK",
                title="Rule Pack",
                severity=Severity.ERROR,
                status=Status.UNKNOWN,
                message=f"Rule pack not found: {pack_path}",
                recommendation="Check the rule_packs path in your config.",
            ))
            continue

        try:
            manifest = load_rule_pack(resolved)
            pack_names.append(manifest.name or str(resolved))
            results = evaluate_rules(manifest, repo_path)
            all_results.extend(results)
        except Exception as exc:
            from oss_paper_ci.models import CheckResult
            all_results.append(CheckResult(
                id="RULE_PACK",
                title="Rule Pack",
                severity=Severity.ERROR,
                status=Status.UNKNOWN,
                message=f"Failed to load rule pack {pack_path}: {exc}",
                recommendation="Check the rule pack YAML syntax.",
            ))

    return all_results, pack_names


def _apply_suppressions(
    checks: list, config: Config
) -> tuple[list, list[dict]]:
    """Apply suppressions to check results.

    Returns:
        Tuple of (remaining checks, suppressed findings list).
    """
    supp = config.suppressions

    # Build sets for quick lookup
    suppressed_ids = {f.id for f in supp.findings if f.id}
    suppressed_paths = set(supp.paths)

    remaining = []
    suppressed = []

    for check in checks:
        # Check if this finding is suppressed by ID
        if check.id in suppressed_ids:
            entry = next(f for f in supp.findings if f.id == check.id)
            suppressed.append({
                "id": check.id,
                "title": check.title,
                "severity": check.severity.value,
                "status": check.status.value,
                "message": check.message,
                "reason": entry.reason,
                "until": entry.until,
            })
            continue

        # Check if finding relates to a suppressed path
        # (check if any evidence path matches suppressed paths)
        is_path_suppressed = False
        for evidence in check.evidence:
            for pattern in suppressed_paths:
                if _path_matches(evidence, pattern):
                    is_path_suppressed = True
                    break
            if is_path_suppressed:
                break

        if is_path_suppressed:
            suppressed.append({
                "id": check.id,
                "title": check.title,
                "severity": check.severity.value,
                "status": check.status.value,
                "message": check.message,
                "reason": "Path suppression",
                "until": "",
            })
            continue

        remaining.append(check)

    return remaining, suppressed


def _path_matches(path: str, pattern: str) -> bool:
    """Check if a path matches a glob-like pattern."""
    import fnmatch
    return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern + "/*")


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
