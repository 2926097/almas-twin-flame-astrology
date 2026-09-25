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


def m26_temporal_activation(context: ModuleContext) -> ModuleResult:
    """M26: normaliza activaciones temporales ancladas a raíces preexistentes."""

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
    for index, raw in enumerate(signals, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError("Cada temporal_signal debe ser un objeto.")

        signal_id = str(raw.get("signal_id") or f"TEMP_{index:04d}")
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

        k = ACTIVATION_COEFFICIENTS[activation_class]
        effective_strength = strength * k

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

    output = {
        "signals": normalized,
        "selected_independent_signals": selected,
        "suppressed": suppressed,
        "iat": None,
        "iat_state": "NOT_CALCULATED",
        "aggregation_weights_applied": False,
        "structural_score_modified": False,
    }

    return ModuleResult(
        module_id="M26",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"temporal_activation": output},
        limitations=(
            "M26 aplica anclaje, K y deduplicación temporal, pero no calcula IAT sin pesos de agregación preregistrados.",
            "La temporalidad no modifica IEM ni crea raíces estructurales.",
        ),
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
