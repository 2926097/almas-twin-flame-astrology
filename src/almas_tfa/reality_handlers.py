from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleResult,
    not_evaluable_result,
)


VIABILITY = {
    "UNKNOWN",
    "STABLE",
    "UNSTABLE",
    "SEPARATED",
    "NON_ROMANTIC",
    "NO_CONTACT",
    "DEFINED_BY_FACTS",
}

RECIPROCITY = {
    "BILATERAL",
    "PARTIAL",
    "ASYMMETRIC",
    "NOT_EVALUABLE",
}

VIABILITY_BASIS_BY_STATE = {
    "STABLE": {"OBSERVED_STABLE_RELATIONSHIP"},
    "UNSTABLE": {"OBSERVED_UNSTABLE_RELATIONSHIP"},
    "SEPARATED": {"DOCUMENTED_SEPARATION"},
    "NON_ROMANTIC": {"EXPLICIT_NON_ROMANTIC_DEFINITION"},
    "NO_CONTACT": {"DOCUMENTED_NO_CONTACT"},
    "DEFINED_BY_FACTS": {"OTHER_DOCUMENTED_RELATIONSHIP_FORM"},
}

RECIPROCITY_BASIS_BY_STATE = {
    "BILATERAL": {"DOCUMENTED_BILATERALITY"},
    "PARTIAL": {"DOCUMENTED_PARTIAL_RECIPROCITY"},
    "ASYMMETRIC": {"DOCUMENTED_ASYMMETRY"},
}

DECISIVE_DOCUMENTARY_QUALITIES = {
    "DQ1_PRIMARY_DOCUMENT",
    "DQ2_DIRECT_SELF_REPORT",
    "DQ3_CORROBORATED_REPORT",
}

OBSERVATION_TYPES = {
    "EXPLICIT_STATEMENT",
    "OBSERVABLE_ACTION",
    "MUTUAL_AGREEMENT",
    "BOUNDARY_OR_REFUSAL",
    "DOCUMENTED_STATUS",
}


