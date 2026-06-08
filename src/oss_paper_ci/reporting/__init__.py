"""Report generation for oss-paper-ci."""

from oss_paper_ci.reporting.graph_report import (
    generate_graph_dot,
    generate_graph_json,
    generate_graph_markdown,
)
from oss_paper_ci.reporting.json_report import generate_json_report
from oss_paper_ci.reporting.markdown_report import generate_markdown_report
from oss_paper_ci.reporting.sarif_report import generate_sarif_report

__all__ = [
    "generate_graph_dot",
    "generate_graph_json",
    "generate_graph_markdown",
    "generate_json_report",
    "generate_markdown_report",
    "generate_sarif_report",
]
