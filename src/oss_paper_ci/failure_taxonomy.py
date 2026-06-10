"""Failure taxonomy for human-centered reproducibility guidance.

Provides structured failure types with explanations, likely causes,
suggested next steps, and role-specific guidance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FailureType:
    """A structured failure type with human-readable guidance."""

    id: str
    short_explanation: str
    likely_causes: list[str]
    suggested_next_steps: list[str]
    what_this_does_not_mean: list[str]
    severity: str  # "info", "warning", "error"
    role_guidance: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "short_explanation": self.short_explanation,
            "likely_causes": self.likely_causes,
            "suggested_next_steps": self.suggested_next_steps,
            "what_this_does_not_mean": self.what_this_does_not_mean,
            "severity": self.severity,
            "role_guidance": self.role_guidance,
        }


FAILURE_TYPES: list[FailureType] = [
    FailureType(
        id="source_resolution_failed",
        short_explanation="The repository URL or path could not be resolved to a clonable source.",
        likely_causes=[
            "The URL is malformed or incomplete",
            "The repository is private and not accessible",
            "A paper URL was provided without a --repo flag",
            "The local path does not exist",
        ],
        suggested_next_steps=[
            "Check the URL format (https://github.com/owner/repo)",
            "For paper URLs, use --repo to specify the code repository",
            "For local paths, verify the directory exists",
        ],
        what_this_does_not_mean=[
            "This does not mean the paper has no code",
            "This does not mean the research is flawed",
        ],
        severity="error",
        role_guidance={
            "author": "Ensure your repository URL is publicly accessible and correctly formatted.",
            "reviewer": "Ask the author for the correct repository URL.",
            "maintainer": "Check if the repository is in your organization's access list.",
        },
    ),
    FailureType(
        id="environment_missing",
        short_explanation="No environment files (requirements.txt, pyproject.toml, etc.) were found in the repository.",
        likely_causes=[
            "The repository does not declare its dependencies",
            "Dependencies are declared in an unsupported format",
            "The environment file is in a subdirectory",
        ],
        suggested_next_steps=[
            "Check if the repository has a requirements.txt or pyproject.toml",
            "If using conda, check for environment.yml",
            "Contact the author to add dependency declarations",
        ],
        what_this_does_not_mean=[
            "This does not mean the code cannot run",
            "This does not mean the research is invalid",
        ],
        severity="warning",
        role_guidance={
            "author": "Add a requirements.txt or pyproject.toml to declare dependencies.",
            "reviewer": "Note this as a reproducibility concern in your review.",
            "maintainer": "Consider adding a policy that requires dependency declarations.",
        },
    ),
    FailureType(
        id="dependency_install_failed",
        short_explanation="Dependencies could not be installed in the isolated environment.",
        likely_causes=[
            "A package is not available on PyPI",
            "Version conflicts between packages",
            "The package requires system-level dependencies (C libraries, etc.)",
            "Network issues during installation",
        ],
        suggested_next_steps=[
            "Check the error output for specific package failures",
            "Try installing manually in a clean environment",
            "Check if the package requires system dependencies",
        ],
        what_this_does_not_mean=[
            "This does not mean the code is broken",
            "This may be an environment-specific issue, not a code issue",
        ],
        severity="error",
        role_guidance={
            "author": "Test installation in a clean environment and document system dependencies.",
            "reviewer": "Note which packages failed and whether they are standard.",
            "maintainer": "Check if your CI environment has the required system packages.",
        },
    ),
    FailureType(
        id="command_not_declared",
        short_explanation="No reproduction command was found in the repository configuration.",
        likely_causes=[
            "No reproducibility.yml or .oss-paper-ci.yml exists",
            "No common scripts (scripts/train.py, etc.) were found",
            "The command is not documented",
        ],
        suggested_next_steps=[
            "Use --command to specify the reproduction command manually",
            "Check the README for reproduction instructions",
            "Ask the author to add a reproducibility.yml",
        ],
        what_this_does_not_mean=[
            "This does not mean the code cannot be reproduced",
            "The author may have documented reproduction steps elsewhere",
        ],
        severity="warning",
        role_guidance={
            "author": "Add a reproducibility.yml with your experiment commands.",
            "reviewer": "Check the README for manual reproduction instructions.",
            "maintainer": "Require reproducibility.yml in your repository template.",
        },
    ),
    FailureType(
        id="command_timeout",
        short_explanation="The reproduction command exceeded the time limit.",
        likely_causes=[
            "The command requires more time than the default timeout",
            "The command is waiting for user input",
            "The command is stuck in an infinite loop",
            "The command requires more resources than available",
        ],
        suggested_next_steps=[
            "Increase the timeout with --timeout N",
            "Check if the command requires interactive input",
            "Check if the command requires GPU or special hardware",
        ],
        what_this_does_not_mean=[
            "This does not mean the code is broken",
            "The command may work with more time or resources",
        ],
        severity="warning",
        role_guidance={
            "author": "Document expected runtime and resource requirements.",
            "reviewer": "Note if the runtime is reasonable for the research.",
            "maintainer": "Set appropriate timeout limits for your CI.",
        },
    ),
    FailureType(
        id="command_failed",
        short_explanation="The reproduction command returned a non-zero exit code.",
        likely_causes=[
            "A runtime error occurred in the code",
            "Missing input data or files",
            "Incorrect file paths or configuration",
            "Incompatible Python or library versions",
        ],
        suggested_next_steps=[
            "Check the stderr output for error messages",
            "Verify that all required input files exist",
            "Check Python and library version compatibility",
            "Try running the command manually to see the full error",
        ],
        what_this_does_not_mean=[
            "This does not necessarily mean the paper's claims are wrong",
            "This may be an environment-specific issue",
            "The code may work in a different environment",
        ],
        severity="error",
        role_guidance={
            "author": "Fix the error and test in a clean environment.",
            "reviewer": "Note the specific error and whether it affects the paper's claims.",
            "maintainer": "Check if the error is environment-specific.",
        },
    ),
    FailureType(
        id="artifact_missing",
        short_explanation="Expected output files were not generated by the reproduction command.",
        likely_causes=[
            "The command did not complete successfully",
            "The output path is different than expected",
            "The command generates outputs in a different location",
        ],
        suggested_next_steps=[
            "Check if the command completed successfully",
            "Look for output files in alternative locations",
            "Check the command's documentation for output paths",
        ],
        what_this_does_not_mean=[
            "This does not mean the research failed",
            "The outputs may exist in a different location",
        ],
        severity="warning",
        role_guidance={
            "author": "Document expected output paths in reproducibility.yml.",
            "reviewer": "Check if outputs are generated in alternative locations.",
            "maintainer": "Require output path documentation.",
        },
    ),
    FailureType(
        id="scan_blocking_findings",
        short_explanation="The repository scan found issues that block reproducibility.",
        likely_causes=[
            "Missing README, license, or citation information",
            "No environment files or dependency declarations",
            "No experiment scripts or entry points",
            "Missing data documentation",
        ],
        suggested_next_steps=[
            "Review the scan report for specific findings",
            "Address blocking issues first (errors), then warnings",
            "Use oss-paper-ci init to scaffold missing files",
        ],
        what_this_does_not_mean=[
            "This does not mean the research is bad",
            "This means the repository lacks engineering basics for reproducibility",
        ],
        severity="error",
        role_guidance={
            "author": "Address the blocking findings to improve reproducibility readiness.",
            "reviewer": "Use the scan report to assess reproducibility readiness.",
            "maintainer": "Set minimum score thresholds for your repositories.",
        },
    ),
    FailureType(
        id="capsule_integrity_failed",
        short_explanation="The reproduction capsule failed integrity verification.",
        likely_causes=[
            "The capsule was modified after creation",
            "The capsule was corrupted during transfer",
            "The capsule was created with a different tool version",
        ],
        suggested_next_steps=[
            "Re-generate the capsule from the original reproduction",
            "Verify the capsule was not modified after creation",
            "Check that the capsule was created with the same oss-paper-ci version",
        ],
        what_this_does_not_mean=[
            "This does not mean the reproduction failed",
            "This means the evidence package cannot be verified",
        ],
        severity="error",
        role_guidance={
            "author": "Re-generate the capsule and verify before sharing.",
            "reviewer": "Request a new capsule if integrity fails.",
            "maintainer": "Archive capsules with integrity verification.",
        },
    ),
    FailureType(
        id="unsupported_environment",
        short_explanation="The repository requires an environment that cannot be provided automatically.",
        likely_causes=[
            "Requires conda instead of pip",
            "Requires GPU hardware",
            "Requires external data that must be downloaded separately",
            "Requires system-level packages not available",
        ],
        suggested_next_steps=[
            "Check the repository's documentation for manual setup",
            "Install conda and use the environment.yml",
            "Download required data manually",
            "Set up the required hardware environment",
        ],
        what_this_does_not_mean=[
            "This does not mean the research is not reproducible",
            "This means automated reproduction is not possible in this environment",
        ],
        severity="warning",
        role_guidance={
            "author": "Document all environment requirements clearly.",
            "reviewer": "Note if the requirements are reasonable for the research.",
            "maintainer": "Provide the required environment in your CI.",
        },
    ),
]

# Index by ID for quick lookup
FAILURE_TYPE_INDEX: dict[str, FailureType] = {ft.id: ft for ft in FAILURE_TYPES}


def get_failure_type(failure_id: str) -> FailureType | None:
    """Get a failure type by ID."""
    return FAILURE_TYPE_INDEX.get(failure_id)


def get_all_failure_types() -> list[FailureType]:
    """Get all failure types."""
    return FAILURE_TYPES


def format_failure_guidance(failure_id: str, role: str | None = None) -> str:
    """Format human-readable guidance for a failure type."""
    ft = get_failure_type(failure_id)
    if ft is None:
        return f"Unknown failure type: {failure_id}"

    lines = [f"## {ft.id}\n"]
    lines.append(f"{ft.short_explanation}\n")

    lines.append("**Likely causes:**")
    for cause in ft.likely_causes:
        lines.append(f"- {cause}")
    lines.append("")

    lines.append("**Suggested next steps:**")
    for step in ft.suggested_next_steps:
        lines.append(f"- {step}")
    lines.append("")

    lines.append("**What this does not mean:**")
    for item in ft.what_this_does_not_mean:
        lines.append(f"- {item}")
    lines.append("")

    if role and role in ft.role_guidance:
        lines.append(f"**For {role}s:**")
        lines.append(f"- {ft.role_guidance[role]}")
        lines.append("")

    return "\n".join(lines)
