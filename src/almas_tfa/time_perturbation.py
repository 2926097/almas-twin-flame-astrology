from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from importlib import resources
import json
from math import ceil
from typing import Any, Mapping, Sequence

from .astrology_handlers import make_m02_natal
from .core import score_model
from .draconic_handlers import m10_individual_draconics, m11_natal_draconic_cross
from .evidence_handlers import (
    m15_evidence_extraction,
    m16_dependency_deduplication,
    m17_independent_roots,
)
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult
from .pillar_attribution import derive_pillars_from_roots, load_root_pillar_policy
from .relational_handlers import m03_synastry
from .relationship_chart_handlers import make_m08_davison, m07_composite
from .relationship_consonance import m09_relationship_chart_consonance
from .symmetry_handlers import m05_declinations, m06_antiscia


POLICY_RESOURCE = "birth-time-perturbation-policy.json"
POLICY_PACKAGE = "almas_tfa"
MODELS = ("AF", "KA", "AG", "LG")


def load_birth_time_perturbation_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_BIRTH_TIME_PERTURBATION_V1":
        raise ValueError("Política de perturbación horaria desconocida.")
    return policy


def _parse_local_datetime(subject: Mapping[str, Any]) -> tuple[datetime, bool]:
    birth_date = subject.get("birth_date")
    birth_time = subject.get("birth_time")
    if not isinstance(birth_date, str) or not birth_date:
        raise ValueError("birth_date es obligatorio para perturbación horaria.")
    if not isinstance(birth_time, str) or not birth_time:
        raise ValueError("birth_time es obligatorio para perturbación horaria.")

    has_seconds = birth_time.count(":") >= 2
    formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")
    value = f"{birth_date} {birth_time}"
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt), has_seconds
        except ValueError:
            continue
    raise ValueError(f"Hora local no interpretable: {value!r}.")


def _shift_subject(subject: Mapping[str, Any], offset_minutes: int) -> dict[str, Any]:
    shifted = dict(subject)
    local_dt, has_seconds = _parse_local_datetime(subject)
    local_dt = local_dt + timedelta(minutes=int(offset_minutes))
    shifted["birth_date"] = local_dt.strftime("%Y-%m-%d")
    shifted["birth_time"] = local_dt.strftime(
        "%H:%M:%S" if has_seconds else "%H:%M"
    )
    return shifted


