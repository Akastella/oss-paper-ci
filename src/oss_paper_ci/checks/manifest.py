"""Rule pack manifest schema for oss-paper-ci.

Defines the YAML format for manifest-based rule packs that allow
users to add custom checks without writing Python code.

Supported rule types:
  - file_exists: check that a specific file exists
  - any_file_exists: check that at least one of several files exists
  - forbidden_path: fail if a specific path exists
  - forbidden_glob: fail if any file matching a glob exists
  - text_contains: check that a file contains specific text
  - regex_contains: check that a file matches a regex
  - yaml_key_exists: check that a YAML file has a specific key
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# Valid rule types
VALID_RULE_TYPES = {
    "file_exists",
    "any_file_exists",
    "forbidden_path",
    "forbidden_glob",
    "text_contains",
    "regex_contains",
    "yaml_key_exists",
}

# Valid severity values for rules
VALID_SEVERITIES = {"info", "warning", "error", "important", "advisory", "blocking"}

# Severity mapping from manifest to internal
_SEVERITY_MAP = {
    "info": "info",
    "advisory": "info",
    "warning": "warning",
    "important": "warning",
    "error": "error",
    "blocking": "error",
}


@dataclass
class RuleDefinition:
    """A single rule defined in a manifest."""

    id: str
    name: str
    severity: str = "warning"
    category: str = "custom"
    rule_type: str = "file_exists"
    message: str = ""
    recommendation: str = ""
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def internal_severity(self) -> str:
        """Map manifest severity to internal severity."""
        return _SEVERITY_MAP.get(self.severity, "warning")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity,
            "category": self.category,
            "type": self.rule_type,
            "message": self.message,
        }


@dataclass
class RuleManifest:
    """A parsed rule pack manifest."""

    version: int = 1
    name: str = ""
    description: str = ""
    rules: list[RuleDefinition] = field(default_factory=list)
    path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "rules": [r.to_dict() for r in self.rules],
            "path": self.path,
        }


@dataclass
class ManifestValidationIssue:
    """A validation issue in a manifest."""

    path: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        prefix = "ERROR" if self.severity == "error" else "WARN "
        return f"[{prefix}] {self.path}: {self.message}"


@dataclass
class ManifestValidationResult:
    """Result of validating a rule pack manifest."""

    valid: bool = True
    issues: list[ManifestValidationIssue] = field(default_factory=list)
    manifest_path: str = ""

    def add_error(self, path: str, message: str) -> None:
        self.issues.append(ManifestValidationIssue(path, message, "error"))
        self.valid = False

    def add_warning(self, path: str, message: str) -> None:
        self.issues.append(ManifestValidationIssue(path, message, "warning"))

    def format_text(self) -> str:
        if not self.issues:
            return f"Rule pack is valid: {self.manifest_path}"
        lines = [f"Rule pack validation: {self.manifest_path}"]
        lines.append("")
        for issue in self.issues:
            lines.append(f"  {issue}")
        lines.append("")
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        lines.append(f"{errors} error(s), {warnings} warning(s)")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "manifest_path": self.manifest_path,
            "issues": [
                {"path": i.path, "message": i.message, "severity": i.severity}
                for i in self.issues
            ],
        }


def parse_manifest(path: str | Path) -> RuleManifest:
    """Parse a rule pack manifest YAML file.

    Args:
        path: Path to the manifest YAML file.

    Returns:
        Parsed RuleManifest.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the YAML is invalid.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Rule pack not found: {path}")

    try:
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in rule pack: {exc}")

    if not isinstance(data, dict):
        raise ValueError("Rule pack must be a YAML mapping")

    return _parse_manifest_data(data, str(p))


def _parse_manifest_data(data: dict[str, Any], path: str) -> RuleManifest:
    """Parse manifest data dict into RuleManifest."""
    manifest = RuleManifest(path=path)

    if "version" in data:
        manifest.version = int(data["version"])

    if "name" in data:
        manifest.name = str(data["name"])

    if "description" in data:
        manifest.description = str(data["description"])

    rules_data = data.get("checks", data.get("rules", []))
    if not isinstance(rules_data, list):
        raise ValueError("'checks' must be a list")

    for i, rule_data in enumerate(rules_data):
        if not isinstance(rule_data, dict):
            raise ValueError(f"Rule {i} must be a mapping")
        manifest.rules.append(_parse_rule(rule_data, i))

    return manifest


