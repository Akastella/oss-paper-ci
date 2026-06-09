"""Batch scan orchestration for multi-project workspace scanning.

Scans multiple projects defined in a workspace config, with optional
parallel execution and incremental caching.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci import __version__
from oss_paper_ci.cache import (
    CacheStats,
    compute_cache_key,
    get_cache_dir,
    lookup_cache,
    store_cache,
)
from oss_paper_ci.config import load_config
from oss_paper_ci.scanner import scan as run_scan
from oss_paper_ci.workspace import (
    WorkspaceConfig,
    WorkspaceProject,
    resolve_project_path,
)


@dataclass
class ProjectResult:
    """Result of scanning a single project."""

    id: str
    path: str
    profile: str
    status: str = "unknown"
    score: int = 0
    finding_counts: dict[str, int] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    cache_hit: bool = False
    duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "path": self.path,
            "profile": self.profile,
            "status": self.status,
            "score": self.score,
            "finding_counts": self.finding_counts,
            "cache_hit": self.cache_hit,
        }
        if self.error:
            result["error"] = self.error
        if self.duration_seconds:
            result["duration_seconds"] = round(self.duration_seconds, 3)
        return result


@dataclass
class BatchResult:
    """Result of a batch scan across all workspace projects."""

    schema_version: str = "0.5"
    tool: str = "oss-paper-ci"
    version: str = __version__
    workspace_name: str = ""
    workspace_path: str = ""
    project_count: int = 0
    projects: list[ProjectResult] = field(default_factory=list)
    cache_stats: CacheStats = field(default_factory=CacheStats)
    duration_seconds: float = 0.0

    @property
    def summary(self) -> dict[str, Any]:
        """Compute aggregate summary from project results."""
        status_counts = {"pass": 0, "warn": 0, "fail": 0, "error": 0}
        total_score = 0.0
        scored = 0

        for proj in self.projects:
            if proj.error:
                status_counts["error"] += 1
            else:
                status_counts[proj.status] = status_counts.get(proj.status, 0) + 1
                total_score += proj.score
                scored += 1

        avg_score = round(total_score / scored, 1) if scored else 0.0

        return {
            "pass": status_counts["pass"],
            "warn": status_counts["warn"],
            "fail": status_counts["fail"],
            "error": status_counts["error"],
            "average_score": avg_score,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool": self.tool,
            "version": self.version,
            "workspace": {
                "name": self.workspace_name,
                "project_count": self.project_count,
            },
            "summary": self.summary,
            "projects": [p.to_dict() for p in self.projects],
            "cache": self.cache_stats.to_dict(),
            "duration_seconds": round(self.duration_seconds, 3),
        }


def run_batch_scan(
    workspace: WorkspaceConfig,
    workspace_path: Path,
    *,
    jobs: int = 1,
    use_cache: bool = False,
) -> BatchResult:
    """Run batch scan across all workspace projects.

    Args:
        workspace: Parsed workspace configuration.
        workspace_path: Path to the workspace file.
        jobs: Number of parallel workers (1 = sequential).
        use_cache: Whether to use incremental cache.

    Returns:
        BatchResult with all project results.
    """
    start_time = time.monotonic()
    workspace_dir = workspace_path.parent.resolve()
    cache_dir = get_cache_dir(workspace_dir) if use_cache else None

    # Prepare scan tasks
    tasks = []
    for proj in workspace.projects:
        project_path = resolve_project_path(proj, workspace_dir)
        tasks.append((proj, project_path))

    # Execute scans
    if jobs > 1 and len(tasks) > 1:
        project_results = _run_parallel(tasks, workspace_dir, cache_dir, jobs)
    else:
        project_results = _run_sequential(tasks, workspace_dir, cache_dir)

    # Build cache stats
    cache_stats = CacheStats(total=len(project_results))
    for pr in project_results:
        if pr.cache_hit:
            cache_stats.hits += 1
        elif pr.error:
            cache_stats.errors += 1
        else:
            cache_stats.misses += 1

    elapsed = time.monotonic() - start_time

    return BatchResult(
        workspace_name=workspace.name,
        workspace_path=str(workspace_path),
        project_count=len(project_results),
        projects=project_results,
        cache_stats=cache_stats,
        duration_seconds=elapsed,
    )


def _run_sequential(
    tasks: list[tuple[WorkspaceProject, Path]],
    workspace_dir: Path,
    cache_dir: Path | None,
) -> list[ProjectResult]:
    """Run scans sequentially."""
    results = []
    for proj, project_path in tasks:
        result = _scan_one_project(proj, project_path, workspace_dir, cache_dir)
        results.append(result)
    return results


def _run_parallel(
    tasks: list[tuple[WorkspaceProject, Path]],
    workspace_dir: Path,
    cache_dir: Path | None,
    jobs: int,
) -> list[ProjectResult]:
    """Run scans in parallel using process pool.

    Results are returned in the original workspace order.
    """
    results: list[ProjectResult | None] = [None] * len(tasks)
    futures = []

    # Use ProcessPoolExecutor for true parallelism on Windows/Linux
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        for i, (proj, project_path) in enumerate(tasks):
            future = executor.submit(
                _scan_one_project_worker,
                project_id=proj.id,
                project_path_str=str(project_path),
                profile=proj.profile,
                config_path=proj.config,
                rules=proj.rules,
                fail_under=proj.fail_under,
                allow_failure=proj.allow_failure,
                workspace_dir_str=str(workspace_dir),
                cache_dir_str=str(cache_dir) if cache_dir else None,
            )
            futures.append((i, future))

        for i, future in futures:
            try:
                results[i] = future.result()
            except Exception as exc:
                proj, _ = tasks[i]
                results[i] = ProjectResult(
                    id=proj.id,
                    path=str(tasks[i][1]),
                    profile=proj.profile,
                    error=str(exc),
                )

    return [r for r in results if r is not None]


def _scan_one_project(
    proj: WorkspaceProject,
    project_path: Path,
    workspace_dir: Path,
    cache_dir: Path | None,
) -> ProjectResult:
    """Scan a single project."""
    return _scan_one_project_worker(
        project_id=proj.id,
        project_path_str=str(project_path),
        profile=proj.profile,
        config_path=proj.config,
        rules=proj.rules,
        fail_under=proj.fail_under,
        allow_failure=proj.allow_failure,
        workspace_dir_str=str(workspace_dir),
        cache_dir_str=str(cache_dir) if cache_dir else None,
    )


def _scan_one_project_worker(
    *,
    project_id: str,
    project_path_str: str,
    profile: str,
    config_path: str,
    rules: list[str],
    fail_under: int,
    allow_failure: bool,
    workspace_dir_str: str,
    cache_dir_str: str | None,
) -> ProjectResult:
    """Worker function for scanning a single project.

    This is a module-level function so it can be pickled for ProcessPoolExecutor.
    """
    project_path = Path(project_path_str)
    workspace_dir = Path(workspace_dir_str)
    start_time = time.monotonic()

    # Check existence
    if not project_path.exists():
        return ProjectResult(
            id=project_id,
            path=project_path_str,
            profile=profile or "default",
            error=f"Project path does not exist: {project_path_str}",
            duration_seconds=time.monotonic() - start_time,
        )

    effective_profile = profile or "default"

    # Load config and compute cache key
    config = load_config(config_path=config_path or None, repo_root=str(project_path))
    if profile:
        config.profile = profile
    for r in rules:
        resolved_r = r
        if not Path(r).is_absolute():
            resolved_r = str(workspace_dir / r)
        config.rule_packs.append(resolved_r)

    # Cache lookup
    cache_dir = Path(cache_dir_str) if cache_dir_str else None
    cache_key = ""
    if cache_dir:
        # Read config content for cache key
        config_content = ""
        if config.config_path:
            try:
                config_content = Path(config.config_path).read_text(encoding="utf-8")
            except OSError:
                pass

        rules_contents = []
        for rp in config.rule_packs:
            try:
                rules_contents.append(Path(rp).read_text(encoding="utf-8"))
            except OSError:
                rules_contents.append("")

        cache_key = compute_cache_key(
            project_path_str, effective_profile, config_content, rules_contents
        )

        cached = lookup_cache(cache_dir, project_id, cache_key)
        if cached is not None:
            # Use cached result
            summary = cached.get("summary", {})
            return ProjectResult(
                id=project_id,
                path=project_path_str,
                profile=effective_profile,
                status=summary.get("status", "unknown"),
                score=summary.get("score", 0),
                finding_counts=_count_findings(cached.get("checks", [])),
                report=cached,
                cache_hit=True,
                duration_seconds=time.monotonic() - start_time,
            )

    # Run scan
    try:
        report = run_scan(str(project_path), config)
        report_dict = report.to_dict()

        # Store in cache
        if cache_dir and cache_key:
            store_cache(cache_dir, project_id, cache_key, report_dict)

        summary = report_dict.get("summary", {})
        return ProjectResult(
            id=project_id,
            path=project_path_str,
            profile=effective_profile,
            status=summary.get("status", "unknown"),
            score=summary.get("score", 0),
            finding_counts=_count_findings(report_dict.get("checks", [])),
            report=report_dict,
            cache_hit=False,
            duration_seconds=time.monotonic() - start_time,
        )
    except Exception as exc:
        return ProjectResult(
            id=project_id,
            path=project_path_str,
            profile=effective_profile,
            error=str(exc),
            duration_seconds=time.monotonic() - start_time,
        )


def _count_findings(checks: list[dict[str, Any]]) -> dict[str, int]:
    """Count findings by severity+status combination."""
    counts = {"blocking": 0, "important": 0, "advisory": 0}
    for c in checks:
        sev = c.get("severity", "")
        status = c.get("status", "")
        if sev == "error" and status == "fail":
            counts["blocking"] += 1
        elif (sev == "warning" and status == "fail") or (sev == "error" and status == "warn"):
            counts["important"] += 1
        elif status == "warn":
            counts["advisory"] += 1
    return counts


def compute_batch_diff(
    old_batch: dict[str, Any],
    new_batch: dict[str, Any],
) -> dict[str, Any]:
    """Compute diff between two batch scan results.

    Args:
        old_batch: Old batch result dict.
        new_batch: New batch result dict.

    Returns:
        Diff dict with project_added, project_removed, score_delta, etc.
    """
    old_projects = {p["id"]: p for p in old_batch.get("projects", [])}
    new_projects = {p["id"]: p for p in new_batch.get("projects", [])}

    old_ids = set(old_projects.keys())
    new_ids = set(new_projects.keys())

    project_added = sorted(new_ids - old_ids)
    project_removed = sorted(old_ids - new_ids)
    common = sorted(old_ids & new_ids)

    project_diffs = []
    new_failures = []
    resolved_failures = []

    for pid in common:
        old_p = old_projects[pid]
        new_p = new_projects[pid]
        old_score = old_p.get("score", 0)
        new_score = new_p.get("score", 0)
        old_status = old_p.get("status", "unknown")
        new_status = new_p.get("status", "unknown")

        score_delta = new_score - old_score
        status_changed = old_status != new_status

        diff_entry: dict[str, Any] = {
            "id": pid,
            "old_score": old_score,
            "new_score": new_score,
            "score_delta": score_delta,
            "old_status": old_status,
            "new_status": new_status,
            "status_changed": status_changed,
        }
        project_diffs.append(diff_entry)

        # Track new failures and resolved failures
        if old_status in ("pass", "warn") and new_status == "fail":
            new_failures.append(pid)
        elif old_status == "fail" and new_status in ("pass", "warn"):
            resolved_failures.append(pid)

    # Average score delta
    old_avg = old_batch.get("summary", {}).get("average_score", 0)
    new_avg = new_batch.get("summary", {}).get("average_score", 0)

    return {
        "old_workspace": old_batch.get("workspace", {}).get("name", ""),
        "new_workspace": new_batch.get("workspace", {}).get("name", ""),
        "old_project_count": old_batch.get("workspace", {}).get("project_count", 0),
        "new_project_count": new_batch.get("workspace", {}).get("project_count", 0),
        "project_added": project_added,
        "project_removed": project_removed,
        "project_diffs": project_diffs,
        "new_failures": new_failures,
        "resolved_failures": resolved_failures,
        "old_average_score": old_avg,
        "new_average_score": new_avg,
        "average_score_delta": round(new_avg - old_avg, 1),
    }


def format_batch_diff_markdown(diff: dict[str, Any]) -> str:
    """Format batch diff as Markdown."""
    lines = ["# Batch Report Diff\n"]

    # Summary
    lines.append("## Summary\n")
    lines.append("| Metric | Old | New | Delta |")
    lines.append("|--------|-----|-----|-------|")
    lines.append(
        f"| Projects | {diff['old_project_count']} | {diff['new_project_count']} | "
        f"{diff['new_project_count'] - diff['old_project_count']:+d} |"
    )
    lines.append(
        f"| Average Score | {diff['old_average_score']} | {diff['new_average_score']} | "
        f"{diff['average_score_delta']:+.1f} |"
    )
    lines.append("")

    # Added projects
    if diff["project_added"]:
        lines.append(f"## Projects Added ({len(diff['project_added'])})\n")
        for pid in diff["project_added"]:
            lines.append(f"- `{pid}`")
        lines.append("")

    # Removed projects
    if diff["project_removed"]:
        lines.append(f"## Projects Removed ({len(diff['project_removed'])})\n")
        for pid in diff["project_removed"]:
            lines.append(f"- `{pid}`")
        lines.append("")

    # Project score changes
    if diff["project_diffs"]:
        lines.append("## Project Changes\n")
        lines.append("| Project | Old Score | New Score | Delta | Old Status | New Status |")
        lines.append("|---------|-----------|-----------|-------|------------|------------|")
        for d in diff["project_diffs"]:
            lines.append(
                f"| `{d['id']}` | {d['old_score']} | {d['new_score']} | "
                f"{d['score_delta']:+d} | {d['old_status']} | {d['new_status']} |"
            )
        lines.append("")

    # New failures
    if diff["new_failures"]:
        lines.append(f"## New Failures ({len(diff['new_failures'])})\n")
        for pid in diff["new_failures"]:
            lines.append(f"- `{pid}`")
        lines.append("")

    # Resolved failures
    if diff["resolved_failures"]:
        lines.append(f"## Resolved Failures ({len(diff['resolved_failures'])})\n")
        for pid in diff["resolved_failures"]:
            lines.append(f"- `{pid}`")
        lines.append("")

    if not any([diff["project_added"], diff["project_removed"],
                diff["project_diffs"], diff["new_failures"],
                diff["resolved_failures"]]):
        lines.append("No changes detected.\n")

    return "\n".join(lines)
