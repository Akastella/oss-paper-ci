"""Metric validation for the reproduction orchestrator.

Parses metrics.json files and validates that metric values fall within
expected tolerance ranges defined in reproducibility.yml.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MetricCheckResult:
    """Result of checking a single metric."""

    file: str = ""
    key: str = ""
    actual_value: Any = None
    expected_min: float | None = None
    expected_max: float | None = None
    in_range: bool = True
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file": self.file,
            "key": self.key,
            "in_range": self.in_range,
        }
        if self.actual_value is not None:
            d["actual_value"] = self.actual_value
        if self.expected_min is not None:
            d["expected_min"] = self.expected_min
        if self.expected_max is not None:
            d["expected_max"] = self.expected_max
        if self.error:
            d["error"] = self.error
        return d


@dataclass
class MetricValidationReport:
    """Report of metric validation."""

    total: int = 0
    in_range: int = 0
    out_of_range: int = 0
    errors: int = 0
    checks: list[MetricCheckResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "in_range": self.in_range,
            "out_of_range": self.out_of_range,
            "errors": self.errors,
            "checks": [c.to_dict() for c in self.checks],
            "warnings": self.warnings,
        }

    @property
    def ok(self) -> bool:
        return self.out_of_range == 0 and self.errors == 0


def validate_metrics(
    repo_path: str,
    metric_specs: list[dict[str, Any]],
) -> MetricValidationReport:
    """Validate metrics against expected ranges.

    Args:
        repo_path: Root directory of the repository.
        metric_specs: List of metric specifications from reproducibility.yml.
            Each must have 'file', 'key', and optionally 'expected_min'/'expected_max'.

    Returns:
        MetricValidationReport with per-metric results.
    """
    root = Path(repo_path)
    report = MetricValidationReport(total=len(metric_specs))

    # Cache loaded JSON files
    _json_cache: dict[str, dict[str, Any]] = {}

    for spec in metric_specs:
        file_path = spec.get("file", "")
        key = spec.get("key", "")
        expected_min = spec.get("expected_min")
        expected_max = spec.get("expected_max")

        check = MetricCheckResult(
            file=file_path,
            key=key,
            expected_min=expected_min,
            expected_max=expected_max,
        )

        if not file_path or not key:
            check.error = "Missing 'file' or 'key' in metric spec"
            check.in_range = False
            report.errors += 1
            report.checks.append(check)
            continue

        # Load the metrics file
        full_path = root / file_path
        if file_path not in _json_cache:
            if not full_path.exists():
                check.error = f"Metrics file not found: {file_path}"
                check.in_range = False
                report.errors += 1
                report.checks.append(check)
                continue
            try:
                with open(full_path, encoding="utf-8") as f:
                    _json_cache[file_path] = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                check.error = f"Failed to parse {file_path}: {exc}"
                check.in_range = False
                report.errors += 1
                report.checks.append(check)
                continue

        data = _json_cache[file_path]

        # Extract the metric value (supports dotted keys like "model.accuracy")
        value = _get_nested(data, key)
        if value is None:
            check.error = f"Key '{key}' not found in {file_path}"
            check.in_range = False
            report.errors += 1
            report.checks.append(check)
            continue

        check.actual_value = value

        # Validate range
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            check.error = f"Value for '{key}' is not numeric: {value!r}"
            check.in_range = False
            report.errors += 1
            report.checks.append(check)
            continue

        if expected_min is not None and num_value < expected_min:
            check.in_range = False
        if expected_max is not None and num_value > expected_max:
            check.in_range = False

        if check.in_range:
            report.in_range += 1
        else:
            report.out_of_range += 1

        report.checks.append(check)

    return report


def _get_nested(data: dict[str, Any], key: str) -> Any:
    """Get a value from a dict using dotted key notation.

    Example: _get_nested({"model": {"acc": 0.9}}, "model.acc") -> 0.9
    """
    parts = key.split(".")
    current: Any = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current
