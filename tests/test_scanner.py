"""Tests for the scanner module and checker integration."""

import json
import pytest
from pathlib import Path

from oss_paper_ci.scanner import scan
from oss_paper_ci.config import Config


FIXTURES = Path(__file__).parent / "fixtures"
BAD_REPO = str(FIXTURES / "minimal_bad_repo")
BROKEN_REPO = str(FIXTURES / "broken_paper_repo")
GOOD_REPO = str(FIXTURES / "paper_ready_repo")


class TestScanner:
    def test_scan_produces_report(self):
        report = scan(BAD_REPO)
        assert report.tool == "oss-paper-ci"
        assert len(report.checks) > 0

    def test_scan_with_config(self):
        config = Config()
        config.checks.min_score = 50
        report = scan(BAD_REPO, config=config)
        assert report.summary.score >= 0

    def test_bad_repo_has_failures(self):
        report = scan(BAD_REPO)
        fail_statuses = [c.status for c in report.checks if c.status.value == "fail"]
        assert len(fail_statuses) > 0

    def test_score_ordering(self):
        bad = scan(BAD_REPO)
        broken = scan(BROKEN_REPO)
        good = scan(GOOD_REPO)
        assert good.summary.score > broken.summary.score > bad.summary.score

    def test_report_to_dict_json_serializable(self):
        report = scan(GOOD_REPO)
        data = report.to_dict()
        text = json.dumps(data)
        parsed = json.loads(text)
        assert parsed["tool"] == "oss-paper-ci"

    def test_check_ids_unique_per_checker(self):
        report = scan(GOOD_REPO)
        ids = [c.id for c in report.checks]
        assert len(set(ids)) >= 5

    def test_all_checks_have_required_fields(self):
        report = scan(GOOD_REPO)
        for c in report.checks:
            assert c.id
            assert c.title
            assert c.severity.value in ("info", "warning", "error")
            assert c.status.value in ("pass", "warn", "fail", "unknown")
            assert c.message

    def test_detected_languages(self):
        report = scan(GOOD_REPO)
        assert "Python" in report.repository.detected_languages

    def test_score_breakdown_present(self):
        report = scan(BAD_REPO)
        assert len(report.summary.score_breakdown) > 0


class TestScoreRanges:
    def test_bad_repo_score_low(self):
        report = scan(BAD_REPO)
        assert report.summary.score < 50
        assert report.summary.status == "fail"

    def test_broken_repo_score_medium(self):
        report = scan(BROKEN_REPO)
        assert 30 <= report.summary.score <= 75

    def test_good_repo_score_high(self):
        report = scan(GOOD_REPO)
        assert report.summary.score >= 80


class TestCheckerCoverage:
    def test_metadata_checks_present(self):
        ids = {c.id for c in scan(GOOD_REPO).checks}
        assert "META001" in ids
        assert "META002" in ids

    def test_environment_checks_present(self):
        assert "ENV001" in {c.id for c in scan(GOOD_REPO).checks}

    def test_experiment_checks_present(self):
        assert "EXP001" in {c.id for c in scan(GOOD_REPO).checks}

    def test_data_checks_present(self):
        assert "DATA001" in {c.id for c in scan(GOOD_REPO).checks}

    def test_results_checks_present(self):
        assert "RES001" in {c.id for c in scan(GOOD_REPO).checks}

    def test_paper_code_checks_present(self):
        assert "PAP001" in {c.id for c in scan(GOOD_REPO).checks}

    def test_ci_checks_present(self):
        assert "CI001" in {c.id for c in scan(GOOD_REPO).checks}
