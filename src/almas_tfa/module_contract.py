from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol


class ExecutionStatus(str, Enum):
    """Estado operativo de una etapa del pipeline."""

    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ModuleContext:
    """Entrada inmutable entregada a cada módulo.

    canonical_snapshot es una copia lógica del estado acumulado en el momento
    de ejecutar el módulo. Un módulo no debe modificarla in-place.
    """

    module_id: str
    module_name: str
    mode: str
    raw_input: Mapping[str, Any]
    canonical_snapshot: Mapping[str, Any]
    prior_results: Mapping[str, "ModuleResult"]


@dataclass(frozen=True)
class ModuleResult:
    """Salida normalizada de un módulo ALMAS.

    canonical_updates contiene namespaces canónicos de primer nivel. El
    orquestador aplica estos cambios y prohíbe que otro módulo sobrescriba
    silenciosamente un namespace ya reclamado.
    """

    module_id: str
    status: ExecutionStatus
    payload: Mapping[str, Any] = field(default_factory=dict)
    canonical_updates: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "status": self.status.value,
            "payload": dict(self.payload),
            "canonical_updates": dict(self.canonical_updates),
            "evidence_refs": list(self.evidence_refs),
            "limitations": list(self.limitations),
            "diagnostics": list(self.diagnostics),
        }


class ModuleHandler(Protocol):
    """Firma ejecutable común para módulos registrados."""

    def __call__(self, context: ModuleContext) -> ModuleResult:
        ...


def not_evaluable_result(module_id: str, reason: str) -> ModuleResult:
    """Construye una salida explícita cuando una etapa no puede evaluarse."""

    return ModuleResult(
        module_id=module_id,
        status=ExecutionStatus.NOT_EVALUABLE,
        limitations=(reason,),
    )
