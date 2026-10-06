from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .analysis_profiles import resolve_analysis_profile
from .relational_policy_presets import (
    RelationalPolicyPresetError,
    resolve_relational_policy_preset,
)
from .structural_policies import validate_declared_aspect_policy


PUBLIC_VERSION = "1.26.0"
ADAPTER_ID = "ALMAS_RELATIONAL_WORK_REQUEST_ADAPTER_V1"

_FIXED_POLICIES: dict[str, dict[str, Any]] = {
    "composite_policy": {
        "midpoint_mode": "SHORTEST_ARC",
        "opposition_tie_break": "NOT_EVALUABLE",
    },
    "davison_policy": {
        "time_midpoint": "UTC_INSTANT",
        "geographic_midpoint": "SPHERICAL_GREAT_CIRCLE",
    },
    "draconic_policy": {
        "node_id": "NORTH_NODE",
        "transform": "NORTH_NODE_TO_ZERO",
        "include_angles": True,
        "include_houses": True,
    },
}

_REQUIRED_DECLARED_POLICIES_BY_PROFILE: dict[str, tuple[str, ...]] = {
    "FULL_ASTROLOGY": (
        "aspect_policy",
        "declination_policy",
        "antiscia_policy",
        "relationship_chart_consonance_policy",
        "draconic_aspect_policy",
    ),
    "FULL_MULTIDISCIPLINARY": (
        "aspect_policy",
        "declination_policy",
        "antiscia_policy",
        "relationship_chart_consonance_policy",
        "draconic_aspect_policy",
    ),
    "TEMPORAL": (
        "aspect_policy",
        "declination_policy",
        "antiscia_policy",
        "relationship_chart_consonance_policy",
        "draconic_aspect_policy",
    ),
    "SOUL_CONTRACT": (
        "aspect_policy",
        "declination_policy",
        "antiscia_policy",
        "relationship_chart_consonance_policy",
        "draconic_aspect_policy",
    ),
}

_OPTIONAL_POLICY_KEYS = (
    "rulership_policy",
    "maximum_definition_context",
    "lot_policy",
    "secondary_symbolic_policy",
)


class RelationalWorkRequestError(ValueError):
    """La envolvente del panel no puede adaptarse al raw_input relacional."""


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RelationalWorkRequestError(f"{label} debe ser un objeto.")
    return value


