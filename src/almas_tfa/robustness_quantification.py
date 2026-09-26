from __future__ import annotations

from copy import deepcopy
from math import ceil
from importlib import resources
import json
from itertools import combinations
from typing import Any, Mapping, Sequence

from .core import (
    diagnostic_discrimination,
    idd_band,
    pillar_score,
    robustness_component,
    score_model,
)
from .model_attribution import derive_model_attributions
from .time_perturbation import structural_recalculation_snapshot


POLICY_RESOURCE = "robustness-q5-policy.json"
POLICY_PACKAGE = "almas_tfa"
MODELS = ("AF", "KA", "AG", "LG")
PILLARS = ("PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU")


def load_q5_robustness_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_ROBUSTNESS_Q5_V1":
        raise ValueError("Política Q5 de robustez desconocida.")
    return policy


def _nearest_rank(values: Sequence[float], percentile: float) -> float:
    if not values:
        raise ValueError("nearest-rank requiere valores.")
    ordered = sorted(float(value) for value in values)
    rank = max(1, ceil(float(percentile) * len(ordered)))
    return ordered[rank - 1]


def _core_root_ids(canonical: Mapping[str, Any]) -> set[str]:
    roots_obj = canonical.get("independent_roots")
    if not isinstance(roots_obj, Mapping):
        return set()
    roots = roots_obj.get("roots")
    if not isinstance(roots, list):
        return set()
    return {
        str(root.get("root_id"))
        for root in roots
        if isinstance(root, Mapping)
        and bool(root.get("core_eligible"))
        and root.get("strength_state") == "CALCULATED_CORE"
        and str(root.get("root_id") or "")
    }


def _baseline_iem(canonical: Mapping[str, Any]) -> dict[str, float] | None:
    indices = canonical.get("structural_model_indices")
    if not isinstance(indices, Mapping):
        return None
    output: dict[str, float] = {}
    for model in MODELS:
        data = indices.get(model)
        if not isinstance(data, Mapping) or data.get("iem_pre") is None:
            return None
        output[model] = float(data["iem_pre"])
    return output


def _pillars_from_root_attributions(
    root_attributions: Sequence[Mapping[str, Any]],
    surviving_root_ids: set[str],
) -> dict[str, float | None]:
    strengths: dict[str, list[float]] = {
        pillar: [] for pillar in PILLARS if pillar != "PU"
    }
    for item in root_attributions:
        if not isinstance(item, Mapping) or not item.get("eligible"):
            continue
        root_id = str(item.get("root_id") or "")
        if root_id not in surviving_root_ids:
            continue
        contributions = item.get("contributions")
        if not isinstance(contributions, Mapping):
            continue
        for pillar, value in contributions.items():
            pillar = str(pillar)
            if pillar == "PU" or pillar not in strengths:
                continue
            strengths[pillar].append(float(value))

    pillars: dict[str, float | None] = {}
    for pillar in PILLARS:
        if pillar == "PU":
            pillars[pillar] = None
        else:
            values = strengths[pillar]
            pillars[pillar] = pillar_score(values) if values else 0.0
    return pillars


def _iem_from_pillars(pillars: Mapping[str, float | None]) -> dict[str, float]:
    output = {}
    for model in MODELS:
        score = score_model(model, pillars, ice=0.0)
        if not score.essential_evaluable:
            raise ValueError(f"{model}: IEM_pre no evaluable.")
        output[model] = float(score.iem_pre)
    return output


