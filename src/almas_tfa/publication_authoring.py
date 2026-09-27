from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


AUTHORING_PRINCIPLE = "INTERPRETATION_PRIMARY_METHOD_SUPPORT"
SECTION_IDS = (
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


def validate_narrative_block(block: Mapping[str, Any]) -> None:
    role = block.get("role")
    canonical_paths = list(block.get("canonical_paths", []))
    source_ids = list(block.get("source_ids", []))
    text = block.get("text")

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Cada bloque editorial necesita texto no vacío.")

    if role == "ASTROLOGICAL_READING" and not canonical_paths:
        raise ValueError(
            "ASTROLOGICAL_READING requiere al menos una ruta canónica."
        )
    if role == "METAPHYSICAL_HERMENEUTICS":
        if not canonical_paths:
            raise ValueError(
                "METAPHYSICAL_HERMENEUTICS requiere soporte astrológico canónico."
            )
        if not source_ids:
            raise ValueError(
                "METAPHYSICAL_HERMENEUTICS requiere al menos una fuente."
            )
    if role == "DOCTRINAL_INTERPRETATION" and not source_ids:
        raise ValueError(
            "DOCTRINAL_INTERPRETATION requiere al menos una fuente."
        )
    if role == "TECHNICAL_SUPPORT" and not canonical_paths:
        raise ValueError(
            "TECHNICAL_SUPPORT requiere una ruta canónica verificable."
        )


def build_publication_manuscript(
    *,
    report_document_model: Mapping[str, Any],
    canonical_analysis: Mapping[str, Any],
    title: str,
    subtitle: str | None,
    narrative_sections: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    expected = report_document_model.get("canonical_fingerprint")
    actual = canonical_fingerprint(canonical_analysis)
    if expected != actual:
        raise ValueError(
            "El canonical no coincide con el fingerprint aprobado por M30/M31."
        )
    if report_document_model.get("canonical_fingerprint_verified") is not True:
        raise ValueError("M31 no verificó el fingerprint canónico.")

    model_sections = report_document_model.get("sections", [])
    if [s.get("section_id") for s in model_sections] != list(SECTION_IDS):
        raise ValueError("El modelo documental M31 no conserva las 11 secciones.")

    by_id = {section.get("section_id"): section for section in narrative_sections}
    if set(by_id) != set(SECTION_IDS):
        raise ValueError(
            "El manuscrito debe aportar exactamente las 11 secciones canónicas."
        )

    output_sections: list[dict[str, Any]] = []
    for model_section in model_sections:
        section_id = model_section["section_id"]
        supplied = by_id[section_id]
        blocks = [dict(block) for block in supplied.get("blocks", [])]
        for block in blocks:
            validate_narrative_block(block)

        if model_section.get("section_state") == "NOT_AVAILABLE":
            forbidden = [
                block for block in blocks
                if block.get("role") not in {"LIMITATION", "SOURCE_NOTE"}
            ]
            if forbidden:
                raise ValueError(
                    f"{section_id} está NOT_AVAILABLE y no admite interpretación."
                )

        output_sections.append(
            {
                "section_id": section_id,
                "title": supplied.get("title") or model_section.get("title"),
                "section_state": model_section.get("section_state"),
                "blocks": blocks,
            }
        )

    return {
        "schema_version": "1.0.0",
        "document_kind": "ALMAS_PUBLICATION_MANUSCRIPT",
        "language": "es",
        "title": title,
        "subtitle": subtitle,
        "canonical_fingerprint": actual,
        "authoring_principle": AUTHORING_PRINCIPLE,
        "sections": output_sections,
    }