def _parse_as_of(value: Any) -> date:
    if not isinstance(value, str) or not value:
        raise ValueError("as_of_date es obligatorio en formato YYYY-MM-DD.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("as_of_date debe usar formato YYYY-MM-DD.") from exc


def _event_is_future(event: Mapping[str, Any], as_of: date) -> bool | None:
    precision = event.get("date_precision")
    raw_date = event.get("date")

    if precision == "EXACT_DATETIME" and isinstance(raw_date, str):
        try:
            dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            return dt.date() > as_of
        except ValueError:
            return None

    if precision == "EXACT_DATE" and isinstance(raw_date, str):
        try:
            return date.fromisoformat(raw_date) > as_of
        except ValueError:
            return None

    if precision == "MONTH" and isinstance(raw_date, str):
        try:
            year, month = (int(part) for part in raw_date.split("-", 1))
            return date(year, month, 1) > as_of
        except (TypeError, ValueError):
            return None

    if precision == "YEAR" and isinstance(raw_date, str):
        try:
            return date(int(raw_date), 1, 1) > as_of
        except (TypeError, ValueError):
            return None

    return None


def _event_eligibility(
    event: Mapping[str, Any],
    *,
    required_role: str,
    assessment_subjects: set[str],
    basis_subjects: set[str],
    as_of: date,
) -> tuple[bool, list[str], str]:
    issues: list[str] = []

    if event.get("record_status") != "ACTIVE":
        issues.append("EVENT_NOT_ACTIVE")

    if required_role not in event.get("evidence_roles", []):
        issues.append(f"MISSING_ROLE_{required_role}")

    if event.get("documentary_quality_contract_met") is not True:
        issues.append("DOCUMENTARY_QUALITY_CONTRACT_NOT_MET")

    if event.get("date_precision_contract_met") is not True:
        issues.append("DATE_PRECISION_CONTRACT_NOT_MET")

    if event.get("fact_interpretation_separated") is not True:
        issues.append("FACT_INTERPRETATION_NOT_SEPARATED")

    if event.get("documentary_quality") not in DECISIVE_DOCUMENTARY_QUALITIES:
        issues.append("DOCUMENTARY_QUALITY_NOT_DECISIVE_FOR_M29")

    event_subjects = {
        str(subject)
        for subject in event.get("subjects", [])
        if isinstance(subject, str) and subject
    }
    if not basis_subjects:
        issues.append("EMPTY_SUBJECT_COVERAGE")
    if not basis_subjects.issubset(assessment_subjects):
        issues.append("SUBJECT_COVERAGE_OUTSIDE_ASSESSMENT")
    if not basis_subjects.issubset(event_subjects):
        issues.append("SUBJECT_COVERAGE_NOT_SUPPORTED_BY_EVENT")

    future = _event_is_future(event, as_of)
    if future is True:
        issues.append("EVENT_AFTER_AS_OF_DATE")
        temporal_state = "AFTER_AS_OF_DATE"
    elif future is False:
        temporal_state = "ON_OR_BEFORE_AS_OF_DATE"
    else:
        temporal_state = "NOT_ORDERABLE_FROM_RECORDED_PRECISION"

    return not issues, issues, temporal_state


def _validate_basis(
    raw_basis: Any,
    *,
    axis: str,
    final_state: str,
    allowed_kinds: set[str],
    events: Mapping[str, Mapping[str, Any]],
    assessment_subjects: set[str],
    as_of: date,
) -> tuple[list[dict[str, Any]], set[str]]:
    if raw_basis is None:
        raw_basis = []
    if not isinstance(raw_basis, list):
        raise ValueError(f"{axis}_basis debe ser una lista.")

    normalized: list[dict[str, Any]] = []
    covered_subjects: set[str] = set()
    seen_event_kind: set[tuple[str, str]] = set()
    required_role = (
        "VIABILITY_FACT" if axis == "viability" else "RECIPROCITY_FACT"
    )

    for index, raw in enumerate(raw_basis):
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"{axis}_basis[{index}] debe ser un objeto."
            )

        event_id = raw.get("event_id")
        basis_kind = raw.get("basis_kind")
        observation_type = raw.get("observation_type")
        subject_ids = raw.get("subject_ids")

        if not isinstance(event_id, str) or not event_id:
            raise ValueError(
                f"{axis}_basis[{index}].event_id es obligatorio."
            )
        if event_id not in events:
            raise ValueError(
                f"{axis}_basis referencia evento desconocido: {event_id}"
            )
        if basis_kind not in allowed_kinds:
            raise ValueError(
                f"{axis}_basis[{index}].basis_kind no corresponde a {final_state}."
            )
        if observation_type not in OBSERVATION_TYPES:
            raise ValueError(
                f"{axis}_basis[{index}].observation_type inválido."
            )
        if (
            not isinstance(subject_ids, list)
            or not subject_ids
            or any(not isinstance(value, str) or not value for value in subject_ids)
        ):
            raise ValueError(
                f"{axis}_basis[{index}].subject_ids debe contener IDs válidos."
            )
        if len(set(subject_ids)) != len(subject_ids):
            raise ValueError(
                f"{axis}_basis[{index}].subject_ids contiene duplicados."
            )

        key = (event_id, str(basis_kind))
        if key in seen_event_kind:
            raise ValueError(
                f"Base factual duplicada para {event_id} / {basis_kind}."
            )
        seen_event_kind.add(key)

        basis_subjects = set(subject_ids)
        eligible, issues, temporal_state = _event_eligibility(
            events[event_id],
            required_role=required_role,
            assessment_subjects=assessment_subjects,
            basis_subjects=basis_subjects,
            as_of=as_of,
        )
        if not eligible:
            raise ValueError(
                f"{axis}_basis {event_id} no es elegible para M29: {issues}"
            )

        if basis_kind == "DOCUMENTED_SEPARATION":
            if events[event_id].get("event_type") != "SEPARATION":
                raise ValueError(
                    f"{event_id}: DOCUMENTED_SEPARATION exige event_type=SEPARATION."
                )
        if basis_kind == "DOCUMENTED_NO_CONTACT":
            if events[event_id].get("event_type") != "NO_CONTACT":
                raise ValueError(
                    f"{event_id}: DOCUMENTED_NO_CONTACT exige event_type=NO_CONTACT."
                )

        covered_subjects.update(basis_subjects)
        normalized.append(
            {
                "event_id": event_id,
                "basis_kind": basis_kind,
                "observation_type": observation_type,
                "subject_ids": sorted(basis_subjects),
                "required_role": required_role,
                "documentary_quality": events[event_id].get(
                    "documentary_quality"
                ),
                "temporal_admissibility": temporal_state,
                "eligible": True,
            }
        )

    normalized.sort(
        key=lambda item: (
            item["event_id"],
            item["basis_kind"],
            item["observation_type"],
        )
    )
    return normalized, covered_subjects


