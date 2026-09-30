"""Anota dependencia técnica temporal sin crear puntuaciones ni sumar señales."""
from __future__ import annotations
from collections import defaultdict
from typing import Any, Mapping

FAMILY_CLUSTERS = {"TATACIR": "SLOW_SYMBOLIC_DIRECTIONS", "TDIR": "SLOW_SYMBOLIC_DIRECTIONS"}


def summarize_temporal_dependencies(signals: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Group same-root related directions as one recurrence unit, keeping signals."""
    if not isinstance(signals, list):
        raise ValueError("signals must be a list.")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    seen_ids: set[str] = set()
    for index, signal in enumerate(signals, start=1):
        if not isinstance(signal, Mapping):
            raise ValueError("each signal must be an object.")
        signal_id = signal.get("signal_id") or f"SIGNAL_{index:04d}"
        family = signal.get("temporal_family")
        root_id = signal.get("root_id")
        if not isinstance(signal_id, str) or not signal_id or signal_id in seen_ids:
            raise ValueError("signal_id must be non-empty and unique.")
        if not isinstance(family, str) or not family:
            raise ValueError("temporal_family is required.")
        if root_id is not None and (not isinstance(root_id, str) or not root_id):
            raise ValueError("root_id must be non-empty text or null.")
        seen_ids.add(signal_id)
        cluster = FAMILY_CLUSTERS.get(family, f"TEMPORAL_FAMILY:{family}")
        # Unanchored signals cannot create cross-signal recurrence evidence.
        root_key = root_id if root_id else f"UNANCHORED:{signal_id}"
        grouped[(root_key, cluster)].append({
            "signal_id": signal_id,
            "root_id": root_id,
            "temporal_family": family,
            "technique": signal.get("technique", family),
            "dependency_cluster": cluster,
        })
    units = []
    for (root, cluster), members in sorted(grouped.items()):
        units.append({
            "root_id": None if root.startswith("UNANCHORED:") else root,
            "dependency_cluster": cluster,
            "member_signal_ids": sorted(item["signal_id"] for item in members),
            "techniques": sorted({str(item["technique"]) for item in members}),
            "temporal_families": sorted({item["temporal_family"] for item in members}),
            "independent_unit_count": 1,
        })
    return {
        "policy_id": "ALMAS_TEMPORAL_DEPENDENCY_POLICY_V1",
        "signals": [item for _, members in sorted(grouped.items()) for item in members],
        "dependency_units": units,
        "score_created": False,
        "legacy_iat_modified": False,
    }
