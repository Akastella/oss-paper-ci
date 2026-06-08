"""Check modules for oss-paper-ci.

Each module implements one or more checkers that examine a repository
and produce CheckResult objects.

The actual registry lives in ``registry.py``.  This module re-exports the
public API for backward compatibility so that existing code that does
``from oss_paper_ci.checks import register, get_all_checkers`` keeps
working.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from oss_paper_ci.checks.registry import (
    get_all_checkers,
    get_checker_by_id,
    get_checkers_by_category,
    register,
)

if TYPE_CHECKING:
    from oss_paper_ci.checks.base import BaseChecker

# Re-export for backward compatibility
__all__ = [
    "register",
    "get_all_checkers",
    "get_checker_by_id",
    "get_checkers_by_category",
    "run_all_checks",
]


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

    # Resolve enabled/disabled sets from config
    checks_cfg = config.checks
    enabled_set = set(checks_cfg.enabled) if checks_cfg.enabled else set()
    disabled_set = set(checks_cfg.disabled)
    severity_overrides = checks_cfg.severity_overrides or {}

    results = []
    for checker_cls in get_all_checkers():
        checker = checker_cls()

        # Skip disabled checks
        check_id = getattr(checker, "check_id", "")
        if check_id in disabled_set:
            continue
        # If an enabled list is provided, only run those
        if enabled_set and check_id not in enabled_set:
            continue

        # Apply severity override
        if check_id in severity_overrides:
            from oss_paper_ci.models import Severity as _Sev
            override = severity_overrides[check_id].upper()
            if hasattr(_Sev, override):
                checker.severity = getattr(_Sev, override)

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
