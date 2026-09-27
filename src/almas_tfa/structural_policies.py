from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping


PACKAGE = "almas_tfa"


def _load_json(name: str) -> dict[str, Any]:
    resource = resources.files(PACKAGE).joinpath("data", name)
    with resource.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_technique_dependency_registry() -> dict[str, Any]:
    registry = _load_json("technique-dependency-registry.json")
    if registry.get("registry_id") != "ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1":
        raise ValueError("Registro técnica/dependencia desconocido.")

    bindings = registry.get("source_bindings")
    if not isinstance(bindings, Mapping) or not bindings:
        raise ValueError("source_bindings debe ser un objeto no vacío.")

    required = {
        "module_id",
        "technique_family",
        "dependency_family",
        "support_only",
        "core_eligible",
        "directional",
    }
    for source, spec in bindings.items():
        if not isinstance(source, str) or not source:
            raise ValueError("source_bindings contiene una clave inválida.")
        if not isinstance(spec, Mapping):
            raise ValueError(f"{source}: binding inválido.")
        if not required.issubset(spec):
            missing = sorted(required - set(spec))
            raise ValueError(f"{source}: faltan campos {missing}.")
        for key in ("module_id", "technique_family", "dependency_family"):
            if not isinstance(spec.get(key), str) or not spec.get(key):
                raise ValueError(f"{source}: {key} debe ser string no vacío.")
        for key in ("support_only", "core_eligible", "directional"):
            if not isinstance(spec.get(key), bool):
                raise ValueError(f"{source}: {key} debe ser boolean.")
        if spec["support_only"] and spec["core_eligible"]:
            raise ValueError(
                f"{source}: support_only no puede ser core_eligible."
            )

    return registry


def load_declared_orb_contract_policy() -> dict[str, Any]:
    policy = _load_json("declared-orb-contract-policy.json")
    if policy.get("policy_id") != "ALMAS_DECLARED_ORB_CONTRACT_V1":
        raise ValueError("Política de orbes declarados desconocida.")
    return policy


def load_structural_loading_policy() -> dict[str, Any]:
    policy = _load_json("structural-loading-policy.json")
    if policy.get("policy_id") != "ALMAS_STRUCTURAL_LOADING_CONTRACT_V1":
        raise ValueError("Política de loading estructural desconocida.")
    return policy


def validate_declared_aspect_policy(
    aspect_policy: Mapping[str, Mapping[str, Any]],
    *,
    policy: Mapping[str, Any] | None = None,
) -> None:
    """Valida un mapa de aspectos sin inferir ángulos ni orbes implícitos."""

    if policy is None:
        policy = load_declared_orb_contract_policy()

    if not isinstance(aspect_policy, Mapping) or not aspect_policy:
        raise ValueError("aspect_policy debe ser un objeto no vacío.")

    constraints = policy.get("numeric_constraints")
    if not isinstance(constraints, Mapping):
        raise ValueError("numeric_constraints debe ser un objeto.")

    angle_min = float(constraints["angle_min"])
    angle_max = float(constraints["angle_max"])
    orb_min = float(constraints["orb_min"])

    for name, spec in aspect_policy.items():
        if not isinstance(name, str) or not name:
            raise ValueError("El nombre de aspecto debe ser string no vacío.")
        if not isinstance(spec, Mapping):
            raise ValueError(f"{name}: la política de aspecto debe ser objeto.")
        if set(spec) - {"angle", "orb"}:
            raise ValueError(
                f"{name}: sólo se permiten los campos angle y orb."
            )
        if "angle" not in spec or "orb" not in spec:
            raise ValueError(f"{name}: angle y orb son obligatorios.")

        angle = spec["angle"]
        orb = spec["orb"]
        if isinstance(angle, bool) or not isinstance(angle, (int, float)):
            raise ValueError(f"{name}: angle debe ser numérico.")
        if isinstance(orb, bool) or not isinstance(orb, (int, float)):
            raise ValueError(f"{name}: orb debe ser numérico.")

        if not angle_min <= float(angle) <= angle_max:
            raise ValueError(
                f"{name}: angle debe estar en [{angle_min:g}, {angle_max:g}]."
            )
        if float(orb) < orb_min:
            raise ValueError(f"{name}: orb no puede ser negativo.")
