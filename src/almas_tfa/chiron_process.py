"""Personal Venus–Node–Chiron complexes and process-state firewall.

All aspect contacts and documentary links must be computed/verified upstream.
This module classifies supplied evidence and never modifies structural scoring.
"""
from __future__ import annotations

import json
from importlib import resources
from typing import Any, Mapping

from .astrology_geometry import match_declared_aspect

PROCESS_STATES = {
    "LATENT_ARCHITECTURE", "REACTIVATION", "RECAPITULATION", "CONFRONTATION",
    "REORGANIZATION", "INTEGRATION_WINDOW", "INTEGRATION_DOCUMENTED",
    "CLOSURE_NOT_ESTABLISHED", "INDETERMINATE",
}
COMPLEX_TYPES = {
    "VENUS_NODAL_CORE", "CHIRON_NODAL_LINK", "VENUS_CHIRON_LINK",
    "TRIADIC_TEMPORAL_BRIDGE",
}
POINT_GROUPS = {"VENUS", "CHIRON", "AXIS_NODES"}
PROCESS_MARKERS = {"TENSION", "INTEGRATIVE", "NEUTRAL", "TRANSITIONAL"}
POLICY_ID = "ALMAS_CHIRON_PROCESS_V1"


def load_chiron_process_policy() -> dict[str, Any]:
    resource = resources.files("almas_tfa").joinpath("data", "chiron-process-policy.json")
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != POLICY_ID:
        raise ValueError("Política de CHIRON_PROCESS desconocida.")
    return policy


