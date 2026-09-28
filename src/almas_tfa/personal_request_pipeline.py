from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .astrology_backend import (
    AstronomyBackendNotEvaluableError,
    AstrologyBackend,
    natal_request_from_subject,
)
from .personal_reporting import (
    PROFILE_SECTIONS,
    build_personal_report_document_model,
    validate_personal_canonical,
)


class PersonalRequestError(ValueError):
    pass


_ALLOWED_NATAL_KEYS = (
    "subject_id",
    "timed",
    "backend_id",
    "backend_version",
    "zodiac",
    "positions",
    "angles",
    "houses",
    "backend_provenance",
)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PersonalRequestError(f"{label} debe ser un objeto.")
    return value


def _request_profile(request: Mapping[str, Any]) -> str:
    profile = request.get("report_profile")
    if not isinstance(profile, str) or profile not in PROFILE_SECTIONS:
        raise PersonalRequestError(
            f"Perfil personal desconocido o ausente: {profile}"
        )
    return profile


def _subject_payload(request: Mapping[str, Any]) -> Mapping[str, Any]:
    subject = _require_mapping(request.get("subject"), "subject")
    if not isinstance(subject.get("id"), str) or not subject.get("id"):
        raise PersonalRequestError("subject.id es obligatorio.")
    if (
        not isinstance(subject.get("birth_date"), str)
        or not subject.get("birth_date")
    ):
        raise PersonalRequestError("subject.birth_date es obligatorio.")

    quality = subject.get("time_reliability")
    if quality not in {"A", "B", "C", "D"}:
        raise PersonalRequestError(
            "subject.time_reliability debe ser A, B, C o D."
        )

    source_class = subject.get("birth_time_source_class")
    if source_class not in {
        None,
        "DOCUMENTARY",
        "REPORTED",
        "RECTIFIED",
        "UNKNOWN",
    }:
        raise PersonalRequestError(
            "subject.birth_time_source_class no reconocido."
        )
    return subject


def _backend_provenance(
    chart: Mapping[str, Any],
    backend: AstrologyBackend,
) -> dict[str, Any]:
    chart_provenance = chart.get("backend_provenance")
    backend_provenance = getattr(backend, "provenance", None)

    if chart_provenance is not None and not isinstance(
        chart_provenance,
        Mapping,
    ):
        raise PersonalRequestError(
            "backend_provenance de la carta debe ser un objeto."
        )
    if backend_provenance is not None and not isinstance(
        backend_provenance,
        Mapping,
    ):
        raise PersonalRequestError(
            "backend.provenance debe ser un objeto."
        )

    if (
        isinstance(chart_provenance, Mapping)
        and isinstance(backend_provenance, Mapping)
        and dict(chart_provenance) != dict(backend_provenance)
    ):
        raise PersonalRequestError(
            "La procedencia de la carta diverge de la procedencia del backend."
        )

    selected = chart_provenance or backend_provenance
    if not isinstance(selected, Mapping):
        raise PersonalRequestError(
            "El pipeline personal exige backend_provenance explícita."
        )
    return deepcopy(dict(selected))


