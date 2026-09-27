from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping

from .analysis_profiles import resolve_analysis_profile
from .core import score_model, supported_gate
from .module_contract import ExecutionStatus, ModuleResult


POLICY_RESOURCE = "canonical-assembly-policy.json"
POLICY_PACKAGE = "almas_tfa"
MODELS = ("AF", "KA", "AG", "LG")


def load_canonical_assembly_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_CANONICAL_ASSEMBLY_V2":
        raise ValueError("Política de ensamblaje canónico desconocida.")
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
        raise ValueError("Q7/Q14 produjo q fuera de la política de cobertura.")

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


def _astronomy_backend_trace(canonical: Mapping[str, Any]) -> dict[str, Any]:
    natal = canonical.get("natal")
    backend = natal.get("backend") if isinstance(natal, Mapping) else None
    if not isinstance(backend, Mapping):
        return {
            "state": "NOT_AVAILABLE",
            "backend_id": None,
            "backend_version": None,
            "provenance_state": "NOT_AVAILABLE",
            "provenance": None,
        }

    backend_id = backend.get("id")
    backend_version = backend.get("version")
    provenance = backend.get("provenance")
    declared = isinstance(provenance, Mapping)

    return {
        "state": "AVAILABLE",
        "backend_id": (
            str(backend_id)
            if isinstance(backend_id, str) and backend_id
            else None
        ),
        "backend_version": (
            str(backend_version)
            if isinstance(backend_version, str) and backend_version
            else None
        ),
        "provenance_state": "DECLARED" if declared else "NOT_DECLARED",
        "provenance": dict(provenance) if declared else None,
    }


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


HOUSE_OVERLAY_NATAL_FAMILIES = {"SYN", "DECLINATION"}


def _house_rulership_context(
    subjects: Mapping[str, Any],
    *,
    target_subject: str,
    house: int,
) -> dict[str, Any] | None:
    target = subjects.get(target_subject)
    if not isinstance(target, Mapping):
        return None

    rulerships = target.get("rulerships")
    rule = (
        rulerships.get(str(house))
        if isinstance(rulerships, Mapping)
        else None
    )
    if not isinstance(rule, Mapping):
        return None

    cusp_sign = rule.get("cusp_sign")
    raw_rulers = rule.get("rulers")
    if not isinstance(cusp_sign, str) or not cusp_sign:
        return None
    if not isinstance(raw_rulers, list) or not raw_rulers:
        return None

    point_signs = target.get("point_signs")
    placements = target.get("house_placements")
    ruler_context: list[dict[str, Any]] = []

    for raw_ruler in raw_rulers:
        ruler_id = str(raw_ruler).strip().upper()
        if not ruler_id:
            continue

        sign = None
        if isinstance(point_signs, Mapping):
            sign_data = point_signs.get(ruler_id)
            if isinstance(sign_data, Mapping):
                value = sign_data.get("sign")
                if isinstance(value, str) and value:
                    sign = value

        ruler_house = None
        if isinstance(placements, Mapping):
            placement = placements.get(ruler_id)
            if isinstance(placement, Mapping):
                value = placement.get("house")
                if (
                    isinstance(value, int)
                    and not isinstance(value, bool)
                    and 1 <= value <= 12
                ):
                    ruler_house = value

        ruler_context.append(
            {
                "ruler_id": ruler_id,
                "sign": sign,
                "house": ruler_house,
            }
        )

    rulers = [item["ruler_id"] for item in ruler_context]
    if not rulers:
        return None

    return {
        "cusp_sign": cusp_sign,
        "rulers": rulers,
        "ruler_context": ruler_context,
    }


