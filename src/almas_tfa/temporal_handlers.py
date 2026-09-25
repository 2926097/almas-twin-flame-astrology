from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
import re
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


def _date_precision_contract(
    event_id: str,
    precision: str,
    raw_date: Any,
    raw_range: Any,
) -> tuple[bool, str | None]:
    """Valida presencia/formato mínimo sin inventar precisión temporal."""

    if precision == "UNKNOWN":
        return True, None

    if precision == "RANGE":
        if not isinstance(raw_range, str) or not raw_range.strip():
            return False, "date_range requerido para RANGE"
        return True, None

    if not isinstance(raw_date, str) or not raw_date.strip():
        return False, f"date requerido para {precision}"

    value = raw_date.strip()
    try:
        if precision == "EXACT_DATETIME":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif precision == "EXACT_DATE":
            date.fromisoformat(value)
        elif precision == "MONTH":
            if re.fullmatch(r"\d{4}-\d{2}", value) is None:
                raise ValueError
            month = int(value[-2:])
            if not 1 <= month <= 12:
                raise ValueError
        elif precision == "YEAR":
            if re.fullmatch(r"\d{4}", value) is None:
                raise ValueError
        elif precision == "APPROXIMATE":
            pass
        else:
            return False, f"date_precision no soportada: {precision}"
    except ValueError:
        return False, f"formato de date incompatible con {precision}"

    return True, None


def _known_clause_ids(canonical: Mapping[str, Any]) -> tuple[set[str], str]:
    """Recupera IDs de cláusula si la arquitectura contractual está disponible."""

    candidates: list[Any] = []

    direct = canonical.get("clause_assembly")
    if isinstance(direct, Mapping):
        candidates.append(direct.get("clauses"))

    reconstruction = canonical.get("preincarnation_reconstruction")
    if isinstance(reconstruction, Mapping):
        assembly = reconstruction.get("clause_assembly")
        if isinstance(assembly, Mapping):
            candidates.append(assembly.get("clauses"))
        candidates.append(reconstruction.get("clauses"))

    clauses_direct = canonical.get("clauses")
    candidates.append(clauses_direct)

    ids: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, list):
            continue
        for clause in candidate:
            if isinstance(clause, Mapping) and clause.get("id"):
                ids.add(str(clause["id"]))

    return ids, ("AVAILABLE" if ids else "NOT_AVAILABLE")


def _role_target_state(
    role: str,
    *,
    resolved_roots: list[str],
    unresolved_roots: list[str],
    resolved_clauses: list[str],
    unresolved_clauses: list[str],
    counterevidence_effect: Any,
    clause_registry_state: str,
) -> tuple[bool, str]:
    """Evalúa trazabilidad del destino del rol, no verdad metafísica."""

    if role == "ACTIVATION_CORROBORATION":
        if resolved_roots or resolved_clauses:
            return True, "RESOLVED_TARGET"
        if unresolved_roots or unresolved_clauses:
            return False, "UNRESOLVED_TARGET"
        return False, "MISSING_ROOT_OR_CLAUSE_TARGET"

    if role == "FULFILLMENT_EVIDENCE":
        if resolved_clauses:
            return True, "RESOLVED_CLAUSE_TARGET"
        if unresolved_clauses:
            return False, "UNRESOLVED_CLAUSE_TARGET"
        if clause_registry_state == "NOT_AVAILABLE":
            return False, "CLAUSE_REGISTRY_NOT_AVAILABLE"
        return False, "MISSING_CLAUSE_TARGET"

    if role == "COUNTEREVIDENCE":
        if resolved_roots or resolved_clauses:
            return True, "RESOLVED_TARGET"
        if isinstance(counterevidence_effect, str) and counterevidence_effect.strip():
            return True, "DECLARED_COUNTEREVIDENCE_EFFECT"
        if unresolved_roots or unresolved_clauses:
            return False, "UNRESOLVED_TARGET"
        return False, "MISSING_COUNTEREVIDENCE_TARGET"

    return True, "NO_STRUCTURAL_TARGET_REQUIRED"


