from __future__ import annotations

from importlib import resources
import json
from math import sqrt
from statistics import NormalDist
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "recurrence-null-calibration-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_recurrence_null_calibration_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_RECURRENCE_NULL_CALIBRATION_V1":
        raise ValueError("Política de calibración nula de recurrencia desconocida.")
    return policy


def _wilson(successes: int, trials: int, confidence: float) -> dict[str, float]:
    if trials <= 0:
        raise ValueError("trials debe ser positivo.")
    if successes < 0 or successes > trials:
        raise ValueError("successes fuera de rango.")
    alpha = 1.0 - float(confidence)
    z = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    phat = successes / trials
    z2 = z * z
    den = 1.0 + z2 / trials
    center = (phat + z2 / (2.0 * trials)) / den
    half = (
        z
        * sqrt(
            phat * (1.0 - phat) / trials
            + z2 / (4.0 * trials * trials)
        )
        / den
    )
    return {
        "confidence_level": float(confidence),
        "lower": max(0.0, center - half),
        "upper": min(1.0, center + half),
    }


def _frequency(successes: int, trials: int, confidence: float) -> dict[str, Any]:
    return {
        "n": int(trials),
        "count": int(successes),
        "frequency": successes / trials,
        "wilson_interval": _wilson(successes, trials, confidence),
    }


