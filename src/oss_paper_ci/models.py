"""Core data models for oss-paper-ci.

All checkers, reporters, and the CLI operate on these models.
They are plain dataclasses with no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Severity level for a check finding."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Status(str, Enum):
    """Outcome of a single check."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    UNKNOWN = "unknown"


@dataclass
class CheckResult:
    """Result of a single check."""

    id: str
    title: str
    severity: Severity
    status: Status
    message: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass
class RepoInfo:
    """Detected information about the scanned repository."""

    path: str
    detected_languages: list[str] = field(default_factory=list)
    detected_project_types: list[str] = field(default_factory=list)


@dataclass
class Summary:
    """Aggregate summary of all check results."""

    score: int = 0
    status: str = "pass"
    counts: dict[str, int] = field(default_factory=lambda: {"info": 0, "warning": 0, "error": 0})

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "status": self.status,
            "counts": self.counts,
        }


@dataclass
class Report:
    """Complete report produced by a scan."""

    schema_version: str = "0.1"
    tool: str = "oss-paper-ci"
    version: str = "0.1.0"
    repository: RepoInfo = field(default_factory=lambda: RepoInfo(path="."))
    summary: Summary = field(default_factory=Summary)
    checks: list[CheckResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool": self.tool,
            "version": self.version,
            "repository": {
                "path": self.repository.path,
                "detected_languages": self.repository.detected_languages,
                "detected_project_types": self.repository.detected_project_types,
            },
            "summary": self.summary.to_dict(),
            "checks": [c.to_dict() for c in self.checks],
        }