def _house_overlay_for_point(
    cross: Mapping[str, Any],
    subjects: Mapping[str, Any],
    *,
    source_subject: str,
    point_id: str,
    target_subject: str,
) -> dict[str, Any] | None:
    if source_subject == target_subject:
        return None
    if point_id.startswith("AXIS_"):
        return None

    overlay = cross.get(f"{source_subject}_IN_{target_subject}")
    placements = (
        overlay.get("placements")
        if isinstance(overlay, Mapping)
        else None
    )
    if not isinstance(placements, Mapping):
        return None

    placement = placements.get(point_id)
    resolved_point_id = point_id
    if not isinstance(placement, Mapping):
        for candidate_id, candidate in placements.items():
            if str(candidate_id).upper() == point_id:
                placement = candidate
                resolved_point_id = str(candidate_id)
                break
    if not isinstance(placement, Mapping):
        return None

    house = placement.get("house")
    if isinstance(house, bool) or not isinstance(house, int):
        return None
    if not 1 <= house <= 12:
        return None

    output = {
        "source_subject": source_subject,
        "point_id": resolved_point_id,
        "target_subject": target_subject,
        "house": house,
    }
    rulership = _house_rulership_context(
        subjects,
        target_subject=target_subject,
        house=house,
    )
    if rulership is not None:
        output["rulership"] = rulership
    return output


