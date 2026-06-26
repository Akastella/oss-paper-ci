"""Tests that examples/dsl/reproducibility.v1.yml loads and validates."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.validator import validate_dsl
from oss_paper_ci.repro_dsl.dag import build_dag
from oss_paper_ci.repro_dsl.safety import check_dsl_safety
from oss_paper_ci.repro_dsl.normalizer import normalize_dsl_json
import json


EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "dsl"


@pytest.fixture
def example_dsl():
    path = EXAMPLES_DIR / "reproducibility.v1.yml"
    if not path.exists():
        pytest.skip("Example DSL file not found")
    return load_dsl(path)


class TestExampleDslLoads:
    def test_loads_without_error(self, example_dsl):
        assert example_dsl is not None

    def test_is_v1(self, example_dsl):
        assert example_dsl.version == 1

    def test_has_project_name(self, example_dsl):
        assert example_dsl.project.name
        assert example_dsl.project.name != "unnamed"

    def test_has_steps(self, example_dsl):
        assert len(example_dsl.steps) > 0

    def test_has_safety(self, example_dsl):
        assert example_dsl.safety is not None


class TestExampleDslValidates:
    def test_is_valid(self, example_dsl):
        result = validate_dsl(example_dsl)
        assert result.is_valid is True

    def test_no_errors(self, example_dsl):
        result = validate_dsl(example_dsl)
        assert len(result.errors) == 0


class TestExampleDslDag:
    def test_dag_is_valid(self, example_dsl):
        dag = build_dag(example_dsl)
        assert dag.is_valid is True

    def test_no_cycles(self, example_dsl):
        dag = build_dag(example_dsl)
        assert len(dag.cycles) == 0

    def test_no_missing_deps(self, example_dsl):
        dag = build_dag(example_dsl)
        assert len(dag.missing_deps) == 0

    def test_has_critical_path(self, example_dsl):
        dag = build_dag(example_dsl)
        assert len(dag.critical_path) > 0

    def test_has_parallel_groups(self, example_dsl):
        dag = build_dag(example_dsl)
        assert len(dag.parallel_groups) > 0


class TestExampleDslSafety:
    def test_safety_report_generated(self, example_dsl):
        report = check_dsl_safety(example_dsl)
        assert report is not None

    def test_no_blocked_commands(self, example_dsl):
        report = check_dsl_safety(example_dsl)
        assert report.has_blocks is False


class TestExampleDslNormalization:
    def test_normalizes_to_valid_json(self, example_dsl):
        j = normalize_dsl_json(example_dsl)
        parsed = json.loads(j)
        assert parsed["version"] == 1

    def test_deterministic(self, example_dsl):
        j1 = normalize_dsl_json(example_dsl)
        j2 = normalize_dsl_json(example_dsl)
        assert j1 == j2
