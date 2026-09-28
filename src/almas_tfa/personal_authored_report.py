from __future__ import annotations

from typing import Any, Mapping, Sequence

from .personal_reporting import personal_canonical_fingerprint


class PersonalAuthoringError(ValueError):
    pass


def _claim_ids(canonical: Mapping[str, Any]) -> set[str]:
    doctrine = canonical.get("doctrine")
    if not isinstance(doctrine, list):
        return set()
    return {
        str(item["claim_id"])
        for item in doctrine
        if isinstance(item, Mapping)
        and isinstance(item.get("claim_id"), str)
        and item.get("claim_id")
    }


def _canonical_source_ids(canonical: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()

    source_trace = canonical.get("source_trace")
    if isinstance(source_trace, list):
        for item in source_trace:
            if not isinstance(item, Mapping):
                continue
            source_id = item.get("source_id")
            if isinstance(source_id, str) and source_id:
                result.add(source_id)

    doctrine = canonical.get("doctrine")
    if isinstance(doctrine, list):
        for item in doctrine:
            if not isinstance(item, Mapping):
                continue
            source_id = item.get("source_id")
            if isinstance(source_id, str) and source_id:
                result.add(source_id)
            refs = item.get("source_refs")
            if isinstance(refs, list):
                result.update(
                    str(ref)
                    for ref in refs
                    if isinstance(ref, str) and ref
                )
    return result


def validate_personal_authored_report_trace(
    authored_report: Mapping[str, Any],
    report_document_model: Mapping[str, Any],
    personal_canonical_analysis: Mapping[str, Any],
) -> None:
    """Valida autoría personal sin recalcular ni permitir fuentes no trazadas."""

    expected_fingerprint = personal_canonical_fingerprint(
        personal_canonical_analysis
    )
    model_fingerprint = report_document_model.get("canonical_fingerprint")
    authored_fingerprint = authored_report.get("canonical_fingerprint")

    if report_document_model.get("document_kind") != "ALMAS_PERSONAL_REPORT_MODEL":
        raise PersonalAuthoringError(
            "El modelo documental no es ALMAS_PERSONAL_REPORT_MODEL."
        )
    if authored_report.get("document_kind") != "ALMAS_PERSONAL_AUTHORED_REPORT":
        raise PersonalAuthoringError(
            "El documento redactado no es ALMAS_PERSONAL_AUTHORED_REPORT."
        )
    if report_document_model.get("canonical_fingerprint_verified") is not True:
        raise PersonalAuthoringError(
            "El modelo documental no verificó el fingerprint personal."
        )
    if model_fingerprint != expected_fingerprint:
        raise PersonalAuthoringError(
            "El personal_report_document_model no corresponde al canonical."
        )
    if authored_fingerprint != expected_fingerprint:
        raise PersonalAuthoringError(
            "El personal_authored_report no corresponde al canonical."
        )

    for field in ("report_profile", "report_state"):
        if authored_report.get(field) != report_document_model.get(field):
            raise PersonalAuthoringError(
                f"El personal_authored_report debe conservar {field}."
            )

    model_sections = report_document_model.get("sections")
    authored_sections = authored_report.get("sections")
    if not isinstance(model_sections, Sequence) or isinstance(
        model_sections, (str, bytes)
    ):
        raise PersonalAuthoringError(
            "personal_report_document_model.sections inválido."
        )
    if not isinstance(authored_sections, Sequence) or isinstance(
        authored_sections, (str, bytes)
    ):
        raise PersonalAuthoringError(
            "personal_authored_report.sections inválido."
        )

    model_ids = [
        section.get("section_id")
        for section in model_sections
        if isinstance(section, Mapping)
    ]
    authored_ids = [
        section.get("section_id")
        for section in authored_sections
        if isinstance(section, Mapping)
    ]
    if authored_ids != model_ids:
        raise PersonalAuthoringError(
            "La autoría personal debe conservar exactamente el orden del modelo."
        )

    model_by_id = {
        section.get("section_id"): section
        for section in model_sections
        if isinstance(section, Mapping)
    }

    canonical_claim_ids = _claim_ids(personal_canonical_analysis)
    canonical_source_ids = _canonical_source_ids(
        personal_canonical_analysis
    )

    bibliography = authored_report.get("bibliography")
    if not isinstance(bibliography, list):
        raise PersonalAuthoringError(
            "personal_authored_report.bibliography debe ser una lista."
        )

    bibliography_ids: set[str] = set()
    for entry in bibliography:
        if not isinstance(entry, Mapping):
            raise PersonalAuthoringError(
                "Cada entrada bibliográfica debe ser un objeto."
            )
        source_id = entry.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise PersonalAuthoringError(
                "Cada entrada bibliográfica debe declarar source_id."
            )
        if source_id in bibliography_ids:
            raise PersonalAuthoringError(
                f"Fuente bibliográfica duplicada: {source_id}"
            )
        if source_id not in canonical_source_ids:
            raise PersonalAuthoringError(
                f"Fuente bibliográfica no trazada en el canonical: {source_id}"
            )
        bibliography_ids.add(source_id)

    for section in authored_sections:
        if not isinstance(section, Mapping):
            raise PersonalAuthoringError(
                "Cada sección redactada debe ser un objeto."
            )
        section_id = section.get("section_id")
        model_section = model_by_id.get(section_id)
        if not isinstance(model_section, Mapping):
            raise PersonalAuthoringError(
                f"Sección no declarada por el modelo personal: {section_id}"
            )

        state = section.get("authoring_state")
        model_state = model_section.get("section_state")
        if model_state == "NOT_AVAILABLE":
            if state != "OMITTED_NOT_AVAILABLE":
                raise PersonalAuthoringError(
                    f"{section_id}: sección no disponible no puede redactarse."
                )
            if section.get("narrative") not in ("", None):
                raise PersonalAuthoringError(
                    f"{section_id}: sección omitida debe tener narrative vacío."
                )
            for field in (
                "canonical_paths_used",
                "epistemic_classes_used",
                "doctrinal_claim_refs",
                "source_refs",
            ):
                if section.get(field):
                    raise PersonalAuthoringError(
                        f"{section_id}: sección omitida no admite {field}."
                    )
            continue

        if state != "AUTHORED":
            raise PersonalAuthoringError(
                f"{section_id}: sección disponible debe quedar AUTHORED."
            )
        narrative = section.get("narrative")
        if not isinstance(narrative, str) or not narrative.strip():
            raise PersonalAuthoringError(
                f"{section_id}: narrative no puede estar vacío."
            )

        used_paths = section.get("canonical_paths_used", [])
        if not isinstance(used_paths, list) or not used_paths:
            raise PersonalAuthoringError(
                f"{section_id}: debe declarar canonical_paths_used."
            )
        allowed_paths = set(model_section.get("available_paths", []))
        unknown_paths = sorted(set(used_paths) - allowed_paths)
        if unknown_paths:
            raise PersonalAuthoringError(
                f"{section_id}: rutas no autorizadas: "
                + ", ".join(unknown_paths)
            )

        used_classes = set(section.get("epistemic_classes_used", []))
        allowed_classes = set(
            model_section.get("epistemic_classes_allowed", [])
        )
        if not used_classes.issubset(allowed_classes):
            raise PersonalAuthoringError(
                f"{section_id}: clases epistemológicas fuera del contrato."
            )

        unknown_claims = sorted(
            set(section.get("doctrinal_claim_refs", []))
            - canonical_claim_ids
        )
        if unknown_claims:
            raise PersonalAuthoringError(
                f"{section_id}: claims doctrinales desconocidos: "
                + ", ".join(unknown_claims)
            )

        unknown_sources = sorted(
            set(section.get("source_refs", [])) - bibliography_ids
        )
        if unknown_sources:
            raise PersonalAuthoringError(
                f"{section_id}: source_refs sin bibliografía: "
                + ", ".join(unknown_sources)
            )

    expected_flags = {
        "metaphysical_scientific_validation_claimed": False,
        "personal_data_minimized": True,
        "canonical_values_mutated": False,
        "new_calculations_performed": False,
        "new_scores_created": False,
    }
    for field, expected in expected_flags.items():
        if authored_report.get(field) is not expected:
            raise PersonalAuthoringError(
                f"{field} debe conservarse como {expected}."
            )
