from __future__ import annotations

import json
from importlib import resources
from typing import Any, Mapping, Sequence

from .core import pillar_score


POLICY_RESOURCE = "root-pillar-attribution-policy.json"
POLICY_PACKAGE = "almas_tfa"
PILLARS = ("PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU")


def load_root_pillar_policy() -> dict[str, Any]:
    """Carga la política canónica congelada de atribución raíz→pilar."""

    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_ROOT_PILLAR_ATTRIBUTION_V1":
        raise ValueError("Política raíz→pilar desconocida o no congelada.")
    return policy


def _norm(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_").replace("-", "_")


def _set(policy: Mapping[str, Any], group: str, name: str) -> set[str]:
    container = policy.get(group)
    if not isinstance(container, Mapping):
        raise ValueError(f"{group} debe ser un objeto.")
    raw = container.get(name)
    if not isinstance(raw, list):
        raise ValueError(f"{group}.{name} debe ser una lista.")
    return {_norm(item) for item in raw}


def _root_points(root: Mapping[str, Any]) -> list[str]:
    raw = root.get("point_ids")
    if not isinstance(raw, list):
        return []
    return [_norm(item) for item in raw if str(item).strip()]


def _root_relations(root: Mapping[str, Any]) -> set[str]:
    raw = root.get("relation_ids")
    if not isinstance(raw, list):
        return set()
    return {_norm(item) for item in raw if str(item).strip()}


def _other_point_matches(
    points: Sequence[str],
    anchor_set: set[str],
    counterpart_set: set[str],
) -> bool:
    for index, point in enumerate(points):
        if point not in anchor_set:
            continue
        others = list(points[:index]) + list(points[index + 1 :])
        if any(other in counterpart_set for other in others):
            return True
    return False


def _at_least(points: Sequence[str], allowed: set[str], count: int) -> bool:
    return sum(1 for point in points if point in allowed) >= count


def _matches_primary(
    rule_id: str,
    root: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    points = _root_points(root)
    relations = _root_relations(root)
    family_count = int(root.get("independent_family_count") or 0)

    point_sets = policy["point_sets"]
    relation_sets = policy["relation_sets"]

    if rule_id == "PS_MISSION_SERVICE":
        mission = {_norm(v) for v in point_sets["MISSION_ANCHOR"]}
        return (
            family_count >= 2
            and "AXIS_MERIDIAN" in points
            and _other_point_matches(
                points,
                {"AXIS_MERIDIAN"},
                mission,
            )
        )

    if rule_id == "PK_KARMIC_CONTINUITY":
        karmic = {_norm(v) for v in point_sets["KARMIC_ANCHOR"]}
        counterpart = {
            _norm(v) for v in point_sets["MEANINGFUL_COUNTERPART"]
        }
        return _other_point_matches(points, karmic, counterpart)

    if rule_id == "PT_TRANSFORMATION":
        transformation = {
            _norm(v) for v in point_sets["TRANSFORMATION_ANCHOR"]
        }
        counterpart = {
            _norm(v) for v in point_sets["MEANINGFUL_COUNTERPART"]
        }
        return _other_point_matches(points, transformation, counterpart)

    if rule_id == "PE_MIRROR_COMPLEMENTARITY":
        mirror = {_norm(v) for v in relation_sets["MIRROR_HARD"]}
        counterpart = {
            _norm(v) for v in point_sets["MEANINGFUL_COUNTERPART"]
        }
        return bool(relations & mirror) and _at_least(points, counterpart, 2)

    if rule_id == "PR_RELATIONAL_COHERENCE":
        coherent = {_norm(v) for v in relation_sets["COHERENT"]}
        relational = {
            _norm(v) for v in point_sets["PERSONAL_RELATIONAL"]
        }
        if not relations & coherent:
            return False
        return (
            _other_point_matches(points, {"MERCURY"}, relational)
            or _other_point_matches(points, {"AXIS_HORIZON"}, relational)
        )

    if rule_id == "PA_STRUCTURAL_AFFINITY":
        affinity = {_norm(v) for v in point_sets["AFFINITY"]}
        return _at_least(points, affinity, 2)

    raise ValueError(f"Regla raíz→pilar desconocida: {rule_id}")


def classify_root(
    root: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Clasifica una raíz core en un único pilar semántico primario.

    PX puede añadirse como propiedad ortogonal de recurrencia. PU permanece
    NOT_EVALUABLE en la baseline v1.
    """

    if policy is None:
        policy = load_root_pillar_policy()

    root_id = str(root.get("root_id") or "")
    strength = root.get("strength")

    if not bool(root.get("core_eligible")):
        return {
            "root_id": root_id,
            "eligible": False,
            "reason": "NOT_CORE_ELIGIBLE",
            "primary_pillar": None,
            "loadings": {},
            "normalized_loadings": {},
            "contributions": {},
        }

    if root.get("strength_state") != "CALCULATED_CORE":
        return {
            "root_id": root_id,
            "eligible": False,
            "reason": "ROOT_STRENGTH_NOT_CORE_CALCULATED",
            "primary_pillar": None,
            "loadings": {},
            "normalized_loadings": {},
            "contributions": {},
        }

    if isinstance(strength, bool) or not isinstance(strength, (int, float)):
        return {
            "root_id": root_id,
            "eligible": False,
            "reason": "ROOT_STRENGTH_NOT_EVALUABLE",
            "primary_pillar": None,
            "loadings": {},
            "normalized_loadings": {},
            "contributions": {},
        }

    strength = float(strength)
    if not 0.0 <= strength <= 1.0:
        raise ValueError(f"{root_id}: strength debe estar en [0,1].")

    primary = None
    matched_rule = None
    for rule_id in policy["primary_rule_order"]:
        if _matches_primary(rule_id, root, policy):
            primary = str(policy["rules"][rule_id]["pillar"])
            matched_rule = rule_id
            break

    if primary is None:
        return {
            "root_id": root_id,
            "eligible": False,
            "reason": "NO_SEMANTIC_RULE_MATCH",
            "primary_pillar": None,
            "loadings": {},
            "normalized_loadings": {},
            "contributions": {},
        }

    recurrence = policy["recurrence_rule"]
    recurrent = int(root.get("independent_family_count") or 0) >= int(
        recurrence["requires_independent_family_count_at_least"]
    )

    if recurrent:
        raw_loadings = {
            primary: float(recurrence["raw_loading_semantic"]),
            "PX": float(recurrence["raw_loading_recurrence"]),
        }
    else:
        raw_loadings = {primary: 1.0}

    total = sum(raw_loadings.values())
    if total <= 0.0 or total > 1.0 + 1e-12:
        raise ValueError(
            f"{root_id}: las cargas brutas deben cumplir 0 < sum(loadings) <= 1."
        )

    maximum = max(raw_loadings.values())
    normalized = {
        pillar: value / maximum
        for pillar, value in raw_loadings.items()
    }
    contributions = {
        pillar: strength * value
        for pillar, value in normalized.items()
    }

    return {
        "root_id": root_id,
        "eligible": True,
        "reason": None,
        "matched_rule": matched_rule,
        "primary_pillar": primary,
        "recurrent": recurrent,
        "loadings": raw_loadings,
        "normalized_loadings": normalized,
        "contributions": contributions,
        "strength": strength,
        "point_ids": list(_root_points(root)),
        "relation_ids": sorted(_root_relations(root)),
        "independent_family_count": int(
            root.get("independent_family_count") or 0
        ),
    }


def derive_pillars_from_roots(
    roots: Sequence[Mapping[str, Any]],
    *,
    structural_absence_is_zero: bool,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Deriva raíces por pilar y puntuaciones M18 sin entrada manual."""

    if policy is None:
        policy = load_root_pillar_policy()

    root_attributions = [
        classify_root(root, policy=policy)
        for root in roots
        if isinstance(root, Mapping)
    ]

    strengths: dict[str, list[float]] = {pillar: [] for pillar in PILLARS}
    root_ids: dict[str, list[str]] = {pillar: [] for pillar in PILLARS}

    for item in root_attributions:
        if not item.get("eligible"):
            continue
        for pillar, contribution in item["contributions"].items():
            if pillar == "PU":
                continue
            strengths[pillar].append(float(contribution))
            root_ids[pillar].append(str(item["root_id"]))

    pillars: dict[str, float | None] = {}
    for pillar in PILLARS:
        if pillar == "PU":
            pillars[pillar] = None
            continue
        values = strengths[pillar]
        if values:
            pillars[pillar] = pillar_score(values)
        else:
            pillars[pillar] = 0.0 if structural_absence_is_zero else None

    return {
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "structural_absence_is_zero": bool(structural_absence_is_zero),
        "pillar_root_strengths": strengths,
        "pillar_root_ids": root_ids,
        "root_attributions": root_attributions,
        "pillars": pillars,
        "pu_state": "NOT_EVALUABLE",
        "pu_reason": policy["singularity_rule"]["reason"],
        "semantic_cross_pillar_duplication": False,
        "recurrence_meta_pillar_may_repeat_primary_root": True,
    }