def m29_viability_reciprocity(context: ModuleContext) -> ModuleResult:
    """M29: valida viabilidad y reciprocidad exclusivamente desde hechos."""

    assessment = context.raw_input.get("viability_reciprocity_assessment")
    if not isinstance(assessment, Mapping):
        return not_evaluable_result(
            "M29",
            "Falta viability_reciprocity_assessment factual.",
        )

    assessment_ref = assessment.get("assessment_ref")
    if not isinstance(assessment_ref, str) or not assessment_ref:
        raise ValueError("assessment_ref es obligatorio.")

    as_of = _parse_as_of(assessment.get("as_of_date"))

    subjects = assessment.get("subjects")
    if (
        not isinstance(subjects, list)
        or len(subjects) != 2
        or any(not isinstance(value, str) or not value for value in subjects)
        or len(set(subjects)) != 2
    ):
        raise ValueError(
            "M29 requiere exactamente dos subject IDs distintos."
        )
    assessment_subjects = set(subjects)

    viability = assessment.get("real_viability")
    reciprocity = assessment.get("reciprocity")
    if viability not in VIABILITY:
        raise ValueError("real_viability inválida.")
    if reciprocity not in RECIPROCITY:
        raise ValueError("reciprocity inválida.")

    events_obj = context.canonical_snapshot.get("documentary_events")
    events = events_obj.get("events") if isinstance(events_obj, Mapping) else None
    if not isinstance(events, list):
        return not_evaluable_result(
            "M29",
            "M29 requiere documentary_events canónicos procedentes de M27.",
        )

    by_id: dict[str, Mapping[str, Any]] = {}
    for event in events:
        if isinstance(event, Mapping) and event.get("event_id"):
            by_id[str(event["event_id"])] = event

    if viability == "UNKNOWN":
        raw_viability_basis = assessment.get("viability_basis", [])
        if raw_viability_basis not in (None, []):
            raise ValueError(
                "real_viability=UNKNOWN no admite viability_basis confirmatoria."
            )
        viability_basis: list[dict[str, Any]] = []
        viability_coverage: set[str] = set()
    else:
        viability_basis, viability_coverage = _validate_basis(
            assessment.get("viability_basis"),
            axis="viability",
            final_state=viability,
            allowed_kinds=VIABILITY_BASIS_BY_STATE[viability],
            events=by_id,
            assessment_subjects=assessment_subjects,
            as_of=as_of,
        )
        if not viability_basis:
            raise ValueError(
                f"real_viability={viability} exige viability_basis."
            )
        if viability_coverage != assessment_subjects:
            raise ValueError(
                "La base de viabilidad debe cubrir a ambos sujetos."
            )

    if reciprocity == "NOT_EVALUABLE":
        raw_reciprocity_basis = assessment.get("reciprocity_basis", [])
        if raw_reciprocity_basis not in (None, []):
            raise ValueError(
                "reciprocity=NOT_EVALUABLE no admite reciprocity_basis confirmatoria."
            )
        reciprocity_basis: list[dict[str, Any]] = []
        reciprocity_coverage: set[str] = set()
    else:
        reciprocity_basis, reciprocity_coverage = _validate_basis(
            assessment.get("reciprocity_basis"),
            axis="reciprocity",
            final_state=reciprocity,
            allowed_kinds=RECIPROCITY_BASIS_BY_STATE[reciprocity],
            events=by_id,
            assessment_subjects=assessment_subjects,
            as_of=as_of,
        )
        if not reciprocity_basis:
            raise ValueError(
                f"reciprocity={reciprocity} exige reciprocity_basis."
            )
        if reciprocity_coverage != assessment_subjects:
            raise ValueError(
                "La base de reciprocidad debe cubrir a ambos sujetos; "
                "la ausencia de evidencia de una parte no demuestra asimetría."
            )

    viability_event_refs = sorted(
        {item["event_id"] for item in viability_basis}
    )
    reciprocity_event_refs = sorted(
        {item["event_id"] for item in reciprocity_basis}
    )

    output = {
        "assessment_ref": assessment_ref,
        "as_of_date": as_of.isoformat(),
        "subjects": sorted(assessment_subjects),
        "real_viability": viability,
        "reciprocity": reciprocity,
        "viability_basis": viability_basis,
        "reciprocity_basis": reciprocity_basis,
        "viability_event_refs": viability_event_refs,
        "reciprocity_event_refs": reciprocity_event_refs,
        "viability_subject_coverage": sorted(viability_coverage),
        "reciprocity_subject_coverage": sorted(reciprocity_coverage),
        "factual_basis_only": True,
        "astrology_used_as_real_world_fact": False,
        "metaphysical_claim_used_as_real_world_fact": False,
        "phase_used_as_viability": False,
        "phenomenology_used_as_reciprocity_fact": False,
        "absence_used_as_asymmetry": False,
        "mental_states_inferred": False,
        "consent_inferred": False,
        "fidelity_inferred": False,
        "future_decisions_inferred": False,
    }

    return ModuleResult(
        module_id="M29",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"viability_reciprocity": output},
        limitations=(
            "M29 valida una evaluación factual estructurada; no interpreta libremente el texto de los eventos.",
            "Los estados describen la situación documentada hasta as_of_date y no predicen decisiones futuras.",
            "La ausencia de evidencia de reciprocidad de una parte no se convierte en asimetría.",
        ),
    )
