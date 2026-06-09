"""Rule pack loader and evaluator for oss-paper-ci.

Loads manifest-based rule packs and evaluates them against a repository.
All evaluation is safe: no user scripts are executed, only file/text/glob checks.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Any

from oss_paper_ci.checks.manifest import RuleDefinition, RuleManifest, parse_manifest
from oss_paper_ci.models import CheckResult, Severity, Status


def load_rule_pack(path: str | Path) -> RuleManifest:
    """Load a rule pack from a YAML file.

    Args:
        path: Path to the rule pack manifest.

    Returns:
        Parsed RuleManifest.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If YAML is invalid.
    """
    return parse_manifest(path)


def evaluate_rules(manifest: RuleManifest, repo_path: str) -> list[CheckResult]:
    """Evaluate all rules in a manifest against a repository.

    Args:
        manifest: Parsed rule manifest.
        repo_path: Path to the repository root.

    Returns:
        List of CheckResult objects (one per rule).
    """
    results = []
    root = Path(repo_path)

    for rule in manifest.rules:
        try:
            result = evaluate_rule(rule, root)
            results.append(result)
        except Exception as exc:
            # Never let a single rule crash the scan
            results.append(CheckResult(
                id=rule.id,
                title=rule.name,
                severity=Severity.ERROR,
                status=Status.UNKNOWN,
                message=f"Rule evaluation failed: {exc}",
                recommendation="This may be a bug in the rule definition.",
            ))

    return results


def evaluate_rule(rule: RuleDefinition, repo_root: Path) -> CheckResult:
    """Evaluate a single rule against a repository.

    Args:
        rule: The rule definition.
        repo_root: Path to the repository root.

    Returns:
        CheckResult for this rule.
    """
    sev = _map_severity(rule.severity)

    evaluator = _EVALUATORS.get(rule.rule_type)
    if evaluator is None:
        return CheckResult(
            id=rule.id,
            title=rule.name,
            severity=sev,
            status=Status.UNKNOWN,
            message=f"Unknown rule type: {rule.rule_type}",
        )

    return evaluator(rule, repo_root, sev)


def _map_severity(severity: str) -> Severity:
    """Map manifest severity to internal Severity."""
    mapping = {
        "info": Severity.INFO,
        "advisory": Severity.INFO,
        "warning": Severity.WARNING,
        "important": Severity.WARNING,
        "error": Severity.ERROR,
        "blocking": Severity.ERROR,
    }
    return mapping.get(severity, Severity.WARNING)


# ── Rule Evaluators ──────────────────────────────────────────────────────────

def _eval_file_exists(rule: RuleDefinition, root: Path, sev: Severity) -> CheckResult:
    """Check that a specific file exists."""
    file_path = root / rule.params["path"]
    if file_path.exists():
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.PASS,
            message=f"Found: {rule.params['path']}",
        )
    return CheckResult(
        id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
        message=rule.message or f"Missing: {rule.params['path']}",
        recommendation=rule.recommendation,
    )


def _eval_any_file_exists(rule: RuleDefinition, root: Path, sev: Severity) -> CheckResult:
    """Check that at least one of several files exists."""
    paths = rule.params.get("paths", [])
    found = [p for p in paths if (root / p).exists()]
    if found:
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.PASS,
            message=f"Found: {', '.join(found)}",
            evidence=found,
        )
    return CheckResult(
        id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
        message=rule.message or f"None of {paths} found",
        recommendation=rule.recommendation,
    )


def _eval_forbidden_path(rule: RuleDefinition, root: Path, sev: Severity) -> CheckResult:
    """Fail if a specific path exists."""
    file_path = root / rule.params["path"]
    if file_path.exists():
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
            message=rule.message or f"Forbidden path exists: {rule.params['path']}",
            evidence=[rule.params["path"]],
            recommendation=rule.recommendation,
        )
    return CheckResult(
        id=rule.id, title=rule.name, severity=sev, status=Status.PASS,
        message=f"Forbidden path not found: {rule.params['path']}",
    )


def _eval_forbidden_glob(rule: RuleDefinition, root: Path, sev: Severity) -> CheckResult:
    """Fail if any file matching a glob exists."""
    pattern = rule.params["pattern"]
    matches = list(root.glob(pattern))
    if matches:
        match_strs = [str(m.relative_to(root)) for m in matches[:10]]
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
            message=rule.message or f"Forbidden files found matching '{pattern}'",
            evidence=match_strs,
            recommendation=rule.recommendation,
        )
    return CheckResult(
        id=rule.id, title=rule.name, severity=sev, status=Status.PASS,
        message=f"No forbidden files matching '{pattern}'",
    )


def _eval_text_contains(rule: RuleDefinition, root: Path, sev: Severity) -> CheckResult:
    """Check that a file contains specific text."""
    file_path = root / rule.params["path"]
    text = rule.params["text"]

    if not file_path.exists():
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
            message=f"File not found: {rule.params['path']}",
            recommendation=rule.recommendation,
        )

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.UNKNOWN,
            message=f"Cannot read {rule.params['path']}: {exc}",
        )

    if text in content:
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.PASS,
            message=f"Found '{text}' in {rule.params['path']}",
        )
    return CheckResult(
        id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
        message=rule.message or f"'{text}' not found in {rule.params['path']}",
        recommendation=rule.recommendation,
    )


def _eval_regex_contains(rule: RuleDefinition, root: Path, sev: Severity) -> CheckResult:
    """Check that a file matches a regex."""
    file_path = root / rule.params["path"]
    pattern = rule.params["pattern"]

    if not file_path.exists():
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
            message=f"File not found: {rule.params['path']}",
            recommendation=rule.recommendation,
        )

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.UNKNOWN,
            message=f"Cannot read {rule.params['path']}: {exc}",
        )

    try:
        match = re.search(pattern, content)
    except re.error as exc:
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.UNKNOWN,
            message=f"Invalid regex pattern: {exc}",
        )

    if match:
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.PASS,
            message=f"Pattern '{pattern}' found in {rule.params['path']}",
        )
    return CheckResult(
        id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
        message=rule.message or f"Pattern '{pattern}' not found in {rule.params['path']}",
        recommendation=rule.recommendation,
    )


def _eval_yaml_key_exists(rule: RuleDefinition, root: Path, sev: Severity) -> CheckResult:
    """Check that a YAML file has a specific key."""
    import yaml as yaml_mod

    file_path = root / rule.params["path"]
    key = rule.params["key"]

    if not file_path.exists():
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
            message=f"File not found: {rule.params['path']}",
            recommendation=rule.recommendation,
        )

    try:
        with open(file_path, encoding="utf-8") as f:
            data = yaml_mod.safe_load(f)
    except Exception as exc:
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.UNKNOWN,
            message=f"Cannot parse YAML {rule.params['path']}: {exc}",
        )

    if not isinstance(data, dict):
        return CheckResult(
            id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
            message=f"{rule.params['path']} is not a YAML mapping",
        )

    # Support dotted key paths: "experiments.0.command"
    parts = key.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return CheckResult(
                    id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
                    message=rule.message or f"Key '{key}' not found in {rule.params['path']}",
                    recommendation=rule.recommendation,
                )
        else:
            return CheckResult(
                id=rule.id, title=rule.name, severity=sev, status=Status.FAIL,
                message=rule.message or f"Key '{key}' not found in {rule.params['path']}",
                recommendation=rule.recommendation,
            )

    return CheckResult(
        id=rule.id, title=rule.name, severity=sev, status=Status.PASS,
        message=f"Key '{key}' found in {rule.params['path']}",
    )


# Evaluator dispatch table
_EVALUATORS = {
    "file_exists": _eval_file_exists,
    "any_file_exists": _eval_any_file_exists,
    "forbidden_path": _eval_forbidden_path,
    "forbidden_glob": _eval_forbidden_glob,
    "text_contains": _eval_text_contains,
    "regex_contains": _eval_regex_contains,
    "yaml_key_exists": _eval_yaml_key_exists,
}
