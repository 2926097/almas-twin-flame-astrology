from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleResult,
    not_evaluable_result,
)


EPISTEMIC_CLASSES = {
    "A_CALCULATED",
    "B_TECHNIQUE",
    "C_DOCTRINE",
    "D_CONTEMPORARY_USAGE",
    "E_PROJECT_HYPOTHESIS",
}

CLAIM_STATUSES = {
    "SUPPORTED",
    "COMPATIBLE",
    "INSUFFICIENT",
    "CONTRADICTED",
    "NOT_EVALUABLE",
}

DISCRIMINATOR_STATES = {
    "VALIDATED",
    "OPERATIONAL_FUNCTIONAL_ONLY",
    "OPERATIONAL_EPISTEMIC",
    "DOCTRINAL_ONLY",
    "NOT_VALIDATED",
    "NOT_APPLICABLE",
}

EXPECTED_SCOPES = {
    "A_CALCULATED": {"CALCULATED_FACT"},
    "B_TECHNIQUE": {"TECHNIQUE_DESCRIPTION"},
    "C_DOCTRINE": {"DOCTRINAL_ATTRIBUTION"},
    "D_CONTEMPORARY_USAGE": {"CONTEMPORARY_USAGE"},
    "E_PROJECT_HYPOTHESIS": {
        "PROJECT_OPERATIONALIZATION",
        "PROJECT_SYNTHESIS",
    },
}

SOURCE_RELATIONS = {
    "DIRECT_DOCTRINE",
    "ACADEMIC_DESCRIPTION",
    "HISTORICAL_ANTECEDENT",
    "COMPARATIVE_ANALOGUE",
    "CONTEMPORARY_USAGE",
    "PROJECT_OPERATIONALIZATION",
    "PROJECT_SYNTHESIS",
}

NON_IDENTITY_RELATIONS = {
    "ACADEMIC_DESCRIPTION",
    "HISTORICAL_ANTECEDENT",
    "COMPARATIVE_ANALOGUE",
    "CONTEMPORARY_USAGE",
    "PROJECT_OPERATIONALIZATION",
    "PROJECT_SYNTHESIS",
}

NON_IDENTITY_GENEALOGY_RELATIONS = {
    "COMPARATIVE_ANALOGUE",
    "COMPARATIVE_ANTECEDENT_ONLY",
    "COMPARATIVE_MOTIF_ONLY",
    "DOCTRINAL_NEIGHBOR_NOT_IDENTITY",
    "MODERN_REINTERPRETATION_NOT_IDENTITY",
    "NON_EQUIVALENT",
    "NO_DIRECT_DOCTRINAL_IDENTITY",
    "TERMINOLOGICAL_ANTECEDENT_NOT_DOCTRINAL_IDENTITY",
    "PHENOMENOLOGY_NOT_ONTOLOGY",
    "SELF_LABEL_NOT_DOCTRINAL_VERIFICATION",
    "INSUFFICIENT_FOR_DYADIC_ORIGIN",
    "INSUFFICIENT_FOR_BILATERAL_CONTRACT",
    "PAIRING_NOT_CONTRACT",
    "FUNCTION_NOT_CONTRACT_PROOF",
    "FRAMEWORK_NOT_METHOD",
    "NON_EXCLUSIVE_NETWORK_VS_DYAD",
}

ACADEMIC_ROLES = {
    "ACADEMIC_ANALYSIS",
    "ACADEMIC_CONTEXT",
    "LITERARY_CRITICISM",
}

CONTEMPORARY_USAGE_ROLES = {
    "EMIC_USAGE",
    "IDENTIFIED_METHOD",
    "ACADEMIC_ANALYSIS",
    "ACADEMIC_CONTEXT",
    "HISTORICAL_RECEPTION",
}


