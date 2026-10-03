from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from importlib import resources
import json
from typing import Any, Mapping

from .structural_policies import validate_declared_aspect_policy


PACKAGE = "almas_tfa"
RESOURCE = "relational-analysis-policy-presets.json"
REGISTRY_ID = "ALMAS_RELATIONAL_POLICY_PRESET_REGISTRY_V1"


class RelationalPolicyPresetError(ValueError):
    pass


def _policy_fingerprint(policies: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        policies,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def load_relational_policy_preset_registry() -> dict[str, Any]:
    resource = resources.files(PACKAGE).joinpath("data", RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        registry = json.load(handle)
    if registry.get("registry_id") != REGISTRY_ID:
        raise RelationalPolicyPresetError(
            "Registro de presets relacionales desconocido."
        )
    presets = registry.get("presets")
    if not isinstance(presets, Mapping) or not presets:
        raise RelationalPolicyPresetError(
            "El registro de presets relacionales está vacío."
        )
    return registry


def _validate_pair_policy(
    policy: Mapping[str, Any],
    *,
    keys: tuple[str, str],
    label: str,
) -> None:
    present = 0
    for key in keys:
        value = policy.get(key)
        if value is None:
            continue
        present += 1
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or float(value) < 0
        ):
            raise RelationalPolicyPresetError(
                f"{label}.{key} debe ser numérico y >= 0."
            )
    if present == 0:
        raise RelationalPolicyPresetError(
            f"{label} no declara ningún orbe evaluable."
        )


def _validate_preset(preset_id: str, preset: Mapping[str, Any]) -> None:
    if preset.get("epistemic_class") != "E_PROJECT_POLICY":
        raise RelationalPolicyPresetError(
            f"{preset_id}: todo preset debe permanecer E_PROJECT_POLICY."
        )
    if preset.get("status") not in {"EXPERIMENTAL", "FROZEN_EXPERIMENTAL_BASELINE"}:
        raise RelationalPolicyPresetError(
            f"{preset_id}: status no admitido."
        )

    profiles = preset.get("analysis_profiles")
    if not isinstance(profiles, list) or not profiles:
        raise RelationalPolicyPresetError(
            f"{preset_id}: analysis_profiles debe ser lista no vacía."
        )

    policies = preset.get("policies")
    if not isinstance(policies, Mapping):
        raise RelationalPolicyPresetError(
            f"{preset_id}: policies debe ser un objeto."
        )

    required = {
        "aspect_policy",
        "declination_policy",
        "antiscia_policy",
        "relationship_chart_consonance_policy",
        "draconic_aspect_policy",
    }
    missing = required - set(policies)
    if missing:
        raise RelationalPolicyPresetError(
            f"{preset_id}: faltan políticas {sorted(missing)}."
        )

    for name in ("aspect_policy", "draconic_aspect_policy"):
        policy = policies[name]
        if not isinstance(policy, Mapping):
            raise RelationalPolicyPresetError(
                f"{preset_id}.{name} debe ser un objeto."
            )
        try:
            validate_declared_aspect_policy(policy)
        except ValueError as exc:
            raise RelationalPolicyPresetError(
                f"{preset_id}.{name}: {exc}"
            ) from exc

    decl = policies["declination_policy"]
    if not isinstance(decl, Mapping):
        raise RelationalPolicyPresetError(
            f"{preset_id}.declination_policy debe ser objeto."
        )
    _validate_pair_policy(
        decl,
        keys=("parallel_orb", "contra_parallel_orb"),
        label=f"{preset_id}.declination_policy",
    )

    anti = policies["antiscia_policy"]
    if not isinstance(anti, Mapping):
        raise RelationalPolicyPresetError(
            f"{preset_id}.antiscia_policy debe ser objeto."
        )
    _validate_pair_policy(
        anti,
        keys=("antiscia_orb", "contra_antiscia_orb"),
        label=f"{preset_id}.antiscia_policy",
    )

    relchart = policies["relationship_chart_consonance_policy"]
    if not isinstance(relchart, Mapping):
        raise RelationalPolicyPresetError(
            f"{preset_id}.relationship_chart_consonance_policy debe ser objeto."
        )
    rel_aspects = relchart.get("aspect_policy")
    if not isinstance(rel_aspects, Mapping):
        raise RelationalPolicyPresetError(
            f"{preset_id}: RELCHART debe declarar aspect_policy."
        )
    try:
        validate_declared_aspect_policy(rel_aspects)
    except ValueError as exc:
        raise RelationalPolicyPresetError(
            f"{preset_id}.relationship_chart_consonance_policy: {exc}"
        ) from exc

    sources = preset.get("source_basis")
    if not isinstance(sources, list) or not sources:
        raise RelationalPolicyPresetError(
            f"{preset_id}: source_basis debe ser lista no vacía."
        )

    limitations = preset.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        raise RelationalPolicyPresetError(
            f"{preset_id}: limitations debe ser lista no vacía."
        )


def resolve_relational_policy_preset(
    preset_id: str,
    *,
    analysis_profile: str,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(preset_id, str) or not preset_id.strip():
        raise RelationalPolicyPresetError(
            "analysis_policy_profile debe ser un identificador no vacío."
        )
    if registry is None:
        registry = load_relational_policy_preset_registry()

    presets = registry.get("presets")
    if not isinstance(presets, Mapping) or preset_id not in presets:
        raise RelationalPolicyPresetError(
            f"Preset relacional desconocido: {preset_id}."
        )
    preset = presets[preset_id]
    if not isinstance(preset, Mapping):
        raise RelationalPolicyPresetError(
            f"{preset_id}: preset inválido."
        )
    _validate_preset(preset_id, preset)

    allowed = {str(item) for item in preset["analysis_profiles"]}
    if analysis_profile not in allowed:
        raise RelationalPolicyPresetError(
            f"{preset_id} no admite analysis_profile={analysis_profile}."
        )

    return {
        "preset_id": preset_id,
        "registry_id": str(registry["registry_id"]),
        "registry_status": str(registry["status"]),
        "epistemic_class": str(preset["epistemic_class"]),
        "status": str(preset["status"]),
        "policies": deepcopy(dict(preset["policies"])),
        "policy_fingerprint": _policy_fingerprint(preset["policies"]),
        "source_basis": deepcopy(list(preset["source_basis"])),
        "project_choices": deepcopy(list(preset.get("project_choices", []))),
        "limitations": deepcopy(list(preset["limitations"])),
        "explicit_selection": True,
        "implicit_orbs_used": False,
        "case_fitting_used": False,
    }
