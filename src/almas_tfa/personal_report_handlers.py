from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


PERSONAL_SCHEMA_VERSION = "1.0.0"
PERSONAL_ANALYSIS_TYPE = "PERSONAL_NATAL"

PROFILE_SECTIONS: dict[str, tuple[str, ...]] = {
    "EXECUTIVE_PERSONAL_REPORT": (
        "P01_SYNTHESIS", "P02_DATA_METHOD", "P03_NATAL_ARCHITECTURE",
        "P09_TEMPORAL", "P10_COUNTEREVIDENCE", "P11_SOURCES_ATLAS",
    ),
    "STANDARD_PERSONAL_REPORT": (
        "P01_SYNTHESIS", "P02_DATA_METHOD", "P03_NATAL_ARCHITECTURE",
        "P04_PERSONALITY_INTEGRATION", "P05_AFFECTIVE_RELATIONAL_STYLE",
        "P06_VOCATION_RESOURCES", "P08_COMPLEMENTARY_LAYERS",
        "P09_TEMPORAL", "P10_COUNTEREVIDENCE", "P11_SOURCES_ATLAS",
    ),
    "FULL_CRITICAL_REPORT": (
        "P01_SYNTHESIS", "P02_DATA_METHOD", "P03_NATAL_ARCHITECTURE",
        "P04_PERSONALITY_INTEGRATION", "P05_AFFECTIVE_RELATIONAL_STYLE",
        "P06_VOCATION_RESOURCES", "P07_EVOLUTIONARY_ESOTERIC",
        "P08_COMPLEMENTARY_LAYERS", "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE", "P11_SOURCES_ATLAS",
    ),
    "TECHNICAL_ATLAS": (
        "P02_DATA_METHOD", "P03_NATAL_ARCHITECTURE",
        "P08_COMPLEMENTARY_LAYERS", "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE", "P11_SOURCES_ATLAS",
    ),
    "ESOTERIC_KABBALISTIC_REPORT": (
        "P01_SYNTHESIS", "P02_DATA_METHOD", "P03_NATAL_ARCHITECTURE",
        "P04_PERSONALITY_INTEGRATION", "P07_EVOLUTIONARY_ESOTERIC",
        "P08_COMPLEMENTARY_LAYERS", "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE", "P11_SOURCES_ATLAS",
    ),
}

