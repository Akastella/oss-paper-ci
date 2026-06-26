"""Tests that evidence can include DSL summary."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.dag import build_dag
from oss_paper_ci.repro_dsl.safety import check_dsl_safety
from oss_paper_ci.repro_dsl.normalizer import normalize_dsl


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestEvidenceIncludesDslSummary:
    def test_dsl_provides_project_metadata(self):
        """DSL project metadata can be included in evidence reports."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        assert dsl.project.name
        assert dsl.project.description

    def test_dag_summary_for_evidence(self):
        """DAG summary can be included in evidence bundles."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        dag = build_dag(dsl)
        dag_dict = dag.to_dict()
        assert "topological_order" in dag_dict
        assert "critical_path" in dag_dict
        assert "parallel_groups" in dag_dict

    def test_safety_summary_for_evidence(self):
        """Safety report can be included in evidence bundles."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        report_dict = report.to_dict()
        assert "safety_level" in report_dict
        assert "findings" in report_dict

    def test_normalized_dsl_for_evidence(self):
        """Normalized DSL can be stored in evidence bundles."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        normalized = normalize_dsl(dsl)
        assert isinstance(normalized, dict)
        assert normalized["version"] == 1

    def test_step_count_for_evidence(self):
        """Step count can be reported in evidence."""
        dsl = load_dsl(FIXTURES / "valid_multistep_pipeline" / "reproducibility.yml")
        assert len(dsl.steps) == 4

    def test_artifact_list_for_evidence(self):
        """Artifact list can be included in evidence."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        artifact_paths = [a.path for a in dsl.artifacts]
        assert len(artifact_paths) > 0

    def test_expected_metrics_for_evidence(self):
        """Expected metrics can be included in evidence for comparison."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        expected = dsl.expected.to_dict()
        if expected:
            assert "metrics" in expected

    def test_dag_hash_for_evidence_identity(self):
        """DAG hash uniquely identifies the pipeline structure for evidence."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        h = dsl.dag_hash()
        assert isinstance(h, str)
        assert len(h) == 16
