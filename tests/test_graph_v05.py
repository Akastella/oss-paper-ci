"""Tests for graph v0.5 features: DOT output, orphans, markdown formatting."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
RML = str(FIXTURES / "realistic_ml_repo")
GOOD = str(FIXTURES / "paper_ready_repo")


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
        errors="replace",
    )


class TestGraphDot:
    """Test DOT output format for the evidence graph."""

    def test_dot_output_format(self):
        result = run_cli("graph", RML, "--format", "dot")
        assert result.returncode == 0
        assert "digraph" in result.stdout

    def test_dot_has_nodes(self):
        result = run_cli("graph", RML, "--format", "dot")
        assert result.returncode == 0
        assert "->" in result.stdout or "node" in result.stdout.lower()

    def test_dot_has_edges(self):
        result = run_cli("graph", RML, "--format", "dot")
        assert result.returncode == 0
        assert "->" in result.stdout

    def test_dot_write_to_file(self, tmp_path):
        out = tmp_path / "graph.dot"
        result = run_cli("graph", RML, "--format", "dot", "--output", str(out))
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "digraph" in content


class TestGraphOrphans:
    """Test orphan node display in graph output."""

    def test_show_orphans(self):
        result = run_cli("graph", RML, "--show-orphans")
        assert result.returncode == 0

    def test_show_orphans_json(self):
        result = run_cli("graph", RML, "--show-orphans", "--format", "json")
        assert result.returncode == 0
        # Output may have orphan report before JSON
        # Find the JSON part
        stdout = result.stdout
        json_start = stdout.find("{")
        if json_start >= 0:
            data = json.loads(stdout[json_start:])
            assert "nodes" in data

    def test_show_conflicts(self):
        result = run_cli("graph", RML, "--show-conflicts")
        assert result.returncode == 0


class TestGraphNodeTypes:
    """Test graph node type diversity."""

    def test_graph_has_multiple_node_types(self):
        result = run_cli("graph", RML, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        types = {n["type"] for n in data["nodes"]}
        assert len(types) >= 3

    def test_graph_nodes_have_required_fields(self):
        result = run_cli("graph", RML, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        for node in data["nodes"]:
            assert "id" in node
            assert "type" in node

    def test_graph_edges_have_required_fields(self):
        result = run_cli("graph", RML, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        for edge in data["edges"]:
            assert "source" in edge
            assert "target" in edge
            assert "relation" in edge


class TestGraphPaperReadyRepo:
    """Test graph on the paper_ready_repo fixture via CLI."""

    def test_paper_ready_graph_json(self):
        result = run_cli("graph", GOOD, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["nodes"]) > 0

    def test_paper_ready_graph_has_edges(self):
        result = run_cli("graph", GOOD, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["edges"]) > 0

    def test_paper_ready_graph_markdown(self):
        result = run_cli("graph", GOOD, "--format", "markdown")
        assert result.returncode == 0
        assert "Evidence Graph" in result.stdout or "nodes" in result.stdout.lower()


class TestGraphInternal:
    """Test graph builder internals directly."""

    def test_build_evidence_graph(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        assert len(g.nodes) > 0

    def test_graph_find_orphan_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        orphans = g.find_orphan_nodes()
        # Orphans should be a valid list (may be empty)
        assert isinstance(orphans, list)

    def test_graph_find_broken_edges(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        broken = g.find_broken_edges()
        assert isinstance(broken, list)
        assert len(broken) == 0

    def test_graph_to_dict_roundtrip(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        d = g.to_dict()
        text = json.dumps(d)
        parsed = json.loads(text)
        assert len(parsed["nodes"]) == len(g.nodes)
        assert len(parsed["edges"]) == len(g.edges)
