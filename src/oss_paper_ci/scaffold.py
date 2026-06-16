"""Scaffold engine for generating reproducibility file skeletons.

Provides dry-run preview and safe apply modes for scaffolding
missing reproducibility files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from oss_paper_ci.adoption import AdoptionPlan, PatchItem, build_adoption_plan
from oss_paper_ci.safe_write import (
    WriteAction, ApplyResult, apply_multiple, preview_write, validate_path,
)
from oss_paper_ci.templates import get_scaffold_templates, ScaffoldTemplate


@dataclass
class ScaffoldResult:
    """Result of a scaffold operation."""
    plan: AdoptionPlan = field(default_factory=AdoptionPlan)
    apply_result: ApplyResult | None = None
    dry_run: bool = True
    output_dir: str = ""

    def to_dict(self) -> dict:
        d = {
            "plan": self.plan.to_dict(),
            "dry_run": self.dry_run,
        }
        if self.apply_result:
            d["apply"] = {
                "total_attempted": self.apply_result.total_attempted,
                "total_written": self.apply_result.total_written,
                "total_skipped": self.apply_result.total_skipped,
                "total_errors": self.apply_result.total_errors,
                "results": [
                    {"path": r.path, "success": r.success, "action": r.action, "message": r.message}
                    for r in self.apply_result.results
                ],
            }
        return d


def run_scaffold(
    repo_path: str = ".",
    ecosystems: list[dict] | None = None,
    scan_data: dict | None = None,
    dry_run: bool = True,
    force: bool = False,
    output_dir: str = "",
) -> ScaffoldResult:
    """Run the scaffold engine.

    Args:
        repo_path: Path to the repository root.
        ecosystems: Detected ecosystems.
        scan_data: Scan report data.
        dry_run: If True, only preview, don't write.
        force: Allow overwriting existing files.
        output_dir: Directory to write scaffold output (for --apply).

    Returns:
        ScaffoldResult with plan and apply results.
    """
    repo = Path(repo_path).resolve()

    # Build adoption plan
    plan = build_adoption_plan(
        repo_path=repo_path,
        ecosystems=ecosystems,
        scan_data=scan_data,
    )

    # Get templates
    templates = get_scaffold_templates(
        ecosystems=ecosystems,
    )

    # Filter templates to only missing files
    applicable = []
    for tmpl in templates:
        target = repo / tmpl.path
        if not target.exists() or force:
            applicable.append(tmpl)

    # Build write actions
    actions = []
    for tmpl in applicable:
        actions.append(WriteAction(
            path=tmpl.path,
            content=tmpl.content,
            action="create",
            reason=tmpl.description,
            risk=tmpl.risk,
        ))

    # Apply or preview
    if dry_run:
        result = ScaffoldResult(plan=plan, dry_run=True)
    else:
        apply_result = apply_multiple(
            actions=actions,
            repo_root=str(repo),
            force=force,
            dry_run=False,
        )
        result = ScaffoldResult(plan=plan, apply_result=apply_result, dry_run=False)

    return result


def generate_scaffold_patch(
    repo_path: str = ".",
    ecosystems: list[dict] | None = None,
) -> str:
    """Generate a unified diff-style patch preview.

    Returns a markdown-formatted preview of what would be scaffolded.
    """
    repo = Path(repo_path).resolve()
    templates = get_scaffold_templates(ecosystems=ecosystems)

    lines = ["# Scaffold Patch Preview", ""]
    lines.append(f"Repository: `{repo}`")
    lines.append("")

    for tmpl in templates:
        target = repo / tmpl.path
        exists = target.exists()

        lines.append(f"## {tmpl.path}")
        lines.append("")
        if exists:
            lines.append(f"**Status:** Already exists (skipped)")
        else:
            lines.append(f"**Status:** Would create")
        lines.append(f"**Risk:** {tmpl.risk}")
        lines.append(f"**Description:** {tmpl.description}")
        lines.append("")
        lines.append("```")
        content_lines = tmpl.content.split("\n")
        for line in content_lines[:15]:
            lines.append(line)
        if len(content_lines) > 15:
            lines.append(f"... ({len(content_lines) - 15} more lines)")
        lines.append("```")
        lines.append("")

    return "\n".join(lines)
