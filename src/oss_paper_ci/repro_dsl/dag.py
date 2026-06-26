"""DAG structures for Reproducibility DSL v1.

Provides topological sort, cycle detection, missing dependency detection,
parallel group detection, and critical path analysis.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Any

from .schema import ReproDSL, StepSpec


@dataclass
class DAGNode:
    """A node in the execution DAG."""

    step_id: str
    command: str
    needs: list[str]
    produces: list[str]
    timeout: int
    in_degree: int = 0
    out_degree: int = 0
    depth: int = 0  # longest path from root
    level: int = 0  # parallel group level

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "command": self.command,
            "needs": sorted(self.needs),
            "produces": sorted(self.produces),
            "timeout": self.timeout,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "depth": self.depth,
            "level": self.level,
        }


@dataclass
class DAG:
    """Directed Acyclic Graph for reproduction step execution."""

    nodes: dict[str, DAGNode]
    edges: list[tuple[str, str]]  # (from_id, to_id)
    topological_order: list[str]
    parallel_groups: list[list[str]]  # groups of steps that can run in parallel
    critical_path: list[str]
    critical_path_duration: int
    cycles: list[list[str]]  # detected cycles
    missing_deps: dict[str, list[str]]  # step_id -> list of missing dependency ids
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in sorted(self.nodes.items())},
            "edges": sorted(self.edges),
            "topological_order": self.topological_order,
            "parallel_groups": self.parallel_groups,
            "critical_path": self.critical_path,
            "critical_path_duration": self.critical_path_duration,
            "cycles": self.cycles,
            "missing_deps": {
                k: sorted(v) for k, v in sorted(self.missing_deps.items())
            },
            "warnings": sorted(self.warnings),
        }

    @property
    def is_valid(self) -> bool:
        return len(self.cycles) == 0 and len(self.missing_deps) == 0


def _find_cycle_paths(
    remaining: set[str], adj: dict[str, list[str]]
) -> list[list[str]]:
    """Find simple cycle paths from the set of nodes remaining after Kahn's.

    Uses DFS with a path stack to extract actual cycle paths.
    Returns a deduplicated list of cycle paths, each sorted with the
    lexicographically smallest node first for deterministic output.
    """
    found: set[tuple[str, ...]] = set()

    def _dfs_from(start: str) -> None:
        """DFS from *start* to find all simple cycles that include it."""
        stack: list[tuple[str, list[str]]] = [(start, [start])]
        while stack:
            node, path = stack.pop()
            for nxt in sorted(adj.get(node, [])):
                if nxt not in remaining:
                    continue
                if nxt == start and (len(path) > 1 or node == start):
                    # Found a cycle back to start.
                    # len(path)>1 handles normal cycles;
                    # node==start handles self-loops (start->start).
                    cycle = tuple(path)
                    # Normalize: rotate so the smallest element is first
                    min_idx = min(
                        range(len(cycle)), key=lambda i: cycle[i]
                    )
                    normalized = cycle[min_idx:] + cycle[:min_idx]
                    found.add(normalized)
                elif nxt not in path:
                    stack.append((nxt, path + [nxt]))

    for node in sorted(remaining):
        _dfs_from(node)

    return [list(c) for c in sorted(found)]


def _compute_topological_order(
    valid_nodes: set[str],
    adj: dict[str, list[str]],
    in_deg: dict[str, int],
) -> list[str]:
    """Kahn's algorithm for deterministic topological sort.

    Ties are broken by lexicographic step_id order.
    Returns only nodes reachable without cycles.
    """
    heap: list[str] = sorted(n for n in valid_nodes if in_deg[n] == 0)
    heapq.heapify(heap)
    local_in = {n: in_deg[n] for n in valid_nodes}
    result: list[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nxt in sorted(adj.get(node, [])):
            if nxt not in valid_nodes:
                continue
            local_in[nxt] -= 1
            if local_in[nxt] == 0:
                heapq.heappush(heap, nxt)

    return result


def _compute_depths(
    topo: list[str],
    adj: dict[str, list[str]],
    pred: dict[str, list[str]],
) -> dict[str, int]:
    """Compute depth (longest path from any root) for each node.

    Roots have depth 0; other nodes have depth = max(depth[p]) + 1
    over all predecessors *p*.
    """
    dist: dict[str, int] = {}
    for node in topo:
        preds = [p for p in pred.get(node, []) if p in dist]
        dist[node] = (max(dist[p] for p in preds) + 1) if preds else 0
    return dist


def _compute_critical_path(
    topo: list[str],
    pred: dict[str, list[str]],
    node_map: dict[str, DAGNode],
) -> tuple[list[str], int]:
    """Compute the critical (longest weighted) path through the DAG.

    Uses dynamic programming over topological order with timeout as weight.
    Returns (path as list of step_ids, total duration).
    """
    if not topo:
        return [], 0

    # dist[node] = longest weighted distance from any root to node (inclusive)
    dist: dict[str, int] = {}
    prev: dict[str, str | None] = {}

    for node in topo:
        preds = [p for p in pred.get(node, []) if p in dist]
        if preds:
            best_pred = max(preds, key=lambda p: dist[p])
            dist[node] = dist[best_pred] + node_map[node].timeout
            prev[node] = best_pred
        else:
            dist[node] = node_map[node].timeout
            prev[node] = None

    # Find the node at the end of the critical path
    end_node = max(dist, key=lambda n: dist[n])
    total_duration = dist[end_node]

    # Reconstruct the path by walking predecessors
    path: list[str] = []
    cur: str | None = end_node
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()

    return path, total_duration


def build_dag(dsl: ReproDSL) -> DAG:
    """Build a DAG from a ReproDSL specification.

    Performs:
    1. Node creation from steps
    2. Edge creation from needs dependencies
    3. Missing dependency detection
    4. Cycle detection (Kahn's algorithm)
    5. Topological sort
    6. Parallel group detection
    7. Critical path analysis
    """
    warnings: list[str] = []
    step_ids = set(dsl.steps.keys())

    # ---- 1. Create nodes ----
    nodes: dict[str, DAGNode] = {}
    for step_id in sorted(dsl.steps):
        step = dsl.steps[step_id]
        nodes[step_id] = DAGNode(
            step_id=step_id,
            command=step.command,
            needs=list(step.needs),
            produces=list(step.produces),
            timeout=step.timeout,
        )

    # ---- 2. Build edges & detect missing deps ----
    edges: list[tuple[str, str]] = []
    missing_deps: dict[str, list[str]] = {}
    # adj[step_id] = list of successor step_ids
    adj: dict[str, list[str]] = {sid: [] for sid in step_ids}
    # pred[step_id] = list of predecessor step_ids
    pred: dict[str, list[str]] = {sid: [] for sid in step_ids}
    # in-degree counts (only for edges whose source exists)
    in_deg: dict[str, int] = {sid: 0 for sid in step_ids}

    for step_id in sorted(dsl.steps):
        step = dsl.steps[step_id]
        for dep_id in step.needs:
            if dep_id not in step_ids:
                missing_deps.setdefault(step_id, []).append(dep_id)
                warnings.append(
                    f"Step '{step_id}' depends on non-existent step '{dep_id}'"
                )
            else:
                edges.append((dep_id, step_id))
                adj[dep_id].append(step_id)
                pred[step_id].append(dep_id)
                in_deg[step_id] += 1

    # Sort adjacency and predecessor lists for determinism
    for sid in adj:
        adj[sid].sort()
    for sid in pred:
        pred[sid].sort()

    # Set sorted in/out degrees on nodes
    for sid, node in nodes.items():
        node.in_degree = in_deg[sid]
        node.out_degree = len(adj[sid])

    # ---- 3. Cycle detection via Kahn's algorithm ----
    # Phase 1: peel away all nodes with in_degree == 0 (BFS).
    # Use a min-heap for deterministic (lexicographic) processing order.
    heap: list[str] = sorted(sid for sid in step_ids if in_deg[sid] == 0)
    heapq.heapify(heap)
    visited_kahn: set[str] = set()
    local_in = dict(in_deg)

    while heap:
        node_id = heapq.heappop(heap)
        visited_kahn.add(node_id)
        for nxt in adj[node_id]:
            local_in[nxt] -= 1
            if local_in[nxt] == 0:
                heapq.heappush(heap, nxt)

    remaining = step_ids - visited_kahn  # nodes involved in cycles

    if remaining:
        warnings.append(
            f"Cycle(s) detected involving {len(remaining)} step(s): "
            + ", ".join(sorted(remaining))
        )

    # ---- 4. Find actual cycle paths ----
    # Build adjacency restricted to remaining nodes for cycle path extraction.
    cycle_adj: dict[str, list[str]] = {}
    for sid in remaining:
        cycle_adj[sid] = [nxt for nxt in adj[sid] if nxt in remaining]

    cycles = _find_cycle_paths(remaining, cycle_adj)

    # ---- 5. Topological sort (acyclic nodes only) ----
    valid_nodes = step_ids - remaining
    topo = _compute_topological_order(valid_nodes, adj, in_deg)

    # ---- 6. Depth computation (longest path from any root) ----
    depths = _compute_depths(topo, adj, pred)

    # Nodes in cycles get depth = -1 to distinguish them.
    for sid in remaining:
        depths[sid] = -1

    # Apply depths to nodes
    for sid, node in nodes.items():
        node.depth = depths[sid]

    # ---- 7. Parallel groups (nodes sharing the same depth) ----
    depth_groups: dict[int, list[str]] = {}
    for sid in topo:
        d = depths[sid]
        depth_groups.setdefault(d, []).append(sid)

    parallel_groups: list[list[str]] = []
    for d in sorted(depth_groups):
        group = sorted(depth_groups[d])
        parallel_groups.append(group)

    # Assign level to each node (index of its parallel group)
    for level_idx, group in enumerate(parallel_groups):
        for sid in group:
            nodes[sid].level = level_idx

    # Nodes in cycles: assign level = -1
    for sid in remaining:
        nodes[sid].level = -1

    # ---- 8. Critical path (longest weighted path by timeout) ----
    critical_path, critical_path_duration = _compute_critical_path(
        topo, pred, nodes
    )

    if remaining:
        warnings.append(
            "Critical path excludes steps involved in cycles: "
            + ", ".join(sorted(remaining))
        )

    # ---- 9. Build and return DAG ----
    return DAG(
        nodes=nodes,
        edges=edges,
        topological_order=topo,
        parallel_groups=parallel_groups,
        critical_path=critical_path,
        critical_path_duration=critical_path_duration,
        cycles=cycles,
        missing_deps=missing_deps,
        warnings=warnings,
    )
