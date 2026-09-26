from __future__ import annotations

import copy
from typing import Any, Mapping

from almas_tfa.discriminator_promotion_registry import (
    has_complete_l3_record,
    load_discriminator_promotion_registry,
)
from almas_tfa.promotion_state_machine import (
    MAINLINE_STATES,
    load_promotion_state_machine_policy,
    missing_stage_requirements,
)


REPORTING_VERSION = "1.0.0"


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _next_mainline_status(
    current_status: str,
    policy: Mapping[str, Any],
) -> str | None:
    if current_status == "BLOCKED" or current_status == "RETIRED":
        return None
    if current_status == "VALIDATED_DISCRIMINATOR":
        return None
    target = policy.get("forward_transitions", {}).get(current_status)
    return str(target) if isinstance(target, str) and target else None


def _requirements_for_stage(
    record: Mapping[str, Any],
    target_status: str | None,
    policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if target_status is None:
        return []

    requirement_keys = (
        policy.get("cumulative_stage_requirements", {})
        .get(target_status, [])
    )
    evidence = record.get("promotion_evidence", {})
    if not isinstance(evidence, Mapping):
        evidence = {}

    return [
        {
            "requirement_id": str(key),
            "satisfied": _nonempty_string_list(evidence.get(key)),
            "evidence_refs": (
                list(evidence.get(key, []))
                if isinstance(evidence.get(key), list)
                else []
            ),
        }
        for key in requirement_keys
    ]


def _history_snapshot(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    history = record.get("state_history", [])
    if not isinstance(history, list):
        return []

    allowed = (
        "transition_id",
        "from_status",
        "to_status",
        "mode",
        "occurred_at",
        "actor_ref",
        "reason",
        "evidence_refs",
        "record_fingerprint_before",
        "record_fingerprint_after",
    )
    snapshot: list[dict[str, Any]] = []
    for event in history:
        if not isinstance(event, Mapping):
            continue
        snapshot.append(
            {
                key: copy.deepcopy(event.get(key))
                for key in allowed
            }
        )
    return snapshot


def _record_reporting_view(
    record: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    discriminator_id = record.get("discriminator_id")
    current_status = str(record.get("current_status"))
    next_status = _next_mainline_status(current_status, policy)

    if current_status in MAINLINE_STATES:
        current_missing = (
            missing_stage_requirements(
                record,
                current_status,
                policy=policy,
            )
            if current_status != "EXPLORATORY"
            else []
        )
    else:
        current_missing = []

    next_requirements = _requirements_for_stage(
        record,
        next_status,
        policy,
    )
    next_missing = [
        item["requirement_id"]
        for item in next_requirements
        if item["satisfied"] is not True
    ]

    l3_gate_complete = has_complete_l3_record(record)

    return {
        "discriminator_id": discriminator_id,
        "current_status": current_status,
        "last_active_status": record.get("last_active_status"),
        "block_reason": record.get("block_reason"),
        "uses_astrology": record.get("uses_astrology") is True,
        "l3_authorized": record.get("l3_authorized") is True,
        "l3_gate_complete": l3_gate_complete,
        "next_mainline_status": next_status,
        "current_stage_gate_satisfied": not current_missing,
        "current_stage_missing_requirements": current_missing,
        "next_stage_requirements": next_requirements,
        "next_stage_missing_requirements": next_missing,
        "promotion_ref": record.get("promotion_ref"),
        "promoted_at": record.get("promoted_at"),
        "validated_pairs": copy.deepcopy(record.get("validated_pairs", [])),
        "history": _history_snapshot(record),
        "history_count": len(_history_snapshot(record)),
        "terminal": current_status == "RETIRED",
        "blocked": current_status == "BLOCKED",
        "methodological_status_only": True,
        "ontological_weight": 0,
        "can_change_case_classification": False,
        "can_raise_irc": False,
    }


def build_promotion_reporting(
    *,
    registry: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or load_discriminator_promotion_registry()
    policy = policy or load_promotion_state_machine_policy()

    records = registry.get("records", [])
    if not isinstance(records, list):
        raise ValueError("Registro de promoción inválido: records debe ser lista.")

    views = [
        _record_reporting_view(record, policy)
        for record in records
        if isinstance(record, Mapping)
    ]
    views.sort(key=lambda item: str(item["discriminator_id"]))

    summary_counts = {
        state: sum(1 for item in views if item["current_status"] == state)
        for state in (
            "EXPLORATORY",
            "REPRODUCIBLE",
            "REPLICATION_READY",
            "CONFIRMATORY_ELIGIBLE",
            "VALIDATED_DISCRIMINATOR",
            "BLOCKED",
            "RETIRED",
        )
    }

    return {
        "reporting_version": REPORTING_VERSION,
        "reporting_kind": "DISCRIMINATOR_PROMOTION_STATUS",
        "source_registry_authority": registry.get("authority"),
        "source_registry_version": registry.get("registry_version"),
        "state_machine_policy_id": policy.get("policy_id"),
        "epistemic_role": "METHODOLOGICAL_STATUS_ONLY",
        "methodological_status_only": True,
        "ontological_inference_allowed": False,
        "case_classification_mutated": False,
        "irc_mutated": False,
        "validated_discriminator_ids": list(
            registry.get("validated_discriminator_ids", [])
        ),
        "summary_counts": summary_counts,
        "records": views,
    }
