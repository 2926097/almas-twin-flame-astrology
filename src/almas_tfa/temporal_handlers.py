from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


TEMPORAL_FAMILIES = {
    "TPROG",
    "TDIR",
    "TTRANSIT",
    "TECLIPSE",
    "TREL",
    "TATACIR",
}

ACTIVATION_COEFFICIENTS = {
    "DIRECT_REPETITION": 1.00,
    "RELATIONAL_ROOT_ACTIVATION": 0.90,
    "ENDPOINT_ACTIVATION": 0.70,
    "UNANCHORED": 0.0,
}

WINDOW_STATUSES = {
    "RETROSPECTIVE_CONFIRMED",
    "RETROSPECTIVE_UNCONFIRMED",
    "CURRENT_ACTIVE",
    "PROSPECTIVE_ACTIVATION",
    "EXPLORATORY",
    "UNANCHORED",
}


def _nonnegative_weight(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} debe ser numérico.")
    value = float(value)
    if value < 0.0:
        raise ValueError(f"{label} no puede ser negativo.")
    return value


def _signal_traceability(raw: Mapping[str, Any], signal_id: str) -> tuple[bool, list[str]]:
    missing: list[str] = []

    structural_family = raw.get("structural_family")
    if not isinstance(structural_family, str) or not structural_family:
        missing.append("structural_family")

    exactitude_orb = raw.get("exactitude_orb")
    if (
        isinstance(exactitude_orb, bool)
        or not isinstance(exactitude_orb, (int, float))
        or float(exactitude_orb) < 0.0
    ):
        missing.append("exactitude_orb")

    rule = raw.get("preregistered_window_rule")
    if not isinstance(rule, str) or not rule:
        missing.append("preregistered_window_rule")

    return not missing, missing


def _calculate_iat(
    selected: list[dict[str, Any]],
    policy: Mapping[str, Any] | None,
) -> tuple[float | None, str, bool, dict[str, Any] | None, list[str]]:
    """Agrega señales independientes sólo bajo pesos preregistrados."""

    eligible = [
        item
        for item in selected
        if item["iat_eligible"]
    ]
    eligible_ids = [item["signal_id"] for item in eligible]

    if not eligible:
        return None, "NOT_CALCULATED", False, None, eligible_ids

    if policy is None:
        return None, "NOT_CALCULATED", False, None, eligible_ids

    preregistration_ref = policy.get("preregistration_ref")
    if not isinstance(preregistration_ref, str) or not preregistration_ref:
        raise ValueError(
            "iat_aggregation_policy.preregistration_ref es obligatorio."
        )

    if policy.get("formula") != "WEIGHTED_MEAN_EFFECTIVE_STRENGTH":
        raise ValueError(
            "M26 sólo admite formula=WEIGHTED_MEAN_EFFECTIVE_STRENGTH."
        )

    window_scope_ref = policy.get("window_scope_ref")
    if not isinstance(window_scope_ref, str) or not window_scope_ref:
        raise ValueError(
            "iat_aggregation_policy.window_scope_ref es obligatorio."
        )

    family_weights = policy.get("family_weights")
    root_weights = policy.get("root_weights")
    if not isinstance(family_weights, Mapping) or not isinstance(root_weights, Mapping):
        raise ValueError(
            "iat_aggregation_policy debe declarar family_weights y root_weights."
        )

    weighted_sum = 0.0
    total_weight = 0.0
    applied: list[dict[str, Any]] = []

    for signal in eligible:
        family = signal["temporal_family"]
        root_id = signal["root_id"]

        if family not in family_weights:
            raise ValueError(
                f"Falta peso preregistrado para la familia temporal {family}."
            )
        if root_id not in root_weights:
            raise ValueError(
                f"Falta peso preregistrado para la raíz {root_id}."
            )

        family_weight = _nonnegative_weight(
            family_weights[family],
            f"family_weights[{family}]",
        )
        root_weight = _nonnegative_weight(
            root_weights[root_id],
            f"root_weights[{root_id}]",
        )
        combined_weight = family_weight * root_weight

        weighted_sum += combined_weight * signal["effective_strength"]
        total_weight += combined_weight
        applied.append(
            {
                "signal_id": signal["signal_id"],
                "root_id": root_id,
                "temporal_family": family,
                "family_weight": family_weight,
                "root_weight": root_weight,
                "combined_weight": combined_weight,
                "effective_strength": signal["effective_strength"],
            }
        )

    if total_weight <= 0.0:
        raise ValueError(
            "La suma de pesos combinados del IAT debe ser mayor que cero."
        )

    iat = 100.0 * weighted_sum / total_weight
    policy_output = {
        "preregistration_ref": preregistration_ref,
        "window_scope_ref": window_scope_ref,
        "formula": "WEIGHTED_MEAN_EFFECTIVE_STRENGTH",
        "family_weights": {
            str(k): float(v) for k, v in family_weights.items()
        },
        "root_weights": {
            str(k): float(v) for k, v in root_weights.items()
        },
        "applied_signal_weights": applied,
    }

    return iat, "CALCULATED", True, policy_output, eligible_ids


