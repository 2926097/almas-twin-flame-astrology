from __future__ import annotations

from collections import defaultdict
from importlib import resources
import json
from math import prod
from numbers import Real
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "irc-aggregation-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_irc_aggregation_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_IRC_DEPENDENCY_AGGREGATION_V2":
        raise ValueError("Política de agregación IRC desconocida.")
    return policy


def _unit(value: Any, *, component_id: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{component_id}: value debe ser numérico.")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{component_id}: value debe estar en [0,1].")
    return value


def _group_id(
    component: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> str:
    kind = str(component.get("kind") or "")
    mapping = policy["kind_dependency_groups"]
    if kind in mapping:
        return str(mapping[kind])
    if kind == "VALIDATED_DISCRIMINATOR":
        component_id = str(component.get("id") or "")
        if not component_id:
            raise ValueError("VALIDATED_DISCRIMINATOR sin id.")
        return "VALIDATED_DISCRIMINATOR:" + component_id
    raise ValueError(f"kind de robustez sin grupo de dependencia: {kind}.")


def grouped_robustness_index(
    components: Sequence[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any] | None = None,
) -> tuple[float, float, list[dict[str, Any]]]:
    """Agrega IRC por grupos de dependencia.

    Los componentes correlacionados se colapsan con MIN y cada grupo resultante
    pesa una sola vez en la media geométrica. R_min conserva el mínimo de todos
    los componentes originales.
    """

    if policy is None:
        policy = load_irc_aggregation_policy()
    if not components:
        raise ValueError("se requiere al menos un componente de robustez")

    grouped: dict[str, list[tuple[str, str, float]]] = defaultdict(list)
    raw_values: list[float] = []

    for index, component in enumerate(components, start=1):
        if not isinstance(component, Mapping):
            raise ValueError(f"Componente IRC {index}: debe ser un objeto.")
        component_id = str(component.get("id") or "")
        if not component_id:
            raise ValueError(f"Componente IRC {index}: id obligatorio.")
        value = _unit(component.get("value"), component_id=component_id)
        group_id = _group_id(component, policy=policy)
        grouped[group_id].append(
            (component_id, str(component.get("kind") or ""), value)
        )
        raw_values.append(value)

    diagnostics: list[dict[str, Any]] = []
    group_values: list[float] = []
    for group_id in sorted(grouped):
        members = grouped[group_id]
        aggregate = min(item[2] for item in members)
        group_values.append(aggregate)
        diagnostics.append(
            {
                "dependency_group": group_id,
                "component_ids": [item[0] for item in members],
                "component_kinds": sorted({item[1] for item in members}),
                "component_values": [item[2] for item in members],
                "aggregate_value": aggregate,
                "within_group_aggregation": "MIN",
            }
        )

    if any(value == 0.0 for value in group_values):
        geometric = 0.0
    else:
        geometric = prod(group_values) ** (1.0 / len(group_values))

    return 100.0 * geometric, min(raw_values), diagnostics
