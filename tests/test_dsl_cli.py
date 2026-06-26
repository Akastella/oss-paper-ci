"""Tests for DSL CLI commands via subprocess (dsl validate/normalize/graph/plan/explain/migrate)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import pytest


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


def _run_dsl_cmd(subcommand: str, path: Path, *args: str) -> subprocess.CompletedProcess:
    """Run oss-paper-ci dsl <subcommand> <path> via subprocess."""
    cmd = [
        sys.executable, "-m", "oss_paper_ci",
        "dsl", subcommand, str(path),
        *args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


class TestDslValidate:
    def test_valid_pipeline_returns_zero(self):
        result = _run_dsl_cmd("validate", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert result.returncode == 0

    def test_valid_pipeline_has_output(self):
        result = _run_dsl_cmd("validate", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert len(result.stdout) > 0
        assert "Validation" in result.stdout or "PASS" in result.stdout

    def test_missing_dependency_returns_nonzero(self):
        result = _run_dsl_cmd("validate", FIXTURES / "missing_dependency" / "reproducibility.yml")
        assert result.returncode != 0

    def test_validate_json_format(self):
        result = _run_dsl_cmd("validate", FIXTURES / "valid_python_pipeline" / "reproducibility.yml", "--format", "json")
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert "is_valid" in parsed

    def test_validate_invalid_schema_returns_nonzero(self):
        result = _run_dsl_cmd("validate", FIXTURES / "invalid_schema" / "reproducibility.yml")
        # Should either return nonzero or print an error
        assert result.returncode != 0 or "error" in result.stderr.lower()


class TestDslNormalize:
    def test_normalize_returns_json(self):
        result = _run_dsl_cmd("normalize", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["version"] == 1

    def test_normalize_deterministic(self):
        r1 = _run_dsl_cmd("normalize", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        r2 = _run_dsl_cmd("normalize", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert r1.stdout == r2.stdout

    def test_normalize_legacy(self):
        result = _run_dsl_cmd("normalize", FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["version"] == 1


class TestDslGraph:
    def test_graph_returns_dot(self):
        result = _run_dsl_cmd("graph", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert result.returncode == 0
        assert "digraph" in result.stdout

    def test_graph_contains_nodes(self):
        result = _run_dsl_cmd("graph", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert "train" in result.stdout
        assert "evaluate" in result.stdout

    def test_graph_contains_edges(self):
        result = _run_dsl_cmd("graph", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert "->" in result.stdout


class TestDslPlan:
    def test_plan_returns_markdown(self):
        result = _run_dsl_cmd("plan", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert result.returncode == 0
        assert "Execution Plan" in result.stdout or "Executable" in result.stdout

    def test_plan_json_format(self):
        result = _run_dsl_cmd("plan", FIXTURES / "valid_python_pipeline" / "reproducibility.yml", "--format", "json")
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert "steps" in parsed

    def test_plan_unsafe_returns_nonzero(self):
        result = _run_dsl_cmd("plan", FIXTURES / "unsafe_command" / "reproducibility.yml")
        # Should return nonzero because safety block
        assert result.returncode != 0


class TestDslExplain:
    def test_explain_returns_markdown(self):
        result = _run_dsl_cmd("explain", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert result.returncode == 0
        assert len(result.stdout) > 0

    def test_explain_json_format(self):
        result = _run_dsl_cmd("explain", FIXTURES / "valid_python_pipeline" / "reproducibility.yml", "--format", "json")
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert "steps" in parsed


class TestDslMigrate:
    def test_migrate_legacy(self):
        result = _run_dsl_cmd("migrate", FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["version"] == 1

    def test_migrate_v1_already(self):
        result = _run_dsl_cmd("migrate", FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        # Should indicate already v1
        assert result.returncode == 0
        assert "v1" in result.stderr.lower() or "already" in result.stderr.lower()

    def test_migrate_markdown_format(self):
        result = _run_dsl_cmd(
            "migrate",
            FIXTURES / "legacy_config_v0" / "reproducibility.yml",
            "--format", "markdown",
        )
        assert result.returncode == 0
        assert "Migration" in result.stdout


class TestDslCliOutput:
    def test_validate_output_to_file(self, tmp_path):
        out_file = tmp_path / "report.md"
        result = _run_dsl_cmd(
            "validate",
            FIXTURES / "valid_python_pipeline" / "reproducibility.yml",
            "--output", str(out_file),
        )
        assert result.returncode == 0
        assert out_file.exists()
        content = out_file.read_text()
        assert len(content) > 0