def _request_object(work_request: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = work_request.get("request")
    if nested is None:
        return work_request
    return _require_mapping(nested, "request")


def _validate_subjects(subjects: Any) -> list[dict[str, Any]]:
    if not isinstance(subjects, list) or len(subjects) != 2:
        raise RelationalWorkRequestError(
            "ALMAS_WORK_REQUEST relacional exige exactamente dos subjects."
        )

    normalized: list[dict[str, Any]] = []
    for index, raw_subject in enumerate(subjects):
        subject = _require_mapping(raw_subject, f"subjects[{index}]")
        subject_id = subject.get("id")
        birth_date = subject.get("birth_date")
        if not isinstance(subject_id, str) or not subject_id.strip():
            raise RelationalWorkRequestError(
                f"subjects[{index}].id es obligatorio."
            )
        if not isinstance(birth_date, str) or not birth_date.strip():
            raise RelationalWorkRequestError(
                f"{subject_id}: birth_date es obligatorio."
            )
        reliability = subject.get("time_reliability")
        if reliability not in {"A", "B", "C", "D"}:
            raise RelationalWorkRequestError(
                f"{subject_id}: time_reliability debe ser A/B/C/D."
            )
        latitude = subject.get("latitude")
        longitude = subject.get("longitude")
        if (
            isinstance(latitude, bool)
            or not isinstance(latitude, (int, float))
            or not -90 <= float(latitude) <= 90
        ):
            raise RelationalWorkRequestError(
                f"{subject_id}: latitude numérica válida es obligatoria."
            )
        if (
            isinstance(longitude, bool)
            or not isinstance(longitude, (int, float))
            or not -180 <= float(longitude) <= 180
        ):
            raise RelationalWorkRequestError(
                f"{subject_id}: longitude numérica válida es obligatoria."
            )
        normalized.append(deepcopy(dict(subject)))
    return normalized


def _validate_nonnegative_pair(
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
            raise RelationalWorkRequestError(
                f"{label}.{key} debe ser numérico y >= 0."
            )
    if present == 0:
        raise RelationalWorkRequestError(
            f"{label} debe declarar al menos uno de {keys[0]} o {keys[1]}."
        )


def _validate_declared_policy(name: str, value: Any) -> dict[str, Any]:
    policy = _require_mapping(value, f"analysis_policies.{name}")

    if name in {"aspect_policy", "draconic_aspect_policy"}:
        try:
            validate_declared_aspect_policy(policy)
        except ValueError as exc:
            raise RelationalWorkRequestError(str(exc)) from exc
    elif name == "declination_policy":
        _validate_nonnegative_pair(
            policy,
            keys=("parallel_orb", "contra_parallel_orb"),
            label="declination_policy",
        )
    elif name == "antiscia_policy":
        _validate_nonnegative_pair(
            policy,
            keys=("antiscia_orb", "contra_antiscia_orb"),
            label="antiscia_policy",
        )
    elif name == "relationship_chart_consonance_policy":
        aspect_policy = policy.get("aspect_policy")
        if not isinstance(aspect_policy, Mapping) or not aspect_policy:
            raise RelationalWorkRequestError(
                "relationship_chart_consonance_policy.aspect_policy es obligatorio."
            )
        try:
            validate_declared_aspect_policy(aspect_policy)
        except ValueError as exc:
            raise RelationalWorkRequestError(str(exc)) from exc
        point_ids = policy.get("point_ids")
        if point_ids is not None and (
            not isinstance(point_ids, list)
            or any(not isinstance(item, str) or not item for item in point_ids)
        ):
            raise RelationalWorkRequestError(
                "relationship_chart_consonance_policy.point_ids debe ser una lista de strings."
            )

    return deepcopy(dict(policy))


def _merge_fixed_policy(
    name: str,
    declared: Any,
) -> dict[str, Any]:
    expected = _FIXED_POLICIES[name]
    if declared is None:
        return deepcopy(expected)

    policy = _require_mapping(declared, f"analysis_policies.{name}")
    unexpected = set(policy) - set(expected)
    if unexpected:
        raise RelationalWorkRequestError(
            f"{name}: campos no admitidos por la convención congelada: "
            + ", ".join(sorted(unexpected))
        )
    for key, expected_value in expected.items():
        if key in policy and policy[key] != expected_value:
            raise RelationalWorkRequestError(
                f"{name}.{key}={policy[key]!r} contradice la convención "
                f"congelada {expected_value!r}."
            )
    return deepcopy(expected)


def assess_relational_work_request(
    work_request: Mapping[str, Any],
    *,
    expected_public_version: str = PUBLIC_VERSION,
) -> dict[str, Any]:
    """Valida la envolvente y describe si puede adaptarse sin inventar orbes."""

    root = _require_mapping(work_request, "work_request")
    request = _request_object(root)

    if request.get("format") != "ALMAS_WORK_REQUEST":
        raise RelationalWorkRequestError(
            "request.format debe ser ALMAS_WORK_REQUEST."
        )
    if request.get("type") != "RELATIONAL":
        raise RelationalWorkRequestError("request.type debe ser RELATIONAL.")
    if request.get("execution_state") != "REQUEST_ONLY":
        raise RelationalWorkRequestError(
            "El adaptador sólo acepta execution_state=REQUEST_ONLY."
        )
    compatible_versions = {expected_public_version}
    # 1.26 añade una capa optativa: la envolvente de entrada 1.25 sigue válida.
    if expected_public_version == "1.26.0":
        compatible_versions.add("1.25.0")
    if request.get("public_version") not in compatible_versions:
        raise RelationalWorkRequestError(
            "public_version incompatible: "
            f"esperado {expected_public_version}, recibido "
            f"{request.get('public_version')!r}."
        )

    profile_id = request.get("analysis_profile")
    try:
        profile = resolve_analysis_profile(profile_id)
    except ValueError as exc:
        raise RelationalWorkRequestError(str(exc)) from exc

    _validate_subjects(request.get("subjects"))

    events = request.get("events", [])
    if not isinstance(events, list):
        raise RelationalWorkRequestError("request.events debe ser una lista.")

    analysis_policies = request.get("analysis_policies", {})
    if analysis_policies is None:
        analysis_policies = {}
    analysis_policies = _require_mapping(
        analysis_policies,
        "request.analysis_policies",
    )

    required_declared = _REQUIRED_DECLARED_POLICIES_BY_PROFILE.get(
        profile["profile_id"],
        (),
    )

    policy_profile_id = request.get("analysis_policy_profile")
    resolved_preset = None
    if policy_profile_id is not None:
        if not isinstance(policy_profile_id, str) or not policy_profile_id.strip():
            raise RelationalWorkRequestError(
                "analysis_policy_profile debe ser un identificador no vacío."
            )
        conflicting = sorted(
            set(required_declared) & set(analysis_policies)
        )
        if conflicting:
            raise RelationalWorkRequestError(
                "No se puede combinar analysis_policy_profile con overrides "
                "inline de políticas de orbe: "
                + ", ".join(conflicting)
                + "."
            )
        try:
            resolved_preset = resolve_relational_policy_preset(
                policy_profile_id,
                analysis_profile=profile["profile_id"],
            )
        except RelationalPolicyPresetError as exc:
            raise RelationalWorkRequestError(str(exc)) from exc

    missing = (
        []
        if resolved_preset is not None
        else [
            key
            for key in required_declared
            if key not in analysis_policies
        ]
    )

    return {
        "adapter_id": ADAPTER_ID,
        "public_version": expected_public_version,
        "profile_id": profile["profile_id"],
        "analysis_mode": profile["analysis_mode"],
        "ready_for_raw_input": not missing,
        "missing_declared_policies": missing,
        "analysis_policy_profile": (
            resolved_preset["preset_id"]
            if resolved_preset is not None
            else None
        ),
        "analysis_policy_fingerprint": (
            resolved_preset["policy_fingerprint"]
            if resolved_preset is not None
            else None
        ),
        "policy_source": (
            "EXPLICIT_PRESET"
            if resolved_preset is not None
            else "EXPLICIT_INLINE"
        ),
        "fixed_policies_available": sorted(_FIXED_POLICIES),
        "implicit_orbs_allowed": False,
        "case_fitting_allowed": False,
    }


def prepare_relational_raw_input(
    work_request: Mapping[str, Any],
    *,
    expected_public_version: str = PUBLIC_VERSION,
    require_complete: bool = True,
) -> dict[str, Any]:
    """Adapta ALMAS_WORK_REQUEST al raw_input M00-M31 sin inferir orbes."""

    assessment = assess_relational_work_request(
        work_request,
        expected_public_version=expected_public_version,
    )
    root = _require_mapping(work_request, "work_request")
    request = _request_object(root)
    analysis_policies = request.get("analysis_policies") or {}
    analysis_policies = _require_mapping(
        analysis_policies,
        "request.analysis_policies",
    )

    if require_complete and assessment["missing_declared_policies"]:
        raise RelationalWorkRequestError(
            "Faltan políticas declaradas requeridas para "
            f"{assessment['profile_id']}: "
            + ", ".join(assessment["missing_declared_policies"])
            + ". ALMAS no infiere orbes en runtime."
        )

    raw: dict[str, Any] = {
        "mode": assessment["analysis_mode"],
        "analysis_profile": assessment["profile_id"],
        "subjects": _validate_subjects(request.get("subjects")),
        "events": deepcopy(request.get("events", [])),
    }

    declared_keys: list[str] = []
    policy_profile_id = assessment.get("analysis_policy_profile")
    if isinstance(policy_profile_id, str):
        try:
            preset = resolve_relational_policy_preset(
                policy_profile_id,
                analysis_profile=assessment["profile_id"],
            )
        except RelationalPolicyPresetError as exc:
            raise RelationalWorkRequestError(str(exc)) from exc
        for name, value in preset["policies"].items():
            raw[name] = _validate_declared_policy(name, value)
            declared_keys.append(name)
    else:
        for name in _REQUIRED_DECLARED_POLICIES_BY_PROFILE.get(
            assessment["profile_id"],
            (),
        ):
            if name not in analysis_policies:
                continue
            raw[name] = _validate_declared_policy(
                name,
                analysis_policies[name],
            )
            declared_keys.append(name)

    for name in _FIXED_POLICIES:
        raw[name] = _merge_fixed_policy(
            name,
            analysis_policies.get(name),
        )

    for name in _OPTIONAL_POLICY_KEYS:
        if name in analysis_policies:
            if name == "maximum_definition_context" and not isinstance(analysis_policies[name], bool):
                raise RelationalWorkRequestError(
                    "analysis_policies.maximum_definition_context debe ser booleano."
                )
            raw[name] = deepcopy(analysis_policies[name])
            declared_keys.append(name)

    if "atacires_requests" in request:
        requests = request["atacires_requests"]
        if not isinstance(requests, list) or not 1 <= len(requests) <= 16:
            raise RelationalWorkRequestError("atacires_requests requiere de 1 a 16 solicitudes.")
        raw["atacires_requests"] = deepcopy(requests)

    raw["request_adapter_trace"] = {
        "adapter_id": ADAPTER_ID,
        "source_format": "ALMAS_WORK_REQUEST",
        "source_execution_state": request.get("execution_state"),
        "public_version": expected_public_version,
        "analysis_profile": assessment["profile_id"],
        "analysis_policy_profile": assessment.get("analysis_policy_profile"),
        "analysis_policy_fingerprint": assessment.get(
            "analysis_policy_fingerprint"
        ),
        "policy_source": assessment.get("policy_source"),
        "fixed_policies_injected": sorted(_FIXED_POLICIES),
        "declared_policy_keys": sorted(set(declared_keys)),
        "missing_declared_policies": list(
            assessment["missing_declared_policies"]
        ),
        "implicit_orbs_used": False,
        "case_fitting_used": False,
    }
    return raw
