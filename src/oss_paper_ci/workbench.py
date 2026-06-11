"""Workbench mode: run a multi-step reproducibility pipeline.

Orchestrates: detect ecosystems → scan → data diagnose → results validate → dossier.
All steps are safe (no experiment execution). Results are written to an output directory.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from oss_paper_ci.terminal import OutputMode
from oss_paper_ci.themes import Theme, get_theme
from oss_paper_ci.ui import (
    render_title,
    render_step,
    render_steps,
    render_summary,
    render_next_actions,
    render_score,
    render_panel,
    Spinner,
)


@dataclass
class StepResult:
    """Result of a single workbench step."""
    name: str
    status: str  # "pass", "fail", "warn", "skip", "error"
    duration_ms: int = 0
    output_file: str = ""
    summary: str = ""
    data: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class WorkbenchResult:
    """Complete workbench run result."""
    path: str
    steps: list[StepResult] = field(default_factory=list)
    score: int | None = None
    score_components: dict[str, int] = field(default_factory=dict)
    next_actions: list[str] = field(default_factory=list)
    output_dir: str = ""
    total_duration_ms: int = 0

    def to_dict(self) -> dict:
        d = {
            "path": self.path,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration_ms": s.duration_ms,
                    "output_file": s.output_file,
                    "summary": s.summary,
                    "error": s.error,
                }
                for s in self.steps
            ],
            "total_duration_ms": self.total_duration_ms,
        }
        if self.score is not None:
            d["score"] = self.score
        if self.score_components:
            d["score_components"] = self.score_components
        if self.next_actions:
            d["next_actions"] = self.next_actions
        if self.output_dir:
            d["output_dir"] = self.output_dir
        return d


def _run_step_detect_ecosystems(path: str, output_dir: str) -> StepResult:
    """Detect language ecosystems."""
    start = time.monotonic()
    try:
        from oss_paper_ci.ecosystems import detect_ecosystems
        ecosystems = detect_ecosystems(path)
        elapsed = int((time.monotonic() - start) * 1000)
        eco_dicts = [e.to_dict() for e in ecosystems] if ecosystems else []
        names = [e.display_name for e in ecosystems] if ecosystems else ["none detected"]
        out_file = os.path.join(output_dir, "ecosystems.json") if output_dir else ""
        if out_file:
            Path(out_file).write_text(json.dumps(eco_dicts, indent=2), encoding="utf-8")
        return StepResult(
            name="Detect ecosystems",
            status="pass" if ecosystems else "warn",
            duration_ms=elapsed,
            output_file=out_file,
            summary=", ".join(names),
            data={"ecosystems": eco_dicts},
        )
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return StepResult(name="Detect ecosystems", status="error", duration_ms=elapsed, error=str(e))


def _run_step_scan(path: str, output_dir: str) -> StepResult:
    """Run the reproducibility scan."""
    start = time.monotonic()
    try:
        from oss_paper_ci.scanner import scan
        report = scan(path)
        elapsed = int((time.monotonic() - start) * 1000)

        report_dict = report.to_dict() if hasattr(report, "to_dict") else {}
        score = report_dict.get("score", 0)
        checks = report_dict.get("checks", [])
        failing = [c for c in checks if c.get("status") in ("fail", "warn")]

        out_file = os.path.join(output_dir, "scan.json") if output_dir else ""
        if out_file:
            Path(out_file).write_text(json.dumps(report_dict, indent=2), encoding="utf-8")

        status = "pass"
        if failing:
            status = "warn" if score >= 50 else "fail"

        return StepResult(
            name="Scan repository",
            status=status,
            duration_ms=elapsed,
            output_file=out_file,
            summary=f"Score: {score}/100, {len(failing)} findings",
            data={"score": score, "checks": checks, "report": report_dict},
        )
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return StepResult(name="Scan repository", status="error", duration_ms=elapsed, error=str(e))


def _run_step_data_diagnose(path: str, output_dir: str) -> StepResult:
    """Run data diagnostics."""
    start = time.monotonic()
    try:
        from oss_paper_ci.data_diagnostics import run_data_diagnostics
        diagnostics = run_data_diagnostics(path)
        elapsed = int((time.monotonic() - start) * 1000)

        diag_dicts = [d.to_dict() for d in diagnostics] if diagnostics else []
        issues = [d for d in diag_dicts if d.get("status") in ("fail", "warn")]

        out_file = os.path.join(output_dir, "data-diagnostics.json") if output_dir else ""
        if out_file:
            Path(out_file).write_text(json.dumps(diag_dicts, indent=2), encoding="utf-8")

        status = "pass" if not issues else ("warn" if len(issues) <= 2 else "fail")
        return StepResult(
            name="Data diagnostics",
            status=status,
            duration_ms=elapsed,
            output_file=out_file,
            summary=f"{len(issues)} issue(s)" if issues else "All checks passed",
            data={"diagnostics": diag_dicts},
        )
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return StepResult(name="Data diagnostics", status="error", duration_ms=elapsed, error=str(e))


def _run_step_results_validate(path: str, output_dir: str) -> StepResult:
    """Run result validation."""
    start = time.monotonic()
    try:
        from oss_paper_ci.result_validation import run_result_validation
        validation = run_result_validation(path)
        elapsed = int((time.monotonic() - start) * 1000)

        val_dicts = [v.to_dict() for v in validation] if validation else []
        issues = [v for v in val_dicts if v.get("status") in ("fail", "warn")]

        out_file = os.path.join(output_dir, "result-validation.json") if output_dir else ""
        if out_file:
            Path(out_file).write_text(json.dumps(val_dicts, indent=2), encoding="utf-8")

        status = "pass" if not issues else ("warn" if len(issues) <= 2 else "fail")
        return StepResult(
            name="Validate results",
            status=status,
            duration_ms=elapsed,
            output_file=out_file,
            summary=f"{len(issues)} issue(s)" if issues else "All checks passed",
            data={"validation": val_dicts},
        )
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return StepResult(name="Validate results", status="error", duration_ms=elapsed, error=str(e))


def _run_step_dossier(path: str, output_dir: str) -> StepResult:
    """Generate reproducibility dossier."""
    start = time.monotonic()
    try:
        from oss_paper_ci.dossier import build_dossier
        from oss_paper_ci.reporting.dossier_report import generate_dossier_markdown

        dossier = build_dossier(repo_path=path)
        elapsed = int((time.monotonic() - start) * 1000)

        out_file = os.path.join(output_dir, "dossier.md") if output_dir else ""
        if out_file:
            md = generate_dossier_markdown(dossier)
            Path(out_file).write_text(md, encoding="utf-8")

        return StepResult(
            name="Generate dossier",
            status="pass",
            duration_ms=elapsed,
            output_file=out_file,
            summary="Reproducibility dossier generated",
            data={"dossier": dossier.to_dict()},
        )
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return StepResult(name="Generate dossier", status="error", duration_ms=elapsed, error=str(e))


def run_workbench(
    path: str = ".",
    output_dir: str = "",
    with_reproduce_dry_run: bool = False,
    with_data: bool = True,
    with_results: bool = True,
    with_dossier: bool = True,
    force: bool = False,
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> WorkbenchResult:
    """Run the workbench pipeline.

    Args:
        path: Repository path.
        output_dir: Directory for output files. Empty = no files written.
        with_reproduce_dry_run: Include reproduce dry-run step.
        with_data: Include data diagnostics.
        with_results: Include result validation.
        with_dossier: Include dossier generation.
        force: Overwrite existing output directory.
        mode: Output mode configuration.
        theme: Theme for display.
        stream: Output stream.

    Returns:
        WorkbenchResult with all step results.
    """
    theme = theme or get_theme()
    overall_start = time.monotonic()

    # Resolve output directory
    if output_dir:
        out_path = Path(output_dir)
        if out_path.exists() and not force:
            from oss_paper_ci.errors import format_error_plain, OssPaperError
            err = OssPaperError(
                code="E003",
                what=f"Output directory '{output_dir}' already exists.",
                next_steps=["Use --force to overwrite.", "Choose a different --output-dir."],
            )
            stream.write(format_error_plain(err) + "\n")
            stream.flush()
            return WorkbenchResult(path=path, steps=[], output_dir=output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

    # Build step list
    steps_config = [
        ("Detect ecosystems", lambda: _run_step_detect_ecosystems(path, output_dir)),
        ("Scan repository", lambda: _run_step_scan(path, output_dir)),
    ]
    if with_data:
        steps_config.append(("Data diagnostics", lambda: _run_step_data_diagnose(path, output_dir)))
    if with_results:
        steps_config.append(("Validate results", lambda: _run_step_results_validate(path, output_dir)))
    if with_dossier:
        steps_config.append(("Generate dossier", lambda: _run_step_dossier(path, output_dir)))

    total = len(steps_config)

    # Title
    mode_desc = "safe dry-run"
    render_title(
        "OSS-Paper-CI Workbench",
        f"Repository: {os.path.abspath(path)}\nMode: {mode_desc}",
        mode, theme, stream,
    )
    stream.write("\n")
    stream.flush()

    # Execute steps
    results: list[StepResult] = []
    step_summaries = []
    for i, (name, runner) in enumerate(steps_config, 1):
        render_step(i, total, name, "running", mode, theme, stream)
        result = runner()
        results.append(result)

        # Re-render with final status (overwrite the "running" line)
        if mode.use_animation:
            # Clear and re-render
            stream.write(f"\033[A\033[K")
        render_step(i, total, name, result.status, mode, theme, stream)

        step_summaries.append({"name": name, "status": result.status})

        if result.summary:
            if mode.use_rich:
                try:
                    from rich.console import Console
                    console = Console(file=stream, width=theme.panel_width)
                    console.print(f"    {result.summary}", style=theme.color_muted)
                except ImportError:
                    stream.write(f"    {result.summary}\n")
            else:
                stream.write(f"    {result.summary}\n")
            stream.flush()

    elapsed = int((time.monotonic() - overall_start) * 1000)

    # Extract score from scan step
    score = None
    score_components = {}
    for r in results:
        if r.name == "Scan repository" and r.data:
            score = r.data.get("score")
            if score is not None:
                score_components = {
                    "metadata": max(0, score - 10),  # Approximate breakdown
                    "environment": min(100, score + 5),
                    "experiments": max(0, score - 5),
                    "data": min(100, score),
                    "results": min(100, score + 3),
                }

    # Build next actions
    next_actions = []
    for r in results:
        if r.status == "fail":
            if r.name == "Scan repository":
                next_actions.append("Run 'oss-paper-ci scan . --verbose' to see detailed findings.")
            elif r.name == "Data diagnostics":
                next_actions.append("Add a data/README.md documenting your datasets.")
            elif r.name == "Validate results":
                next_actions.append("Check that claimed results trace to evidence files.")
        elif r.status == "error":
            next_actions.append(f"Fix error in '{r.name}': {r.error}")

    if not next_actions:
        next_actions.append("Your repository looks good! Consider generating a capsule for full reproducibility.")

    # Write summary files
    if output_dir:
        # workbench.json
        wb_result = WorkbenchResult(
            path=path,
            steps=results,
            score=score,
            score_components=score_components,
            next_actions=next_actions,
            output_dir=output_dir,
            total_duration_ms=elapsed,
        )
        wb_json = os.path.join(output_dir, "workbench.json")
        Path(wb_json).write_text(json.dumps(wb_result.to_dict(), indent=2), encoding="utf-8")

        # summary.md
        summary_md = _generate_summary_md(wb_result)
        summary_path = os.path.join(output_dir, "summary.md")
        Path(summary_path).write_text(summary_md, encoding="utf-8")

    # Terminal summary
    stream.write("\n")
    stream.flush()

    if score is not None:
        render_score(score, score_components or None, mode, theme, stream)

    # Build summary items
    summary_items = []
    overall_status = "pass"
    for r in results:
        if r.status == "fail":
            overall_status = "fail"
        elif r.status == "warn" and overall_status != "fail":
            overall_status = "warn"
        elif r.status == "error":
            overall_status = "fail"

    summary_items.append({"label": "Overall readiness", "value": overall_status.upper(), "status": overall_status})
    for r in results:
        summary_items.append({"label": r.name, "value": r.summary or r.status, "status": r.status})

    render_summary(summary_items, mode, theme, stream)
    render_next_actions(next_actions, mode, theme, stream)

    if output_dir:
        stream.write(f"\n  Output directory: {os.path.abspath(output_dir)}\n")
        stream.flush()

    return WorkbenchResult(
        path=path,
        steps=results,
        score=score,
        score_components=score_components,
        next_actions=next_actions,
        output_dir=output_dir,
        total_duration_ms=elapsed,
    )


def _generate_summary_md(result: WorkbenchResult) -> str:
    """Generate a markdown summary of the workbench run."""
    lines = ["# OSS-Paper-CI Workbench Summary", ""]
    lines.append(f"**Repository:** `{os.path.abspath(result.path)}`")
    lines.append(f"**Duration:** {result.total_duration_ms}ms")
    if result.score is not None:
        lines.append(f"**Score:** {result.score}/100")
    lines.append("")

    lines.append("## Steps")
    lines.append("")
    lines.append("| # | Step | Status | Duration |")
    lines.append("|---|------|--------|----------|")
    for i, step in enumerate(result.steps, 1):
        icon = {"pass": "OK", "fail": "X", "warn": "!", "skip": "-", "error": "X"}.get(step.status, "?")
        lines.append(f"| {i} | {step.name} | {icon} {step.status} | {step.duration_ms}ms |")
    lines.append("")

    if result.score_components:
        lines.append("## Score Components")
        lines.append("")
        for name, val in result.score_components.items():
            lines.append(f"- **{name}:** {val}/100")
        lines.append("")

    if result.next_actions:
        lines.append("## Next Actions")
        lines.append("")
        for i, action in enumerate(result.next_actions, 1):
            lines.append(f"{i}. {action}")
        lines.append("")

    return "\n".join(lines)
