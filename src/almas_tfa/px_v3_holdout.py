from __future__ import annotations

from hashlib import sha256
import json
from math import ceil
from statistics import mean, median
from typing import Any, Mapping, Sequence

from .external_control_cohorts import (
    load_external_recurrence_cohort_policy,
    validate_external_recurrence_cohort,
)
from .px_v3_candidates import (
    evaluate_px_v3_candidate,
    load_px_v3_candidate_freeze_policy,
)
from importlib import resources


POLICY_RESOURCE = "px-v3-holdout-evaluation-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_px_v3_holdout_evaluation_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        POLICY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_PX_V3_HOLDOUT_EVALUATION_V1":
        raise ValueError("Política S7 de evaluación holdout desconocida.")
    return policy


def _clean_external_sample_refs(
    cohort: Mapping[str, Any],
    *,
    cohort_policy: Mapping[str, Any],
) -> list[str]:
    refs = []
    for sample in cohort.get("samples", []):
        if not isinstance(sample, Mapping):
            continue
        if sample.get("validation_status") not in cohort_policy[
            "external_candidate_statuses"
        ]:
            continue
        if sample.get("selection_status") != "PREREGISTERED":
            continue
        if sample.get("contamination") is not False:
            continue
        if any(
            int(sample.get(field, 0)) != 0
            for field in (
                "forbidden_field_hits",
                "label_leakage_count",
                "narrative_leakage_count",
                "case_fitting_count",
            )
        ):
            continue
        snapshot = sample.get("recurrence_snapshot")
        if not isinstance(snapshot, Mapping):
            continue
        pillar = snapshot.get("pillar_attribution")
        if not isinstance(pillar, Mapping):
            continue
        if not isinstance(pillar.get("semantic_motifs"), Mapping):
            continue
        if not isinstance(pillar.get("recurrence_quality"), Mapping):
            continue
        ref = sample.get("sample_ref")
        if isinstance(ref, str) and ref:
            refs.append(ref)
    return refs


