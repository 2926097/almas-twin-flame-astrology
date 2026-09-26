from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping


PERSONAL_REPORT_MODES = {
    "EXECUTIVE_PERSONAL_REPORT",
    "STANDARD_PERSONAL_REPORT",
    "FULL_CRITICAL_REPORT",
    "TECHNICAL_ATLAS",
    "ESOTERIC_KABBALISTIC_REPORT",
}

PERSONAL_SECTION_SPECS = (
    ("P01_THESIS", "Tesis de lectura", ("natal",), {"EXECUTIVE_PERSONAL_REPORT", "STANDARD_PERSONAL_REPORT", "FULL_CRITICAL_REPORT", "ESOTERIC_KABBALISTIC_REPORT"}),
    ("P02_DATA_METHOD", "Calidad de datos y método", ("data_quality",), PERSONAL_REPORT_MODES),
    ("P03_NATAL_ARCHITECTURE", "Arquitectura natal", ("natal",), PERSONAL_REPORT_MODES),
    ("P04_TRADITIONAL_STRUCTURE", "Secta, regencias, dispositores y estructura", ("natal",), {"STANDARD_PERSONAL_REPORT", "FULL_CRITICAL_REPORT", "TECHNICAL_ATLAS"}),
    ("P05_PSYCHOLOGICAL_EVOLUTION", "Dinámica psicológica y evolutiva", ("interpretive_layers",), {"STANDARD_PERSONAL_REPORT", "FULL_CRITICAL_REPORT", "ESOTERIC_KABBALISTIC_REPORT"}),
    ("P06_RELATIONSHIP_FIELD", "Campo vincular", ("interpretive_layers",), {"STANDARD_PERSONAL_REPORT", "FULL_CRITICAL_REPORT"}),
    ("P07_VOCATION_VALUE", "Vocación, valor y dirección", ("interpretive_layers",), {"STANDARD_PERSONAL_REPORT", "FULL_CRITICAL_REPORT"}),
    ("P08_ESOTERIC_DOCTRINE", "Capas esotéricas y doctrina comparada", ("doctrine",), {"FULL_CRITICAL_REPORT", "ESOTERIC_KABBALISTIC_REPORT"}),
    ("P09_TEMPORAL", "Ciclos y activación temporal", ("temporal",), {"STANDARD_PERSONAL_REPORT", "FULL_CRITICAL_REPORT", "TECHNICAL_ATLAS"}),
    ("P10_COUNTEREVIDENCE", "Contraevidencia, dependencia y límites", ("counterevidence",), {"FULL_CRITICAL_REPORT", "TECHNICAL_ATLAS"}),
    ("P11_SYNTHESIS", "Síntesis longitudinal", ("natal",), {"EXECUTIVE_PERSONAL_REPORT", "STANDARD_PERSONAL_REPORT", "FULL_CRITICAL_REPORT", "ESOTERIC_KABBALISTIC_REPORT"}),
    ("P12_ATLAS_SOURCES", "Atlas técnico, fuentes y anexos", ("technical_atlas",), {"FULL_CRITICAL_REPORT", "TECHNICAL_ATLAS"}),
)


def personal_fingerprint(canonical: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def make_personal_canonical(
    *,
    subject: Mapping[str, Any],
    data_quality: Mapping[str, Any],
    natal: Mapping[str, Any],
    interpretive_layers: Mapping[str, Any] | None = None,
    temporal: Mapping[str, Any] | None = None,
    doctrine: list[Mapping[str, Any]] | None = None,
    technical_atlas: Mapping[str, Any] | None = None,
    counterevidence: list[Mapping[str, Any]] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    if not subject.get("id"):
        raise ValueError("El análisis personal necesita subject.id.")
    if not natal:
        raise ValueError("El análisis personal necesita una capa natal calculada.")

    return {
        "schema_version": "1.0.0",
        "canonical_kind": "ALMAS_PERSONAL_ANALYSIS",
        "subject": dict(subject),
        "data_quality": dict(data_quality),
        "natal": dict(natal),
        "interpretive_layers": dict(interpretive_layers or {}),
        "temporal": dict(temporal or {}),
        "doctrine": [dict(item) for item in (doctrine or [])],
        "technical_atlas": dict(technical_atlas or {}),
        "counterevidence": [dict(item) for item in (counterevidence or [])],
        "limitations": list(limitations or []),
        "epistemic_classes": [
            "A_CALCULATED",
            "B_TECHNIQUE",
            "C_DOCTRINE",
            "D_CONTEMPORARY_USAGE",
            "E_PROJECT_HYPOTHESIS",
        ],
    }


def _path_available(canonical: Mapping[str, Any], path: str) -> bool:
    current: Any = canonical
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False
        current = current[part]
    if current in ({}, [], None):
        return False
    return True


def build_personal_report_model(
    canonical: Mapping[str, Any],
    *,
    mode: str = "FULL_CRITICAL_REPORT",
) -> dict[str, Any]:
    if mode not in PERSONAL_REPORT_MODES:
        raise ValueError(f"Modo personal no reconocido: {mode}")
    if canonical.get("canonical_kind") != "ALMAS_PERSONAL_ANALYSIS":
        raise ValueError("Se requiere un ALMAS_PERSONAL_ANALYSIS canónico.")
    for required in ("subject", "data_quality", "natal", "counterevidence"):
        if required not in canonical:
            raise ValueError(f"Falta ruta canónica obligatoria: {required}")

    sections = []
    for section_id, title, paths, modes in PERSONAL_SECTION_SPECS:
        if mode not in modes:
            continue
        available = [path for path in paths if _path_available(canonical, path)]
        missing = [path for path in paths if path not in available]
        sections.append(
            {
                "section_id": section_id,
                "order": len(sections) + 1,
                "title": title,
                "source_paths": list(paths),
                "available_paths": available,
                "missing_paths": missing,
                "section_state": "READY" if not missing else "PARTIAL",
                "canonical_values_embedded": False,
                "narrative_generated": False,
            }
        )

    return {
        "model_version": "1.0.0",
        "document_kind": "ALMAS_PERSONAL_REPORT_MODEL",
        "language": "es",
        "report_mode": mode,
        "canonical_source": "personal_canonical_analysis",
        "canonical_fingerprint": personal_fingerprint(canonical),
        "canonical_fingerprint_verified": True,
        "sections": sections,
        "canonical_values_embedded": False,
        "canonical_values_mutated": False,
        "prose_generated": False,
        "publication_pipeline_required": True,
    }