def _parse_registry(
    registry: Any,
) -> tuple[dict[str, dict[str, Any]], str]:
    if isinstance(registry, Mapping):
        entries = registry.get("entries")
        if not isinstance(entries, list):
            raise ValueError("source_registry.entries debe ser una lista.")

        output: dict[str, dict[str, Any]] = {}
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise ValueError("Cada entrada de source_registry debe ser un objeto.")
            source_id = entry.get("id")
            if not isinstance(source_id, str) or not source_id:
                raise ValueError("Cada fuente debe declarar id.")
            if source_id in output:
                raise ValueError(f"Fuente duplicada en source_registry: {source_id}")
            output[source_id] = dict(entry)
        return output, "FULL_METADATA"

    if isinstance(registry, list):
        ids: dict[str, dict[str, Any]] = {}
        for value in registry:
            if not isinstance(value, str) or not value:
                raise ValueError("source_registry legacy debe contener IDs válidos.")
            if value in ids:
                raise ValueError(f"Fuente duplicada en source_registry: {value}")
            ids[value] = {"id": value}
        return ids, "IDS_ONLY"

    return {}, "ABSENT"


def _source_id_for_anchor(
    anchor_ref: str,
    registry: Mapping[str, Mapping[str, Any]],
) -> str | None:
    if anchor_ref in registry:
        return anchor_ref

    for separator in (":", "#"):
        prefix = anchor_ref.split(separator, 1)[0]
        if prefix in registry:
            return prefix
    return None


def _support_refs(
    raw: Any,
    registry: Mapping[str, Mapping[str, Any]],
    claim_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if raw is None:
        return [], []
    if not isinstance(raw, list):
        raise ValueError(f"{claim_id}: source_support_refs debe ser una lista.")

    normalized: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()

    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            raise ValueError(
                f"{claim_id}: source_support_refs[{index}] debe ser un objeto."
            )
        source_id = item.get("source_id")
        support_index = item.get("support_index")

        if not isinstance(source_id, str) or not source_id:
            raise ValueError(
                f"{claim_id}: source_support_refs[{index}].source_id es obligatorio."
            )
        if (
            isinstance(support_index, bool)
            or not isinstance(support_index, int)
            or support_index < 0
        ):
            raise ValueError(
                f"{claim_id}: source_support_refs[{index}].support_index debe ser entero >= 0."
            )
        key = (source_id, support_index)
        if key in seen:
            raise ValueError(
                f"{claim_id}: source_support_ref duplicado {source_id}#{support_index}."
            )
        seen.add(key)

        entry = registry.get(source_id)
        resolved = False
        if isinstance(entry, Mapping):
            supports = entry.get("supports")
            if isinstance(supports, list) and support_index < len(supports):
                resolved = True

        normalized.append(
            {
                "source_id": source_id,
                "support_index": support_index,
                "resolved": resolved,
            }
        )
        if not resolved:
            issues.append(
                {
                    "claim_id": claim_id,
                    "source_id": source_id,
                    "support_index": support_index,
                    "issue": "SUPPORT_REF_NOT_RESOLVED",
                }
            )

    return normalized, issues


def _source_audit(
    source_ids: list[str],
    source_anchor_refs: list[str],
    support_refs: list[dict[str, Any]],
    registry: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]]]:
    unresolved_sources: list[dict[str, str]] = []
    unresolved_anchors: list[dict[str, str]] = []
    audit: list[dict[str, Any]] = []

    support_indices: dict[str, list[int]] = {}
    for item in support_refs:
        if item.get("resolved"):
            support_indices.setdefault(str(item["source_id"]), []).append(
                int(item["support_index"])
            )

    anchor_sources = {
        anchor_ref: _source_id_for_anchor(anchor_ref, registry)
        for anchor_ref in source_anchor_refs
    }

    declared_source_ids = set(source_ids)
    for anchor_ref, source_id in anchor_sources.items():
        if source_id is None:
            unresolved_anchors.append(
                {"anchor_ref": anchor_ref, "issue": "ANCHOR_SOURCE_NOT_RESOLVED"}
            )
        elif source_id not in declared_source_ids:
            unresolved_anchors.append(
                {
                    "anchor_ref": anchor_ref,
                    "issue": "ANCHOR_SOURCE_NOT_DECLARED_IN_CLAIM",
                }
            )

    for source_id in source_ids:
        entry = registry.get(source_id)
        if not isinstance(entry, Mapping):
            unresolved_sources.append(
                {"source_id": source_id, "issue": "SOURCE_NOT_RESOLVED"}
            )
            continue

        related_anchor_refs = sorted(
            anchor_ref
            for anchor_ref, anchor_source_id in anchor_sources.items()
            if anchor_source_id == source_id
        )

        audit.append(
            {
                "source_id": source_id,
                "priority": entry.get("priority"),
                "source_role": entry.get("source_role"),
                "tradition": entry.get("tradition"),
                "verification_status": entry.get("verification_status"),
                "verification_anchor_present": bool(entry.get("verification_anchor")),
                "verification_anchor_type": entry.get("verification_anchor_type"),
                "evidence_scope": entry.get("evidence_scope"),
                "anchor_refs": related_anchor_refs,
                "support_indices": sorted(support_indices.get(source_id, [])),
                "does_not_support_count": (
                    len(entry.get("does_not_support"))
                    if isinstance(entry.get("does_not_support"), list)
                    else 0
                ),
            }
        )

    return audit, unresolved_sources, unresolved_anchors


