from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


SOURCE_SPECS = {
    "synastry": {
        "module_id": "M03",
        "technique_family": "SYN",
        "dependency_family": "SYN",
        "support_only": False,
        "core_eligible": True,
        "directional": False,
    },
    "declinations": {
        "module_id": "M05",
        "technique_family": "DECLINATION",
        "dependency_family": "DECLINATION",
        "support_only": False,
        "core_eligible": True,
        "directional": False,
    },
    "antiscia": {
        "module_id": "M06",
        "technique_family": "ANTISCIA",
        "dependency_family": "ANTISCIA",
        "support_only": False,
        "core_eligible": True,
        "directional": False,
    },
    "relationship_chart_consonance": {
        "module_id": "M09",
        "technique_family": "RELCHART",
        "dependency_family": "RELCHART",
        "support_only": False,
        "core_eligible": True,
        "directional": False,
    },
    "natal_draconic_cross": {
        "module_id": "M11",
        "technique_family": "NATAL_DRACONIC",
        "dependency_family": "NATAL_DRACONIC",
        "support_only": False,
        "core_eligible": True,
        "directional": True,
    },
    "draconic_draconic": {
        "module_id": "M12",
        "technique_family": "DRACONIC_DD",
        "dependency_family": "DRACONIC_DD",
        "support_only": True,
        "core_eligible": False,
        "directional": False,
    },
    "secondary_symbolic": {
        "module_id": "M14",
        "technique_family": "SECONDARY",
        "dependency_family": "SECONDARY",
        "support_only": True,
        "core_eligible": False,
        "directional": False,
    },
}

AXIS_GROUPS = {
    "ASC": "AXIS_HORIZON",
    "DSC": "AXIS_HORIZON",
    "MC": "AXIS_MERIDIAN",
    "IC": "AXIS_MERIDIAN",
    "NORTH_NODE": "AXIS_NODES",
    "SOUTH_NODE": "AXIS_NODES",
    "NN": "AXIS_NODES",
    "SN": "AXIS_NODES",
    "VERTEX": "AXIS_VERTEX",
    "ANTI_VERTEX": "AXIS_VERTEX",
    "ANTIVERTEX": "AXIS_VERTEX",
}


def _normalized_point(point_id: str) -> str:
    return AXIS_GROUPS.get(point_id.upper(), point_id.upper())


def _relation_signature(contact: Mapping[str, Any], endpoints: tuple[str, str]) -> str:
    relation = str(contact.get("aspect") or contact.get("relation") or "UNSPECIFIED")
    angle = contact.get("angle")

    if any(endpoint.startswith("AXIS_") for endpoint in endpoints) and angle is not None:
        value = float(angle)
        reduced = min(value, abs(180.0 - value))
        return f"AXIS_ANGLE:{reduced:.6f}"

    return relation


def _root_key(
    contact: Mapping[str, Any],
    *,
    directional: bool,
) -> str:
    subject_a = str(contact.get("subject_a", "A"))
    subject_b = str(contact.get("subject_b", "B"))
    point_a = _normalized_point(str(contact.get("point_a", "UNKNOWN_A")))
    point_b = _normalized_point(str(contact.get("point_b", "UNKNOWN_B")))

    endpoint_a = f"{subject_a}:{point_a}"
    endpoint_b = f"{subject_b}:{point_b}"

    if directional:
        endpoints = (endpoint_a, endpoint_b)
    else:
        endpoints = tuple(sorted((endpoint_a, endpoint_b)))

    relation = _relation_signature(contact, (point_a, point_b))

    layer_a = str(contact.get("layer_a", ""))
    layer_b = str(contact.get("layer_b", ""))
    layer_suffix = f"|{layer_a}>{layer_b}" if directional else ""

    return f"{endpoints[0]}|{endpoints[1]}|{relation}{layer_suffix}"


def m15_evidence_extraction(context: ModuleContext) -> ModuleResult:
    """M15: normaliza contactos geométricos sin inventar pesos ni ontología."""

    evidence: list[dict[str, Any]] = []
    counters: dict[str, int] = defaultdict(int)

    for canonical_key, spec in SOURCE_SPECS.items():
        source = context.canonical_snapshot.get(canonical_key)
        if not isinstance(source, Mapping):
            continue

        contacts = source.get("contacts")
        if not isinstance(contacts, list):
            continue

        for contact in contacts:
            if not isinstance(contact, Mapping):
                continue

            counters[spec["module_id"]] += 1
            evidence_id = (
                f"E-{spec['module_id']}-{counters[spec['module_id']]:04d}"
            )
            exactness = contact.get("exactness")
            root_key = _root_key(contact, directional=bool(spec["directional"]))

            evidence.append(
                {
                    "evidence_id": evidence_id,
                    "source_module": spec["module_id"],
                    "canonical_source": canonical_key,
                    "technique_family": spec["technique_family"],
                    "dependency_family": spec["dependency_family"],
                    "support_only": bool(
                        contact.get("support_only", spec["support_only"])
                    ),
                    "core_eligible": bool(spec["core_eligible"]),
                    "directional": bool(spec["directional"]),
                    "root_key": root_key,
                    "exactness": (
                        float(exactness) if exactness is not None else None
                    ),
                    "contact": dict(contact),
                }
            )

    if not evidence:
        return not_evaluable_result(
            "M15",
            "No existen contactos canónicos extraíbles en las capas implementadas.",
        )

    evidence.sort(key=lambda x: (x["root_key"], x["dependency_family"], x["evidence_id"]))
    output = {
        "items": evidence,
        "count": len(evidence),
        "strength_policy_applied": False,
    }

    return ModuleResult(
        module_id="M15",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"evidence_graph": output},
        limitations=(
            "M15 no asigna pesos de técnica, factor horario ni coeficientes de aspecto.",
        ),
    )


