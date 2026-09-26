from __future__ import annotations

from typing import Iterable


CAPABILITIES = frozenset(
    {
        "NATAL_CORE",
        "TIMED_ANGLES_HOUSES",
        "DECLINATIONS",
        "ANTISCIA",
        "COMPOSITE",
        "DAVISON",
        "DRACONIC",
        "LOTS",
        "FIXED_STARS",
        "PARANS",
        "TRANSITS",
        "PROGRESSIONS",
        "SOLAR_ARC",
        "PROFECTIONS",
        "RETURNS",
        "ATACIRES",
        "RELATIONAL_CANONICAL",
        "PERSONAL_CANONICAL",
        "REPORT_MODEL",
        "DOCX_AUTHORING",
        "PDF_RENDER",
        "PDF_PREFLIGHT",
    }
)

REPORT_REQUIREMENTS = {
    "RELATIONAL_RESEARCH": {
        "required": {"RELATIONAL_CANONICAL", "REPORT_MODEL"},
        "optional": {
            "TIMED_ANGLES_HOUSES", "DECLINATIONS", "ANTISCIA", "COMPOSITE",
            "DAVISON", "DRACONIC", "LOTS", "TRANSITS", "PROGRESSIONS",
            "SOLAR_ARC", "PROFECTIONS", "RETURNS", "ATACIRES",
        },
    },
    "EXECUTIVE_PERSONAL_REPORT": {
        "required": {"NATAL_CORE", "PERSONAL_CANONICAL"},
        "optional": {"TIMED_ANGLES_HOUSES"},
    },
    "STANDARD_PERSONAL_REPORT": {
        "required": {"NATAL_CORE", "PERSONAL_CANONICAL"},
        "optional": {
            "TIMED_ANGLES_HOUSES", "DECLINATIONS", "ANTISCIA", "LOTS",
            "TRANSITS", "PROGRESSIONS",
        },
    },
    "FULL_CRITICAL_REPORT": {
        "required": {"NATAL_CORE", "PERSONAL_CANONICAL"},
        "optional": {
            "TIMED_ANGLES_HOUSES", "DECLINATIONS", "ANTISCIA", "DRACONIC",
            "LOTS", "FIXED_STARS", "PARANS", "TRANSITS", "PROGRESSIONS",
            "SOLAR_ARC", "PROFECTIONS", "RETURNS", "ATACIRES",
        },
    },
    "TECHNICAL_ATLAS": {
        "required": {"NATAL_CORE", "PERSONAL_CANONICAL"},
        "optional": {
            "TIMED_ANGLES_HOUSES", "DECLINATIONS", "ANTISCIA", "DRACONIC",
            "LOTS", "FIXED_STARS", "PARANS", "TRANSITS", "PROGRESSIONS",
            "SOLAR_ARC", "PROFECTIONS", "RETURNS", "ATACIRES",
        },
    },
    "ESOTERIC_KABBALISTIC_REPORT": {
        "required": {"NATAL_CORE", "PERSONAL_CANONICAL"},
        "optional": {"DRACONIC", "LOTS", "FIXED_STARS", "PARANS"},
    },
}


def route_capabilities(
    report_kind: str,
    available: Iterable[str],
    *,
    output_format: str = "PLAN",
) -> dict:
    if report_kind not in REPORT_REQUIREMENTS:
        raise ValueError(f"report_kind no reconocido: {report_kind}")

    available_set = set(available)
    unknown = sorted(available_set - CAPABILITIES)
    spec = REPORT_REQUIREMENTS[report_kind]
    required = set(spec["required"])
    optional = set(spec["optional"])

    if output_format.upper() == "PDF":
        required |= {"PDF_RENDER", "PDF_PREFLIGHT"}
        optional |= {"DOCX_AUTHORING"}
    elif output_format.upper() == "DOCX":
        required |= {"DOCX_AUTHORING"}
    elif output_format.upper() != "PLAN":
        raise ValueError("output_format debe ser PLAN, DOCX o PDF.")

    missing_required = sorted(required - available_set)
    missing_optional = sorted(optional - available_set)

    if missing_required:
        state = "BLOCKED"
    elif missing_optional:
        state = "PARTIAL"
    else:
        state = "READY"

    return {
        "route_version": "1.0.0",
        "report_kind": report_kind,
        "output_format": output_format.upper(),
        "state": state,
        "required_capabilities": sorted(required),
        "optional_capabilities": sorted(optional),
        "available_capabilities": sorted(available_set & CAPABILITIES),
        "missing_required_capabilities": missing_required,
        "missing_optional_capabilities": missing_optional,
        "unknown_capabilities": unknown,
        "silent_fallback_allowed": False,
    }