def _direct_doctrine_gate(
    claim_id: str,
    source_audit: list[dict[str, Any]],
    support_refs: list[dict[str, Any]],
    does_not_support_checked: bool,
    registry_mode: str,
) -> dict[str, Any]:
    if registry_mode != "FULL_METADATA":
        raise ValueError(
            f"{claim_id}: DIRECT_DOCTRINE exige source_registry con metadatos completos."
        )

    candidates = [
        source
        for source in source_audit
        if source.get("priority") == "P1_PRIMARY"
        and source.get("source_role") == "DOCTRINAL_PRIMARY"
        and source.get("verification_status") == "VERIFIED_PRIMARY"
        and source.get("verification_anchor_present") is True
        and bool(source.get("anchor_refs"))
        and source.get("evidence_scope") == "DOCTRINAL_CLAIM"
    ]
    if not candidates:
        raise ValueError(
            f"{claim_id}: DIRECT_DOCTRINE exige al menos una fuente P1 doctrinal primaria verificada."
        )

    candidate_ids = {source["source_id"] for source in candidates}
    supported_ids = {
        str(item["source_id"])
        for item in support_refs
        if item.get("resolved")
    }
    if not candidate_ids & supported_ids:
        raise ValueError(
            f"{claim_id}: DIRECT_DOCTRINE exige source_support_refs hacia una fuente P1 válida."
        )

    if does_not_support_checked is not True:
        raise ValueError(
            f"{claim_id}: DIRECT_DOCTRINE exige does_not_support_checked=true."
        )

    return {
        "passed": True,
        "qualifying_source_ids": sorted(candidate_ids),
        "support_refs_resolved": True,
        "does_not_support_checked": True,
    }


def _academic_description_gate(
    claim_id: str,
    source_audit: list[dict[str, Any]],
    registry_mode: str,
) -> dict[str, Any]:
    if registry_mode != "FULL_METADATA":
        raise ValueError(
            f"{claim_id}: ACADEMIC_DESCRIPTION exige source_registry con metadatos completos."
        )

    qualifying = [
        source["source_id"]
        for source in source_audit
        if source.get("priority") == "P2_ACADEMIC"
        and source.get("source_role") in ACADEMIC_ROLES
        and source.get("verification_anchor_present") is True
        and bool(source.get("anchor_refs"))
        and source.get("evidence_scope") in {
            "ACADEMIC_DESCRIPTION",
            "HISTORICAL_CONTEXT",
            "PHENOMENOLOGY",
        }
    ]
    if not qualifying:
        raise ValueError(
            f"{claim_id}: ACADEMIC_DESCRIPTION exige al menos una fuente P2 académica anclada."
        )
    return {"passed": True, "qualifying_source_ids": sorted(qualifying)}


def _contemporary_usage_gate(
    claim_id: str,
    source_audit: list[dict[str, Any]],
    registry_mode: str,
) -> dict[str, Any]:
    if registry_mode != "FULL_METADATA":
        raise ValueError(
            f"{claim_id}: CONTEMPORARY_USAGE exige source_registry con metadatos completos."
        )

    qualifying = [
        source["source_id"]
        for source in source_audit
        if source.get("source_role") in CONTEMPORARY_USAGE_ROLES
        or source.get("priority") == "P5_EMIC"
    ]
    if not qualifying:
        raise ValueError(
            f"{claim_id}: CONTEMPORARY_USAGE carece de fuente académica, emic o método identificado."
        )
    return {"passed": True, "qualifying_source_ids": sorted(qualifying)}


