from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping

from .core import score_model, supported_gate
from .module_contract import ExecutionStatus, ModuleResult


POLICY_RESOURCE = "canonical-assembly-policy.json"
POLICY_PACKAGE = "almas_tfa"
MODELS = ("AF", "KA", "AG", "LG")


def load_canonical_assembly_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_CANONICAL_ASSEMBLY_V1":
        raise ValueError("Política Q7 de ensamblaje canónico desconocida.")
    return policy


def _completed(prior_results: Mapping[str, Any], module_id: str) -> bool:
    result = prior_results.get(module_id)
    return (
        isinstance(result, ModuleResult)
        and result.status is ExecutionStatus.COMPLETED
    )


def _half_or_full(
    prior_results: Mapping[str, Any],
    module_ids: tuple[str, ...],
    *,
    full_requires_all: bool = True,
) -> float:
    flags = [_completed(prior_results, module_id) for module_id in module_ids]
    if all(flags):
        return 1.0
    if any(flags):
        return 0.5
    return 0.0


def _angles_houses_quality(canonical: Mapping[str, Any]) -> float:
    context = canonical.get("natal_context")
    if not isinstance(context, Mapping):
        return 0.0
    subjects = context.get("subjects")
    if not isinstance(subjects, Mapping) or not subjects:
        return 0.0

    complete = 0
    partial = 0
    for subject in subjects.values():
        if not isinstance(subject, Mapping):
            continue
        angles = subject.get("angles")
        cusps = subject.get("house_cusps")
        has_angles = isinstance(angles, Mapping) and bool(angles)
        has_twelve_cusps = (
            isinstance(cusps, Mapping)
            and all(str(i) in cusps for i in range(1, 13))
        )
        if has_angles and has_twelve_cusps:
            complete += 1
        elif has_angles or (
            isinstance(cusps, Mapping) and bool(cusps)
        ):
            partial += 1

    subject_count = len(subjects)
    if complete == subject_count:
        return 1.0
    if complete or partial:
        return 0.5
    return 0.0


def derive_canonical_coverage(
    canonical: Mapping[str, Any],
    prior_results: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if policy is None:
        policy = load_canonical_assembly_policy()

    domains = {
        "BASE_NATAL": 1.0 if _completed(prior_results, "M02") else 0.0,
        "SYNASTRY_NODES": _half_or_full(
            prior_results,
            ("M03", "M04"),
        ),
        "ANGLES_HOUSES": _angles_houses_quality(canonical),
        "SYMMETRIES": _half_or_full(
            prior_results,
            ("M05", "M06"),
        ),
        "RELATIONSHIP_CHARTS": _half_or_full(
            prior_results,
            ("M07", "M08", "M09"),
        ),
        "DRACONIC": (
            1.0
            if _completed(prior_results, "M10")
            and _completed(prior_results, "M11")
            else (
                0.5
                if _completed(prior_results, "M10")
                or _completed(prior_results, "M11")
                else 0.0
            )
        ),
        "LOTS_SECONDARY": _half_or_full(
            prior_results,
            ("M13", "M14"),
        ),
    }

    allowed = {float(value) for value in policy["coverage"]["allowed_q"]}
    if any(value not in allowed for value in domains.values()):
        raise ValueError("Q7 produjo q fuera de la política de cobertura.")

    icc = 100.0 * sum(domains.values()) / len(domains)
    return {
        "ICC": icc,
        "domains": {
            domain: {
                "q": value,
            }
            for domain, value in domains.items()
        },
        "formula": policy["coverage"]["formula"],
        "policy_id": policy["policy_id"],
    }


def _counterevidence_state(
    canonical: Mapping[str, Any],
) -> tuple[dict[str, float] | None, dict[str, bool], list[dict[str, Any]]]:
    counter = canonical.get("counterevidence")
    if not isinstance(counter, Mapping):
        return None, {model: False for model in MODELS}, []

    ice_raw = counter.get("ice_by_model")
    ice_by_model = None
    if isinstance(ice_raw, Mapping):
        ice_by_model = {
            model: float(ice_raw.get(model, 0.0))
            for model in MODELS
        }

    essential = {model: False for model in MODELS}
    flattened: list[dict[str, Any]] = []
    models = counter.get("models")
    if isinstance(models, Mapping):
        for model in MODELS:
            model_data = models.get(model)
            if not isinstance(model_data, Mapping):
                continue
            essential[model] = bool(
                model_data.get("essential_contradiction", False)
            )
            items = model_data.get("items")
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, Mapping):
                        flattened.append(dict(item))

    return ice_by_model, essential, flattened


