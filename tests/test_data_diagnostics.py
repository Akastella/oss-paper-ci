"""Tests for data diagnostics."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.data_diagnostics import DataDiagnostic, run_data_diagnostics

FIXTURES = Path(__file__).parent / "fixtures"


class TestDataDiagnostic:
    """Test DataDiagnostic dataclass."""

    def test_to_dict(self):
        d = DataDiagnostic(
            check_id="TEST",
            title="Test",
            status="present",
            message="OK",
        )
        result = d.to_dict()
        assert result["check_id"] == "TEST"
        assert result["status"] == "present"


class TestMissingData:
    """Test diagnostics on repo with missing data."""

    def test_missing_data_dir(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_missing_repo"))
        ids = [d.check_id for d in diags]
        assert "DATA_DIR" in ids

    def test_missing_data_readme(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_missing_repo"))
        readme_diag = next((d for d in diags if d.check_id == "DATA_README"), None)
        if readme_diag:
            assert readme_diag.status in ("missing", "partial")
        else:
            # DATA_README only generated if data/ exists
            dir_diag = next(d for d in diags if d.check_id == "DATA_DIR")
            assert dir_diag.status == "missing"

    def test_missing_availability_statement(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_missing_repo"))
        avail_diag = next(d for d in diags if d.check_id == "DATA_AVAILABILITY")
        assert avail_diag.status == "missing"


class TestDocumentedData:
    """Test diagnostics on repo with documented data."""

    def test_has_data_dir(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_documented_repo"))
        dir_diag = next(d for d in diags if d.check_id == "DATA_DIR")
        assert dir_diag.status == "present"

    def test_has_data_readme(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_documented_repo"))
        readme_diag = next(d for d in diags if d.check_id == "DATA_README")
        assert readme_diag.status == "present"

    def test_has_availability_statement(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_documented_repo"))
        avail_diag = next(d for d in diags if d.check_id == "DATA_AVAILABILITY")
        assert avail_diag.status == "present"


class TestDiagnosticsOutput:
    """Test diagnostics output format."""

    def test_returns_list(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_missing_repo"))
        assert isinstance(diags, list)
        assert len(diags) > 0

    def test_all_have_required_fields(self):
        diags = run_data_diagnostics(str(FIXTURES / "data_missing_repo"))
        for d in diags:
            assert d.check_id
            assert d.title
            assert d.status in ("present", "missing", "partial", "unknown")
            assert d.message
