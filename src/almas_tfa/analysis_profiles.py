from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping


POLICY_RESOURCE = "analysis-profile-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_analysis_profile_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_ANALYSIS_PROFILES_V1":
        raise ValueError("Política de perfiles de análisis desconocida.")
    return policy


def resolve_analysis_profile(
    requested: Any,
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if policy is None:
        policy = load_analysis_profile_policy()

    profile_id = (
        str(requested).strip().upper()
        if isinstance(requested, str) and requested.strip()
        else str(policy["default_profile"])
    )
    profiles = policy.get("profiles")
    if not isinstance(profiles, Mapping) or profile_id not in profiles:
        raise ValueError(f"analysis_profile desconocido: {profile_id}.")

    raw = profiles[profile_id]
    if not isinstance(raw, Mapping):
        raise ValueError(f"Perfil inválido: {profile_id}.")

    required = {str(value) for value in raw.get("required_modules", [])}
    optional = {str(value) for value in raw.get("optional_modules", [])}
    excluded = {str(value) for value in raw.get("excluded_modules", [])}

    if required & optional or required & excluded or optional & excluded:
        raise ValueError(f"{profile_id}: módulos solapados entre clases.")

    return {
        "profile_id": profile_id,
        "analysis_mode": str(raw.get("analysis_mode") or "FULL"),
        "required_modules": sorted(required),
        "optional_modules": sorted(optional),
        "excluded_modules": sorted(excluded),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
    }


def profile_trace_assessment(
    trace: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Clasifica missingness de ejecución según el alcance elegido."""

    required = set(profile["required_modules"])
    optional = set(profile["optional_modules"])
    excluded = set(profile["excluded_modules"])

    not_evaluable = set(trace.get("not_evaluable_modules", []))
    skipped = set(trace.get("skipped_modules", []))
    not_applicable = set(trace.get("not_applicable_modules", []))
    completed = set(trace.get("completed_modules", []))

    required_not_evaluable = sorted(required & not_evaluable)
    required_skipped = sorted(required & skipped)

    ignored_not_evaluable = sorted((optional | excluded) & not_evaluable)
    ignored_skipped = sorted((optional | excluded) & skipped)
    profile_not_applicable = sorted(excluded)

    # Un módulo requerido que el orchestrator declaró NOT_APPLICABLE continúa
    # siendo una carencia del perfil, no se silencia.
    required_not_applicable = sorted(required & not_applicable)

    unexecuted_required = sorted(
        module_id
        for module_id in required
        if module_id not in completed
        and module_id not in not_evaluable
        and module_id not in skipped
        and module_id not in not_applicable
    )

    return {
        "required_not_evaluable": required_not_evaluable,
        "required_skipped": required_skipped,
        "required_not_applicable": required_not_applicable,
        "unexecuted_required": unexecuted_required,
        "ignored_not_evaluable": ignored_not_evaluable,
        "ignored_skipped": ignored_skipped,
        "profile_not_applicable": profile_not_applicable,
    }
