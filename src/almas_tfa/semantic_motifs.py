from __future__ import annotations

import json
from importlib import resources
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "semantic-motif-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_semantic_motif_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_SEMANTIC_MOTIF_RECURRENCE_V1":
        raise ValueError("Política de motivos semánticos desconocida.")
    return policy


def _norm(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_").replace("-", "_")


def _point_set(policy: Mapping[str, Any], name: str) -> set[str]:
    raw = policy.get("point_sets", {}).get(name)
    if not isinstance(raw, list):
        raise ValueError(f"point_sets.{name} debe ser una lista.")
    return {_norm(item) for item in raw}


def _relation_set(policy: Mapping[str, Any], name: str) -> set[str]:
    raw = policy.get("relation_sets", {}).get(name)
    if not isinstance(raw, list):
        raise ValueError(f"relation_sets.{name} debe ser una lista.")
    return {_norm(item) for item in raw}


def _points(root: Mapping[str, Any]) -> list[str]:
    raw = root.get("point_ids")
    if not isinstance(raw, list):
        return []
    return [_norm(item) for item in raw if str(item).strip()]


def _relations(root: Mapping[str, Any]) -> set[str]:
    raw = root.get("relation_ids")
    if not isinstance(raw, list):
        return set()
    return {_norm(item) for item in raw if str(item).strip()}


def _families(root: Mapping[str, Any]) -> list[str]:
    raw = root.get("dependency_families")
    if not isinstance(raw, list):
        return []
    return sorted({_norm(item) for item in raw if str(item).strip()})


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


def classify_semantic_motif(
    root: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> str | None:
    """Asigna un único motivo semántico primario a una raíz core."""

    if policy is None:
        policy = load_semantic_motif_policy()

    if not bool(root.get("core_eligible")):
        return None
    if root.get("strength_state") != "CALCULATED_CORE":
        return None

    points = _points(root)
    relations = _relations(root)
    meaningful = _point_set(policy, "MEANINGFUL_COUNTERPART")
    personal = _point_set(policy, "PERSONAL_RELATIONAL")
    affinity = _point_set(policy, "AFFINITY")

    for motif in policy["motif_rule_order"]:
        if motif == "MISSION_SERVICE":
            if _other_point_matches(
                points,
                {"AXIS_MERIDIAN"},
                _point_set(policy, "MISSION_ANCHOR"),
            ):
                return motif
        elif motif == "KARMIC_CONTINUITY":
            if _other_point_matches(
                points,
                _point_set(policy, "KARMIC_ANCHOR"),
                meaningful,
            ):
                return motif
        elif motif == "WOUND_REPAIR":
            if _other_point_matches(
                points,
                _point_set(policy, "WOUND_ANCHOR"),
                meaningful,
            ):
                return motif
        elif motif == "TRANSFORMATION_POWER":
            if _other_point_matches(
                points,
                _point_set(policy, "TRANSFORMATION_ANCHOR"),
                meaningful,
            ):
                return motif
        elif motif == "TRANSPERSONAL_FIELD":
            if _other_point_matches(
                points,
                _point_set(policy, "TRANSPERSONAL_ANCHOR"),
                meaningful,
            ):
                return motif
        elif motif == "MIRROR_POLARITY":
            if (
                relations & _relation_set(policy, "MIRROR_HARD")
                and _at_least(points, meaningful, 2)
            ):
                return motif
        elif motif == "RELATIONAL_COHERENCE":
            if relations & _relation_set(policy, "COHERENT"):
                if (
                    _other_point_matches(points, {"MERCURY"}, personal)
                    or _other_point_matches(points, {"AXIS_HORIZON"}, personal)
                ):
                    return motif
        elif motif == "STRUCTURAL_AFFINITY":
            if _at_least(points, affinity, 2):
                return motif
        else:
            raise ValueError(f"Motivo semántico desconocido: {motif}.")

    return None


def derive_semantic_motifs(
    roots: Sequence[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any] | None = None,
    active_root_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Agrega raíces por motivo y familia de dependencia.

    Dentro de cada familia se conserva sólo la raíz más fuerte. La recurrencia
    requiere al menos dos familias independientes y su fuerza es la segunda
    mayor fuerza familiar, una regla conservadora sin pesos adicionales.
    """

    if policy is None:
        policy = load_semantic_motif_policy()

    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    root_motifs: list[dict[str, Any]] = []

    for root in roots:
        if not isinstance(root, Mapping):
            continue
        root_id = str(root.get("root_id") or "")
        if active_root_ids is not None and root_id not in active_root_ids:
            continue

        motif = classify_semantic_motif(root, policy=policy)
        if motif is None:
            continue

        strength = root.get("strength")
        if isinstance(strength, bool) or not isinstance(strength, (int, float)):
            continue
        strength = float(strength)
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"{root_id}: strength debe estar en [0,1].")

        families = _families(root)
        if not families:
            continue

        root_motifs.append(
            {
                "root_id": root_id,
                "motif_id": motif,
                "strength": strength,
                "dependency_families": families,
                "point_ids": _points(root),
                "relation_ids": sorted(_relations(root)),
            }
        )

        motif_bucket = grouped.setdefault(motif, {})
        for family in families:
            current = motif_bucket.get(family)
            candidate = {"root_id": root_id, "strength": strength}
            if current is None or (
                strength,
                root_id,
            ) > (
                float(current["strength"]),
                str(current["root_id"]),
            ):
                motif_bucket[family] = candidate

    minimum = int(policy["recurrence"]["minimum_independent_families"])
    motifs: list[dict[str, Any]] = []
    motif_attributions: list[dict[str, Any]] = []

    for motif in policy["motif_rule_order"]:
        families = grouped.get(motif, {})
        ordered = sorted(
            (
                {
                    "dependency_family": family,
                    "root_id": data["root_id"],
                    "strength": float(data["strength"]),
                }
                for family, data in families.items()
            ),
            key=lambda item: (
                -item["strength"],
                item["dependency_family"],
                item["root_id"],
            ),
        )
        recurrent = len(ordered) >= minimum
        recurrence_strength = (
            float(ordered[minimum - 1]["strength"])
            if recurrent
            else None
        )

        motif_record = {
            "motif_id": motif,
            "independent_family_count": len(ordered),
            "family_representatives": ordered,
            "recurrent": recurrent,
            "recurrence_strength": recurrence_strength,
            "recurrence_strength_rule": policy["principles"][
                "recurrence_strength_rule"
            ],
        }
        motifs.append(motif_record)

        if recurrent and recurrence_strength is not None:
            contributions = {
                str(policy["recurrence"]["px_pillar"]): recurrence_strength
            }
            if motif == "MISSION_SERVICE":
                contributions[
                    str(policy["recurrence"]["ps_pillar"])
                ] = recurrence_strength

            motif_attributions.append(
                {
                    "root_id": "MOTIF:" + motif,
                    "attribution_type": "SEMANTIC_MOTIF",
                    "motif_id": motif,
                    "eligible": True,
                    "contributions": contributions,
                    "strength": recurrence_strength,
                    "dependency_families": [
                        item["dependency_family"] for item in ordered
                    ],
                    "source_root_ids": sorted(
                        {item["root_id"] for item in ordered}
                    ),
                }
            )

    recurrent = [item for item in motifs if item["recurrent"]]

    return {
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "root_motifs": root_motifs,
        "motifs": motifs,
        "recurrent_motifs": recurrent,
        "recurrent_motif_count": len(recurrent),
        "motif_attributions": motif_attributions,
        "px_is_ontological_discriminator": False,
        "pu_created": False,
    }
