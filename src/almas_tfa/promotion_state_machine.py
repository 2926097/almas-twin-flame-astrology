from __future__ import annotations

import copy
import json
from functools import lru_cache
from importlib.resources import files
from typing import Any, Mapping

from almas_tfa.blinding_leakage import canonical_sha256
from almas_tfa.discriminator_promotion_registry import has_complete_l3_record


POLICY_RESOURCE = "data/promotion-state-machine-policy.json"

MAINLINE_STATES = (
    "EXPLORATORY",
    "REPRODUCIBLE",
    "REPLICATION_READY",
    "CONFIRMATORY_ELIGIBLE",
    "VALIDATED_DISCRIMINATOR",
)
SPECIAL_STATES = ("BLOCKED", "RETIRED")
ALL_STATES = frozenset(MAINLINE_STATES + SPECIAL_STATES)

ALLOWED_UPDATE_FIELDS = frozenset(
    {
        "promotion_evidence",
        "frozen",
        "validation_evidence",
        "discriminant_validation",
        "blinding_audit",
        "astrology_validation",
        "validated_pairs",
        "promotion_ref",
        "promoted_at",
        "l3_authorized",
        "block_reason",
    }
)


@lru_cache(maxsize=1)
def load_promotion_state_machine_policy() -> dict[str, Any]:
    resource = files("almas_tfa").joinpath(POLICY_RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _record_fingerprint(record: Mapping[str, Any]) -> str:
    material = {
        key: value
        for key, value in record.items()
        if key != "state_history"
    }
    return canonical_sha256(material)


def _history_ids(record: Mapping[str, Any]) -> set[str]:
    history = record.get("state_history", [])
    if not isinstance(history, list):
        raise ValueError("state_history debe ser una lista.")
    ids: set[str] = set()
    for event in history:
        if not isinstance(event, Mapping):
            raise ValueError("state_history contiene una entrada inválida.")
        transition_id = event.get("transition_id")
        if not isinstance(transition_id, str) or not transition_id:
            raise ValueError("state_history contiene transition_id inválido.")
        if transition_id in ids:
            raise ValueError(f"transition_id duplicado en state_history: {transition_id}")
        ids.add(transition_id)
    return ids


def _promotion_evidence(record: Mapping[str, Any]) -> Mapping[str, Any]:
    evidence = record.get("promotion_evidence")
    if not isinstance(evidence, Mapping):
        raise ValueError("promotion_evidence debe existir como objeto.")
    return evidence


def missing_stage_requirements(
    record: Mapping[str, Any],
    target_status: str,
    *,
    policy: Mapping[str, Any] | None = None,
) -> list[str]:
    policy = policy or load_promotion_state_machine_policy()
    requirements = (
        policy.get("cumulative_stage_requirements", {})
        .get(target_status, [])
    )
    evidence = _promotion_evidence(record)
    return [
        str(key)
        for key in requirements
        if not _nonempty_string_list(evidence.get(key))
    ]


def _validate_transition_shape(
    record: Mapping[str, Any],
    transition: Mapping[str, Any],
) -> None:
    required = (
        "transition_id",
        "from_status",
        "to_status",
        "mode",
        "occurred_at",
        "actor_ref",
        "reason",
        "evidence_refs",
        "record_updates",
    )
    for key in required:
        if key not in transition:
            raise ValueError(f"Transición incompleta: falta {key}.")

    for key in ("transition_id", "occurred_at", "actor_ref", "reason"):
        if not isinstance(transition.get(key), str) or not transition[key]:
            raise ValueError(f"Transición inválida: {key} debe ser texto no vacío.")

    if not _nonempty_string_list(transition.get("evidence_refs")):
        raise ValueError("Transición inválida: evidence_refs no vacío es obligatorio.")

    from_status = transition.get("from_status")
    to_status = transition.get("to_status")
    if from_status not in ALL_STATES or to_status not in ALL_STATES:
        raise ValueError("Transición contiene un estado no reconocido.")

    if record.get("current_status") != from_status:
        raise ValueError(
            "from_status no coincide con current_status del registro."
        )

    transition_id = str(transition["transition_id"])
    if transition_id in _history_ids(record):
        raise ValueError(f"transition_id ya utilizado: {transition_id}")

    updates = transition.get("record_updates")
    if not isinstance(updates, Mapping):
        raise ValueError("record_updates debe ser un objeto.")

    forbidden = set(updates) - ALLOWED_UPDATE_FIELDS
    if forbidden:
        raise ValueError(
            "record_updates contiene campos inmutables/no autorizados: "
            + ", ".join(sorted(forbidden))
        )


def _validate_route(
    record: Mapping[str, Any],
    transition: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> None:
    mode = transition.get("mode")
    source = str(transition.get("from_status"))
    target = str(transition.get("to_status"))

    if source == "RETIRED":
        raise ValueError("RETIRED es terminal.")

    if mode == "FORWARD":
        expected = policy.get("forward_transitions", {}).get(source)
        if target != expected:
            raise ValueError(
                f"Salto de promoción no permitido: {source} -> {target}."
            )
        return

    if mode == "ROLLBACK":
        if source == "VALIDATED_DISCRIMINATOR":
            raise ValueError(
                "VALIDATED_DISCRIMINATOR no admite rollback; debe RETIRE."
            )
        expected = policy.get("rollback_transitions", {}).get(source)
        if target != expected:
            raise ValueError(
                f"Rollback no permitido: {source} -> {target}."
            )
        return

    if mode == "BLOCK":
        if source not in MAINLINE_STATES[:-1] or target != "BLOCKED":
            raise ValueError("BLOCK sólo puede bloquear un estado activo no-L3.")
        if not isinstance(transition.get("reason"), str) or not transition["reason"]:
            raise ValueError("BLOCK requiere reason.")
        return

    if mode == "UNBLOCK":
        if source != "BLOCKED":
            raise ValueError("UNBLOCK sólo puede salir de BLOCKED.")
        resume = record.get("last_active_status")
        if resume not in MAINLINE_STATES[:-1] or target != resume:
            raise ValueError(
                "UNBLOCK debe volver exactamente a last_active_status."
            )
        refs = transition.get("block_resolution_refs")
        if not _nonempty_string_list(refs):
            raise ValueError("UNBLOCK requiere block_resolution_refs.")
        return

    if mode == "RETIRE":
        if target != "RETIRED":
            raise ValueError("RETIRE debe terminar en RETIRED.")
        return

    raise ValueError(f"Modo de transición no permitido: {mode}")


def _build_candidate_record(
    record: Mapping[str, Any],
    transition: Mapping[str, Any],
) -> dict[str, Any]:
    candidate = copy.deepcopy(dict(record))
    updates = transition.get("record_updates", {})
    for key, value in updates.items():
        candidate[key] = copy.deepcopy(value)

    source = str(transition["from_status"])
    target = str(transition["to_status"])
    mode = str(transition["mode"])

    candidate["current_status"] = target

    if mode == "BLOCK":
        candidate["last_active_status"] = source
        candidate["block_reason"] = str(transition["reason"])
        candidate["l3_authorized"] = False
    elif mode == "UNBLOCK":
        candidate["last_active_status"] = None
        candidate["block_reason"] = None
        candidate["l3_authorized"] = False
    elif mode == "RETIRE":
        candidate["last_active_status"] = None
        candidate["l3_authorized"] = False
        if not candidate.get("block_reason"):
            candidate["block_reason"] = str(transition["reason"])
    elif target != "VALIDATED_DISCRIMINATOR":
        candidate["last_active_status"] = None
        candidate["l3_authorized"] = False

    return candidate


def _validate_target_gates(
    candidate: Mapping[str, Any],
    target_status: str,
    *,
    policy: Mapping[str, Any],
) -> None:
    if target_status in {
        "REPRODUCIBLE",
        "REPLICATION_READY",
        "CONFIRMATORY_ELIGIBLE",
    }:
        missing = missing_stage_requirements(
            candidate,
            target_status,
            policy=policy,
        )
        if missing:
            raise ValueError(
                f"{target_status} carece de requisitos acumulativos: "
                + ", ".join(missing)
            )

    if target_status == "VALIDATED_DISCRIMINATOR":
        if candidate.get("l3_authorized") is not True:
            raise ValueError(
                "VALIDATED_DISCRIMINATOR requiere l3_authorized=true."
            )
        if not has_complete_l3_record(candidate):
            raise ValueError(
                "VALIDATED_DISCRIMINATOR no supera los gates L3 acumulativos."
            )
    elif candidate.get("l3_authorized") is True:
        raise ValueError(
            "Sólo VALIDATED_DISCRIMINATOR puede mantener l3_authorized=true."
        )


def validate_promotion_transition(
    record: Mapping[str, Any],
    transition: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or load_promotion_state_machine_policy()
    _validate_transition_shape(record, transition)
    _validate_route(record, transition, policy)

    candidate = _build_candidate_record(record, transition)
    _validate_target_gates(
        candidate,
        str(transition["to_status"]),
        policy=policy,
    )

    return candidate


def apply_promotion_transition(
    record: Mapping[str, Any],
    transition: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or load_promotion_state_machine_policy()
    before_fingerprint = _record_fingerprint(record)
    candidate = validate_promotion_transition(
        record,
        transition,
        policy=policy,
    )

    after_fingerprint = _record_fingerprint(candidate)
    history = copy.deepcopy(list(record.get("state_history", [])))
    history.append(
        {
            "transition_id": transition["transition_id"],
            "from_status": transition["from_status"],
            "to_status": transition["to_status"],
            "mode": transition["mode"],
            "occurred_at": transition["occurred_at"],
            "actor_ref": transition["actor_ref"],
            "reason": transition["reason"],
            "evidence_refs": list(transition["evidence_refs"]),
            "record_fingerprint_before": before_fingerprint,
            "record_fingerprint_after": after_fingerprint,
        }
    )
    candidate["state_history"] = history
    return candidate
