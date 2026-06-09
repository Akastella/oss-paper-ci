"""Public SDK API for oss-paper-ci rule packs.

This module provides the stable public interface for rule pack authors.
Import from here, not from internal modules.

Usage:
    from oss_paper_ci.checks.sdk import load_rule_pack, evaluate_rules, validate_rule_pack

    manifest = load_rule_pack("oss-paper-ci-rules.yml")
    results = evaluate_rules(manifest, "/path/to/repo")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from oss_paper_ci.checks.loader import evaluate_rule, evaluate_rules, load_rule_pack
from oss_paper_ci.checks.manifest import (
    ManifestValidationResult,
    RuleDefinition,
    RuleManifest,
    validate_manifest as validate_rule_pack,
    parse_manifest,
)
from oss_paper_ci.models import CheckResult, Severity, Status

__all__ = [
    "load_rule_pack",
    "evaluate_rules",
    "evaluate_rule",
    "validate_rule_pack",
    "RuleManifest",
    "RuleDefinition",
    "ManifestValidationResult",
    "CheckResult",
    "Severity",
    "Status",
]
