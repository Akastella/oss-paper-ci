"""JSON report generation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oss_paper_ci.models import Report


def generate_json_report(report: Report, output_path: str | None = None) -> str:
    """Generate a JSON report string.

    Args:
        report: The Report object.
        output_path: If provided, write to this file.

    Returns:
        JSON string of the report.
    """
    data = report.to_dict()
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
    return text
