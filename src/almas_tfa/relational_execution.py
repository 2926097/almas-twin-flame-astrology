from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

from .handlers import configured_handlers
from .orchestrator import Orchestrator
from .relational_request_pipeline import (
    assess_relational_work_request,
    prepare_relational_raw_input,
)


EXECUTION_ID = "ALMAS_PRIVATE_RELATIONAL_RUNNER_V1"


class RelationalExecutionError(RuntimeError):
    pass


def _json_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def execute_relational_work_request(
    work_request: Mapping[str, Any],
    manifest: Mapping[str, Any],
    *,
    astrology_backend: Any,
    davison_backend: Any | None = None,
    stop_on_failure: bool = False,
) -> dict[str, Any]:
    """Ejecuta una solicitud relacional preparada sin publicar el caso.

    Esta función no crea un canonical alternativo. Sólo devuelve
    canonical_analysis cuando M30 lo ha materializado dentro del pipeline.
    """

    if astrology_backend is None:
        raise RelationalExecutionError(
            "astrology_backend es obligatorio."
        )
    if davison_backend is None:
        davison_backend = astrology_backend

    assessment = assess_relational_work_request(work_request)
    raw_input = prepare_relational_raw_input(work_request)

    handlers = configured_handlers(
        astrology_backend=astrology_backend,
        davison_backend=davison_backend,
    )
    run = Orchestrator(handlers).run(
        raw_input,
        manifest,
        stop_on_failure=stop_on_failure,
    )
    run_dict = run.to_dict()

    module_statuses = {
        module_id: result.status.value
        for module_id, result in run.results.items()
    }
    failed_modules = sorted(
        module_id
        for module_id, status in module_statuses.items()
        if status == "FAILED"
    )
    not_evaluable_modules = sorted(
        module_id
        for module_id, status in module_statuses.items()
        if status == "NOT_EVALUABLE"
    )

    canonical = run.canonical.get("canonical_analysis")
    canonical_analysis = (
        deepcopy(dict(canonical))
        if isinstance(canonical, Mapping)
        else None
    )

    gate = run.canonical.get("report_gate")
    gate_obj = dict(gate) if isinstance(gate, Mapping) else {}
    backend_provenance = getattr(astrology_backend, "provenance", None)
    if not isinstance(backend_provenance, Mapping):
        backend_provenance = {
            "backend_id": getattr(astrology_backend, "backend_id", None),
            "backend_version": getattr(
                astrology_backend,
                "backend_version",
                None,
            ),
        }

    receipt = {
        "execution_id": EXECUTION_ID,
        "request_sha256": _json_sha256(work_request),
        "analysis_profile": assessment["profile_id"],
        "analysis_mode": assessment["analysis_mode"],
        "analysis_policy_profile": assessment.get(
            "analysis_policy_profile"
        ),
        "analysis_policy_fingerprint": assessment.get(
            "analysis_policy_fingerprint"
        ),
        "policy_source": assessment.get("policy_source"),
        "backend_provenance": deepcopy(dict(backend_provenance)),
        "module_statuses": module_statuses,
        "failed_modules": failed_modules,
        "not_evaluable_modules": not_evaluable_modules,
        "report_gate_state": gate_obj.get("state"),
        "canonical_fingerprint": gate_obj.get(
            "canonical_fingerprint"
        ),
        "canonical_analysis_available": canonical_analysis is not None,
        "canonical_reconstructed_outside_pipeline": False,
        "network_io_requested_by_runner": False,
        "case_published_by_runner": False,
    }

    return {
        "assessment": deepcopy(assessment),
        "raw_input": deepcopy(raw_input),
        "orchestration_run": run_dict,
        "canonical_analysis": canonical_analysis,
        "execution_receipt": receipt,
    }
