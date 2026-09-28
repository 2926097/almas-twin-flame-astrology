from __future__ import annotations

import json
from importlib import resources
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "root-strength-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_root_strength_policy() -> dict[str, Any]:
    """Carga la política canónica congelada de fuerza de raíces."""

    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_ROOT_STRENGTH_BASELINE_V1":
        raise ValueError("Política de fuerza de raíces desconocida o no congelada.")

    return policy


def _unit(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} debe ser numérico.")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{field} debe estar en [0,1].")
    return value


def _mapping_factor(
    mapping: Mapping[str, Any],
    key: str,
    *,
    field: str,
) -> float:
    value = mapping.get(key, mapping.get("DEFAULT"))
    if value is None:
        raise ValueError(f"{field}: falta {key!r} y no existe DEFAULT.")
    return _unit(value, f"{field}.{key}")


def _relation_id(contact: Mapping[str, Any]) -> str:
    return str(
        contact.get("aspect")
        or contact.get("relation")
        or "DEFAULT"
    ).upper()


def _uses_time_sensitive_point(
    contact: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    birth_policy = policy.get("birth_time_factor")
    if not isinstance(birth_policy, Mapping):
        raise ValueError("birth_time_factor debe ser un objeto.")

    raw_ids = birth_policy.get("time_sensitive_point_ids", [])
    if not isinstance(raw_ids, list):
        raise ValueError("time_sensitive_point_ids debe ser una lista.")

    timed_ids = {str(value).upper() for value in raw_ids}
    point_a = str(contact.get("point_a", "")).upper()
    point_b = str(contact.get("point_b", "")).upper()
    type_a = str(contact.get("point_a_type", "")).upper()
    type_b = str(contact.get("point_b_type", "")).upper()

    return (
        point_a in timed_ids
        or point_b in timed_ids
        or type_a == "ANGLE"
        or type_b == "ANGLE"
    )


def evidence_strength(
    evidence: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> float | None:
    """Calcula S para una evidencia ya normalizada por M15.

    La baseline v1 es deliberadamente neutral: las familias técnicas y
    coeficientes de aspecto valen 1.0 hasta que exista calibración externa
    preregistrada. La incertidumbre de hora natal se evalúa en M23-M25,
    evitando penalizarla dos veces.
    """

    if policy is None:
        policy = load_root_strength_policy()

    exactness_raw = evidence.get("exactness")
    if exactness_raw is None:
        return None
    exactness = _unit(exactness_raw, "exactness")

    family = str(evidence.get("technique_family") or "DEFAULT").upper()
    technique_policy = policy.get("technique_reliability")
    if not isinstance(technique_policy, Mapping):
        raise ValueError("technique_reliability debe ser un objeto.")
    technique = _mapping_factor(
        technique_policy,
        family,
        field="technique_reliability",
    )

    contact = evidence.get("contact")
    if not isinstance(contact, Mapping):
        contact = {}

    aspect_policy = policy.get("aspect_coefficient")
    if not isinstance(aspect_policy, Mapping):
        raise ValueError("aspect_coefficient debe ser un objeto.")
    aspect = _mapping_factor(
        aspect_policy,
        _relation_id(contact),
        field="aspect_coefficient",
    )

    birth_policy = policy.get("birth_time_factor")
    if not isinstance(birth_policy, Mapping):
        raise ValueError("birth_time_factor debe ser un objeto.")
    birth_key = (
        "TIMED_POINT"
        if _uses_time_sensitive_point(contact, policy)
        else "DEFAULT"
    )
    birth = _mapping_factor(
        birth_policy,
        birth_key,
        field="birth_time_factor",
    )

    return max(0.0, min(1.0, exactness * technique * birth * aspect))


def derive_root_strength(
    members: Sequence[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Deriva una fuerza conservadora para una raíz M17.

    Si existe evidencia core, la fuerza de raíz es el máximo S entre las
    evidencias core independientes que ya sobrevivieron M16. Las capas
    support-only pueden recibir fuerza diagnóstica, pero nunca sustituyen una
    raíz core ni la hacen core-eligible.
    """

    if policy is None:
        policy = load_root_strength_policy()

    calculated: list[dict[str, Any]] = []
    for member in members:
        strength = evidence_strength(member, policy=policy)
        calculated.append(
            {
                "evidence_id": str(member.get("evidence_id")),
                "strength": strength,
                "core_eligible": bool(member.get("core_eligible")),
                "support_only": bool(member.get("support_only")),
                "dependency_family": member.get("dependency_family"),
                "technique_family": member.get("technique_family"),
            }
        )

    core = [
        item for item in calculated
        if item["strength"] is not None
        and item["core_eligible"]
        and not item["support_only"]
    ]
    support = [
        item for item in calculated
        if item["strength"] is not None
        and (item["support_only"] or not item["core_eligible"])
    ]

    if core:
        winner = max(core, key=lambda item: (item["strength"], item["evidence_id"]))
        state = "CALCULATED_CORE"
        strength = float(winner["strength"])
    elif support:
        winner = max(
            support,
            key=lambda item: (item["strength"], item["evidence_id"]),
        )
        state = "CALCULATED_SUPPORT_ONLY"
        strength = float(winner["strength"])
    else:
        winner = None
        state = "NOT_EVALUABLE"
        strength = None

    return {
        "strength": strength,
        "strength_state": state,
        "dominant_evidence_id": (
            winner["evidence_id"] if winner is not None else None
        ),
        "evidence_strengths": calculated,
        "policy_id": policy["policy_id"],
        "aggregation": policy["principles"]["root_aggregation"],
    }
