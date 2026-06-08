"""Tests for deep graph analysis."""

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
RML = str(FIXTURES / "realistic_ml_repo")
GOOD = str(FIXTURES / "paper_ready_repo")


class TestGraphStructure:
    """Test graph node and edge structure."""

    def test_graph_has_script_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        script_nodes = [n for n in g.nodes if n.type == "script"]
        assert len(script_nodes) > 0

    def test_graph_has_config_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        config_nodes = [n for n in g.nodes if n.type == "config"]
        assert len(config_nodes) > 0

    def test_graph_has_readme_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        readme_nodes = [n for n in g.nodes if n.type == "readme"]
        assert len(readme_nodes) > 0

    def test_graph_has_edges(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        assert len(g.edges) > 0

    def test_graph_edge_types(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        relations = {e.relation for e in g.edges}
        assert len(relations) > 0

    def test_graph_has_environment_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        env_nodes = [n for n in g.nodes if n.type == "environment"]
        assert len(env_nodes) > 0

    def test_graph_has_tex_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        tex_nodes = [n for n in g.nodes if n.type == "tex"]
        assert len(tex_nodes) > 0

    def test_graph_has_ci_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        ci_nodes = [n for n in g.nodes if n.type == "ci"]
        assert len(ci_nodes) > 0

    def test_graph_has_notebook_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        notebook_nodes = [n for n in g.nodes if n.type == "notebook"]
        assert len(notebook_nodes) > 0


class TestGraphConnectivity:
    """Test graph edge connectivity."""

    def test_graph_orphan_nodes_exist(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        connected = set()
        for e in g.edges:
            connected.add(e.source)
            connected.add(e.target)
        assert len(connected) > 0

    def test_graph_no_broken_edges(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        broken = g.find_broken_edges()
        assert len(broken) == 0

    def test_graph_tex_references_figures(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        tex_refs = [e for e in g.edges if e.relation == "references"]
        assert len(tex_refs) > 0

    def test_graph_readme_runs_scripts(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        run_edges = [e for e in g.edges if e.relation == "runs"]
        assert len(run_edges) > 0


class TestGraphNodeProperties:
    """Test graph node properties."""

    def test_node_has_id(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        for n in g.nodes:
            assert n.id
            assert isinstance(n.id, str)

    def test_node_has_type(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        valid_types = {
            "paper", "tex", "bib", "readme", "script", "config",
            "environment", "data", "result", "figure", "table",
            "notebook", "ci", "contract", "make_target",
        }
        for n in g.nodes:
            assert n.type in valid_types

    def test_node_has_path(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        # Most nodes have a path; synthetic nodes (e.g. make_target) may have empty path
        nodes_with_path = [n for n in g.nodes if n.path]
        assert len(nodes_with_path) > 0

    def test_node_has_label(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        for n in g.nodes:
            assert n.label

    def test_node_ids_unique(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        ids = [n.id for n in g.nodes]
        assert len(ids) == len(set(ids))


class TestGraphEdgeProperties:
    """Test graph edge properties."""

    def test_edge_has_source(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        for e in g.edges:
            assert e.source

    def test_edge_has_target(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        for e in g.edges:
            assert e.target

    def test_edge_has_relation(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        for e in g.edges:
            assert e.relation

    def test_edge_has_confidence(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        for e in g.edges:
            assert e.confidence in ("explicit", "inferred")


class TestGraphQuery:
    """Test graph query methods."""

    def test_get_node_exists(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        first = g.nodes[0]
        result = g.get_node(first.id)
        assert result is not None
        assert result.id == first.id

    def test_get_node_missing(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        result = g.get_node("nonexistent:node")
        assert result is None

    def test_get_edges_from(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        if g.edges:
            source_id = g.edges[0].source
            edges = g.get_edges_from(source_id)
            assert all(e.source == source_id for e in edges)

    def test_get_edges_to(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        if g.edges:
            target_id = g.edges[0].target
            edges = g.get_edges_to(target_id)
            assert all(e.target == target_id for e in edges)

    def test_find_orphan_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        orphans = g.find_orphan_nodes()
        # Orphans should not appear in any edge
        connected = set()
        for e in g.edges:
            connected.add(e.source)
            connected.add(e.target)
        for o in orphans:
            assert o.id not in connected


class TestGraphSerialization:
    """Test graph serialization."""

    def test_to_dict_has_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        d = g.to_dict()
        assert "nodes" in d
        assert isinstance(d["nodes"], list)

    def test_to_dict_has_edges(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        d = g.to_dict()
        assert "edges" in d
        assert isinstance(d["edges"], list)

    def test_node_to_dict(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        node = g.nodes[0]
        d = node.to_dict()
        assert "id" in d
        assert "type" in d
        assert "path" in d

    def test_edge_to_dict(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(RML)
        edge = g.edges[0]
        d = edge.to_dict()
        assert "source" in d
        assert "target" in d
        assert "relation" in d


class TestGraphPaperReadyRepo:
    """Test graph on the paper_ready_repo fixture."""

    def test_paper_ready_has_nodes(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(GOOD)
        assert len(g.nodes) > 0

    def test_paper_ready_has_edges(self):
        from oss_paper_ci.graph import build_evidence_graph
        g = build_evidence_graph(GOOD)
        assert len(g.edges) > 0