def _nearest_rank(values: Sequence[float], percentile: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("nearest-rank requiere valores.")
    rank = max(1, ceil(float(percentile) * len(ordered)))
    return ordered[rank - 1]


def _distribution_summary(values: Sequence[float]) -> dict[str, Any]:
    clean = [float(value) for value in values]
    if not clean:
        raise ValueError("No hay valores holdout evaluables.")
    ordered = sorted(clean)
    return {
        "count": len(clean),
        "mean": mean(clean),
        "median": median(clean),
        "min": ordered[0],
        "max": ordered[-1],
        "p10_nearest_rank": _nearest_rank(clean, 0.10),
        "p90_nearest_rank": _nearest_rank(clean, 0.90),
    }


def _fingerprint(
    candidate_id: str,
    formula_ref: str,
    values: Sequence[float],
) -> str:
    payload = {
        "candidate_id": candidate_id,
        "formula_ref": formula_ref,
        "values_sorted": sorted(float(value) for value in values),
    }
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def evaluate_px_v3_holdout(
    candidate: Mapping[str, Any],
    cohort: Mapping[str, Any],
    score_bundle: Mapping[str, Any],
    *,
    candidate_policy: Mapping[str, Any] | None = None,
    cohort_policy: Mapping[str, Any] | None = None,
    evaluation_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evalúa una distribución holdout congelada sin decidir promoción."""

    if candidate_policy is None:
        candidate_policy = load_px_v3_candidate_freeze_policy()
    if cohort_policy is None:
        cohort_policy = load_external_recurrence_cohort_policy()
    if evaluation_policy is None:
        evaluation_policy = load_px_v3_holdout_evaluation_policy()

    candidate_eval = evaluate_px_v3_candidate(
        candidate,
        policy=candidate_policy,
    )
    if not candidate_eval["frozen_for_validation"]:
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": evaluation_policy["policy_id"],
            "reason": "El candidato no está FROZEN_FOR_VALIDATION.",
            "candidate_id": candidate_eval["candidate_id"],
            "promotion_decision": "FORBIDDEN",
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    cohort_summary = validate_external_recurrence_cohort(
        cohort,
        policy=cohort_policy,
    )
    if cohort_summary["state"] != "PROTOCOL_READY":
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": evaluation_policy["policy_id"],
            "reason": "La cohorte no supera el firewall S4.",
            "candidate_id": candidate_eval["candidate_id"],
            "cohort_summary": cohort_summary,
            "promotion_decision": "FORBIDDEN",
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    clean_refs = _clean_external_sample_refs(
        cohort,
        cohort_policy=cohort_policy,
    )
    if not clean_refs:
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": evaluation_policy["policy_id"],
            "reason": "No existen muestras holdout externas limpias.",
            "candidate_id": candidate_eval["candidate_id"],
            "cohort_summary": cohort_summary,
            "promotion_decision": "FORBIDDEN",
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    development_refs = set(candidate.get("development_case_refs", []))
    overlap = sorted(development_refs.intersection(clean_refs))
    if overlap:
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": evaluation_policy["policy_id"],
            "reason": "DEVELOPMENT_HOLDOUT_OVERLAP",
            "candidate_id": candidate_eval["candidate_id"],
            "overlap_count": len(overlap),
            "promotion_decision": "FORBIDDEN",
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    formula_ref = score_bundle.get("formula_ref")
    if formula_ref != candidate_eval["formula_ref"]:
        raise ValueError("score_bundle.formula_ref no coincide con el candidato.")

    engine_ref = score_bundle.get("evaluation_engine_ref")
    if not isinstance(engine_ref, str) or not engine_ref:
        raise ValueError("evaluation_engine_ref obligatorio.")

    raw_scores = score_bundle.get("scores")
    if not isinstance(raw_scores, list):
        raise ValueError("score_bundle.scores debe ser una lista.")

    score_by_ref: dict[str, float] = {}
    for index, item in enumerate(raw_scores):
        if not isinstance(item, Mapping):
            raise ValueError(f"scores[{index}] debe ser un objeto.")
        ref = item.get("sample_ref")
        value = item.get("candidate_value")
        if not isinstance(ref, str) or not ref:
            raise ValueError(f"scores[{index}].sample_ref inválido.")
        if ref in score_by_ref:
            raise ValueError(f"sample_ref duplicado en score_bundle: {ref}.")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{ref}: candidate_value debe ser numérico.")
        score_by_ref[ref] = float(value)

    missing = sorted(set(clean_refs) - set(score_by_ref))
    if missing:
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": evaluation_policy["policy_id"],
            "reason": "INCOMPLETE_HOLDOUT_SCORE_COVERAGE",
            "candidate_id": candidate_eval["candidate_id"],
            "missing_score_count": len(missing),
            "promotion_decision": "FORBIDDEN",
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    values = [score_by_ref[ref] for ref in clean_refs]
    summary = _distribution_summary(values)
    fingerprint = _fingerprint(
        candidate_eval["candidate_id"],
        candidate_eval["formula_ref"],
        values,
    )

    return {
        "state": "HOLDOUT_EVALUATED_DIAGNOSTIC_ONLY",
        "policy_id": evaluation_policy["policy_id"],
        "policy_status": evaluation_policy["status"],
        "epistemic_class": evaluation_policy["epistemic_class"],
        "candidate_id": candidate_eval["candidate_id"],
        "formula_ref": candidate_eval["formula_ref"],
        "evaluation_engine_ref": engine_ref,
        "cohort_id": str(cohort["cohort_id"]),
        "null_model": str(cohort["null_model"]),
        "clean_holdout_sample_count": len(clean_refs),
        "distribution": summary,
        "distribution_fingerprint_sha256": fingerprint,
        "cohort_summary": cohort_summary,
        "sample_identifiers_exposed": False,
        "sample_values_exposed": False,
        "promotion_decision": "FORBIDDEN",
        "candidate_validated": False,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
        "population_probability_claim": False,
    }
