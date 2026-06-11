"""Remediation planner for reproducibility dossiers.

Converts findings and failures into prioritized, actionable steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RemediationItem:
    """A single remediation action."""

    priority: str  # P0, P1, P2, P3
    action: str
    rationale: str
    estimated_effort: str  # low, medium, high
    suggested_file: str = ""
    command_to_verify: str = ""
    blocking: bool = False
    audience: str = "author"

    def to_dict(self) -> dict[str, Any]:
        return {
            "priority": self.priority,
            "action": self.action,
            "rationale": self.rationale,
            "estimated_effort": self.estimated_effort,
            "suggested_file": self.suggested_file,
            "command_to_verify": self.command_to_verify,
            "blocking": self.blocking,
            "audience": self.audience,
        }


@dataclass
class RiskItem:
    """A single risk register entry."""

    risk_id: str
    title: str
    severity: str  # low, medium, high, critical
    likelihood: str  # low, medium, high
    impact: str
    evidence: str
    mitigation: str
    owner_hint: str = "author"
    does_not_mean: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_id": self.risk_id,
            "title": self.title,
            "severity": self.severity,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "evidence": self.evidence,
            "mitigation": self.mitigation,
            "owner_hint": self.owner_hint,
            "does_not_mean": self.does_not_mean,
        }


def build_remediation_from_scan(scan_data: dict[str, Any]) -> list[RemediationItem]:
    """Build remediation plan from scan report."""
    items: list[RemediationItem] = []
    checks = scan_data.get("checks", [])

    for check in checks:
        if check.get("status") not in ("fail", "warn"):
            continue

        severity = check.get("severity", "warning")
        cid = check.get("id", "")
        message = check.get("message", "")
        recommendation = check.get("recommendation", "")

        if severity == "error":
            priority = "P0"
            effort = "medium"
            blocking = True
        elif severity == "warning":
            priority = "P1"
            effort = "low"
            blocking = False
        else:
            priority = "P2"
            effort = "low"
            blocking = False

        items.append(RemediationItem(
            priority=priority,
            action=recommendation or f"Address {cid}: {message}",
            rationale=f"Check {cid} reported: {message}",
            estimated_effort=effort,
            command_to_verify=f"oss-paper-ci scan .  # check {cid}",
            blocking=blocking,
        ))

    # Sort by priority
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    items.sort(key=lambda x: priority_order.get(x.priority, 9))

    return items


def build_remediation_from_reproduce(reproduce_data: dict[str, Any]) -> list[RemediationItem]:
    """Build remediation plan from reproduce report."""
    items: list[RemediationItem] = []

    # Missing environment
    env = reproduce_data.get("environment", {})
    if not env or not env.get("environment_files"):
        items.append(RemediationItem(
            priority="P0",
            action="Add a requirements.txt or pyproject.toml with dependencies",
            rationale="No environment files were found. Dependencies cannot be installed automatically.",
            estimated_effort="low",
            suggested_file="requirements.txt",
            command_to_verify="oss-paper-ci reproduce . --dry-run",
            blocking=True,
        ))

    # Missing commands
    if not reproduce_data.get("reproduction_commands"):
        items.append(RemediationItem(
            priority="P0",
            action="Add a reproducibility.yml with experiment commands",
            rationale="No reproduction command was found. Others cannot know how to reproduce.",
            estimated_effort="low",
            suggested_file="reproducibility.yml",
            command_to_verify="oss-paper-ci reproduce . --dry-run",
            blocking=True,
        ))

    # Failed commands
    for i, cmd_result in enumerate(reproduce_data.get("command_results", [])):
        if cmd_result.get("exit_code", 0) != 0 and not cmd_result.get("blocked"):
            items.append(RemediationItem(
                priority="P1",
                action=f"Fix command failure: {cmd_result.get('command', 'unknown')}",
                rationale=f"Command exited with code {cmd_result.get('exit_code')}",
                estimated_effort="medium",
                command_to_verify=f"oss-paper-ci reproduce . --execute",
                blocking=False,
            ))

    return items


def build_risk_register_from_scan(scan_data: dict[str, Any]) -> list[RiskItem]:
    """Build risk register from scan report."""
    risks: list[RiskItem] = []
    checks = scan_data.get("checks", [])

    check_index = {c["id"]: c for c in checks}

    # Missing environment
    env_check = check_index.get("ENV001")
    if env_check and env_check.get("status") == "fail":
        risks.append(RiskItem(
            risk_id="missing_environment",
            title="Missing environment declaration",
            severity="high",
            likelihood="high",
            impact="Others cannot install dependencies to reproduce results.",
            evidence=env_check.get("message", ""),
            mitigation="Add requirements.txt or pyproject.toml.",
            does_not_mean="The research is flawed. It means the setup is not documented.",
        ))

    # Missing reproduction command
    exp_check = check_index.get("EXP001")
    if exp_check and exp_check.get("status") == "fail":
        risks.append(RiskItem(
            risk_id="missing_reproduction_command",
            title="No declared reproduction command",
            severity="high",
            likelihood="high",
            impact="Others cannot know how to run the experiments.",
            evidence=exp_check.get("message", ""),
            mitigation="Add reproducibility.yml with experiment commands.",
            does_not_mean="The code cannot be reproduced. It means the path is not declared.",
        ))

    # Missing data instructions
    data_check = check_index.get("DATA001")
    if data_check and data_check.get("status") in ("fail", "warn"):
        risks.append(RiskItem(
            risk_id="missing_data_instructions",
            title="Missing data documentation",
            severity="medium",
            likelihood="medium",
            impact="Others may not know what data is needed or where to get it.",
            evidence=data_check.get("message", ""),
            mitigation="Add data/README.md with download instructions.",
            does_not_mean="The data is unavailable. It means it is not documented here.",
        ))

    # Missing license
    license_check = check_index.get("META002")
    if license_check and license_check.get("status") == "fail":
        risks.append(RiskItem(
            risk_id="unclear_license",
            title="Missing or unclear license",
            severity="medium",
            likelihood="medium",
            impact="Others may not know if they can use or modify the code.",
            evidence=license_check.get("message", ""),
            mitigation="Add a LICENSE file.",
            does_not_mean="The code is restricted. It means terms are not stated.",
        ))

    return risks
