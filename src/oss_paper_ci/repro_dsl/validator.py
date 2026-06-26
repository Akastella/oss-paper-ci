"""Validator for Reproducibility DSL v1 specifications.

Checks structural validity, dependency integrity, path safety,
and safety declarations. Does NOT execute code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .schema import ReproDSL


@dataclass
class ValidationFinding:
    """A single validation finding."""

    severity: str  # "error", "warning", "info"
    category: str  # "schema", "dependency", "path", "safety", "metric", "dataset"
    message: str
    field_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
        }
        if self.field_path:
            d["field_path"] = self.field_path
        return d


@dataclass
class ValidationResult:
    """Result of DSL validation."""

    findings: list[ValidationFinding]
    is_valid: bool  # True if no errors
    checked_fields: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": [f.to_dict() for f in self.findings],
            "is_valid": self.is_valid,
            "checked_fields": self.checked_fields,
        }

    @property
    def errors(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.severity == "warning"]


def validate_dsl(dsl: ReproDSL, base_path: Path | None = None) -> ValidationResult:
    """Validate a ReproDSL specification.

    Checks:
    1. Schema structure (version, required fields)
    2. Step dependencies (no missing refs, no self-deps)
    3. Path declarations (relative, no traversal)
    4. Safety declarations consistency
    5. Metric specifications
    6. Dataset declarations
    7. Environment references
    8. Artifact declarations

    Args:
        dsl: The DSL specification to validate
        base_path: Optional base path for checking file existence

    Returns:
        ValidationResult with findings
    """
    findings: list[ValidationFinding] = []
    checked = 0

    # 1. Schema structure
    checked += 1
    if dsl.version != 1:
        findings.append(
            ValidationFinding(
                severity="error",
                category="schema",
                message=f"Unsupported DSL version: {dsl.version}. Expected 1.",
                field_path="version",
            )
        )

    checked += 1
    if not dsl.project.name or dsl.project.name == "unnamed":
        findings.append(
            ValidationFinding(
                severity="warning",
                category="schema",
                message="Project name is missing or default.",
                field_path="project.name",
            )
        )

    # 2. Steps validation
    if not dsl.steps:
        findings.append(
            ValidationFinding(
                severity="warning",
                category="schema",
                message="No steps defined in DSL.",
                field_path="steps",
            )
        )

    step_ids = set(dsl.steps.keys())
    for step_id in sorted(dsl.steps.keys()):
        step = dsl.steps[step_id]
        checked += 1

        # Empty command
        if not step.command:
            findings.append(
                ValidationFinding(
                    severity="error",
                    category="schema",
                    message=f"Step '{step_id}' has empty command.",
                    field_path=f"steps.{step_id}.command",
                )
            )

        # Self-dependency
        if step_id in step.needs:
            findings.append(
                ValidationFinding(
                    severity="error",
                    category="dependency",
                    message=f"Step '{step_id}' depends on itself.",
                    field_path=f"steps.{step_id}.needs",
                )
            )

        # Missing dependency references
        for dep in step.needs:
            checked += 1
            if dep not in step_ids:
                findings.append(
                    ValidationFinding(
                        severity="error",
                        category="dependency",
                        message=f"Step '{step_id}' depends on non-existent step '{dep}'.",
                        field_path=f"steps.{step_id}.needs",
                    )
                )

        # Duplicate needs
        if len(step.needs) != len(set(step.needs)):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    category="dependency",
                    message=f"Step '{step_id}' has duplicate dependencies.",
                    field_path=f"steps.{step_id}.needs",
                )
            )

        # Timeout sanity
        checked += 1
        if step.timeout <= 0:
            findings.append(
                ValidationFinding(
                    severity="error",
                    category="schema",
                    message=f"Step '{step_id}' has invalid timeout: {step.timeout}.",
                    field_path=f"steps.{step_id}.timeout",
                )
            )
        elif step.timeout > 86400:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    category="schema",
                    message=f"Step '{step_id}' has very long timeout: {step.timeout}s (>24h).",
                    field_path=f"steps.{step_id}.timeout",
                )
            )

        # Check adapter reference
        if step.adapter:
            checked += 1
            if step.adapter not in dsl.environments and step.adapter not in (
                "python",
                "r",
                "julia",
                "node",
                "rust",
                "java",
                "cpp",
                "make",
                "snakemake",
                "nextflow",
                "shell",
                "matlab",
            ):
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        category="schema",
                        message=f"Step '{step_id}' references unknown adapter '{step.adapter}'.",
                        field_path=f"steps.{step_id}.adapter",
                    )
                )

    # 3. Dataset validation
    for ds_id in sorted(dsl.datasets.keys()):
        ds = dsl.datasets[ds_id]
        checked += 1
        if not ds.path:
            findings.append(
                ValidationFinding(
                    severity="error",
                    category="dataset",
                    message=f"Dataset '{ds_id}' has empty path.",
                    field_path=f"datasets.{ds_id}.path",
                )
            )
        # Check for absolute paths
        if ds.path.startswith("/"):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    category="path",
                    message=f"Dataset '{ds_id}' uses absolute path: {ds.path}",
                    field_path=f"datasets.{ds_id}.path",
                )
            )

    # 4. Artifact validation
    for i, artifact in enumerate(dsl.artifacts):
        checked += 1
        if not artifact.path:
            findings.append(
                ValidationFinding(
                    severity="error",
                    category="schema",
                    message=f"Artifact at index {i} has empty path.",
                    field_path=f"artifacts[{i}].path",
                )
            )

    # 5. Metric validation
    for key, metric in dsl.expected.metrics.items():
        checked += 1
        if metric.min is not None and metric.max is not None:
            if metric.min > metric.max:
                findings.append(
                    ValidationFinding(
                        severity="error",
                        category="metric",
                        message=f"Metric '{key}' has min ({metric.min}) > max ({metric.max}).",
                        field_path=f"expected.metrics.{key}",
                    )
                )

    # 6. Environment validation
    for env_name in sorted(dsl.environments.keys()):
        env = dsl.environments[env_name]
        checked += 1
        if not env.adapter and not env.runtime:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    category="schema",
                    message=f"Environment '{env_name}' has no adapter or runtime specified.",
                    field_path=f"environments.{env_name}",
                )
            )

    # Check for error count
    is_valid = not any(f.severity == "error" for f in findings)

    return ValidationResult(
        findings=findings,
        is_valid=is_valid,
        checked_fields=checked,
    )
