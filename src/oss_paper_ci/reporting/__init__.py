"""Report generation for oss-paper-ci."""

from oss_paper_ci.reporting.json_report import generate_json_report
from oss_paper_ci.reporting.markdown_report import generate_markdown_report

__all__ = ["generate_json_report", "generate_markdown_report"]
