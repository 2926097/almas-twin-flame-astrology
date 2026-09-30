"""Evaluación documental de surrender según la política ALMAS congelada."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping


MIN_WINDOW_DAYS = 30
COMPONENTS = (
    "cessation_of_pursuit",
    "boundary_assertion",
    "behavioral_decentering",
)
COUNTEREVIDENCE = {
    "CONTINUED_PURSUIT",
    "EXPLICIT_STRATEGIC_SILENCE_TO_PROVOKE_RESPONSE",
    "REPEATED_CONFLICT_REOPENING",
    "OUTCOME_BARGAINING",
    "CONTROL_ATTEMPT",
}
ACTIVITY_DOMAINS = {
    "WORK", "HEALTH", "FAMILY", "FRIENDSHIP", "LEARNING", "CREATIVE", "COMMUNITY"
}


def _day_span(start: str, end: str) -> int:
    try:
        return (date.fromisoformat(end) - date.fromisoformat(start)).days
    except (TypeError, ValueError) as exc:
        raise ValueError("assessment dates must be ISO 8601 calendar dates.") from exc


def _component(state: str, refs: list[str], reason: str) -> dict[str, Any]:
    return {"state": state, "evidence_refs": sorted(set(refs)), "reason": reason}


def assess_surrender(actor: str, assessment: Mapping[str, Any]) -> dict[str, Any]:
    """Return candidate/stabilized states without inferring private motivation."""
    if actor not in {"A", "B"}:
        raise ValueError("actor must be A or B.")
    start, end = assessment.get("assessment_start"), assessment.get("assessment_end")
    days = _day_span(start, end)
    if days < 0:
        raise ValueError("assessment_end must not precede assessment_start.")

    pursuit = assessment.get("pursuit_ledger", {})
    if not isinstance(pursuit, Mapping):
        raise ValueError("pursuit_ledger must be an object.")
    before_refs = list(pursuit.get("prior_pursuit_attempt_refs", []))
    after_refs = list(pursuit.get("post_window_pursuit_refs", []))
    opportunities = list(pursuit.get("contact_opportunity_refs", []))
    if after_refs:
        s1 = _component("ABSENT", after_refs, "Pursuit consta dentro de la ventana evaluada.")
    elif (
        days >= MIN_WINDOW_DAYS
        and pursuit.get("contact_log_complete") is True
        and len(set(before_refs)) >= 2
        and opportunities
    ):
        s1 = _component("PRESENT", before_refs + opportunities,
                         "No se registran nuevos intentos durante una ventana completa con oportunidades documentadas.")
    else:
        s1 = _component("NOT_EVALUABLE", [],
                         "Falta línea base, oportunidad, log completo o ventana mínima.")

    boundary_refs = list(assessment.get("boundary_assertion_refs", []))
    s2 = (
        _component("PRESENT", boundary_refs, "Afirmación o acto de límite documentado por el actor.")
        if boundary_refs else
        _component("NOT_EVALUABLE", [], "No se aporta un acto o declaración directa de límite.")
    )

    activities = assessment.get("decentering_activities", [])
    if not isinstance(activities, list):
        raise ValueError("decentering_activities must be a list.")
    accepted_activities = [
        item for item in activities
        if isinstance(item, Mapping)
        and item.get("fact_id")
        and item.get("actor") == actor
        and item.get("independent_of_other_actor_response") is True
        and item.get("domain") in ACTIVITY_DOMAINS
    ]
    activity_refs = [item["fact_id"] for item in accepted_activities]
    if len(activity_refs) != len(set(activity_refs)):
        raise ValueError("decentering activity fact_id values must be unique.")
    activity_dates = [date.fromisoformat(item["occurred_on"]) for item in accepted_activities]
    domains = {item["domain"] for item in accepted_activities}
    if len(activity_refs) >= 2 and len(domains) >= 2 and len(activity_dates) >= 2:
        activity_span = (max(activity_dates) - min(activity_dates)).days
    else:
        activity_span = 0
    if (
        len(set(activity_refs)) >= 2
        and len(domains) >= 2
        and activity_span >= MIN_WINDOW_DAYS
    ):
        s3 = _component("PRESENT", activity_refs,
                         "Hay acciones documentadas en dominios distintos durante la ventana y no condicionadas a la respuesta del otro actor.")
    else:
        s3 = _component("NOT_EVALUABLE", [],
                         "Se requieren dos dominios de actividad documentados a lo largo de 30 días y separados de la respuesta del otro actor.")

    components = {
        "cessation_of_pursuit": s1,
        "boundary_assertion": s2,
        "behavioral_decentering": s3,
    }
    contrary = assessment.get("counterevidence", [])
    if not isinstance(contrary, list):
        raise ValueError("counterevidence must be a list.")
    retained = []
    for item in contrary:
        if not isinstance(item, Mapping) or item.get("kind") not in COUNTEREVIDENCE:
            raise ValueError("counterevidence kind is not registered.")
        refs = item.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("counterevidence requires evidence_refs.")
        if item["kind"] == "EXPLICIT_STRATEGIC_SILENCE_TO_PROVOKE_RESPONSE" and item.get("actor_self_reported_intent") is not True:
            raise ValueError("strategic silence requires the actor's explicit self-report; intent is not inferred.")
        retained.append({"kind": item["kind"], "evidence_refs": sorted(set(refs))})

    present = [key for key, item in components.items() if item["state"] == "PRESENT"]
    base_candidate = (
        len(present) >= 2
        and any(key in present for key in ("boundary_assertion", "behavioral_decentering"))
    )
    if retained:
        candidate_status = "CONTRADICTED"
    elif base_candidate:
        candidate_status = "COMPATIBLE"
    elif not present:
        candidate_status = "NOT_EVALUABLE"
    else:
        candidate_status = "INSUFFICIENT"

    preregistration_ref = assessment.get("preregistration_ref")
    stabilized = (
        set(present) == set(COMPONENTS)
        and days >= MIN_WINDOW_DAYS
        and isinstance(preregistration_ref, str)
        and bool(preregistration_ref)
        and not retained
    )
    stabilized_status = "SUPPORTED" if stabilized else (
        "CONTRADICTED" if retained else "INSUFFICIENT"
    )

    return {
        "actor": actor,
        "policy_id": "ALMAS_SURRENDER_OPERATIONAL_POLICY_V1",
        "assessment_window_days": days,
        "components": components,
        "candidate": {
            "phase_id": "surrender_candidate",
            "status": candidate_status,
            "component_refs": present,
        },
        "stabilized": {
            "phase_id": "surrender_stabilized",
            "status": stabilized_status,
            "preregistration_ref": preregistration_ref,
        },
        "counterevidence": retained,
        "metaphysical_claim": False,
        "private_intent_inferred": False,
    }
