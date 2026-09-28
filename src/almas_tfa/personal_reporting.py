from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


PERSONAL_SCHEMA_VERSION = "1.0.0"
PERSONAL_ANALYSIS_TYPE = "PERSONAL_NATAL"

PROFILE_SECTIONS: dict[str, tuple[str, ...]] = {
    "EXECUTIVE_PERSONAL_REPORT": (
        "P01_SYNTHESIS",
        "P02_DATA_METHOD",
        "P03_NATAL_ARCHITECTURE",
        "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE",
        "P11_SOURCES_ATLAS",
    ),
    "STANDARD_PERSONAL_REPORT": (
        "P01_SYNTHESIS",
        "P02_DATA_METHOD",
        "P03_NATAL_ARCHITECTURE",
        "P04_PERSONALITY_INTEGRATION",
        "P05_AFFECTIVE_RELATIONAL_STYLE",
        "P06_VOCATION_RESOURCES",
        "P08_COMPLEMENTARY_LAYERS",
        "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE",
        "P11_SOURCES_ATLAS",
    ),
    "FULL_CRITICAL_REPORT": (
        "P01_SYNTHESIS",
        "P02_DATA_METHOD",
        "P03_NATAL_ARCHITECTURE",
        "P04_PERSONALITY_INTEGRATION",
        "P05_AFFECTIVE_RELATIONAL_STYLE",
        "P06_VOCATION_RESOURCES",
        "P07_EVOLUTIONARY_ESOTERIC",
        "P08_COMPLEMENTARY_LAYERS",
        "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE",
        "P11_SOURCES_ATLAS",
    ),
    "TECHNICAL_ATLAS": (
        "P02_DATA_METHOD",
        "P03_NATAL_ARCHITECTURE",
        "P08_COMPLEMENTARY_LAYERS",
        "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE",
        "P11_SOURCES_ATLAS",
    ),
    "ESOTERIC_KABBALISTIC_REPORT": (
        "P01_SYNTHESIS",
        "P02_DATA_METHOD",
        "P03_NATAL_ARCHITECTURE",
        "P04_PERSONALITY_INTEGRATION",
        "P07_EVOLUTIONARY_ESOTERIC",
        "P08_COMPLEMENTARY_LAYERS",
        "P09_TEMPORAL",
        "P10_COUNTEREVIDENCE",
        "P11_SOURCES_ATLAS",
    ),
}

