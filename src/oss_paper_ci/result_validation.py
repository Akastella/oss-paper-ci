"""Result and artifact validation for reproducibility.

Checks existence, format, and schema of declared result artifacts.
Does NOT verify scientific correctness of results.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    """A single validation result."""

    check_id: str
    title: str
    status: str  # present, missing, invalid, unknown
    message: str
    recommendation: str = ""
    severity: str = "info"

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "status": self.status,
            "message": self.message,
            "recommendation": self.recommendation,
            "severity": self.severity,
        }


def run_result_validation(repo_path: str) -> list[ValidationResult]:
    """Run result and artifact validation.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of ValidationResult items.
    """
    root = Path(repo_path)
    results: list[ValidationResult] = []

    # 1. results/ directory
    results_dir = root / "results"
    if results_dir.exists():
        result_files = list(results_dir.glob("*"))
        results.append(ValidationResult(
            check_id="RESULTS_DIR",
            title="Results directory",
            status="present",
            message=f"results/ directory exists with {len(result_files)} file(s)",
            severity="info",
        ))
    else:
        results.append(ValidationResult(
            check_id="RESULTS_DIR",
            title="Results directory",
            status="missing",
            message="No results/ directory found",
            recommendation="Create a results/ directory for output artifacts.",
            severity="warning",
        ))

    # 2. metrics.json
    metrics_files = list(root.glob("results/metrics*.json"))
    if not metrics_files:
        metrics_files = list(root.glob("**/metrics.json"))

    if metrics_files:
        for mf in metrics_files[:3]:
            rel = str(mf.relative_to(root))
            try:
                content = json.loads(mf.read_text(encoding="utf-8"))
                if isinstance(content, dict):
                    # Check if values are numeric
                    numeric_count = sum(1 for v in content.values() if isinstance(v, (int, float)))
                    results.append(ValidationResult(
                        check_id="METRICS_JSON",
                        title="Metrics file",
                        status="present",
                        message=f"{rel} is valid JSON with {len(content)} fields ({numeric_count} numeric)",
                        severity="info",
                    ))
                else:
                    results.append(ValidationResult(
                        check_id="METRICS_JSON",
                        title="Metrics file",
                        status="invalid",
                        message=f"{rel} is valid JSON but not a dict",
                        recommendation="Metrics file should be a JSON object.",
                        severity="warning",
                    ))
            except json.JSONDecodeError as e:
                results.append(ValidationResult(
                    check_id="METRICS_JSON",
                    title="Metrics file",
                    status="invalid",
                    message=f"{rel} is not valid JSON: {e}",
                    recommendation="Fix JSON syntax in metrics file.",
                    severity="error",
                ))
    else:
        results.append(ValidationResult(
            check_id="METRICS_JSON",
            title="Metrics file",
            status="missing",
            message="No metrics.json found",
            recommendation="Generate a metrics.json with key results.",
            severity="warning",
        ))

    # 3. figures/ directory
    figures_dir = root / "figures"
    if figures_dir.exists():
        fig_files = list(figures_dir.glob("*"))
        results.append(ValidationResult(
            check_id="FIGURES_DIR",
            title="Figures directory",
            status="present",
            message=f"figures/ directory exists with {len(fig_files)} file(s)",
            severity="info",
        ))
    else:
        results.append(ValidationResult(
            check_id="FIGURES_DIR",
            title="Figures directory",
            status="missing",
            message="No figures/ directory found",
            recommendation="Create a figures/ directory for generated figures.",
            severity="info",
        ))

    # 4. tables/ directory
    tables_dir = root / "tables"
    if tables_dir.exists():
        results.append(ValidationResult(
            check_id="TABLES_DIR",
            title="Tables directory",
            status="present",
            message="tables/ directory exists",
            severity="info",
        ))

    # 5. Expected artifacts from reproducibility.yml
    contract_path = _find_contract(root)
    if contract_path:
        expected = _parse_expected_outputs(contract_path)
        if expected:
            for artifact_path in expected:
                full_path = root / artifact_path
                if full_path.exists():
                    results.append(ValidationResult(
                        check_id=f"EXPECTED_ARTIFACT",
                        title=f"Expected artifact: {artifact_path}",
                        status="present",
                        message=f"{artifact_path} exists as declared",
                        severity="info",
                    ))
                else:
                    results.append(ValidationResult(
                        check_id=f"EXPECTED_ARTIFACT",
                        title=f"Expected artifact: {artifact_path}",
                        status="missing",
                        message=f"{artifact_path} is declared but not found",
                        recommendation=f"Run the reproduction command to generate {artifact_path}.",
                        severity="warning",
                    ))

    # 6. Large result files
    large_results = _find_large_files(root / "results" if results_dir.exists() else root)
    if large_results:
        results.append(ValidationResult(
            check_id="RESULTS_LARGE_FILES",
            title="Large result files",
            status="present",
            message=f"Found {len(large_results)} large file(s) in results/",
            recommendation="Consider compressing large result files.",
            severity="info",
        ))

    return results


def _find_contract(root: Path) -> Path | None:
    """Find reproducibility.yml contract."""
    for name in ("reproducibility.yml", "reproducibility.yaml"):
        if (root / name).exists():
            return root / name
    return None


def _parse_expected_outputs(contract_path: Path) -> list[str]:
    """Parse expected outputs from reproducibility.yml."""
    import yaml
    try:
        data = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(data, dict):
        return []

    outputs = []
    experiments = data.get("experiments", [])
    if isinstance(experiments, list):
        for exp in experiments:
            if isinstance(exp, dict):
                for output in exp.get("expected_outputs", []):
                    if isinstance(output, str):
                        outputs.append(output)
    return outputs


def _find_large_files(path: Path, threshold_mb: int = 50) -> list[Path]:
    """Find large files in a directory."""
    if not path.exists():
        return []
    threshold_bytes = threshold_mb * 1024 * 1024
    found = []
    for f in path.glob("*"):
        if f.is_file():
            try:
                if f.stat().st_size > threshold_bytes:
                    found.append(f)
            except OSError:
                pass
    return found[:5]
