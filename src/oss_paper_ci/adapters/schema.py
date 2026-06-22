"""Schema definitions for adapter reports."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .. import __version__

SCHEMA_VERSION = "0.1"
REPORT_TYPE = "oss-paper-ci-language-adapter-report"

def build_adapter_report(path, detections, plans=None, warnings=None, limitations=None):
    report = {"schema_version": SCHEMA_VERSION, "report_type": REPORT_TYPE, "tool_version": __version__, "path": ".", "detected_adapters": detections}
    if plans: report["plans"] = plans
    recommended = None
    if detections:
        for det in sorted(detections, key=lambda d: d.get("confidence", 0), reverse=True):
            runtime = det.get("runtime", {})
            if runtime.get("available", False):
                recommended = det["name"]
                break
        if not recommended and detections: recommended = detections[0]["name"]
    if recommended: report["recommended_adapter"] = recommended
    if warnings: report["warnings"] = sorted(warnings)
    if limitations: report["limitations"] = sorted(limitations)
    return report

def validate_report(report):
    errors = []
    for field in ["schema_version", "report_type", "tool_version", "path"]:
        if field not in report: errors.append(f"Missing required field: {field}")
    if report.get("schema_version") != SCHEMA_VERSION: errors.append(f"Unexpected schema version: {report.get('schema_version')}")
    if report.get("report_type") != REPORT_TYPE: errors.append(f"Unexpected report type: {report.get('report_type')}")
    for det in report.get("detected_adapters", []):
        if "name" not in det: errors.append("Detection missing 'name' field")
        if "confidence" not in det: errors.append(f"Detection '{det.get('name', '?')}' missing 'confidence'")
    return errors
