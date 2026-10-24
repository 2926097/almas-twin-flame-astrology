#!/usr/bin/env python3
"""End-to-end synthetic two-birth test of the exact ALMAS Web local engine.

Requires a manually/CI-fetched SHA-pinned JPL kernel. Emits STATUS ONLY, never
birth details, raw_input, full canonical or other potentially identifying data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "almas-web-preview"))
from local_astronomy_preflight import assess_local_astronomy_runtime
from local_engine_server import process_locally

PRESET = "ALMAS_RELATIONAL_STRICT_RESEARCH_V1"

def synthetic_request() -> dict:
    return {
        "format": "ALMAS_WORK_REQUEST",
        "type": "RELATIONAL",
        "execution_state": "REQUEST_ONLY",
        "public_version": "1.26.0",
        "analysis_profile": "FULL_ASTROLOGY",
        "analysis_policy_profile": PRESET,
        "subjects": [
            {"id": "A", "birth_date": "1988-06-17", "birth_time": "13:20",
             "timezone": "Europe/Madrid", "latitude": 40.4168,
             "longitude": -3.7038, "time_reliability": "B"},
            {"id": "B", "birth_date": "1990-11-06", "birth_time": "09:10",
             "timezone": "America/Chicago", "latitude": 41.8781,
             "longitude": -87.6298, "time_reliability": "B"},
        ],
        "events": [],
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    # The preflight does not certify precision; existing golden workflows do.
    preflight = assess_local_astronomy_runtime(
        args.kernel, args.sha256, "DE440", "PLACIDUS")
    from almas_tfa.production_astronomy import MoiraBackendConfig, MoiraProductionBackend
    config = MoiraBackendConfig(
        kernel_path=str(args.kernel), kernel_sha256=args.sha256,
        kernel_family="DE440", house_system="PLACIDUS")
    out = process_locally(synthetic_request(),
        backend_factory=lambda: MoiraProductionBackend(config))
    statuses = out.get("module_statuses") or {}
    result = {
        "kind": "ALMAS_WEB_SYNTHETIC_TWO_BIRTH_E2E_V1",
        "synthetic": True,
        "kernel_sha256": preflight["kernel_sha256"],
        "provider_version": preflight["provider_version"],
        "manifest_modules": len(statuses),
        "module_statuses": statuses,
        "state": out["state"],
        "canonical_produced_by_m30": isinstance(out.get("canonical_analysis"), dict),
        "m30_state": out.get("m30", {}).get("state"),
        "m31_state": out.get("m31", {}).get("report_state"),
        "fingerprints_agree": (
            isinstance(out.get("m30"), dict) and
            isinstance(out.get("m31"), dict) and
            out["m30"].get("canonical_fingerprint") ==
            out["m31"].get("canonical_fingerprint") ==
            out.get("atlas", {}).get("canonical_fingerprint")
        ),
        "narrative_generated": False,
        "user_data_processed": False,
        "network_download_during_calculation": False,
        "metaphysical_claims_validated": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n",
        encoding="utf-8")
    # No values, personal identifiers or chart details in CI logs.
    print("ALMAS synthetic E2E: "+result["state"]+
        ", modules="+str(result["manifest_modules"])+
        ", canonical="+str(result["canonical_produced_by_m30"])+
        ", fingerprint_gate="+str(result["fingerprints_agree"]))
    if result["manifest_modules"] != 32:
        return 3
    if any(status == "FAILED" for status in statuses.values()):
        return 4
    if not result["canonical_produced_by_m30"]:
        return 5
    if out["state"] not in ("PARTIAL","READY") or not result["fingerprints_agree"]:
        return 6
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
