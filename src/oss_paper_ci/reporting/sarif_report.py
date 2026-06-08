"""SARIF (Static Analysis Results Interchange Format) v2.1.0 report generation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oss_paper_ci.models import Report

_SEVERITY_TO_LEVEL = {
    "error": "error",
    "warning": "warning",
    "info": "note",
}

_STATUS_TO_LEVEL = {
    "fail": "error",
    "warn": "warning",
    "pass": "none",
    "unknown": "none",
}

# Map check ID prefix to SARIF category
_CATEGORY_MAP = {
    "META": "metadata",
    "ENV": "environment",
    "EXP": "experiments",
    "DATA": "data",
    "RES": "results",
    "PAP": "paper-code",
    "CI": "ci-maintenance",
    "CON": "contract",
}


def _get_category(check_id: str) -> str:
    prefix = check_id[:3] if len(check_id) >= 3 else check_id
    return _CATEGORY_MAP.get(prefix, "other")


def _extract_file_from_evidence(evidence: list[str]) -> str | None:
    """Try to extract a file path from evidence items."""
    for item in evidence:
        # Look for file-like paths
        item = item.strip()
        if item.endswith(('.py', '.sh', '.yml', '.yaml', '.toml', '.txt', '.md', '.tex', '.bib', '.ipynb')):
            return item
        if '/' in item and not item.startswith('http'):
            return item
        if '\\' in item:
            return item.replace('\\', '/')
    return None


def _make_rule(check: dict) -> dict:
    """Build a SARIF reportingDescriptor from a check dict."""
    severity = check.get("severity", "info")
    level = _SEVERITY_TO_LEVEL.get(severity, "warning")
    category = _get_category(check.get("id", ""))
    return {
        "id": check["id"],
        "name": check["id"],
        "shortDescription": {"text": check.get("title", check["id"])},
        "fullDescription": {"text": check.get("recommendation", check.get("message", ""))},
        "defaultConfiguration": {"level": level},
        "properties": {
            "category": category,
            "severity": severity,
        },
        "help": {
            "text": check.get("recommendation", check.get("title", "")),
        },
    }


def _make_result(check: dict, include_pass: bool = False) -> dict | None:
    """Build a SARIF result from a check dict. Returns None for pass if not including pass."""
    status = check.get("status", "unknown")
    level = _STATUS_TO_LEVEL.get(status, "none")

    # Skip pass results by default
    if not include_pass and status == "pass":
        return None

    # Compose message
    parts = [check.get("message", "")]
    evidence = check.get("evidence", [])
    if evidence:
        parts.append("Evidence:")
        for item in evidence:
            parts.append(f"- {item}")

    message_text = "\n".join(parts)

    result: dict = {
        "ruleId": check["id"],
        "level": level,
        "message": {"text": message_text},
    }

    # Add physicalLocation if we can identify a file
    file_path = _extract_file_from_evidence(evidence)
    if file_path:
        result["locations"] = [{
            "physicalLocation": {
                "artifactLocation": {"uri": file_path},
            }
        }]

    # Add related locations for evidence
    if evidence:
        related_locations = []
        for i, item in enumerate(evidence):
            loc: dict = {
                "id": i,
                "message": {"text": item},
            }
            # If item looks like a file, add physicalLocation
            if any(item.endswith(ext) for ext in ('.py', '.sh', '.yml', '.yaml', '.toml', '.txt', '.md', '.tex', '.bib', '.ipynb')):
                loc["physicalLocation"] = {
                    "artifactLocation": {"uri": item.replace('\\', '/')},
                }
            related_locations.append(loc)
        result["relatedLocations"] = related_locations

    return result


def generate_sarif_report(
    report: Report,
    output_path: str | None = None,
    include_pass: bool = False,
) -> str:
    """Generate a SARIF v2.1.0 JSON report.

    Args:
        report: The Report object.
        output_path: If provided, write to this file.
        include_pass: If True, include passing checks. Default False.

    Returns:
        SARIF JSON string.
    """
    rules = []
    results = []
    seen_rules = set()

    for check in report.checks:
        check_dict = check.to_dict() if hasattr(check, "to_dict") else check

        # Add rule (deduplicated)
        rule_id = check_dict["id"]
        if rule_id not in seen_rules:
            rules.append(_make_rule(check_dict))
            seen_rules.add(rule_id)

        # Add result
        result = _make_result(check_dict, include_pass=include_pass)
        if result is not None:
            results.append(result)

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": report.tool,
                        "version": report.version,
                        "informationUri": "https://github.com/<owner>/<repo>",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }

    text = json.dumps(sarif, indent=2, ensure_ascii=False)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
    return text
