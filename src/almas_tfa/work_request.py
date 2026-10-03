from __future__ import annotations

from copy import deepcopy
from importlib import metadata
from math import isfinite
from typing import Any, Mapping

from .analysis_profiles import resolve_analysis_profile
from .structural_policies import (
    load_relational_orb_baseline_policy,
    validate_declared_aspect_policy,
)


class WorkRequestError(ValueError):
    """Solicitud del panel incompatible con el contrato relacional ALMAS."""


PACKAGE_NAME = "almas-twin-flame-astrology"
WORK_REQUEST_FORMAT = "ALMAS_WORK_REQUEST"
SUPPORTED_TYPE = "RELATIONAL"
POLICY_BUNDLE_SCHEMA_VERSION = "1.0.0"
RELATIONAL_ORB_PRESET_ID = "ALMAS_RELATIONAL_ORB_BASELINE_V1"


# Estas convenciones ya están fijadas por la implementación de producción.
# No contienen valores de orbe y no pueden usarse para ajustar el caso.
NORMATIVE_DEFAULTS: dict[str, Mapping[str, Any]] = {
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


# Sólo se exigen políticas cuando el perfil realmente requiere el módulo.
MODULE_POLICY_REQUIREMENTS: dict[str, str] = {
    "M03": "aspect_policy",
    "M05": "declination_policy",
    "M06": "antiscia_policy",
    "M07": "composite_policy",
    "M08": "davison_policy",
    "M09": "relationship_chart_consonance_policy",
    "M10": "draconic_policy",
    "M11": "draconic_aspect_policy",
    "M13": "lot_policy",
    "M14": "secondary_symbolic_policy",
}


def _public_version() -> str:
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError as exc:
        raise WorkRequestError(
            "No puede resolverse la versión pública instalada de ALMAS."
        ) from exc


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WorkRequestError(f"{label} debe ser un objeto.")
    return value


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WorkRequestError(f"{label} debe ser numérico.")
    number = float(value)
    if not isfinite(number):
        raise WorkRequestError(f"{label} debe ser finito.")
    return number


def _normalize_subject(subject: Mapping[str, Any], index: int) -> dict[str, Any]:
    out = deepcopy(dict(subject))
    subject_id = out.get("id")
    if not isinstance(subject_id, str) or not subject_id:
        raise WorkRequestError(f"subjects[{index}].id es obligatorio.")
    birth_date = out.get("birth_date")
    if not isinstance(birth_date, str) or not birth_date:
        raise WorkRequestError(
            f"subjects[{index}].birth_date es obligatorio."
        )

    if out.get("latitude") is not None:
        latitude = _finite_number(
            out["latitude"], f"subjects[{index}].latitude"
        )
        if not -90.0 <= latitude <= 90.0:
            raise WorkRequestError(
                f"subjects[{index}].latitude fuera de rango."
            )
        out["latitude"] = latitude

    if out.get("longitude") is not None:
        longitude = _finite_number(
            out["longitude"], f"subjects[{index}].longitude"
        )
        if not -180.0 <= longitude <= 180.0:
            raise WorkRequestError(
                f"subjects[{index}].longitude fuera de rango."
            )
        out["longitude"] = longitude

    reliability = out.get("time_reliability")
    if reliability not in {"A", "B", "C", "D", None}:
        raise WorkRequestError(
            f"subjects[{index}].time_reliability debe ser A/B/C/D o null."
        )
    return out


def _normalize_situation_location(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    raw = _mapping(value, "situation_location")
    out = deepcopy(dict(raw))
    for field, minimum, maximum in (
        ("latitude", -90.0, 90.0),
        ("longitude", -180.0, 180.0),
    ):
        if out.get(field) is None:
            continue
        raw_value = out[field]
        if isinstance(raw_value, str):
            try:
                raw_value = float(raw_value)
            except ValueError as exc:
                raise WorkRequestError(
                    f"situation_location.{field} debe ser numérico."
                ) from exc
        number = _finite_number(
            raw_value, f"situation_location.{field}"
        )
        if not minimum <= number <= maximum:
            raise WorkRequestError(
                f"situation_location.{field} fuera de rango."
            )
        out[field] = number
    return out


def _validate_nonnegative_optional(
    policy: Mapping[str, Any],
    fields: tuple[str, ...],
    label: str,
) -> None:
    present = False
    for field in fields:
        if policy.get(field) is None:
            continue
        present = True
        value = _finite_number(policy[field], f"{label}.{field}")
        if value < 0:
            raise WorkRequestError(f"{label}.{field} no puede ser negativo.")
    if not present:
        raise WorkRequestError(
            f"{label} debe declarar al menos uno de: {', '.join(fields)}."
        )


def _expand_policy_preset(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Expande un preset sólo cuando el request lo selecciona explícitamente."""

    out = deepcopy(dict(bundle))
    preset_ref = out.get("preset_ref")
    if preset_ref is None:
        return out
    if preset_ref != RELATIONAL_ORB_PRESET_ID:
        raise WorkRequestError(
            f"analysis_policies.preset_ref desconocido: {preset_ref!r}."
        )
    if out.get("policy_bundle_id") != preset_ref:
        raise WorkRequestError(
            "Con preset_ref, policy_bundle_id debe coincidir con el preset."
        )

    protected = set(MODULE_POLICY_REQUIREMENTS.values())
    inline_overrides = sorted(protected & set(out))
    if inline_overrides:
        raise WorkRequestError(
            "Un preset no admite overrides inline de políticas: "
            + ", ".join(inline_overrides)
        )

    preset = load_relational_orb_baseline_policy()
    policies = preset.get("analysis_policies")
    if not isinstance(policies, Mapping):
        raise WorkRequestError("El preset relacional no contiene analysis_policies.")

    expanded = {
        "schema_version": out.get("schema_version"),
        "policy_bundle_id": out.get("policy_bundle_id"),
        "preset_ref": preset_ref,
        "preset_status": preset.get("status"),
        "preset_epistemic_class": preset.get("epistemic_class"),
        "preset_external_validation_status": preset.get(
            "external_validation_status"
        ),
    }
    expanded.update(deepcopy(dict(policies)))
    return expanded


def _validate_policy_bundle(
    bundle: Mapping[str, Any],
    required_modules: set[str],
) -> None:
    if bundle.get("schema_version") != POLICY_BUNDLE_SCHEMA_VERSION:
        raise WorkRequestError(
            "analysis_policies.schema_version debe ser 1.0.0."
        )
    bundle_id = bundle.get("policy_bundle_id")
    if not isinstance(bundle_id, str) or not bundle_id.strip():
        raise WorkRequestError(
            "analysis_policies.policy_bundle_id es obligatorio."
        )

    aspect = bundle.get("aspect_policy")
    if "M03" in required_modules and isinstance(aspect, Mapping):
        validate_declared_aspect_policy(aspect)

    draconic_aspect = bundle.get("draconic_aspect_policy")
    if "M11" in required_modules and isinstance(
        draconic_aspect, Mapping
    ):
        validate_declared_aspect_policy(draconic_aspect)

    relchart = bundle.get("relationship_chart_consonance_policy")
    if "M09" in required_modules and isinstance(relchart, Mapping):
        rel_aspects = relchart.get("aspect_policy")
        if not isinstance(rel_aspects, Mapping) or not rel_aspects:
            raise WorkRequestError(
                "relationship_chart_consonance_policy.aspect_policy es obligatorio."
            )
        validate_declared_aspect_policy(rel_aspects)

    declination = bundle.get("declination_policy")
    if "M05" in required_modules and isinstance(declination, Mapping):
        _validate_nonnegative_optional(
            declination,
            ("parallel_orb", "contra_parallel_orb"),
            "declination_policy",
        )

    antiscia = bundle.get("antiscia_policy")
    if "M06" in required_modules and isinstance(antiscia, Mapping):
        _validate_nonnegative_optional(
            antiscia,
            ("antiscia_orb", "contra_antiscia_orb"),
            "antiscia_policy",
        )

    for policy_name, expected in NORMATIVE_DEFAULTS.items():
        module_id = next(
            (
                module
                for module, name in MODULE_POLICY_REQUIREMENTS.items()
                if name == policy_name
            ),
            None,
        )
        if module_id not in required_modules:
            continue
        supplied = bundle.get(policy_name)
        if not isinstance(supplied, Mapping):
            continue
        mismatched = [
            key
            for key, expected_value in expected.items()
            if supplied.get(key) != expected_value
        ]
        if mismatched:
            raise WorkRequestError(
                f"{policy_name} diverge de la convención normativa vigente: "
                + ", ".join(sorted(mismatched))
            )


def assess_work_request(envelope: Mapping[str, Any]) -> dict[str, Any]:
    """Evalúa si un ALMAS_WORK_REQUEST puede convertirse en raw_input.

    No calcula astrología y no completa orbes ausentes.
    """

    if envelope.get("case_title") is not None and not isinstance(
        envelope.get("case_title"), str
    ):
        raise WorkRequestError("case_title debe ser string cuando se declara.")

    request = _mapping(envelope.get("request"), "request")
    if request.get("format") != WORK_REQUEST_FORMAT:
        raise WorkRequestError(
            f"request.format debe ser {WORK_REQUEST_FORMAT}."
        )
    if request.get("type") != SUPPORTED_TYPE:
        raise WorkRequestError("Sólo se admite type=RELATIONAL.")

    installed_version = _public_version()
    requested_version = request.get("public_version")
    if requested_version != installed_version:
        raise WorkRequestError(
            "Versión del request incompatible con el motor instalado: "
            f"{requested_version!r} != {installed_version!r}."
        )

    subjects = request.get("subjects")
    if not isinstance(subjects, list) or len(subjects) != 2:
        raise WorkRequestError(
            "request.subjects debe contener exactamente dos sujetos."
        )
    normalized_subjects = [
        _normalize_subject(_mapping(item, f"subjects[{index}]"), index)
        for index, item in enumerate(subjects)
    ]

    profile = resolve_analysis_profile(request.get("analysis_profile"))
    required_modules = set(profile["required_modules"])
    profile_supported = profile["profile_id"] == "FULL_ASTROLOGY"

    supplied_bundle = request.get("analysis_policies")
    bundle: dict[str, Any]
    if supplied_bundle is None:
        bundle = {
            "schema_version": POLICY_BUNDLE_SCHEMA_VERSION,
            "policy_bundle_id": None,
        }
    else:
        bundle = deepcopy(
            dict(_mapping(supplied_bundle, "analysis_policies"))
        )
        try:
            bundle = _expand_policy_preset(bundle)
        except WorkRequestError as exc:
            bundle["_preset_error"] = str(exc)

    # Las convenciones de método congeladas sí pueden completarse
    # determinísticamente. Si el usuario suministra una variante distinta,
    # se conserva para que la validación del módulo correspondiente decida.
    for name, value in NORMATIVE_DEFAULTS.items():
        bundle.setdefault(name, deepcopy(dict(value)))

    missing_policies: list[str] = []
    for module_id, policy_name in MODULE_POLICY_REQUIREMENTS.items():
        if module_id not in required_modules:
            continue
        value = bundle.get(policy_name)
        if not isinstance(value, Mapping) or not value:
            missing_policies.append(policy_name)

    bundle_header_valid = (
        bundle.get("schema_version") == POLICY_BUNDLE_SCHEMA_VERSION
        and isinstance(bundle.get("policy_bundle_id"), str)
        and bool(str(bundle.get("policy_bundle_id")).strip())
    )

    policy_errors: list[str] = []
    preset_error = bundle.pop("_preset_error", None)
    if isinstance(preset_error, str):
        policy_errors.append(preset_error)

    if bundle_header_valid and preset_error is None:
        try:
            _validate_policy_bundle(bundle, required_modules)
        except (ValueError, WorkRequestError) as exc:
            policy_errors.append(str(exc))
    else:
        if bundle.get("schema_version") != POLICY_BUNDLE_SCHEMA_VERSION:
            policy_errors.append(
                "analysis_policies.schema_version debe ser 1.0.0."
            )
        if not isinstance(bundle.get("policy_bundle_id"), str) or not str(
            bundle.get("policy_bundle_id") or ""
        ).strip():
            policy_errors.append(
                "analysis_policies.policy_bundle_id es obligatorio."
            )

    if not profile_supported:
        policy_errors.append(
            "El puente relacional 1.0.0 sólo declara execution_ready para FULL_ASTROLOGY."
        )

    executable = (
        profile_supported
        and not missing_policies
        and not policy_errors
    )

    return {
        "public_version": installed_version,
        "format": WORK_REQUEST_FORMAT,
        "type": SUPPORTED_TYPE,
        "analysis_profile": profile["profile_id"],
        "analysis_mode": profile["analysis_mode"],
        "bridge_profile_supported": profile_supported,
        "subjects": normalized_subjects,
        "analysis_policies": bundle,
        "required_modules": sorted(required_modules),
        "missing_policies": sorted(set(missing_policies)),
        "policy_errors": policy_errors,
        "execution_ready": executable,
        "implicit_orbs_used": False,
        "case_fitting_used": False,
        "preset_ref": bundle.get("preset_ref"),
    }


def build_raw_input_from_work_request(
    envelope: Mapping[str, Any],
    *,
    require_execution_ready: bool = True,
) -> dict[str, Any]:
    """Convierte la envolvente del panel al raw_input del orquestador."""

    assessment = assess_work_request(envelope)
    if require_execution_ready and not assessment["execution_ready"]:
        details = []
        if assessment["missing_policies"]:
            details.append(
                "políticas ausentes: "
                + ", ".join(assessment["missing_policies"])
            )
        if assessment["policy_errors"]:
            details.append(
                "errores de política: "
                + "; ".join(assessment["policy_errors"])
            )
        raise WorkRequestError(
            "ALMAS_WORK_REQUEST no está listo para ejecución; "
            + " | ".join(details)
        )

    request = _mapping(envelope.get("request"), "request")
    raw: dict[str, Any] = {
        "mode": assessment["analysis_mode"],
        "analysis_profile": assessment["analysis_profile"],
        "subjects": deepcopy(assessment["subjects"]),
        "events": deepcopy(request.get("events") or []),
    }

    research_question = request.get("research_question")
    if isinstance(research_question, str) and research_question.strip():
        raw["research_question"] = research_question.strip()

    situation = _normalize_situation_location(
        request.get("situation_location")
    )
    if situation is not None:
        raw["situation_location"] = situation

    bundle = assessment["analysis_policies"]
    raw["analysis_policy_bundle"] = {
        "schema_version": bundle.get("schema_version"),
        "policy_bundle_id": bundle.get("policy_bundle_id"),
        "preset_ref": bundle.get("preset_ref"),
        "preset_status": bundle.get("preset_status"),
        "preset_epistemic_class": bundle.get("preset_epistemic_class"),
        "preset_external_validation_status": bundle.get(
            "preset_external_validation_status"
        ),
        "implicit_orbs_used": False,
        "case_fitting_used": False,
    }
    for name in MODULE_POLICY_REQUIREMENTS.values():
        value = bundle.get(name)
        if isinstance(value, Mapping) and value:
            raw[name] = deepcopy(dict(value))

    # Convenciones normativas que no aparecen en MODULE_POLICY_REQUIREMENTS
    # quedarían aquí en futuras versiones sin necesidad de cambiar el contrato.
    for name in NORMATIVE_DEFAULTS:
        value = bundle.get(name)
        if isinstance(value, Mapping) and value:
            raw[name] = deepcopy(dict(value))

    return raw
