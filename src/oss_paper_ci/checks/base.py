"""Base checker class and context for all check modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from oss_paper_ci.config import Config
from oss_paper_ci.models import CheckResult, Severity, Status
from oss_paper_ci.utils.fs import list_files


@dataclass
class CheckContext:
    """Context passed to each checker during a scan."""

    repo_path: str
    config: Config

    _files: list[Path] | None = None

    @property
    def root(self) -> Path:
        return Path(self.repo_path)

    @property
    def files(self) -> list[Path]:
        """List all files in the repo (cached)."""
        if self._files is None:
            self._files = list_files(self.repo_path, self.config.ignore.paths)
        return self._files

    def has_file(self, *path_parts: str) -> bool:
        """Check if a specific file exists relative to repo root."""
        return (self.root / Path(*path_parts)).exists()

    def file_names(self) -> set[str]:
        """Get set of all file names (not paths) in the repo."""
        return {f.name for f in self.files}

    def file_suffixes(self) -> set[str]:
        """Get set of all file extensions in the repo."""
        return {f.suffix for f in self.files}

    def read_file(self, *path_parts: str) -> str | None:
        """Read a file relative to repo root. Returns None on failure."""
        path = self.root / Path(*path_parts)
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
        return None


class BaseChecker(ABC):
    """Abstract base class for all checkers."""

    check_id: str = ""
    title: str = ""
    severity: Severity = Severity.INFO
    category: str = ""
    default_enabled: bool = True
    description: str = ""

    @abstractmethod
    def check(self, ctx: CheckContext) -> list[CheckResult]:
        """Run this checker against the repository.

        Args:
            ctx: The check context with repo path, config, and file listing.

        Returns:
            List of CheckResult objects.
        """

    def _pass(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=self.severity,
            status=Status.PASS,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )

    def _warn(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.WARNING,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )

    def _fail(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.ERROR,
            status=Status.FAIL,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )

    def _unknown(self, message: str, evidence: list[str] | None = None) -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=self.severity,
            status=Status.UNKNOWN,
            message=message,
            evidence=evidence or [],
        )
