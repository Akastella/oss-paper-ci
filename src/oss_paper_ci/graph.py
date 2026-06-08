"""Evidence graph model and builder for oss-paper-ci.

The evidence graph captures relationships between repository artifacts:
which scripts generate which figures, which papers reference which results,
which configs govern which runs, etc.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from oss_paper_ci.utils.fs import find_files_by_extensions, list_files, read_text_file


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class GraphNode:
    """A single artifact in the evidence graph."""

    id: str
    type: str  # paper|tex|bib|readme|script|config|environment|data|result|figure|table|notebook|ci|contract
    path: str = ""
    label: str = ""
    exists: bool = True
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GraphEdge:
    """A directed relationship between two nodes."""

    source: str  # node id
    target: str  # node id
    relation: str  # references|generates|requires|declares|documents|validates|runs|outputs
    evidence: str = ""
    confidence: str = "inferred"  # explicit|inferred

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvidenceGraph:
    """Collection of nodes and edges representing repository evidence."""

    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)

    # -- mutation -----------------------------------------------------------

    def add_node(self, node: GraphNode) -> None:
        """Add a node, replacing any existing node with the same id."""
        for i, n in enumerate(self.nodes):
            if n.id == node.id:
                self.nodes[i] = node
                return
        self.nodes.append(node)

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge (duplicates are allowed -- they carry evidence)."""
        self.edges.append(edge)

    # -- queries ------------------------------------------------------------

    def get_node(self, id: str) -> GraphNode | None:
        """Return node by id, or None."""
        for n in self.nodes:
            if n.id == id:
                return n
        return None

    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        """Return all edges originating from *node_id*."""
        return [e for e in self.edges if e.source == node_id]

    def get_edges_to(self, node_id: str) -> list[GraphEdge]:
        """Return all edges targeting *node_id*."""
        return [e for e in self.edges if e.target == node_id]

    def find_orphan_nodes(self) -> list[GraphNode]:
        """Return nodes that have no edges (neither incoming nor outgoing)."""
        connected: set[str] = set()
        for e in self.edges:
            connected.add(e.source)
            connected.add(e.target)
        return [n for n in self.nodes if n.id not in connected]

    def find_broken_edges(self) -> list[GraphEdge]:
        """Return edges whose source or target node does not exist in the graph."""
        node_ids = {n.id for n in self.nodes}
        return [e for e in self.edges if e.source not in node_ids or e.target not in node_ids]

    def to_dict(self) -> dict:
        """Serialize to a JSON-friendly dict.

        Includes ``missing_edges``, ``orphan_nodes``, and ``coverage``
        metrics in addition to the raw ``nodes`` and ``edges``.
        """
        node_ids = {n.id for n in self.nodes}
        missing_edges = [
            e.to_dict() for e in self.edges
            if e.source not in node_ids or e.target not in node_ids
        ]
        orphan_nodes = [n.to_dict() for n in self.find_orphan_nodes()]

        # Coverage: do paper artifacts / results / figures have a generation path?
        fig_with_gen = 0
        fig_total = 0
        res_with_gen = 0
        res_total = 0
        paper_with_gen = 0
        paper_total = 0

        for n in self.nodes:
            if n.type == "figure":
                fig_total += 1
                if any(e.relation == "generates" for e in self.get_edges_to(n.id)):
                    fig_with_gen += 1
            elif n.type == "result":
                res_total += 1
                if any(e.relation == "generates" for e in self.get_edges_to(n.id)):
                    res_with_gen += 1
            elif n.type == "tex":
                paper_total += 1
                if any(
                    e.relation in ("references", "generates")
                    for e in self.get_edges_from(n.id)
                    if self.get_node(e.target) and self.get_node(e.target).type == "script"
                ):
                    paper_with_gen += 1

        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "missing_edges": missing_edges,
            "orphan_nodes": orphan_nodes,
            "coverage": {
                "paper_artifacts_with_generation_path": paper_with_gen,
                "results_with_generation_path": res_with_gen,
                "figures_with_generation_path": fig_with_gen,
                "paper_artifacts_total": paper_total,
                "results_total": res_total,
                "figures_total": fig_total,
            },
        }


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

# Extension -> node type mapping
_EXT_TYPE_MAP: dict[str, str] = {
    ".tex": "tex",
    ".bib": "bib",
    ".py": "script",
    ".sh": "script",
    ".r": "script",
    ".R": "script",
    ".jl": "script",
    ".ipynb": "notebook",
    ".yml": "config",
    ".yaml": "config",
    ".toml": "config",
    ".cfg": "config",
    ".ini": "config",
    ".json": "config",
    ".png": "figure",
    ".jpg": "figure",
    ".jpeg": "figure",
    ".pdf": "figure",
    ".svg": "figure",
    ".csv": "data",
    ".tsv": "data",
    ".h5": "data",
    ".hdf5": "data",
    ".parquet": "data",
    ".npy": "data",
    ".npz": "data",
    ".pkl": "data",
    ".pickle": "data",
    ".md": "readme",
    ".rst": "readme",
}

# Files that indicate environment definitions
_ENV_FILES = {
    "requirements.txt", "environment.yml", "environment.yaml",
    "conda.yml", "conda.yaml", "Pipfile", "poetry.lock",
    "pyproject.toml", "setup.py", "setup.cfg",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "Makefile",
}