SECTION_SPECS: dict[str, dict[str, Any]] = {
    "P01_SYNTHESIS": {
        "title": "Síntesis ejecutiva",
        "required": ("natal",),
        "optional": ("limitations", "hypotheses"),
        "classes": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    "P02_DATA_METHOD": {
        "title": "Calidad de datos y método",
        "required": ("data_quality", "natal.backend_provenance"),
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
        "required": ("natal.backend_provenance",),
        "optional": ("source_trace", "secondary_layers", "temporal", "doctrine"),
        "classes": (
            "A_CALCULATED",
            "B_TECHNIQUE",
            "C_DOCTRINE",
            "D_CONTEMPORARY_USAGE",
            "E_PROJECT_HYPOTHESIS",
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


def _layer_enabled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, Mapping):
        if "available" in value:
            return value.get("available") is True
        state = value.get("state")
        if isinstance(state, str):
            return state.upper() not in {
                "NOT_AVAILABLE",
                "NOT_EVALUABLE",
                "DISABLED",
                "ABSENT",
            }
        return bool(value)
    return bool(value)


def validate_personal_canonical(canonical: Mapping[str, Any]) -> dict[str, Any]:
    blocking: list[str] = []
    degraded: list[str] = []

    required = {
        "schema_version",
        "analysis_type",
        "subject",
        "data_quality",
        "natal",
        "counterevidence",
        "limitations",
    }
    missing = sorted(required - set(canonical))
    if missing:
        blocking.append("MISSING_REQUIRED_FIELDS:" + ",".join(missing))

    if canonical.get("schema_version") != PERSONAL_SCHEMA_VERSION:
        blocking.append("UNSUPPORTED_SCHEMA_VERSION")
    if canonical.get("analysis_type") != PERSONAL_ANALYSIS_TYPE:
        blocking.append("INVALID_ANALYSIS_TYPE")

    subject = canonical.get("subject")
    subject_id = None
    if not isinstance(subject, Mapping):
        blocking.append("SUBJECT_REQUIRED")
    else:
        subject_id = subject.get("subject_id")
        if not isinstance(subject_id, str) or not subject_id:
            blocking.append("SUBJECT_ID_REQUIRED")

    data_quality = canonical.get("data_quality")
    timed = None
    if not isinstance(data_quality, Mapping):
        blocking.append("DATA_QUALITY_REQUIRED")
    else:
        quality = data_quality.get("birth_time_quality")
        if quality not in {"A", "B", "C", "D"}:
            blocking.append("INVALID_BIRTH_TIME_QUALITY")
        elif quality in {"C", "D"}:
            degraded.append("TIME_SENSITIVE_FACTORS_REQUIRE_DOWNGRADE")
        timed = data_quality.get("timed")
        if not isinstance(timed, bool):
            blocking.append("DATA_QUALITY_TIMED_REQUIRED")

    natal = canonical.get("natal")
    if not isinstance(natal, Mapping):
        blocking.append("NATAL_REQUIRED")
    else:
        if subject_id and natal.get("subject_id") != subject_id:
            blocking.append("NATAL_SUBJECT_ID_MISMATCH")
        if timed is not None and natal.get("timed") is not timed:
            blocking.append("NATAL_TIMED_MISMATCH")
        positions = natal.get("positions")
        if not isinstance(positions, Mapping) or not positions:
            blocking.append("NATAL_POSITIONS_REQUIRED")
        provenance = natal.get("backend_provenance")
        if not isinstance(provenance, Mapping):
            blocking.append("BACKEND_PROVENANCE_REQUIRED")
        else:
            for field in (
                "policy_id",
                "adapter_id",
                "backend_id",
                "backend_version",
                "kernel_sha256",
                "house_system",
                "node_mode",
                "zodiac",
            ):
                if not provenance.get(field):
                    blocking.append("PROVENANCE_MISSING:" + field)
            if provenance.get("network_io_used") is not False:
                blocking.append("PROVENANCE_NETWORK_IO_MUST_BE_FALSE")
            if provenance.get("geocoding_used") is not False:
                blocking.append("PROVENANCE_GEOCODING_MUST_BE_FALSE")

    if not isinstance(canonical.get("counterevidence"), list):
        blocking.append("COUNTEREVIDENCE_MUST_BE_ARRAY")
    if not isinstance(canonical.get("limitations"), list):
        blocking.append("LIMITATIONS_MUST_BE_ARRAY")

    temporal = canonical.get("temporal")
    if isinstance(temporal, Mapping):
        returns = temporal.get("returns")
        if returns is not None:
            if not isinstance(returns, Sequence) or isinstance(returns, (str, bytes)):
                blocking.append("TEMPORAL_RETURNS_MUST_BE_ARRAY")
            else:
                for index, item in enumerate(returns):
                    if not isinstance(item, Mapping):
                        blocking.append(f"RETURN_{index}:MUST_BE_OBJECT")
                        continue
                    if (
                        item.get("houses_included") is True
                        and item.get("location_documented") is not True
                    ):
                        blocking.append(
                            f"RETURN_{index}:HOUSES_WITHOUT_DOCUMENTED_LOCATION"
                        )

    blocking = sorted(set(blocking))
    degraded = sorted(set(degraded))
    return {
        "state": "BLOCKED" if blocking else ("PARTIAL" if degraded else "READY"),
        "reportable": not blocking,
        "blocking_issues": blocking,
        "degradation_reasons": degraded,
        "canonical_fingerprint": (
            None if blocking else personal_canonical_fingerprint(canonical)
        ),
    }


def route_personal_reference_domains(canonical: Mapping[str, Any]) -> list[str]:
    domains = {
        "foundations",
        "traditional",
        "modern_psychological",
        "publication",
    }

    structural = canonical.get("structural_layers")
    if isinstance(structural, Mapping):
        for key, domain in (
            ("evolutionary", "evolutionary"),
            ("karmic", "karmic"),
            ("esoteric", "esoteric"),
            ("kabbalistic", "kabbalah"),
        ):
            if _layer_enabled(structural.get(key)):
                domains.add(domain)

    secondary = canonical.get("secondary_layers")
    if isinstance(secondary, Mapping):
        if _layer_enabled(secondary.get("draconic")):
            domains.add("draconic")
        if _layer_enabled(secondary.get("lots")):
            domains.add("lots")
        if any(
            _layer_enabled(secondary.get(key))
            for key in ("declinations", "antiscia", "midpoints")
        ):
            domains.add("symmetry")
        if any(
            _layer_enabled(secondary.get(key))
            for key in ("fixed_stars", "parans")
        ):
            domains.add("fixed_stars")
        if _layer_enabled(secondary.get("asteroids")):
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


def _section_model(
    section_id: str,
    canonical: Mapping[str, Any],
    order: int,
) -> dict[str, Any]:
    spec = SECTION_SPECS[section_id]
    required = list(spec["required"])
    optional = list(spec["optional"])
    available_required = [
        path for path in required if _path_available(canonical, path)
    ]
    missing_required = [
        path for path in required if path not in available_required
    ]
    available_optional = [
        path for path in optional if _path_available(canonical, path)
    ]
    missing_optional = [
        path for path in optional if path not in available_optional
    ]

    if missing_required:
        state = "PARTIAL" if available_required else "NOT_AVAILABLE"
    elif required:
        state = "READY"
    elif available_optional:
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
        "available_paths": sorted(
            set(available_required + available_optional)
        ),
        "missing_required_paths": missing_required,
        "missing_optional_paths": missing_optional,
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

    current = personal_canonical_fingerprint(canonical)
    if current != gate["canonical_fingerprint"]:
        raise ValueError("El fingerprint personal cambió durante la validación.")

    sections = [
        _section_model(section_id, canonical, order)
        for order, section_id in enumerate(PROFILE_SECTIONS[profile], start=1)
    ]

    return {
        "model_version": "1.0.0",
        "document_kind": "ALMAS_PERSONAL_REPORT_MODEL",
        "language": "es",
        "analysis_type": PERSONAL_ANALYSIS_TYPE,
        "report_profile": profile,
        "report_state": gate["state"],
        "degradation_reasons": gate["degradation_reasons"],
        "canonical_source": "personal_canonical_analysis",
        "canonical_fingerprint": current,
        "canonical_fingerprint_verified": True,
        "reference_domains": route_personal_reference_domains(canonical),
        "sections": sections,
        "publication_contract": {
            "profile_family": "ALMAS_B5",
            "reuse_existing_publication_infrastructure": True,
            "adapter_status": "READY",
        },
        "canonical_values_embedded": False,
        "canonical_values_mutated": False,
        "prose_generated": False,
        "docx_created": False,
        "pdf_created": False,
        "pdf_preflight_performed": False,
    }
