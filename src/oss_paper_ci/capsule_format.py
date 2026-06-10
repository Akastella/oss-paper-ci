"""Capsule format definitions and constants.

Defines the structure, schema version, and required files for
oss-paper-ci reproduction capsules.
"""

from __future__ import annotations

from typing import Any

# Capsule schema version
CAPSULE_SCHEMA_VERSION = "0.1"
CAPSULE_TYPE = "oss-paper-ci-reproduction-capsule"
CAPSULE_ROOT_DIR = "oss-paper-ci-capsule"

# Required files that must exist in every capsule
REQUIRED_FILES = [
    "capsule.json",
    "SHA256SUMS",
    "reports/reproduce_report.json",
    "metadata/source.json",
    "metadata/environment.json",
    "metadata/commands.json",
    "metadata/limitations.md",
]

# Optional files
OPTIONAL_FILES = [
    "reports/reproduce_report.md",
    "reports/reproduce_report.html",
    "reports/scan_report.json",
    "reports/scan_report.md",
    "metadata/oss_paper_ci.json",
]

# Directories
CAPSULE_DIRS = [
    "reports",
    "logs",
    "artifacts",
    "artifacts/generated",
    "metadata",
]

# Excluded patterns (never packaged into capsule)
EXCLUDED_PATTERNS = [
    ".git",
    ".git/**",
    "__pycache__",
    "__pycache__/**",
    ".oss-paper-ci-repro",
    ".oss-paper-ci-repro/**",
    ".oss-paper-ci-cache",
    ".oss-paper-ci-cache/**",
    "venv",
    "venv/**",
    ".venv",
    ".venv/**",
    "node_modules",
    "node_modules/**",
    "*.pyc",
    "*.pyo",
    ".env",
]

# Max artifact size per file (10 MB default)
MAX_ARTIFACT_SIZE_BYTES = 10 * 1024 * 1024

# Max total capsule size (100 MB)
MAX_CAPSULE_SIZE_BYTES = 100 * 1024 * 1024

# Max number of artifact files
MAX_ARTIFACT_FILES = 200

# Max log size per file (1 MB)
MAX_LOG_SIZE_BYTES = 1024 * 1024


def create_capsule_manifest(
    *,
    oss_paper_ci_version: str,
    source: dict[str, Any],
    execution: dict[str, Any],
    reports: dict[str, Any],
    limitations: list[str],
) -> dict[str, Any]:
    """Create the capsule.json manifest structure.

    Args:
        oss_paper_ci_version: Version of oss-paper-ci that created this capsule.
        source: Source metadata (input_url, repo_url, commit_sha, etc.).
        execution: Execution metadata (mode, install, commands, etc.).
        reports: Report file paths within the capsule.
        limitations: List of limitation statements.

    Returns:
        Dict suitable for JSON serialization as capsule.json.
    """
    return {
        "schema_version": CAPSULE_SCHEMA_VERSION,
        "capsule_type": CAPSULE_TYPE,
        "created_by": "oss-paper-ci",
        "oss_paper_ci_version": oss_paper_ci_version,
        "source": source,
        "execution": execution,
        "reports": reports,
        "integrity": {
            "sha256sums": "SHA256SUMS",
        },
        "limitations": limitations,
    }
