from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .doctrine_handlers import m28_doctrine_hermeneutics
from .reality_handlers import m29_viability_reciprocity
from .report_gate_handlers import m30_report_gate





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
