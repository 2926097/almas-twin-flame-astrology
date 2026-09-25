from __future__ import annotations

from typing import Any, Mapping

from .astrology_backend import AstrologyBackend, natal_request_from_subject
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


def make_m02_natal(backend: AstrologyBackend):
    """Construye M02 para un backend astronómico explícitamente suministrado."""

    def m02_natal(context: ModuleContext) -> ModuleResult:
        subjects = context.raw_input.get("subjects")
        if not isinstance(subjects, list) or len(subjects) != 2:
            return not_evaluable_result(
                "M02",
                "M02 requiere exactamente dos subjects normalizados.",
            )

        charts: dict[str, Any] = {}
        limitations = []

        for subject in subjects:
            if not isinstance(subject, Mapping):
                raise ValueError("Cada subject debe ser un objeto.")

            request = natal_request_from_subject(subject)
            chart = dict(backend.calculate_natal(request))

            chart.setdefault("subject_id", request.subject_id)
            chart.setdefault("timed", request.timed)
            chart.setdefault("backend_id", backend.backend_id)
            chart.setdefault("backend_version", backend.backend_version)

            if not request.timed:
                limitations.append(
                    f"{request.subject_id}: carta no horaria; casas y ángulos "
                    "no deben inferirse como si fueran fiables."
                )

            charts[request.subject_id] = chart

        output = {
            "backend": {
                "id": backend.backend_id,
                "version": backend.backend_version,
            },
            "charts": charts,
        }

        return ModuleResult(
            module_id="M02",
            status=ExecutionStatus.COMPLETED,
            payload=output,
            canonical_updates={"natal": output},
            limitations=tuple(limitations),
        )

    return m02_natal
