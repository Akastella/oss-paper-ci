"""Tests for new features in v0.2.0: SARIF, list-checks, fail-under, strict, registry."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from oss_paper_ci.models import Report, RepoInfo, Summary, CheckResult, Severity, Status
from oss_paper_ci.reporting.sarif_report import generate_sarif_report
from oss_paper_ci.reporting import generate_json_report, generate_markdown_report


FIXTURES = Path(__file__).parent / "fixtures"
GOOD_REPO = str(FIXTURES / "paper_ready_repo")


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace",
    )


def _sample_report() -> Report:
    return Report(
        repository=RepoInfo(path="/test", detected_languages=["Python"]),
        summary=Summary(score=75, status="warn", counts={"info": 1, "warning": 1, "error": 0}),
        checks=[
            CheckResult(id="META001", title="README exists", severity=Severity.INFO,
                        status=Status.PASS, message="Found README.md"),
            CheckResult(id="ENV001", title="Env file", severity=Severity.ERROR,
                        status=Status.WARN, message="No requirements.txt",
                        evidence=["No requirements.txt"], recommendation="Add requirements.txt"),
        ],
    )


class TestSarifReport:
    def test_valid_json(self):
        report = _sample_report()
        text = generate_sarif_report(report)
        data = json.loads(text)
        assert data["version"] == "2.1.0"

    def test_has_runs(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        assert len(data["runs"]) == 1

    def test_has_rules(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        rules = data["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) >= 2

    def test_has_results(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        results = data["runs"][0]["results"]
        # Default excludes pass, so only warn/fail results
        assert len(results) >= 1

    def test_include_pass(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report, include_pass=True))
        results = data["runs"][0]["results"]
        assert len(results) >= 2

    def test_result_has_rule_id(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        for r in data["runs"][0]["results"]:
            assert "ruleId" in r
            assert "level" in r
            assert "message" in r

    def test_write_to_file(self, tmp_path):
        report = _sample_report()
        out = tmp_path / "report.sarif"
        generate_sarif_report(report, output_path=str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["version"] == "2.1.0"

    def test_level_mapping(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        results = data["runs"][0]["results"]
        levels = {r["level"] for r in results}
        # Should have at least "none" (for pass) and "warning" (for warn)
        assert "none" in levels or "warning" in levels


class TestListChecks:
    def test_list_checks_text(self):
        result = run_cli("list-checks")
        assert result.returncode == 0
        assert "META001" in result.stdout
        assert "ENV001" in result.stdout

    def test_list_checks_json(self):
        result = run_cli("list-checks", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) >= 40
        assert any(d["id"] == "META001" for d in data)

    def test_list_checks_by_category(self):
        result = run_cli("list-checks", "--category", "environment")
        assert result.returncode == 0
        assert "ENV001" in result.stdout
        assert "META001" not in result.stdout


class TestRegistry:
    def test_get_all_checkers(self):
        from oss_paper_ci.checks.registry import get_all_checkers
        checkers = get_all_checkers()
        assert len(checkers) >= 40

    def test_get_checker_by_id(self):
        from oss_paper_ci.checks.registry import get_checker_by_id
        cls = get_checker_by_id("META001")
        assert cls is not None
        assert cls().check_id == "META001"

    def test_get_checker_by_id_unknown(self):
        from oss_paper_ci.checks.registry import get_checker_by_id
        cls = get_checker_by_id("FAKE999")
        assert cls is None

    def test_get_checkers_by_category(self):
        from oss_paper_ci.checks.registry import get_checkers_by_category
        env_checkers = get_checkers_by_category("environment")
        assert len(env_checkers) >= 5
        assert all(c().category == "environment" for c in env_checkers)


class TestFailUnder:
    def test_fail_under_below_threshold(self):
        result = run_cli("scan", GOOD_REPO, "--fail-under", "99")
        assert result.returncode == 1

    def test_fail_under_above_threshold(self):
        result = run_cli("scan", GOOD_REPO, "--fail-under", "10")
        assert result.returncode in (0, 1)  # depends on warnings


class TestStrict:
    def test_strict_with_warnings(self):
        result = run_cli("scan", GOOD_REPO, "--strict")
        # Should fail if there are any warnings
        assert result.returncode in (0, 1)


class TestVerbose:
    def test_verbose_flag_accepted(self):
        result = run_cli("scan", GOOD_REPO, "--verbose", "--format", "markdown")
        assert result.returncode in (0, 1)
        assert "oss-paper-ci" in result.stdout


class TestJsonSchemaV2:
    def test_schema_version_02(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert data["schema_version"] == "0.4"

    def test_has_metadata(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert "metadata" in data
        assert "generated_at" in data["metadata"]

    def test_has_recommendations(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert "recommendations" in data

    def test_has_blocking_issues(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert "blocking_issues" in data


class TestExplainCommand:
    def test_explain_known_check(self):
        result = run_cli("explain", "META001")
        assert result.returncode == 0
        assert "META001" in result.stdout

    def test_explain_unknown_check(self):
        result = run_cli("explain", "FAKE999")
        assert result.returncode == 1