def _genealogy_audit(
    concept_id: Any,
    identity_target_concept_id: Any,
    genealogy: Any,
) -> tuple[bool, list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(genealogy, Mapping):
        return False, [], []

    edges = genealogy.get("edges")
    if not isinstance(edges, list):
        raise ValueError("doctrinal_genealogy.edges debe ser una lista.")

    relevant: list[dict[str, Any]] = []
    pair_non_identity: list[dict[str, Any]] = []
    if not isinstance(concept_id, str) or not concept_id:
        return True, relevant, pair_non_identity

    target = (
        identity_target_concept_id
        if isinstance(identity_target_concept_id, str)
        and identity_target_concept_id
        else None
    )

    for edge in edges:
        if not isinstance(edge, Mapping):
            raise ValueError("Cada edge doctrinal debe ser un objeto.")
        edge_from = edge.get("from")
        edge_to = edge.get("to")
        if edge_from == concept_id or edge_to == concept_id:
            copied = dict(edge)
            relevant.append(copied)

            if target is not None:
                same_pair = {
                    str(edge_from),
                    str(edge_to),
                } == {concept_id, target}
                if (
                    same_pair
                    and edge.get("relation") in NON_IDENTITY_GENEALOGY_RELATIONS
                ):
                    pair_non_identity.append(copied)

    return True, relevant, pair_non_identity


def m28_doctrine_hermeneutics(context: ModuleContext) -> ModuleResult:
    """M28: gate doctrinal, comparativo y hermenéutico con trazabilidad."""

    claims = context.raw_input.get("doctrinal_claims")
    if not isinstance(claims, list) or not claims:
        return not_evaluable_result(
            "M28",
            "Faltan doctrinal_claims estructuradas.",
        )

    registry, registry_mode = _parse_registry(
        context.raw_input.get("source_registry")
    )
    genealogy = context.raw_input.get("doctrinal_genealogy")

    normalized: list[dict[str, Any]] = []
    unresolved_sources: list[dict[str, Any]] = []
    unresolved_anchors: list[dict[str, Any]] = []
    support_ref_issues: list[dict[str, Any]] = []
    epistemic_counts: Counter[str] = Counter()
    relation_counts: Counter[str] = Counter()
    priority_counts: Counter[str] = Counter()
    tradition_counts: Counter[str] = Counter()
    seen_claim_ids: set[str] = set()

    for index, raw in enumerate(claims, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError("Cada doctrinal_claim debe ser un objeto.")

        if raw.get("schema_version") != "2.0.0":
            raise ValueError(
                f"Claim {index}: schema_version debe ser 2.0.0."
            )

        claim_id = raw.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError(f"Claim {index}: claim_id es obligatorio.")
        if claim_id in seen_claim_ids:
            raise ValueError(f"claim_id duplicado: {claim_id}")
        seen_claim_ids.add(claim_id)

        statement = raw.get("statement")
        epistemic_class = raw.get("epistemic_class")
        claim_scope = raw.get("claim_scope")
        source_relation = raw.get("source_relation")
        status = raw.get("status")
        discriminator_state = raw.get("discriminator_state")

        if not isinstance(statement, str) or not statement.strip():
            raise ValueError(f"{claim_id}: statement es obligatorio.")
        if epistemic_class not in EPISTEMIC_CLASSES:
            raise ValueError(f"{claim_id}: epistemic_class inválida.")
        if claim_scope not in EXPECTED_SCOPES[epistemic_class]:
            raise ValueError(
                f"{claim_id}: claim_scope {claim_scope} no corresponde a {epistemic_class}."
            )
        if source_relation not in SOURCE_RELATIONS:
            raise ValueError(f"{claim_id}: source_relation inválida.")
        if status not in CLAIM_STATUSES:
            raise ValueError(f"{claim_id}: status inválido.")
        if discriminator_state not in DISCRIMINATOR_STATES:
            raise ValueError(f"{claim_id}: discriminator_state inválido.")

        source_ids = raw.get("source_ids")
        anchor_refs = raw.get("source_anchor_refs")
        astrological_refs = raw.get("astrological_refs", [])
        alternatives = raw.get("alternatives")
        limitations = raw.get("limitations")
        allowed_conclusion = raw.get("allowed_conclusion")
        inferential_ceiling = raw.get("inferential_ceiling")

        if not isinstance(source_ids, list) or any(
            not isinstance(x, str) or not x for x in source_ids
        ):
            raise ValueError(f"{claim_id}: source_ids debe ser una lista de IDs.")
        if len(set(source_ids)) != len(source_ids):
            raise ValueError(f"{claim_id}: source_ids contiene duplicados.")

        if not isinstance(anchor_refs, list) or any(
            not isinstance(x, str) or not x for x in anchor_refs
        ):
            raise ValueError(
                f"{claim_id}: source_anchor_refs debe ser una lista de referencias."
            )
        if len(set(anchor_refs)) != len(anchor_refs):
            raise ValueError(
                f"{claim_id}: source_anchor_refs contiene duplicados."
            )

        if not isinstance(astrological_refs, list) or any(
            not isinstance(x, str) or not x for x in astrological_refs
        ):
            raise ValueError(
                f"{claim_id}: astrological_refs debe ser una lista de IDs."
            )
        if not isinstance(alternatives, list):
            raise ValueError(f"{claim_id}: alternatives debe ser una lista.")
        if not isinstance(limitations, list):
            raise ValueError(f"{claim_id}: limitations debe ser una lista.")
        if not isinstance(allowed_conclusion, str) or not allowed_conclusion:
            raise ValueError(f"{claim_id}: allowed_conclusion es obligatorio.")
        if not isinstance(inferential_ceiling, str) or not inferential_ceiling:
            raise ValueError(f"{claim_id}: inferential_ceiling es obligatorio.")
        if raw.get("ceiling_enforced") is not True:
            raise ValueError(f"{claim_id}: ceiling_enforced debe ser true.")

        if source_relation == "DIRECT_DOCTRINE" and epistemic_class != "C_DOCTRINE":
            raise ValueError(
                f"{claim_id}: DIRECT_DOCTRINE sólo puede usarse con C_DOCTRINE."
            )
        if source_relation == "PROJECT_SYNTHESIS" and epistemic_class != "E_PROJECT_HYPOTHESIS":
            raise ValueError(
                f"{claim_id}: PROJECT_SYNTHESIS exige E_PROJECT_HYPOTHESIS."
            )
        if source_relation == "PROJECT_OPERATIONALIZATION" and epistemic_class not in {
            "B_TECHNIQUE",
            "E_PROJECT_HYPOTHESIS",
        }:
            raise ValueError(
                f"{claim_id}: PROJECT_OPERATIONALIZATION sólo admite B_TECHNIQUE o E_PROJECT_HYPOTHESIS."
            )
        if epistemic_class == "D_CONTEMPORARY_USAGE" and source_relation not in {
            "CONTEMPORARY_USAGE",
            "ACADEMIC_DESCRIPTION",
        }:
            raise ValueError(
                f"{claim_id}: D_CONTEMPORARY_USAGE requiere CONTEMPORARY_USAGE o ACADEMIC_DESCRIPTION."
            )
        if epistemic_class == "E_PROJECT_HYPOTHESIS" and source_relation == "DIRECT_DOCTRINE":
            raise ValueError(
                f"{claim_id}: E_PROJECT_HYPOTHESIS no puede presentarse como DIRECT_DOCTRINE."
            )

        support_refs, support_issues = _support_refs(
            raw.get("source_support_refs"),
            registry,
            claim_id,
        )
        if any(
            str(item.get("source_id")) not in set(source_ids)
            for item in support_refs
        ):
            raise ValueError(
                f"{claim_id}: source_support_refs sólo puede referir fuentes declaradas en source_ids."
            )
        support_ref_issues.extend(support_issues)

        source_audit, claim_unresolved_sources, claim_unresolved_anchors = _source_audit(
            list(source_ids),
            list(anchor_refs),
            support_refs,
            registry,
        )
        unresolved_sources.extend(
            {"claim_id": claim_id, **item}
            for item in claim_unresolved_sources
        )
        unresolved_anchors.extend(
            {"claim_id": claim_id, **item}
            for item in claim_unresolved_anchors
        )

        if (
            status == "SUPPORTED"
            and source_relation in {
                "DIRECT_DOCTRINE",
                "ACADEMIC_DESCRIPTION",
                "CONTEMPORARY_USAGE",
            }
            and (
                claim_unresolved_sources
                or claim_unresolved_anchors
                or support_issues
            )
        ):
            raise ValueError(
                f"{claim_id}: una atribución SUPPORTED no puede contener "
                "fuentes, anclas o soportes sin resolver."
            )

        if source_ids and registry_mode == "ABSENT":
            raise ValueError(
                f"{claim_id}: existen source_ids pero no source_registry."
            )

        doctrine_gate: dict[str, Any] | None = None
        academic_gate: dict[str, Any] | None = None
        contemporary_gate: dict[str, Any] | None = None

        if source_relation == "DIRECT_DOCTRINE":
            if not source_ids or not anchor_refs:
                raise ValueError(
                    f"{claim_id}: DIRECT_DOCTRINE exige source_ids y source_anchor_refs."
                )
            doctrine_gate = _direct_doctrine_gate(
                claim_id,
                source_audit,
                support_refs,
                raw.get("does_not_support_checked") is True,
                registry_mode,
            )

        if source_relation == "ACADEMIC_DESCRIPTION":
            academic_gate = _academic_description_gate(
                claim_id,
                source_audit,
                registry_mode,
            )

        if source_relation == "CONTEMPORARY_USAGE":
            contemporary_gate = _contemporary_usage_gate(
                claim_id,
                source_audit,
                registry_mode,
            )

        if epistemic_class == "B_TECHNIQUE" and not astrological_refs:
            raise ValueError(
                f"{claim_id}: B_TECHNIQUE exige astrological_refs."
            )

        if epistemic_class == "D_CONTEMPORARY_USAGE" and not source_ids:
            raise ValueError(
                f"{claim_id}: D_CONTEMPORARY_USAGE exige fuentes."
            )

        if epistemic_class == "E_PROJECT_HYPOTHESIS":
            if source_relation not in {
                "PROJECT_OPERATIONALIZATION",
                "PROJECT_SYNTHESIS",
                "HISTORICAL_ANTECEDENT",
                "COMPARATIVE_ANALOGUE",
            }:
                raise ValueError(
                    f"{claim_id}: E_PROJECT_HYPOTHESIS usa una relación de fuente incompatible."
                )
            if raw.get("requested_conclusion") not in {None, ""} and not alternatives:
                raise ValueError(
                    f"{claim_id}: una hipótesis de proyecto con conclusión solicitada debe registrar alternativas."
                )

        requested = raw.get("requested_conclusion")
        if (
            discriminator_state == "NOT_VALIDATED"
            and status == "SUPPORTED"
            and requested not in {None, ""}
            and requested != allowed_conclusion
        ):
            raise ValueError(
                f"{claim_id}: un discriminador NOT_VALIDATED no puede elevar la conclusión por encima de allowed_conclusion."
            )

        concept_id = raw.get("concept_id")
        identity_target_concept_id = raw.get("identity_target_concept_id")
        asserts_identity = raw.get("asserts_doctrinal_identity") is True
        if asserts_identity:
            if not isinstance(concept_id, str) or not concept_id:
                raise ValueError(
                    f"{claim_id}: una identidad doctrinal exige concept_id."
                )
            if (
                not isinstance(identity_target_concept_id, str)
                or not identity_target_concept_id
            ):
                raise ValueError(
                    f"{claim_id}: una identidad doctrinal exige identity_target_concept_id."
                )
            if identity_target_concept_id == concept_id:
                raise ValueError(
                    f"{claim_id}: identity_target_concept_id debe ser distinto de concept_id."
                )

        genealogy_checked, genealogy_edges, non_identity_edges = _genealogy_audit(
            concept_id,
            identity_target_concept_id,
            genealogy,
        )

        traditions = sorted(
            {
                str(source["tradition"])
                for source in source_audit
                if source.get("tradition") not in {None, ""}
            }
        )
        relation_forbids_identity = source_relation in NON_IDENTITY_RELATIONS

        if asserts_identity and relation_forbids_identity:
            raise ValueError(
                f"{claim_id}: {source_relation} no autoriza identidad doctrinal."
            )
        if asserts_identity and len(traditions) > 1:
            raise ValueError(
                f"{claim_id}: M28 no permite inferir identidad doctrinal entre tradiciones distintas."
            )
        if asserts_identity and non_identity_edges:
            raise ValueError(
                f"{claim_id}: la genealogía contiene relaciones explícitas de no identidad."
            )

        for source in source_audit:
            if source.get("priority"):
                priority_counts[str(source["priority"])] += 1
            if source.get("tradition"):
                tradition_counts[str(source["tradition"])] += 1

        epistemic_counts[str(epistemic_class)] += 1
        relation_counts[str(source_relation)] += 1

        item = dict(raw)
        item["source_ids"] = list(source_ids)
        item["source_anchor_refs"] = list(anchor_refs)
        item["astrological_refs"] = list(astrological_refs)
        item["alternatives"] = list(alternatives)
        item["limitations"] = list(limitations)
        item["source_support_refs"] = support_refs
        item["source_audit"] = source_audit
        item["traditions"] = traditions
        item["doctrine_gate"] = doctrine_gate
        item["academic_description_gate"] = academic_gate
        item["contemporary_usage_gate"] = contemporary_gate
        item["genealogy_checked"] = genealogy_checked
        item["genealogy_edges"] = genealogy_edges
        item["identity_target_concept_id"] = identity_target_concept_id
        item["non_identity_genealogy_edges"] = non_identity_edges
        item["comparative_only"] = source_relation in {
            "HISTORICAL_ANTECEDENT",
            "COMPARATIVE_ANALOGUE",
        }
        item["doctrinal_identity_allowed"] = (
            asserts_identity
            and source_relation == "DIRECT_DOCTRINE"
            and len(traditions) <= 1
            and not non_identity_edges
        )
        item["project_construction"] = (
            epistemic_class == "E_PROJECT_HYPOTHESIS"
        )
        item["contemporary_usage_promoted_to_ontology"] = False
        item["project_hypothesis_promoted_to_doctrine"] = False
        item["cross_tradition_identity_inferred"] = False
        item["doctrine_adds_structural_score"] = False
        normalized.append(item)

    output = {
        "claims": normalized,
        "claim_count": len(normalized),
        "source_registry_mode": registry_mode,
        "source_registry_checked": registry_mode != "ABSENT",
        "genealogy_checked": isinstance(genealogy, Mapping),
        "unresolved_sources": unresolved_sources,
        "unresolved_anchors": unresolved_anchors,
        "support_ref_issues": support_ref_issues,
        "epistemic_class_counts": dict(sorted(epistemic_counts.items())),
        "source_relation_counts": dict(sorted(relation_counts.items())),
        "source_priority_counts": dict(sorted(priority_counts.items())),
        "tradition_counts": dict(sorted(tradition_counts.items())),
        "doctrine_adds_structural_score": False,
        "source_count_used_as_structural_weight": False,
        "epistemic_separation_enforced": True,
        "non_equivalence_enforced": True,
        "contemporary_usage_promoted_to_ontology": False,
        "project_hypothesis_promoted_to_doctrine": False,
        "cross_tradition_identity_inferred": False,
    }

    limitations = [
        "M28 valida atribución, procedencia y techo inferencial; no añade puntos estructurales.",
        "source_support_refs demuestra trazabilidad hacia el alcance registrado de la fuente, pero no sustituye revisión filológica o histórica del pasaje.",
    ]
    if not isinstance(genealogy, Mapping):
        limitations.append(
            "No se suministró doctrinal_genealogy a la ejecución; se aplica el firewall por source_relation, pero no se auditan edges del grafo doctrinal."
        )

    return ModuleResult(
        module_id="M28",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"doctrine_hermeneutics": output},
        limitations=tuple(limitations),
    )
