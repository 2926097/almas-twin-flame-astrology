from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .doctrine_handlers import m28_doctrine_hermeneutics



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


def m29_viability_reciprocity(context: ModuleContext) -> ModuleResult:
    """M29: acepta únicamente evaluación factual de viabilidad y reciprocidad."""

    assessment = context.raw_input.get("viability_reciprocity_assessment")
    if not isinstance(assessment, Mapping):
        return not_evaluable_result(
            "M29",
            "Falta viability_reciprocity_assessment factual.",
        )

    viability = assessment.get("real_viability")
    reciprocity = assessment.get("reciprocity")
    if viability not in VIABILITY:
        raise ValueError("real_viability inválida.")
    if reciprocity not in RECIPROCITY:
        raise ValueError("reciprocity inválida.")

    events_obj = context.canonical_snapshot.get("documentary_events")
    events = events_obj.get("events") if isinstance(events_obj, Mapping) else []
    by_id = {
        str(event.get("event_id")): event
        for event in events or []
        if isinstance(event, Mapping) and event.get("event_id")
    }

    viability_refs = [str(x) for x in assessment.get("viability_event_refs", [])]
    reciprocity_refs = [str(x) for x in assessment.get("reciprocity_event_refs", [])]

    unknown_refs = sorted(
        {
            ref
            for ref in viability_refs + reciprocity_refs
            if ref not in by_id
        }
    )
    if unknown_refs:
        raise ValueError(
            f"M29 contiene referencias documentales desconocidas: {unknown_refs}"
        )

    if viability not in {"UNKNOWN"}:
        if not viability_refs:
            raise ValueError(
                "Una viabilidad distinta de UNKNOWN exige viability_event_refs."
            )
        if not any(
            "VIABILITY_FACT" in by_id[ref].get("evidence_roles", [])
            for ref in viability_refs
        ):
            raise ValueError(
                "La viabilidad declarada requiere al menos un evento VIABILITY_FACT."
            )

    if reciprocity != "NOT_EVALUABLE":
        if not reciprocity_refs:
            raise ValueError(
                "Una reciprocidad evaluada exige reciprocity_event_refs."
            )
        if not any(
            "RECIPROCITY_FACT" in by_id[ref].get("evidence_roles", [])
            for ref in reciprocity_refs
        ):
            raise ValueError(
                "La reciprocidad declarada requiere al menos un evento RECIPROCITY_FACT."
            )

    output = {
        "real_viability": viability,
        "reciprocity": reciprocity,
        "viability_event_refs": viability_refs,
        "reciprocity_event_refs": reciprocity_refs,
        "astrology_used_as_real_world_fact": False,
        "future_decisions_inferred": False,
    }

    return ModuleResult(
        module_id="M29",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"viability_reciprocity": output},
        limitations=(
            "La reciprocidad astrológica no sustituye la reciprocidad interpersonal documentada.",
        ),
    )


CANONICAL_REQUIRED = {
    "schema_version",
    "analysis_mode",
    "evidence",
    "models",
    "coverage",
    "robustness",
    "counterevidence",
}


