from __future__ import annotations

from .counterevidence_index import resolve_counterevidence
from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleResult,
    not_evaluable_result,
)


def m20_counterevidence(context: ModuleContext) -> ModuleResult:
    """M20: normaliza contraevidencia y resuelve ICE con firewall de revisión."""

    raw_items = context.raw_input.get("counterevidence_items")
    precomputed = context.raw_input.get("ice_by_model")
    review_complete = context.raw_input.get("counterevidence_review_complete") is True

    if raw_items is None and precomputed is None and not review_complete:
        return not_evaluable_result(
            "M20",
            "No se declararon contradicciones explícitas, revisión completa ni ICE precomputado.",
        )

    output = resolve_counterevidence(context.raw_input)

    limitations = [
        "La ausencia de datos no entra en ICE ni se trata como contraevidencia.",
        "Las contradicciones dependientes se deduplican antes de cualquier agregación.",
    ]
    if output["ice_state"] == "DERIVED_AUTONOMOUS_V1":
        limitations.append(
            "ICE autónomo es E_PROJECT_POLICY: un índice de contraevidencia estructural, no una probabilidad metafísica."
        )
    elif output["ice_state"] == "PRECOMPUTED":
        limitations.append(
            "ICE se conserva como entrada precomputada porque no se declaró una revisión completa de contraevidencia."
        )
    else:
        limitations.append(
            "La revisión de contraevidencia no está cerrada: ICE permanece NOT_CALCULATED."
        )

    return ModuleResult(
        module_id="M20",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"counterevidence": output},
        limitations=tuple(limitations),
    )