def m16_dependency_deduplication(context: ModuleContext) -> ModuleResult:
    """M16: elimina multiplicación dentro de una misma familia dependiente."""

    graph = context.canonical_snapshot.get("evidence_graph")
    if not isinstance(graph, Mapping):
        return not_evaluable_result("M16", "Falta la salida de M15.")

    items = graph.get("items")
    if not isinstance(items, list) or not items:
        return not_evaluable_result("M16", "M15 no contiene evidencia.")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        if not isinstance(item, Mapping):
            continue
        key = f"{item.get('dependency_family')}|{item.get('root_key')}"
        groups[key].append(dict(item))

    retained: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    group_output: list[dict[str, Any]] = []

    for key in sorted(groups):
        members = groups[key]
        members.sort(
            key=lambda x: (
                -(x.get("exactness") if x.get("exactness") is not None else -1.0),
                x.get("evidence_id", ""),
            )
        )
        winner = members[0]
        retained.append(winner)

        suppressed_ids = []
        for duplicate in members[1:]:
            duplicate["suppressed_by"] = winner["evidence_id"]
            duplicate["suppression_reason"] = "SAME_DEPENDENCY_FAMILY_AND_ROOT"
            suppressed.append(duplicate)
            suppressed_ids.append(duplicate["evidence_id"])

        group_output.append(
            {
                "dependency_key": key,
                "retained_evidence_id": winner["evidence_id"],
                "suppressed_evidence_ids": suppressed_ids,
            }
        )

    output = {
        "retained": retained,
        "suppressed": suppressed,
        "groups": group_output,
        "retained_count": len(retained),
        "suppressed_count": len(suppressed),
    }

    return ModuleResult(
        module_id="M16",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"deduplicated_evidence": output},
    )


def m17_independent_roots(context: ModuleContext) -> ModuleResult:
    """M17: agrupa evidencia deduplicada en raíces estructurales conservadoras."""

    dedup = context.canonical_snapshot.get("deduplicated_evidence")
    if not isinstance(dedup, Mapping):
        return not_evaluable_result("M17", "Falta la salida de M16.")

    retained = dedup.get("retained")
    if not isinstance(retained, list) or not retained:
        return not_evaluable_result("M17", "M16 no contiene evidencia retenida.")

    by_root: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in retained:
        if isinstance(item, Mapping):
            by_root[str(item.get("root_key"))].append(dict(item))

    roots: list[dict[str, Any]] = []
    for index, root_key in enumerate(sorted(by_root), start=1):
        members = by_root[root_key]
        dependency_families = sorted(
            {str(x.get("dependency_family")) for x in members}
        )
        core_ids = [
            str(x.get("evidence_id"))
            for x in members
            if bool(x.get("core_eligible")) and not bool(x.get("support_only"))
        ]
        support_ids = [
            str(x.get("evidence_id"))
            for x in members
            if bool(x.get("support_only")) or not bool(x.get("core_eligible"))
        ]
        exactness_values = [
            float(x["exactness"])
            for x in members
            if x.get("exactness") is not None
        ]

        roots.append(
            {
                "root_id": f"R{index:04d}",
                "root_key": root_key,
                "evidence_ids": [str(x.get("evidence_id")) for x in members],
                "dependency_families": dependency_families,
                "independent_family_count": len(dependency_families),
                "core_eligible": bool(core_ids),
                "core_evidence_ids": core_ids,
                "support_evidence_ids": support_ids,
                "max_exactness": max(exactness_values) if exactness_values else None,
                "strength": None,
                "strength_state": "NOT_CALCULATED",
            }
        )

    output = {
        "roots": roots,
        "root_count": len(roots),
        "strength_policy_applied": False,
    }

    return ModuleResult(
        module_id="M17",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"independent_roots": output},
        limitations=(
            "Las raíces no reciben fuerza final hasta existir una política explícita para S=F×fiabilidad×factor_horario×coeficiente.",
        ),
    )
