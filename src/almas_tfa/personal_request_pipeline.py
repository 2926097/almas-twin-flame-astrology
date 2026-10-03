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
from .chiron_process import assess_chiron_process, derive_natal_contacts
from .surrender_vestal import evaluate_surrender_requests
from .dual_nodes import build_dual_node_layer, classify_nodal_variant_concordance


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
    "nodal_variant_layer",
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

    frozen = {
        "policy_id": "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1",
        "adapter_id": "ALMAS_MOIRA_JPL_SPK_V1",
        "backend_id": "MOIRA_JPL_SPK",
        "backend_version": "6.8.2",
        "provider_package": "moira-astro",
        "provider_version": "6.8.2",
        "node_mode": "TRUE_NODE",
        "node_variants": ["TRUE", "MEAN"],
        "zodiac": "TROPICAL",
        "coordinate_origin": "GEOCENTRIC",
        "reference_frame": "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
        "apparent_reduction": True,
        "topocentric_positions": False,
        "network_io_used": False,
        "geocoding_used": False,
    }
    for field, expected in frozen.items():
        if selected.get(field) != expected:
            raise PersonalRequestError(
                f"backend_provenance incompatible: {field}"
            )

    for field in (
        "kernel_filename",
        "kernel_family",
        "kernel_sha256",
        "house_system",
    ):
        if not isinstance(selected.get(field), str) or not selected.get(field):
            raise PersonalRequestError(
                f"backend_provenance incompleta: {field}"
            )

    if selected["kernel_family"] not in {"DE430", "DE440", "DE441"}:
        raise PersonalRequestError(
            "backend_provenance incompatible: kernel_family"
        )
    kernel_sha = selected["kernel_sha256"]
    if (
        len(kernel_sha) != 64
        or any(ch not in "0123456789abcdef" for ch in kernel_sha)
    ):
        raise PersonalRequestError(
            "backend_provenance incompatible: kernel_sha256"
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
    if chart["backend_provenance"].get("node_variants") == ["TRUE", "MEAN"]:
        required_nodes = {"NORTH_NODE", "SOUTH_NODE", "MEAN_NORTH_NODE", "MEAN_SOUTH_NODE"}
        if not required_nodes.issubset(positions):
            raise PersonalRequestError(
                "El backend declara nodos TRUE+MEAN pero no devolvió los cuatro extremos."
            )
        dual = build_dual_node_layer(
            positions["NORTH_NODE"], positions["MEAN_NORTH_NODE"],
        )
        dual["nodal_variant_concordance"] = classify_nodal_variant_concordance(dual)
        dual["interpretive_hypothesis"] = {
            "statement": "Mean Node = vector estructural; True Node = modulación fenoménica/oscilatoria",
            "epistemic_class": "E_PROJECT_HYPOTHESIS",
            "validation_status": "UNVALIDATED",
        }
        chart["nodal_variant_layer"] = dual

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

    fixed = request.get("fixed_stars")
    if fixed is not None:
        if not isinstance(fixed, Mapping) or set(fixed) != {"enabled"} or type(fixed["enabled"]) is not bool:
            raise PersonalRequestError("fixed_stars exige exclusivamente enabled booleano.")
        if fixed["enabled"]:
            from .personal_fixed_stars import calculate_personal_fixed_stars
            canonical["secondary_layers"] = {"fixed_stars": calculate_personal_fixed_stars(
                backend, natal_request, quality=quality, provenance=chart["backend_provenance"])}
            from .corpus_doctrine import load_corpus_doctrine_policy
            source_ids = canonical["secondary_layers"]["fixed_stars"]["method_source_ids"]
            sources = {entry["id"]: entry for entry in load_corpus_doctrine_policy()["source_snapshots"]}
            canonical["source_trace"] = [dict(source_id=source_id,
                author=sources[source_id]["author"], work=sources[source_id]["work"],
                url=sources[source_id]["url"], source_scope="METHOD", epistemic_class="B_TECHNIQUE",
                verification_status=sources[source_id]["verification_status"],
                verification_anchor=sources[source_id]["verification_anchor"]) for source_id in source_ids]


    chiron_request = request.get("chiron_process")
    if chiron_request is not None:
        if not isinstance(chiron_request, Mapping):
            raise PersonalRequestError("chiron_process debe ser un objeto.")
        aspect_policy = chiron_request.get("aspect_policy")
        aspect_policy_ref = chiron_request.get("aspect_policy_ref")
        if not isinstance(aspect_policy, Mapping) or not isinstance(aspect_policy_ref, str):
            raise PersonalRequestError(
                "chiron_process requiere aspect_policy y aspect_policy_ref explícitos."
            )
        derived = derive_natal_contacts(
            chart.get("positions", {}), aspect_policy,
            aspect_policy_ref=aspect_policy_ref,
        )
        complex_result = assess_chiron_process(
            natal_contacts=derived["contacts"],
            temporal_signals=chiron_request.get("temporal_signals", []),
            temporal_sequence=chiron_request.get("temporal_sequence"),
            documentary_evidence=chiron_request.get("documentary_evidence", []),
            technique_search=chiron_request.get("technique_search"),
            counterevidence=chiron_request.get("counterevidence", []),
            complex_id=str(chiron_request.get("complex_id") or "PTC-001"),
        )
        complex_result["natal_architecture"]["counterevidence"] = derived["counterevidence"]
        canonical["personal_temporal_complexes"] = [complex_result]
        canonical["counterevidence"].extend(derived["counterevidence"])

    vestal_request = request.get("surrender_vestal")
    if vestal_request is not None:
        if not isinstance(vestal_request, Mapping) or vestal_request.get("subject_id") != canonical["subject"]["subject_id"]:
            raise PersonalRequestError("surrender_vestal debe identificar al sujeto de la solicitud personal.")
        canonical["surrender_vestal"] = evaluate_surrender_requests([vestal_request])

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