def m26_temporal_activation(context: ModuleContext) -> ModuleResult:
    """M26: normaliza activaciones ancladas y calcula IAT sólo con pesos preregistrados."""

    signals = context.raw_input.get("temporal_signals")
    if not isinstance(signals, list) or not signals:
        return not_evaluable_result(
            "M26",
            "Faltan temporal_signals preregistradas.",
        )

    roots_obj = context.canonical_snapshot.get("independent_roots")
    roots = roots_obj.get("roots") if isinstance(roots_obj, Mapping) else None
    known_roots = {
        str(root.get("root_id"))
        for root in roots or []
        if isinstance(root, Mapping) and root.get("root_id")
    }

    normalized: list[dict[str, Any]] = []
    seen_signal_ids: set[str] = set()

    for index, raw in enumerate(signals, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError("Cada temporal_signal debe ser un objeto.")

        signal_id = str(raw.get("signal_id") or f"TEMP_{index:04d}")
        if signal_id in seen_signal_ids:
            raise ValueError(f"signal_id duplicado: {signal_id}")
        seen_signal_ids.add(signal_id)

        family = raw.get("temporal_family")
        if family not in TEMPORAL_FAMILIES:
            raise ValueError(
                f"{signal_id}: temporal_family desconocida: {family}."
            )

        strength = float(raw.get("strength", -1))
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"{signal_id}: strength debe estar en [0,1].")

        root_id = raw.get("root_id")
        root_id = str(root_id) if root_id is not None else None
        anchored = bool(root_id and root_id in known_roots)

        activation_class = raw.get("activation_class")
        if not anchored:
            activation_class = "UNANCHORED"
        if activation_class not in ACTIVATION_COEFFICIENTS:
            raise ValueError(
                f"{signal_id}: activation_class inválida: {activation_class}."
            )

        status = raw.get("window_status")
        if status not in WINDOW_STATUSES:
            raise ValueError(
                f"{signal_id}: window_status inválido: {status}."
            )

        preregistered = bool(raw.get("preregistered", False))
        if family == "TATACIR" and not preregistered:
            status = "EXPLORATORY"

        if not anchored:
            status = "UNANCHORED"

        traceability_complete, missing_traceability = _signal_traceability(
            raw,
            signal_id,
        )

        k = ACTIVATION_COEFFICIENTS[activation_class]
        effective_strength = strength * k

        iat_eligible = (
            anchored
            and preregistered
            and traceability_complete
            and status not in {"EXPLORATORY", "UNANCHORED"}
            and effective_strength > 0.0
        )

        normalized.append(
            {
                "signal_id": signal_id,
                "root_id": root_id,
                "anchored": anchored,
                "clause_id": raw.get("clause_id"),
                "structural_family": raw.get("structural_family"),
                "temporal_family": family,
                "activation_class": activation_class,
                "k": k,
                "strength": strength,
                "effective_strength": effective_strength,
                "exactitude_orb": raw.get("exactitude_orb"),
                "preregistered_window_rule": raw.get(
                    "preregistered_window_rule"
                ),
                "preregistered": preregistered,
                "window_status": status,
                "date_or_period": raw.get("date_or_period"),
                "event_refs": list(raw.get("event_refs", [])),
                "traceability_complete": traceability_complete,
                "missing_traceability": missing_traceability,
                "iat_eligible": iat_eligible,
                "creates_structural_root": False,
                "predicts_real_world_event": False,
            }
        )

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in normalized:
        root_key = signal["root_id"] or "UNANCHORED"
        key = f"{root_key}|{signal['temporal_family']}"
        groups[key].append(signal)

    selected: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    for key in sorted(groups):
        members = groups[key]
        members.sort(
            key=lambda item: (
                -item["effective_strength"],
                item["signal_id"],
            )
        )
        winner = dict(members[0])
        selected.append(winner)
        for item in members[1:]:
            duplicate = dict(item)
            duplicate["suppressed_by"] = winner["signal_id"]
            duplicate["suppression_reason"] = "SAME_ROOT_AND_TEMPORAL_FAMILY"
            suppressed.append(duplicate)

    root_families: dict[str, set[str]] = defaultdict(set)
    root_signal_ids: dict[str, list[str]] = defaultdict(list)
    for signal in selected:
        if signal["iat_eligible"] and signal["root_id"]:
            root_families[signal["root_id"]].add(signal["temporal_family"])
            root_signal_ids[signal["root_id"]].append(signal["signal_id"])

    root_activation_summary = [
        {
            "root_id": root_id,
            "independent_temporal_families": sorted(families),
            "independent_family_count": len(families),
            "selected_signal_ids": sorted(root_signal_ids[root_id]),
            "recurring_across_independent_families": len(families) >= 2,
        }
        for root_id, families in sorted(root_families.items())
    ]

    aggregation_policy = context.raw_input.get("iat_aggregation_policy")
    if aggregation_policy is not None and not isinstance(
        aggregation_policy,
        Mapping,
    ):
        raise ValueError("iat_aggregation_policy debe ser un objeto.")

    iat, iat_state, weights_applied, policy_output, eligible_ids = _calculate_iat(
        selected,
        aggregation_policy,
    )

    output = {
        "signals": normalized,
        "selected_independent_signals": selected,
        "suppressed": suppressed,
        "root_activation_summary": root_activation_summary,
        "iat_eligible_signal_ids": eligible_ids,
        "iat": iat,
        "iat_state": iat_state,
        "iat_policy": policy_output,
        "aggregation_weights_applied": weights_applied,
        "structural_score_modified": False,
        "structural_roots_created": False,
        "real_world_event_prediction_made": False,
    }

    limitations = [
        "La temporalidad no modifica IEM ni crea raíces estructurales.",
        "Una ventana futura describe activación potencial de una raíz, no contacto, decisión, consentimiento, reunión o cierre.",
    ]
    if iat_state == "NOT_CALCULATED":
        limitations.append(
            "IAT no se calcula sin señales elegibles y una política de agregación preregistrada."
        )

    return ModuleResult(
        module_id="M26",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"temporal_activation": output},
        limitations=tuple(limitations),
    )


