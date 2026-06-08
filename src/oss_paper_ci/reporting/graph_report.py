"""Evidence graph report generation for oss-paper-ci.

Provides JSON, Markdown, and DOT report formats that answer key questions
about the relationships between paper artifacts, code, data, and results.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oss_paper_ci.graph import EvidenceGraph, GraphEdge, GraphNode


# ---------------------------------------------------------------------------
# JSON report
# ---------------------------------------------------------------------------

def generate_graph_json(
    graph: EvidenceGraph,
    output_path: str | None = None,
) -> str:
    """Serialize the evidence graph to JSON.

    Args:
        graph: The evidence graph.
        output_path: If provided, write to this file.

    Returns:
        JSON string.
    """
    data = graph.to_dict()

    # Add summary analytics
    data["summary"] = _build_summary(graph)

    text = json.dumps(data, indent=2, ensure_ascii=False)
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# DOT (Graphviz) report
# ---------------------------------------------------------------------------

def generate_graph_dot(
    graph: EvidenceGraph,
    output_path: str | None = None,
) -> str:
    """Generate a Graphviz DOT representation of the evidence graph.

    Args:
        graph: The evidence graph.
        output_path: If provided, write to this file.

    Returns:
        DOT string.
    """
    from oss_paper_ci.graph import generate_dot

    text = generate_dot(graph)
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def generate_graph_markdown(
    graph: EvidenceGraph,
    output_path: str | None = None,
) -> str:
    """Generate a Markdown report that answers key evidence-graph questions.

    Args:
        graph: The evidence graph.
        output_path: If provided, write to this file.

    Returns:
        Markdown string.
    """
    lines: list[str] = []

    lines.append("# Evidence Graph Report")
    lines.append("")

    # -- Overview -----------------------------------------------------------
    summary = _build_summary(graph)
    lines.append("## Overview")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total nodes | {summary['total_nodes']} |")
    lines.append(f"| Total edges | {summary['total_edges']} |")
    lines.append(f"| Orphan nodes | {summary['orphan_nodes']} |")
    lines.append(f"| Broken edges | {summary['broken_edges']} |")
    lines.append("")

    # -- Node type breakdown -----------------------------------------------
    lines.append("### Node types")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for ntype, count in sorted(summary.get("node_types", {}).items()):
        lines.append(f"| {ntype} | {count} |")
    lines.append("")

    # -- Edge relation breakdown --------------------------------------------
    lines.append("### Edge relations")
    lines.append("")
    lines.append("| Relation | Count |")
    lines.append("|----------|-------|")
    for rel, count in sorted(summary.get("edge_relations", {}).items()):
        lines.append(f"| {rel} | {count} |")
    lines.append("")

    # -- Edge confidence breakdown -----------------------------------------
    conf = summary.get("edge_confidence", {})
    if conf:
        lines.append("### Edge confidence")
        lines.append("")
        lines.append("| Confidence | Count |")
        lines.append("|------------|-------|")
        for c, count in sorted(conf.items()):
            lines.append(f"| {c} | {count} |")
        lines.append("")

    # -- Coverage ----------------------------------------------------------
    coverage = summary.get("coverage", {})
    if coverage:
        lines.append("### Coverage")
        lines.append("")
        lines.append("| Artifact type | With generation path |")
        lines.append("|---------------|---------------------|")
        lines.append(f"| Paper artifacts | {coverage.get('paper_artifacts_with_generation_path', 0)} |")
        lines.append(f"| Results | {coverage.get('results_with_generation_path', 0)} |")
        lines.append(f"| Figures | {coverage.get('figures_with_generation_path', 0)} |")
        lines.append("")

    # -- Q1: Which paper artifacts have code links? -------------------------
    lines.append("## 1. Paper artifacts with code links")
    lines.append("")
    _section_paper_code_links(graph, lines)

    # -- Q2: Which results have generation scripts? -------------------------
    lines.append("## 2. Results with generation scripts")
    lines.append("")
    _section_results_with_scripts(graph, lines)

    # -- Q3: Which scripts depend on undeclared environment? ----------------
    lines.append("## 3. Scripts with undeclared environment dependencies")
    lines.append("")
    _section_undeclared_env(graph, lines)

    # -- Q4: Which data is referenced but has no availability? --------------
    lines.append("## 4. Referenced data without availability")
    lines.append("")
    _section_data_no_availability(graph, lines)

    # -- Q5: Which figures/tables are orphan? -------------------------------
    lines.append("## 5. Orphan figures and tables")
    lines.append("")
    _section_orphan_figures(graph, lines)

    # -- Q6: Which expected outputs are missing? ----------------------------
    lines.append("## 6. Expected outputs that are missing")
    lines.append("")
    _section_missing_outputs(graph, lines)

    # -- Node listing -------------------------------------------------------
    lines.append("## Full node listing")
    lines.append("")
    lines.append("| ID | Type | Path | Exists |")
    lines.append("|----|------|------|--------|")
    for n in sorted(graph.nodes, key=lambda n: (n.type, n.path)):
        exists_mark = "yes" if n.exists else "**no**"
        lines.append(f"| `{n.id}` | {n.type} | `{n.path}` | {exists_mark} |")
    lines.append("")

    # -- Edge listing -------------------------------------------------------
    lines.append("## Full edge listing")
    lines.append("")
    lines.append("| Source | Relation | Target | Confidence | Evidence |")
    lines.append("|--------|----------|--------|------------|----------|")
    for e in graph.edges:
        evidence_short = e.evidence[:60] + "..." if len(e.evidence) > 60 else e.evidence
        lines.append(f"| `{e.source}` | {e.relation} | `{e.target}` | {e.confidence} | {evidence_short} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated by oss-paper-ci evidence graph*")

    text = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def _build_summary(graph: EvidenceGraph) -> dict:
    """Build summary statistics for the graph."""
    node_types: dict[str, int] = {}
    for n in graph.nodes:
        node_types[n.type] = node_types.get(n.type, 0) + 1

    edge_relations: dict[str, int] = {}
    edge_confidence: dict[str, int] = {}
    for e in graph.edges:
        edge_relations[e.relation] = edge_relations.get(e.relation, 0) + 1
        edge_confidence[e.confidence] = edge_confidence.get(e.confidence, 0) + 1

    orphans = graph.find_orphan_nodes()
    broken = graph.find_broken_edges()

    # Coverage metrics
    fig_with_gen = sum(
        1 for n in graph.nodes
        if n.type == "figure" and any(e.relation == "generates" for e in graph.get_edges_to(n.id))
    )
    res_with_gen = sum(
        1 for n in graph.nodes
        if n.type == "result" and any(e.relation == "generates" for e in graph.get_edges_to(n.id))
    )
    paper_with_gen = sum(
        1 for n in graph.nodes
        if n.type == "tex" and any(
            e.relation in ("references", "generates")
            for e in graph.get_edges_from(n.id)
            if graph.get_node(e.target) and graph.get_node(e.target).type == "script"
        )
    )

    return {
        "total_nodes": len(graph.nodes),
        "total_edges": len(graph.edges),
        "orphan_nodes": len(orphans),
        "broken_edges": len(broken),
        "node_types": node_types,
        "edge_relations": edge_relations,
        "edge_confidence": edge_confidence,
        "coverage": {
            "paper_artifacts_with_generation_path": paper_with_gen,
            "results_with_generation_path": res_with_gen,
            "figures_with_generation_path": fig_with_gen,
        },
    }


# ---------------------------------------------------------------------------
# Section helpers -- each answers one question
# ---------------------------------------------------------------------------

def _section_paper_code_links(graph: EvidenceGraph, lines: list[str]) -> None:
    """Q1: Which paper/tex artifacts have links to code (scripts)?"""
    tex_nodes = [n for n in graph.nodes if n.type == "tex"]
    if not tex_nodes:
        lines.append("No LaTeX paper files found.")
        lines.append("")
        return

    linked: list[tuple[str, list[str]]] = []
    unlinked: list[str] = []

    for tex in tex_nodes:
        script_targets = []
        for e in graph.get_edges_from(tex.id):
            target = graph.get_node(e.target)
            if target and target.type == "script":
                script_targets.append(target.path)
        if script_targets:
            linked.append((tex.path, script_targets))
        else:
            unlinked.append(tex.path)

    if linked:
        for tex_path, scripts in linked:
            lines.append(f"- **{tex_path}** links to: {', '.join(f'`{s}`' for s in scripts)}")
    if unlinked:
        lines.append("")
        lines.append("**Papers without code links:**")
        for p in unlinked:
            lines.append(f"- `{p}`")
    if not linked and not unlinked:
        lines.append("No paper-code links detected.")
    lines.append("")


def _section_results_with_scripts(graph: EvidenceGraph, lines: list[str]) -> None:
    """Q2: Which results/figures have generation scripts?"""
    result_fig_nodes = [n for n in graph.nodes if n.type in ("figure", "result", "table")]
    if not result_fig_nodes:
        lines.append("No figure or result nodes found.")
        lines.append("")
        return

    generated: list[tuple[str, list[str]]] = []
    orphaned: list[str] = []

    for rf in result_fig_nodes:
        gen_scripts = []
        for e in graph.get_edges_to(rf.id):
            source = graph.get_node(e.source)
            if source and source.type == "script" and e.relation == "generates":
                gen_scripts.append(source.path)
        if gen_scripts:
            generated.append((rf.path, gen_scripts))
        else:
            orphaned.append(rf.path)

    if generated:
        lines.append("**Generated results/figures:**")
        for rf_path, scripts in generated:
            lines.append(f"- `{rf_path}` -- generated by: {', '.join(f'`{s}`' for s in scripts)}")
    if orphaned:
        lines.append("")
        lines.append("**Results/figures without a known generation script:**")
        for p in orphaned:
            lines.append(f"- `{p}`")
    if not generated and not orphaned:
        lines.append("No results or figures detected.")
    lines.append("")


def _section_undeclared_env(graph: EvidenceGraph, lines: list[str]) -> None:
    """Q3: Which scripts depend on undeclared environment?"""
    env_nodes = [n for n in graph.nodes if n.type == "environment"]
    declared_envs = {n.path for n in env_nodes}

    script_nodes = [n for n in graph.nodes if n.type == "script"]
    if not script_nodes:
        lines.append("No script nodes found.")
        lines.append("")
        return

    if not declared_envs:
        lines.append("**No environment files found.** All scripts depend on undeclared environment.")
        for s in script_nodes:
            lines.append(f"- `{s.path}`")
        lines.append("")
        return

    lines.append(f"Declared environment files: {', '.join(f'`{e}`' for e in sorted(declared_envs))}")
    lines.append("")

    # Check if any script has a "requires" edge from an environment node
    scripts_with_env: set[str] = set()
    for e in graph.edges:
        if e.relation == "requires":
            source = graph.get_node(e.source)
            target = graph.get_node(e.target)
            if source and source.type == "script" and target and target.type == "environment":
                scripts_with_env.add(source.id)

    undeclared = [s for s in script_nodes if s.id not in scripts_with_env]
    if undeclared:
        lines.append("**Scripts without explicit environment dependency:**")
        for s in undeclared:
            lines.append(f"- `{s.path}`")
    else:
        lines.append("All scripts have explicit environment dependencies.")
    lines.append("")


def _section_data_no_availability(graph: EvidenceGraph, lines: list[str]) -> None:
    """Q4: Which data is referenced but has no availability (file does not exist)?"""
    data_nodes = [n for n in graph.nodes if n.type == "data"]
    if not data_nodes:
        lines.append("No data nodes found.")
        lines.append("")
        return

    missing = [n for n in data_nodes if not n.exists]
    present = [n for n in data_nodes if n.exists]

    if missing:
        lines.append("**Referenced data files that do not exist on disk:**")
        for n in missing:
            referrers = []
            for e in graph.get_edges_to(n.id):
                source = graph.get_node(e.source)
                if source:
                    referrers.append(source.path)
            ref_str = f" (referenced by: {', '.join(f'`{r}`' for r in referrers)})" if referrers else ""
            lines.append(f"- `{n.path}`{ref_str}")
    if present:
        lines.append("")
        lines.append(f"Data files that exist: {len(present)}")
    if not data_nodes:
        lines.append("No data references detected.")
    lines.append("")


def _section_orphan_figures(graph: EvidenceGraph, lines: list[str]) -> None:
    """Q5: Which figures/tables are orphan (no incoming edges)?"""
    fig_table_nodes = [n for n in graph.nodes if n.type in ("figure", "table")]
    if not fig_table_nodes:
        lines.append("No figure or table nodes found.")
        lines.append("")
        return

    orphaned: list[GraphNode] = []
    connected: list[tuple[GraphNode, list[str]]] = []

    for ft in fig_table_nodes:
        incoming = graph.get_edges_to(ft.id)
        if not incoming:
            orphaned.append(ft)
        else:
            sources = []
            for e in incoming:
                source = graph.get_node(e.source)
                if source:
                    sources.append(source.path)
            connected.append((ft, sources))

    if orphaned:
        lines.append("**Orphan figures/tables (not referenced by any paper):**")
        for ft in orphaned:
            lines.append(f"- `{ft.path}` (type: {ft.type})")
    else:
        lines.append("No orphan figures or tables -- all are referenced.")

    if connected:
        lines.append("")
        lines.append("**Connected figures/tables:**")
        for ft, sources in connected:
            lines.append(f"- `{ft.path}` referenced by: {', '.join(f'`{s}`' for s in sources)}")
    lines.append("")


def _section_missing_outputs(graph: EvidenceGraph, lines: list[str]) -> None:
    """Q6: Which expected outputs are missing (generates edge target doesn't exist)?"""
    generates_edges = [e for e in graph.edges if e.relation == "generates"]
    if not generates_edges:
        lines.append("No 'generates' edges found -- no expected outputs to check.")
        lines.append("")
        return

    missing: list[tuple[str, str, str]] = []  # (script, output, evidence)
    present: list[tuple[str, str]] = []

    for e in generates_edges:
        target = graph.get_node(e.target)
        source = graph.get_node(e.source)
        if target and source:
            if not target.exists:
                missing.append((source.path, target.path, e.evidence))
            else:
                present.append((source.path, target.path))

    if missing:
        lines.append("**Expected outputs that do not exist on disk:**")
        for script, output, ev in missing:
            lines.append(f"- `{script}` should generate `{output}` ({ev})")
    else:
        lines.append("All expected outputs exist on disk.")

    if present:
        lines.append("")
        lines.append(f"Verified outputs: {len(present)}")
    lines.append("")
