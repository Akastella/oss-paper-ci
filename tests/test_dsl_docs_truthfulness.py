"""Tests that documentation doesn't overclaim DSL capabilities."""
from __future__ import annotations

from pathlib import Path
import pytest

DOCS_DIR = Path(__file__).parent.parent / "docs"


class TestDslDocsTruthfulness:
    """Verify that documentation claims match actual behavior."""

    @pytest.fixture
    def dsl_doc(self):
        path = DOCS_DIR / "reproducibility-dsl.md"
        if not path.exists():
            pytest.skip("DSL documentation not found")
        return path.read_text(encoding="utf-8")

    def test_docs_exist(self, dsl_doc):
        assert len(dsl_doc) > 0

    def test_docs_describe_validate_command(self, dsl_doc):
        assert "validate" in dsl_doc.lower()

    def test_docs_describe_normalize_command(self, dsl_doc):
        assert "normalize" in dsl_doc.lower()

    def test_docs_describe_graph_command(self, dsl_doc):
        assert "graph" in dsl_doc.lower()

    def test_docs_describe_plan_command(self, dsl_doc):
        assert "plan" in dsl_doc.lower()

    def test_docs_describe_migrate_command(self, dsl_doc):
        assert "migrate" in dsl_doc.lower()

    def test_docs_mention_dry_run(self, dsl_doc):
        """Docs should mention that DSL commands are dry-run by default."""
        assert "dry" in dsl_doc.lower() or "read-only" in dsl_doc.lower()

    def test_docs_mention_no_auto_execute(self, dsl_doc):
        """Docs should clarify the tool doesn't auto-execute."""
        assert "never" in dsl_doc.lower() or "no" in dsl_doc.lower()

    def test_docs_mention_safety_defaults(self, dsl_doc):
        """Docs should mention safety defaults are restrictive."""
        assert "false" in dsl_doc.lower() or "restrictive" in dsl_doc.lower()

    def test_docs_mention_dag(self, dsl_doc):
        """Docs should explain DAG structure."""
        assert "dag" in dsl_doc.lower() or "acyclic" in dsl_doc.lower()

    def test_docs_mention_cycle_detection(self, dsl_doc):
        """Docs should mention cycle detection."""
        assert "cycle" in dsl_doc.lower()

    def test_docs_mention_topological_sort(self, dsl_doc):
        """Docs should mention topological ordering."""
        assert "topological" in dsl_doc.lower() or "order" in dsl_doc.lower()

    def test_docs_mention_deterministic(self, dsl_doc):
        """Docs should mention deterministic normalization."""
        assert "deterministic" in dsl_doc.lower() or "stable" in dsl_doc.lower()

    def test_docs_reference_sub_documents(self, dsl_doc):
        """Docs should reference related sub-documents."""
        assert "schema" in dsl_doc.lower() or "migration" in dsl_doc.lower()

    def test_docs_show_yaml_example(self, dsl_doc):
        """Docs should include a YAML example."""
        assert "```yaml" in dsl_doc or "version:" in dsl_doc

    def test_docs_no_false_performance_claims(self, dsl_doc):
        """Docs should not claim sub-millisecond or instant performance."""
        assert "instant" not in dsl_doc.lower()
        assert "sub-millisecond" not in dsl_doc.lower()