EVENT_TYPES = {
    "FIRST_MEETING","CONTACT","CONVERSATION","RELATIONSHIP_CHANGE",
    "COMMITMENT","SEPARATION","RECONCILIATION","NO_CONTACT","MARRIAGE",
    "BIRTH","DEATH","MOVE","TRAVEL","FAMILY_EVENT","WORK_OR_SERVICE",
    "HEALTH_EVENT","SPIRITUAL_EVENT","CONFLICT","BOUNDARY","OTHER",
}

DATE_PRECISIONS = {
    "EXACT_DATETIME","EXACT_DATE","MONTH","YEAR","RANGE","APPROXIMATE","UNKNOWN",
}

DOCUMENTARY_QUALITIES = {
    "DQ1_PRIMARY_DOCUMENT","DQ2_DIRECT_SELF_REPORT","DQ3_CORROBORATED_REPORT",
    "DQ4_SECONDARY_REPORT","DQ5_UNVERIFIED",
}

PRIVACY_CLASSES = {
    "PUBLIC_VERIFIABLE","PRIVATE_AUTHORIZED","PRIVATE_RESTRICTED","SYNTHETIC",
}

EVIDENCE_ROLES = {
    "ACTIVATION_CORROBORATION","FULFILLMENT_EVIDENCE","COUNTEREVIDENCE",
    "VIABILITY_FACT","RECIPROCITY_FACT","PHENOMENOLOGY_DOCUMENT","CONTEXT_ONLY",
}