def _root_house_overlays(
    canonical: Mapping[str, Any],
    root: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Une una raíz M17 con casas M04 sólo desde contactos natales compatibles."""

    dependency_families = {
        str(value)
        for value in root.get("dependency_families", [])
        if str(value)
    }
    if not dependency_families.intersection(HOUSE_OVERLAY_NATAL_FAMILIES):
        return []

    context = canonical.get("natal_context")
    cross = (
        context.get("cross_house_placements")
        if isinstance(context, Mapping)
        else None
    )
    subjects = (
        context.get("subjects")
        if isinstance(context, Mapping)
        else None
    )
    if not isinstance(cross, Mapping):
        return []
    if not isinstance(subjects, Mapping):
        subjects = {}

    output_by_key: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    concrete_contacts = root.get("concrete_contacts")

    if isinstance(concrete_contacts, list) and concrete_contacts:
        for concrete in concrete_contacts:
            if not isinstance(concrete, Mapping):
                continue
            if (
                str(concrete.get("dependency_family", ""))
                not in HOUSE_OVERLAY_NATAL_FAMILIES
            ):
                continue

            subject_a = str(concrete.get("subject_a", "")).strip()
            subject_b = str(concrete.get("subject_b", "")).strip()
            point_a = str(concrete.get("point_a", "")).strip().upper()
            point_b = str(concrete.get("point_b", "")).strip().upper()
            if not subject_a or not subject_b or not point_a or not point_b:
                continue

            for source_subject, point_id, target_subject in (
                (subject_a, point_a, subject_b),
                (subject_b, point_b, subject_a),
            ):
                item = _house_overlay_for_point(
                    cross,
                    subjects,
                    source_subject=source_subject,
                    point_id=point_id,
                    target_subject=target_subject,
                )
                if item is None:
                    continue
                key = (
                    item["source_subject"],
                    item["point_id"],
                    item["target_subject"],
                    item["house"],
                )
                output_by_key[key] = item
    else:
        # Compatibilidad con raíces importadas anteriores a concrete_contacts.
        root_key = root.get("root_key")
        if isinstance(root_key, str) and root_key:
            parts = root_key.split("|")
            if len(parts) >= 2:
                endpoints: list[tuple[str, str]] = []
                for part in parts[:2]:
                    if ":" not in part:
                        endpoints = []
                        break
                    subject_id, point_id = part.split(":", 1)
                    subject_id = subject_id.strip()
                    point_id = point_id.strip().upper()
                    if not subject_id or not point_id:
                        endpoints = []
                        break
                    endpoints.append((subject_id, point_id))

                if len(endpoints) == 2:
                    for index, (source_subject, point_id) in enumerate(endpoints):
                        target_subject = endpoints[1 - index][0]
                        item = _house_overlay_for_point(
                            cross,
                            subjects,
                            source_subject=source_subject,
                            point_id=point_id,
                            target_subject=target_subject,
                        )
                        if item is None:
                            continue
                        key = (
                            item["source_subject"],
                            item["point_id"],
                            item["target_subject"],
                            item["house"],
                        )
                        output_by_key[key] = item

    return [
        output_by_key[key]
        for key in sorted(output_by_key)
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
        dependency_families = list(
            root.get("dependency_families", [])
        )
        evidence.append(
            {
                "evidence_id": "ROOT:" + root_id,
                "source_module": "M17",
                "root_id": root_id,
                "root_key": root.get("root_key"),
                "strength": root.get("strength"),
                "strength_state": root.get("strength_state"),
                "core_eligible": bool(root.get("core_eligible")),
                "dependency_families": dependency_families,
                "independent_family_count": int(
                    root.get(
                        "independent_family_count",
                        len(dependency_families),
                    )
                ),
                "point_ids": list(root.get("point_ids", [])),
                "relation_ids": list(root.get("relation_ids", [])),
                "concrete_contacts": [
                    dict(item)
                    for item in root.get("concrete_contacts", [])
                    if isinstance(item, Mapping)
                ],
                "max_exactness": root.get("max_exactness"),
                "house_overlays": _root_house_overlays(
                    canonical,
                    root,
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


def _timed_architecture_present(canonical: Mapping[str, Any]) -> bool:
    roots_obj = canonical.get("independent_roots")
    roots = roots_obj.get("roots") if isinstance(roots_obj, Mapping) else None
    if not isinstance(roots, list):
        return False
    timed_points = {
        "AXIS_HORIZON",
        "AXIS_MERIDIAN",
        "AXIS_VERTEX",
        "PART_OF_FORTUNE",
        "FORTUNE",
    }
    for root in roots:
        if not isinstance(root, Mapping):
            continue
        point_ids = root.get("point_ids")
        if not isinstance(point_ids, list):
            continue
        if timed_points & {str(value).upper() for value in point_ids}:
            return True
    return False


def _birth_time_component_present(robustness: Mapping[str, Any]) -> bool:
    components = robustness.get("components")
    if not isinstance(components, list):
        return False
    return any(
        isinstance(item, Mapping)
        and item.get("kind") == "BIRTH_TIME"
        for item in components
    )


def assemble_canonical_analysis(
    canonical: Mapping[str, Any],
    prior_results: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
    analysis_profile: str | None = None,
) -> dict[str, Any]:
    """Serializa M01–M29 en canonical_analysis sin recalcular astrología."""

    if policy is None:
        policy = load_canonical_assembly_policy()

    profile = resolve_analysis_profile(analysis_profile)

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

    timed_architecture = _timed_architecture_present(canonical)
    birth_time_component = _birth_time_component_present(robustness)
    require_birth_time = bool(
        policy["model_state"].get(
            "supported_requires_birth_time_component_when_timed_architecture",
            False,
        )
    )
    birth_time_gate_ok = (
        not require_birth_time
        or not timed_architecture
        or birth_time_component
    )

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
            if ice_evaluable and birth_time_gate_ok:
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
            "birth_time_gate_required": require_birth_time and timed_architecture,
            "birth_time_gate_satisfied": birth_time_gate_ok,
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
        "analysis_mode": profile["analysis_mode"],
        "analysis_profile": profile["profile_id"],
        "profile_policy_id": profile["policy_id"],
        "astronomy_backend": _astronomy_backend_trace(canonical),
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
            "timed_architecture_present": timed_architecture,
            "birth_time_component_present": birth_time_component,
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
            "analysis_profile": profile,
            "recalculated_astrology": False,
            "recalculated_roots": False,
            "recalculated_pillars": False,
        },
    }

    pillar_attribution = canonical.get("pillar_attribution")
    if isinstance(pillar_attribution, Mapping):
        motifs = pillar_attribution.get("semantic_motifs")
        if isinstance(motifs, Mapping):
            assembled["semantic_motifs"] = motifs

    ontology = canonical.get("ontological_discrimination")
    if isinstance(ontology, Mapping):
        assembled["ontological_discrimination"] = dict(ontology)

    null_models = canonical.get("null_models")
    if isinstance(null_models, Mapping):
        assembled["null_models"] = null_models

    time_sensitivity = canonical.get("time_sensitivity")
    if isinstance(time_sensitivity, Mapping):
        assembled["time_sensitivity"] = time_sensitivity

    return {
        "state": "EVALUABLE",
        "canonical_analysis": assembled,
        "coverage": coverage,
        "ice_evaluable": ice_evaluable,
        "analysis_profile": profile,
    }