def summarize_temporal_process(temporal_signals: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Derive a descriptive sequence vector from multiple dated coded signals."""
    if not isinstance(temporal_signals, list):
        raise ValueError("temporal_signals debe ser una lista.")
    dated = []
    for signal in temporal_signals:
        if not isinstance(signal, Mapping):
            raise ValueError("Cada señal temporal debe ser un objeto.")
        marker = signal.get("process_marker")
        if marker is not None and marker not in PROCESS_MARKERS:
            raise ValueError("process_marker no reconocido.")
        if marker and signal.get("exact_datetime"):
            dated.append((str(signal["exact_datetime"]), marker, signal))
    dated.sort(key=lambda item: item[0])
    groups = {str(item[2].get("dependency_group")) for item in dated if item[2].get("dependency_group")}
    if len(dated) < 2:
        vector = "INDETERMINATE"
    else:
        markers = [item[1] for item in dated]
        strengths = [float(item[2].get("strength", 0.0)) for item in dated]
        alternating = any(markers[i] != markers[i - 1] for i in range(1, len(markers)))
        if len(groups) == 1 and any(item[2].get("pass_number", 1) > 1 for item in dated):
            vector = "RECURRING"
        elif len(strengths) >= 2 and all(a < b for a, b in zip(strengths, strengths[1:])):
            vector = "ESCALATING"
        elif markers[0] == "TENSION" and "INTEGRATIVE" in markers[1:]:
            vector = "REORGANIZING"
        elif len(strengths) >= 2 and all(a > b for a, b in zip(strengths, strengths[1:])):
            vector = "DEACTIVATING"
        elif alternating and sum(markers[i] != markers[i - 1] for i in range(1, len(markers))) >= 2:
            vector = "OSCILLATING"
        else:
            vector = "INDETERMINATE"
    geometry = [str(item[2].get("geometry_class", "")).upper() for item in dated]
    tension_count = sum(value in {"HARD", "TENSION"} for value in geometry)
    integrative_count = sum(value in {"HARMONIC", "INTEGRATIVE"} for value in geometry)
    if not geometry or not any(geometry):
        signature = "NOT_EVALUABLE"
    elif tension_count > integrative_count:
        signature = "TENSION_DOMINANT"
    elif integrative_count > tension_count:
        signature = "INTEGRATIVE_GEOMETRY_DOMINANT"
    elif tension_count and integrative_count:
        signature = "MIXED"
    else:
        signature = "TRANSITIONAL"
    return {
        "process_vector": vector,
        "integration_signature": signature,
        "dated_signal_count": len(dated),
        "independent_dependency_group_count": len(groups),
        "dependency_groups": sorted(groups),
        "sequence_evidence_refs": sorted({
            ref for _, _, signal in dated for ref in signal.get("evidence_refs", [])
            if isinstance(ref, str) and ref
        }),
        "epistemic_class": "E_PROJECT_HYPOTHESIS",
        "probability_created": False,
    }


def summarize_complex_temporal_convergence(temporal_signals: list[Mapping[str, Any]]) -> dict[str, Any]:
    """CTC is a transparent count summary; it is not a score or probability."""
    process = summarize_temporal_process(temporal_signals)
    exact = [signal for signal in temporal_signals if isinstance(signal, Mapping) and signal.get("orb") is not None]
    preregistered = [signal for signal in temporal_signals if isinstance(signal, Mapping) and signal.get("preregistered") is True]
    exploratory = [signal for signal in temporal_signals if isinstance(signal, Mapping) and signal.get("preregistered") is False]
    return {
        "independent_dependency_group_count": process["independent_dependency_group_count"],
        "dated_signal_count": process["dated_signal_count"],
        "exactness_values_recorded": len(exact),
        "preregistered_signal_count": len(preregistered),
        "exploratory_signal_count": len(exploratory),
        "multiple_testing_context": "REQUIRES_DECLARED_SEARCH_UNIVERSE",
        "score_created": False,
        "metaphysical_probability_created": False,
        "epistemic_class": "E_PROJECT_HYPOTHESIS",
    }


def normalize_technique_search_audit(
    technique_search: Mapping[str, Any] | None,
    temporal_signals: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Preserve the searched and preregistered universe, including negatives."""
    if technique_search is None:
        tested = sorted({str(item.get("technique_variant") or item.get("technique")) for item in temporal_signals})
        matched = sorted({str(item.get("technique_variant") or item.get("technique")) for item in temporal_signals if item.get("exact_datetime")})
        preregistered = sorted({str(item.get("technique_variant") or item.get("technique")) for item in temporal_signals if item.get("preregistered") is True})
        exploratory = sorted({str(item.get("technique_variant") or item.get("technique")) for item in temporal_signals if item.get("preregistered") is False})
        return {
            "techniques_tested": tested, "techniques_matched": matched,
            "preregistered_techniques": preregistered,
            "exploratory_techniques": exploratory,
            "multiple_testing_context": "UNDECLARED_SEARCH_UNIVERSE",
            "selection_after_observation": None,
            "universe_complete": False,
        }
    if not isinstance(technique_search, Mapping):
        raise ValueError("technique_search debe ser un objeto.")
    fields = ("techniques_tested", "techniques_matched", "preregistered_techniques", "exploratory_techniques")
    normalized: dict[str, Any] = {}
    for field in fields:
        values = technique_search.get(field)
        if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"technique_search.{field} debe ser una lista de textos no vacíos.")
        normalized[field] = sorted(set(values))
    if not set(normalized["techniques_matched"]).issubset(normalized["techniques_tested"]):
        raise ValueError("techniques_matched debe ser subconjunto de techniques_tested.")
    if not set(normalized["preregistered_techniques"]).issubset(normalized["techniques_tested"]):
        raise ValueError("preregistered_techniques debe ser subconjunto de techniques_tested.")
    if not set(normalized["exploratory_techniques"]).issubset(normalized["techniques_tested"]):
        raise ValueError("exploratory_techniques debe ser subconjunto de techniques_tested.")
    if set(normalized["preregistered_techniques"]) & set(normalized["exploratory_techniques"]):
        raise ValueError("Una técnica no puede marcarse a la vez preregistrada y exploratoria.")
    if not isinstance(technique_search.get("multiple_testing_context"), str) or not technique_search["multiple_testing_context"].strip():
        raise ValueError("multiple_testing_context debe declarar el universo/corrección.")
    selection = technique_search.get("selection_after_observation")
    if selection is not None and not isinstance(selection, bool):
        raise ValueError("selection_after_observation debe ser boolean o null.")
    normalized["multiple_testing_context"] = technique_search["multiple_testing_context"]
    normalized["selection_after_observation"] = selection
    normalized["universe_complete"] = technique_search.get("universe_complete") is True
    return normalized


