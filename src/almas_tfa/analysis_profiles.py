from __future__ import annotations

import json
from importlib import resources
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
    value: Any,
    *,
    policy: Mapping[str, Any] | None = None,
) -> str:
    if policy is None:
        policy = load_analysis_profile_policy()
    profile = (
        str(value)
        if isinstance(value, str) and value
        else str(policy["default_profile"])
    )
    profiles = policy.get("profiles")
    if not isinstance(profiles, Mapping) or profile not in profiles:
        raise ValueError(f"analysis_profile desconocido: {profile!r}.")
    return profile


def classify_trace_for_profile(
    trace: Mapping[str, Any],
    profile: str,
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if policy is None:
        policy = load_analysis_profile_policy()
    profile = resolve_analysis_profile(profile, policy=policy)
    spec = policy["profiles"][profile]

    optional_ne = set(spec["non_degrading_not_evaluable_modules"])
    optional_skipped = set(spec["non_degrading_skipped_modules"])

    not_evaluable = set(trace.get("not_evaluable_modules", []))
    skipped = set(trace.get("skipped_modules", []))

    optional_ne_actual = sorted(not_evaluable & optional_ne)
    required_ne = sorted(not_evaluable - optional_ne)
    optional_skipped_actual = sorted(skipped & optional_skipped)
    required_skipped = sorted(skipped - optional_skipped)

    return {
        "analysis_profile": profile,
        "required_not_evaluable_modules": required_ne,
        "optional_not_evaluable_modules": optional_ne_actual,
        "required_skipped_modules": required_skipped,
        "optional_skipped_modules": optional_skipped_actual,
        "profile_description": spec["description"],
        "policy_id": policy["policy_id"],
    }