# CI-related files
_CI_PATHS = {".github", ".circleci", ".travis.yml", ".gitlab-ci.yml", "Jenkinsfile"}

# Contract files
_CONTRACT_FILES = {"contract.yml", "contract.yaml", "reproducibility.yml", "reproducibility.yaml"}


def _make_node_id(node_type: str, rel_path: str) -> str:
    """Build a deterministic node id."""
    return f"{node_type}:{rel_path}"


def _normalise_rel_path(path: Path, root: Path) -> str:
    """Return path relative to root, using forward slashes."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_under(rel_path: str, dirs: list[str]) -> bool:
    """Check whether rel_path lives under any of the given directories."""
    parts = Path(rel_path).parts
    return any(d in parts for d in dirs)


def build_evidence_graph(repo_path: str, config=None) -> EvidenceGraph:
    """Build an evidence graph from repository analysis.

    Args:
        repo_path: Absolute path to the repository root.
        config: Optional ``Config`` object (used for ignore paths and
                project directories).  If *None*, defaults are used.

    Returns:
        A fully-populated ``EvidenceGraph``.
    """
    from oss_paper_ci.config import load_config

    root = Path(repo_path).resolve()
    if config is None:
        config = load_config(repo_root=str(root))

    ignore = list(config.ignore.paths)
    graph = EvidenceGraph()

    files = list_files(root, ignore)

    # -- 1. Create nodes for every relevant file ---------------------------
    file_nodes: dict[str, GraphNode] = {}  # rel_path -> node

    for fpath in files:
        ext = fpath.suffix.lower()
        rel = fpath.as_posix()
        node_type = _EXT_TYPE_MAP.get(ext)

        # Special file-name checks
        fname = fpath.name
        if fname in _ENV_FILES or fname == "requirements.txt":
            node_type = "environment"
        if fname in _CONTRACT_FILES:
            node_type = "contract"
        if any(p in fpath.parts for p in _CI_PATHS) or fname in {
            ".travis.yml", ".gitlab-ci.yml", "Jenkinsfile"
        }:
            node_type = "ci"
        if fname.lower() in {"readme.md", "readme.rst", "readme.txt"}:
            node_type = "readme"

        if node_type is None:
            continue

        nid = _make_node_id(node_type, rel)
        node = GraphNode(id=nid, type=node_type, path=rel, label=fname)
        graph.add_node(node)
        file_nodes[rel] = node

    # -- 2. Scan .tex files for \includegraphics and \input ----------------
    _scan_tex_references(graph, root, file_nodes)

    # -- 3. Scan README for commands that run scripts ----------------------
    _scan_readme_commands(graph, root, file_nodes)

    # -- 4. Scan scripts for data file references --------------------------
    _scan_script_data_refs(graph, root, file_nodes)

    # -- 5. Scan configs for referenced scripts/data -----------------------
    _scan_config_refs(graph, root, file_nodes)

    # -- 6. Python AST analysis -------------------------------------------
    _run_ast_analysis(graph, root, file_nodes)

    # -- 7. Makefile analysis ---------------------------------------------
    _run_makefile_analysis(graph, root, file_nodes)

    # -- 8. GitHub Actions workflow analysis ------------------------------
    _run_workflow_analysis(graph, root, file_nodes)

    # -- 9. If contract exists, add declared edges ------------------------
    _add_contract_edges(graph, root, file_nodes)

    # -- 10. Infer generation edges (scripts -> figures/results) -----------
    _infer_generation_edges(graph, file_nodes)

    return graph


# ---------------------------------------------------------------------------
# DOT (Graphviz) output
# ---------------------------------------------------------------------------


def generate_dot(graph: EvidenceGraph) -> str:
    """Generate Graphviz DOT format output.

    Args:
        graph: The evidence graph.

    Returns:
        A string containing valid Graphviz DOT syntax.
    """
    lines = ["digraph evidence {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [shape=box];")

    for node in graph.nodes:
        label = node.label or node.path or node.id
        # Escape quotes in label for DOT syntax
        label = label.replace('"', '\\"')
        color = "green" if node.exists else "red"
        lines.append(f'  "{node.id}" [label="{label}" color={color}];')

    for edge in graph.edges:
        relation = edge.relation.replace('"', '\\"')
        lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{relation}"];')

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scanning helpers
# ---------------------------------------------------------------------------

_INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
_INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
_BIBLIOGRAPHY_RE = re.compile(r"\\bibliography\{([^}]+)\}")
_BIBTEX_RE = re.compile(r"\\bibliographystyle\{[^}]+\}")


def _scan_tex_references(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Add edges from tex files to referenced figures, tables, and bib files."""
    for rel, node in file_nodes.items():
        if node.type != "tex":
            continue

        content = read_text_file(root / rel)
        if content is None:
            continue

        tex_dir = Path(rel).parent

        # \includegraphics -> figure references
        for match in _INCLUDEGRAPHICS_RE.finditer(content):
            ref_path = match.group(1).strip()
            # Resolve relative to the .tex file directory
            resolved = (tex_dir / ref_path).as_posix()
            fig_id = _make_node_id("figure", resolved)
            if graph.get_node(fig_id) is None:
                # Create a stub node (may not exist on disk)
                fig_node = GraphNode(
                    id=fig_id, type="figure", path=resolved,
                    label=Path(resolved).name, exists=(root / resolved).exists(),
                )
                graph.add_node(fig_node)
            graph.add_edge(GraphEdge(
                source=node.id, target=fig_id,
                relation="references",
                evidence=f"\\includegraphics{{{ref_path}}}",
                confidence="explicit",
            ))

        # \input -> table/section references
        for match in _INPUT_RE.finditer(content):
            ref_path = match.group(1).strip()
            if not ref_path.endswith(".tex"):
                ref_path += ".tex"
            resolved = (tex_dir / ref_path).as_posix()
            input_id = _make_node_id("tex", resolved)
            if graph.get_node(input_id) is None:
                input_node = GraphNode(
                    id=input_id, type="tex", path=resolved,
                    label=Path(resolved).name, exists=(root / resolved).exists(),
                )
                graph.add_node(input_node)
            graph.add_edge(GraphEdge(
                source=node.id, target=input_id,
                relation="references",
                evidence=f"\\input{{{match.group(1)}}}",
                confidence="explicit",
            ))

        # \bibliography -> bib references
        for match in _BIBLIOGRAPHY_RE.finditer(content):
            for bib_name in match.group(1).split(","):
                bib_name = bib_name.strip()
                if not bib_name.endswith(".bib"):
                    bib_name += ".bib"
                resolved = (tex_dir / bib_name).as_posix()
                bib_id = _make_node_id("bib", resolved)
                if graph.get_node(bib_id) is None:
                    bib_node = GraphNode(
                        id=bib_id, type="bib", path=resolved,
                        label=Path(resolved).name, exists=(root / resolved).exists(),
                    )
                    graph.add_node(bib_node)
                graph.add_edge(GraphEdge(
                    source=node.id, target=bib_id,
                    relation="references",
                    evidence=f"\\bibliography{{{match.group(1)}}}",
                    confidence="explicit",
                ))


