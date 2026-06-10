"""Human-centered guidance for oss-paper-ci.

Provides guided entry points, role-based recommendations,
topic walkthroughs, and plain-language summaries.
"""

from __future__ import annotations

from typing import Any

from oss_paper_ci.failure_taxonomy import (
    FAILURE_TYPES,
    format_failure_guidance,
    get_all_failure_types,
)


# Role definitions
ROLES = {
    "author": {
        "name": "Paper/Project Author",
        "description": "I want my repository to be easier to reproduce.",
        "recommended_commands": [
            ("oss-paper-ci scan .", "Check your repository's reproducibility readiness"),
            ("oss-paper-ci init --contract", "Create a reproducibility contract"),
            ("oss-paper-ci guide --topic scan", "Learn about scanning"),
            ("oss-paper-ci guide --topic reproduce", "Learn about reproduction"),
            ("oss-paper-ci guide --topic capsule", "Learn about capsules"),
        ],
        "key_concerns": [
            "Make your repository easy for others to understand and run",
            "Document dependencies, data, and experiment commands",
            "Provide a reproducibility.yml with clear instructions",
        ],
        "warnings": [
            "A high scan score does not prove your paper is correct",
            "Reproduction success depends on the environment, not just the code",
        ],
    },
    "reviewer": {
        "name": "Reviewer / Reader",
        "description": "I want to assess whether a repository provides enough evidence for reproducibility.",
        "recommended_commands": [
            ("oss-paper-ci scan <repo>", "Check the repository's reproducibility readiness"),
            ("oss-paper-ci reproduce <repo> --dry-run", "See what reproduction would involve"),
            ("oss-paper-ci capsule verify <capsule.zip>", "Verify a reproduction capsule"),
            ("oss-paper-ci guide --topic scan", "Learn about scanning"),
        ],
        "key_concerns": [
            "Check if the repository has clear dependency declarations",
            "Check if experiment commands are documented",
            "Check if the scan report shows blocking issues",
        ],
        "warnings": [
            "Scan results reflect engineering readiness, not scientific quality",
            "A low score does not mean the research is flawed",
            "Reproduction attempts are evidence, not proof",
        ],
    },
    "maintainer": {
        "name": "Repository / Organization Maintainer",
        "description": "I manage multiple repositories and want to enforce reproducibility standards.",
        "recommended_commands": [
            ("oss-paper-ci config init --profile strict", "Create a strict config"),
            ("oss-paper-ci workspace validate --workspace ws.yml", "Validate a workspace"),
            ("oss-paper-ci batch scan --workspace ws.yml", "Scan multiple repositories"),
            ("oss-paper-ci guide --topic scan", "Learn about scanning"),
        ],
        "key_concerns": [
            "Set reproducibility standards for your organization",
            "Batch scan multiple repositories",
            "Track reproducibility over time with baselines",
        ],
        "warnings": [
            "Standards should be realistic for your field",
            "Not all repositories need the same level of reproducibility",
        ],
    },
}