def m27_dated_events(context: ModuleContext) -> ModuleResult:
    """M27: valida el ledger documental sin modificar arquitectura congelada."""

    ledger = context.raw_input.get("documentary_event_ledger")
    if not isinstance(ledger, Mapping):
        return not_evaluable_result(
            "M27",
            "Falta documentary_event_ledger.",
        )

    if ledger.get("schema_version") != "1.0.0":
        raise ValueError("M27 requiere documentary_event_ledger schema_version=1.0.0.")

    freeze_ref = ledger.get("analysis_freeze_ref")
    if not isinstance(freeze_ref, str) or not freeze_ref:
        raise ValueError("analysis_freeze_ref es obligatorio.")

    events = ledger.get("events")
    if not isinstance(events, list):
        raise ValueError("events debe ser una lista.")

    roots_obj = context.canonical_snapshot.get("independent_roots")
    roots = roots_obj.get("roots") if isinstance(roots_obj, Mapping) else None
    known_roots = {
        str(root.get("root_id"))
        for root in roots or []
        if isinstance(root, Mapping) and root.get("root_id")
    }

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    unresolved_root_refs: list[dict[str, str]] = []

    for raw in events:
        if not isinstance(raw, Mapping):
            raise ValueError("Cada evento debe ser un objeto.")

        event_id = raw.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("Cada evento necesita event_id.")
        if event_id in seen:
            raise ValueError(f"event_id duplicado: {event_id}")

        supersedes = raw.get("supersedes_event_id")
        if supersedes is not None:
            if not isinstance(supersedes, str) or supersedes not in seen:
                raise ValueError(
                    f"{event_id}: supersedes_event_id debe referir un evento previo."
                )
            if not raw.get("correction_reason"):
                raise ValueError(
                    f"{event_id}: una corrección requiere correction_reason."
                )

        if raw.get("event_type") not in EVENT_TYPES:
            raise ValueError(f"{event_id}: event_type inválido.")
        if raw.get("date_precision") not in DATE_PRECISIONS:
            raise ValueError(f"{event_id}: date_precision inválida.")
        if raw.get("documentary_quality") not in DOCUMENTARY_QUALITIES:
            raise ValueError(f"{event_id}: documentary_quality inválida.")
        if raw.get("privacy_class") not in PRIVACY_CLASSES:
            raise ValueError(f"{event_id}: privacy_class inválida.")

        roles = raw.get("evidence_roles")
        if not isinstance(roles, list) or any(role not in EVIDENCE_ROLES for role in roles):
            raise ValueError(f"{event_id}: evidence_roles inválidos.")

        fact_statement = raw.get("fact_statement")
        if not isinstance(fact_statement, str) or not fact_statement.strip():
            raise ValueError(f"{event_id}: fact_statement es obligatorio.")

        linked_roots = [
            str(root_id) for root_id in raw.get("linked_root_refs", [])
        ]
        for root_id in linked_roots:
            if root_id not in known_roots:
                unresolved_root_refs.append(
                    {"event_id": event_id, "root_id": root_id}
                )

        item = dict(raw)
        item["linked_root_refs"] = linked_roots
        item["public_exportable"] = raw.get("privacy_class") in {
            "PUBLIC_VERIFIABLE",
            "SYNTHETIC",
        }
        item["creates_structural_root"] = False
        normalized.append(item)
        seen.add(event_id)

    role_counts: dict[str, int] = defaultdict(int)
    for event in normalized:
        for role in event["evidence_roles"]:
            role_counts[str(role)] += 1

    output = {
        "schema_version": "1.0.0",
        "analysis_freeze_ref": freeze_ref,
        "events": normalized,
        "event_count": len(normalized),
        "role_counts": dict(sorted(role_counts.items())),
        "unresolved_root_refs": unresolved_root_refs,
        "structural_mutation_allowed": False,
        "append_only_validated": True,
    }

    return ModuleResult(
        module_id="M27",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"documentary_events": output},
        limitations=(
            "Los eventos pueden corroborar activación, cumplimiento, viabilidad o reciprocidad; no crean retrospectivamente raíces o cláusulas.",
        ),
    )
