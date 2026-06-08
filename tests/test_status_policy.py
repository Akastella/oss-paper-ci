"""Tests for status policy and finding classification."""

import pytest

from oss_paper_ci.models import CheckResult, Severity, Status
from oss_paper_ci.scoring import classify_finding, compute_score


class TestClassifyFinding:
    """Test classify_finding function."""

    def test_blocking_error_fail(self):
        c = CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m")
        assert classify_finding(c) == "blocking"

    def test_blocking_env_fail(self):
        c = CheckResult(id="ENV001", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m")
        assert classify_finding(c) == "blocking"

    def test_important_warning_fail(self):
        c = CheckResult(id="EXP001", title="t", severity=Severity.WARNING, status=Status.FAIL, message="m")
        assert classify_finding(c) == "important"

    def test_important_error_warn(self):
        c = CheckResult(id="META003", title="t", severity=Severity.ERROR, status=Status.WARN, message="m")
        assert classify_finding(c) == "important"

    def test_advisory_info_warn(self):
        c = CheckResult(id="META005", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_ci_maintenance(self):
        c = CheckResult(id="CI004", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_ci003(self):
        c = CheckResult(id="CI003", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_ci005(self):
        c = CheckResult(id="CI005", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_ci006(self):
        c = CheckResult(id="CI006", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_meta007(self):
        c = CheckResult(id="META007", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_pass(self):
        c = CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_info_pass(self):
        c = CheckResult(id="META003", title="t", severity=Severity.INFO, status=Status.PASS, message="m")
        assert classify_finding(c) == "advisory"


class TestStatusPolicyComputeScore:
    """Test status determination via compute_score."""

    def test_advisory_does_not_affect_status(self):
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
            CheckResult(id="CI004", title="t", severity=Severity.INFO, status=Status.WARN, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "pass"

    def test_blocking_fails(self):
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "fail"

    def test_important_warns(self):
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
            CheckResult(id="EXP001", title="t", severity=Severity.WARNING, status=Status.FAIL, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "warn"

    def test_all_pass_gives_pass(self):
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
            CheckResult(id="ENV001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "pass"

    def test_multiple_advisories_still_pass(self):
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
            CheckResult(id="CI003", title="t", severity=Severity.INFO, status=Status.WARN, message="m"),
            CheckResult(id="CI004", title="t", severity=Severity.INFO, status=Status.WARN, message="m"),
            CheckResult(id="CI005", title="t", severity=Severity.INFO, status=Status.WARN, message="m"),
            CheckResult(id="META005", title="t", severity=Severity.INFO, status=Status.WARN, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "pass"

    def test_error_warn_is_important(self):
        """Error-severity warn should be classified as important, affecting status."""
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
            CheckResult(id="ENV002", title="t", severity=Severity.ERROR, status=Status.WARN, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "warn"

    def test_score_with_no_checks(self):
        score, status, counts = compute_score([])
        assert score == 0
        assert status == "unknown"

    def test_score_all_error_fail(self):
        # Use known critical check IDs to guarantee fail status
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m"),
            CheckResult(id="META002", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m"),
            CheckResult(id="ENV001", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m"),
        ]
        score, status, _ = compute_score(checks)
        assert status == "fail"
        assert score < 50

    def test_severity_counts(self):
        checks = [
            CheckResult(id="A001", title="t", severity=Severity.INFO, status=Status.PASS, message="m"),
            CheckResult(id="A002", title="t", severity=Severity.WARNING, status=Status.WARN, message="m"),
            CheckResult(id="A003", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m"),
        ]
        _, _, counts = compute_score(checks)
        assert counts["info"] == 1
        assert counts["warning"] == 1
        assert counts["error"] == 1
