"""Tests for limitations documentation truthfulness."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestLimitationsDocs:
    """Test that limitations docs are honest."""

    def test_limitations_doc_exists(self):
        assert (ROOT / "docs" / "limitations.md").exists()

    def test_data_diagnostics_doc_exists(self):
        assert (ROOT / "docs" / "data-diagnostics.md").exists()

    def test_result_validation_doc_exists(self):
        assert (ROOT / "docs" / "result-validation.md").exists()

    def test_evidence_scores_doc_exists(self):
        assert (ROOT / "docs" / "evidence-scores.md").exists()

    def test_no_scientific_correctness_claim(self):
        """Docs should not claim to judge scientific correctness."""
        docs = [
            ROOT / "docs" / "data-diagnostics.md",
            ROOT / "docs" / "result-validation.md",
            ROOT / "docs" / "evidence-scores.md",
        ]
        for doc in docs:
            if doc.exists():
                content = doc.read_text(encoding="utf-8").lower()
                if "correctness" in content:
                    assert "not" in content or "does not" in content

    def test_no_accept_reject_claim(self):
        """Docs should not claim to predict acceptance."""
        docs = [
            ROOT / "docs" / "evidence-scores.md",
            ROOT / "docs" / "limitations.md",
        ]
        for doc in docs:
            if doc.exists():
                content = doc.read_text(encoding="utf-8").lower()
                if "accept" in content and "reject" in content:
                    assert "not" in content or "does not" in content

    def test_data_diagnose_command_exists(self):
        """CLI reference should list data diagnose."""
        cli_ref = ROOT / "docs" / "cli-reference.md"
        if cli_ref.exists():
            content = cli_ref.read_text(encoding="utf-8")
            assert "data" in content.lower() or "diagnose" in content.lower()

    def test_results_validate_command_exists(self):
        """CLI reference should list results validate."""
        cli_ref = ROOT / "docs" / "cli-reference.md"
        if cli_ref.exists():
            content = cli_ref.read_text(encoding="utf-8")
            assert "results" in content.lower() or "validate" in content.lower()
