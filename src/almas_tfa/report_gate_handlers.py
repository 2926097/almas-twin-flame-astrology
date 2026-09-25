from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult


CANONICAL_REQUIRED = {
    "schema_version",
    "analysis_mode",
    "evidence",
    "models",
    "coverage",
    "robustness",
    "counterevidence",
}

ALLOWED_ANALYSIS_MODES = {"FULL", "TARGETED", "TEMPORAL", "REPORT"}
MODEL_IDS = {"AF", "KA", "AG", "LG"}
MODEL_STATES = {
    "SUPPORTED",
    "COMPATIBLE",
    "INSUFFICIENT",
    "CONTRADICTED",
    "NOT_EVALUABLE",
}


def _fingerprint(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _number_0_100(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and 0.0 <= float(value) <= 100.0
    )


def _semantic_checks(
    canonical: Mapping[str, Any],
) -> tuple[list[str], list[str]]:
    """Devuelve (blocking_issues, degradation_reasons)."""

    blocking: list[str] = []
    degraded: list[str] = []

    if canonical.get("schema_version") != "1.0.0":
        blocking.append("UNSUPPORTED_CANONICAL_SCHEMA_VERSION")

    mode = canonical.get("analysis_mode")
    if mode not in ALLOWED_ANALYSIS_MODES:
        blocking.append("INVALID_ANALYSIS_MODE")

    evidence = canonical.get("evidence")
    models = canonical.get("models")
    coverage = canonical.get("coverage")
    robustness = canonical.get("robustness")
    counterevidence = canonical.get("counterevidence")

    if not isinstance(evidence, list):
        blocking.append("EVIDENCE_MUST_BE_ARRAY")
        evidence = []
    if not isinstance(models, Mapping):
        blocking.append("MODELS_MUST_BE_OBJECT")
        models = {}
    if not isinstance(coverage, Mapping):
        blocking.append("COVERAGE_MUST_BE_OBJECT")
        coverage = {}
    if not isinstance(robustness, Mapping):
        blocking.append("ROBUSTNESS_MUST_BE_OBJECT")
        robustness = {}
    if not isinstance(counterevidence, list):
        blocking.append("COUNTEREVIDENCE_MUST_BE_ARRAY")

    if mode == "FULL":
        missing_models = sorted(MODEL_IDS - set(models))
        if missing_models:
            blocking.append(
                "FULL_MISSING_MODELS:" + ",".join(missing_models)
            )

    positive_model_claim = False
    for model_id, raw_model in models.items():
        if model_id not in MODEL_IDS:
            degraded.append(f"UNKNOWN_MODEL_NAMESPACE:{model_id}")
            continue
        if not isinstance(raw_model, Mapping):
            blocking.append(f"{model_id}:MODEL_MUST_BE_OBJECT")
            continue

        state = raw_model.get("state")
        iem = raw_model.get("iem")
        if state not in MODEL_STATES:
            blocking.append(f"{model_id}:INVALID_MODEL_STATE")
            continue

        if iem is not None and not _number_0_100(iem):
            blocking.append(f"{model_id}:IEM_OUT_OF_RANGE")

        if state == "NOT_EVALUABLE" and iem is not None:
            blocking.append(f"{model_id}:NOT_EVALUABLE_WITH_NUMERIC_IEM")
        if state != "NOT_EVALUABLE" and iem is None:
            blocking.append(f"{model_id}:EVALUATED_STATE_WITHOUT_IEM")

        if state in {"SUPPORTED", "COMPATIBLE"}:
            positive_model_claim = True

    if positive_model_claim and not evidence:
        blocking.append("POSITIVE_MODEL_CLAIM_WITHOUT_EVIDENCE")

    if mode == "FULL":
        icc = coverage.get("ICC")
        if icc is None:
            degraded.append("FULL_COVERAGE_ICC_NOT_DECLARED")
        elif not _number_0_100(icc):
            blocking.append("COVERAGE_ICC_OUT_OF_RANGE")

        irc = robustness.get("IRC")
        if irc is None:
            degraded.append("FULL_ROBUSTNESS_IRC_NOT_DECLARED")
        elif not _number_0_100(irc):
            blocking.append("ROBUSTNESS_IRC_OUT_OF_RANGE")

        indices = canonical.get("indices")
        if not isinstance(indices, Mapping):
            degraded.append("FULL_INDICES_NOT_DECLARED")

    if mode in {"TARGETED", "TEMPORAL"}:
        degraded.append(f"PARTIAL_ANALYSIS_MODE:{mode}")

    return sorted(set(blocking)), sorted(set(degraded))


def _execution_trace(
    prior_results: Mapping[str, Any],
) -> dict[str, Any]:
    failed: list[str] = []
    not_evaluable: list[str] = []
    skipped: list[str] = []
    not_applicable: list[str] = []
    completed: list[str] = []

    for module_id, result in prior_results.items():
        status = getattr(result, "status", None)
        if status is ExecutionStatus.FAILED:
            failed.append(module_id)
        elif status is ExecutionStatus.NOT_EVALUABLE:
            not_evaluable.append(module_id)
        elif status is ExecutionStatus.SKIPPED:
            skipped.append(module_id)
        elif status is ExecutionStatus.NOT_APPLICABLE:
            not_applicable.append(module_id)
        elif status is ExecutionStatus.COMPLETED:
            completed.append(module_id)

    available = bool(prior_results)
    return {
        "state": "AVAILABLE" if available else "UNAVAILABLE",
        "completed_modules": sorted(completed),
        "failed_modules": sorted(failed),
        "not_evaluable_modules": sorted(not_evaluable),
        "skipped_modules": sorted(skipped),
        "not_applicable_modules": sorted(not_applicable),
    }


def m30_report_gate(context: ModuleContext) -> ModuleResult:
    """M30: gate reproducible de integridad canónica y reportabilidad."""

    raw_canonical = context.raw_input.get("canonical_analysis")
    snapshot_canonical = context.canonical_snapshot.get("canonical_analysis")

    raw_present = isinstance(raw_canonical, Mapping)
    snapshot_present = isinstance(snapshot_canonical, Mapping)

    source_conflict = False
    if raw_present and snapshot_present:
        source_conflict = dict(raw_canonical) != dict(snapshot_canonical)

    if source_conflict:
        output = {
            "gate_version": "1.0.0",
            "state": "BLOCKED",
            "reportable": False,
            "source": "CONFLICT",
            "canonical_fingerprint": None,
            "canonical_schema_checked": False,
            "canonical_source_conflict": True,
            "analysis_mode": None,
            "missing_fields": [],
            "blocking_issues": ["RAW_AND_SNAPSHOT_CANONICAL_DIVERGE"],
            "degradation_reasons": [],
            "execution_trace_state": (
                "AVAILABLE" if context.prior_results else "UNAVAILABLE"
            ),
            "completed_modules": [],
            "failed_modules": [],
            "not_evaluable_modules": [],
            "skipped_modules": [],
            "not_applicable_modules": [],
            "canonical_values_mutated": False,
        }
        return ModuleResult(
            module_id="M30",
            status=ExecutionStatus.COMPLETED,
            payload=output,
            canonical_updates={"report_gate": output},
            limitations=(
                "M30 no elige entre dos canonical_analysis divergentes.",
            ),
        )

    if snapshot_present:
        canonical_analysis = snapshot_canonical
        source = "CANONICAL_SNAPSHOT"
    elif raw_present:
        canonical_analysis = raw_canonical
        source = "RAW_INPUT"
    else:
        trace = _execution_trace(context.prior_results)
        output = {
            "gate_version": "1.0.0",
            "state": "BLOCKED",
            "reportable": False,
            "source": None,
            "canonical_fingerprint": None,
            "canonical_schema_checked": False,
            "canonical_source_conflict": False,
            "analysis_mode": None,
            "missing_fields": sorted(CANONICAL_REQUIRED),
            "blocking_issues": ["CANONICAL_ANALYSIS_ABSENT"],
            "degradation_reasons": [],
            "execution_trace_state": trace["state"],
            "completed_modules": trace["completed_modules"],
            "failed_modules": trace["failed_modules"],
            "not_evaluable_modules": trace["not_evaluable_modules"],
            "skipped_modules": trace["skipped_modules"],
            "not_applicable_modules": trace["not_applicable_modules"],
            "canonical_values_mutated": False,
        }
        return ModuleResult(
            module_id="M30",
            status=ExecutionStatus.COMPLETED,
            payload=output,
            canonical_updates={"report_gate": output},
        )

    canonical_copy = deepcopy(dict(canonical_analysis))
    missing = sorted(CANONICAL_REQUIRED - set(canonical_copy))
    blocking_issues: list[str] = []
    degradation_reasons: list[str] = []

    if missing:
        blocking_issues.append("CANONICAL_REQUIRED_FIELDS_MISSING")
    else:
        semantic_blocking, semantic_degraded = _semantic_checks(canonical_copy)
        blocking_issues.extend(semantic_blocking)
        degradation_reasons.extend(semantic_degraded)

    trace = _execution_trace(context.prior_results)
    if trace["failed_modules"]:
        blocking_issues.append("FAILED_PRIOR_MODULES")

    if trace["state"] == "UNAVAILABLE":
        degradation_reasons.append("EXECUTION_TRACE_UNAVAILABLE")
    else:
        if trace["not_evaluable_modules"]:
            degradation_reasons.append("PRIOR_MODULES_NOT_EVALUABLE")
        if trace["skipped_modules"]:
            degradation_reasons.append("PRIOR_MODULES_SKIPPED")

    mode = canonical_copy.get("analysis_mode")
    blocking_issues = sorted(set(blocking_issues))
    degradation_reasons = sorted(set(degradation_reasons))

    if blocking_issues:
        state = "BLOCKED"
        reportable = False
    elif degradation_reasons:
        state = "PARTIAL"
        reportable = True
    else:
        state = "READY"
        reportable = True

    output = {
        "gate_version": "1.0.0",
        "state": state,
        "reportable": reportable,
        "source": source,
        "canonical_fingerprint": _fingerprint(canonical_copy),
        "canonical_schema_checked": True,
        "canonical_source_conflict": False,
        "analysis_mode": mode,
        "missing_fields": missing,
        "blocking_issues": blocking_issues,
        "degradation_reasons": degradation_reasons,
        "execution_trace_state": trace["state"],
        "completed_modules": trace["completed_modules"],
        "failed_modules": trace["failed_modules"],
        "not_evaluable_modules": trace["not_evaluable_modules"],
        "skipped_modules": trace["skipped_modules"],
        "not_applicable_modules": trace["not_applicable_modules"],
        "canonical_values_mutated": False,
    }

    updates: dict[str, Any] = {"report_gate": output}
    if source == "RAW_INPUT":
        updates["canonical_analysis"] = canonical_copy

    return ModuleResult(
        module_id="M30",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates=updates,
        limitations=(
            "M30 valida coherencia y procedencia; no corrige ni reinterpreta valores canónicos.",
            "NOT_EVALUABLE o SKIPPED degradan a PARTIAL; FAILED bloquea.",
            "Una traza de ejecución ausente no invalida el objeto importado, pero impide READY.",
        ),
    )
