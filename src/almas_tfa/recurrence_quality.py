from __future__ import annotations

from collections import defaultdict
from importlib import resources
import json
from math import exp, log
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "recurrence-quality-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_recurrence_quality_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1":
        raise ValueError("Política de calidad de recurrencia desconocida.")
    return policy


def _family_strengths(root: Mapping[str, Any]) -> dict[str, float]:
    """Fuerza core máxima por familia; support-only queda fuera."""

    raw = root.get("evidence_strengths")
    output: dict[str, float] = {}
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            if not bool(item.get("core_eligible")):
                continue
            if bool(item.get("support_only")):
                continue
            family = str(item.get("dependency_family") or "")
            value = item.get("strength")
            if (
                not family
                or isinstance(value, bool)
                or not isinstance(value, (int, float))
            ):
                continue
            value = float(value)
            if not 0.0 <= value <= 1.0:
                continue
            output[family] = max(output.get(family, 0.0), value)

    if output:
        return output

    if not bool(root.get("core_eligible")):
        return {}
    if root.get("strength_state") != "CALCULATED_CORE":
        return {}

    value = root.get("strength")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return {}
    value = float(value)
    if not 0.0 <= value <= 1.0:
        return {}

    families = root.get("dependency_families")
    if not isinstance(families, list):
        return {}
    return {
        str(family): value
        for family in families
        if str(family)
    }


def _family_class(
    family: str,
    *,
    policy: Mapping[str, Any],
) -> str:
    mapping = policy.get("family_classes")
    if isinstance(mapping, Mapping) and family in mapping:
        return str(mapping[family])

    mode = str(policy.get("unknown_core_family_mode") or "")
    if mode == "OWN_CLASS":
        return "OTHER:" + family
    return "UNKNOWN"


def _recurrence_state(
    roots: Sequence[Mapping[str, Any]],
    *,
    excluded_families: set[str],
    semantic_policy: Mapping[str, Any],
) -> dict[str, Any]:
    family_maxima: dict[str, float] = {}
    surviving_root_ids: list[str] = []
    exact_multifamily = False

    for root in roots:
        if not isinstance(root, Mapping):
            continue
        strengths = {
            family: value
            for family, value in _family_strengths(root).items()
            if family not in excluded_families
        }
        if not strengths:
            continue

        root_id = str(root.get("root_id") or "")
        if root_id:
            surviving_root_ids.append(root_id)
        if len(strengths) >= 2:
            exact_multifamily = True

        for family, value in strengths.items():
            family_maxima[family] = max(
                family_maxima.get(family, 0.0),
                value,
            )

    limits = semantic_policy["minimum_recurrence"]
    family_count = len(family_maxima)
    root_count = len(set(surviving_root_ids))
    recurrent = (
        family_count >= int(limits["distinct_dependency_families"])
        and (
            root_count >= int(limits["distinct_roots"])
            or (
                bool(limits["allow_single_exact_root_when_multifamily"])
                and exact_multifamily
            )
        )
    )

    return {
        "recurrent": recurrent,
        "family_count": family_count,
        "root_count": root_count,
        "family_strengths": {
            key: family_maxima[key]
            for key in sorted(family_maxima)
        },
    }


def _entropy_metrics(values: Sequence[float]) -> tuple[float, float, float]:
    clean = [float(value) for value in values if float(value) > 0.0]
    if not clean:
        return 0.0, 0.0, 0.0

    total = sum(clean)
    probabilities = [value / total for value in clean]
    raw_entropy = -sum(p * log(p) for p in probabilities)
    if len(clean) <= 1:
        normalized = 0.0
    else:
        normalized = raw_entropy / log(len(clean))
    effective = exp(raw_entropy)
    dominance = max(probabilities)
    return normalized, effective, dominance