def _global_idd(canonical: Mapping[str, Any]) -> tuple[float | None, dict[str, Any]]:
    raw = canonical.get("pairwise_idd")
    if not isinstance(raw, Mapping):
        return None, {}

    pairwise: dict[str, Any] = {}
    values: list[float] = []
    for pair_id, data in raw.items():
        if not isinstance(data, Mapping):
            continue
        value = data.get("idd")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        value = float(value)
        values.append(value)
        pairwise[str(pair_id)] = {
            "idd": value,
            "band": data.get("band"),
        }

    return (min(values) if values else None), pairwise


def _temporal_index(canonical: Mapping[str, Any]) -> float | None:
    temporal = canonical.get("temporal_activation")
    if not isinstance(temporal, Mapping):
        return None
    value = temporal.get("iat")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _doctrine_claims(canonical: Mapping[str, Any]) -> list[dict[str, Any]]:
    doctrine = canonical.get("doctrine_hermeneutics")
    if not isinstance(doctrine, Mapping):
        return []
    claims = doctrine.get("claims")
    if not isinstance(claims, list):
        return []
    return [
        dict(item) for item in claims if isinstance(item, Mapping)
    ]


def _evidence_from_roots(canonical: Mapping[str, Any]) -> list[dict[str, Any]]:
    roots_obj = canonical.get("independent_roots")
    roots = roots_obj.get("roots") if isinstance(roots_obj, Mapping) else None
    if not isinstance(roots, list):
        return []

    evidence = []
    for root in roots:
        if not isinstance(root, Mapping):
            continue
        root_id = root.get("root_id")
        if not isinstance(root_id, str) or not root_id:
            continue
        evidence.append(
            {
                "evidence_id": "ROOT:" + root_id,
                "source_module": "M17",
                "root_id": root_id,
                "root_key": root.get("root_key"),
                "strength": root.get("strength"),
                "strength_state": root.get("strength_state"),
                "core_eligible": bool(root.get("core_eligible")),
                "dependency_families": list(
                    root.get("dependency_families", [])
                ),
            }
        )
    return evidence


def _limitations(prior_results: Mapping[str, Any]) -> list[str]:
    output: list[str] = []
    for module_id in sorted(prior_results):
        result = prior_results[module_id]
        if not isinstance(result, ModuleResult):
            continue
        for limitation in result.limitations:
            value = f"{module_id}: {limitation}"
            if value not in output:
                output.append(value)
    return output