def _canonical_point(value: Any) -> str:
    text = str(value or "").upper().replace("-", "_")
    if text in {"NODE", "NODES", "NORTH_NODE", "SOUTH_NODE", "NN", "SN",
                "TRUE_NORTH_NODE", "TRUE_SOUTH_NODE", "MEAN_NORTH_NODE", "MEAN_SOUTH_NODE"}:
        return "AXIS_NODES"
    return text


def _contact_edges(natal_contacts: Any) -> tuple[set[tuple[str, str]], list[str]]:
    if not isinstance(natal_contacts, list):
        raise ValueError("natal_contacts debe ser una lista explícita.")
    edges: set[tuple[str, str]] = set()
    counterevidence: list[str] = []
    for index, contact in enumerate(natal_contacts, start=1):
        if not isinstance(contact, Mapping):
            raise ValueError("Cada contacto natal debe ser un objeto.")
        a = _canonical_point(contact.get("point_a"))
        b = _canonical_point(contact.get("point_b"))
        orb, limit = contact.get("orb"), contact.get("declared_orb")
        ref = contact.get("aspect_policy_ref")
        if a not in POINT_GROUPS or b not in POINT_GROUPS or a == b:
            counterevidence.append(f"CONTACT_{index}_OUTSIDE_COMPLEX")
            continue
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 for v in (orb, limit)):
            raise ValueError(f"contact {index}: orb y declared_orb deben ser no negativos.")
        if not isinstance(ref, str) or not ref.strip():
            raise ValueError(f"contact {index}: aspect_policy_ref es obligatorio.")
        if float(orb) <= float(limit):
            edges.add(tuple(sorted((a, b))))
        else:
            counterevidence.append(f"CONTACT_{index}_OUTSIDE_DECLARED_ORB")
    return edges, counterevidence


def _connected(nodes: set[str], edges: set[tuple[str, str]]) -> bool:
    if not nodes:
        return False
    reached = {next(iter(nodes))}
    changed = True
    while changed:
        changed = False
        for a, b in edges:
            if a in reached and b in nodes and b not in reached:
                reached.add(b); changed = True
            if b in reached and a in nodes and a not in reached:
                reached.add(a); changed = True
    return reached == nodes


def derive_natal_contacts(
    positions: Mapping[str, Any],
    aspect_policy: Mapping[str, Mapping[str, Any]],
    *,
    aspect_policy_ref: str,
) -> dict[str, Any]:
    """Derive declared-orb contacts from a personal chart for both node variants."""
    if not isinstance(positions, Mapping) or not isinstance(aspect_policy, Mapping):
        raise ValueError("positions y aspect_policy deben ser objetos.")
    if not isinstance(aspect_policy_ref, str) or not aspect_policy_ref.strip():
        raise ValueError("aspect_policy_ref debe identificar la política usada.")
    contacts: list[dict[str, Any]] = []
    counterevidence: list[dict[str, Any]] = []
    pair_specs = [("VENUS", "CHIRON", None), ("VENUS", "NORTH_NODE", "TRUE"),
                  ("CHIRON", "NORTH_NODE", "TRUE"), ("VENUS", "MEAN_NORTH_NODE", "MEAN"),
                  ("CHIRON", "MEAN_NORTH_NODE", "MEAN")]
    pair_results: dict[tuple[str, str, str | None], bool] = {}
    for point_a, point_b, variant in pair_specs:
        left, right = positions.get(point_a), positions.get(point_b)
        if not isinstance(left, Mapping) or not isinstance(right, Mapping):
            counterevidence.append({"id": "MISSING_NATAL_POINT", "points": [point_a, point_b], "node_variant": variant})
            pair_results[(point_a, point_b, variant)] = False
            continue
        a, b = left.get("longitude"), right.get("longitude")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in (a, b)):
            raise ValueError(f"Longitudes no numéricas en {point_a}/{point_b}.")
        match = match_declared_aspect(float(a), float(b), aspect_policy)
        pair_results[(point_a, point_b, variant)] = match is not None
        if match is None:
            counterevidence.append({"id": "NO_DECLARED_NATAL_ASPECT", "points": [point_a, point_b], "node_variant": variant})
            continue
        normalized_a = "AXIS_NODES" if point_a == "NORTH_NODE" else point_a
        normalized_b = "AXIS_NODES" if point_b in {"NORTH_NODE", "MEAN_NORTH_NODE"} else point_b
        contacts.append({
            "point_a": normalized_a,
            "point_b": normalized_b,
            "orb": match["orb"],
            "declared_orb": match["orb_limit"],
            "aspect": match["aspect"],
            "angle": match["angle"],
            "aspect_policy_ref": aspect_policy_ref,
            "node_variant": variant,
            "nodal_axis_id": "LUNAR_NODE_AXIS" if variant else None,
            "epistemic_class": "A_CALCULATED",
        })
    return {
        "contacts": contacts,
        "counterevidence": counterevidence,
        "aspect_policy_ref": aspect_policy_ref,
        "node_variants_examined": ["TRUE", "MEAN"],
        "epistemic_class": "A_CALCULATED",
    }


