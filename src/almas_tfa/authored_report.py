from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


SECTION_ORDER = (
    "S01_SYNTHESIS",
    "S02_DATA_METHOD",
    "S03_NUMERIC_ONTOLOGY",
    "S04_STRUCTURE",
    "S05_RELATIONAL",
    "S06_DIFFERENTIAL",
    "S07_TEMPORAL",
    "S08_ROBUSTNESS",
    "S09_DOCTRINE",
    "S10_FINAL_SYNTHESIS",
    "S11_SOURCES_APPENDICES",
)


def canonical_fingerprint(canonical: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _claim_ids(canonical: Mapping[str, Any]) -> set[str]:
    claims = canonical.get("doctrine")
    if not isinstance(claims, list):
        return set()
    return {
        str(item["claim_id"])
        for item in claims
        if isinstance(item, Mapping)
        and isinstance(item.get("claim_id"), str)
        and item.get("claim_id")
    }


def _evidence_ids(canonical: Mapping[str, Any]) -> set[str]:
    evidence = canonical.get("evidence")
    if not isinstance(evidence, list):
        return set()
    return {
        str(item["evidence_id"])
        for item in evidence
        if isinstance(item, Mapping)
        and isinstance(item.get("evidence_id"), str)
        and item.get("evidence_id")
    }


def validate_authored_report_trace(
    authored_report: Mapping[str, Any],
    report_document_model: Mapping[str, Any],
    canonical_analysis: Mapping[str, Any],
) -> None:
    """Valida trazabilidad editorial sin valorar ni reescribir la interpretación."""

    expected_fingerprint = canonical_fingerprint(canonical_analysis)
    model_fingerprint = report_document_model.get("canonical_fingerprint")
    authored_fingerprint = authored_report.get("canonical_fingerprint")

    if report_document_model.get("canonical_fingerprint_verified") is not True:
        raise ValueError("M31 no verificó el fingerprint canónico.")
    if model_fingerprint != expected_fingerprint:
        raise ValueError("El report_document_model no corresponde al canonical_analysis.")
    if authored_fingerprint != expected_fingerprint:
        raise ValueError("El authored_report no corresponde al canonical_analysis.")
    if authored_report.get("report_state") != report_document_model.get("report_state"):
        raise ValueError("El authored_report debe conservar report_state de M31.")

    model_sections = report_document_model.get("sections")
    authored_sections = authored_report.get("sections")
    if not isinstance(model_sections, Sequence) or isinstance(model_sections, (str, bytes)):
        raise ValueError("report_document_model.sections inválido.")
    if not isinstance(authored_sections, Sequence) or isinstance(authored_sections, (str, bytes)):
        raise ValueError("authored_report.sections inválido.")

    model_by_id = {
        section.get("section_id"): section
        for section in model_sections
        if isinstance(section, Mapping)
    }
    authored_ids = [
        section.get("section_id")
        for section in authored_sections
        if isinstance(section, Mapping)
    ]
    if tuple(authored_ids) != SECTION_ORDER:
        raise ValueError("Las secciones authored_report deben conservar el orden M31 exacto.")

    claim_ids = _claim_ids(canonical_analysis)
    evidence_ids = _evidence_ids(canonical_analysis)

    bibliography = authored_report.get("bibliography")
    if not isinstance(bibliography, list):
        raise ValueError("authored_report.bibliography debe ser una lista.")
    bibliography_ids: set[str] = set()
    for entry in bibliography:
        if not isinstance(entry, Mapping):
            raise ValueError("Cada entrada bibliográfica debe ser un objeto.")
        source_id = entry.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("Cada entrada bibliográfica debe declarar source_id.")
        if source_id in bibliography_ids:
            raise ValueError(f"Fuente bibliográfica duplicada: {source_id}")
        bibliography_ids.add(source_id)

    for section in authored_sections:
        if not isinstance(section, Mapping):
            raise ValueError("Cada sección redactada debe ser un objeto.")
        section_id = section.get("section_id")
        model_section = model_by_id.get(section_id)
        if not isinstance(model_section, Mapping):
            raise ValueError(f"Sección no declarada por M31: {section_id}")

        state = section.get("authoring_state")
        if model_section.get("section_state") == "NOT_AVAILABLE":
            if state != "OMITTED_NOT_AVAILABLE":
                raise ValueError(
                    f"{section_id}: M31 la declaró NOT_AVAILABLE y no puede redactarse."
                )
            continue
        if state != "AUTHORED":
            raise ValueError(
                f"{section_id}: una sección disponible debe quedar AUTHORED."
            )

        used_paths = section.get("canonical_paths_used", [])
        allowed_paths = set(model_section.get("available_paths", []))
        unknown_paths = sorted(set(used_paths) - allowed_paths)
        if unknown_paths:
            raise ValueError(
                f"{section_id}: rutas canónicas no autorizadas por M31: "
                + ", ".join(unknown_paths)
            )

        used_classes = set(section.get("epistemic_classes_used", []))
        allowed_classes = set(model_section.get("epistemic_classes_allowed", []))
        if not used_classes.issubset(allowed_classes):
            raise ValueError(
                f"{section_id}: clases epistemológicas fuera del contrato M31."
            )

        unknown_claims = sorted(
            set(section.get("doctrinal_claim_refs", [])) - claim_ids
        )
        if unknown_claims:
            raise ValueError(
                f"{section_id}: doctrinal_claim_refs desconocidos: "
                + ", ".join(unknown_claims)
            )

        unknown_evidence = sorted(
            set(section.get("evidence_refs", [])) - evidence_ids
        )
        if unknown_evidence:
            raise ValueError(
                f"{section_id}: evidence_refs desconocidos: "
                + ", ".join(unknown_evidence)
            )

        unknown_sources = sorted(
            set(section.get("source_refs", [])) - bibliography_ids
        )
        if unknown_sources:
            raise ValueError(
                f"{section_id}: source_refs sin entrada bibliográfica: "
                + ", ".join(unknown_sources)
            )

    if authored_report.get("canonical_values_mutated") is not False:
        raise ValueError("La autoría no puede mutar valores canónicos.")
    if authored_report.get("new_calculations_performed") is not False:
        raise ValueError("La autoría no puede ejecutar nuevos cálculos.")
    if authored_report.get("new_scores_created") is not False:
        raise ValueError("La autoría no puede crear nuevos scores.")
