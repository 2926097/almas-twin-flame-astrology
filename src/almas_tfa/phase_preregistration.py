"""Verificación de prerregistros de fases previos a la aplicación de casos."""
from __future__ import annotations
import hashlib
from pathlib import Path
from importlib import resources
from typing import Any, Mapping

REQUIRED_ARTIFACTS = {
    "reference/dynamic-phase-vocabulary.json",
    "reference/surrender-operational-policy.json",
    "reference/awakening-operational-policy.json",
    "reference/doctrinal-sequence-models.json",
}


def verify_phase_preregistration(record: Mapping[str, Any], root: Path | None = None) -> dict[str, Any]:
    """Check preregistration status and content fingerprints; no case fitting."""
    if record.get("policy_id") != "ALMAS_PHASE_PREREGISTRATION_V1":
        raise ValueError("unregistered preregistration policy.")
    if record.get("status") != "FROZEN_BEFORE_CASE_APPLICATION":
        raise ValueError("preregistration is not frozen before case application.")
    if record.get("case_data_included") is not False or record.get("case_specific_tuning") is not False:
        raise ValueError("preregistration must not contain or tune to case data.")
    artifacts = record.get("frozen_artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("frozen_artifacts must be a list.")
    paths = [item.get("path") for item in artifacts if isinstance(item, Mapping)]
    if len(paths) != len(artifacts) or set(paths) != REQUIRED_ARTIFACTS or len(paths) != len(set(paths)):
        raise ValueError("frozen_artifacts must contain exactly the registered policy artifacts.")
    verified = []
    for item in artifacts:
        path = Path(item["path"])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("frozen artifact path must remain within the repository.")
        # Default verification uses the exact frozen bytes distributed in the
        # wheel. An explicit root audits a caller-supplied repository instead.
        target = (Path(root) / path if root is not None else
                  resources.files("almas_tfa").joinpath("data", path.name))
        if not target.is_file():
            raise ValueError(f"frozen artifact is missing: {item['path']}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if item.get("sha256") != actual:
            raise ValueError(f"frozen artifact fingerprint mismatch: {item['path']}")
        verified.append(item["path"])
    if record.get("sequence_rules", {}).get("causal_status") != "UNESTABLISHED":
        raise ValueError("preregistered sequence rules must preserve the causal firewall.")
    return {"status": "VERIFIED", "verified_artifacts": sorted(verified), "case_data_included": False}
