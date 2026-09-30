"""Anota dependencia técnica temporal sin crear puntuaciones ni sumar señales."""
from __future__ import annotations
from collections import defaultdict
from typing import Any, Mapping

FAMILY_CLUSTERS = {"TATACIR": "SLOW_SYMBOLIC_DIRECTIONS", "TDIR": "SLOW_SYMBOLIC_DIRECTIONS"}


def summarize_temporal_dependencies(signals: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Group same-root related directions as one recurrence unit, keeping signals."""
    if not isinstance(signals, list):
        raise ValueError("signals must be a list.")
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    explicit_v2 = any(
        isinstance(signal, Mapping)
        and any(key in signal for key in ("dependency_group", "technique_variant", "node_variant", "nodal_axis_id"))
        for signal in signals
    )
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
        declared_group = signal.get("dependency_group")
        if declared_group is not None and (not isinstance(declared_group, str) or not declared_group.strip()):
            raise ValueError("dependency_group must be non-empty text or null.")
        cluster = declared_group or FAMILY_CLUSTERS.get(family, f"TEMPORAL_FAMILY:{family}")
        nodal_axis_id = signal.get("nodal_axis_id")
        node_variant = signal.get("node_variant")
        if nodal_axis_id is not None and (not isinstance(nodal_axis_id, str) or not nodal_axis_id):
            raise ValueError("nodal_axis_id must be non-empty text or null.")
        if node_variant is not None and node_variant not in {"TRUE", "MEAN"}:
            raise ValueError("node_variant must be TRUE, MEAN or null.")
        if node_variant and not nodal_axis_id:
            raise ValueError("node_variant requires nodal_axis_id for deduplication.")
        # Unanchored signals cannot create cross-signal recurrence evidence.
        root_key = root_id if root_id else f"UNANCHORED:{signal_id}"
        axis_key = nodal_axis_id or "NO_NODAL_AXIS"
        grouped[(root_key, cluster, axis_key)].append({
            "signal_id": signal_id,
            "root_id": root_id,
            "temporal_family": family,
            "technique": signal.get("technique", family),
            "dependency_cluster": cluster,
            "technique_variant": signal.get("technique_variant"),
            "node_variant": node_variant,
            "nodal_axis_id": nodal_axis_id,
        })
    units = []
    for (root, cluster, axis_key), members in sorted(grouped.items()):
        serialized = []
        for item in members:
            signal = {key: item[key] for key in ("signal_id", "root_id", "temporal_family", "technique", "dependency_cluster")}
            for optional in ("technique_variant", "node_variant", "nodal_axis_id"):
                if item[optional] is not None:
                    signal[optional] = item[optional]
            serialized.append(signal)
        units.append({
            "root_id": None if root.startswith("UNANCHORED:") else root,
            "dependency_cluster": cluster,
            **({"nodal_axis_id": axis_key} if axis_key != "NO_NODAL_AXIS" else {}),
            "member_signal_ids": sorted(item["signal_id"] for item in members),
            "techniques": sorted({str(item["technique"]) for item in members}),
            "technique_variants": sorted({str(item["technique_variant"]) for item in members if item["technique_variant"]}),
            "node_variants": sorted({str(item["node_variant"]) for item in members if item["node_variant"]}),
            "temporal_families": sorted({item["temporal_family"] for item in members}),
            "independent_unit_count": 1,
        })
    return {
        "policy_id": "ALMAS_TEMPORAL_DEPENDENCY_POLICY_V2" if explicit_v2 else "ALMAS_TEMPORAL_DEPENDENCY_POLICY_V1",
        "signals": [
            {key: item[key] for key in ("signal_id", "root_id", "temporal_family", "technique", "dependency_cluster")}
            | {optional: item[optional] for optional in ("technique_variant", "node_variant", "nodal_axis_id") if item[optional] is not None}
            for _, members in sorted(grouped.items()) for item in members
        ],
        "dependency_units": units,
        "score_created": False,
        "legacy_iat_modified": False,
    }