def assemble_canonical_analysis(
    canonical: Mapping[str, Any],
    prior_results: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Serializa M01–M29 en canonical_analysis sin recalcular astrología."""

    if policy is None:
        policy = load_canonical_assembly_policy()

    required_namespaces = (
        "independent_roots",
        "pillars",
        "structural_model_indices",
        "robustness_index",
    )
    missing = [
        name for name in required_namespaces
        if not isinstance(canonical.get(name), Mapping)
    ]
    if missing:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "MISSING_CANONICAL_NAMESPACES:" + ",".join(missing),
        }

    coverage = derive_canonical_coverage(
        canonical,
        prior_results,
        policy=policy,
    )
    icc = float(coverage["ICC"])

    robustness = canonical["robustness_index"]
    irc = robustness.get("irc")
    r_min = robustness.get("r_min")
    if (
        isinstance(irc, bool)
        or not isinstance(irc, (int, float))
        or isinstance(r_min, bool)
        or not isinstance(r_min, (int, float))
    ):
        return {
            "state": "NOT_EVALUABLE",
            "reason": "ROBUSTNESS_INDEX_INCOMPLETE",
        }
    irc = float(irc)
    r_min = float(r_min)

    pillars = canonical["pillars"]
    if not isinstance(pillars, Mapping):
        return {
            "state": "NOT_EVALUABLE",
            "reason": "PILLARS_NOT_MAPPING",
        }

    ice_by_model, essential, counter_items = _counterevidence_state(
        canonical
    )
    ice_evaluable = ice_by_model is not None

    models: dict[str, Any] = {}
    model_ice_values: list[float] = []
    for model in MODELS:
        ice_value = (
            float(ice_by_model[model])
            if ice_by_model is not None
            else 0.0
        )
        if ice_evaluable:
            model_ice_values.append(ice_value)

        score = score_model(model, pillars, ice=ice_value)
        if not score.essential_evaluable:
            state = "NOT_EVALUABLE"
            iem = None
            iem_final = None
        elif essential.get(model, False):
            state = "CONTRADICTED"
            iem = score.iem_final if ice_evaluable else score.iem_pre
            iem_final = score.iem_final if ice_evaluable else None
        else:
            gate = False
            if ice_evaluable:
                gate = supported_gate(
                    score,
                    icc=icc,
                    irc=irc,
                    r_min=r_min,
                    essential_contradiction=False,
                )
            if gate:
                state = "SUPPORTED"
            elif score.iem_pre > 0:
                state = "COMPATIBLE"
            else:
                state = "INSUFFICIENT"
            iem = score.iem_final if ice_evaluable else score.iem_pre
            iem_final = score.iem_final if ice_evaluable else None

        models[model] = {
            "iem": iem,
            "state": state,
            "core": score.core,
            "support": score.support,
            "iem_pre": score.iem_pre,
            "iem_final": iem_final,
            "ice": ice_value if ice_evaluable else None,
            "ice_state": (
                "EVALUABLE" if ice_evaluable else "NOT_EVALUABLE"
            ),
            "supported_gate": state == "SUPPORTED",
        }

    global_idd, pairwise_idd = _global_idd(canonical)
    global_ice = max(model_ice_values) if model_ice_values else None
    iat = _temporal_index(canonical)

    temporal = {}
    if isinstance(canonical.get("temporal_activation"), Mapping):
        temporal["activation"] = canonical["temporal_activation"]
    if isinstance(canonical.get("documentary_events"), Mapping):
        temporal["events"] = canonical["documentary_events"]

    assembled = {
        "schema_version": "1.0.0",
        "analysis_mode": policy["analysis_mode"],
        "evidence": _evidence_from_roots(canonical),
        "models": models,
        "indices": {
            "IDD": global_idd,
            "IAT": iat,
            "ICC": icc,
            "IRC": irc,
            "ICE": global_ice,
        },
        "pairwise_idd": pairwise_idd,
        "coverage": coverage,
        "robustness": {
            "IRC": irc,
            "R_min": r_min,
            "component_count": robustness.get("component_count"),
            "components": robustness.get("components", []),
            "null_model_rarity_used_as_robustness": False,
        },
        "counterevidence": counter_items,
        "counterevidence_state": {
            "ice_evaluable": ice_evaluable,
            "ice_by_model": ice_by_model,
            "essential_contradictions": essential,
        },
        "ontology": {},
        "doctrine": _doctrine_claims(canonical),
        "temporal": temporal,
        "limitations": _limitations(prior_results),
        "assembly": {
            "policy_id": policy["policy_id"],
            "policy_status": policy["status"],
            "epistemic_class": policy["epistemic_class"],
            "source": "M01_M29_CANONICAL_NAMESPACES",
            "recalculated_astrology": False,
            "recalculated_roots": False,
            "recalculated_pillars": False,
        },
    }

    ontology = canonical.get("ontological_discrimination")
    if isinstance(ontology, Mapping):
        assembled["ontological_discrimination"] = dict(ontology)

    null_models = canonical.get("null_models")
    if isinstance(null_models, Mapping):
        assembled["null_models"] = null_models

    return {
        "state": "EVALUABLE",
        "canonical_analysis": assembled,
        "coverage": coverage,
        "ice_evaluable": ice_evaluable,
    }
