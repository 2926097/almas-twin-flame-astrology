"""Grafo cronológico descriptivo; no completa fases ausentes ni infiere causa."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Mapping

NODE_KINDS = ("EVENT", "ACTIVATION", "ROOT", "PHASE")
EDGE_KINDS = {
    ("EVENT", "ACTIVATION"),
    ("ACTIVATION", "ROOT"),
    ("ROOT", "PHASE"),
}


def build_temporal_sequence_graph(
    nodes: list[Mapping[str, Any]], edges: list[Mapping[str, Any]]
) -> dict[str, Any]:
    """Validate a caller-supplied EVENT→ACTIVATION→ROOT→PHASE graph.

    Nodes and edges are retained only when the caller supplies evidence refs.
    The function never invents intermediate nodes or interprets graph edges as
    causal relations.
    """
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("nodes and edges must be lists.")
    normalized_nodes: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, Mapping):
            raise ValueError("each node must be an object.")
        node_id, kind = node.get("node_id"), node.get("kind")
        refs = node.get("evidence_refs")
        if not isinstance(node_id, str) or not node_id.strip() or node_id in by_id:
            raise ValueError("node_id must be non-empty and unique.")
        if kind not in NODE_KINDS:
            raise ValueError(f"{node_id}: unsupported node kind.")
        if not isinstance(refs, list) or not refs or not all(
            isinstance(ref, str) and ref.strip() for ref in refs
        ):
            raise ValueError(f"{node_id}: evidence_refs must be non-empty.")
        item = {"node_id": node_id, "kind": kind, "evidence_refs": sorted(set(refs))}
        by_id[node_id] = item
        normalized_nodes.append(item)

    normalized_edges: list[dict[str, Any]] = []
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in by_id}
    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, Mapping):
            raise ValueError("each edge must be an object.")
        source, target = edge.get("source_id"), edge.get("target_id")
        refs = edge.get("evidence_refs")
        if source not in by_id or target not in by_id:
            raise ValueError("edge endpoints must reference declared nodes.")
        if (by_id[source]["kind"], by_id[target]["kind"]) not in EDGE_KINDS:
            raise ValueError("edge must follow EVENT→ACTIVATION→ROOT→PHASE order.")
        if (source, target) in seen_edges:
            raise ValueError("duplicate graph edge.")
        if not isinstance(refs, list) or not refs or not all(
            isinstance(ref, str) and ref.strip() for ref in refs
        ):
            raise ValueError("edge evidence_refs must be non-empty.")
        seen_edges.add((source, target))
        adjacency[source].append(target)
        indegree[target] += 1
        normalized_edges.append({
            "source_id": source,
            "target_id": target,
            "evidence_refs": sorted(set(refs)),
        })

    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for target in adjacency[current]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(by_id):
        raise ValueError("temporal sequence graph must be acyclic.")

    normalized_nodes.sort(key=lambda item: item["node_id"])
    normalized_edges.sort(key=lambda item: (item["source_id"], item["target_id"]))
    return {
        "status": "READY" if normalized_nodes else "NOT_EVALUABLE",
        "nodes": normalized_nodes,
        "edges": normalized_edges,
        "unresolved": [] if normalized_nodes else ["No evidence-backed graph nodes were supplied."],
        "missing_phases_inferred": False,
        "causal_status": "UNESTABLISHED",
    }
