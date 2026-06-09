"""Schema validation for oss-paper-ci configuration files.

Validates .oss-paper-ci.yml structure and reports clear error messages.
Does NOT validate reproducibility.yml (that lives in contract_schema.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from oss_paper_ci.policy import list_profiles


@dataclass
class ValidationIssue:
    """A single validation problem."""

    path: str  # dot-separated field path, e.g. "checks.min_score"
    message: str
    severity: str = "error"  # "error" or "warning"

    def __str__(self) -> str:
        prefix = "ERROR" if self.severity == "error" else "WARN "
        return f"[{prefix}] {self.path}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validating a config file."""

    valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    config_path: str = ""

    def add_error(self, path: str, message: str) -> None:
        self.issues.append(ValidationIssue(path, message, "error"))
        self.valid = False

    def add_warning(self, path: str, message: str) -> None:
        self.issues.append(ValidationIssue(path, message, "warning"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "config_path": self.config_path,
            "issues": [
                {"path": i.path, "message": i.message, "severity": i.severity}
                for i in self.issues
            ],
        }

    def format_text(self) -> str:
        if not self.issues:
            return f"Configuration is valid: {self.config_path}"
        lines = [f"Configuration validation: {self.config_path}"]
        lines.append("")
        for issue in self.issues:
            lines.append(f"  {issue}")
        lines.append("")
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        lines.append(f"{errors} error(s), {warnings} warning(s)")
        return "\n".join(lines)


# ── Known field definitions ──────────────────────────────────────────────────

_KNOWN_TOP_LEVEL = {"version", "profile", "project", "checks", "ignore", "output",
                    "paths", "thresholds", "severity", "reports", "ci"}

_KNOWN_PROJECT = {"name", "paper_dir", "code_dirs", "data_dirs", "results_dirs"}

_KNOWN_CHECKS = {"min_score", "require_license", "require_citation",
                 "require_environment", "require_quickstart",
                 "enabled", "disabled", "severity_overrides"}

_KNOWN_IGNORE = {"paths"}

_KNOWN_OUTPUT = {"default_format"}

_KNOWN_PATHS = {"include", "exclude"}

_KNOWN_THRESHOLDS = {"pass_score", "warn_score", "fail_under"}

_KNOWN_SEVERITY = {"fail_on", "treat_as_blocking"}

_KNOWN_REPORTS = {"default_format", "include_recommendations", "max_findings"}

_KNOWN_CI = {"github_annotations", "step_summary"}

_VALID_SEVERITIES = {"info", "warning", "error", "blocking", "important", "advisory"}


def validate_config_file(path: str | Path) -> ValidationResult:
    """Validate a .oss-paper-ci.yml file.

    Args:
        path: Path to the YAML config file.

    Returns:
        ValidationResult with any issues found.
    """
    result = ValidationResult(config_path=str(path))
    p = Path(path)

    if not p.exists():
        result.add_error("file", f"Config file not found: {path}")
        return result

    try:
        raw = p.read_text(encoding="utf-8")
    except Exception as exc:
        result.add_error("file", f"Cannot read config file: {exc}")
        return result

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        result.add_error("file", f"Invalid YAML: {exc}")
        return result

    if data is None:
        # Empty file — valid but nothing to validate
        return result

    if not isinstance(data, dict):
        result.add_error("file", "Config must be a YAML mapping, not a scalar or list")
        return result

    _validate_top_level(data, result)
    return result


def validate_config_data(data: dict[str, Any]) -> ValidationResult:
    """Validate an already-parsed config dict.

    Args:
        data: Parsed YAML dict.

    Returns:
        ValidationResult with any issues found.
    """
    result = ValidationResult()
    if not isinstance(data, dict):
        result.add_error("file", "Config must be a YAML mapping")
        return result
    _validate_top_level(data, result)
    return result


def _validate_top_level(data: dict[str, Any], result: ValidationResult) -> None:
    """Validate top-level keys."""
    # Check for unknown top-level keys
    for key in data:
        if key not in _KNOWN_TOP_LEVEL:
            result.add_warning(key, f"Unknown top-level key: {key!r}")

    # version
    if "version" in data:
        ver = data["version"]
        if not isinstance(ver, (str, int, float)):
            result.add_error("version", "Must be a string or number")

    # profile
    if "profile" in data:
        profile = data["profile"]
        if not isinstance(profile, str):
            result.add_error("profile", "Must be a string")
        elif profile not in list_profiles():
            available = ", ".join(list_profiles())
            result.add_error(
                "profile",
                f"Unknown profile: {profile!r}. Available: {available}"
            )

    # project
    if "project" in data:
        _validate_section(data["project"], "project", _KNOWN_PROJECT, result)

    # checks
    if "checks" in data:
        _validate_checks(data["checks"], result)

    # ignore
    if "ignore" in data:
        _validate_section(data["ignore"], "ignore", _KNOWN_IGNORE, result)

    # output
    if "output" in data:
        _validate_section(data["output"], "output", _KNOWN_OUTPUT, result)

    # paths
    if "paths" in data:
        _validate_paths(data["paths"], result)

    # thresholds
    if "thresholds" in data:
        _validate_thresholds(data["thresholds"], result)

    # severity
    if "severity" in data:
        _validate_severity(data["severity"], result)

    # reports
    if "reports" in data:
        _validate_reports(data["reports"], result)

    # ci
    if "ci" in data:
        _validate_ci(data["ci"], result)


def _validate_section(
    data: Any, prefix: str, known: set[str], result: ValidationResult
) -> None:
    if not isinstance(data, dict):
        result.add_error(prefix, "Must be a mapping")
        return
    for key in data:
        if key not in known:
            result.add_warning(f"{prefix}.{key}", f"Unknown key: {key!r}")


def _validate_checks(data: Any, result: ValidationResult) -> None:
    if not isinstance(data, dict):
        result.add_error("checks", "Must be a mapping")
        return

    for key in data:
        if key not in _KNOWN_CHECKS:
            result.add_warning(f"checks.{key}", f"Unknown key: {key!r}")

    if "min_score" in data:
        val = data["min_score"]
        if not isinstance(val, int) or not (0 <= val <= 100):
            result.add_error("checks.min_score", "Must be an integer 0-100")

    if "disabled" in data:
        val = data["disabled"]
        if not isinstance(val, list):
            result.add_error("checks.disabled", "Must be a list of check IDs")

    if "enabled" in data:
        val = data["enabled"]
        if not isinstance(val, list):
            result.add_error("checks.enabled", "Must be a list of check IDs")

    if "severity_overrides" in data:
        val = data["severity_overrides"]
        if not isinstance(val, dict):
            result.add_error("checks.severity_overrides", "Must be a mapping")
        else:
            for cid, sev in val.items():
                if sev not in _VALID_SEVERITIES:
                    result.add_error(
                        f"checks.severity_overrides.{cid}",
                        f"Invalid severity: {sev!r}. "
                        f"Valid: {', '.join(sorted(_VALID_SEVERITIES))}"
                    )


def _validate_paths(data: Any, result: ValidationResult) -> None:
    if not isinstance(data, dict):
        result.add_error("paths", "Must be a mapping")
        return

    for key in data:
        if key not in _KNOWN_PATHS:
            result.add_warning(f"paths.{key}", f"Unknown key: {key!r}")

    if "include" in data:
        val = data["include"]
        if not isinstance(val, list):
            result.add_error("paths.include", "Must be a list of path patterns")

    if "exclude" in data:
        val = data["exclude"]
        if not isinstance(val, list):
            result.add_error("paths.exclude", "Must be a list of path patterns")


def _validate_thresholds(data: Any, result: ValidationResult) -> None:
    if not isinstance(data, dict):
        result.add_error("thresholds", "Must be a mapping")
        return

    for key in data:
        if key not in _KNOWN_THRESHOLDS:
            result.add_warning(f"thresholds.{key}", f"Unknown key: {key!r}")

    for field_name in ("pass_score", "warn_score", "fail_under"):
        if field_name in data:
            val = data[field_name]
            if not isinstance(val, int) or not (0 <= val <= 100):
                result.add_error(
                    f"thresholds.{field_name}",
                    "Must be an integer 0-100"
                )

    # Logical consistency
    ps = data.get("pass_score")
    ws = data.get("warn_score")
    fu = data.get("fail_under")
    if ps is not None and ws is not None and isinstance(ps, int) and isinstance(ws, int):
        if ws > ps:
            result.add_error(
                "thresholds",
                f"warn_score ({ws}) must be <= pass_score ({ps})"
            )
    if fu is not None and ws is not None and isinstance(fu, int) and isinstance(ws, int):
        if fu > ws:
            result.add_error(
                "thresholds",
                f"fail_under ({fu}) must be <= warn_score ({ws})"
            )


def _validate_severity(data: Any, result: ValidationResult) -> None:
    if not isinstance(data, dict):
        result.add_error("severity", "Must be a mapping")
        return

    for key in data:
        if key not in _KNOWN_SEVERITY:
            result.add_warning(f"severity.{key}", f"Unknown key: {key!r}")

    if "fail_on" in data:
        val = data["fail_on"]
        if isinstance(val, list):
            for item in val:
                if item not in _VALID_SEVERITIES:
                    result.add_error(
                        "severity.fail_on",
                        f"Invalid value: {item!r}"
                    )
        else:
            result.add_error("severity.fail_on", "Must be a list")

    if "treat_as_blocking" in data:
        val = data["treat_as_blocking"]
        if isinstance(val, list):
            for item in val:
                if not isinstance(item, str):
                    result.add_error(
                        "severity.treat_as_blocking",
                        f"Invalid value: {item!r} (expected check ID string)"
                    )
        else:
            result.add_error("severity.treat_as_blocking", "Must be a list")


def _validate_reports(data: Any, result: ValidationResult) -> None:
    if not isinstance(data, dict):
        result.add_error("reports", "Must be a mapping")
        return

    for key in data:
        if key not in _KNOWN_REPORTS:
            result.add_warning(f"reports.{key}", f"Unknown key: {key!r}")

    if "default_format" in data:
        val = data["default_format"]
        valid_formats = {"json", "markdown", "sarif", "html", "github"}
        if val not in valid_formats:
            result.add_error(
                "reports.default_format",
                f"Unknown format: {val!r}. Valid: {', '.join(sorted(valid_formats))}"
            )

    if "max_findings" in data:
        val = data["max_findings"]
        if not isinstance(val, int) or val < 0:
            result.add_error("reports.max_findings", "Must be a non-negative integer")


def _validate_ci(data: Any, result: ValidationResult) -> None:
    if not isinstance(data, dict):
        result.add_error("ci", "Must be a mapping")
        return

    for key in data:
        if key not in _KNOWN_CI:
            result.add_warning(f"ci.{key}", f"Unknown key: {key!r}")

    for field_name in ("github_annotations", "step_summary"):
        if field_name in data:
            val = data[field_name]
            if not isinstance(val, bool):
                result.add_error(
                    f"ci.{field_name}",
                    "Must be a boolean (true/false)"
                )