def m30_report_gate(context: ModuleContext) -> ModuleResult:
    """M30: comprueba que el informe derive de un análisis canónico suficiente."""

    canonical_analysis = context.raw_input.get("canonical_analysis")
    source = "RAW_INPUT"
    if not isinstance(canonical_analysis, Mapping):
        canonical_analysis = context.canonical_snapshot.get("canonical_analysis")
        source = "CANONICAL_SNAPSHOT"

    if not isinstance(canonical_analysis, Mapping):
        output = {
            "state": "BLOCKED",
            "source": None,
            "missing_fields": sorted(CANONICAL_REQUIRED),
            "failed_modules": [],
            "reportable": False,
            "reason": "No existe canonical_analysis.",
        }
        return ModuleResult(
            module_id="M30",
            status=ExecutionStatus.COMPLETED,
            payload=output,
            canonical_updates={"report_gate": output},
        )

    missing = sorted(CANONICAL_REQUIRED - set(canonical_analysis))
    failed_modules = sorted(
        module_id
        for module_id, result in context.prior_results.items()
        if result.status is ExecutionStatus.FAILED
    )

    analysis_mode = canonical_analysis.get("analysis_mode")
    partial_mode = analysis_mode in {"TARGETED", "TEMPORAL"}

    if failed_modules or missing:
        state = "BLOCKED"
        reportable = False
    elif partial_mode:
        state = "PARTIAL"
        reportable = True
    else:
        state = "READY"
        reportable = True

    output = {
        "state": state,
        "source": source,
        "missing_fields": missing,
        "failed_modules": failed_modules,
        "reportable": reportable,
        "analysis_mode": analysis_mode,
        "canonical_values_mutated": False,
    }

    updates = {"report_gate": output}
    if source == "RAW_INPUT":
        updates["canonical_analysis"] = deepcopy(dict(canonical_analysis))

    return ModuleResult(
        module_id="M30",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates=updates,
        limitations=(
            "M30 valida suficiencia formal; no corrige ni reinterpreta valores canónicos.",
        ),
    )


REPORT_SECTIONS = (
    ("S01_SYNTHESIS", "Síntesis"),
    ("S02_DATA_METHOD", "Calidad de datos y método"),
    ("S03_NUMERIC_ONTOLOGY", "Ontología numérica"),
    ("S04_STRUCTURE", "Arquitectura estructural"),
    ("S05_RELATIONAL", "Capas relacionales y cruzadas"),
    ("S06_DIFFERENTIAL", "Diagnóstico diferencial y contraevidencia"),
    ("S07_TEMPORAL", "Activación temporal y eventos"),
    ("S08_ROBUSTNESS", "Robustez y validación"),
    ("S09_DOCTRINE", "Doctrina comparada y corpus"),
    ("S10_FINAL_SYNTHESIS", "Síntesis final"),
    ("S11_SOURCES_APPENDICES", "Fuentes y anexos"),
)


def m31_report(context: ModuleContext) -> ModuleResult:
    """M31: crea un modelo documental que sólo referencia la verdad canónica."""

    gate = context.canonical_snapshot.get("report_gate")
    canonical_analysis = context.canonical_snapshot.get("canonical_analysis")

    if not isinstance(gate, Mapping) or gate.get("reportable") is not True:
        return not_evaluable_result(
            "M31",
            "El report gate no autoriza generación de modelo documental.",
        )
    if not isinstance(canonical_analysis, Mapping):
        return not_evaluable_result(
            "M31",
            "No existe canonical_analysis canónico.",
        )

    path_map = {
        "S01_SYNTHESIS": ["models", "ontology"],
        "S02_DATA_METHOD": ["coverage", "limitations"],
        "S03_NUMERIC_ONTOLOGY": ["models", "indices", "ontology"],
        "S04_STRUCTURE": ["evidence", "models"],
        "S05_RELATIONAL": ["evidence"],
        "S06_DIFFERENTIAL": ["models", "counterevidence"],
        "S07_TEMPORAL": ["temporal"],
        "S08_ROBUSTNESS": ["robustness", "indices"],
        "S09_DOCTRINE": ["doctrine"],
        "S10_FINAL_SYNTHESIS": ["models", "ontology", "limitations"],
        "S11_SOURCES_APPENDICES": ["evidence", "doctrine"],
    }

    sections = [
        {
            "section_id": section_id,
            "title": title,
            "canonical_paths": path_map[section_id],
        }
        for section_id, title in REPORT_SECTIONS
    ]

    output = {
        "model_version": "1.0.0",
        "analysis_mode": canonical_analysis.get("analysis_mode"),
        "sections": sections,
        "canonical_source": "canonical_analysis",
        "canonical_values_mutated": False,
        "rendered_document_created": False,
    }

    return ModuleResult(
        module_id="M31",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"report_document_model": output},
        limitations=(
            "M31 construye el modelo documental; la renderización DOCX/PDF pertenece al pipeline de publicación.",
        ),
    )
