from __future__ import annotations

from importlib import resources
import json
import re
from typing import Any, Mapping

from .px_v3_candidates import load_px_v3_candidate_registry


POLICY_RESOURCE = "px-v3-activation-firewall-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_px_v3_activation_firewall_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        POLICY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_PX_V3_ACTIVATION_FIREWALL_V1":
        raise ValueError("Política S9 de activación PX v3 desconocida.")
    return policy


def _minor_line(version: str) -> str:
    if not isinstance(version, str):
        raise ValueError("version debe ser string.")
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
    if match is None:
        raise ValueError("version debe seguir SemVer MAJOR.MINOR.PATCH.")
    return f"{match.group(1)}.{match.group(2)}"


def evaluate_px_v3_activation_firewall(
    current_version: str,
    *,
    registry: Mapping[str, Any] | None = None,
    promotion_result: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Audita que PX v3 no pueda activarse dentro de la línea 1.15."""

    if policy is None:
        policy = load_px_v3_activation_firewall_policy()
    if registry is None:
        registry = load_px_v3_candidate_registry()

    release_line = _minor_line(current_version)
    expected_line = str(policy["release_line"])
    if release_line != expected_line:
        return {
            "state": "OUTSIDE_RELEASE_LINE",
            "policy_id": policy["policy_id"],
            "current_version": current_version,
            "release_line": release_line,
            "expected_release_line": expected_line,
            "px_v3_active": False,
            "activation_permitted": False,
            "requires_new_version_policy": True,
            "operational_px_engine": policy["operational_px_engine"],
            "metaphysical_probability": False,
        }

    records = registry.get("records")
    if not isinstance(records, list):
        raise ValueError("registry.records debe ser una lista.")
    validated = registry.get("validated_candidate_ids")
    if not isinstance(validated, list):
        raise ValueError("registry.validated_candidate_ids debe ser lista.")

    promotion_eligible = bool(
        isinstance(promotion_result, Mapping)
        and promotion_result.get("state") == "PROMOTION_ELIGIBLE"
    )

    violations = []
    if records:
        violations.append("PX_V3_CANDIDATE_RECORDS_PRESENT_IN_1_15")
    if validated:
        violations.append("VALIDATED_PX_V3_IDS_PRESENT_IN_1_15")
    if registry.get("scoring_enabled") is not False:
        violations.append("REGISTRY_SCORING_ENABLED")
    if registry.get("weighting_enabled") is not False:
        violations.append("REGISTRY_WEIGHTING_ENABLED")
    if registry.get("ontology_enabled") is not False:
        violations.append("REGISTRY_ONTOLOGY_ENABLED")

    state = (
        "NO_ACTIVE_PX_V3_CANDIDATE"
        if not violations
        else "BLOCKED_RELEASE_FIREWALL"
    )

    return {
        "state": state,
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "current_version": current_version,
        "release_line": release_line,
        "operational_px_engine": policy["operational_px_engine"],
        "px_v3_candidate_record_count": len(records),
        "validated_px_v3_candidate_count": len(validated),
        "promotion_eligible_input_present": promotion_eligible,
        "promotion_eligible_causes_activation": False,
        "violations": violations,
        "px_v3_active": False,
        "activation_permitted": False,
        "runtime_activation": False,
        "automatic_registry_mutation": False,
        "manual_new_version_required": True,
        "new_release_audit_required": True,
        "new_public_contract_validation_required": True,
        "px_v2_remains_operational": True,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
