"""Tests for repro_dsl.report -- all format_* functions with valid and edge-case data."""
from __future__ import annotations

import json
import re
from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.dag import build_dag
from oss_paper_ci.repro_dsl.planner import plan_execution
from oss_paper_ci.repro_dsl.safety import check_dsl_safety, SafetyReport, SafetyFinding
from oss_paper_ci.repro_dsl.migration import MigrationReport
from oss_paper_ci.repro_dsl.validator import validate_dsl, ValidationResult, ValidationFinding
from oss_paper_ci.repro_dsl.schema import ReproDSL, ProjectSpec, StepSpec, SafetySpec
from oss_paper_ci.repro_dsl.report import (
    format_validation_report,
    format_plan_report,
    format_dag_dot,
    format_dag_html,
    format_normalized_json,
    format_migration_report,
    format_safety_report,
)


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestFormatValidationReport:
    def test_markdown_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = validate_dsl(dsl)
        report = format_validation_report(result, "markdown")
        assert "Validation" in report
        assert "PASS" in report or "FAIL" in report

    def test_json_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        result = validate_dsl(dsl)
        report = format_validation_report(result, "json")
        parsed = json.loads(report)
        assert "is_valid" in parsed

    def test_with_findings(self):
        dsl = load_dsl(FIXTURES / "missing_dependency" / "reproducibility.yml")
        result = validate_dsl(dsl)
        report = format_validation_report(result, "markdown")
        assert "FAIL" in report
        assert "Findings" in report

    def test_empty_findings(self):
        result = ValidationResult(findings=[], is_valid=True, checked_fields=5)
        report = format_validation_report(result, "markdown")
        assert "No findings" in report


class TestFormatPlanReport:
    def test_markdown_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        report = format_plan_report(plan, "markdown")
        assert "Execution Plan" in report
        assert "Executable" in report

    def test_json_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        report = format_plan_report(plan, "json")
        parsed = json.loads(report)
        assert "steps" in parsed

    def test_contains_step_table(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        report = format_plan_report(plan, "markdown")
        assert "train" in report
        assert "evaluate" in report

    def test_contains_safety_section(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        plan = plan_execution(dsl)
        report = format_plan_report(plan, "markdown")
        assert "Safety" in report

    def test_with_blocked_steps(self):
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        plan = plan_execution(dsl)
        report = format_plan_report(plan, "markdown")
        assert "blocked" in report.lower()


class TestFormatDagDot:
    def test_dot_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        dot = format_dag_dot(dag)
        assert "digraph" in dot
        assert "}" in dot

    def test_contains_nodes(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        dot = format_dag_dot(dag)
        assert "train" in dot
        assert "evaluate" in dot

    def test_contains_edges(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        dot = format_dag_dot(dag)
        assert "->" in dot

    def test_deterministic(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        dot1 = format_dag_dot(dag)
        dot2 = format_dag_dot(dag)
        assert dot1 == dot2

    def test_with_cycles(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        dot = format_dag_dot(dag)
        assert "digraph" in dot


class TestFormatDagHtml:
    def test_html_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        html = format_dag_html(dag)
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

    def test_no_external_cdn(self):
        """HTML must be self-contained with no external CDN references."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        html = format_dag_html(dag)
        assert "cdn" not in html.lower()
        assert "googleapis" not in html.lower()
        assert "cloudflare" not in html.lower()
        assert "jsdelivr" not in html.lower()
        assert "unpkg" not in html.lower()

    def test_no_absolute_paths(self):
        """HTML must not contain absolute file paths."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        html = format_dag_html(dag)
        # Check for common absolute path patterns (but not URLs)
        assert "C:\\" not in html
        assert "C:/" not in html

    def test_contains_css_inline(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        html = format_dag_html(dag)
        assert "<style>" in html

    def test_custom_title(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        html = format_dag_html(dag, title="My Custom Title")
        assert "My Custom Title" in html

    def test_contains_summary_cards(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        html = format_dag_html(dag)
        assert "summary-card" in html

    def test_with_cycles_shows_warnings(self):
        dsl = load_dsl(FIXTURES / "cyclic_dependency" / "reproducibility.yml")
        dag = build_dag(dsl)
        html = format_dag_html(dag)
        assert "Warnings" in html or "Cycle" in html

    def test_html_escapes_user_content(self):
        """User content should be HTML-escaped."""
        dsl = ReproDSL(
            project=ProjectSpec(name="<script>alert('xss')</script>"),
            steps={"s1": StepSpec(id="s1", command="echo <b>bold</b>")},
            safety=SafetySpec(),
        )
        dag = build_dag(dsl)
        html = format_dag_html(dag)
        # The literal script tag should be escaped
        assert "<script>alert" not in html


class TestFormatNormalizedJson:
    def test_json_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        json_str = format_normalized_json(dsl)
        parsed = json.loads(json_str)
        assert parsed["version"] == 1

    def test_deterministic(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        j1 = format_normalized_json(dsl)
        j2 = format_normalized_json(dsl)
        assert j1 == j2

    def test_ends_with_newline(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert format_normalized_json(dsl).endswith("\n")


class TestFormatMigrationReport:
    def test_markdown_format(self):
        report = MigrationReport(source_version="v0.3", steps_converted=2, datasets_converted=1)
        md = format_migration_report(report, "markdown")
        assert "Migration" in md
        assert "v0.3" in md

    def test_json_format(self):
        report = MigrationReport(source_version="v0.3")
        j = format_migration_report(report, "json")
        parsed = json.loads(j)
        assert parsed["source_version"] == "v0.3"

    def test_with_warnings(self):
        report = MigrationReport(source_version="v0.3", warnings=["test warning"])
        md = format_migration_report(report, "markdown")
        assert "test warning" in md

    def test_empty_warnings(self):
        report = MigrationReport(source_version="v0.3")
        md = format_migration_report(report, "markdown")
        assert "Warnings" not in md


class TestFormatSafetyReport:
    def test_markdown_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        md = format_safety_report(report, "markdown")
        assert "Safety" in md

    def test_json_format(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        j = format_safety_report(report, "json")
        parsed = json.loads(j)
        assert "safety_level" in parsed

    def test_with_blocked_commands(self):
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        md = format_safety_report(report, "markdown")
        assert "Blocked" in md

    def test_with_findings(self):
        dsl = load_dsl(FIXTURES / "undeclared_network" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        md = format_safety_report(report, "markdown")
        assert "Findings" in md