def _motif_roots(
    roots_by_id: Mapping[str, Mapping[str, Any]],
    motif_record: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    output = []
    for root_id in motif_record.get("root_ids", []):
        root = roots_by_id.get(str(root_id))
        if isinstance(root, Mapping):
            output.append(root)
    return output


def _diagnose_motif(
    motif_record: Mapping[str, Any],
    roots: Sequence[Mapping[str, Any]],
    *,
    semantic_policy: Mapping[str, Any],
    quality_policy: Mapping[str, Any],
) -> dict[str, Any]:
    baseline = _recurrence_state(
        roots,
        excluded_families=set(),
        semantic_policy=semantic_policy,
    )
    strengths = list(baseline["family_strengths"].values())
    entropy, effective_count, dominance = _entropy_metrics(strengths)

    families = sorted(baseline["family_strengths"])
    family_classes = sorted(
        {
            _family_class(family, policy=quality_policy)
            for family in families
        }
    )

    leave_family = {}
    for family in families:
        state = _recurrence_state(
            roots,
            excluded_families={family},
            semantic_policy=semantic_policy,
        )
        leave_family[family] = {
            "recurrent": bool(state["recurrent"]),
            "remaining_family_count": int(state["family_count"]),
            "remaining_root_count": int(state["root_count"]),
        }

    class_to_families: dict[str, set[str]] = defaultdict(set)
    for family in families:
        class_to_families[
            _family_class(family, policy=quality_policy)
        ].add(family)

    leave_class = {}
    for class_id in sorted(class_to_families):
        state = _recurrence_state(
            roots,
            excluded_families=set(class_to_families[class_id]),
            semantic_policy=semantic_policy,
        )
        leave_class[class_id] = {
            "excluded_families": sorted(class_to_families[class_id]),
            "recurrent": bool(state["recurrent"]),
            "remaining_family_count": int(state["family_count"]),
            "remaining_root_count": int(state["root_count"]),
        }

    non_draconic = _recurrence_state(
        roots,
        excluded_families={"NATAL_DRACONIC"},
        semantic_policy=semantic_policy,
    )

    family_survival_fraction = (
        sum(1 for item in leave_family.values() if item["recurrent"])
        / len(leave_family)
        if leave_family
        else 0.0
    )
    class_survival_fraction = (
        sum(1 for item in leave_class.values() if item["recurrent"])
        / len(leave_class)
        if leave_class
        else 0.0
    )

    return {
        "motif_id": str(motif_record.get("motif_id") or ""),
        "motif_type": str(motif_record.get("motif_type") or ""),
        "baseline_recurrent": bool(baseline["recurrent"]),
        "root_count": int(baseline["root_count"]),
        "dependency_families": families,
        "family_count": int(baseline["family_count"]),
        "family_classes": family_classes,
        "family_class_count": len(family_classes),
        "cross_class_recurrence": len(family_classes) >= 2,
        "family_strength_entropy": entropy,
        "effective_family_count": effective_count,
        "family_dominance_share": dominance,
        "includes_natal_draconic": "NATAL_DRACONIC" in families,
        "non_draconic_recurrence": bool(non_draconic["recurrent"]),
        "non_draconic_family_count": int(non_draconic["family_count"]),
        "non_draconic_root_count": int(non_draconic["root_count"]),
        "leave_one_family_out": leave_family,
        "leave_one_family_out_survival_fraction": family_survival_fraction,
        "leave_one_class_out": leave_class,
        "leave_one_class_out_survival_fraction": class_survival_fraction,
    }


def _aggregate(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not items:
        return {
            "motif_count": 0,
            "cross_class_recurrent_count": 0,
            "non_draconic_recurrent_count": 0,
            "all_include_natal_draconic": False,
            "all_fail_without_natal_draconic": False,
            "mean_family_strength_entropy": None,
            "mean_effective_family_count": None,
            "mean_leave_one_family_out_survival_fraction": None,
            "mean_leave_one_class_out_survival_fraction": None,
        }

    count = len(items)
    return {
        "motif_count": count,
        "cross_class_recurrent_count": sum(
            1 for item in items if item["cross_class_recurrence"]
        ),
        "non_draconic_recurrent_count": sum(
            1 for item in items if item["non_draconic_recurrence"]
        ),
        "all_include_natal_draconic": all(
            item["includes_natal_draconic"] for item in items
        ),
        "all_fail_without_natal_draconic": all(
            not item["non_draconic_recurrence"] for item in items
        ),
        "mean_family_strength_entropy": sum(
            float(item["family_strength_entropy"]) for item in items
        ) / count,
        "mean_effective_family_count": sum(
            float(item["effective_family_count"]) for item in items
        ) / count,
        "mean_leave_one_family_out_survival_fraction": sum(
            float(item["leave_one_family_out_survival_fraction"])
            for item in items
        ) / count,
        "mean_leave_one_class_out_survival_fraction": sum(
            float(item["leave_one_class_out_survival_fraction"])
            for item in items
        ) / count,
    }


def derive_recurrence_quality_diagnostics(
    roots: Sequence[Mapping[str, Any]],
    motif_graph: Mapping[str, Any],
    *,
    semantic_policy: Mapping[str, Any],
    quality_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Diagnóstico descriptivo de recurrencia.

    Este bloque no modifica PX/PS ni ningún índice. Su finalidad es exponer
    dependencia de familias, diversidad técnica y fragilidad leave-one-out.
    """

    if quality_policy is None:
        quality_policy = load_recurrence_quality_policy()

    roots_by_id = {
        str(root.get("root_id")): root
        for root in roots
        if isinstance(root, Mapping) and str(root.get("root_id") or "")
    }

    primary = []
    for item in motif_graph.get("recurrent_primary_motifs", []):
        if not isinstance(item, Mapping):
            continue
        primary.append(
            _diagnose_motif(
                item,
                _motif_roots(roots_by_id, item),
                semantic_policy=semantic_policy,
                quality_policy=quality_policy,
            )
        )

    mission = []
    for item in motif_graph.get("recurrent_mission_motifs", []):
        if not isinstance(item, Mapping):
            continue
        mission.append(
            _diagnose_motif(
                item,
                _motif_roots(roots_by_id, item),
                semantic_policy=semantic_policy,
                quality_policy=quality_policy,
            )
        )

    return {
        "policy_id": quality_policy["policy_id"],
        "policy_status": quality_policy["status"],
        "epistemic_class": quality_policy["epistemic_class"],
        "state": "DESCRIPTIVE_ONLY",
        "primary_motifs": primary,
        "mission_motifs": mission,
        "px_diagnostics": _aggregate(primary),
        "ps_diagnostics": _aggregate(mission),
        "used_in_px_score": False,
        "used_in_ps_score": False,
        "used_in_iem": False,
        "used_in_idd": False,
        "used_in_irc": False,
        "used_in_ontology": False,
        "population_specificity_claim": False,
        "null_calibration_required_before_weighting": True,
    }
