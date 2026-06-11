"""Tests for result validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.result_validation import ValidationResult, run_result_validation

FIXTURES = Path(__file__).parent / "fixtures"


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_to_dict(self):
        v = ValidationResult(
            check_id="TEST",
            title="Test",
            status="present",
            message="OK",
        )
        result = v.to_dict()
        assert result["check_id"] == "TEST"


class TestResultValidation:
    """Test result validation on repos."""

    def test_results_dir_check(self):
        vals = run_result_validation(str(FIXTURES / "realistic_ml_repo"))
        ids = [v.check_id for v in vals]
        assert "RESULTS_DIR" in ids

    def test_figures_dir_check(self):
        vals = run_result_validation(str(FIXTURES / "realistic_ml_repo"))
        ids = [v.check_id for v in vals]
        assert "FIGURES_DIR" in ids

    def test_returns_list(self):
        vals = run_result_validation(str(FIXTURES / "data_missing_repo"))
        assert isinstance(vals, list)

    def test_all_have_required_fields(self):
        vals = run_result_validation(str(FIXTURES / "data_missing_repo"))
        for v in vals:
            assert v.check_id
            assert v.title
            assert v.status in ("present", "missing", "invalid", "unknown")
            assert v.message