# Topic definitions
TOPICS = {
    "scan": {
        "name": "Scanning a Repository",
        "description": "Check a repository's reproducibility readiness.",
        "steps": [
            ("Install oss-paper-ci", "pip install -e '.[dev]'"),
            ("Scan your repository", "oss-paper-ci scan /path/to/repo"),
            ("Review the report", "The report shows a score, findings, and recommendations"),
            ("Address blocking issues", "Fix errors first, then warnings"),
            ("Re-scan to verify", "Run the scan again to confirm fixes"),
        ],
        "safety": "Scanning is read-only. No code is executed, no files are modified.",
        "limitations": [
            "Scans check engineering basics, not scientific correctness",
            "A high score does not guarantee reproducibility",
            "A low score does not mean the research is flawed",
        ],
    },
    "reproduce": {
        "name": "Attempting Reproduction",
        "description": "Safely attempt to reproduce a paper's computational results.",
        "steps": [
            ("Start with dry-run", "oss-paper-ci reproduce <repo> --dry-run"),
            ("Review what would happen", "Check the report for commands, environment, risks"),
            ("Execute if trusted", "oss-paper-ci reproduce <repo> --execute --install"),
            ("Review the results", "Check exit codes, output, and scan findings"),
            ("Generate a capsule", "oss-paper-ci reproduce <repo> --execute --install --capsule repro.zip"),
        ],
        "safety": (
            "Default mode is dry-run. --execute is required to run code. "
            "Only use --execute on repositories you trust."
        ),
        "limitations": [
            "This is an attempted reproduction, not guaranteed reproduction",
            "Results may differ due to hardware, software, or randomness",
            "Success does not prove the paper's claims are correct",
        ],
    },
    "capsule": {
        "name": "Reproduction Capsules",
        "description": "Generate and verify self-contained evidence packages.",
        "steps": [
            ("Generate a capsule", "oss-paper-ci reproduce <repo> --execute --install --capsule repro.zip"),
            ("Verify integrity", "oss-paper-ci capsule verify repro.zip"),
            ("Inspect contents", "oss-paper-ci capsule inspect repro.zip"),
            ("Compare capsules", "oss-paper-ci capsule diff old.zip new.zip"),
        ],
        "safety": "Capsules contain SHA256 checksums for integrity verification.",
        "limitations": [
            "A capsule is an evidence package, not a proof of correctness",
            "Capsules record what was done, not whether the results are valid",
            "Verify capsule integrity before trusting its contents",
        ],
    },
}


def get_guide(
    role: str | None = None,
    topic: str | None = None,
) -> dict[str, Any]:
    """Get guided content for a role or topic.

    Args:
        role: Role name (author, reviewer, maintainer).
        topic: Topic name (scan, reproduce, capsule).

    Returns:
        Dict with guidance content.
    """
    result: dict[str, Any] = {
        "oss_paper_ci_version": "2.1.0rc1",
        "disclaimer": (
            "This tool checks reproducibility readiness, not scientific correctness. "
            "A high score does not guarantee reproduction. A low score does not mean the "
            "research is flawed. Reproduction attempts are evidence, not proof."
        ),
    }

    if role:
        role_info = ROLES.get(role)
        if role_info:
            result["role"] = role
            result["role_name"] = role_info["name"]
            result["description"] = role_info["description"]
            result["recommended_commands"] = role_info["recommended_commands"]
            result["key_concerns"] = role_info["key_concerns"]
            result["warnings"] = role_info["warnings"]
        else:
            result["error"] = f"Unknown role: {role}. Available: {', '.join(ROLES.keys())}"

    if topic:
        topic_info = TOPICS.get(topic)
        if topic_info:
            result["topic"] = topic
            result["topic_name"] = topic_info["name"]
            result["topic_description"] = topic_info["description"]
            result["steps"] = topic_info["steps"]
            result["safety"] = topic_info["safety"]
            result["topic_limitations"] = topic_info["limitations"]
        else:
            result["error"] = f"Unknown topic: {topic}. Available: {', '.join(TOPICS.keys())}"

    if not role and not topic:
        result["overview"] = (
            "OSS-Paper-CI helps you check, attempt, and package scientific "
            "repository reproducibility evidence."
        )
        result["available_roles"] = list(ROLES.keys())
        result["available_topics"] = list(TOPICS.keys())
        result["quick_start"] = [
            ("Scan a repository", "oss-paper-ci scan ."),
            ("Try reproduction (safe)", "oss-paper-ci reproduce <repo> --dry-run"),
            ("Get guided help", "oss-paper-ci guide --role author"),
        ]

    return result


