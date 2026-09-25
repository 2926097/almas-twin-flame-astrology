from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .doctrine_handlers import m28_doctrine_hermeneutics
from .reality_handlers import m29_viability_reciprocity




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
