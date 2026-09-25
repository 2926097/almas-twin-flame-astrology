from __future__ import annotations

from datetime import date
from itertools import combinations
from typing import Any, Mapping

from .astrology_handlers import make_m02_natal
from .relationship_chart_handlers import make_m08_davison
from .core import (
    diagnostic_discrimination,
    idd_band,
    pillar_score,
    robustness_index,
    score_model,
    supported_gate,
)
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .relational_handlers import m03_synastry, m04_nodes_angles_houses_regencies
from .symmetry_handlers import m05_declinations, m06_antiscia
from .relationship_chart_handlers import m07_composite
from .relationship_consonance import m09_relationship_chart_consonance
from .draconic_handlers import m10_individual_draconics, m11_natal_draconic_cross, m12_draconic_draconic
from .lot_handlers import m13_lots
from .secondary_handlers import m14_secondary_symbolic
from .evidence_handlers import m15_evidence_extraction, m16_dependency_deduplication, m17_independent_roots
from .counterevidence_handlers import m20_counterevidence
from .ablation_handlers import m22_ablation
from .time_sensitivity_handlers import m23_time_sensitivity
from .robustness_handlers import m23_time_sensitivity, m24_null_models
from .temporal_handlers import m26_temporal_activation, m27_dated_events
from .final_handlers import m28_doctrine_hermeneutics, m29_viability_reciprocity, m30_report_gate, m31_report


MODELS = ("AF", "KA", "AG", "LG")
PILLARS = ("PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU")



def m01_data_quality(context: ModuleContext) -> ModuleResult:
    """M01: evalúa completitud factual sin convertir ausencia en contradicción."""

    subjects = context.raw_input.get("subjects")
    if not isinstance(subjects, list) or len(subjects) != 2:
        return not_evaluable_result(
            "M01",
            "La entrada relacional debe contener exactamente dos subjects.",
        )

    evaluated = []
    degraded_reasons = []
    dates_complete = True
    timed_layers_evaluable = True

    for index, subject in enumerate(subjects):
        if not isinstance(subject, Mapping):
            raise ValueError(f"subjects[{index}] debe ser un objeto.")

        subject_id = str(subject.get("id") or f"subject_{index + 1}")
        birth_date = subject.get("birth_date")
        date_valid = False
        if isinstance(birth_date, str):
            try:
                date.fromisoformat(birth_date)
                date_valid = True
            except ValueError:
                date_valid = False

        if not date_valid:
            dates_complete = False
            degraded_reasons.append(f"{subject_id}: birth_date ausente o inválida.")

        birth_time = subject.get("birth_time")
        has_birth_time = isinstance(birth_time, str) and bool(birth_time.strip())
        has_timezone = isinstance(subject.get("timezone"), str) and bool(
            subject.get("timezone").strip()
        )
        has_place = isinstance(subject.get("place"), str) and bool(
            subject.get("place").strip()
        )
        latitude = subject.get("latitude")
        longitude = subject.get("longitude")
        has_coordinates = (
            isinstance(latitude, (int, float))
            and not isinstance(latitude, bool)
            and -90 <= float(latitude) <= 90
            and isinstance(longitude, (int, float))
            and not isinstance(longitude, bool)
            and -180 <= float(longitude) <= 180
        )
        location_available = has_coordinates or has_place
        timed_subject_evaluable = (
            date_valid and has_birth_time and has_timezone and location_available
        )

        if not timed_subject_evaluable:
            timed_layers_evaluable = False
            missing = []
            if not has_birth_time:
                missing.append("birth_time")
            if not has_timezone:
                missing.append("timezone")
            if not location_available:
                missing.append("place/coordinates")
            if missing:
                degraded_reasons.append(
                    f"{subject_id}: capas horarias degradadas por {', '.join(missing)}."
                )

        evaluated.append(
            {
                "id": subject_id,
                "birth_date_valid": date_valid,
                "birth_time_present": has_birth_time,
                "timezone_present": has_timezone,
                "location_available": location_available,
                "coordinates_valid": has_coordinates,
                "time_reliability": subject.get("time_reliability"),
                "timed_layers_evaluable": timed_subject_evaluable,
            }
        )

    output = {
        "subjects": evaluated,
        "untimed_layers_evaluable": dates_complete,
        "timed_layers_evaluable": dates_complete and timed_layers_evaluable,
        "degraded_reasons": degraded_reasons,
        "missing_data_are_counterevidence": False,
    }

    return ModuleResult(
        module_id="M01",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"data_quality": output},
        limitations=tuple(degraded_reasons),
    )


