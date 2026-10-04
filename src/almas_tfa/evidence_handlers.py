from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .root_strengths import derive_root_strength, load_root_strength_policy
from .structural_policies import load_technique_dependency_registry


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


CONCRETE_POINT_ALIASES = {
    "NN": "NORTH_NODE",
    "SN": "SOUTH_NODE",
    "ANTIVERTEX": "ANTI_VERTEX",
}


def _concrete_point(point_id: Any) -> str:
    value = str(point_id or "").strip().upper()
    return CONCRETE_POINT_ALIASES.get(value, value)


def _concrete_contact(member: Mapping[str, Any], *, preserve_geometry: bool = False) -> dict[str, Any] | None:
    """Conserva el contacto original como contexto hermenéutico, no como nueva raíz."""

    contact = member.get("contact")
    if not isinstance(contact, Mapping):
        return None

    subject_a = str(contact.get("subject_a", "")).strip()
    subject_b = str(contact.get("subject_b", "")).strip()
    point_a = _concrete_point(contact.get("point_a"))
    point_b = _concrete_point(contact.get("point_b"))
    if not subject_a or not subject_b or not point_a or not point_b:
        return None

    relation_id = (
        str(
            contact.get("aspect")
            or contact.get("relation")
            or "UNSPECIFIED"
        )
        .strip()
        .upper()
        .replace(" ", "_")
        .replace("-", "_")
    )
    exactness = member.get("exactness")

    return {
        "evidence_id": str(member.get("evidence_id", "")),
        "source_module": str(member.get("source_module", "")),
        "dependency_family": str(member.get("dependency_family", "")),
        "directional": bool(member.get("directional")),
        "subject_a": subject_a,
        "point_a": point_a,
        "subject_b": subject_b,
        "point_b": point_b,
        "relation_id": relation_id,
        "layer_a": str(contact.get("layer_a") or "").strip(),
        "layer_b": str(contact.get("layer_b") or "").strip(),
        "exactness": float(exactness) if exactness is not None else None,
        **{key: contact[key] for key in (
            "longitude_a", "longitude_b", "declination_a", "declination_b", "transformed_longitude",
            "angle", "orb", "orb_limit", "separation", "distance",
            "applying", "separating", "phase", "node_variant",
            "calculation_method", "source_ref",
        ) if preserve_geometry and key in contact},
    }


def m15_evidence_extraction(context: ModuleContext) -> ModuleResult:
    """M15: normaliza contactos geométricos sin inventar pesos ni ontología."""

    evidence: list[dict[str, Any]] = []
    counters: dict[str, int] = defaultdict(int)
    registry = load_technique_dependency_registry()
    source_specs = registry["source_bindings"]

    for canonical_key, spec in source_specs.items():
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
        "technique_dependency_registry_id": registry["registry_id"],
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
        point_ids = sorted(
            {
                _normalized_point(str(contact.get(point_key, "")))
                for member in members
                if isinstance(member.get("contact"), Mapping)
                for contact in [member["contact"]]
                for point_key in ("point_a", "point_b")
                if str(contact.get(point_key, "")).strip()
            }
        )
        relation_ids = sorted(
            {
                str(
                    contact.get("aspect")
                    or contact.get("relation")
                    or "UNSPECIFIED"
                )
                .strip()
                .upper()
                .replace(" ", "_")
                .replace("-", "_")
                for member in members
                if isinstance(member.get("contact"), Mapping)
                for contact in [member["contact"]]
            }
        )
        concrete_contacts = [
            concrete
            for member in members
            for concrete in [_concrete_contact(member, preserve_geometry=context.raw_input.get("maximum_definition_context") is True)]
            if concrete is not None
        ]
        concrete_contacts.sort(
            key=lambda item: (
                item["dependency_family"],
                item["evidence_id"],
                item["subject_a"],
                item["point_a"],
                item["subject_b"],
                item["point_b"],
            )
        )

        strength_data = derive_root_strength(
            members,
            policy=load_root_strength_policy(),
        )

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
                "point_ids": point_ids,
                "relation_ids": relation_ids,
                "concrete_contacts": concrete_contacts,
                "max_exactness": max(exactness_values) if exactness_values else None,
                **strength_data,
            }
        )

    output = {
        "roots": roots,
        "root_count": len(roots),
        "strength_policy_applied": True,
        "strength_policy_id": "ALMAS_ROOT_STRENGTH_BASELINE_V1",
    }

    return ModuleResult(
        module_id="M17",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"independent_roots": output},
        limitations=(
            "M17 aplica una baseline neutral congelada: los coeficientes de técnica/aspecto no introducen jerarquías no calibradas.",
            "La sensibilidad a la hora natal se cuantifica en M23-M25 y no se penaliza de nuevo en la fuerza de raíz.",
            "Las capas support-only conservan fuerza diagnóstica pero nunca convierten una raíz en core-eligible.",
        ),
    )