SECTION_SPECS: dict[str, dict[str, Any]] = {
    "P01_SYNTHESIS": {
        "title": "Síntesis ejecutiva",
        "required": ("natal",),
        "optional": ("limitations",),
        "classes": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    "P02_DATA_METHOD": {
        "title": "Calidad de datos y método",
        "required": ("data_quality", "calculation_provenance"),
        "optional": ("source_trace", "limitations"),
        "classes": ("A_CALCULATED", "B_TECHNIQUE"),
    },
    "P03_NATAL_ARCHITECTURE": {
        "title": "Arquitectura natal",
        "required": ("natal",),
        "optional": ("structural_layers",),
        "classes": ("A_CALCULATED", "B_TECHNIQUE", "E_PROJECT_HYPOTHESIS"),
    },
    "P04_PERSONALITY_INTEGRATION": {
        "title": "Personalidad e integración",
        "required": ("natal",),
        "optional": ("structural_layers", "hypotheses"),
        "classes": ("A_CALCULATED", "C_DOCTRINE", "E_PROJECT_HYPOTHESIS"),
    },
    "P05_AFFECTIVE_RELATIONAL_STYLE": {
        "title": "Estilo afectivo y relacional personal",
        "required": ("natal",),
        "optional": ("structural_layers", "hypotheses"),
        "classes": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    "P06_VOCATION_RESOURCES": {
        "title": "Vocación, recursos y vida cotidiana",
        "required": ("natal",),
        "optional": ("structural_layers",),
        "classes": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    "P07_EVOLUTIONARY_ESOTERIC": {
        "title": "Capas evolutiva, kármica, esotérica y cabalística",
        "required": (),
        "optional": ("structural_layers", "doctrine", "hypotheses"),
        "classes": ("C_DOCTRINE", "D_CONTEMPORARY_USAGE", "E_PROJECT_HYPOTHESIS"),
    },
    "P08_COMPLEMENTARY_LAYERS": {
        "title": "Capas técnicas complementarias",
        "required": (),
        "optional": ("secondary_layers",),
        "classes": ("A_CALCULATED", "B_TECHNIQUE", "E_PROJECT_HYPOTHESIS"),
    },
    "P09_TEMPORAL": {
        "title": "Ciclos y activación temporal",
        "required": (),
        "optional": ("temporal",),
        "classes": ("A_CALCULATED", "B_TECHNIQUE", "E_PROJECT_HYPOTHESIS"),
    },
    "P10_COUNTEREVIDENCE": {
        "title": "Contraevidencia, alternativas e incertidumbre",
        "required": ("counterevidence", "limitations"),
        "optional": (),
        "classes": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    "P11_SOURCES_ATLAS": {
        "title": "Fuentes, trazabilidad y atlas técnico",
        "required": ("calculation_provenance",),
        "optional": ("source_trace", "secondary_layers", "temporal", "doctrine"),
        "classes": (
            "A_CALCULATED", "B_TECHNIQUE", "C_DOCTRINE",
            "D_CONTEMPORARY_USAGE", "E_PROJECT_HYPOTHESIS",
        ),
    },
}


def personal_canonical_fingerprint(canonical: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _path_available(value: Mapping[str, Any], path: str) -> bool:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False
        current = current[part]
    return current is not None


def validate_personal_canonical(canonical: Mapping[str, Any]) -> dict[str, Any]:
    blocking: list[str] = []
    degraded: list[str] = []

    required = {
        "schema_version", "analysis_type", "subject", "data_quality",
        "calculation_provenance", "natal", "counterevidence", "limitations",
    }
    missing = sorted(required - set(canonical))
    if missing:
        blocking.append("MISSING_REQUIRED_FIELDS:" + ",".join(missing))

    if canonical.get("schema_version") != PERSONAL_SCHEMA_VERSION:
        blocking.append("UNSUPPORTED_SCHEMA_VERSION")
    if canonical.get("analysis_type") != PERSONAL_ANALYSIS_TYPE:
        blocking.append("INVALID_ANALYSIS_TYPE")

    provenance = canonical.get("calculation_provenance")
    if not isinstance(provenance, Mapping):
        blocking.append("CALCULATION_PROVENANCE_REQUIRED")
        provenance = {}
    else:
        for field in ("engine", "zodiac", "house_system", "node_type", "timezone", "coordinates"):
            if not provenance.get(field):
                blocking.append("PROVENANCE_MISSING:" + field)

    data_quality = canonical.get("data_quality")
    if not isinstance(data_quality, Mapping):
        blocking.append("DATA_QUALITY_REQUIRED")
    else:
        q = data_quality.get("birth_time_quality")
        if q not in {"A", "B", "C", "D"}:
            blocking.append("INVALID_BIRTH_TIME_QUALITY")
        elif q in {"C", "D"}:
            degraded.append("TIME_SENSITIVE_FACTORS_REQUIRE_DOWNGRADE")

    natal = canonical.get("natal")
    if not isinstance(natal, Mapping):
        blocking.append("NATAL_OBJECT_REQUIRED")
    else:
        if not isinstance(natal.get("positions"), list):
            blocking.append("NATAL_POSITIONS_REQUIRED")
        if not isinstance(natal.get("aspects"), list):
            blocking.append("NATAL_ASPECTS_REQUIRED")

    if not isinstance(canonical.get("counterevidence"), list):
        blocking.append("COUNTEREVIDENCE_MUST_BE_ARRAY")
    if not isinstance(canonical.get("limitations"), list):
        blocking.append("LIMITATIONS_MUST_BE_ARRAY")

    temporal = canonical.get("temporal")
    if isinstance(temporal, Mapping):
        returns = temporal.get("returns")
        if isinstance(returns, Sequence) and not isinstance(returns, (str, bytes)):
            for idx, item in enumerate(returns):
                if not isinstance(item, Mapping):
                    continue
                if item.get("houses_included") is True and not item.get("location_documented"):
                    blocking.append(f"RETURN_{idx}:HOUSES_WITHOUT_DOCUMENTED_LOCATION")

    warnings = provenance.get("warnings")
    if isinstance(warnings, list) and warnings:
        degraded.append("CALCULATION_WARNINGS_PRESENT")

    return {
        "state": "BLOCKED" if blocking else ("PARTIAL" if degraded else "READY"),
        "reportable": not blocking,
        "blocking_issues": sorted(set(blocking)),
        "degradation_reasons": sorted(set(degraded)),
        "canonical_fingerprint": None if blocking else personal_canonical_fingerprint(canonical),
    }


def route_personal_references(canonical: Mapping[str, Any]) -> list[str]:
    domains = {"foundations", "traditional", "modern_psychological", "publication"}

    structural = canonical.get("structural_layers")
    if isinstance(structural, Mapping):
        for key, domain in (
            ("evolutionary", "evolutionary"),
            ("karmic", "karmic"),
            ("esoteric", "esoteric"),
            ("kabbalistic", "kabbalah"),
        ):
            if structural.get(key):
                domains.add(domain)

    secondary = canonical.get("secondary_layers")
    if isinstance(secondary, Mapping):
        if secondary.get("draconic"):
            domains.add("draconic")
        if secondary.get("lots"):
            domains.add("lots")
        if any(secondary.get(k) for k in ("declinations", "antiscia", "midpoints")):
            domains.add("symmetry")
        if any(secondary.get(k) for k in ("fixed_stars", "parans")):
            domains.add("fixed_stars")
        if secondary.get("asteroids"):
            domains.add("asteroids")

    if canonical.get("temporal"):
        domains.add("timing")

    doctrine = canonical.get("doctrine")
    if isinstance(doctrine, list):
        serialized = json.dumps(doctrine, ensure_ascii=False).upper()
        if "KABB" in serialized or "CABAL" in serialized:
            domains.add("kabbalah")
        if "ESOTER" in serialized:
            domains.add("esoteric")

    return sorted(domains)


def _section(section_id: str, canonical: Mapping[str, Any], order: int) -> dict[str, Any]:
    spec = SECTION_SPECS[section_id]
    required = list(spec["required"])
    optional = list(spec["optional"])
    available_required = [p for p in required if _path_available(canonical, p)]
    missing_required = [p for p in required if p not in available_required]
    available_optional = [p for p in optional if _path_available(canonical, p)]

    if missing_required:
        state = "PARTIAL" if available_required else "NOT_AVAILABLE"
    elif required or available_optional:
        state = "READY"
    else:
        state = "NOT_AVAILABLE"

    return {
        "section_id": section_id,
        "order": order,
        "title": spec["title"],
        "section_state": state,
        "required_paths": required,
        "optional_paths": optional,
        "available_paths": sorted(set(available_required + available_optional)),
        "missing_required_paths": missing_required,
        "epistemic_classes_allowed": list(spec["classes"]),
        "canonical_values_embedded": False,
        "narrative_generated": False,
    }


def build_personal_report_document_model(
    canonical: Mapping[str, Any],
    profile: str = "FULL_CRITICAL_REPORT",
) -> dict[str, Any]:
    if profile not in PROFILE_SECTIONS:
        raise ValueError(f"Perfil personal desconocido: {profile}")

    gate = validate_personal_canonical(canonical)
    if not gate["reportable"]:
        raise ValueError(
            "personal_canonical_analysis no es reportable: "
            + "; ".join(gate["blocking_issues"])
        )

    fingerprint = gate["canonical_fingerprint"]
    current = personal_canonical_fingerprint(canonical)
    if fingerprint != current:
        raise ValueError("Fingerprint canónico personal inconsistente.")

    sections = [
        _section(section_id, canonical, order)
        for order, section_id in enumerate(PROFILE_SECTIONS[profile], start=1)
    ]

    if any(s["section_state"] == "PARTIAL" for s in sections):
        state = "PARTIAL"
    else:
        state = gate["state"]

    return {
        "model_version": "1.0.0",
        "document_kind": "ALMAS_PERSONAL_ASTROLOGY_REPORT_MODEL",
        "language": "es",
        "report_profile": profile,
        "report_state": state,
        "partial_disclosure_required": state == "PARTIAL",
        "degradation_reasons": list(gate["degradation_reasons"]),
        "canonical_source": "personal_canonical_analysis",
        "canonical_fingerprint": fingerprint,
        "canonical_fingerprint_verified": True,
        "sections": sections,
        "reference_domains": route_personal_references(canonical),
        "publication_contract": {
            "preferred_authoring": "DOCX",
            "default_page_size": "B5_176x250mm",
            "pdf_target": "PDF_1_7_GENERAL_PRINT",
            "pdf_x_claimed": False,
            "cmyk_icc_claimed": False,
            "font_embedding_required": True,
            "image_effective_dpi_minimum": 270,
            "full_page_render_qa_required": True,
            "pdf_preflight_required": True,
            "book_recto_openings_preferred": True,
            "mirrored_running_heads_preferred": True,
        },
        "canonical_values_embedded": False,
        "canonical_values_mutated": False,
        "prose_generated": False,
        "rendered_document_created": False,
        "docx_created": False,
        "pdf_created": False,
        "pdf_preflight_performed": False,
    }
