"""Adoption plan generation.

Analyzes a repository and generates a structured adoption plan
with missing files, recommended scaffolds, and patch items.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PatchItem:
    """A single patch item in an adoption plan."""
    id: str
    title: str
    path: str
    action: str  # "create", "modify", "skip"
    reason: str
    preview: str = ""
    risk: str = "low"
    requires_confirmation: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "path": self.path,
            "action": self.action,
            "reason": self.reason,
            "risk": self.risk,
            "requires_confirmation": self.requires_confirmation,
        }


@dataclass
class AdoptionPlan:
    """A structured adoption plan for a repository."""
    schema_version: str = "0.1"
    plan_type: str = "oss-paper-ci-adoption-plan"
    repo: str = "."
    detected_ecosystems: list[dict] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    recommended_files: list[str] = field(default_factory=list)
    patches: list[PatchItem] = field(default_factory=list)
    manual_steps: list[str] = field(default_factory=list)
    safety: dict = field(default_factory=lambda: {
        "dry_run": True,
        "will_overwrite": False,
        "requires_apply": True,
    })

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "plan_type": self.plan_type,
            "repo": self.repo,
            "detected_ecosystems": self.detected_ecosystems,
            "missing_files": self.missing_files,
            "recommended_files": self.recommended_files,
            "patches": [p.to_dict() for p in self.patches],
            "manual_steps": self.manual_steps,
            "safety": self.safety,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def _check_file_exists(repo: Path, path: str) -> bool:
    """Check if a file exists in the repo."""
    return (repo / path).exists()


def build_adoption_plan(
    repo_path: str = ".",
    ecosystems: list[dict] | None = None,
    scan_data: dict | None = None,
) -> AdoptionPlan:
    """Build an adoption plan for a repository.

    Args:
        repo_path: Path to the repository root.
        ecosystems: Detected ecosystems from detect_ecosystems().
        scan_data: Scan report data (optional).

    Returns:
        AdoptionPlan with missing files and recommended patches.
    """
    repo = Path(repo_path).resolve()
    plan = AdoptionPlan(repo=str(repo))

    # Store detected ecosystems
    if ecosystems:
        plan.detected_ecosystems = [
            {"id": e.get("id", ""), "display_name": e.get("display_name", "")}
            for e in ecosystems
        ]

    # Check for key files
    checks = [
        ("reproducibility.yml", "Reproducibility contract", "reproducibility-yml"),
        ("oss-paper-ci.yml", "OSS-Paper-CI configuration", "oss-paper-ci-yml"),
        ("data/README.md", "Data documentation", "data-readme"),
        ("results/README.md", "Results documentation", "results-readme"),
        ("figures/README.md", "Figures documentation", "figures-readme"),
        (".github/workflows/oss-paper-ci.yml", "CI workflow", "github-workflow"),
        ("README.md", "Project README", None),
        ("requirements.txt", "Python dependencies", None),
        ("LICENSE", "License file", None),
    ]

    for file_path, description, patch_id in checks:
        if _check_file_exists(repo, file_path):
            plan.recommended_files.append(file_path)
        else:
            plan.missing_files.append(file_path)
            if patch_id:
                plan.patches.append(PatchItem(
                    id=patch_id,
                    title=f"Add {file_path}",
                    path=file_path,
                    action="create",
                    reason=f"Missing {description.lower()}",
                    risk="low",
                ))

    # Check ecosystem-specific files
    if ecosystems:
        eco = ecosystems[0] if ecosystems else {}
        eco_id = eco.get("id", "")

        if eco_id == "python":
            if not _check_file_exists(repo, "requirements.txt") and \
               not _check_file_exists(repo, "pyproject.toml"):
                plan.manual_steps.append(
                    "Add requirements.txt or pyproject.toml with Python dependencies"
                )
        elif eco_id == "r":
            if not _check_file_exists(repo, "renv.lock"):
                plan.manual_steps.append(
                    "Consider adding renv.lock for reproducible R environment"
                )
        elif eco_id == "julia":
            if not _check_file_exists(repo, "Project.toml"):
                plan.manual_steps.append(
                    "Add Project.toml with Julia project dependencies"
                )
        elif eco_id == "node":
            if not _check_file_exists(repo, "package.json"):
                plan.manual_steps.append(
                    "Add package.json with Node.js dependencies"
                )

    # Add manual steps from scan data
    if scan_data:
        checks_list = scan_data.get("checks", [])
        for check in checks_list:
            if check.get("status") in ("fail", "warn"):
                rec = check.get("recommendation", "")
                if rec and rec not in plan.manual_steps:
                    plan.manual_steps.append(rec)

    return plan


def format_adoption_plan_markdown(plan: AdoptionPlan) -> str:
    """Format adoption plan as markdown."""
    lines = ["# Adoption Plan", ""]
    lines.append(f"**Repository:** `{plan.repo}`")
    lines.append("")

    # Detected ecosystems
    if plan.detected_ecosystems:
        lines.append("## Detected Ecosystems")
        lines.append("")
        for eco in plan.detected_ecosystems:
            lines.append(f"- {eco.get('display_name', eco.get('id', 'unknown'))}")
        lines.append("")

    # Missing files
    if plan.missing_files:
        lines.append("## Missing Files")
        lines.append("")
        for f in plan.missing_files:
            lines.append(f"- `{f}`")
        lines.append("")

    # Recommended patches
    if plan.patches:
        lines.append("## Recommended Scaffolds")
        lines.append("")
        for p in plan.patches:
            lines.append(f"- **{p.title}** (`{p.path}`) — {p.reason}")
        lines.append("")

    # Manual steps
    if plan.manual_steps:
        lines.append("## Manual Steps")
        lines.append("")
        for i, step in enumerate(plan.manual_steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    # Safety
    lines.append("## Safety")
    lines.append("")
    lines.append("- Default mode is **dry-run**: no files will be modified")
    lines.append("- Use `--apply` to write scaffold files")
    lines.append("- Existing files are never overwritten without `--force`")
    lines.append("")

    return "\n".join(lines)
