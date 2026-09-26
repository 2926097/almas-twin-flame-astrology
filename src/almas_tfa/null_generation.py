from __future__ import annotations

import calendar
from copy import deepcopy
from datetime import date, timedelta
from importlib import resources
import json
from typing import Any, Mapping

from .time_perturbation import structural_recalculation_snapshot


POLICY_RESOURCE = "null-within-year-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_null_generation_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_NULL_WITHIN_YEAR_V1":
        raise ValueError("Política Q6 de generación nula desconocida.")
    return policy


def _parse_birth_date(subject: Mapping[str, Any]) -> date:
    value = subject.get("birth_date")
    if not isinstance(value, str) or not value:
        raise ValueError("birth_date es obligatorio para Q6.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"birth_date inválida: {value!r}.") from exc


def _stratified_dates(
    subject: Mapping[str, Any],
    *,
    sample_count: int,
) -> list[date]:
    original = _parse_birth_date(subject)
    if sample_count <= 0:
        raise ValueError("samples_per_subject debe ser positivo.")

    days = 366 if calendar.isleap(original.year) else 365
    start = date(original.year, 1, 1)
    original_index = (original - start).days

    indices: list[int] = []
    for index in range(sample_count):
        # Centro de cada estrato: determinista, reproducible y sin RNG.
        day_index = int(((index + 0.5) * days) // sample_count)
        day_index = min(days - 1, max(0, day_index))
        if day_index == original_index:
            day_index = (day_index + 1) % days
        if day_index in indices:
            probe = day_index
            for _ in range(days):
                probe = (probe + 1) % days
                if probe != original_index and probe not in indices:
                    day_index = probe
                    break
        indices.append(day_index)

    if len(set(indices)) != sample_count:
        raise ValueError("La estratificación Q6 produjo fechas duplicadas.")

    return [start + timedelta(days=day_index) for day_index in indices]


def _statistic(snapshot: Mapping[str, Any], statistic_id: str) -> float:
    if statistic_id == "CORE_ROOT_COUNT":
        return float(snapshot["core_root_count"])
    if statistic_id == "MAX_IEM_PRE":
        values = snapshot.get("iem_pre")
        if not isinstance(values, Mapping) or not values:
            raise ValueError("Snapshot sin IEM_pre para MAX_IEM_PRE.")
        return max(float(value) for value in values.values())
    if statistic_id == "PX_PILLAR_SCORE":
        pillars = snapshot.get("pillars")
        if not isinstance(pillars, Mapping):
            raise ValueError("Snapshot sin pilares para PX_PILLAR_SCORE.")
        value = pillars.get("PX")
        if value is None:
            raise ValueError("PX no evaluable en snapshot Q6.")
        return 100.0 * float(value)
    raise ValueError(f"Estadístico Q6 desconocido: {statistic_id}.")


def generate_within_year_null_runs(
    raw_input: Mapping[str, Any],
    *,
    astrology_backend,
    davison_backend,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Genera muestras WITHIN_YEAR y specs compatibles con M24.

    Cada sujeto se perturba por separado manteniendo fijo al otro. Se conserva
    año, hora local, zona horaria y localización. No pretende representar una
    población externa ni reemplaza PAIR_SHUFFLE/MATCHED_AGE.
    """

    if policy is None:
        policy = load_null_generation_policy()

    subjects = raw_input.get("subjects")
    if not isinstance(subjects, list) or len(subjects) != 2:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "Q6 requiere exactamente dos sujetos.",
        }
    if not all(isinstance(subject, Mapping) for subject in subjects):
        return {
            "state": "NOT_EVALUABLE",
            "reason": "Cada subject debe ser un objeto.",
        }

    spec = policy.get("generator")
    if not isinstance(spec, Mapping):
        raise ValueError("generator debe ser un objeto.")
    sample_count = int(spec["samples_per_subject"])

    baseline = structural_recalculation_snapshot(
        raw_input,
        astrology_backend=astrology_backend,
        davison_backend=davison_backend,
    )
    if baseline.get("state") != "EVALUABLE":
        return {
            "state": "NOT_EVALUABLE",
            "reason": "Baseline Q6 no evaluable: " + str(baseline.get("reason")),
            "failed_module": baseline.get("failed_module"),
        }

    generated_samples: list[dict[str, Any]] = []
    for subject_index, subject in enumerate(subjects):
        subject_id = str(subject.get("id") or f"subject_{subject_index + 1}")
        try:
            dates = _stratified_dates(
                subject,
                sample_count=sample_count,
            )
        except ValueError as exc:
            return {
                "state": "NOT_EVALUABLE",
                "reason": str(exc),
            }

        for replacement_date in dates:
            perturbed = deepcopy(dict(raw_input))
            perturbed_subjects = [
                deepcopy(dict(item)) for item in subjects
            ]
            perturbed_subjects[subject_index]["birth_date"] = (
                replacement_date.isoformat()
            )
            perturbed["subjects"] = perturbed_subjects

            snapshot = structural_recalculation_snapshot(
                perturbed,
                astrology_backend=astrology_backend,
                davison_backend=davison_backend,
            )
            if snapshot.get("state") != "EVALUABLE":
                return {
                    "state": "NOT_EVALUABLE",
                    "reason": (
                        f"Q6 {subject_id}/{replacement_date.isoformat()} "
                        "no evaluable: " + str(snapshot.get("reason"))
                    ),
                    "failed_module": snapshot.get("failed_module"),
                }

            generated_samples.append(
                {
                    "perturbed_subject_id": subject_id,
                    "replacement_birth_date": replacement_date.isoformat(),
                    "snapshot": snapshot,
                }
            )

    if not generated_samples:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "Q6 no produjo muestras nulas.",
        }

    frozen = policy["frozen_refs"]
    statistics = policy.get("statistics")
    if not isinstance(statistics, list) or not statistics:
        raise ValueError("statistics debe contener al menos un estadístico.")

    run_specs = []
    sample_manifest = []
    for sample in generated_samples:
        snap = sample["snapshot"]
        sample_manifest.append(
            {
                "perturbed_subject_id": sample["perturbed_subject_id"],
                "replacement_birth_date": sample["replacement_birth_date"],
                "core_root_count": int(snap["core_root_count"]),
                "max_iem_pre": _statistic(snap, "MAX_IEM_PRE"),
                "px_pillar_score": _statistic(snap, "PX_PILLAR_SCORE"),
            }
        )

    for statistic in statistics:
        if not isinstance(statistic, Mapping):
            raise ValueError("Cada estadístico Q6 debe ser un objeto.")
        statistic_id = str(statistic.get("id") or "")
        tail = str(statistic.get("tail") or "")
        if not statistic_id or not tail:
            raise ValueError("Cada estadístico Q6 requiere id y tail.")

        observed = _statistic(baseline, statistic_id)
        null_samples = [
            _statistic(sample["snapshot"], statistic_id)
            for sample in generated_samples
        ]

        run_specs.append(
            {
                "id": "AUTO_WITHIN_YEAR_" + statistic_id,
                "preregistration_ref": policy["policy_id"],
                "null_model": policy["null_model"],
                "feature_set_ref": frozen["feature_set_ref"],
                "orb_policy_ref": frozen["orb_policy_ref"],
                "event_set_ref": frozen["event_set_ref"],
                "generator_ref": frozen["generator_ref"],
                "statistic_id": statistic_id,
                "observed_value": observed,
                "tail": tail,
                "confidence_level": float(policy["confidence_level"]),
                "null_samples": null_samples,
            }
        )

    return {
        "state": "EVALUABLE",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "null_model": policy["null_model"],
        "run_specs": run_specs,
        "sample_count": len(generated_samples),
        "samples_per_subject": sample_count,
        "sample_manifest": sample_manifest,
        "generator": dict(spec),
        "metaphysical_probability": False,
        "external_population_claim": False,
        "combined_p_value": None,
        "combined_p_value_state": "FORBIDDEN",
    }
