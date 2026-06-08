"""Tests for Round 4 features: contract, graph, baseline, smoke, status policy."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from oss_paper_ci.models import CheckResult, Severity, Status
from oss_paper_ci.scoring import classify_finding, compute_score


FIXTURES = Path(__file__).parent / "fixtures"
RML = str(FIXTURES / "realistic_ml_repo")
GOOD = str(FIXTURES / "paper_ready_repo")
BAD = str(FIXTURES / "minimal_bad_repo")


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace",
    )


class TestStatusPolicy:
    def test_paper_ready_repo_passes(self):
        from oss_paper_ci.scanner import scan
        report = scan(GOOD)
        assert report.summary.status == "pass", f"Expected pass, got {report.summary.status}"

    def test_realistic_ml_repo_passes(self):
        from oss_paper_ci.scanner import scan
        report = scan(RML)
        assert report.summary.status == "pass", f"Expected pass, got {report.summary.status}"

    def test_minimal_bad_repo_fails(self):
        from oss_paper_ci.scanner import scan
        report = scan(BAD)
        assert report.summary.status == "fail"

    def test_classify_blocking(self):
        c = CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.FAIL, message="m")
        assert classify_finding(c) == "blocking"

    def test_classify_important(self):
        c = CheckResult(id="EXP001", title="t", severity=Severity.WARNING, status=Status.FAIL, message="m")
        assert classify_finding(c) == "important"

    def test_classify_advisory_info_warn(self):
        c = CheckResult(id="META005", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_classify_advisory_ci_maintenance(self):
        c = CheckResult(id="CI004", title="t", severity=Severity.INFO, status=Status.WARN, message="m")
        assert classify_finding(c) == "advisory"

    def test_advisory_does_not_change_status(self):
        """Advisory warnings should not change pass to warn."""
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
            CheckResult(id="CI004", title="t", severity=Severity.INFO, status=Status.WARN, message="m"),
            CheckResult(id="META005", title="t", severity=Severity.INFO, status=Status.WARN, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "pass"

    def test_important_changes_status(self):
        """Important findings should change pass to warn."""
        checks = [
            CheckResult(id="META001", title="t", severity=Severity.ERROR, status=Status.PASS, message="m"),
            CheckResult(id="EXP001", title="t", severity=Severity.WARNING, status=Status.FAIL, message="m"),
        ]
        _, status, _ = compute_score(checks)
        assert status == "warn"


class TestContract:
    def test_init_contract(self, tmp_path):
        out = tmp_path / "contract.yml"
        result = run_cli("init", "--contract", "--template", "ml", "--output", str(out))
        assert result.returncode == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "version:" in content
        assert "experiments:" in content

    def test_validate_contract_no_contract(self):
        result = run_cli("validate-contract", BAD)
        # Returns 1 when no contract found (not an error, just informational)
        assert "No reproducibility contract found" in result.stdout or "No reproducibility contract found" in result.stderr

    def test_contract_schema_load(self):
        from oss_paper_ci.contract_schema import ReproducibilityContract
        c = ReproducibilityContract()
        assert c.version == "0.3"
        assert c.project_type == "other"

    def test_contract_parse_yaml(self, tmp_path):
        import yaml
        from oss_paper_ci.contract import load_contract
        contract_data = {
            "version": "0.3",
            "project_name": "test",
            "experiments": [{"id": "smoke", "command": "echo ok", "safe_to_run": True}],
        }
        path = tmp_path / "contract.yml"
        path.write_text(yaml.dump(contract_data), encoding="utf-8")
        contract = load_contract(str(path))
        assert contract.project_name == "test"
        assert len(contract.experiments) == 1


class TestGraph:
    def test_graph_json_output(self):
        result = run_cli("graph", RML, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) > 0

    def test_graph_has_edges(self):
        result = run_cli("graph", RML, "--format", "json")
        data = json.loads(result.stdout)
        assert len(data["edges"]) > 0, "Graph should have edges"

    def test_graph_node_types(self):
        result = run_cli("graph", RML, "--format", "json")
        data = json.loads(result.stdout)
        types = {n["type"] for n in data["nodes"]}
        assert "script" in types or "readme" in types

    def test_graph_markdown_output(self):
        result = run_cli("graph", RML, "--format", "markdown")
        assert result.returncode == 0
        assert "Evidence Graph" in result.stdout or "nodes" in result.stdout.lower()

    def test_graph_write_to_file(self, tmp_path):
        out = tmp_path / "graph.json"
        result = run_cli("graph", RML, "--format", "json", "--output", str(out))
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "nodes" in data


class TestBaseline:
    def test_baseline_create(self, tmp_path):
        out = tmp_path / "baseline.json"
        result = run_cli("baseline", "create", RML, "--output", str(out))
        assert result.returncode == 0
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "score" in data
        assert "status" in data

    def test_baseline_compare_no_regression(self, tmp_path):
        baseline = tmp_path / "baseline.json"
        run_cli("baseline", "create", RML, "--output", str(baseline))
        result = run_cli("baseline", "compare", RML, "--baseline", str(baseline), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["score_delta"] == 0
        assert len(data["regressions"]) == 0

    def test_baseline_compare_with_regression(self, tmp_path):
        baseline = tmp_path / "baseline.json"
        run_cli("baseline", "create", GOOD, "--output", str(baseline))
        result = run_cli("baseline", "compare", BAD, "--baseline", str(baseline), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["score_delta"] < 0


class TestSmokeRunner:
    def test_smoke_dry_run(self):
        result = run_cli("smoke", RML, "--dry-run")
        assert result.returncode == 0
        assert "Command:" in result.stdout

    def test_smoke_with_explicit_command(self):
        result = run_cli("smoke", RML, "--command", "echo hello", "--timeout", "10")
        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_smoke_timeout(self):
        result = run_cli("smoke", RML, "--command", "python -c \"import time; time.sleep(10)\"", "--timeout", "2")
        assert result.returncode != 0 or "timed out" in result.stdout.lower() or "timeout" in result.stdout.lower()

    def test_dangerous_command_blocked(self):
        result = run_cli("smoke", RML, "--command", "rm -rf /")
        assert result.returncode != 0
        assert "dangerous" in result.stdout.lower() or "blocked" in result.stdout.lower() or "error" in result.stdout.lower()


class TestSarifLocations:
    def test_sarif_has_physical_location(self):
        from oss_paper_ci.reporting.sarif_report import generate_sarif_report
        from oss_paper_ci.scanner import scan
        # Use broken_paper_repo which has file references in evidence
        report = scan(str(FIXTURES / "broken_paper_repo"))
        sarif = json.loads(generate_sarif_report(report))
        results = sarif["runs"][0]["results"]
        # At least one result should have a physicalLocation or relatedLocations
        has_location = any(
            "locations" in r or "relatedLocations" in r
            for r in results
        )
        assert has_location, "SARIF should have at least one location"

    def test_sarif_excludes_pass_by_default(self):
        from oss_paper_ci.reporting.sarif_report import generate_sarif_report
        from oss_paper_ci.scanner import scan
        report = scan(GOOD)
        sarif = json.loads(generate_sarif_report(report))
        results = sarif["runs"][0]["results"]
        # Should not have pass results
        pass_results = [r for r in results if r.get("level") == "none"]
        assert len(pass_results) == 0, "SARIF should exclude pass results by default"

    def test_sarif_rules_have_category(self):
        from oss_paper_ci.reporting.sarif_report import generate_sarif_report
        from oss_paper_ci.scanner import scan
        report = scan(GOOD)
        sarif = json.loads(generate_sarif_report(report))
        rules = sarif["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) > 0
        for rule in rules:
            assert "properties" in rule
            assert "category" in rule["properties"]


class TestMultilanguage:
    def test_r_detection(self, tmp_path):
        (tmp_path / "DESCRIPTION").write_text("Package: test\n", encoding="utf-8")
        (tmp_path / "analysis.R").write_text("x <- 1\n", encoding="utf-8")
        from oss_paper_ci.scanner import _detect_languages
        langs = _detect_languages(str(tmp_path), type('C', (), {'ignore': type('I', (), {'paths': []})()})())
        assert "R" in langs

    def test_julia_detection(self, tmp_path):
        (tmp_path / "Project.toml").write_text("[deps]\n", encoding="utf-8")
        (tmp_path / "main.jl").write_text("println(\"hello\")\n", encoding="utf-8")
        from oss_paper_ci.scanner import _detect_languages
        langs = _detect_languages(str(tmp_path), type('C', (), {'ignore': type('I', (), {'paths': []})()})())
        assert "Julia" in langs


class TestActionMetadata:
    def test_action_yml_exists(self):
        assert Path("action.yml").exists()

    def test_action_yml_valid(self):
        import yaml
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["name"] == "oss-paper-ci"
        assert "inputs" in data
        assert "runs" in data

    def test_action_has_required_inputs(self):
        import yaml
        with open("action.yml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        inputs = data.get("inputs", {})
        assert "path" in inputs
        assert "format" in inputs
        assert "fail-under" in inputs