def m27_dated_events(context: ModuleContext) -> ModuleResult:
    """M27: valida hechos documentales sin reescribir la estructura congelada."""

    ledger = context.raw_input.get("documentary_event_ledger")
    if not isinstance(ledger, Mapping):
        return not_evaluable_result(
            "M27",
            "Falta documentary_event_ledger.",
        )

    if ledger.get("schema_version") != "1.0.0":
        raise ValueError(
            "M27 requiere documentary_event_ledger schema_version=1.0.0."
        )

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
    root_registry_state = "AVAILABLE" if known_roots else "NOT_AVAILABLE"

    known_clauses, clause_registry_state = _known_clause_ids(
        context.canonical_snapshot
    )

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    unresolved_root_refs: list[dict[str, str]] = []
    unresolved_clause_refs: list[dict[str, str]] = []
    date_contract_issues: list[dict[str, str]] = []
    role_traceability_issues: list[dict[str, str]] = []
    documentary_quality_issues: list[dict[str, str]] = []

    for raw in events:
        if not isinstance(raw, Mapping):
            raise ValueError("Cada evento debe ser un objeto.")

        event_id = raw.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("Cada evento necesita event_id.")
        if event_id in seen:
            raise ValueError(f"event_id duplicado: {event_id}")

        subjects = raw.get("subjects")
        if (
            not isinstance(subjects, list)
            or not subjects
            or any(not isinstance(x, str) or not x for x in subjects)
        ):
            raise ValueError(f"{event_id}: subjects debe contener IDs válidos.")
        if len(set(subjects)) != len(subjects):
            raise ValueError(f"{event_id}: subjects contiene duplicados.")

        supersedes = raw.get("supersedes_event_id")
        is_correction = supersedes is not None
        if is_correction:
            if not isinstance(supersedes, str) or supersedes not in seen:
                raise ValueError(
                    f"{event_id}: supersedes_event_id debe referir un evento previo."
                )
            if not raw.get("correction_reason"):
                raise ValueError(
                    f"{event_id}: una corrección requiere correction_reason."
                )

        event_type = raw.get("event_type")
        if event_type not in EVENT_TYPES:
            raise ValueError(f"{event_id}: event_type inválido.")

        precision = raw.get("date_precision")
        if precision not in DATE_PRECISIONS:
            raise ValueError(f"{event_id}: date_precision inválida.")

        date_contract_met, date_issue = _date_precision_contract(
            event_id,
            precision,
            raw.get("date"),
            raw.get("date_range"),
        )
        if not date_contract_met and date_issue:
            date_contract_issues.append(
                {"event_id": event_id, "issue": date_issue}
            )

        quality = raw.get("documentary_quality")
        if quality not in DOCUMENTARY_QUALITIES:
            raise ValueError(f"{event_id}: documentary_quality inválida.")

        privacy_class = raw.get("privacy_class")
        if privacy_class not in PRIVACY_CLASSES:
            raise ValueError(f"{event_id}: privacy_class inválida.")

        roles = raw.get("evidence_roles")
        if (
            not isinstance(roles, list)
            or any(role not in EVIDENCE_ROLES for role in roles)
        ):
            raise ValueError(f"{event_id}: evidence_roles inválidos.")
        if len(set(roles)) != len(roles):
            raise ValueError(f"{event_id}: evidence_roles contiene duplicados.")

        fact_statement = raw.get("fact_statement")
        if not isinstance(fact_statement, str) or not fact_statement.strip():
            raise ValueError(f"{event_id}: fact_statement es obligatorio.")

        source_refs = raw.get("source_refs")
        if (
            not isinstance(source_refs, list)
            or any(not isinstance(ref, str) or not ref for ref in source_refs)
        ):
            raise ValueError(f"{event_id}: source_refs debe ser una lista de IDs.")
        if len(set(source_refs)) != len(source_refs):
            raise ValueError(f"{event_id}: source_refs contiene duplicados.")

        minimum_sources = 0
        if quality == "DQ1_PRIMARY_DOCUMENT":
            minimum_sources = 1
        elif quality == "DQ3_CORROBORATED_REPORT":
            minimum_sources = 2

        source_count_requirement_met = len(source_refs) >= minimum_sources
        if not source_count_requirement_met:
            documentary_quality_issues.append(
                {
                    "event_id": event_id,
                    "issue": (
                        f"{quality} requiere al menos {minimum_sources} "
                        "source_refs para sostener la etiqueta declarada."
                    ),
                }
            )

        independence_state = "NOT_APPLICABLE"
        if quality == "DQ3_CORROBORATED_REPORT":
            independence_state = (
                "DECLARED"
                if raw.get("source_independence_declared") is True
                else "NOT_VERIFIED"
            )

        if is_correction and not source_refs:
            documentary_quality_issues.append(
                {
                    "event_id": event_id,
                    "issue": "Una corrección append-only debe aportar source_refs.",
                }
            )

        interpretations = raw.get("interpretations", [])
        if not isinstance(interpretations, list) or any(
            not isinstance(item, Mapping) for item in interpretations
        ):
            raise ValueError(
                f"{event_id}: interpretations debe ser una lista de objetos."
            )

        linked_roots = [
            str(root_id) for root_id in raw.get("linked_root_refs", [])
        ]
        linked_clauses = [
            str(clause_id) for clause_id in raw.get("linked_clause_refs", [])
        ]
        if len(set(linked_roots)) != len(linked_roots):
            raise ValueError(f"{event_id}: linked_root_refs contiene duplicados.")
        if len(set(linked_clauses)) != len(linked_clauses):
            raise ValueError(f"{event_id}: linked_clause_refs contiene duplicados.")

        resolved_roots = [
            root_id for root_id in linked_roots if root_id in known_roots
        ]
        unresolved_roots = [
            root_id for root_id in linked_roots if root_id not in known_roots
        ]
        for root_id in unresolved_roots:
            unresolved_root_refs.append(
                {"event_id": event_id, "root_id": root_id}
            )

        resolved_clauses = [
            clause_id for clause_id in linked_clauses if clause_id in known_clauses
        ]
        unresolved_clauses = [
            clause_id for clause_id in linked_clauses if clause_id not in known_clauses
        ]
        for clause_id in unresolved_clauses:
            unresolved_clause_refs.append(
                {"event_id": event_id, "clause_id": clause_id}
            )

        role_traceability: dict[str, Any] = {}
        for role in roles:
            complete, state = _role_target_state(
                role,
                resolved_roots=resolved_roots,
                unresolved_roots=unresolved_roots,
                resolved_clauses=resolved_clauses,
                unresolved_clauses=unresolved_clauses,
                counterevidence_effect=raw.get("counterevidence_effect"),
                clause_registry_state=clause_registry_state,
            )
            role_traceability[role] = {
                "target_traceability_complete": complete,
                "state": state,
            }
            if not complete:
                role_traceability_issues.append(
                    {
                        "event_id": event_id,
                        "role": role,
                        "issue": state,
                    }
                )

        item = dict(raw)
        item["subjects"] = list(subjects)
        item["source_refs"] = list(source_refs)
        item["evidence_roles"] = list(roles)
        item["linked_root_refs"] = linked_roots
        item["linked_clause_refs"] = linked_clauses
        item["resolved_root_refs"] = resolved_roots
        item["unresolved_root_refs"] = unresolved_roots
        item["resolved_clause_refs"] = resolved_clauses
        item["unresolved_clause_refs"] = unresolved_clauses
        item["date_precision_contract_met"] = date_contract_met
        item["documentary_quality_contract_met"] = (
            source_count_requirement_met
            and (not is_correction or bool(source_refs))
        )
        item["source_independence_state"] = independence_state
        item["role_traceability"] = role_traceability
        item["fact_interpretation_separated"] = True
        item["interpretation_count"] = len(interpretations)
        item["is_correction"] = is_correction
        item["public_exportable"] = privacy_class in {
            "PUBLIC_VERIFIABLE",
            "SYNTHETIC",
        }
        item["creates_structural_root"] = False
        item["creates_clause"] = False
        item["elevates_origin"] = False
        item["astrology_backfill_allowed"] = False
        normalized.append(item)
        seen.add(event_id)

    superseded_by: dict[str, str] = {}
    for event in normalized:
        supersedes = event.get("supersedes_event_id")
        if isinstance(supersedes, str):
            superseded_by[supersedes] = event["event_id"]

    for event in normalized:
        event["record_status"] = (
            "SUPERSEDED"
            if event["event_id"] in superseded_by
            else "ACTIVE"
        )
        event["superseded_by_event_id"] = superseded_by.get(event["event_id"])

    role_counts: dict[str, int] = defaultdict(int)
    for event in normalized:
        for role in event["evidence_roles"]:
            role_counts[str(role)] += 1

    temporal = context.canonical_snapshot.get("temporal_activation")
    unresolved_temporal_event_refs: list[dict[str, str]] = []
    temporal_event_links: list[dict[str, str]] = []
    event_ids = {event["event_id"] for event in normalized}

    if isinstance(temporal, Mapping):
        temporal_signals = temporal.get("signals")
        if isinstance(temporal_signals, list):
            for signal in temporal_signals:
                if not isinstance(signal, Mapping):
                    continue
                signal_id = str(signal.get("signal_id") or "")
                for event_ref in signal.get("event_refs", []):
                    event_ref = str(event_ref)
                    if event_ref in event_ids:
                        temporal_event_links.append(
                            {
                                "signal_id": signal_id,
                                "event_id": event_ref,
                            }
                        )
                    else:
                        unresolved_temporal_event_refs.append(
                            {
                                "signal_id": signal_id,
                                "event_id": event_ref,
                            }
                        )

    public_event_ids = [
        event["event_id"] for event in normalized if event["public_exportable"]
    ]
    restricted_event_ids = [
        event["event_id"] for event in normalized if not event["public_exportable"]
    ]

    output = {
        "schema_version": "1.0.0",
        "analysis_freeze_ref": freeze_ref,
        "analysis_freeze_reference_declared": True,
        "analysis_freeze_reference_verified": False,
        "root_reference_registry_state": root_registry_state,
        "clause_reference_registry_state": clause_registry_state,
        "events": normalized,
        "event_count": len(normalized),
        "active_event_count": sum(
            1 for event in normalized if event["record_status"] == "ACTIVE"
        ),
        "superseded_event_count": sum(
            1 for event in normalized if event["record_status"] == "SUPERSEDED"
        ),
        "role_counts": dict(sorted(role_counts.items())),
        "unresolved_root_refs": unresolved_root_refs,
        "unresolved_clause_refs": unresolved_clause_refs,
        "date_contract_issues": date_contract_issues,
        "role_traceability_issues": role_traceability_issues,
        "documentary_quality_issues": documentary_quality_issues,
        "temporal_event_links": temporal_event_links,
        "unresolved_temporal_event_refs": unresolved_temporal_event_refs,
        "public_event_ids": public_event_ids,
        "restricted_event_ids": restricted_event_ids,
        "structural_mutation_allowed": False,
        "clause_creation_allowed": False,
        "origin_elevation_allowed": False,
        "astrology_backfill_allowed": False,
        "public_export_policy_enforced": True,
        "append_only_validated": True,
    }

    limitations = [
        "Los hechos pueden corroborar, refutar o describir viabilidad/reciprocidad; no crean retrospectivamente raíces, cláusulas u origen.",
        "analysis_freeze_ref queda declarado pero no verificado criptográfica o canónicamente porque todavía no existe un registro de freeze ejecutable.",
    ]
    if clause_registry_state == "NOT_AVAILABLE":
        limitations.append(
            "No existe un registro canónico de cláusulas disponible en esta ejecución; sus referencias no pueden resolverse."
        )

    return ModuleResult(
        module_id="M27",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"documentary_events": output},
        limitations=tuple(limitations),
    )