def _parse_rule(data: dict[str, Any], index: int) -> RuleDefinition:
    """Parse a single rule definition."""
    rule_id = data.get("id", "")
    if not rule_id:
        raise ValueError(f"Rule {index}: 'id' is required")

    name = data.get("name", "")
    if not name:
        raise ValueError(f"Rule {index} ({rule_id}): 'name' is required")

    severity = data.get("severity", "warning")
    if severity not in VALID_SEVERITIES:
        raise ValueError(
            f"Rule {index} ({rule_id}): invalid severity '{severity}'. "
            f"Valid: {', '.join(sorted(VALID_SEVERITIES))}"
        )

    category = data.get("category", "custom")
    rule_type = data.get("type", "file_exists")
    if rule_type not in VALID_RULE_TYPES:
        raise ValueError(
            f"Rule {index} ({rule_id}): invalid type '{rule_type}'. "
            f"Valid: {', '.join(sorted(VALID_RULE_TYPES))}"
        )

    message = data.get("message", f"Rule {rule_id} failed")
    recommendation = data.get("recommendation", "")

    # Collect all other fields as params
    params = {}
    for key, value in data.items():
        if key not in {"id", "name", "severity", "category", "type", "message", "recommendation"}:
            params[key] = value

    return RuleDefinition(
        id=rule_id,
        name=name,
        severity=severity,
        category=category,
        rule_type=rule_type,
        message=message,
        recommendation=recommendation,
        params=params,
    )


def validate_manifest(path: str | Path) -> ManifestValidationResult:
    """Validate a rule pack manifest file.

    Args:
        path: Path to the manifest YAML file.

    Returns:
        ManifestValidationResult with any issues found.
    """
    result = ManifestValidationResult(manifest_path=str(path))
    p = Path(path)

    if not p.exists():
        result.add_error("file", f"Rule pack not found: {path}")
        return result

    try:
        manifest = parse_manifest(p)
    except (ValueError, FileNotFoundError) as exc:
        result.add_error("file", str(exc))
        return result

    # Validate version
    if manifest.version != 1:
        result.add_warning("version", f"Unknown version: {manifest.version}")

    # Validate rules
    seen_ids = set()
    for rule in manifest.rules:
        if rule.id in seen_ids:
            result.add_error(f"checks.{rule.id}", f"Duplicate rule ID: {rule.id}")
        seen_ids.add(rule.id)

        # Validate rule-specific params
        _validate_rule_params(rule, result)

    return result


def _validate_rule_params(rule: RuleDefinition, result: ManifestValidationResult) -> None:
    """Validate rule-type-specific parameters."""
    prefix = f"checks.{rule.id}"

    if rule.rule_type == "file_exists":
        if "path" not in rule.params:
            result.add_error(prefix, "file_exists requires 'path' parameter")

    elif rule.rule_type == "any_file_exists":
        paths = rule.params.get("paths", [])
        if not paths or not isinstance(paths, list):
            result.add_error(prefix, "any_file_exists requires 'paths' list parameter")

    elif rule.rule_type == "forbidden_path":
        if "path" not in rule.params:
            result.add_error(prefix, "forbidden_path requires 'path' parameter")

    elif rule.rule_type == "forbidden_glob":
        if "pattern" not in rule.params:
            result.add_error(prefix, "forbidden_glob requires 'pattern' parameter")

    elif rule.rule_type == "text_contains":
        if "path" not in rule.params:
            result.add_error(prefix, "text_contains requires 'path' parameter")
        if "text" not in rule.params:
            result.add_error(prefix, "text_contains requires 'text' parameter")

    elif rule.rule_type == "regex_contains":
        if "path" not in rule.params:
            result.add_error(prefix, "regex_contains requires 'path' parameter")
        if "pattern" not in rule.params:
            result.add_error(prefix, "regex_contains requires 'pattern' parameter")

    elif rule.rule_type == "yaml_key_exists":
        if "path" not in rule.params:
            result.add_error(prefix, "yaml_key_exists requires 'path' parameter")
        if "key" not in rule.params:
            result.add_error(prefix, "yaml_key_exists requires 'key' parameter")
