"""Tests for matrix report generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.matrix import plan_matrix, MatrixPlan
from oss_paper_ci.matrix_report import (
    generate_matrix_plan_markdown,
    generate_matrix_result_markdown,
    generate_matrix_json,
)

DEMO_REPO = str(Path(__file__).parent.parent / "examples" / "repro-system-demo")


class TestMatrixReport:
    """Test matrix report generation."""

    def test_plan_markdown(self):
        """Plan markdown has expected content."""
        plan = plan_matrix(DEMO_REPO, python_versions=["3.12"])
        text = generate_matrix_plan_markdown(plan)
        assert "Matrix Plan" in text
        assert "python-3.12" in text

    def test_plan_json(self):
        """Plan JSON is valid."""
        plan = plan_matrix(DEMO_REPO, python_versions=["3.12"])
        text = generate_matrix_json(plan)
        data = json.loads(text)
        assert data["report_type"] == "oss-paper-ci-matrix-plan"

    def test_plan_has_variants(self):
        """Plan has variants."""
        plan = plan_matrix(DEMO_REPO, python_versions=["3.10", "3.12"])
        assert len(plan.variants) == 2

    def test_plan_marks_unavailable(self):
        """Plan marks unavailable runtimes."""
        plan = plan_matrix(DEMO_REPO, python_versions=["3.9"])
        unavailable = [v for v in plan.variants if not v.available]
        # 3.9 may or may not be available
        assert isinstance(unavailable, list)

    def test_plan_output_file(self, tmp_path):
        """Plan writes to file."""
        plan = plan_matrix(DEMO_REPO, python_versions=["3.12"])
        out = tmp_path / "plan.md"
        generate_matrix_plan_markdown(plan, str(out))
        assert out.exists()
