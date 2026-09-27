from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from importlib import resources
import json
import re
from typing import Any, Mapping


POLICY_RESOURCE = "validation-execution-ledger-policy.json"
POLICY_PACKAGE = "almas_tfa"
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def load_validation_execution_ledger_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data", POLICY_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_VALIDATION_EXECUTION_LEDGER_V1":
        raise ValueError("Política de ledger de validación desconocida.")
    return policy


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha(value: Mapping[str, Any]) -> str:
    return sha256(_canonical_json(value)).hexdigest()


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA_RE.fullmatch(value) is not None


def _entry_core(
    *,
    sequence: int,
    event_type: str,
    artifact_ref: str,
    artifact_sha256: str,
    previous_entry_sha256: str | None,
) -> dict[str, Any]:
    return {
        "sequence": sequence,
        "event_type": event_type,
        "artifact_ref": artifact_ref,
        "artifact_sha256": artifact_sha256,
        "previous_entry_sha256": previous_entry_sha256,
    }


def _make_entry(**kwargs: Any) -> dict[str, Any]:
    core = _entry_core(**kwargs)
    return {**core, "entry_sha256": _sha(core)}


def initialize_validation_ledger(
    preregistration: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if policy is None:
        policy = load_validation_execution_ledger_policy()

    if preregistration.get("state") != "PREREGISTERED_READY":
        return _blocked("PREREGISTRATION_NOT_READY")

    bundle = preregistration.get("bundle")
    bundle_sha = preregistration.get("bundle_sha256")
    if not isinstance(bundle, Mapping) or not _valid_sha(bundle_sha):
        return _blocked("INVALID_PREREGISTRATION_ARTIFACT")
    if _sha(bundle) != bundle_sha:
        return _blocked("PREREGISTRATION_FINGERPRINT_MISMATCH")

    validation_id = bundle.get("validation_id")
    if not isinstance(validation_id, str) or not validation_id:
        return _blocked("MISSING_VALIDATION_ID")

    entry = _make_entry(
        sequence=1,
        event_type="PREREGISTERED",
        artifact_ref=str(bundle.get("preregistration_ref") or validation_id),
        artifact_sha256=bundle_sha,
        previous_entry_sha256=None,
    )
    ledger = {
        "schema_version": "1.0.0",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "validation_id": validation_id,
        "entries": [entry],
        "entry_count": 1,
        "current_event": "PREREGISTERED",
        "chain_head_sha256": entry["entry_sha256"],
        "closed": False,
        "automatic_registry_mutation": False,
        "promotion_decision": "FORBIDDEN",
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
    return {"state": "LEDGER_ACTIVE", "ledger": ledger}


def append_validation_event(
    ledger: Mapping[str, Any],
    *,
    event_type: str,
    artifact_ref: str,
    artifact_sha256: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if policy is None:
        policy = load_validation_execution_ledger_policy()

    audit = audit_validation_ledger(ledger, policy=policy)
    if audit.get("state") != "LEDGER_VALID":
        return _blocked("LEDGER_INTEGRITY_FAILURE")

    if bool(ledger.get("closed")):
        return _blocked("LEDGER_ALREADY_CLOSED")
    if not isinstance(artifact_ref, str) or not artifact_ref:
        return _blocked("INVALID_ARTIFACT_REF")
    if not _valid_sha(artifact_sha256):
        return _blocked("INVALID_ARTIFACT_SHA256")

    order = list(policy["event_order"])
    current = ledger.get("current_event")
    try:
        current_index = order.index(str(current))
    except ValueError:
        return _blocked("UNKNOWN_CURRENT_EVENT")
    if current_index + 1 >= len(order):
        return _blocked("NO_FURTHER_EVENT_ALLOWED")
    expected = order[current_index + 1]
    if event_type != expected:
        return _blocked(
            "INVALID_EVENT_TRANSITION",
            expected_event=expected,
            supplied_event=event_type,
        )

    entries = deepcopy(list(ledger["entries"]))
    previous = str(ledger["chain_head_sha256"])
    entry = _make_entry(
        sequence=len(entries) + 1,
        event_type=event_type,
        artifact_ref=artifact_ref,
        artifact_sha256=artifact_sha256,
        previous_entry_sha256=previous,
    )
    entries.append(entry)

    updated = deepcopy(dict(ledger))
    updated["entries"] = entries
    updated["entry_count"] = len(entries)
    updated["current_event"] = event_type
    updated["chain_head_sha256"] = entry["entry_sha256"]
    updated["closed"] = event_type == "VALIDATION_CLOSED"
    return {"state": "LEDGER_ACTIVE" if not updated["closed"] else "LEDGER_CLOSED", "ledger": updated}


def audit_validation_ledger(
    ledger: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if policy is None:
        policy = load_validation_execution_ledger_policy()

    if ledger.get("policy_id") != policy["policy_id"]:
        return {"state": "LEDGER_INVALID", "reason": "POLICY_ID_MISMATCH"}
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not entries:
        return {"state": "LEDGER_INVALID", "reason": "MISSING_ENTRIES"}

    expected_order = list(policy["event_order"])
    previous = None
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, Mapping):
            return {"state": "LEDGER_INVALID", "reason": "ENTRY_NOT_OBJECT"}
        if entry.get("sequence") != index:
            return {"state": "LEDGER_INVALID", "reason": "SEQUENCE_MISMATCH"}
        if index > len(expected_order) or entry.get("event_type") != expected_order[index - 1]:
            return {"state": "LEDGER_INVALID", "reason": "EVENT_ORDER_MISMATCH"}
        if entry.get("previous_entry_sha256") != previous:
            return {"state": "LEDGER_INVALID", "reason": "CHAIN_LINK_MISMATCH"}

        core = {
            "sequence": entry.get("sequence"),
            "event_type": entry.get("event_type"),
            "artifact_ref": entry.get("artifact_ref"),
            "artifact_sha256": entry.get("artifact_sha256"),
            "previous_entry_sha256": entry.get("previous_entry_sha256"),
        }
        expected_sha = _sha(core)
        if entry.get("entry_sha256") != expected_sha:
            return {"state": "LEDGER_INVALID", "reason": "ENTRY_HASH_MISMATCH"}
        if not _valid_sha(entry.get("artifact_sha256")):
            return {"state": "LEDGER_INVALID", "reason": "ARTIFACT_HASH_INVALID"}
        previous = expected_sha

    if ledger.get("entry_count") != len(entries):
        return {"state": "LEDGER_INVALID", "reason": "ENTRY_COUNT_MISMATCH"}
    if ledger.get("chain_head_sha256") != previous:
        return {"state": "LEDGER_INVALID", "reason": "CHAIN_HEAD_MISMATCH"}
    if ledger.get("current_event") != entries[-1].get("event_type"):
        return {"state": "LEDGER_INVALID", "reason": "CURRENT_EVENT_MISMATCH"}
    expected_closed = entries[-1].get("event_type") == "VALIDATION_CLOSED"
    if bool(ledger.get("closed")) != expected_closed:
        return {"state": "LEDGER_INVALID", "reason": "CLOSED_STATE_MISMATCH"}

    return {
        "state": "LEDGER_VALID",
        "entry_count": len(entries),
        "current_event": entries[-1]["event_type"],
        "chain_head_sha256": previous,
        "closed": expected_closed,
        "promotion_decision": "FORBIDDEN",
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "state": "BLOCKED_LEDGER_OPERATION",
        "reason": reason,
        **extra,
        "promotion_decision": "FORBIDDEN",
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
