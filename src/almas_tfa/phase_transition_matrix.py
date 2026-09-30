"""Matriz de evidencia por transición; símbolos y doctrina no sustituyen hechos."""
from __future__ import annotations
from typing import Any, Mapping

LAYER_NAMES = (
    "documentary", "behavioral", "astrological_structural", "astrological_temporal",
    "doctrinal", "contemporary_use", "counterevidence",
)
VALID_STATES = {"SUPPORTED", "COMPATIBLE", "INSUFFICIENT", "CONTRADICTED", "NOT_EVALUABLE"}
FACTUAL_SUPPORT_LAYERS = {"documentary", "behavioral"}


def build_phase_transition_matrix(
    transition_id: str,
    source_phase: str,
    target_phase: str,
    why_proposed: str,
    layers: Mapping[str, Any],
    unresolved: list[str] | None = None,
) -> dict[str, Any]:
    """Return a traceable matrix and a conservative final status."""
    if not all(isinstance(value, str) and value.strip() for value in (transition_id, source_phase, target_phase, why_proposed)):
        raise ValueError("transition identity, phases, and rationale are required.")
    if not isinstance(layers, Mapping) or set(layers) != set(LAYER_NAMES):
        raise ValueError("layers must contain exactly the seven registered evidence categories.")
    normalized = {}
    for name in LAYER_NAMES:
        item = layers[name]
        if not isinstance(item, Mapping):
            raise ValueError(f"{name} must be an object.")
        state, refs, rationale = item.get("status"), item.get("evidence_refs"), item.get("rationale")
        if state not in VALID_STATES:
            raise ValueError(f"{name}.status is invalid.")
        if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref for ref in refs):
            raise ValueError(f"{name}.evidence_refs must be a list of non-empty strings.")
        if len(refs) != len(set(refs)):
            raise ValueError(f"{name}.evidence_refs must be unique.")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"{name}.rationale is required, including when evidence is unavailable.")
        if state == "SUPPORTED" and not refs:
            raise ValueError(f"{name}: SUPPORTED requires evidence references.")
        normalized[name] = {"status": state, "evidence_refs": sorted(refs), "rationale": rationale.strip()}

    unresolved = unresolved or []
    if not isinstance(unresolved, list) or any(not isinstance(value, str) or not value.strip() for value in unresolved):
        raise ValueError("unresolved must be a list of non-empty statements.")

    contrary = normalized["counterevidence"]
    factual = [normalized[key] for key in FACTUAL_SUPPORT_LAYERS]
    if contrary["status"] == "SUPPORTED" and contrary["evidence_refs"]:
        final = "CONTRADICTED"
    elif any(item["status"] == "CONTRADICTED" and item["evidence_refs"] for item in factual):
        final = "CONTRADICTED"
    elif any(item["status"] == "SUPPORTED" and item["evidence_refs"] for item in factual):
        final = "SUPPORTED"
    elif any(item["status"] == "COMPATIBLE" and item["evidence_refs"] for item in factual):
        final = "COMPATIBLE"
    elif unresolved or any(normalized[key]["evidence_refs"] for key in LAYER_NAMES if key not in FACTUAL_SUPPORT_LAYERS | {"counterevidence"}):
        final = "INSUFFICIENT"
    else:
        final = "NOT_EVALUABLE"

    return {
        "transition_id": transition_id,
        "source_phase": source_phase,
        "target_phase": target_phase,
        "why_proposed": why_proposed.strip(),
        **normalized,
        "unresolved": [value.strip() for value in unresolved],
        "final_status": final,
        "astrology_or_doctrine_promoted_factual_transition": False,
    }
