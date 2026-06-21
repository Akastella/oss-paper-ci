"""Reproduction comparison: expected vs actual results.

Compares a reproduction run against the expected values declared in
reproducibility.yml (artifacts, metrics, command outcomes).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci.metric_validator import validate_metrics
from oss_paper_ci.repro_schema import load_orchestrator_contract


@dataclass
class ComparisonItem:
    """A single comparison result."""

    category: str = ""  # command | artifact | metric
    item_id: str = ""
    expected: Any = None
    actual: Any = None
    match: bool = True
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "category": self.category,
            "item_id": self.item_id,
            "match": self.match,
            "message": self.message,
        }
        if self.expected is not None:
            d["expected"] = self.expected
        if self.actual is not None:
            d["actual"] = self.actual
        return d


@dataclass
class ComparisonReport:
    """Report comparing expected vs actual results."""

    run_dir: str = ""
    contract_path: str = ""
    total: int = 0
    matched: int = 0
    mismatched: int = 0
    items: list[ComparisonItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_dir": self.run_dir,
            "contract_path": self.contract_path,
            "total": self.total,
            "matched": self.matched,
            "mismatched": self.mismatched,
            "items": [i.to_dict() for i in self.items],
            "warnings": self.warnings,
            "error": self.error,
        }

    @property
    def ok(self) -> bool:
        return self.mismatched == 0 and not self.error


def compare_run(
    run_dir: str,
    expected_path: str,
) -> ComparisonReport:
    """Compare a reproduction run against expected values.

    Args:
        run_dir: Path to the run directory (containing run-manifest.json).
        expected_path: Path to reproducibility.yml with expected values.

    Returns:
        ComparisonReport with per-item comparison results.
    """
    report = ComparisonReport(run_dir=run_dir, contract_path=expected_path)

    # Load run manifest
    manifest_path = Path(run_dir) / "run-manifest.json"
    if not manifest_path.exists():
        report.error = f"No run-manifest.json found in {run_dir}"
        return report

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as exc:
        report.error = f"Failed to read manifest: {exc}"
        return report

    # Load expected contract
    try:
        contract = load_orchestrator_contract(expected_path)
    except Exception as exc:
        report.error = f"Failed to load contract: {exc}"
        return report

    # Compare commands
    cmd_results = {cr["command_id"]: cr for cr in manifest.get("command_results", [])}
    for cmd in contract.commands:
        item = ComparisonItem(
            category="command",
            item_id=cmd.id,
            expected="success",
        )
        actual = cmd_results.get(cmd.id)
        if actual:
            item.actual = actual.get("status", "unknown")
            item.match = item.actual == "success"
            if not item.match:
                item.message = (
                    f"Command '{cmd.id}' status: expected 'success', "
                    f"got '{item.actual}'"
                )
        else:
            item.actual = "not_run"
            item.match = False
            item.message = f"Command '{cmd.id}' was not executed"
        report.items.append(item)

    # Compare artifacts
    art_hashes = manifest.get("artifact_hashes", {})
    for art in contract.artifacts:
        item = ComparisonItem(
            category="artifact",
            item_id=art.path,
            expected="present",
        )
        if art.path in art_hashes:
            item.actual = f"present (sha256:{art_hashes[art.path][:16]}...)"
            item.match = True
        else:
            item.actual = "missing"
            item.match = False
            item.message = f"Artifact '{art.path}' is missing"
        report.items.append(item)

    # Compare metrics
    if contract.metrics:
        # Re-validate metrics from the run
        repo_path = manifest.get("repo_path", "")
        if repo_path and repo_path != "<redacted>":
            met_report = validate_metrics(
                repo_path,
                [m.to_dict() for m in contract.metrics],
            )
            for check in met_report.checks:
                item = ComparisonItem(
                    category="metric",
                    item_id=f"{check.file}:{check.key}",
                    expected={
                        "min": check.expected_min,
                        "max": check.expected_max,
                    },
                    actual=check.actual_value,
                    match=check.in_range,
                )
                if not check.in_range:
                    item.message = (
                        f"Metric '{check.key}' value {check.actual_value} "
                        f"outside range [{check.expected_min}, {check.expected_max}]"
                    )
                report.items.append(item)

    report.total = len(report.items)
    report.matched = sum(1 for i in report.items if i.match)
    report.mismatched = report.total - report.matched

    return report


def format_compare_markdown(report: ComparisonReport) -> str:
    """Format comparison report as Markdown."""
    lines = [
        "# Reproduction Comparison",
        "",
        f"**Run directory:** `{report.run_dir}`",
        f"**Expected:** `{report.contract_path}`",
        "",
        f"**Total:** {report.total} | "
        f"**Matched:** {report.matched} | "
        f"**Mismatched:** {report.mismatched}",
        "",
    ]

    if report.error:
        lines.append(f"**Error:** {report.error}")
        lines.append("")
        return "\n".join(lines)

    # Group by category
    categories = {"command": "Commands", "artifact": "Artifacts", "metric": "Metrics"}
    for cat_key, cat_title in categories.items():
        items = [i for i in report.items if i.category == cat_key]
        if not items:
            continue
        lines.append(f"## {cat_title}")
        lines.append("")
        lines.append("| Item | Expected | Actual | Status |")
        lines.append("|------|----------|--------|--------|")
        for item in items:
            status = "✅" if item.match else "❌"
            exp = str(item.expected) if item.expected is not None else "—"
            act = str(item.actual) if item.actual is not None else "—"
            lines.append(f"| `{item.item_id}` | {exp} | {act} | {status} |")
        lines.append("")

    # Warnings
    if report.warnings:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for w in report.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Disclaimer
    lines.append("---")
    lines.append("")
    lines.append(
        "*This comparison checks declared expectations against observed results. "
        "It does not verify scientific correctness.*"
    )

    return "\n".join(lines)


def format_compare_json(report: ComparisonReport) -> str:
    """Format comparison report as JSON."""
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
