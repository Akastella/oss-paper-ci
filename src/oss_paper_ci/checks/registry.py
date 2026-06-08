"""Singleton checker registry for oss-paper-ci.

Stores all checker classes and provides lookup by ID, category, etc.
Uses lazy loading: checker modules are not imported until first access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oss_paper_ci.checks.base import BaseChecker

# Module-level singleton state
_CHECKER_CLASSES: list[type[BaseChecker]] = []
_ID_INDEX: dict[str, type[BaseChecker]] = {}
_CATEGORY_INDEX: dict[str, list[type[BaseChecker]]] = {}
_loaded = False


def register(cls: type[BaseChecker]) -> type[BaseChecker]:
    """Decorator to register a checker class.

    Can be used as ``@register`` on any BaseChecker subclass.
    """
    _CHECKER_CLASSES.append(cls)

    # Update indexes
    check_id = getattr(cls, "check_id", "")
    if check_id:
        _ID_INDEX[check_id] = cls

    category = getattr(cls, "category", "")
    if category:
        _CATEGORY_INDEX.setdefault(category, []).append(cls)

    return cls


def get_all_checkers() -> list[type[BaseChecker]]:
    """Return all registered checker classes (triggers lazy load)."""
    _ensure_loaded()
    return list(_CHECKER_CLASSES)


def get_checker_by_id(check_id: str) -> type[BaseChecker] | None:
    """Look up a single checker class by its check_id."""
    _ensure_loaded()
    return _ID_INDEX.get(check_id)


def get_checkers_by_category(category: str) -> list[type[BaseChecker]]:
    """Return all checker classes whose category matches."""
    _ensure_loaded()
    return list(_CATEGORY_INDEX.get(category, []))


def _ensure_loaded() -> None:
    """Import all checker modules once to trigger @register decorators."""
    global _loaded
    if _loaded:
        return
    _loaded = True

    from oss_paper_ci.checks import (  # noqa: F401
        metadata,
        environment,
        experiments,
        data,
        results,
        paper_code,
        ci,
        contract,
    )