def assess_chiron_process(
    *,
    natal_contacts: list[Mapping[str, Any]],
    temporal_signals: list[Mapping[str, Any]] | None = None,
    temporal_sequence: Mapping[str, Any] | None = None,
    documentary_evidence: list[Mapping[str, Any]] | None = None,
    technique_search: Mapping[str, Any] | None = None,
    counterevidence: list[Mapping[str, Any]] | None = None,
    complex_id: str = "PTC-001",
) -> dict[str, Any]:
    """Classify a personal complex without making clinical or ontological claims."""
    if not isinstance(complex_id, str) or not complex_id.strip():
        raise ValueError("complex_id es obligatorio.")
    policy = load_chiron_process_policy()
    edges, contact_counterevidence = _contact_edges(natal_contacts)
    types: list[str] = []
    for edge in sorted(edges):
        if edge == tuple(sorted(("VENUS", "AXIS_NODES"))):
            types.append("VENUS_NODAL_CORE")
        elif edge == tuple(sorted(("CHIRON", "AXIS_NODES"))):
            types.append("CHIRON_NODAL_LINK")
        elif edge == tuple(sorted(("VENUS", "CHIRON"))):
            types.append("VENUS_CHIRON_LINK")
    triadic = _connected(POINT_GROUPS, edges)
    if triadic:
        complex_type = "VENUS_NODAL_CHIRON"
    elif types:
        complex_type = "+".join(sorted(set(types)))
    else:
        complex_type = "NONE_ESTABLISHED"

    signals = temporal_signals or []
    if not isinstance(signals, list):
        raise ValueError("temporal_signals debe ser una lista.")
    normalized_signals: list[dict[str, Any]] = []
    temporal_edges: set[tuple[str, str]] = set()
    groups: set[str] = set()
    pass_numbers: list[int] = []
    for signal in signals:
        if not isinstance(signal, Mapping):
            raise ValueError("Cada señal temporal debe ser un objeto.")
        required = ("signal_id", "technique", "technique_variant", "exact_datetime",
                    "source_point", "target_point", "relation", "dependency_group")
        if any(not isinstance(signal.get(key), str) or not signal.get(key).strip() for key in required):
            raise ValueError("Cada señal requiere trazabilidad cinemática completa.")
        if signal.get("node_variant") not in {None, "TRUE", "MEAN"}:
            raise ValueError("node_variant debe ser TRUE, MEAN o null.")
        if signal.get("preregistered") is False:
            status = "EXPLORATORY"
        else:
            status = str(signal.get("window_status", "EXPLORATORY"))
        normalized = dict(signal)
        normalized["window_status"] = status
        normalized["epistemic_class"] = "B_TECHNIQUE"
        normalized_signals.append(normalized)
        source = _canonical_point(signal.get("source_point"))
        target = _canonical_point(signal.get("target_point"))
        if source in POINT_GROUPS and target in POINT_GROUPS and source != target:
            temporal_edges.add(tuple(sorted((source, target))))
        groups.add(str(signal["dependency_group"]))
        number = signal.get("pass_number")
        if isinstance(number, int) and not isinstance(number, bool):
            pass_numbers.append(number)

    docs = documentary_evidence or []
    if not isinstance(docs, list):
        raise ValueError("documentary_evidence debe ser una lista.")
    documentary_support = []
    for evidence in docs:
        if not isinstance(evidence, Mapping):
            raise ValueError("Cada evidencia documental debe ser un objeto.")
        quality = evidence.get("documentary_quality", evidence.get("quality"))
        source_refs = evidence.get("source_refs", [evidence.get("source_ref")])
        roles = evidence.get("evidence_roles", [evidence.get("evidence_role")])
        valid = (
            evidence.get("module") == "M27"
            and isinstance(evidence.get("event_ref"), str) and bool(evidence.get("event_ref"))
            and isinstance(source_refs, list) and any(isinstance(ref, str) and ref for ref in source_refs)
            and isinstance(roles, list) and "INTEGRATION_OUTCOME" in roles
            and quality in {"DQ1_PRIMARY_DOCUMENT", "DQ2_DIRECT_SELF_REPORT"}
            and evidence.get("documentary_quality_contract_met") is True
            and evidence.get("date_precision_contract_met") is True
            and evidence.get("fact_interpretation_separated") is True
        )
        if valid:
            documentary_support.append(dict(evidence))

    has_architecture = complex_type != "NONE_ESTABLISHED"
    temporal_bridge = _connected(POINT_GROUPS, temporal_edges)
    if not has_architecture and temporal_bridge:
        complex_type = "TRIADIC_TEMPORAL_BRIDGE"
    sequence = temporal_sequence or summarize_temporal_process(normalized_signals)
    sequence_state = sequence.get("process_vector") if isinstance(sequence, Mapping) else None
    coherent_sequence = (
        isinstance(sequence, Mapping)
        and sequence.get("sequence_evidence_refs")
        and sequence_state in {"REORGANIZING", "DEACTIVATING"}
        and len(groups) >= int(policy["independent_dependency_groups_required_for_integration_window"])
    )
    if not has_architecture:
        state = "INDETERMINATE"
    elif documentary_support and coherent_sequence:
        state = "INTEGRATION_DOCUMENTED"
    elif coherent_sequence:
        state = "INTEGRATION_WINDOW"
    elif normalized_signals:
        state = "RECAPITULATION" if any(number > 1 for number in pass_numbers) else "REACTIVATION"
    else:
        state = "LATENT_ARCHITECTURE"

    counter = list(counterevidence or [])
    if not isinstance(counter, list) or any(not isinstance(item, Mapping) for item in counter):
        raise ValueError("counterevidence debe ser una lista de objetos.")
    counter.extend({"id": item, "epistemic_class": "A_CALCULATED"} for item in contact_counterevidence)
    invalid_docs = len(docs) - len(documentary_support)
    if invalid_docs:
        counter.append({
            "id": "DOCUMENTARY_EVIDENCE_NOT_QUALIFIED",
            "count": invalid_docs,
            "epistemic_class": "A_CALCULATED",
        })
    architecture_status = "SUPPORTED" if has_architecture else "INSUFFICIENT"
    status = "SUPPORTED" if has_architecture else "INSUFFICIENT"
    search_audit = normalize_technique_search_audit(technique_search, normalized_signals)
    convergence = summarize_complex_temporal_convergence(normalized_signals)
    convergence["multiple_testing_context"] = search_audit["multiple_testing_context"]
    return {
        "policy_id": POLICY_ID,
        "complex_id": complex_id,
        "complex_type": complex_type,
        "natal_architecture": {
            "contacts": [dict(contact) for contact in natal_contacts],
            "contact_edges": [list(edge) for edge in sorted(edges)],
            "status": architecture_status,
            "temporal_bridge_present": temporal_bridge,
            "vulnerability_clinical_inference": False,
        },
        "nodal_variants": {
            "node_variant_policy": "TRUE_AND_MEAN_SHARE_ONE_AXIS",
            "independent_axis_count": 1,
        },
        "temporal_signals": normalized_signals,
        "dependency_groups": sorted(groups),
        "exact_hits": [signal for signal in normalized_signals if signal.get("exact_datetime")],
        "process_state": state,
        "temporal_process_vector": sequence_state or "INDETERMINATE",
        "integration_signature": sequence.get("integration_signature", "NOT_EVALUABLE") if isinstance(sequence, Mapping) else "NOT_EVALUABLE",
        "temporal_convergence": convergence,
        "technique_search_audit": search_audit,
        "counterevidence": counter,
        "documentary_evidence": documentary_support,
        "status": status,
        "epistemic_class": "E_PROJECT_HYPOTHESIS",
        "structural_scoring_modified": policy["structural_scoring_modified"],
        "ontological_category_created": policy["ontological_category_created"],
    }