def format_guide_markdown(guide: dict[str, Any]) -> str:
    """Format guide content as markdown."""
    lines = ["# oss-paper-ci Guide\n"]

    if "disclaimer" in guide:
        lines.append(f"> {guide['disclaimer']}\n")

    if "overview" in guide:
        lines.append(f"## Overview\n\n{guide['overview']}\n")

    if "role" in guide:
        lines.append(f"## Role: {guide['role_name']}\n")
        lines.append(f"{guide['description']}\n")

        if guide.get("recommended_commands"):
            lines.append("### Recommended Commands\n")
            for cmd, desc in guide["recommended_commands"]:
                lines.append(f"- `{cmd}` — {desc}")
            lines.append("")

        if guide.get("key_concerns"):
            lines.append("### Key Concerns\n")
            for concern in guide["key_concerns"]:
                lines.append(f"- {concern}")
            lines.append("")

        if guide.get("warnings"):
            lines.append("### Important Notes\n")
            for warning in guide["warnings"]:
                lines.append(f"- {warning}")
            lines.append("")

    if "topic" in guide:
        lines.append(f"## Topic: {guide['topic_name']}\n")
        lines.append(f"{guide['topic_description']}\n")

        if guide.get("steps"):
            lines.append("### Steps\n")
            for i, (step, cmd) in enumerate(guide["steps"], 1):
                lines.append(f"{i}. **{step}**")
                lines.append(f"   ```bash")
                lines.append(f"   {cmd}")
                lines.append(f"   ```")
            lines.append("")

        if guide.get("safety"):
            lines.append(f"### Safety\n\n{guide['safety']}\n")

        if guide.get("topic_limitations"):
            lines.append("### Limitations\n")
            for lim in guide["topic_limitations"]:
                lines.append(f"- {lim}")
            lines.append("")

    if "quick_start" in guide:
        lines.append("## Quick Start\n")
        for desc, cmd in guide["quick_start"]:
            lines.append(f"- {desc}: `{cmd}`")
        lines.append("")

    if "available_roles" in guide:
        lines.append("## Available Roles\n")
        for role in guide["available_roles"]:
            lines.append(f"- `{role}`")
        lines.append("")

    if "available_topics" in guide:
        lines.append("## Available Topics\n")
        for topic in guide["available_topics"]:
            lines.append(f"- `{topic}`")
        lines.append("")

    if "error" in guide:
        lines.append(f"## Error\n\n{guide['error']}\n")

    return "\n".join(lines)


def get_plain_language_summary(
    mode: str,
    commands_attempted: int,
    commands_succeeded: int,
    commands_failed: int,
    scan_score: int | None = None,
    scan_status: str | None = None,
) -> str:
    """Generate a plain-language summary of a reproduction attempt.

    Args:
        mode: "dry-run" or "execute".
        commands_attempted: Number of commands attempted.
        commands_succeeded: Number of commands that succeeded.
        commands_failed: Number of commands that failed.
        scan_score: Optional scan score.
        scan_status: Optional scan status.

    Returns:
        Plain-language summary string.
    """
    if mode == "dry-run":
        return (
            "This is a dry-run report. No commands were executed. "
            "It shows what would happen if you ran the reproduction. "
            "To actually run commands, use --execute."
        )

    if commands_attempted == 0:
        return (
            "No reproduction commands were found or executed. "
            "The repository may not have a reproducibility.yml or common scripts. "
            "Use --command to specify a reproduction command."
        )

    if commands_failed == 0 and commands_succeeded > 0:
        summary = (
            f"Configured commands completed successfully ({commands_succeeded}/{commands_attempted}). "
            "This means the repository's declared reproduction path ran in this environment. "
            "It does not prove that the paper's claims are correct. "
            "Results may differ in other environments."
        )
        if scan_score is not None:
            summary += f" Repository scan score: {scan_score}/100 ({scan_status or 'unknown'})."
        return summary

    if commands_failed > 0:
        summary = (
            f"Some commands failed ({commands_failed}/{commands_attempted} failed). "
            "This means the reproduction could not complete successfully. "
            "Check the error output for details. "
            "Failure does not necessarily mean the paper is incorrect — "
            "it may be an environment or dependency issue."
        )
        if scan_score is not None:
            summary += f" Repository scan score: {scan_score}/100 ({scan_status or 'unknown'})."
        return summary

    return (
        f"Reproduction attempt completed. "
        f"{commands_succeeded} succeeded, {commands_failed} failed out of {commands_attempted} commands."
    )