def _offsets_for_subject(
    subject: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> tuple[list[int], dict[str, Any]]:
    subject_id = str(subject.get("id") or "")
    reliability = subject.get("time_reliability")
    windows = policy.get("reliability_windows")
    if not isinstance(windows, Mapping):
        raise ValueError("reliability_windows debe ser un objeto.")

    if reliability not in windows:
        raise ValueError(
            f"{subject_id}: time_reliability debe ser A/B/C/D para Q4."
        )
    spec = windows[reliability]
    if not isinstance(spec, Mapping):
        raise ValueError(f"{subject_id}: política horaria inválida.")

    window = int(spec["window_minutes"])
    step = int(spec["step_minutes"])
    if window <= 0 or step <= 0 or window % step != 0:
        raise ValueError(
            f"{subject_id}: window/step deben ser positivos y divisibles."
        )

    offsets = list(range(-window, window + 1, step))
    if 0 not in offsets:
        raise ValueError(f"{subject_id}: la parrilla debe incluir 0.")

    return offsets, {
        "subject_id": subject_id,
        "time_reliability": reliability,
        "window_minutes": window,
        "step_minutes": step,
        "offset_count": len(offsets),
    }


def _context(
    module_id: str,
    raw_input: Mapping[str, Any],
    canonical: Mapping[str, Any],
    prior: Mapping[str, ModuleResult],
) -> ModuleContext:
    return ModuleContext(
        module_id=module_id,
        module_name=f"q4_{module_id}",
        mode="FULL",
        raw_input=raw_input,
        canonical_snapshot=canonical,
        prior_results=prior,
    )


def _apply(
    module_id: str,
    handler,
    raw_input: Mapping[str, Any],
    canonical: dict[str, Any],
    prior: dict[str, ModuleResult],
) -> ModuleResult:
    result = handler(_context(module_id, raw_input, canonical, prior))
    prior[module_id] = result
    if result.status is ExecutionStatus.COMPLETED:
        for key, value in result.canonical_updates.items():
            canonical[key] = deepcopy(value)
    return result


def _structural_snapshot(
    raw_input: Mapping[str, Any],
    *,
    astrology_backend,
    davison_backend,
) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    prior: dict[str, ModuleResult] = {}

    sequence = (
        ("M02", make_m02_natal(astrology_backend)),
        ("M03", m03_synastry),
        ("M05", m05_declinations),
        ("M06", m06_antiscia),
        ("M07", m07_composite),
        ("M08", make_m08_davison(davison_backend)),
        ("M09", m09_relationship_chart_consonance),
        ("M10", m10_individual_draconics),
        ("M11", m11_natal_draconic_cross),
        ("M15", m15_evidence_extraction),
        ("M16", m16_dependency_deduplication),
        ("M17", m17_independent_roots),
    )

    required = {
        "M02",
        "M03",
        "M05",
        "M06",
        "M07",
        "M08",
        "M09",
        "M10",
        "M11",
        "M15",
        "M16",
        "M17",
    }

    for module_id, handler in sequence:
        result = _apply(module_id, handler, raw_input, canonical, prior)
        if module_id in required and result.status is not ExecutionStatus.COMPLETED:
            reason = "; ".join(result.limitations) or result.status.value
            return {
                "state": "NOT_EVALUABLE",
                "failed_module": module_id,
                "reason": reason,
            }

    roots_obj = canonical.get("independent_roots")
    if not isinstance(roots_obj, Mapping):
        return {
            "state": "NOT_EVALUABLE",
            "failed_module": "M17",
            "reason": "M17 no produjo independent_roots.",
        }
    roots = roots_obj.get("roots")
    if not isinstance(roots, list) or not roots:
        return {
            "state": "NOT_EVALUABLE",
            "failed_module": "M17",
            "reason": "No existen raíces evaluables.",
        }

    pillar_data = derive_pillars_from_roots(
        roots,
        structural_absence_is_zero=True,
        policy=load_root_pillar_policy(),
    )
    pillars = pillar_data["pillars"]

    indices: dict[str, float] = {}
    for model in MODELS:
        score = score_model(model, pillars, ice=0.0)
        if not score.essential_evaluable:
            return {
                "state": "NOT_EVALUABLE",
                "failed_module": "M19",
                "reason": f"{model}: pilares esenciales no evaluables.",
            }
        indices[model] = float(score.iem_pre)

    core_root_keys = sorted(
        {
            str(root.get("root_key"))
            for root in roots
            if bool(root.get("core_eligible"))
            and root.get("strength_state") == "CALCULATED_CORE"
            and str(root.get("root_key") or "")
        }
    )
    if not core_root_keys:
        return {
            "state": "NOT_EVALUABLE",
            "failed_module": "M17",
            "reason": "No existen raíces core para medir preservación.",
        }

    return {
        "state": "EVALUABLE",
        "iem_pre": indices,
        "core_root_keys": core_root_keys,
        "core_root_count": len(core_root_keys),
        "pillars": pillars,
    }


def _nearest_rank(values: Sequence[float], percentile: float) -> float:
    if not values:
        raise ValueError("nearest-rank requiere al menos un valor.")
    if not 0.0 < percentile <= 1.0:
        raise ValueError("percentile debe estar en (0,1].")
    ordered = sorted(float(value) for value in values)
    rank = max(1, ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def generate_birth_time_sensitivity(
    raw_input: Mapping[str, Any],
    *,
    astrology_backend,
    davison_backend,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Genera parrilla horaria, recalcula estructura y deriva delta90/G."""

    if policy is None:
        policy = load_birth_time_perturbation_policy()

    subjects = raw_input.get("subjects")
    if not isinstance(subjects, list) or len(subjects) != 2:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "Q4 requiere exactamente dos sujetos.",
        }

    subject_specs = []
    offset_vectors = []
    for subject in subjects:
        if not isinstance(subject, Mapping):
            return {
                "state": "NOT_EVALUABLE",
                "reason": "Cada subject debe ser un objeto.",
            }
        try:
            _parse_local_datetime(subject)
            offsets, spec = _offsets_for_subject(subject, policy)
        except ValueError as exc:
            return {
                "state": "NOT_EVALUABLE",
                "reason": str(exc),
            }

        if not isinstance(subject.get("timezone"), str) or not subject.get("timezone"):
            return {
                "state": "NOT_EVALUABLE",
                "reason": f"{subject.get('id')}: timezone ausente.",
            }
        location_ok = (
            isinstance(subject.get("place"), str)
            and bool(subject.get("place"))
        ) or (
            isinstance(subject.get("latitude"), (int, float))
            and not isinstance(subject.get("latitude"), bool)
            and isinstance(subject.get("longitude"), (int, float))
            and not isinstance(subject.get("longitude"), bool)
        )
        if not location_ok:
            return {
                "state": "NOT_EVALUABLE",
                "reason": f"{subject.get('id')}: localización ausente.",
            }

        subject_specs.append(spec)
        offset_vectors.append(offsets)

    combinations = [
        (offset_a, offset_b)
        for offset_a in offset_vectors[0]
        for offset_b in offset_vectors[1]
    ]
    max_samples = int(policy["grid"]["maximum_samples"])
    if len(combinations) - 1 > max_samples:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "La parrilla preregistrada excede maximum_samples.",
        }

    baseline_raw = deepcopy(dict(raw_input))
    baseline = _structural_snapshot(
        baseline_raw,
        astrology_backend=astrology_backend,
        davison_backend=davison_backend,
    )
    if baseline.get("state") != "EVALUABLE":
        return {
            "state": "NOT_EVALUABLE",
            "reason": "Baseline no evaluable: " + str(baseline.get("reason")),
            "failed_module": baseline.get("failed_module"),
        }

    baseline_roots = set(baseline["core_root_keys"])
    samples: list[dict[str, Any]] = []
    deltas: list[float] = []
    preservation_values: list[float] = []

    for offset_a, offset_b in combinations:
        if offset_a == 0 and offset_b == 0:
            continue

        perturbed = deepcopy(dict(raw_input))
        perturbed_subjects = [
            _shift_subject(subjects[0], offset_a),
            _shift_subject(subjects[1], offset_b),
        ]
        perturbed["subjects"] = perturbed_subjects

        snapshot = _structural_snapshot(
            perturbed,
            astrology_backend=astrology_backend,
            davison_backend=davison_backend,
        )
        if snapshot.get("state") != "EVALUABLE":
            return {
                "state": "NOT_EVALUABLE",
                "reason": (
                    f"Perturbación ({offset_a},{offset_b}) no evaluable: "
                    + str(snapshot.get("reason"))
                ),
                "failed_module": snapshot.get("failed_module"),
            }

        delta_by_model = {
            model: abs(
                float(snapshot["iem_pre"][model])
                - float(baseline["iem_pre"][model])
            )
            for model in MODELS
        }
        delta = max(delta_by_model.values())

        sample_roots = set(snapshot["core_root_keys"])
        preserved = len(baseline_roots & sample_roots) / len(baseline_roots)

        deltas.append(delta)
        preservation_values.append(preserved)
        samples.append(
            {
                "offset_minutes": {
                    str(subjects[0]["id"]): offset_a,
                    str(subjects[1]["id"]): offset_b,
                },
                "max_abs_iem_pre_delta": delta,
                "delta_by_model": delta_by_model,
                "core_root_preservation": preserved,
                "core_root_count": int(snapshot["core_root_count"]),
            }
        )

    if not samples:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "La parrilla no produjo perturbaciones no nulas.",
        }

    percentile = float(policy["metric"]["percentile"])
    delta90 = _nearest_rank(deltas, percentile)
    preserved_fraction = sum(preservation_values) / len(preservation_values)

    return {
        "state": "EVALUABLE",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "preregistration_ref": policy["policy_id"],
        "subject_scope": policy["subject_scope"],
        "perturbation_rule": {
            "grid_mode": policy["grid"]["mode"],
            "subjects": subject_specs,
        },
        "metric": policy["metric"]["delta"],
        "preservation_metric": policy["metric"]["preserved_fraction"],
        "percentile": percentile,
        "percentile_method": policy["metric"]["percentile_method"],
        "delta90": delta90,
        "preserved_fraction": preserved_fraction,
        "perturbation_count": len(samples),
        "baseline": {
            "iem_pre": baseline["iem_pre"],
            "core_root_count": baseline["core_root_count"],
        },
        "samples": samples,
        "root_preservation_min": min(preservation_values),
        "root_preservation_mean": preserved_fraction,
        "root_preservation_max": max(preservation_values),
        "iem_delta_max": max(deltas),
        "idd_recomputed": False,
        "ice_used": False,
        "iem_final_used": False,
        "temporal_activation_used": False,
        "null_rarity_used": False,
    }
