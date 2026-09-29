"""Compara orden documental con secuencias registradas; nunca infiere causalidad."""
from __future__ import annotations
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping

_ROOT = Path(__file__).resolve().parents[2]
_REGISTRY_PATH = _ROOT / "reference" / "doctrinal-sequence-models.json"
_REGISTRY = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
_MODELS = {model["model_id"]: model for model in _REGISTRY["models"]}


def _temporal_key(value: str) -> datetime:
    try:
        if "T" in value:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        else:
            return datetime.combine(date.fromisoformat(value), datetime.min.time(), tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise ValueError("occurred_at must be an ISO 8601 date or datetime.") from exc
    return value


def evaluate_doctrinal_sequence(model_id: str, observations: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Compare dated documentary phase observations with a frozen model order.

    The evaluator reports sequence fit and raw precedence only. A preceding
    surrender phase is never treated as a cause of awakening.
    """
    if model_id not in _MODELS:
        raise ValueError("model_id is not registered.")
    if not isinstance(observations, list):
        raise ValueError("observations must be a list.")
    model = _MODELS[model_id]
    rows = []
    for item in observations:
        if not isinstance(item, Mapping):
            raise ValueError("each observation must be an object.")
        phase_id, occurred_at, refs = item.get("phase_id"), item.get("occurred_at"), item.get("evidence_refs")
        if not isinstance(phase_id, str) or not phase_id:
            raise ValueError("phase_id is required.")
        if not isinstance(occurred_at, str):
            raise ValueError("occurred_at is required.")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref for ref in refs):
            raise ValueError("each observation requires evidence_refs.")
        _temporal_key(occurred_at)
        rows.append({"phase_id": phase_id, "occurred_at": occurred_at, "_sort_key": _temporal_key(occurred_at), "evidence_refs": sorted(set(refs))})
    rows.sort(key=lambda row: row["_sort_key"])
    observed_sequence = [row["phase_id"] for row in rows]

    expected = model["expected_sequence"]
    if not expected:
        match = "NOT_EVALUABLE"
        compatibility = "NOT_EVALUABLE"
    else:
        if observed_sequence == expected:
            match = "MATCH"
            compatibility = "COMPATIBLE"
        elif all(phase in expected for phase in observed_sequence) and [expected.index(phase) for phase in observed_sequence] == sorted(set(expected.index(phase) for phase in observed_sequence)):
            match = "INCOMPLETE"
            compatibility = "INSUFFICIENT"
        else:
            match = "MISMATCH"
            compatibility = "INCOMPATIBLE"

    surrender_dates = [row["occurred_at"] for row in rows if row["phase_id"] == "surrender_stabilized"]
    awakening_dates = [row["occurred_at"] for row in rows if row["phase_id"] == "awakening_candidate"]
    if not surrender_dates or not awakening_dates:
        precedence = "NOT_EVALUABLE"
    else:
        surrender_time = min(_temporal_key(value) for value in surrender_dates)
        awakening_time = min(_temporal_key(value) for value in awakening_dates)
        precedence = "BEFORE" if surrender_time < awakening_time else "AFTER" if surrender_time > awakening_time else "SAME_TIME"

    sequence_status = "SEQUENCE_SUPPORTED" if match == "MATCH" else (
        "NOT_EVALUABLE" if match == "NOT_EVALUABLE" else "INSUFFICIENT" if match == "INCOMPLETE" else "CONTRADICTED"
    )
    return {
        "model_id": model_id,
        "model_sequence_status": model["sequence_status"],
        "observed_sequence": observed_sequence,
        "temporal_precedence": {
            "earlier_phase": "surrender_stabilized",
            "later_phase": "awakening_candidate",
            "status": precedence,
        },
        "doctrinal_compatibility": compatibility,
        "sequence_match": match,
        "sequence_status": sequence_status,
        "ontology_status": "INSUFFICIENT",
        "twin_flame_demonstrated": False,
        "causal_status": "UNESTABLISHED",
    }