def _snapshot_payload(snapshot: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    pillar = snapshot.get("pillar_attribution")
    if not isinstance(pillar, Mapping):
        raise ValueError("Snapshot sin pillar_attribution.")

    graph = pillar.get("semantic_motifs")
    quality = pillar.get("recurrence_quality")
    if not isinstance(graph, Mapping):
        raise ValueError("Snapshot sin semantic_motifs.")
    if not isinstance(quality, Mapping):
        raise ValueError("Snapshot sin recurrence_quality.")
    return graph, quality


def _motif_maps(
    snapshot: Mapping[str, Any],
    motif_type: str,
) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    graph, quality = _snapshot_payload(snapshot)
    if motif_type == "PRIMARY":
        graph_items = graph.get("recurrent_primary_motifs", [])
        quality_items = quality.get("primary_motifs", [])
    elif motif_type == "MISSION":
        graph_items = graph.get("recurrent_mission_motifs", [])
        quality_items = quality.get("mission_motifs", [])
    else:
        raise ValueError(f"motif_type desconocido: {motif_type}")

    graph_map = {
        str(item.get("motif_id")): item
        for item in graph_items
        if isinstance(item, Mapping) and str(item.get("motif_id") or "")
    }
    quality_map = {
        str(item.get("motif_id")): item
        for item in quality_items
        if isinstance(item, Mapping) and str(item.get("motif_id") or "")
    }
    return graph_map, quality_map


def _is_extreme(value: float, observed: float, tail: str) -> bool:
    if tail == "GREATER_OR_EQUAL":
        return float(value) >= float(observed)
    if tail == "LESS_OR_EQUAL":
        return float(value) <= float(observed)
    raise ValueError(f"tail no soportado: {tail}")


def _numeric_metric(
    *,
    metric_id: str,
    observed: float,
    null_values: Sequence[float | None],
    tail: str,
    confidence: float,
) -> dict[str, Any]:
    total = len(null_values)
    present_values = [float(v) for v in null_values if v is not None]
    extreme = sum(
        1 for value in present_values
        if _is_extreme(value, observed, tail)
    )
    unconditional = _frequency(extreme, total, confidence)
    conditional = (
        _frequency(extreme, len(present_values), confidence)
        if present_values
        else None
    )
    return {
        "metric_id": metric_id,
        "observed": float(observed),
        "tail": tail,
        "null_present_count": len(present_values),
        "unconditional": unconditional,
        "conditional_on_motif_present": conditional,
    }


def _boolean_metric(
    *,
    metric_id: str,
    observed: bool,
    null_values: Sequence[bool | None],
    confidence: float,
) -> dict[str, Any]:
    total = len(null_values)
    present_values = [bool(v) for v in null_values if v is not None]
    true_count = sum(1 for value in present_values if value)
    return {
        "metric_id": metric_id,
        "observed": bool(observed),
        "tail": "BOOLEAN_TRUE",
        "null_present_count": len(present_values),
        "unconditional_true": _frequency(true_count, total, confidence),
        "conditional_on_motif_present": (
            _frequency(true_count, len(present_values), confidence)
            if present_values
            else None
        ),
    }


QUALITY_NUMERIC_FIELDS = {
    "FAMILY_CLASS_COUNT": ("family_class_count", "GREATER_OR_EQUAL"),
    "FAMILY_STRENGTH_ENTROPY": (
        "family_strength_entropy",
        "GREATER_OR_EQUAL",
    ),
    "EFFECTIVE_FAMILY_COUNT": (
        "effective_family_count",
        "GREATER_OR_EQUAL",
    ),
    "FAMILY_DOMINANCE_SHARE": (
        "family_dominance_share",
        "LESS_OR_EQUAL",
    ),
    "LEAVE_ONE_FAMILY_OUT_SURVIVAL": (
        "leave_one_family_out_survival_fraction",
        "GREATER_OR_EQUAL",
    ),
    "LEAVE_ONE_CLASS_OUT_SURVIVAL": (
        "leave_one_class_out_survival_fraction",
        "GREATER_OR_EQUAL",
    ),
}

QUALITY_BOOLEAN_FIELDS = {
    "CROSS_CLASS_RECURRENCE": "cross_class_recurrence",
    "NON_DRACONIC_RECURRENCE": "non_draconic_recurrence",
}


def _calibrate_motif(
    motif_id: str,
    motif_type: str,
    observed_graph: Mapping[str, Any],
    observed_quality: Mapping[str, Any],
    null_snapshots: Sequence[Mapping[str, Any]],
    *,
    confidence: float,
) -> dict[str, Any]:
    null_graph_records: list[Mapping[str, Any] | None] = []
    null_quality_records: list[Mapping[str, Any] | None] = []

    for snapshot in null_snapshots:
        graph_map, quality_map = _motif_maps(snapshot, motif_type)
        null_graph_records.append(graph_map.get(motif_id))
        null_quality_records.append(quality_map.get(motif_id))

    total = len(null_snapshots)
    presence_count = sum(item is not None for item in null_graph_records)

    metrics: dict[str, Any] = {
        "RECURRENCE_PRESENCE": {
            "metric_id": "RECURRENCE_PRESENCE",
            "observed": True,
            "tail": "BOOLEAN_TRUE",
            "unconditional_true": _frequency(
                presence_count,
                total,
                confidence,
            ),
        }
    }

    metrics["MOTIF_STRENGTH"] = _numeric_metric(
        metric_id="MOTIF_STRENGTH",
        observed=float(observed_graph["motif_strength"]),
        null_values=[
            (
                float(item["motif_strength"])
                if isinstance(item, Mapping)
                else None
            )
            for item in null_graph_records
        ],
        tail="GREATER_OR_EQUAL",
        confidence=confidence,
    )

    for metric_id, (field, tail) in QUALITY_NUMERIC_FIELDS.items():
        observed_value = observed_quality.get(field)
        if isinstance(observed_value, bool) or not isinstance(
            observed_value, (int, float)
        ):
            continue
        metrics[metric_id] = _numeric_metric(
            metric_id=metric_id,
            observed=float(observed_value),
            null_values=[
                (
                    float(item[field])
                    if isinstance(item, Mapping)
                    and isinstance(item.get(field), (int, float))
                    and not isinstance(item.get(field), bool)
                    else None
                )
                for item in null_quality_records
            ],
            tail=tail,
            confidence=confidence,
        )

    for metric_id, field in QUALITY_BOOLEAN_FIELDS.items():
        observed_value = observed_quality.get(field)
        if not isinstance(observed_value, bool):
            continue
        metrics[metric_id] = _boolean_metric(
            metric_id=metric_id,
            observed=observed_value,
            null_values=[
                (
                    bool(item[field])
                    if isinstance(item, Mapping)
                    and isinstance(item.get(field), bool)
                    else None
                )
                for item in null_quality_records
            ],
            confidence=confidence,
        )

    return {
        "motif_id": motif_id,
        "motif_type": motif_type,
        "observed_strength": float(observed_graph["motif_strength"]),
        "null_recurrence_count": presence_count,
        "null_recurrence_frequency": presence_count / total,
        "metrics": metrics,
        "used_for_weighting": False,
        "metaphysical_probability": False,
    }


def _null_catalog(
    null_snapshots: Sequence[Mapping[str, Any]],
    motif_type: str,
    *,
    confidence: float,
) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    draconic_counts: dict[str, int] = {}
    non_draconic_counts: dict[str, int] = {}

    for snapshot in null_snapshots:
        graph_map, quality_map = _motif_maps(snapshot, motif_type)
        for motif_id in graph_map:
            counts[motif_id] = counts.get(motif_id, 0) + 1
            quality = quality_map.get(motif_id)
            if isinstance(quality, Mapping):
                if bool(quality.get("includes_natal_draconic")):
                    draconic_counts[motif_id] = (
                        draconic_counts.get(motif_id, 0) + 1
                    )
                if bool(quality.get("non_draconic_recurrence")):
                    non_draconic_counts[motif_id] = (
                        non_draconic_counts.get(motif_id, 0) + 1
                    )

    total = len(null_snapshots)
    return [
        {
            "motif_id": motif_id,
            "motif_type": motif_type,
            "recurrence": _frequency(count, total, confidence),
            "includes_natal_draconic": _frequency(
                draconic_counts.get(motif_id, 0),
                total,
                confidence,
            ),
            "non_draconic_recurrence": _frequency(
                non_draconic_counts.get(motif_id, 0),
                total,
                confidence,
            ),
        }
        for motif_id, count in sorted(counts.items())
    ]


def _aggregate_calibration(
    baseline: Mapping[str, Any],
    null_snapshots: Sequence[Mapping[str, Any]],
    *,
    confidence: float,
) -> dict[str, Any]:
    baseline_graph, _ = _snapshot_payload(baseline)
    observed = {
        "PRIMARY_RECURRENT_MOTIF_COUNT": int(
            baseline_graph.get("px", {}).get("recurrent_motif_count", 0)
        ),
        "MISSION_RECURRENT_MOTIF_COUNT": int(
            baseline_graph.get("ps", {}).get("recurrent_motif_count", 0)
        ),
        "PX_SCORE": float(baseline_graph.get("px", {}).get("score", 0.0)),
        "PS_SCORE": float(baseline_graph.get("ps", {}).get("score", 0.0)),
    }

    null_values: dict[str, list[float]] = {
        key: [] for key in observed
    }
    for snapshot in null_snapshots:
        graph, _ = _snapshot_payload(snapshot)
        null_values["PRIMARY_RECURRENT_MOTIF_COUNT"].append(
            float(graph.get("px", {}).get("recurrent_motif_count", 0))
        )
        null_values["MISSION_RECURRENT_MOTIF_COUNT"].append(
            float(graph.get("ps", {}).get("recurrent_motif_count", 0))
        )
        null_values["PX_SCORE"].append(
            float(graph.get("px", {}).get("score", 0.0))
        )
        null_values["PS_SCORE"].append(
            float(graph.get("ps", {}).get("score", 0.0))
        )

    output = {}
    for metric_id, observed_value in observed.items():
        values = null_values[metric_id]
        extreme = sum(value >= observed_value for value in values)
        output[metric_id] = {
            "observed": observed_value,
            "tail": "GREATER_OR_EQUAL",
            "structural_frequency": _frequency(
                extreme,
                len(values),
                confidence,
            ),
        }
    return output


def derive_recurrence_calibration_payload(
    baseline_snapshot: Mapping[str, Any],
    control_snapshots: Sequence[Mapping[str, Any]],
    *,
    minimum_samples: int,
    confidence_level: float,
) -> dict[str, Any]:
    """Núcleo común de calibración; no asigna procedencia ni autoridad."""

    minimum = int(minimum_samples)
    if minimum <= 0:
        raise ValueError("minimum_samples debe ser positivo.")
    if len(control_snapshots) < minimum:
        return {
            "state": "NOT_EVALUABLE",
            "reason": (
                f"Se requieren al menos {minimum} muestras de control; "
                f"recibidas={len(control_snapshots)}."
            ),
        }

    confidence = float(confidence_level)
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence_level debe estar en (0,1).")

    try:
        baseline_graph, baseline_quality = _snapshot_payload(
            baseline_snapshot
        )
        for snapshot in control_snapshots:
            _snapshot_payload(snapshot)
    except ValueError as exc:
        return {
            "state": "NOT_EVALUABLE",
            "reason": str(exc),
        }

    results = []
    for motif_type, graph_key, quality_key in (
        ("PRIMARY", "recurrent_primary_motifs", "primary_motifs"),
        ("MISSION", "recurrent_mission_motifs", "mission_motifs"),
    ):
        observed_graph = {
            str(item.get("motif_id")): item
            for item in baseline_graph.get(graph_key, [])
            if isinstance(item, Mapping) and str(item.get("motif_id") or "")
        }
        observed_quality = {
            str(item.get("motif_id")): item
            for item in baseline_quality.get(quality_key, [])
            if isinstance(item, Mapping) and str(item.get("motif_id") or "")
        }

        for motif_id in sorted(observed_graph):
            quality = observed_quality.get(motif_id)
            if not isinstance(quality, Mapping):
                continue
            results.append(
                _calibrate_motif(
                    motif_id,
                    motif_type,
                    observed_graph[motif_id],
                    quality,
                    control_snapshots,
                    confidence=confidence,
                )
            )

    return {
        "state": "DIAGNOSTIC_ONLY",
        "sample_count": len(control_snapshots),
        "confidence_level": confidence,
        "observed_motifs": results,
        "null_catalog": {
            "primary": _null_catalog(
                control_snapshots,
                "PRIMARY",
                confidence=confidence,
            ),
            "mission": _null_catalog(
                control_snapshots,
                "MISSION",
                confidence=confidence,
            ),
        },
        "aggregate": _aggregate_calibration(
            baseline_snapshot,
            control_snapshots,
            confidence=confidence,
        ),
    }


def derive_recurrence_null_calibration(
    baseline_snapshot: Mapping[str, Any],
    null_snapshots: Sequence[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Calibra motivos contra WITHIN_YEAR sin introducir pesos."""

    if policy is None:
        policy = load_recurrence_null_calibration_policy()

    core = derive_recurrence_calibration_payload(
        baseline_snapshot,
        null_snapshots,
        minimum_samples=int(policy["null_source"]["minimum_samples"]),
        confidence_level=float(policy["null_source"]["confidence_level"]),
    )

    if core.get("state") != "DIAGNOSTIC_ONLY":
        return {
            **core,
            "policy_id": policy["policy_id"],
            "policy_status": policy["status"],
            "epistemic_class": policy["epistemic_class"],
            "used_for_weighting": False,
            "used_in_px_score": False,
            "used_in_ps_score": False,
            "used_in_iem": False,
            "used_in_idd": False,
            "used_in_irc": False,
            "used_in_ontology": False,
            "metaphysical_probability": False,
            "external_population_claim": False,
        }

    return {
        **core,
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "null_model": policy["null_source"]["required_null_model"],
        "null_generator_policy_id": policy["null_source"][
            "generator_policy_id"
        ],
        "used_for_weighting": False,
        "used_in_px_score": False,
        "used_in_ps_score": False,
        "used_in_iem": False,
        "used_in_idd": False,
        "used_in_irc": False,
        "used_in_ontology": False,
        "metaphysical_probability": False,
        "external_population_claim": False,
        "combined_p_value": None,
        "combined_p_value_state": "FORBIDDEN",
        "multiple_testing_correction_state": "NOT_CLAIMED",
        "external_nulls_required_before_weighting": True,
    }