def derive_ablation_component(
    canonical: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    ablation = canonical.get("ablation")
    pillar_attribution = canonical.get("pillar_attribution")
    baseline_iem = _baseline_iem(canonical)
    baseline_core = _core_root_ids(canonical)

    if (
        not isinstance(ablation, Mapping)
        or not isinstance(pillar_attribution, Mapping)
        or baseline_iem is None
        or not baseline_core
    ):
        return {
            "state": "NOT_EVALUABLE",
            "reason": "Faltan M17/M18/M19/M22 canónicos para ABLATION.",
        }

    root_attributions = pillar_attribution.get("root_attributions")
    if not isinstance(root_attributions, list):
        return {
            "state": "NOT_EVALUABLE",
            "reason": "M18 no contiene root_attributions.",
        }

    runs = ablation.get("runs")
    if not isinstance(runs, list):
        return {
            "state": "NOT_EVALUABLE",
            "reason": "M22 no contiene runs.",
        }
    by_run = {
        str(run.get("run")): run
        for run in runs
        if isinstance(run, Mapping)
    }

    selected = list(policy["ablation"]["selected_runs"])
    samples = []
    deltas = []
    preservation = []

    for run_id in selected:
        run = by_run.get(run_id)
        if not isinstance(run, Mapping):
            return {
                "state": "NOT_EVALUABLE",
                "reason": f"Falta corrida preregistrada {run_id}.",
            }
        surviving = {
            str(root_id)
            for root_id in run.get("surviving_root_ids", [])
        }
        pillars = _pillars_from_root_attributions(
            root_attributions,
            surviving,
        )
        iem = _iem_from_pillars(pillars)
        delta_by_model = {
            model: abs(iem[model] - baseline_iem[model])
            for model in MODELS
        }
        delta = max(delta_by_model.values())
        g = len(baseline_core & surviving) / len(baseline_core)

        deltas.append(delta)
        preservation.append(g)
        samples.append(
            {
                "run": run_id,
                "max_abs_iem_pre_delta": delta,
                "delta_by_model": delta_by_model,
                "core_root_preservation": g,
                "surviving_core_root_count": len(baseline_core & surviving),
            }
        )

    percentile = float(policy["percentile"])
    delta90 = _nearest_rank(deltas, percentile)
    g = sum(preservation) / len(preservation)
    value = robustness_component(delta90, g)

    return {
        "state": "EVALUABLE",
        "component": {
            "id": "ABLATION_AUTO",
            "kind": "ABLATION",
            "value": value,
            "source_module": "M22",
            "preregistration_ref": policy["policy_id"],
            "derivation_ref": "ALMAS_ROBUSTNESS_Q5_V1:ABLATION",
            "note": None,
            "auto_derived": True,
        },
        "details": {
            "delta90": delta90,
            "preserved_fraction": g,
            "samples": samples,
            "percentile": percentile,
            "percentile_method": policy["percentile_method"],
        },
    }


def _scale_aspect_policy(value: Any, factor: float) -> Any:
    if not isinstance(value, Mapping):
        return value
    result = deepcopy(dict(value))
    for spec in result.values():
        if isinstance(spec, dict) and isinstance(spec.get("orb"), (int, float)):
            spec["orb"] = float(spec["orb"]) * factor
    return result


def _scaled_raw_input(
    raw_input: Mapping[str, Any],
    factor: float,
) -> dict[str, Any]:
    raw = deepcopy(dict(raw_input))

    if "aspect_policy" in raw:
        raw["aspect_policy"] = _scale_aspect_policy(
            raw["aspect_policy"],
            factor,
        )
    if "draconic_aspect_policy" in raw:
        raw["draconic_aspect_policy"] = _scale_aspect_policy(
            raw["draconic_aspect_policy"],
            factor,
        )

    declination = raw.get("declination_policy")
    if isinstance(declination, Mapping):
        updated = dict(declination)
        for key in ("parallel_orb", "contra_parallel_orb"):
            if isinstance(updated.get(key), (int, float)):
                updated[key] = float(updated[key]) * factor
        raw["declination_policy"] = updated

    antiscia = raw.get("antiscia_policy")
    if isinstance(antiscia, Mapping):
        updated = dict(antiscia)
        for key in ("antiscia_orb", "contra_antiscia_orb"):
            if isinstance(updated.get(key), (int, float)):
                updated[key] = float(updated[key]) * factor
        raw["antiscia_policy"] = updated

    rel = raw.get("relationship_chart_consonance_policy")
    if isinstance(rel, Mapping):
        updated = deepcopy(dict(rel))
        if "aspect_policy" in updated:
            updated["aspect_policy"] = _scale_aspect_policy(
                updated["aspect_policy"],
                factor,
            )
        raw["relationship_chart_consonance_policy"] = updated

    secondary = raw.get("secondary_symbolic_policy")
    if isinstance(secondary, Mapping):
        updated = deepcopy(dict(secondary))
        if "aspect_policy" in updated:
            updated["aspect_policy"] = _scale_aspect_policy(
                updated["aspect_policy"],
                factor,
            )
        raw["secondary_symbolic_policy"] = updated

    return raw


def _pairwise_idd(
    pillar_attribution: Mapping[str, Any],
) -> dict[str, dict[str, Any]] | None:
    attribution = derive_model_attributions(pillar_attribution)
    if attribution.get("state") != "EVALUABLE":
        return None
    maps = attribution.get("attributions")
    if not isinstance(maps, Mapping):
        return None

    output: dict[str, dict[str, Any]] = {}
    for a, b in combinations(MODELS, 2):
        av = maps.get(a)
        bv = maps.get(b)
        if not isinstance(av, Mapping) or not isinstance(bv, Mapping):
            continue
        value = diagnostic_discrimination(av, bv)
        if value is None:
            continue
        output[f"{a}_vs_{b}"] = {
            "idd": float(value),
            "band": idd_band(value),
        }
    return output or None


def derive_parameter_and_idd_components(
    raw_input: Mapping[str, Any],
    *,
    astrology_backend,
    davison_backend,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    baseline = structural_recalculation_snapshot(
        raw_input,
        astrology_backend=astrology_backend,
        davison_backend=davison_backend,
    )
    if baseline.get("state") != "EVALUABLE":
        return {
            "parameter_state": "NOT_EVALUABLE",
            "idd_state": "NOT_EVALUABLE",
            "reason": "Baseline paramétrica no evaluable: "
            + str(baseline.get("reason")),
        }

    baseline_roots = set(baseline["core_root_keys"])
    if not baseline_roots:
        return {
            "parameter_state": "NOT_EVALUABLE",
            "idd_state": "NOT_EVALUABLE",
            "reason": "Baseline sin raíces core.",
        }

    baseline_idd = _pairwise_idd(baseline["pillar_attribution"])

    factors = [
        float(value)
        for value in policy["parameter_perturbation"]["orb_scale_factors"]
    ]
    samples = []
    param_deltas = []
    root_preservation = []
    idd_deltas = []
    idd_preserved_count = 0
    idd_sample_count = 0

    for factor in factors:
        perturbed_raw = _scaled_raw_input(raw_input, factor)
        snapshot = structural_recalculation_snapshot(
            perturbed_raw,
            astrology_backend=astrology_backend,
            davison_backend=davison_backend,
        )
        if snapshot.get("state") != "EVALUABLE":
            return {
                "parameter_state": "NOT_EVALUABLE",
                "idd_state": "NOT_EVALUABLE",
                "reason": f"Factor {factor} no evaluable: "
                + str(snapshot.get("reason")),
            }

        delta_by_model = {
            model: abs(
                float(snapshot["iem_pre"][model])
                - float(baseline["iem_pre"][model])
            )
            for model in MODELS
        }
        param_delta = max(delta_by_model.values())
        sample_roots = set(snapshot["core_root_keys"])
        root_g = len(baseline_roots & sample_roots) / len(baseline_roots)

        sample = {
            "orb_scale_factor": factor,
            "max_abs_iem_pre_delta": param_delta,
            "delta_by_model": delta_by_model,
            "core_root_preservation": root_g,
        }

        param_deltas.append(param_delta)
        root_preservation.append(root_g)

        if baseline_idd:
            current_idd = _pairwise_idd(snapshot["pillar_attribution"])
            if current_idd is not None:
                baseline_pairs = set(baseline_idd)
                if baseline_pairs.issubset(current_idd):
                    pair_deltas = {
                        key: abs(
                            current_idd[key]["idd"]
                            - baseline_idd[key]["idd"]
                        )
                        for key in baseline_pairs
                    }
                    idd_delta = max(pair_deltas.values())
                    bands_preserved = all(
                        current_idd[key]["band"]
                        == baseline_idd[key]["band"]
                        for key in baseline_pairs
                    )
                    idd_deltas.append(idd_delta)
                    idd_sample_count += 1
                    if bands_preserved:
                        idd_preserved_count += 1
                    sample["idd_max_abs_delta"] = idd_delta
                    sample["idd_bands_preserved"] = bands_preserved
                else:
                    sample["idd_state"] = "PAIR_LOSS"
            else:
                sample["idd_state"] = "NOT_EVALUABLE"

        samples.append(sample)

    percentile = float(policy["percentile"])
    param_delta90 = _nearest_rank(param_deltas, percentile)
    param_g = sum(root_preservation) / len(root_preservation)
    param_value = robustness_component(param_delta90, param_g)

    output: dict[str, Any] = {
        "parameter_state": "EVALUABLE",
        "parameter_component": {
            "id": "PARAMETER_PERTURBATION_AUTO",
            "kind": "PARAMETER_PERTURBATION",
            "value": param_value,
            "source_module": "M25",
            "preregistration_ref": policy["policy_id"],
            "derivation_ref": "ALMAS_ROBUSTNESS_Q5_V1:PARAMETER_PERTURBATION",
            "note": None,
            "auto_derived": True,
        },
        "parameter_details": {
            "delta90": param_delta90,
            "preserved_fraction": param_g,
            "samples": samples,
            "percentile": percentile,
            "percentile_method": policy["percentile_method"],
        },
    }

    if (
        baseline_idd
        and idd_sample_count == len(factors)
        and idd_deltas
    ):
        idd_delta90 = _nearest_rank(idd_deltas, percentile)
        idd_g = idd_preserved_count / idd_sample_count
        idd_value = robustness_component(idd_delta90, idd_g)
        output.update(
            {
                "idd_state": "EVALUABLE",
                "idd_component": {
                    "id": "IDD_STABILITY_AUTO",
                    "kind": "IDD_STABILITY",
                    "value": idd_value,
                    "source_module": "M21",
                    "preregistration_ref": policy["policy_id"],
                    "derivation_ref": "ALMAS_ROBUSTNESS_Q5_V1:IDD_STABILITY",
                    "note": None,
                    "auto_derived": True,
                },
                "idd_details": {
                    "delta90": idd_delta90,
                    "preserved_fraction": idd_g,
                    "baseline_pairwise_idd": baseline_idd,
                    "percentile": percentile,
                    "percentile_method": policy["percentile_method"],
                },
            }
        )
    else:
        output["idd_state"] = "NOT_EVALUABLE"
        output["idd_reason"] = (
            "IDD no fue evaluable en todas las perturbaciones paramétricas."
        )

    return output


def derive_q5_robustness_components(
    raw_input: Mapping[str, Any],
    canonical: Mapping[str, Any],
    *,
    astrology_backend,
    davison_backend,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if policy is None:
        policy = load_q5_robustness_policy()

    ablation = derive_ablation_component(canonical, policy=policy)
    parameter = derive_parameter_and_idd_components(
        raw_input,
        astrology_backend=astrology_backend,
        davison_backend=davison_backend,
        policy=policy,
    )

    components = []
    if ablation.get("state") == "EVALUABLE":
        components.append(ablation["component"])
    if parameter.get("parameter_state") == "EVALUABLE":
        components.append(parameter["parameter_component"])
    if parameter.get("idd_state") == "EVALUABLE":
        components.append(parameter["idd_component"])

    return {
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "components": components,
        "ablation": ablation,
        "parameter": parameter,
        "null_rarity_used": False,
        "temporal_activation_used": False,
        "ice_used": False,
        "iem_final_used": False,
    }
