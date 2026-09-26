from __future__ import annotations

from copy import deepcopy
from importlib import resources
import json
from typing import Any, Mapping, Sequence

from .recurrence_quality import (
    derive_recurrence_quality_diagnostics,
    load_recurrence_quality_policy,
)
from .semantic_motifs import (
    derive_semantic_motif_graph,
    load_semantic_motif_policy,
)


POLICY_RESOURCE = "recurrence-synthetic-controls-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_recurrence_synthetic_controls_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        POLICY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1":
        raise ValueError("Política de controles sintéticos desconocida.")
    return policy


def _core_roots(roots: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for root in roots:
        if not isinstance(root, Mapping):
            continue
        if not bool(root.get("core_eligible")):
            continue
        if root.get("strength_state") != "CALCULATED_CORE":
            continue
        root_id = str(root.get("root_id") or "")
        if not root_id:
            continue
        output.append(deepcopy(dict(root)))
    output.sort(key=lambda item: str(item.get("root_id")))
    return output


def _control_count(root_count: int, maximum: int) -> int:
    if root_count <= 1:
        return 0
    return min(int(maximum), root_count - 1)


def _semantic_payload(root: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "point_ids": list(root.get("point_ids", [])),
        "relation_ids": list(root.get("relation_ids", [])),
        "source_root_id": str(root.get("root_id") or ""),
    }


def _rotated_root(
    target: Mapping[str, Any],
    *,
    points_source: Mapping[str, Any],
    relations_source: Mapping[str, Any],
    control_id: str,
) -> dict[str, Any]:
    root = deepcopy(dict(target))
    root["point_ids"] = list(points_source.get("point_ids", []))
    root["relation_ids"] = list(relations_source.get("relation_ids", []))
    root["root_key"] = (
        "SYNTHETIC:"
        + control_id
        + ":"
        + str(target.get("root_id") or "")
    )
    root["synthetic_control"] = True
    root["synthetic_points_source_root_id"] = str(
        points_source.get("root_id") or ""
    )
    root["synthetic_relations_source_root_id"] = str(
        relations_source.get("root_id") or ""
    )
    return root


def _build_control_roots(
    roots: Sequence[Mapping[str, Any]],
    *,
    family_id: str,
    shift: int,
) -> list[dict[str, Any]]:
    n = len(roots)
    if n <= 1:
        return []

    output = []
    if family_id == "SEMANTIC_SIGNATURE_ROTATION":
        for index, target in enumerate(roots):
            source = roots[(index + shift) % n]
            output.append(
                _rotated_root(
                    target,
                    points_source=source,
                    relations_source=source,
                    control_id=f"{family_id}:{shift}",
                )
            )
        return output

    if family_id == "DECOUPLED_POINT_RELATION_ROTATION":
        relation_shift = (2 * shift + 1) % n
        if relation_shift == 0:
            relation_shift = 1
        if relation_shift == shift and n > 2:
            relation_shift = (relation_shift + 1) % n
            if relation_shift == 0:
                relation_shift = 1

        for index, target in enumerate(roots):
            points_source = roots[(index + shift) % n]
            relations_source = roots[(index + relation_shift) % n]
            output.append(
                _rotated_root(
                    target,
                    points_source=points_source,
                    relations_source=relations_source,
                    control_id=f"{family_id}:{shift}:{relation_shift}",
                )
            )
        return output

    raise ValueError(f"Familia de control desconocida: {family_id}")


def _snapshot(
    roots: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    semantic_policy = load_semantic_motif_policy()
    graph = derive_semantic_motif_graph(
        roots,
        policy=semantic_policy,
    )
    quality = derive_recurrence_quality_diagnostics(
        roots,
        graph,
        semantic_policy=semantic_policy,
        quality_policy=load_recurrence_quality_policy(),
    )
    return {
        "semantic_motifs": graph,
        "recurrence_quality": quality,
    }


def _summary(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    graph = snapshot["semantic_motifs"]
    quality = snapshot["recurrence_quality"]

    primary_quality = {
        str(item.get("motif_id")): item
        for item in quality.get("primary_motifs", [])
        if isinstance(item, Mapping)
    }
    mission_quality = {
        str(item.get("motif_id")): item
        for item in quality.get("mission_motifs", [])
        if isinstance(item, Mapping)
    }

    motifs = {}
    for motif_type, items, quality_map in (
        (
            "PRIMARY",
            graph.get("recurrent_primary_motifs", []),
            primary_quality,
        ),
        (
            "MISSION",
            graph.get("recurrent_mission_motifs", []),
            mission_quality,
        ),
    ):
        for item in items:
            if not isinstance(item, Mapping):
                continue
            motif_id = str(item.get("motif_id") or "")
            if not motif_id:
                continue
            q = quality_map.get(motif_id, {})
            motifs[motif_id] = {
                "motif_type": motif_type,
                "motif_strength": float(item.get("motif_strength", 0.0)),
                "family_count": int(item.get("independent_family_count", 0)),
                "cross_class_recurrence": bool(
                    q.get("cross_class_recurrence", False)
                ),
                "non_draconic_recurrence": bool(
                    q.get("non_draconic_recurrence", False)
                ),
            }

    return {
        "px_score": float(graph.get("px", {}).get("score", 0.0)),
        "ps_score": float(graph.get("ps", {}).get("score", 0.0)),
        "primary_recurrent_motif_count": int(
            graph.get("px", {}).get("recurrent_motif_count", 0)
        ),
        "mission_recurrent_motif_count": int(
            graph.get("ps", {}).get("recurrent_motif_count", 0)
        ),
        "motifs": motifs,
    }


def _frequency(count: int, n: int) -> dict[str, Any]:
    return {
        "count": int(count),
        "n": int(n),
        "frequency": (count / n) if n else None,
        "interpretation_scope": "FINITE_DETERMINISTIC_CONTROL_FAMILY_FREQUENCY",
    }


def _aggregate(
    observed: Mapping[str, Any],
    controls: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    n = len(controls)
    if n == 0:
        return {}

    return {
        "PX_SCORE": _frequency(
            sum(
                float(item["summary"]["px_score"])
                >= float(observed["px_score"])
                for item in controls
            ),
            n,
        ),
        "PS_SCORE": _frequency(
            sum(
                float(item["summary"]["ps_score"])
                >= float(observed["ps_score"])
                for item in controls
            ),
            n,
        ),
        "PRIMARY_RECURRENT_MOTIF_COUNT": _frequency(
            sum(
                int(item["summary"]["primary_recurrent_motif_count"])
                >= int(observed["primary_recurrent_motif_count"])
                for item in controls
            ),
            n,
        ),
        "MISSION_RECURRENT_MOTIF_COUNT": _frequency(
            sum(
                int(item["summary"]["mission_recurrent_motif_count"])
                >= int(observed["mission_recurrent_motif_count"])
                for item in controls
            ),
            n,
        ),
    }


def _motif_calibration(
    observed: Mapping[str, Any],
    controls: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    n = len(controls)
    output = []

    for motif_id, obs in sorted(observed.get("motifs", {}).items()):
        present = []
        for control in controls:
            item = control["summary"]["motifs"].get(motif_id)
            if isinstance(item, Mapping):
                present.append(item)

        presence_count = len(present)
        strength_count = sum(
            float(item["motif_strength"])
            >= float(obs["motif_strength"])
            for item in present
        )
        cross_class_count = sum(
            bool(item["cross_class_recurrence"]) for item in present
        )
        non_draconic_count = sum(
            bool(item["non_draconic_recurrence"]) for item in present
        )

        output.append(
            {
                "motif_id": motif_id,
                "motif_type": obs["motif_type"],
                "observed_strength": float(obs["motif_strength"]),
                "presence": _frequency(presence_count, n),
                "strength_ge_observed_unconditional": _frequency(
                    strength_count,
                    n,
                ),
                "strength_ge_observed_conditional": _frequency(
                    strength_count,
                    presence_count,
                ),
                "cross_class_recurrence": _frequency(
                    cross_class_count,
                    n,
                ),
                "non_draconic_recurrence": _frequency(
                    non_draconic_count,
                    n,
                ),
            }
        )

    return output


def derive_recurrence_synthetic_controls(
    roots: Sequence[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Genera controles sintéticos deterministas, sin alterar scoring real."""

    if policy is None:
        policy = load_recurrence_synthetic_controls_policy()

    core = _core_roots(roots)
    minimum = int(policy["minimum_core_roots"])
    if len(core) < minimum:
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": policy["policy_id"],
            "reason": (
                f"Se requieren al menos {minimum} raíces core; "
                f"disponibles={len(core)}."
            ),
            "used_for_weighting": False,
            "used_in_px_score": False,
            "used_in_ps_score": False,
            "used_in_iem": False,
            "used_in_idd": False,
            "used_in_irc": False,
            "used_in_ontology": False,
            "metaphysical_probability": False,
            "population_probability_claim": False,
        }

    observed_snapshot = _snapshot(core)
    observed = _summary(observed_snapshot)
    count = _control_count(
        len(core),
        int(policy["max_controls_per_family"]),
    )

    controls = []
    for family_spec in policy["control_families"]:
        family_id = str(family_spec["id"])
        for shift in range(1, count + 1):
            synthetic_roots = _build_control_roots(
                core,
                family_id=family_id,
                shift=shift,
            )
            snap = _snapshot(synthetic_roots)
            controls.append(
                {
                    "control_id": f"{family_id}:{shift}",
                    "control_family": family_id,
                    "shift": shift,
                    "summary": _summary(snap),
                }
            )

    by_family = {}
    for family_spec in policy["control_families"]:
        family_id = str(family_spec["id"])
        family_controls = [
            item for item in controls
            if item["control_family"] == family_id
        ]
        by_family[family_id] = {
            "control_count": len(family_controls),
            "aggregate": _aggregate(observed, family_controls),
            "motifs": _motif_calibration(observed, family_controls),
        }

    return {
        "state": "DIAGNOSTIC_ONLY",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "core_root_count": len(core),
        "controls_per_family": count,
        "control_count": len(controls),
        "observed": observed,
        "aggregate": _aggregate(observed, controls),
        "motifs": _motif_calibration(observed, controls),
        "by_control_family": by_family,
        "control_manifest": [
            {
                "control_id": item["control_id"],
                "control_family": item["control_family"],
                "shift": item["shift"],
                "px_score": item["summary"]["px_score"],
                "ps_score": item["summary"]["ps_score"],
                "primary_recurrent_motif_count": item["summary"][
                    "primary_recurrent_motif_count"
                ],
                "mission_recurrent_motif_count": item["summary"][
                    "mission_recurrent_motif_count"
                ],
            }
            for item in controls
        ],
        "deterministic": True,
        "rng_used": False,
        "used_for_weighting": False,
        "used_in_px_score": False,
        "used_in_ps_score": False,
        "used_in_iem": False,
        "used_in_idd": False,
        "used_in_irc": False,
        "used_in_ontology": False,
        "metaphysical_probability": False,
        "population_probability_claim": False,
        "p_value_claim": False,
        "external_nulls_required_before_weighting": True,
    }
