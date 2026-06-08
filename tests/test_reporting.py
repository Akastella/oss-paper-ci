"""Tests for report generation."""

import json
import pytest

from oss_paper_ci.models import CheckResult, Report, ReportMetadata, RepoInfo, Summary, Severity, Status
from oss_paper_ci.reporting import generate_json_report, generate_markdown_report, generate_sarif_report


def _sample_report() -> Report:
    return Report(
        schema_version="0.2",
        repository=RepoInfo(path="/test", detected_languages=["Python"]),
        summary=Summary(score=75, status="warn", counts={"info": 1, "warning": 1, "error": 0}),
        checks=[
            CheckResult(
                id="META001", title="README exists", severity=Severity.INFO,
                status=Status.PASS, message="README.md found",
            ),
            CheckResult(
                id="ENV001", title="Environment file", severity=Severity.ERROR,
                status=Status.WARN, message="No requirements.txt",
                evidence=["No requirements.txt", "No environment.yml"],
                recommendation="Add a requirements.txt file",
            ),
        ],
        metadata=ReportMetadata(
            generated_at="2025-01-01T00:00:00+00:00",
            scanned_files=10,
            ignored_paths=[".git"],
        ),
        recommendations=["Add a requirements.txt file"],
        blocking_issues=[],
    )


class TestJsonReport:
    def test_valid_json(self):
        report = _sample_report()
        text = generate_json_report(report)
        data = json.loads(text)
        assert data["tool"] == "oss-paper-ci"
        assert data["schema_version"] == "0.2"
        assert len(data["checks"]) == 2

    def test_score_in_report(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert data["summary"]["score"] == 75
        assert data["summary"]["status"] == "warn"

    def test_write_to_file(self, tmp_path):
        report = _sample_report()
        out = tmp_path / "report.json"
        generate_json_report(report, output_path=str(out))
        data = json.loads(out.read_text())
        assert data["tool"] == "oss-paper-ci"

    def test_schema_completeness(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        # Required top-level fields
        assert "schema_version" in data
        assert "tool" in data
        assert "version" in data
        assert "metadata" in data
        assert "repository" in data
        assert "summary" in data
        assert "checks" in data
        assert "recommendations" in data
        assert "blocking_issues" in data
        # Metadata fields
        assert "generated_at" in data["metadata"]
        # Repository fields
        assert "path" in data["repository"]
        assert "detected_languages" in data["repository"]
        # Check fields
        check = data["checks"][0]
        assert "id" in check
        assert "title" in check
        assert "severity" in check
        assert "status" in check
        assert "message" in check
        assert "evidence" in check
        assert "recommendation" in check


class TestMarkdownReport:
    def test_contains_header(self):
        report = _sample_report()
        text = generate_markdown_report(report)
        assert "oss-paper-ci Report" in text

    def test_contains_score(self):
        report = _sample_report()
        text = generate_markdown_report(report)
        assert "75/100" in text

    def test_contains_disclaimer(self):
        report = _sample_report()
        text = generate_markdown_report(report)
        assert "Disclaimer" in text or "disclaimer" in text
        assert "reproducibility readiness" in text.lower()

    def test_contains_check_details_in_verbose(self):
        report = _sample_report()
        text = generate_markdown_report(report, verbose=True)
        assert "META001" in text
        assert "ENV001" in text

    def test_contains_evidence_in_verbose(self):
        report = _sample_report()
        text = generate_markdown_report(report, verbose=True)
        assert "requirements.txt" in text

    def test_default_mode_shows_summary(self):
        report = _sample_report()
        text = generate_markdown_report(report)
        assert "75/100" in text
        # Default mode shows warnings section
        assert "ENV001" in text

    def test_default_mode_hides_verbose_details(self):
        """In default mode, PASS checks should not appear in check details table."""
        report = _sample_report()
        text = generate_markdown_report(report, verbose=False)
        # META001 is PASS, should not appear outside of the summary
        # (it only appears in the check details table which is verbose-only)
        assert "Check Details" not in text

    def test_write_to_file(self, tmp_path):
        report = _sample_report()
        out = tmp_path / "report.md"
        generate_markdown_report(report, output_path=str(out))
        content = out.read_text(encoding="utf-8")
        assert "oss-paper-ci" in content


class TestSarifReport:
    def test_valid_json(self):
        report = _sample_report()
        text = generate_sarif_report(report)
        data = json.loads(text)
        assert data["version"] == "2.1.0"
        assert "$schema" in data

    def test_structure(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        assert "runs" in data
        assert len(data["runs"]) == 1
        run = data["runs"][0]
        assert "tool" in run
        assert "results" in run
        driver = run["tool"]["driver"]
        assert driver["name"] == "oss-paper-ci"
        assert driver["version"] == report.version
        assert "informationUri" in driver

    def test_rules_match_checks(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        rules = data["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) == 2
        rule_ids = {r["id"] for r in rules}
        assert "META001" in rule_ids
        assert "ENV001" in rule_ids

    def test_results_exclude_pass_by_default(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        results = data["runs"][0]["results"]
        # Default excludes pass results
        result_ids = {r["ruleId"] for r in results}
        assert "META001" not in result_ids  # pass excluded
        assert "ENV001" in result_ids  # warn included

    def test_results_include_pass_when_asked(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report, include_pass=True))
        results = data["runs"][0]["results"]
        assert len(results) == 2

    def test_level_mapping(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report, include_pass=True))
        results = {r["ruleId"]: r for r in data["runs"][0]["results"]}
        # PASS -> none
        assert results["META001"]["level"] == "none"
        # WARN -> warning
        assert results["ENV001"]["level"] == "warning"

    def test_evidence_in_related_locations(self):
        report = _sample_report()
        data = json.loads(generate_sarif_report(report))
        results = {r["ruleId"]: r for r in data["runs"][0]["results"]}
        env_result = results["ENV001"]
        assert "relatedLocations" in env_result
        assert len(env_result["relatedLocations"]) == 2

    def test_write_to_file(self, tmp_path):
        report = _sample_report()
        out = tmp_path / "report.sarif"
        generate_sarif_report(report, output_path=str(out))
        data = json.loads(out.read_text())
        assert data["version"] == "2.1.0"