def m18_pillars(context: ModuleContext) -> ModuleResult:
    """M18: obtiene pilares precomputados o los deriva de raíces independientes."""

    root_strengths = context.raw_input.get("root_strengths")
    if isinstance(root_strengths, Mapping):
        calculated: dict[str, float | None] = {}
        for pillar in PILLARS:
            roots = root_strengths.get(pillar)
            if roots is None:
                calculated[pillar] = None
            elif isinstance(roots, (list, tuple)):
                calculated[pillar] = pillar_score(roots)
            else:
                raise ValueError(
                    f"{pillar}: root_strengths debe ser una lista de intensidades."
                )

        return ModuleResult(
            module_id="M18",
            status=ExecutionStatus.COMPLETED,
            payload={"source": "ROOT_STRENGTHS", "pillars": calculated},
            canonical_updates={"pillars": calculated},
        )

    pillars = context.raw_input.get("pillars")
    if isinstance(pillars, Mapping):
        copied = {pillar: pillars.get(pillar) for pillar in PILLARS}
        return ModuleResult(
            module_id="M18",
            status=ExecutionStatus.COMPLETED,
            payload={"source": "PRECOMPUTED", "pillars": copied},
            canonical_updates={"pillars": copied},
            limitations=(
                "Los pilares se recibieron precomputados; M18 no reconstruyó sus raíces.",
            ),
        )

    return not_evaluable_result(
        "M18",
        "Faltan pillars precomputados o root_strengths por pilar.",
    )


def m19_structural_model_indices(context: ModuleContext) -> ModuleResult:
    """M19: aplica sin cambios las fórmulas públicas de IEM e ICE."""

    pillars = context.canonical_snapshot.get("pillars")
    if not isinstance(pillars, Mapping):
        pillars = context.raw_input.get("pillars")
    if not isinstance(pillars, Mapping):
        return not_evaluable_result("M19", "No existen pilares evaluables.")

    ice_by_model = context.raw_input.get("ice_by_model") or {}
    if not isinstance(ice_by_model, Mapping):
        raise ValueError("ice_by_model debe ser un objeto.")

    contradictions = context.raw_input.get("essential_contradictions") or {}
    if not isinstance(contradictions, Mapping):
        raise ValueError("essential_contradictions debe ser un objeto.")

    icc = context.raw_input.get("icc")
    irc = context.raw_input.get("irc")
    r_min = context.raw_input.get("r_min")

    output: dict[str, Any] = {}
    for model in MODELS:
        score = score_model(
            model,
            pillars,
            ice=float(ice_by_model.get(model, 0.0)),
        )
        gate = None
        if icc is not None and irc is not None and r_min is not None:
            gate = supported_gate(
                score,
                icc=float(icc),
                irc=float(irc),
                r_min=float(r_min),
                essential_contradiction=bool(contradictions.get(model, False)),
            )

        output[model] = {
            "core": score.core,
            "support": score.support,
            "iem_pre": score.iem_pre,
            "ice": score.ice,
            "iem_final": score.iem_final,
            "essential_evaluable": score.essential_evaluable,
            "supported_gate": gate,
        }

    return ModuleResult(
        module_id="M19",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"structural_model_indices": output},
        limitations=(
            "Los IEM son índices de compatibilidad estructural, no probabilidades metafísicas.",
        ),
    )


