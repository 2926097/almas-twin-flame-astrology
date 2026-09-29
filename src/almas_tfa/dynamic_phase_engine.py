"""Motor documental de candidatos de fase. No analiza texto ni astrología."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

PHASE_RULES = {
    "EXPLICIT_RECOGNITION": {
        "phase_id": "recognition", "scope": "ACTOR",
        "required_actor_evidence": 1,
        "meaning": "El actor declara explícitamente que el encuentro o conexión le resulta significativo.",
    },
    "EXPLICIT_BOUNDARY": {
        "phase_id": "boundary_assertion", "scope": "ACTOR",
        "required_actor_evidence": 1,
        "meaning": "El actor declara o ejecuta un límite identificable de contacto, disponibilidad o trato.",
    },
    "MUTUAL_PAUSE": {
        "phase_id": "separation_or_suspension", "scope": "RELATION",
        "required_actor_evidence": 2,
        "meaning": "Ambos actores documentan acuerdo explícito de pausa en la modalidad de contacto definida.",
    },
    "MUTUAL_RESUMPTION": {
        "phase_id": "bilateral_reengagement", "scope": "RELATION",
        "required_actor_evidence": 2,
        "meaning": "Ambos actores participan voluntariamente en una interacción reanudada, documentada por fuentes directas.",
    },
    "EXPLICIT_TERMINATION": {
        "phase_id": "closure", "scope": "ACTOR",
        "required_actor_evidence": 1,
        "meaning": "El actor declara explícitamente que termina la modalidad de contacto especificada.",
    },
}


def _actor_slot(actor: str) -> str:
    return {"A": "actor_a_phase", "B": "actor_b_phase"}[actor]


def _evidence_quality(items: list[Mapping[str, Any]], witness_count: int) -> str:
    direct = [
        item for item in items
        if item.get("kind") in {"DOCUMENTARY", "BEHAVIORAL"}
        and item.get("source_ref")
    ]
    direct_actors = {item.get("actor") for item in direct if item.get("actor") in {"A", "B"}}
    if witness_count and len(direct_actors) >= witness_count:
        return "DIRECT_MULTI_ACTOR" if witness_count > 1 else "DIRECT_DOCUMENTARY"
    if direct:
        return "DIRECT_PARTIAL"
    if any(item.get("kind") == "SELF_REPORT" for item in items):
        return "SELF_REPORT_ONLY"
    return "NO_DIRECT_EVIDENCE"


def _before_state(event: Mapping[str, Any]) -> dict[str, Any] | None:
    before = event.get("phase_before")
    return deepcopy(dict(before)) if isinstance(before, Mapping) else None


def evaluate_dynamic_phase_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Evalúa únicamente códigos de conducta documental previamente declarados.

    No infiere códigos desde texto libre. Un registro de evento no puede
    promoverse desde el mapeo doctrinal; los códigos desconocidos fallan cerrado.
    """
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise ValueError("event_id obligatorio.")
    behavior = event.get("behavior_code")
    rule = PHASE_RULES.get(behavior)
    before = _before_state(event)
    evidence = event.get("evidence")
    if not isinstance(evidence, list):
        evidence = []
    contrary = event.get("counterevidence")
    if not isinstance(contrary, list):
        contrary = []

    if rule is None:
        return {
            "event_id": event_id,
            "phase_before": before,
            "phase_candidate": None,
            "phase_after": before,
            "evidence_strength": "NO_DIRECT_EVIDENCE",
            "counterevidence": [item.get("fact_id") for item in contrary if isinstance(item, Mapping)],
            "status": "NOT_EVALUABLE",
            "rule_id": None,
            "automatic_text_interpretation": False,
        }

    actor = event.get("actor")
    expected_scope = rule["scope"]
    if expected_scope == "ACTOR" and actor not in {"A", "B"}:
        scope_valid = False
        witnesses: set[str] = set()
    elif expected_scope == "RELATION" and actor != "BOTH":
        scope_valid = False
        witnesses = set()
    else:
        scope_valid = True
        witnesses = {
            item.get("actor") for item in evidence
            if isinstance(item, Mapping)
            and item.get("actor") in {"A", "B"}
            and item.get("kind") in {"DOCUMENTARY", "BEHAVIORAL"}
            and item.get("source_ref")
        }
    quality = _evidence_quality(evidence, rule["required_actor_evidence"])
    refs = [
        item.get("fact_id") for item in evidence
        if isinstance(item, Mapping) and isinstance(item.get("fact_id"), str)
        and item.get("kind") in {"DOCUMENTARY", "BEHAVIORAL"}
        and item.get("source_ref")
    ]
    if not scope_valid or len(witnesses) < rule["required_actor_evidence"] or not refs:
        status = "INSUFFICIENT"
    elif contrary:
        status = "CONTRADICTED"
    else:
        status = "SUPPORTED"

    phase_candidate = {
        "phase_id": rule["phase_id"],
        "scope": expected_scope if expected_scope == "RELATION" else actor,
        "status": status,
        "evidence_refs": sorted(set(refs)),
        "rule_id": f"OBSERVED_BEHAVIOR:{behavior}:V1",
        "interpretation": rule["meaning"],
    }
    if status == "SUPPORTED":
        phase_after = {
            "phase_id": rule["phase_id"],
            "status": "SUPPORTED",
            "evidence_refs": sorted(set(refs)),
        }
    else:
        phase_after = before

    return {
        "event_id": event_id,
        "phase_before": before,
        "phase_candidate": phase_candidate,
        "phase_after": phase_after,
        "evidence_strength": quality,
        "counterevidence": [item.get("fact_id") for item in contrary if isinstance(item, Mapping)],
        "status": status,
        "rule_id": phase_candidate["rule_id"],
        "automatic_text_interpretation": False,
    }
