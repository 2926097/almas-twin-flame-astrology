from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleHandler,
    ModuleResult,
    not_evaluable_result,
)


EXPECTED_PIPELINE_IDS = tuple(f"M{i:02d}" for i in range(32))


class PipelineDefinitionError(ValueError):
    """El manifiesto de pipeline no respeta el contrato M00-M31."""


class CanonicalOverwriteError(RuntimeError):
    """Un módulo intenta sobrescribir un namespace propiedad de otro."""


@dataclass(frozen=True)
class OrchestrationRun:
    mode: str
    canonical: Mapping[str, Any]
    results: Mapping[str, ModuleResult]
    ownership: Mapping[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "canonical": deepcopy(dict(self.canonical)),
            "ownership": dict(self.ownership),
            "modules": {
                module_id: result.to_dict()
                for module_id, result in self.results.items()
            },
        }


def validate_pipeline_manifest(manifest: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """Valida la secuencia mínima del manifiesto FULL sin reinterpretarla."""

    if manifest.get("mode") != "FULL":
        raise PipelineDefinitionError("El manifiesto debe declarar mode=FULL.")

    modules = manifest.get("modules")
    if not isinstance(modules, list):
        raise PipelineDefinitionError("El manifiesto debe contener una lista modules.")

    ids = tuple(module.get("id") for module in modules if isinstance(module, Mapping))
    if ids != EXPECTED_PIPELINE_IDS:
        raise PipelineDefinitionError(
            "El manifiesto debe contener M00..M31, en orden y exactamente una vez."
        )

    for module in modules:
        if not isinstance(module.get("name"), str) or not module["name"]:
            raise PipelineDefinitionError(
                f"{module.get('id')}: falta un nombre de módulo válido."
            )

    return tuple(modules)


class Orchestrator:
    """Ejecutor secuencial y conservador del pipeline ALMAS.

    La existencia del orquestador no implica que las 32 etapas dispongan ya de
    implementación. Las etapas sin handler registrado quedan NOT_EVALUABLE y
    conservan trazabilidad explícita.
    """

    def __init__(self, handlers: Mapping[str, ModuleHandler] | None = None) -> None:
        self._handlers: dict[str, ModuleHandler] = dict(handlers or {})

    def register(self, module_id: str, handler: ModuleHandler) -> None:
        if module_id not in EXPECTED_PIPELINE_IDS:
            raise ValueError(f"ID de módulo desconocido: {module_id}")
        self._handlers[module_id] = handler

    def run(
        self,
        raw_input: Mapping[str, Any],
        manifest: Mapping[str, Any],
        *,
        initial_canonical: Mapping[str, Any] | None = None,
        stop_on_failure: bool = False,
    ) -> OrchestrationRun:
        modules = validate_pipeline_manifest(manifest)
        mode = str(raw_input.get("mode") or manifest.get("mode") or "FULL")

        canonical: dict[str, Any] = deepcopy(dict(initial_canonical or {}))
        ownership: dict[str, str] = {
            key: "__INITIAL__" for key in canonical
        }
        results: dict[str, ModuleResult] = {}

        for spec in modules:
            module_id = str(spec["id"])
            module_name = str(spec["name"])
            handler = self._handlers.get(module_id)

            if handler is None:
                results[module_id] = not_evaluable_result(
                    module_id,
                    "No existe todavía un handler ejecutable registrado para esta etapa.",
                )
                continue

            context = ModuleContext(
                module_id=module_id,
                module_name=module_name,
                mode=mode,
                raw_input=deepcopy(dict(raw_input)),
                canonical_snapshot=deepcopy(canonical),
                prior_results=dict(results),
            )

            try:
                result = handler(context)
                self._validate_result(module_id, result)
                self._apply_updates(
                    module_id,
                    result,
                    canonical=canonical,
                    ownership=ownership,
                )
                results[module_id] = result
            except Exception as exc:
                if stop_on_failure:
                    raise
                results[module_id] = ModuleResult(
                    module_id=module_id,
                    status=ExecutionStatus.FAILED,
                    diagnostics=(f"{type(exc).__name__}: {exc}",),
                )

        return OrchestrationRun(
            mode=mode,
            canonical=canonical,
            results=results,
            ownership=ownership,
        )

    @staticmethod
    def _validate_result(module_id: str, result: ModuleResult) -> None:
        if not isinstance(result, ModuleResult):
            raise TypeError(
                f"{module_id}: el handler debe devolver ModuleResult."
            )
        if result.module_id != module_id:
            raise ValueError(
                f"{module_id}: el resultado declara module_id={result.module_id}."
            )
        if (
            result.status is not ExecutionStatus.COMPLETED
            and result.canonical_updates
        ):
            raise ValueError(
                f"{module_id}: sólo COMPLETED puede escribir estado canónico."
            )

    @staticmethod
    def _apply_updates(
        module_id: str,
        result: ModuleResult,
        *,
        canonical: dict[str, Any],
        ownership: dict[str, str],
    ) -> None:
        if result.status is not ExecutionStatus.COMPLETED:
            return

        for namespace, value in result.canonical_updates.items():
            if not isinstance(namespace, str) or not namespace:
                raise ValueError(
                    f"{module_id}: namespace canónico inválido: {namespace!r}"
                )

            previous_owner = ownership.get(namespace)
            if previous_owner is not None and previous_owner != module_id:
                raise CanonicalOverwriteError(
                    f"{module_id} no puede sobrescribir '{namespace}', "
                    f"propiedad de {previous_owner}."
                )

            canonical[namespace] = deepcopy(value)
            ownership[namespace] = module_id