def m21_differential_discrimination(context: ModuleContext) -> ModuleResult:
    """M21: calcula IDD por pares desde atribuciones de raíces ya derivadas."""

    attributions = context.raw_input.get("attributions")
    if not isinstance(attributions, Mapping):
        return not_evaluable_result(
            "M21",
            "Faltan atribuciones de raíces por modelo para calcular IDD.",
        )

    output: dict[str, Any] = {}
    for a, b in combinations(MODELS, 2):
        av = attributions.get(a)
        bv = attributions.get(b)
        if isinstance(av, Mapping) and isinstance(bv, Mapping):
            value = diagnostic_discrimination(av, bv)
            output[f"{a}_vs_{b}"] = {
                "idd": value,
                "band": idd_band(value),
            }

    if not output:
        return not_evaluable_result(
            "M21",
            "No existe ningún par de modelos con atribuciones evaluables.",
        )

    return ModuleResult(
        module_id="M21",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"pairwise_idd": output},
    )


def m25_robustness(context: ModuleContext) -> ModuleResult:
    """M25: agrega componentes de robustez ya calculados mediante IRC y R_min."""

    components = context.raw_input.get("robustness_components")
    component_map: dict[str, float] = {}

    if isinstance(components, Mapping):
        component_map = {
            str(name): float(value) for name, value in components.items()
        }
    elif isinstance(components, (list, tuple)):
        component_map = {
            f"INPUT_{index + 1}": float(value)
            for index, value in enumerate(components)
        }
    elif components is None:
        canonical_components = context.canonical_snapshot.get(
            "robustness_components"
        )
        if isinstance(canonical_components, Mapping):
            component_map = {
                str(name): float(value)
                for name, value in canonical_components.items()
            }
        elif isinstance(canonical_components, (list, tuple)):
            component_map = {
                f"CANONICAL_{index + 1}": float(value)
                for index, value in enumerate(canonical_components)
            }

    time_sensitivity = context.canonical_snapshot.get("time_sensitivity")
    if isinstance(time_sensitivity, Mapping):
        value = time_sensitivity.get("robustness_component")
        if value is not None and "BIRTH_TIME" not in component_map:
            component_map["BIRTH_TIME"] = float(value)

    if not component_map:
        return not_evaluable_result(
            "M25",
            "Faltan componentes de robustez preregistrados.",
        )

    values = list(component_map.values())
    irc, r_min = robustness_index(values)
    output = {
        "irc": irc,
        "r_min": r_min,
        "components": values,
        "component_map": component_map,
        "null_model_rarity_used_as_robustness": False,
    }

    return ModuleResult(
        module_id="M25",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"robustness_index": output},
        limitations=(
            "La rareza de M24 no entra en IRC salvo preregistro explícito como componente de robustez.",
        ),
    )


def default_handlers():
    """Handlers ejecutables disponibles sin alterar el resto del pipeline."""

    return {
        "M01": m01_data_quality,
        "M03": m03_synastry,
        "M04": m04_nodes_angles_houses_regencies,
        "M05": m05_declinations,
        "M06": m06_antiscia,
        "M07": m07_composite,
        "M09": m09_relationship_chart_consonance,
        "M10": m10_individual_draconics,
        "M11": m11_natal_draconic_cross,
        "M12": m12_draconic_draconic,
        "M13": m13_lots,
        "M14": m14_secondary_symbolic,
        "M15": m15_evidence_extraction,
        "M16": m16_dependency_deduplication,
        "M17": m17_independent_roots,
        "M18": m18_pillars,
        "M19": m19_structural_model_indices,
        "M20": m20_counterevidence,
        "M21": m21_differential_discrimination,
        "M22": m22_ablation,
        "M23": m23_time_sensitivity,
        "M24": m24_null_models,
        "M25": m25_robustness,
        "M26": m26_temporal_activation,
        "M27": m27_dated_events,
        "M28": m28_doctrine_hermeneutics,
        "M29": m29_viability_reciprocity,
        "M30": m30_report_gate,
        "M31": m31_report,
    }


def configured_handlers(*, astrology_backend=None, davison_backend=None):
    """Devuelve handlers por defecto más backends opcionales M02/M08.

    Permite ejecutar el pipeline completo sin acoplar ALMAS a una biblioteca
    astronómica concreta. Los backends se inyectan explícitamente.
    """

    handlers = default_handlers()
    if astrology_backend is not None:
        handlers["M02"] = make_m02_natal(astrology_backend)
    if davison_backend is not None:
        handlers["M08"] = make_m08_davison(davison_backend)
    return handlers
