from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult
from .canonical_assembly import assemble_canonical_analysis, load_canonical_assembly_policy


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


ONTOLOGICAL_IDENTIFIABILITY_STATES = {
    "IDENTIFIABLE",
    "PARTIALLY_IDENTIFIABLE",
    "NON_IDENTIFIABLE",
    "NOT_EVALUABLE",
}
ONTOLOGICAL_EPISTEMIC_STATES = {
    "SUPPORTED",
    "COMPATIBLE",
    "INSUFFICIENT",
    "CONTRADICTED",
    "NOT_EVALUABLE",
}
SHARED_ORIGIN_MODELS = {
    "MONADIC_ORIGIN",
    "SPLIT_SOUL",
    "TWIN_FLAME_MODEL",
}


def _ontological_semantic_checks(
    raw: Any,
) -> tuple[list[str], list[str]]:
    blocking: list[str] = []
    degraded: list[str] = []

    if not isinstance(raw, Mapping):
        return ["ONTOLOGICAL_DISCRIMINATION_MUST_BE_OBJECT"], degraded

    required = {
        "schema_version",
        "candidate_models",
        "confirmed_exclusions",
        "surviving_models",
        "identifiability_state",
        "epistemic_state",
        "classification",
        "promotion_trace",
        "false_specificity_guard",
    }
    missing = sorted(required - set(raw))
    if missing:
        blocking.append(
            "ONTOLOGICAL_DISCRIMINATION_MISSING:" + ",".join(missing)
        )
        return blocking, degraded

    if raw.get("schema_version") != "1.0.0":
        blocking.append("ONTOLOGICAL_DISCRIMINATION_SCHEMA_UNSUPPORTED")

    candidates = raw.get("candidate_models")
    survivors = raw.get("surviving_models")
    exclusions = raw.get("confirmed_exclusions")

    def valid_model_list(value: Any, *, minimum: int = 0) -> bool:
        return (
            isinstance(value, list)
            and len(value) >= minimum
            and len(value) == len(set(value))
            and all(isinstance(item, str) and item for item in value)
        )

    if not valid_model_list(candidates, minimum=2):
        blocking.append("ONTOLOGY_CANDIDATE_MODELS_INVALID")
        return blocking, degraded
    if not valid_model_list(survivors):
        blocking.append("ONTOLOGY_SURVIVING_MODELS_INVALID")
        return blocking, degraded
    if not valid_model_list(exclusions):
        blocking.append("ONTOLOGY_CONFIRMED_EXCLUSIONS_INVALID")
        return blocking, degraded

    candidate_set = set(candidates)
    survivor_set = set(survivors)
    exclusion_set = set(exclusions)

    if not survivor_set.issubset(candidate_set):
        blocking.append("ONTOLOGY_SURVIVOR_OUTSIDE_CANDIDATES")
    if not exclusion_set.issubset(candidate_set):
        blocking.append("ONTOLOGY_EXCLUSION_OUTSIDE_CANDIDATES")
    if survivor_set & exclusion_set:
        blocking.append("ONTOLOGY_SURVIVOR_EXCLUSION_OVERLAP")
    if survivor_set != candidate_set - exclusion_set:
        blocking.append("ONTOLOGY_SURVIVOR_PARTITION_INCONSISTENT")

    identifiability = raw.get("identifiability_state")
    if identifiability not in ONTOLOGICAL_IDENTIFIABILITY_STATES:
        blocking.append("ONTOLOGY_IDENTIFIABILITY_STATE_INVALID")

    epistemic = raw.get("epistemic_state")
    if epistemic not in ONTOLOGICAL_EPISTEMIC_STATES:
        blocking.append("ONTOLOGY_EPISTEMIC_STATE_INVALID")

    if identifiability == "IDENTIFIABLE" and len(survivors) != 1:
        blocking.append("ONTOLOGY_IDENTIFIABLE_WITHOUT_SINGLE_SURVIVOR")
    if (
        identifiability == "PARTIALLY_IDENTIFIABLE"
        and not (1 < len(survivors) < len(candidates))
    ):
        blocking.append("ONTOLOGY_PARTIAL_IDENTIFIABILITY_INCONSISTENT")
    if identifiability == "NOT_EVALUABLE" and epistemic != "NOT_EVALUABLE":
        blocking.append("ONTOLOGY_NOT_EVALUABLE_STATE_MISMATCH")

    classification = raw.get("classification")
    if len(survivors) == 1:
        expected_classification = survivors[0]
    elif (
        len(survivors) >= 2
        and survivor_set
        and survivor_set.issubset(SHARED_ORIGIN_MODELS)
    ):
        expected_classification = "SHARED_ORIGIN_UNDIFFERENTIATED"
    else:
        expected_classification = "INDETERMINATE"

    if classification != expected_classification:
        blocking.append("ONTOLOGY_CLASSIFICATION_INCONSISTENT")

    if raw.get("false_specificity_guard") is not True:
        blocking.append("ONTOLOGY_FALSE_SPECIFICITY_GUARD_FAILED")

    promotion_trace = raw.get("promotion_trace")
    if not isinstance(promotion_trace, list):
        blocking.append("ONTOLOGY_PROMOTION_TRACE_MUST_BE_ARRAY")
    else:
        seen_trace: set[tuple[str, str, str, tuple[str, str]]] = set()
        for index, item in enumerate(promotion_trace):
            if not isinstance(item, Mapping):
                blocking.append(f"ONTOLOGY_PROMOTION_TRACE_ITEM_INVALID:{index}")
                continue
            discriminator_id = item.get("discriminator_id")
            promotion_ref = item.get("promotion_ref")
            root_key = item.get("root_key")
            pair = item.get("pair")
            if not all(
                isinstance(value, str) and value
                for value in (discriminator_id, promotion_ref, root_key)
            ):
                blocking.append(
                    f"ONTOLOGY_PROMOTION_TRACE_FIELDS_INVALID:{index}"
                )
                continue
            if (
                not isinstance(pair, list)
                or len(pair) != 2
                or pair[0] == pair[1]
                or not all(isinstance(model, str) and model for model in pair)
                or not set(pair).issubset(candidate_set)
            ):
                blocking.append(
                    f"ONTOLOGY_PROMOTION_TRACE_PAIR_INVALID:{index}"
                )
                continue
            key = (
                discriminator_id,
                promotion_ref,
                root_key,
                tuple(sorted((pair[0], pair[1]))),
            )
            if key in seen_trace:
                blocking.append(
                    f"ONTOLOGY_PROMOTION_TRACE_DUPLICATE:{index}"
                )
            seen_trace.add(key)

    return sorted(set(blocking)), degraded


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

    if "ontological_discrimination" in canonical:
        ontology_blocking, ontology_degraded = _ontological_semantic_checks(
            canonical.get("ontological_discrimination")
        )
        blocking.extend(ontology_blocking)
        degraded.extend(ontology_degraded)

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



