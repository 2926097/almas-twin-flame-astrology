from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from .core import pillar_score


PRIMARY_MOTIFS = (
    "KARMIC_CONTINUITY",
    "WOUND_REPAIR",
    "IDENTITY_TRANSFORMATION",
    "TRANSFORMATION_POWER",
    "TRANSPERSONAL_FIELD",
    "EROTIC_POLARITY",
    "MIRROR_COMPLEMENTARITY",
    "RELATIONAL_COHERENCE",
    "STRUCTURAL_AFFINITY",
)


def _norm(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_").replace("-", "_")


def _points(root: Mapping[str, Any]) -> list[str]:
    raw = root.get("point_ids")
    if not isinstance(raw, list):
        return []
    return [_norm(value) for value in raw if str(value).strip()]


def _relations(root: Mapping[str, Any]) -> set[str]:
    raw = root.get("relation_ids")
    if not isinstance(raw, list):
        return set()
    return {_norm(value) for value in raw if str(value).strip()}


def _point_set(policy: Mapping[str, Any], name: str) -> set[str]:
    raw = policy["point_sets"][name]
    return {_norm(value) for value in raw}


def _relation_set(policy: Mapping[str, Any], name: str) -> set[str]:
    raw = policy["relation_sets"][name]
    return {_norm(value) for value in raw}


def _contains_pair(
    points: Sequence[str],
    left: set[str],
    right: set[str],
) -> bool:
    for index, point in enumerate(points):
        if point not in left:
            continue
        for other_index, other in enumerate(points):
            if index == other_index:
                continue
            if other in right:
                return True
    return False


def classify_primary_motif(
    root: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> str | None:
    """Asigna un único motivo semántico primario a una raíz core."""

    if not bool(root.get("core_eligible")):
        return None
    if root.get("strength_state") != "CALCULATED_CORE":
        return None

    points = _points(root)
    relations = _relations(root)
    meaningful = _point_set(policy, "MEANINGFUL")
    personal = _point_set(policy, "PERSONAL")
    affinity = _point_set(policy, "AFFINITY")
    transformation = _point_set(policy, "TRANSFORMATION")
    transpersonal = _point_set(policy, "TRANSPERSONAL")
    karmic = _point_set(policy, "KARMIC")
    hard = _relation_set(policy, "HARD")
    coherent = _relation_set(policy, "COHERENT")

    checks = {
        "KARMIC_CONTINUITY": _contains_pair(points, karmic, meaningful),
        "WOUND_REPAIR": _contains_pair(points, {"CHIRON"}, meaningful),
        "IDENTITY_TRANSFORMATION": _contains_pair(
            points,
            {"SUN"},
            {"PLUTO", "URANUS", "NEPTUNE"},
        ),
        "TRANSFORMATION_POWER": _contains_pair(
            points,
            transformation,
            meaningful,
        ),
        "TRANSPERSONAL_FIELD": _contains_pair(
            points,
            transpersonal,
            meaningful,
        ),
        "EROTIC_POLARITY": (
            "VENUS" in points and "MARS" in points
        ),
        "MIRROR_COMPLEMENTARITY": (
            bool(relations & hard)
            and sum(1 for point in points if point in meaningful) >= 2
        ),
        "RELATIONAL_COHERENCE": (
            bool(relations & coherent)
            and sum(1 for point in points if point in personal) >= 2
        ),
        "STRUCTURAL_AFFINITY": (
            sum(1 for point in points if point in affinity) >= 2
        ),
    }

    for motif_id in policy["primary_motif_order"]:
        if checks.get(str(motif_id), False):
            return str(motif_id)
    return None


def mission_motifs(
    root: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> list[str]:
    """Devuelve overlays de misión sin convertirlos en motivos PX genéricos."""

    if not bool(root.get("core_eligible")):
        return []
    if root.get("strength_state") != "CALCULATED_CORE":
        return []

    points = set(_points(root))
    if "AXIS_MERIDIAN" not in points:
        return []

    output = []
    for motif_id, anchor in policy["mission_motifs"].items():
        if _norm(anchor) in points:
            output.append(str(motif_id))
    return sorted(output)


def _family_strengths(root: Mapping[str, Any]) -> dict[str, float]:
    """Extrae fuerza core por familia, evitando que support-only cree recurrencia."""

    raw = root.get("evidence_strengths")
    by_family: dict[str, float] = {}
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            if not bool(item.get("core_eligible")) or bool(item.get("support_only")):
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
            by_family[family] = max(by_family.get(family, 0.0), value)

    if by_family:
        return by_family

    value = root.get("strength")
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or root.get("strength_state") != "CALCULATED_CORE"
    ):
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


def _motif_record(
    motif_id: str,
    roots: Sequence[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any],
    motif_type: str,
) -> dict[str, Any]:
    family_maxima: dict[str, float] = {}
    root_ids: list[str] = []
    exact_multifamily = False

    for root in roots:
        root_id = str(root.get("root_id") or "")
        if root_id:
            root_ids.append(root_id)
        family_strengths = _family_strengths(root)
        if len(family_strengths) >= 2:
            exact_multifamily = True
        for family, value in family_strengths.items():
            family_maxima[family] = max(
                family_maxima.get(family, 0.0),
                value,
            )

    limits = policy["minimum_recurrence"]
    family_count = len(family_maxima)
    root_count = len(set(root_ids))
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

    motif_strength = (
        pillar_score(list(family_maxima.values())) / 100.0
        if recurrent and family_maxima
        else 0.0
    )

    families = sorted(family_maxima)
    return {
        "motif_id": motif_id,
        "motif_type": motif_type,
        "root_ids": sorted(set(root_ids)),
        "root_count": root_count,
        "dependency_families": families,
        "independent_family_count": family_count,
        "family_strengths": {
            family: family_maxima[family]
            for family in families
        },
        "exact_multifamily_root_present": exact_multifamily,
        "recurrence_state": "RECURRENT" if recurrent else "SINGLE_FAMILY_OR_ROOT",
        "motif_strength": motif_strength,
        "includes_relchart": "RELCHART" in family_maxima,
        "includes_natal_draconic": "NATAL_DRACONIC" in family_maxima,
    }


def derive_semantic_motif_graph(
    roots: Sequence[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    """Construye motivos recurrentes sin fusionar ni reescribir root_key."""

    primary_groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    mission_groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    assignments: list[dict[str, Any]] = []

    exact_recurrent_strengths = []

    for root in roots:
        if not isinstance(root, Mapping):
            continue

        root_id = str(root.get("root_id") or "")
        primary = classify_primary_motif(root, policy=policy)
        missions = mission_motifs(root, policy=policy)

        if primary is not None:
            primary_groups[primary].append(root)
        for motif_id in missions:
            mission_groups[motif_id].append(root)

        if (
            bool(root.get("core_eligible"))
            and root.get("strength_state") == "CALCULATED_CORE"
            and int(root.get("independent_family_count") or 0) >= 2
            and isinstance(root.get("strength"), (int, float))
            and not isinstance(root.get("strength"), bool)
        ):
            exact_recurrent_strengths.append(float(root["strength"]))

        assignments.append(
            {
                "root_id": root_id,
                "primary_motif": primary,
                "mission_motifs": missions,
            }
        )

    primary_records = [
        _motif_record(
            motif_id,
            primary_groups[motif_id],
            policy=policy,
            motif_type="PRIMARY",
        )
        for motif_id in sorted(primary_groups)
    ]
    mission_records = [
        _motif_record(
            motif_id,
            mission_groups[motif_id],
            policy=policy,
            motif_type="MISSION",
        )
        for motif_id in sorted(mission_groups)
    ]

    recurrent_primary = [
        item for item in primary_records
        if item["recurrence_state"] == "RECURRENT"
    ]
    recurrent_mission = [
        item for item in mission_records
        if item["recurrence_state"] == "RECURRENT"
    ]

    px_strengths = [
        float(item["motif_strength"])
        for item in recurrent_primary
        if float(item["motif_strength"]) > 0.0
    ]
    ps_strengths = [
        float(item["motif_strength"])
        for item in recurrent_mission
        if float(item["motif_strength"]) > 0.0
    ]

    px_score = pillar_score(px_strengths) if px_strengths else 0.0
    ps_score = pillar_score(ps_strengths) if ps_strengths else 0.0

    relchart_strengths = [
        float(item["motif_strength"])
        for item in recurrent_primary
        if item["includes_relchart"]
    ]
    draconic_strengths = [
        float(item["motif_strength"])
        for item in recurrent_primary
        if item["includes_natal_draconic"]
    ]

    return {
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "assignments": assignments,
        "primary_motifs": primary_records,
        "mission_motifs": mission_records,
        "recurrent_primary_motifs": recurrent_primary,
        "recurrent_mission_motifs": recurrent_mission,
        "px": {
            "score": px_score,
            "strengths": px_strengths,
            "recurrent_motif_count": len(recurrent_primary),
            "components": {
                "PX_G_EXACT_ROOT_RECURRENCE": (
                    pillar_score(exact_recurrent_strengths)
                    if exact_recurrent_strengths else 0.0
                ),
                "PX_S_SEMANTIC_RECURRENCE": px_score,
                "PX_R_RELCHART_CROSS_FAMILY": (
                    pillar_score(relchart_strengths)
                    if relchart_strengths else 0.0
                ),
                "PX_D_NATAL_DRACONIC_CROSS_FAMILY": (
                    pillar_score(draconic_strengths)
                    if draconic_strengths else 0.0
                ),
            },
        },
        "ps": {
            "score": ps_score,
            "strengths": ps_strengths,
            "recurrent_motif_count": len(recurrent_mission),
        },
        "root_identity_mutated": False,
        "support_only_created_core_recurrence": False,
    }
