from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleResult,
    not_evaluable_result,
)


SECTION_SPECS = (
    {
        "section_id": "S01_SYNTHESIS",
        "title": "Síntesis ejecutiva",
        "purpose": "Resumir estados y arquitectura sin elevar conclusiones.",
        "required_paths": ("models",),
        "optional_paths": ("ontology", "limitations"),
        "epistemic_classes_allowed": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    {
        "section_id": "S02_DATA_METHOD",
        "title": "Calidad de datos y método",
        "purpose": "Exponer cobertura, límites y condiciones metodológicas.",
        "required_paths": ("coverage",),
        "optional_paths": ("limitations",),
        "epistemic_classes_allowed": ("A_CALCULATED", "B_TECHNIQUE"),
    },
    {
        "section_id": "S03_NUMERIC_ONTOLOGY",
        "title": "Ontología numérica",
        "purpose": "Presentar índices y estados sin convertirlos en probabilidades metafísicas.",
        "required_paths": ("models",),
        "optional_paths": ("indices", "ontology"),
        "epistemic_classes_allowed": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    {
        "section_id": "S04_STRUCTURE",
        "title": "Arquitectura estructural",
        "purpose": "Describir evidencia y raíces estructurales con trazabilidad.",
        "required_paths": ("evidence", "models"),
        "optional_paths": (),
        "epistemic_classes_allowed": (
            "A_CALCULATED",
            "B_TECHNIQUE",
            "E_PROJECT_HYPOTHESIS",
        ),
    },
    {
        "section_id": "S05_RELATIONAL",
        "title": "Capas relacionales y cruzadas",
        "purpose": "Organizar las capas relacionales sin duplicar evidencia dependiente.",
        "required_paths": ("evidence",),
        "optional_paths": (),
        "epistemic_classes_allowed": (
            "A_CALCULATED",
            "B_TECHNIQUE",
            "E_PROJECT_HYPOTHESIS",
        ),
    },
    {
        "section_id": "S06_DIFFERENTIAL",
        "title": "Diagnóstico diferencial y contraevidencia",
        "purpose": "Contrastar modelos, alternativas y evidencia contraria.",
        "required_paths": ("models", "counterevidence"),
        "optional_paths": ("ontology",),
        "epistemic_classes_allowed": ("A_CALCULATED", "E_PROJECT_HYPOTHESIS"),
    },
    {
        "section_id": "S07_TEMPORAL",
        "title": "Activación temporal y eventos",
        "purpose": "Separar activación simbólica de hechos documentales y predicción.",
        "required_paths": ("temporal",),
        "optional_paths": ("limitations",),
        "epistemic_classes_allowed": (
            "A_CALCULATED",
            "B_TECHNIQUE",
            "E_PROJECT_HYPOTHESIS",
        ),
    },
    {
        "section_id": "S08_ROBUSTNESS",
        "title": "Robustez y validación",
        "purpose": "Exponer cobertura, robustez, sensibilidad y límites estadísticos.",
        "required_paths": ("robustness",),
        "optional_paths": ("indices",),
        "epistemic_classes_allowed": ("A_CALCULATED", "B_TECHNIQUE"),
    },
    {
        "section_id": "S09_DOCTRINE",
        "title": "Doctrina comparada y corpus",
        "purpose": "Separar doctrina, uso contemporáneo e hipótesis del proyecto.",
        "required_paths": ("doctrine",),
        "optional_paths": (),
        "epistemic_classes_allowed": (
            "C_DOCTRINE",
            "D_CONTEMPORARY_USAGE",
            "E_PROJECT_HYPOTHESIS",
        ),
    },
    {
        "section_id": "S10_FINAL_SYNTHESIS",
        "title": "Síntesis final",
        "purpose": "Integrar resultados sin superar los techos inferenciales.",
        "required_paths": ("models",),
        "optional_paths": ("ontology", "limitations"),
        "epistemic_classes_allowed": (
            "A_CALCULATED",
            "C_DOCTRINE",
            "D_CONTEMPORARY_USAGE",
            "E_PROJECT_HYPOTHESIS",
        ),
    },
    {
        "section_id": "S11_SOURCES_APPENDICES",
        "title": "Fuentes y anexos",
        "purpose": "Conservar trazabilidad de evidencia, doctrina y limitaciones.",
        "required_paths": ("evidence",),
        "optional_paths": ("doctrine", "limitations"),
        "epistemic_classes_allowed": (
            "A_CALCULATED",
            "B_TECHNIQUE",
            "C_DOCTRINE",
            "D_CONTEMPORARY_USAGE",
            "E_PROJECT_HYPOTHESIS",
        ),
    },
)


def _canonical_fingerprint(canonical: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _path_available(canonical: Mapping[str, Any], path: str) -> bool:
    current: Any = canonical
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False
        current = current[part]
    return True


def _section_model(
    spec: Mapping[str, Any],
    canonical: Mapping[str, Any],
    order: int,
) -> dict[str, Any]:
    required = list(spec["required_paths"])
    optional = list(spec["optional_paths"])

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

    if not missing_required:
        state = "READY"
    elif available_required:
        state = "PARTIAL"
    else:
        state = "NOT_AVAILABLE"

    return {
        "section_id": spec["section_id"],
        "order": order,
        "title": spec["title"],
        "purpose": spec["purpose"],
        "section_state": state,
        "required_paths": required,
        "optional_paths": optional,
        "available_paths": sorted(
            set(available_required + available_optional)
        ),
        "missing_required_paths": missing_required,
        "missing_optional_paths": missing_optional,
        "epistemic_classes_allowed": list(
            spec["epistemic_classes_allowed"]
        ),
        "canonical_values_embedded": False,
        "narrative_generated": False,
    }


def m31_report(context: ModuleContext) -> ModuleResult:
    """M31: construye un modelo documental trazable, sin redactar ni renderizar."""

    gate = context.canonical_snapshot.get("report_gate")
    canonical = context.canonical_snapshot.get("canonical_analysis")

    if not isinstance(gate, Mapping) or gate.get("reportable") is not True:
        return not_evaluable_result(
            "M31",
            "M30 no autoriza la construcción del modelo documental.",
        )
    if gate.get("state") not in {"READY", "PARTIAL"}:
        return not_evaluable_result(
            "M31",
            "El estado del report gate no es READY ni PARTIAL.",
        )
    if not isinstance(canonical, Mapping):
        return not_evaluable_result(
            "M31",
            "No existe canonical_analysis canónico.",
        )

    gate_fingerprint = gate.get("canonical_fingerprint")
    if not isinstance(gate_fingerprint, str) or not gate_fingerprint:
        raise ValueError(
            "M31 exige canonical_fingerprint procedente de M30."
        )

    current_fingerprint = _canonical_fingerprint(canonical)
    if current_fingerprint != gate_fingerprint:
        raise ValueError(
            "canonical_analysis cambió después de M30; fingerprint no coincide."
        )

    sections = [
        _section_model(spec, canonical, order)
        for order, spec in enumerate(SECTION_SPECS, start=1)
    ]

    section_counts = {
        state: sum(
            1 for section in sections
            if section["section_state"] == state
        )
        for state in ("READY", "PARTIAL", "NOT_AVAILABLE")
    }

    partial_report = gate.get("state") == "PARTIAL"
    degradation_reasons = list(gate.get("degradation_reasons", []))

    output = {
        "model_version": "1.0.0",
        "document_kind": "ALMAS_ANALYTICAL_REPORT_MODEL",
        "language": "es",
        "analysis_mode": canonical.get("analysis_mode"),
        "report_state": gate.get("state"),
        "partial_disclosure_required": partial_report,
        "degradation_reasons": degradation_reasons,
        "canonical_source": "canonical_analysis",
        "canonical_fingerprint": current_fingerprint,
        "canonical_fingerprint_verified": True,
        "sections": sections,
        "section_counts": section_counts,
        "section_order_fixed": True,
        "canonical_values_embedded": False,
        "canonical_values_mutated": False,
        "prose_generated": False,
        "render_profile_selected": False,
        "rendered_document_created": False,
        "docx_created": False,
        "pdf_created": False,
        "pdf_preflight_performed": False,
        "publication_pipeline_required": True,
    }

    limitations = [
        "M31 construye estructura y referencias; no redacta la narrativa final.",
        "M31 no copia valores analíticos al modelo documental: conserva rutas hacia canonical_analysis.",
        "La renderización DOCX/PDF y su preflight pertenecen a la fase de publicación.",
    ]
    if partial_report:
        limitations.append(
            "El documento debe mostrar explícitamente las degradation_reasons heredadas de M30."
        )

    return ModuleResult(
        module_id="M31",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"report_document_model": output},
        limitations=tuple(limitations),
    )