def make_m30_report_gate_auto():
    """Construye M30 con ensamblaje canónico Q7 y compatibilidad legacy.

    Un canonical_analysis ya suministrado conserva prioridad y nunca se
    sobrescribe. Sólo cuando raw/snapshot carecen de canonical se ensambla uno
    desde los namespaces canónicos M01-M29.
    """

    def m30_auto(context: ModuleContext) -> ModuleResult:
        raw_canonical = context.raw_input.get("canonical_analysis")
        snapshot_canonical = context.canonical_snapshot.get("canonical_analysis")
        if isinstance(raw_canonical, Mapping) or isinstance(
            snapshot_canonical,
            Mapping,
        ):
            return m30_report_gate(context)

        assembled = assemble_canonical_analysis(
            context.canonical_snapshot,
            context.prior_results,
            policy=load_canonical_assembly_policy(),
        )
        if assembled.get("state") != "EVALUABLE":
            # Mantiene el comportamiento bloqueante histórico cuando Q7 no
            # puede construir una verdad canónica suficiente.
            result = m30_report_gate(context)
            return ModuleResult(
                module_id="M30",
                status=result.status,
                payload=result.payload,
                canonical_updates=result.canonical_updates,
                evidence_refs=result.evidence_refs,
                limitations=result.limitations
                + (
                    "Q7 canonical assembly no evaluable: "
                    + str(assembled.get("reason")),
                ),
                diagnostics=result.diagnostics
                + ("M30 source=LEGACY_GATE_NO_AUTO_CANONICAL",),
            )

        canonical_analysis = assembled["canonical_analysis"]
        snapshot = dict(context.canonical_snapshot)
        snapshot["canonical_analysis"] = canonical_analysis
        derived_context = ModuleContext(
            module_id=context.module_id,
            module_name=context.module_name,
            mode=context.mode,
            raw_input=context.raw_input,
            canonical_snapshot=snapshot,
            prior_results=context.prior_results,
        )
        result = m30_report_gate(derived_context)

        updates = dict(result.canonical_updates)
        updates["canonical_analysis"] = canonical_analysis

        return ModuleResult(
            module_id="M30",
            status=result.status,
            payload=result.payload,
            canonical_updates=updates,
            evidence_refs=result.evidence_refs,
            limitations=result.limitations
            + (
                "canonical_analysis fue ensamblado por Q7 desde namespaces M01-M29; M30 no recalculó astrología, raíces ni pilares.",
            ),
            diagnostics=result.diagnostics
            + (
                "M30 source=AUTO_CANONICAL_ASSEMBLY_Q7",
                "canonical_assembly_policy=ALMAS_CANONICAL_ASSEMBLY_V1",
            ),
        )

    return m30_auto
