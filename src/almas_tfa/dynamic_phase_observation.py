"""Validación semántica del enlace entre hechos y fase descriptiva."""

from __future__ import annotations

from typing import Any, Mapping


def validate_phase_observation_record(record: Mapping[str, Any]) -> None:
    """Exige que la fase descriptiva apunte a hechos, nunca a la doctrina.

    El schema JSON valida la forma. Esta comprobación resuelve la referencia
    entre arrays, que JSON Schema 2020-12 no puede cotejar dinámicamente.
    """
    facts = record.get("observed_facts")
    state = record.get("observed_state")
    if not isinstance(facts, list) or not facts:
        raise ValueError("observed_facts requiere al menos un hecho identificado.")
    if not isinstance(state, Mapping):
        raise ValueError("observed_state es obligatorio.")

    fact_ids = [
        fact.get("fact_id")
        for fact in facts
        if isinstance(fact, Mapping) and isinstance(fact.get("fact_id"), str)
    ]
    if len(fact_ids) != len(facts) or len(set(fact_ids)) != len(fact_ids):
        raise ValueError("fact_id debe existir y ser único en observed_facts.")

    evidence_refs = state.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise ValueError("observed_state debe referenciar hechos observados.")
    unknown = set(evidence_refs) - set(fact_ids)
    if unknown:
        raise ValueError(
            "observed_state.evidence_refs solo puede referenciar fact_id; "
            f"referencias sin hecho: {sorted(unknown)}"
        )