def _normalized_chart(
    raw_chart: Mapping[str, Any],
    backend: AstrologyBackend,
    *,
    subject_id: str,
    expected_timed: bool,
) -> dict[str, Any]:
    chart = dict(raw_chart)

    chart_subject = chart.get("subject_id")
    if chart_subject is not None and chart_subject != subject_id:
        raise PersonalRequestError(
            "La carta devuelta por el backend pertenece a otro subject_id."
        )

    chart_timed = chart.get("timed")
    if chart_timed is not None and chart_timed is not expected_timed:
        raise PersonalRequestError(
            "La carta devuelta por el backend diverge del estado timed."
        )

    chart_backend_id = chart.get("backend_id")
    if (
        chart_backend_id is not None
        and chart_backend_id != backend.backend_id
    ):
        raise PersonalRequestError(
            "backend_id de la carta diverge del backend inyectado."
        )

    chart_backend_version = chart.get("backend_version")
    if (
        chart_backend_version is not None
        and chart_backend_version != backend.backend_version
    ):
        raise PersonalRequestError(
            "backend_version de la carta diverge del backend inyectado."
        )

    positions = chart.get("positions")
    if not isinstance(positions, Mapping) or not positions:
        raise PersonalRequestError(
            "El backend no devolvió posiciones natales utilizables."
        )

    chart["subject_id"] = subject_id
    chart["timed"] = expected_timed
    chart["backend_id"] = backend.backend_id
    chart["backend_version"] = backend.backend_version
    chart["backend_provenance"] = _backend_provenance(chart, backend)

    # Lista blanca deliberada. En particular, no se persiste metadata del
    # backend porque puede contener instante UTC, JD o coordenadas capaces de
    # reconstruir los datos natales brutos.
    return {
        key: deepcopy(chart[key])
        for key in _ALLOWED_NATAL_KEYS
        if key in chart
    }


def build_personal_canonical_from_request(
    request: Mapping[str, Any],
    backend: AstrologyBackend,
) -> dict[str, Any]:
    """Calcula y minimiza un canonical personal desde una solicitud natal."""

    if request.get("schema_version") != "1.0.0":
        raise PersonalRequestError(
            "personal-report-request.schema_version debe ser 1.0.0."
        )
    _request_profile(request)
    subject = _subject_payload(request)

    natal_request = natal_request_from_subject(subject)
    try:
        raw_chart = backend.calculate_natal(natal_request)
    except AstronomyBackendNotEvaluableError:
        raise

    if not isinstance(raw_chart, Mapping):
        raise PersonalRequestError(
            "El backend debe devolver una carta natal como objeto."
        )

    chart = _normalized_chart(
        raw_chart,
        backend,
        subject_id=natal_request.subject_id,
        expected_timed=natal_request.timed,
    )

    quality = str(subject["time_reliability"])
    if quality in {"A", "B"} and chart["timed"] is not True:
        raise PersonalRequestError(
            "Una calidad horaria A/B requiere una carta timed."
        )

    subject_out: dict[str, Any] = {
        "subject_id": natal_request.subject_id,
    }
    display_name = subject.get("display_name")
    if isinstance(display_name, str) and display_name.strip():
        subject_out["display_name"] = display_name.strip()

    data_quality: dict[str, Any] = {
        "birth_time_quality": quality,
        "timed": bool(chart["timed"]),
    }
    source_class = subject.get("birth_time_source_class")
    if isinstance(source_class, str):
        data_quality["birth_time_source_class"] = source_class

    limitations: list[str] = []
    if quality in {"C", "D"}:
        limitations.append(
            "La hora natal tiene calidad C/D; casas, ángulos y técnicas "
            "sensibles a la hora deben interpretarse con degradación explícita."
        )
    if not chart["timed"]:
        limitations.append(
            "La carta no es horaria; no deben inferirse casas o ángulos "
            "como si fueran fiables."
        )

    canonical = {
        "schema_version": "1.0.0",
        "analysis_type": "PERSONAL_NATAL",
        "subject": subject_out,
        "data_quality": data_quality,
        "natal": chart,
        "counterevidence": [],
        "limitations": limitations,
    }

    gate = validate_personal_canonical(canonical)
    if not gate["reportable"]:
        raise PersonalRequestError(
            "El canonical personal construido no supera su contrato: "
            + "; ".join(gate["blocking_issues"])
        )
    return canonical


def build_personal_report_context_from_request(
    request: Mapping[str, Any],
    backend: AstrologyBackend,
) -> dict[str, Any]:
    """Construye canonical + modelo documental sin redactar ni publicar."""

    profile = _request_profile(request)
    canonical = build_personal_canonical_from_request(
        request,
        backend,
    )
    model = build_personal_report_document_model(
        canonical,
        profile,
    )
    return {
        "personal_canonical_analysis": canonical,
        "personal_report_document_model": model,
    }
