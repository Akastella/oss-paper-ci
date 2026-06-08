"""Check modules for oss-paper-ci.

Each module implements one or more checkers that examine a repository
and produce CheckResult objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oss_paper_ci.checks.base import BaseChecker

# Registry of all checker classes
_CHECKER_CLASSES: list[type[BaseChecker]] = []


def register(cls: type[BaseChecker]) -> type[BaseChecker]:
    """Decorator to register a checker class."""
    _CHECKER_CLASSES.append(cls)
    return cls


def get_all_checkers() -> list[type[BaseChecker]]:
    """Return all registered checker classes."""
    # Import modules to trigger registration
    _ensure_loaded()
    return list(_CHECKER_CLASSES)


def _ensure_loaded() -> None:
    """Import checker modules to trigger @register decorators."""
    from oss_paper_ci.checks import (  # noqa: F401
        metadata,
        environment,
        experiments,
        data,
        results,
        paper_code,
        ci,
    )


def run_all_checks(
    repo_path: str,
    config: "Config | None" = None,
) -> list["CheckResult"]:
    """Run all registered checks against a repository.

    Args:
        repo_path: Path to the repository root.
        config: Optional configuration.

    Returns:
        List of all CheckResult objects from all checkers.
    """
    from oss_paper_ci.config import Config
    from oss_paper_ci.checks.base import CheckContext

    if config is None:
        config = Config()

    ctx = CheckContext(repo_path=repo_path, config=config)
    results = []
    for checker_cls in get_all_checkers():
        checker = checker_cls()
        try:
            results.extend(checker.check(ctx))
        except Exception as e:
            from oss_paper_ci.models import CheckResult, Severity, Status
            results.append(CheckResult(
                id=checker.check_id if hasattr(checker, 'check_id') else "UNKNOWN",
                title=checker.title if hasattr(checker, 'title') else "Check error",
                severity=Severity.ERROR,
                status=Status.UNKNOWN,
                message=f"Check failed with exception: {e}",
                recommendation="This may be a bug in oss-paper-ci. Please report it.",
            ))
    return results
