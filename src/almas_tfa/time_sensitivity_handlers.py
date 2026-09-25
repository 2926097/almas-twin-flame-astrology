from __future__ import annotations

from typing import Any, Mapping

from .core import robustness_component
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


def m23_time_sensitivity(context: ModuleContext) -> ModuleResult:
    """M23: calcula robustez horaria desde resúmenes de perturbación preregistrados.

    M23 no decide cómo estimar delta90. Esa estadística debe llegar ya calculada
    por el protocolo de perturbación utilizado, junto con G (fracción de
    corridas que preservan la banda interpretativa preregistrada).
    """

    families = context.raw_input.get("time_sensitivity_families")
    if not isinstance(families, list) or not families:
        return not_evaluable_result(
            "M23",
            "Faltan time_sensitivity_families preregistradas.",
        )

    output_families: list[dict[str, Any]] = []
    components: list[float] = []

    for index, raw in enumerate(families, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"time_sensitivity_families[{index - 1}] debe ser un objeto."
            )

        family_id = raw.get("id")
        if not isinstance(family_id, str) or not family_id:
            raise ValueError(f"Familia {index}: id es obligatorio.")

        delta90 = raw.get("delta90")
        preserved_fraction = raw.get("preserved_fraction")
        if delta90 is None or preserved_fraction is None:
            raise ValueError(
                f"{family_id}: delta90 y preserved_fraction son obligatorios."
            )

        delta90 = float(delta90)
        preserved_fraction = float(preserved_fraction)
        component = robustness_component(delta90, preserved_fraction)

        n_runs = raw.get("n_runs")
        if n_runs is not None:
            if isinstance(n_runs, bool) or int(n_runs) != n_runs or int(n_runs) <= 0:
                raise ValueError(f"{family_id}: n_runs debe ser entero positivo.")
            n_runs = int(n_runs)

        window_minutes = raw.get("window_minutes")
        if window_minutes is not None:
            window_minutes = float(window_minutes)
            if window_minutes < 0:
                raise ValueError(
                    f"{family_id}: window_minutes no puede ser negativo."
                )

        subjects = raw.get("subjects")
        if subjects is not None:
            if not isinstance(subjects, list) or not all(
                isinstance(x, str) and x for x in subjects
            ):
                raise ValueError(
                    f"{family_id}: subjects debe ser una lista de IDs."
                )

        output_families.append(
            {
                "id": family_id,
                "delta90": delta90,
                "preserved_fraction": preserved_fraction,
                "robustness_component": component,
                "n_runs": n_runs,
                "window_minutes": window_minutes,
                "subjects": list(subjects) if isinstance(subjects, list) else [],
                "metric": raw.get("metric"),
                "band_rule": raw.get("band_rule"),
                "source_ref": raw.get("source_ref"),
            }
        )
        components.append(component)

    output_families.sort(key=lambda item: item["id"])
    output = {
        "families": output_families,
        "component_count": len(components),
        "components": components,
        "formula": "exp(-delta90/20) * sqrt(G)",
        "delta90_estimation": "EXTERNAL_PREREGISTERED",
        "aggregated_irc": None,
    }

    return ModuleResult(
        module_id="M23",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"time_sensitivity": output},
        limitations=(
            "M23 no estima delta90 a partir de muestras: exige un resumen preregistrado.",
            "M23 no calcula IRC agregado; esa agregación pertenece a M25.",
        ),
    )
