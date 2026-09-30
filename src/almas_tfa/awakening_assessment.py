"""Evaluación biográfica y documental de criterios de awakening."""
from __future__ import annotations
from datetime import date
from typing import Any, Mapping

CRITERIA = (
    "explicit_reframing",
    "recognition_of_previous_pattern",
    "sustained_behavioral_change",
    "voluntary_reengagement",
    "increased_congruence_between_words_and_actions",
)


def assess_awakening(actor: str, assessment: Mapping[str, Any]) -> dict[str, Any]:
    """Assess observable biographical criteria; astrology is never an input."""
    if actor not in {"A", "B"}:
        raise ValueError("actor must be A or B.")
    criteria = assessment.get("criteria")
    if not isinstance(criteria, Mapping) or set(criteria) != set(CRITERIA):
        raise ValueError("criteria must contain exactly the five registered criteria.")
    normalized = {}
    for name in CRITERIA:
        item = criteria[name]
        if not isinstance(item, Mapping):
            raise ValueError(f"{name} must be an object.")
        state = item.get("state")
        refs = item.get("evidence_refs")
        if state not in {"SUPPORTED", "CONTRADICTED", "NOT_EVALUABLE"}:
            raise ValueError(f"invalid state for {name}.")
        if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref for ref in refs):
            raise ValueError(f"{name} requires evidence_refs as strings.")
        if state == "SUPPORTED" and not refs:
            raise ValueError(f"{name} requires direct biographical evidence.")
        if len(refs) != len(set(refs)):
            raise ValueError(f"duplicate evidence reference for {name}.")
        normalized[name] = {"state": state, "evidence_refs": sorted(refs)}

    sustained = criteria["sustained_behavioral_change"]
    observations = sustained.get("observations", [])
    if not isinstance(observations, list):
        raise ValueError("sustained behavioral change observations must be a list.")
    dates = []
    for observation in observations:
        if not isinstance(observation, Mapping) or observation.get("actor") != actor:
            continue
        if observation.get("behavior_changed") is not True or not observation.get("fact_id"):
            continue
        dates.append(date.fromisoformat(observation["occurred_on"]))
    if len({observation.get("fact_id") for observation in observations if isinstance(observation, Mapping) and observation.get("actor") == actor and observation.get("behavior_changed") is True}) != sum(
        1 for observation in observations if isinstance(observation, Mapping) and observation.get("actor") == actor and observation.get("behavior_changed") is True
    ):
        raise ValueError("behavior observation fact_id values must be unique.")
    if normalized["sustained_behavioral_change"]["state"] == "SUPPORTED":
        span = (max(dates) - min(dates)).days if len(dates) >= 2 else 0
        if len(dates) < 2 or span < 30:
            normalized["sustained_behavioral_change"] = {"state": "NOT_EVALUABLE", "evidence_refs": []}

    contrary = assessment.get("counterevidence", [])
    if not isinstance(contrary, list):
        raise ValueError("counterevidence must be a list.")
    for item in contrary:
        if not isinstance(item, Mapping) or not item.get("kind") or not isinstance(item.get("evidence_refs"), list) or not item["evidence_refs"]:
            raise ValueError("counterevidence requires a kind and evidence_refs.")
    supported = [key for key, item in normalized.items() if item["state"] == "SUPPORTED"]
    has_contradicted = any(item["state"] == "CONTRADICTED" for item in normalized.values()) or bool(contrary)
    if has_contradicted:
        status = "CONTRADICTED"
    elif len(supported) == len(CRITERIA):
        status = "SUPPORTED"
    elif all(item["state"] == "NOT_EVALUABLE" for item in normalized.values()):
        status = "NOT_EVALUABLE"
    else:
        status = "INSUFFICIENT"
    return {
        "actor": actor,
        "policy_id": "ALMAS_AWAKENING_OPERATIONAL_POLICY_V1",
        "status": status,
        "criteria": normalized,
        "counterevidence": [{"kind": item["kind"], "evidence_refs": sorted(set(item["evidence_refs"]))} for item in contrary],
        "astrology_established_awakening": False,
        "metaphysical_claim": False,
    }