def _scan_readme_commands(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Scan README files for shell commands that reference scripts."""
    from oss_paper_ci.utils.text import find_commands_in_text

    for rel, node in file_nodes.items():
        if node.type != "readme":
            continue

        content = read_text_file(root / rel)
        if content is None:
            continue

        commands = find_commands_in_text(content)
        for cmd in commands:
            # Look for script invocations (e.g., python scripts/train.py)
            script_match = re.search(r'(?:python|python3|bash|sh)\s+([\w./\-]+\.\w+)', cmd)
            if script_match:
                script_path = script_match.group(1)
                script_id = _make_node_id("script", script_path)
                if graph.get_node(script_id) is None:
                    s_node = GraphNode(
                        id=script_id, type="script", path=script_path,
                        label=Path(script_path).name,
                        exists=(root / script_path).exists(),
                    )
                    graph.add_node(s_node)
                graph.add_edge(GraphEdge(
                    source=node.id, target=script_id,
                    relation="runs",
                    evidence=f"Command in README: `{cmd}`",
                    confidence="explicit",
                ))

            # Look for data download commands
            if "download" in cmd.lower() or "wget" in cmd or "curl" in cmd:
                for drel, dnode in file_nodes.items():
                    if dnode.type == "data":
                        if dnode.label in cmd or dnode.path in cmd:
                            graph.add_edge(GraphEdge(
                                source=node.id, target=dnode.id,
                                relation="references",
                                evidence=f"Data mentioned in README: `{cmd}`",
                                confidence="inferred",
                            ))


def _scan_script_data_refs(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Scan Python scripts for file I/O references to data/result paths."""
    _DATA_IO_RE = re.compile(
        r"""(?:open|read_csv|read_json|read_parquet|load|np\.load|pd\.read_|to_csv|savefig|save|write)\s*\(\s*['\"]([\w./\-]+\.\w+)['\"]""",
    )
    _ARGPARSE_PATH_RE = re.compile(
        r"""(?:default|type)\s*=\s*['\"]([\w./\-]+\.\w+)['\"]""",
    )

    for rel, node in file_nodes.items():
        if node.type != "script":
            continue

        content = read_text_file(root / rel)
        if content is None:
            continue

        found_paths: set[str] = set()
        for match in _DATA_IO_RE.finditer(content):
            found_paths.add(match.group(1))
        for match in _ARGPARSE_PATH_RE.finditer(content):
            found_paths.add(match.group(1))

        for ref_path in found_paths:
            # Determine the type of the referenced file
            ext = Path(ref_path).suffix.lower()
            ref_type = _EXT_TYPE_MAP.get(ext, "data")
            ref_id = _make_node_id(ref_type, ref_path)

            if graph.get_node(ref_id) is None:
                ref_node = GraphNode(
                    id=ref_id, type=ref_type, path=ref_path,
                    label=Path(ref_path).name,
                    exists=(root / ref_path).exists(),
                )
                graph.add_node(ref_node)

            # Determine relation: writing = generates, reading = requires
            if any(kw in content for kw in [f"to_csv", f"savefig", f"save", f"write"]):
                rel_type = "generates"
            else:
                rel_type = "requires"
            graph.add_edge(GraphEdge(
                source=node.id, target=ref_id,
                relation=rel_type,
                evidence=f"File reference in {Path(rel).name}",
                confidence="inferred",
            ))


def _scan_config_refs(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Scan YAML/TOML config files for references to scripts and data."""
    _SCRIPT_REF_RE = re.compile(r'(?:script|command|cmd|entry)\s*[:=]\s*["\']?([\w./\-]+\.\w+)["\']?')
    _DATA_REF_RE = re.compile(r'(?:data|path|file|input|output)\s*[:=]\s*["\']?([\w./\-]+/[\w./\-]+\.\w+)["\']?')

    for rel, node in file_nodes.items():
        if node.type != "config":
            continue

        content = read_text_file(root / rel)
        if content is None:
            continue

        for match in _SCRIPT_REF_RE.finditer(content):
            script_path = match.group(1)
            script_id = _make_node_id("script", script_path)
            if graph.get_node(script_id) is None:
                s_node = GraphNode(
                    id=script_id, type="script", path=script_path,
                    label=Path(script_path).name,
                    exists=(root / script_path).exists(),
                )
                graph.add_node(s_node)
            graph.add_edge(GraphEdge(
                source=node.id, target=script_id,
                relation="runs",
                evidence=f"Config reference in {Path(rel).name}",
                confidence="explicit",
            ))

        for match in _DATA_REF_RE.finditer(content):
            data_path = match.group(1)
            ext = Path(data_path).suffix.lower()
            data_type = _EXT_TYPE_MAP.get(ext, "data")
            data_id = _make_node_id(data_type, data_path)
            if graph.get_node(data_id) is None:
                d_node = GraphNode(
                    id=data_id, type=data_type, path=data_path,
                    label=Path(data_path).name,
                    exists=(root / data_path).exists(),
                )
                graph.add_node(d_node)
            graph.add_edge(GraphEdge(
                source=node.id, target=data_id,
                relation="references",
                evidence=f"Config reference in {Path(rel).name}",
                confidence="explicit",
            ))


def _add_contract_edges(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """If a contract file exists, load it and add explicit declared edges.

    This replaces the old simple "link contract to everything" approach.
    Contract-declared edges are marked ``confidence="explicit"``; any
    remaining inferred edges keep ``confidence="inferred"``.
    """
    from oss_paper_ci.contract import find_contract, load_contract

    contract_path = find_contract(str(root))
    if contract_path is None:
        # Fall back to the simple approach if only a contract node was found
        contract_nodes = [n for n in file_nodes.values() if n.type == "contract"]
        for contract in contract_nodes:
            for node in file_nodes.values():
                if node.type in ("script", "config", "environment"):
                    graph.add_edge(GraphEdge(
                        source=contract.id, target=node.id,
                        relation="declares",
                        evidence="Contract declaration",
                        confidence="explicit",
                    ))
        return

    try:
        contract = load_contract(contract_path)
    except Exception:
        return  # gracefully skip if contract can't be parsed

    contract_rel = _normalise_rel_path(Path(contract_path), root)
    contract_id = _make_node_id("contract", contract_rel)

    # --- Experiments -> scripts ---
    for exp in contract.experiments:
        if not exp.command:
            continue
        # Extract script references from the command
        script_match = re.search(r'(?:python3?|bash|sh)\s+([\w./\-]+\.\w+)', exp.command)
        if script_match:
            script_path = script_match.group(1)
            script_id = _make_node_id("script", script_path)
            if graph.get_node(script_id) is None:
                s_node = GraphNode(
                    id=script_id, type="script", path=script_path,
                    label=Path(script_path).name,
                    exists=(root / script_path).exists(),
                )
                graph.add_node(s_node)
            graph.add_edge(GraphEdge(
                source=contract_id, target=script_id,
                relation="declares",
                evidence=f"Contract experiment '{exp.id}' runs: {exp.command}",
                confidence="explicit",
            ))

        # Experiment -> expected outputs
        for output in exp.expected_outputs:
            ext = Path(output).suffix.lower()
            out_type = _EXT_TYPE_MAP.get(ext, "result")
            out_id = _make_node_id(out_type, output)
            if graph.get_node(out_id) is None:
                o_node = GraphNode(
                    id=out_id, type=out_type, path=output,
                    label=Path(output).name,
                    exists=(root / output).exists(),
                )
                graph.add_node(o_node)
            graph.add_edge(GraphEdge(
                source=contract_id, target=out_id,
                relation="declares",
                evidence=f"Contract experiment '{exp.id}' declares output: {output}",
                confidence="explicit",
            ))

    # --- Figures ---
    for fig in contract.figures:
        if not fig.path:
            continue
        fig_id = _make_node_id("figure", fig.path)
        if graph.get_node(fig_id) is None:
            f_node = GraphNode(
                id=fig_id, type="figure", path=fig.path,
                label=Path(fig.path).name,
                exists=(root / fig.path).exists(),
            )
            graph.add_node(f_node)
        graph.add_edge(GraphEdge(
            source=contract_id, target=fig_id,
            relation="declares",
            evidence=f"Contract declares figure '{fig.id}'",
            confidence="explicit",
        ))

        # Link generated_by experiment scripts to the figure
        for exp_id in fig.generated_by:
            # Find matching experiment
            for exp in contract.experiments:
                if exp.id == exp_id and exp.command:
                    script_match = re.search(
                        r'(?:python3?|bash|sh)\s+([\w./\-]+\.\w+)', exp.command,
                    )
                    if script_match:
                        script_id = _make_node_id("script", script_match.group(1))
                        if graph.get_node(script_id):
                            graph.add_edge(GraphEdge(
                                source=script_id, target=fig_id,
                                relation="generates",
                                evidence=f"Contract: figure '{fig.id}' generated_by experiment '{exp_id}'",
                                confidence="explicit",
                            ))

    # --- Results ---
    for res in contract.results:
        if not res.path:
            continue
        res_id = _make_node_id("result", res.path)
        if graph.get_node(res_id) is None:
            r_node = GraphNode(
                id=res_id, type="result", path=res.path,
                label=Path(res.path).name,
                exists=(root / res.path).exists(),
            )
            graph.add_node(r_node)
        graph.add_edge(GraphEdge(
            source=contract_id, target=res_id,
            relation="declares",
            evidence=f"Contract declares result '{res.id}'",
            confidence="explicit",
        ))

        for exp_id in res.generated_by:
            for exp in contract.experiments:
                if exp.id == exp_id and exp.command:
                    script_match = re.search(
                        r'(?:python3?|bash|sh)\s+([\w./\-]+\.\w+)', exp.command,
                    )
                    if script_match:
                        script_id = _make_node_id("script", script_match.group(1))
                        if graph.get_node(script_id):
                            graph.add_edge(GraphEdge(
                                source=script_id, target=res_id,
                                relation="generates",
                                evidence=f"Contract: result '{res.id}' generated_by experiment '{exp_id}'",
                                confidence="explicit",
                            ))

    # --- Data ---
    for ds in contract.data:
        if not ds.path:
            continue
        ext = Path(ds.path).suffix.lower()
        ds_type = _EXT_TYPE_MAP.get(ext, "data")
        ds_id = _make_node_id(ds_type, ds.path)
        if graph.get_node(ds_id) is None:
            d_node = GraphNode(
                id=ds_id, type=ds_type, path=ds.path,
                label=Path(ds.path).name,
                exists=(root / ds.path).exists(),
            )
            graph.add_node(d_node)
        graph.add_edge(GraphEdge(
            source=contract_id, target=ds_id,
            relation="declares",
            evidence=f"Contract declares data '{ds.id}'",
            confidence="explicit",
        ))

    # --- Environment ---
    if contract.environment.file:
        env_id = _make_node_id("environment", contract.environment.file)
        if graph.get_node(env_id) is None:
            e_node = GraphNode(
                id=env_id, type="environment", path=contract.environment.file,
                label=Path(contract.environment.file).name,
                exists=(root / contract.environment.file).exists(),
            )
            graph.add_node(e_node)
        graph.add_edge(GraphEdge(
            source=contract_id, target=env_id,
            relation="declares",
            evidence="Contract declares environment file",
            confidence="explicit",
        ))

    # --- Link contract to remaining scripts/configs not yet linked ---
    for node in file_nodes.values():
        if node.type in ("script", "config", "environment"):
            existing = [
                e for e in graph.edges
                if e.source == contract_id and e.target == node.id
            ]
            if not existing:
                graph.add_edge(GraphEdge(
                    source=contract_id, target=node.id,
                    relation="declares",
                    evidence="Contract declaration",
                    confidence="explicit",
                ))


# ---------------------------------------------------------------------------
# Python AST analysis
# ---------------------------------------------------------------------------


def _resolve_import_aliases(tree: ast.Module) -> dict[str, str]:
    """Build a mapping from local name -> module name for common imports.

    Handles ``import numpy as np``, ``import pandas as pd``, etc.
    Returns e.g. ``{"np": "numpy", "pd": "pandas", "plt": "matplotlib.pyplot"}``.
    """
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name
                aliases[local] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                local = alias.asname or alias.name
                aliases[local] = f"{module}.{alias.name}" if module else alias.name
    return aliases


def _call_name(call: ast.Call, aliases: dict[str, str]) -> str:
    """Return the fully-qualified name of a Call node, resolving aliases."""
    func = call.func
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            mod = aliases.get(func.value.id, func.value.id)
            return f"{mod}.{func.attr}"
        return func.attr
    if isinstance(func, ast.Name):
        return aliases.get(func.id, func.id)
    return ""


def _get_string_args(call: ast.Call) -> list[str]:
    """Extract string literal arguments from a Call node."""
    result: list[str] = []
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            result.append(arg.value)
    for kw in call.keywords:
        if kw.value and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            result.append(kw.value.value)
    return result


def _get_keyword_value(call: ast.Call, keyword: str) -> str | None:
    """Extract a specific keyword argument string value."""
    for kw in call.keywords:
        if kw.arg == keyword and isinstance(kw.value, ast.Constant):
            val = kw.value.value
            if isinstance(val, str):
                return val
    return None


def _analyze_python_file(
    filepath: str,
    repo_root: str,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Parse a Python file with AST and detect patterns relevant to reproducibility.

    Detects:
    - argparse/click/typer entry points -> marks as entrypoint
    - ``open()`` calls with write mode -> script writes to file
    - ``pd.read_csv()``, ``pd.to_csv()`` -> data read/write
    - ``plt.savefig()`` -> script generates figure
    - ``torch.save()``, ``pickle.dump()`` -> model/result save
    - ``json.dump()`` -> JSON output
    - Config file reads (yaml.safe_load, json.load) -> script requires config
    - Seed setting (random.seed, np.random.seed, torch.manual_seed) -> reproducibility marker
    - Hardcoded absolute paths -> risk marker
    """
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    root = Path(repo_root)
    rel_path = filepath

    try:
        source = (root / filepath).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return nodes, edges

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return nodes, edges

    aliases = _resolve_import_aliases(tree)
    script_id = _make_node_id("script", rel_path)
    metadata: dict = {
        "is_entrypoint": False,
        "writes_files": False,
        "generates_figures": False,
        "reads_config": False,
        "sets_seed": False,
        "hardcoded_paths": [],
    }

    # Track all call nodes for pattern detection
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = _call_name(node, aliases)
        str_args = _get_string_args(node)

        # --- Entry point detection ---
        if name in ("argparse.ArgumentParser", "click.command", "typer.Typer"):
            metadata["is_entrypoint"] = True

        # --- File open with write mode ---
        if name == "open" and str_args:
            mode_kw = _get_keyword_value(node, "mode")
            # Check positional mode arg
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                mode_val = node.args[1].value
                if isinstance(mode_val, str) and any(m in mode_val for m in ("w", "a", "x")):
                    metadata["writes_files"] = True
                    for path_str in str_args:
                        _add_file_edge(script_id, path_str, "generates", edges, root, rel_path)
            elif mode_kw and any(m in mode_kw for m in ("w", "a", "x")):
                metadata["writes_files"] = True
                for path_str in str_args:
                    _add_file_edge(script_id, path_str, "generates", edges, root, rel_path)

        # --- pd.read_csv / pd.read_json / pd.read_parquet ---
        if name in ("pandas.read_csv", "pandas.read_json", "pandas.read_parquet"):
            for path_str in str_args:
                _add_file_edge(script_id, path_str, "requires", edges, root, rel_path)

        # --- pd.to_csv ---
        if name == "pandas.DataFrame.to_csv":
            for path_str in str_args:
                _add_file_edge(script_id, path_str, "generates", edges, root, rel_path)

        # --- plt.savefig ---
        if name in ("matplotlib.pyplot.savefig", "plt.savefig"):
            metadata["generates_figures"] = True
            for path_str in str_args:
                _add_file_edge(script_id, path_str, "generates", edges, root, rel_path, node_type="figure")

        # --- torch.save / pickle.dump / np.save ---
        if name in ("torch.save", "pickle.dump", "numpy.save", "numpy.savez"):
            metadata["writes_files"] = True
            for path_str in str_args:
                _add_file_edge(script_id, path_str, "generates", edges, root, rel_path)

        # --- json.dump ---
        if name == "json.dump":
            metadata["writes_files"] = True
            # json.dump(obj, fp) -- fp is the second arg
            if len(node.args) >= 2:
                # fp might be a variable, not a string; skip if not string
                pass
            for path_str in str_args:
                _add_file_edge(script_id, path_str, "generates", edges, root, rel_path)

        # --- Config reads ---
        if name in ("yaml.safe_load", "yaml.load", "yaml.full_load",
                     "json.load", "json.loads", "toml.load"):
            metadata["reads_config"] = True

        # --- Seed setting ---
        if name in ("random.seed", "numpy.random.seed", "numpy.random.RandomState",
                     "torch.manual_seed", "torch.cuda.manual_seed",
                     "torch.cuda.manual_seed_all", "tensorflow.random.set_seed",
                     "set_seed"):
            metadata["sets_seed"] = True

    # --- Hardcoded absolute paths (string literals starting with / or C:\) ---
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if (val.startswith("/") and len(val) > 3 and "." in val) or \
               (re.match(r"^[A-Za-z]:\\", val)):
                metadata["hardcoded_paths"].append(val)

    if metadata["hardcoded_paths"]:
        metadata["hardcoded_paths"] = list(set(metadata["hardcoded_paths"]))[:5]

    # Update the script node metadata (if it exists in graph, it will be merged later)
    nodes.append(GraphNode(
        id=script_id, type="script", path=rel_path,
        label=Path(rel_path).name,
        exists=(root / rel_path).exists(),
        metadata=metadata,
    ))

    return nodes, edges


def _add_file_edge(
    source_id: str,
    path_str: str,
    relation: str,
    edges: list[GraphEdge],
    root: Path,
    script_rel: str,
    node_type: str | None = None,
) -> None:
    """Helper to create an edge from a script to a referenced file path."""
    # Skip URLs, non-file strings
    if path_str.startswith(("http://", "https://", "ftp://")):
        return
    # Skip very short strings or format specifiers
    if len(path_str) < 3 or "%" in path_str:
        return

    # Resolve relative paths against the script's directory
    script_dir = Path(script_rel).parent
    resolved = (script_dir / path_str).resolve()
    try:
        rel = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = path_str

    ext = Path(rel).suffix.lower()
    if node_type is None:
        node_type = _EXT_TYPE_MAP.get(ext, "result")

    target_id = _make_node_id(node_type, rel)
    evidence_desc = "generates" if relation == "generates" else "reads"
    edges.append(GraphEdge(
        source=source_id, target=target_id,
        relation=relation,
        evidence=f"Python AST: script {evidence_desc} '{path_str}'",
        confidence="inferred",
    ))


# ---------------------------------------------------------------------------
# Makefile analysis
# ---------------------------------------------------------------------------

_MAKEFILE_TARGET_RE = re.compile(r"^([a-zA-Z_][\w\-]*)\s*:", re.MULTILINE)


def _analyze_makefile(
    filepath: str,
    repo_root: str,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Parse Makefile targets and extract command relationships.

    Uses regex to find targets (lines starting with ``name:``) and
    extracts ``python ...`` / ``bash ...`` / ``sh ...`` commands from
    each target body.
    """
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    root = Path(repo_root)

    try:
        source = (root / filepath).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return nodes, edges

    lines = source.splitlines()
    current_target: str | None = None
    current_commands: list[str] = []

    for line in lines:
        # Detect target line (not indented, ends with colon)
        target_match = re.match(r"^([a-zA-Z_][\w\-]*)\s*:", line)
        if target_match:
            # Process previous target
            if current_target is not None:
                _process_make_target(current_target, current_commands, filepath, nodes, edges)
            current_target = target_match.group(1)
            current_commands = []
            continue

        # Command lines start with a tab
        if current_target is not None and line.startswith("\t"):
            cmd = line.strip()
            if cmd and not cmd.startswith("#"):
                current_commands.append(cmd)

    # Process last target
    if current_target is not None:
        _process_make_target(current_target, current_commands, filepath, nodes, edges)

    return nodes, edges


def _process_make_target(
    target: str,
    commands: list[str],
    makefile_rel: str,
    nodes: list[GraphNode],
    edges: list[GraphEdge],
) -> None:
    """Create edges for a single Makefile target."""
    # Skip .PHONY and clean-style targets for node creation
    if target.startswith("."):
        return

    makefile_dir = Path(makefile_rel).parent
    target_id = _make_node_id("make_target", f"{makefile_rel}::{target}")

    for cmd in commands:
        # Link target -> scripts
        script_match = re.search(r'(?:python3?|bash|sh)\s+([\w./\-]+\.\w+)', cmd)
        if script_match:
            script_path = script_match.group(1)
            # Resolve relative to makefile directory
            resolved = (makefile_dir / script_path).as_posix()
            script_id = _make_node_id("script", resolved)
            edges.append(GraphEdge(
                source=target_id, target=script_id,
                relation="runs",
                evidence=f"Makefile target '{target}' runs: {cmd}",
                confidence="explicit",
            ))

        # Link target -> config files referenced via --config
        config_match = re.search(r'--config\s+([\w./\-]+\.\w+)', cmd)
        if config_match:
            config_path = config_match.group(1)
            resolved = (makefile_dir / config_path).as_posix()
            config_id = _make_node_id("config", resolved)
            edges.append(GraphEdge(
                source=target_id, target=config_id,
                relation="requires",
                evidence=f"Makefile target '{target}' requires config: {config_path}",
                confidence="explicit",
            ))

        # Link target -> checkpoint files referenced via --checkpoint
        ckpt_match = re.search(r'--checkpoint\s+([\w./\-]+\.\w+)', cmd)
        if ckpt_match:
            ckpt_path = ckpt_match.group(1)
            resolved = (makefile_dir / ckpt_path).as_posix()
            ckpt_id = _make_node_id("data", resolved)
            edges.append(GraphEdge(
                source=target_id, target=ckpt_id,
                relation="requires",
                evidence=f"Makefile target '{target}' requires checkpoint: {ckpt_path}",
                confidence="explicit",
            ))


# ---------------------------------------------------------------------------
# GitHub Actions workflow analysis
# ---------------------------------------------------------------------------


def _analyze_workflow(
    filepath: str,
    repo_root: str,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Parse a GitHub Actions YAML workflow and extract command relationships.

    Extracts ``run:`` commands and links them to referenced scripts.
    """
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    root = Path(repo_root)

    try:
        source = (root / filepath).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return nodes, edges

    try:
        data = yaml.safe_load(source)
    except Exception:
        return nodes, edges

    if not isinstance(data, dict):
        return nodes, edges

    workflow_name = data.get("name", Path(filepath).stem)
    workflow_id = _make_node_id("ci", filepath)

    jobs = data.get("jobs", {})
    if not isinstance(jobs, dict):
        return nodes, edges

    for job_name, job_def in jobs.items():
        if not isinstance(job_def, dict):
            continue
        steps = job_def.get("steps", [])
        if not isinstance(steps, list):
            continue

        for step in steps:
            if not isinstance(step, dict):
                continue
            run_cmd = step.get("run")
            if not run_cmd or not isinstance(run_cmd, str):
                continue

            # Parse multi-line commands
            for line in run_cmd.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Link workflow -> script
                script_match = re.search(
                    r'(?:python3?|bash|sh)\s+([\w./\-]+\.\w+)', line,
                )
                if script_match:
                    script_path = script_match.group(1)
                    script_id = _make_node_id("script", script_path)
                    edges.append(GraphEdge(
                        source=workflow_id, target=script_id,
                        relation="runs",
                        evidence=f"CI workflow '{workflow_name}' ({job_name}) runs: {line}",
                        confidence="explicit",
                    ))

                # Link workflow -> config files via --config
                config_match = re.search(r'--config\s+([\w./\-]+\.\w+)', line)
                if config_match:
                    config_path = config_match.group(1)
                    config_id = _make_node_id("config", config_path)
                    edges.append(GraphEdge(
                        source=workflow_id, target=config_id,
                        relation="requires",
                        evidence=f"CI workflow '{workflow_name}' requires config: {config_path}",
                        confidence="explicit",
                    ))

    return nodes, edges


# ---------------------------------------------------------------------------
# Runner functions for new analyses
# ---------------------------------------------------------------------------


def _run_ast_analysis(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Run Python AST analysis on all script nodes and merge results."""
    for rel, node in file_nodes.items():
        if node.type != "script":
            continue
        if not rel.endswith(".py"):
            continue

        ast_nodes, ast_edges = _analyze_python_file(rel, str(root))

        # Merge metadata from AST analysis into existing node
        for an in ast_nodes:
            existing = graph.get_node(an.id)
            if existing and an.metadata:
                existing.metadata.update(an.metadata)

        # Add edges (avoid exact duplicates)
        existing_edge_keys = {(e.source, e.target, e.relation) for e in graph.edges}
        for edge in ast_edges:
            key = (edge.source, edge.target, edge.relation)
            if key not in existing_edge_keys:
                # Create target node if it doesn't exist yet
                if graph.get_node(edge.target) is None:
                    # Extract type and path from the id: "type:path"
                    parts = edge.target.split(":", 1)
                    if len(parts) == 2:
                        t_type, t_path = parts
                        graph.add_node(GraphNode(
                            id=edge.target, type=t_type, path=t_path,
                            label=Path(t_path).name,
                            exists=(root / t_path).exists(),
                        ))
                graph.add_edge(edge)
                existing_edge_keys.add(key)


def _run_makefile_analysis(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Run Makefile analysis and merge results into the graph."""
    for rel, node in file_nodes.items():
        fname = Path(rel).name
        if fname not in ("Makefile", "makefile", "GNUmakefile"):
            continue

        mk_nodes, mk_edges = _analyze_makefile(rel, str(root))

        for n in mk_nodes:
            graph.add_node(n)

        existing_edge_keys = {(e.source, e.target, e.relation) for e in graph.edges}
        for edge in mk_edges:
            key = (edge.source, edge.target, edge.relation)
            if key not in existing_edge_keys:
                # Create target node if needed
                if graph.get_node(edge.source) is None:
                    parts = edge.source.split(":", 1)
                    if len(parts) == 2:
                        graph.add_node(GraphNode(
                            id=edge.source, type=parts[0], path="",
                            label=edge.source.split("::")[-1] if "::" in edge.source else parts[1],
                        ))
                # Create target artifact node if needed
                if graph.get_node(edge.target) is None:
                    parts = edge.target.split(":", 1)
                    if len(parts) == 2:
                        t_type, t_path = parts
                        graph.add_node(GraphNode(
                            id=edge.target, type=t_type, path=t_path,
                            label=Path(t_path).name,
                            exists=(root / t_path).exists(),
                        ))
                graph.add_edge(edge)
                existing_edge_keys.add(key)


def _run_workflow_analysis(
    graph: EvidenceGraph,
    root: Path,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Run GitHub Actions workflow analysis and merge results into the graph."""
    for rel, node in file_nodes.items():
        if node.type != "ci":
            continue
        if not (rel.endswith(".yml") or rel.endswith(".yaml")):
            continue

        wf_nodes, wf_edges = _analyze_workflow(rel, str(root))

        for n in wf_nodes:
            graph.add_node(n)

        existing_edge_keys = {(e.source, e.target, e.relation) for e in graph.edges}
        for edge in wf_edges:
            key = (edge.source, edge.target, edge.relation)
            if key not in existing_edge_keys:
                # Create CI node if needed
                if graph.get_node(edge.source) is None:
                    graph.add_node(GraphNode(
                        id=edge.source, type="ci", path=rel,
                        label=Path(rel).name,
                    ))
                # Create target node if needed
                if graph.get_node(edge.target) is None:
                    parts = edge.target.split(":", 1)
                    if len(parts) == 2:
                        t_type, t_path = parts
                        graph.add_node(GraphNode(
                            id=edge.target, type=t_type, path=t_path,
                            label=Path(t_path).name,
                            exists=(root / t_path).exists(),
                        ))
                graph.add_edge(edge)
                existing_edge_keys.add(key)


def _infer_generation_edges(
    graph: EvidenceGraph,
    file_nodes: dict[str, GraphNode],
) -> None:
    """Infer edges: scripts whose names suggest they generate figures/results."""
    _PLOT_KEYWORDS = {"plot", "figure", "fig", "visual", "draw", "render", "chart"}
    _RESULT_KEYWORDS = {"result", "eval", "evaluate", "test", "benchmark", "report"}

    for rel, node in file_nodes.items():
        if node.type != "script":
            continue
        stem = Path(rel).stem.lower()

        # If script name contains plot keywords -> may generate figures
        if any(kw in stem for kw in _PLOT_KEYWORDS):
            for fig_rel, fig_node in file_nodes.items():
                if fig_node.type == "figure":
                    # Only add if there is not already an explicit generates edge
                    existing = [
                        e for e in graph.edges
                        if e.source == node.id and e.target == fig_node.id and e.relation == "generates"
                    ]
                    if not existing:
                        graph.add_edge(GraphEdge(
                            source=node.id, target=fig_node.id,
                            relation="generates",
                            evidence=f"Inferred from script name '{stem}'",
                            confidence="inferred",
                        ))

        # If script name contains result keywords -> may generate results
        if any(kw in stem for kw in _RESULT_KEYWORDS):
            for res_rel, res_node in file_nodes.items():
                if res_node.type == "result":
                    existing = [
                        e for e in graph.edges
                        if e.source == node.id and e.target == res_node.id and e.relation == "generates"
                    ]
                    if not existing:
                        graph.add_edge(GraphEdge(
                            source=node.id, target=res_node.id,
                            relation="generates",
                            evidence=f"Inferred from script name '{stem}'",
                            confidence="inferred",
                        ))
