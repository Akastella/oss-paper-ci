"""Tests for the scoring engine."""

import pytest

from oss_paper_ci.models import CheckResult, Severity, Status
from oss_paper_ci.scoring import compute_score, get_score_breakdown


def _make(check_id: str, severity: Severity, status: Status) -> CheckResult:
    return CheckResult(
        id=check_id, title="test", severity=severity, status=status, message="test",
    )


class TestComputeScore:
    def test_empty_checks(self):
        score, status, counts = compute_score([])
        assert score == 0
        assert status == "unknown"

    def test_all_pass(self):
        checks = [
            _make("META001", Severity.ERROR, Status.PASS),
            _make("ENV001", Severity.ERROR, Status.PASS),
            _make("EXP001", Severity.ERROR, Status.PASS),
        ]
        score, status, counts = compute_score(checks)
        assert score == 100
        assert status == "pass"

    def test_critical_fail_low_score(self):
        """Missing README + LICENSE + env file should score below 50."""
        checks = [
            _make("META001", Severity.ERROR, Status.FAIL),  # README
            _make("META002", Severity.ERROR, Status.FAIL),  # LICENSE
            _make("ENV001", Severity.ERROR, Status.FAIL),   # env file
        ]
        score, status, counts = compute_score(checks)
        assert score < 50, f"Score {score} should be < 50 for missing critical artifacts"
        assert status == "fail"

    def test_warnings_reduce_score_moderately(self):
        """Warnings should reduce score but not tank it."""
        checks = [
            _make("META001", Severity.ERROR, Status.PASS),
            _make("ENV001", Severity.ERROR, Status.PASS),
            _make("META003", Severity.WARNING, Status.WARN),
            _make("ENV002", Severity.WARNING, Status.WARN),
        ]
        score, status, counts = compute_score(checks)
        assert 70 <= score <= 100, f"Score {score} should be 70-100 with minor warnings"

    def test_score_bounded_0_100(self):
        checks = [_make(f"X00{i}", Severity.ERROR, Status.FAIL) for i in range(100)]
        score, _, _ = compute_score(checks)
        assert 0 <= score <= 100

    def test_counts_correct(self):
        checks = [
            _make("META001", Severity.INFO, Status.PASS),
            _make("META002", Severity.WARNING, Status.WARN),
            _make("META003", Severity.ERROR, Status.FAIL),
        ]
        _, _, counts = compute_score(checks)
        assert counts["info"] == 1
        assert counts["warning"] == 1
        assert counts["error"] == 1

    def test_error_fail_determines_status(self):
        """Any error-severity fail should result in fail status."""
        checks = [
            _make("META001", Severity.ERROR, Status.PASS),
            _make("META002", Severity.ERROR, Status.FAIL),
        ]
        _, status, _ = compute_score(checks)
        assert status == "fail"

    def test_advisory_warns_preserve_pass(self):
        """Advisory warnings (info-severity warn) should not change status to warn."""
        checks = [
            _make("META001", Severity.ERROR, Status.PASS),
            _make("META003", Severity.INFO, Status.WARN),  # advisory
        ]
        score, status, _ = compute_score(checks)
        assert status == "pass"  # advisory warnings don't affect status

    def test_important_warns_give_warn_status(self):
        """Important warnings (warning-severity fail) should give warn status."""
        checks = [
            _make("META001", Severity.ERROR, Status.PASS),
            _make("META003", Severity.WARNING, Status.FAIL),  # important
        ]
        score, status, _ = compute_score(checks)
        assert status == "warn"

    def test_category_cap(self):
        """Many failures in same category should be capped."""
        checks = [
            _make(f"ENV00{i}", Severity.WARNING, Status.WARN) for i in range(1, 10)
        ]
        score, _, _ = compute_score(checks)
        # With cap of 20 for ENV category, score should be at least 80
        assert score >= 75, f"Score {score} should be >= 75 with category cap"


class TestScoreBreakdown:
    def test_breakdown_only_non_passing(self):
        checks = [
            _make("META001", Severity.ERROR, Status.PASS),
            _make("META002", Severity.ERROR, Status.FAIL),
        ]
        breakdown = get_score_breakdown(checks)
        assert len(breakdown) == 1
        assert breakdown[0]["id"] == "META002"
        assert breakdown[0]["deduction"] > 0

    def test_breakdown_empty_for_all_pass(self):
        checks = [
            _make("META001", Severity.ERROR, Status.PASS),
        ]
        breakdown = get_score_breakdown(checks)
        assert len(breakdown) == 0
