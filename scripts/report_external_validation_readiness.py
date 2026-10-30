#!/usr/bin/env python3
"""Preflight transversal SHADOW de manifiestos de validación externa ALMAS.

No verifica fuentes, independencia o preregistro externos. No abre holdouts,
no admite casos, no altera scoring ni autoriza promoción ontológica.
"""
from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = {
    "cohorts": "manifests/validation-cohort-manifest.json",
    "pair_identity": "manifests/pair-identity-validation-manifest.json",
    "public_holdouts": "validation/holdouts/manifest.json",
    "rra": "validation/returns/external-validation-readiness.json",
}
REQUIRED_RRA_BLOCKERS = frozenset({
    "DOCUMENTARY_FEASIBILITY_COHORT_NOT_IDENTIFIED",
    "EVENT_CODING_AND_AGREEMENT_NOT_COMPLETED",
    "OBSERVATION_PERIODS_AND_CONTROL_STRATA_NOT_FROZEN",
    "PERSON_COMPONENT_SPLIT_NOT_POPULATED",
    "SAMPLE_SIZE_AND_STOPPING_RULE_NOT_JUSTIFIED",
    "EXCHANGEABILITY_AND_MULTIPLICITY_PLAN_NOT_FINALIZED",
    "VERIFIABLE_PREREGISTRATION_NOT_COMPLETED",
})


def load_manifests(root: Path = ROOT) -> dict[str, Any]:
    """Lee únicamente rutas de configuración públicas y fijadas en el código."""
    return {key: json.loads((root / path).read_text(encoding="utf-8"))
            for key, path in SOURCE_FILES.items()}


def _object(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name}: expected JSON object")
    return value


def _list(value: Any, name: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{name}: expected list")
    return value


def audit_external_readiness(manifests: Mapping[str, Any]) -> dict[str, Any]:
    """Informe de preparación no confirmatorio, sin datos individuales.

    NOT_READY: manifiestos coherentes y falta evidencia externa.
    REVIEW_REQUIRED: hay declaraciones de nueva cohorte/artefactos que requieren
    auditoría humana y de procedencia; nunca autoriza ejecución confirmatoria.
    CONTRACT_VIOLATION: indicadores incompatibles o datos mal formados.
    """
    src = _object(manifests, "manifests")
    cohorts = _object(src.get("cohorts"), "cohorts")
    pair = _object(src.get("pair_identity"), "pair_identity")
    public = _object(src.get("public_holdouts"), "public_holdouts")
    rra = _object(src.get("rra"), "rra")

    counts = {
        "general_real_cases": len(_list(cohorts.get("real_cases"), "cohorts.real_cases")),
        "pair_real_cohorts": len(_list(pair.get("real_cohorts"), "pair.real_cohorts")),
        "public_holdout_artifacts": len(_list(public.get("artifacts"), "public.artifacts")),
        "rra_real_cases": len(_list(rra.get("real_cases"), "rra.real_cases")),
    }
    violations: list[str] = []
    if cohorts.get("status") != "PREREGISTRATION_INFRASTRUCTURE":
        violations.append("GENERAL_COHORT_STATUS_NOT_BASELINE")
    if pair.get("policy_id") != "ALMAS_PAIR_IDENTITY_VALIDATION_V1":
        violations.append("PAIR_POLICY_ID_MISMATCH")
    if pair.get("status") != "INFRASTRUCTURE_ONLY_NO_EMPIRICAL_HOLDOUT":
        violations.append("PAIR_STATUS_REQUIRES_REVIEW")
    if public.get("policy_id") != "ALMAS_PUBLIC_DATA_ISOLATION_V1":
        violations.append("PUBLIC_DATA_POLICY_ID_MISMATCH")
    if rra.get("status") != "DRAFT_NOT_PREREGISTERED":
        violations.append("RRA_STATUS_REQUIRES_REVIEW")
    if rra.get("external_validation_status") != "NOT_PERFORMED":
        violations.append("RRA_EXTERNAL_VALIDATION_CLAIM_REQUIRES_REVIEW")
    if rra.get("confirmatory_execution_allowed") is not False:
        violations.append("RRA_CONFIRMATORY_EXECUTION_NOT_BLOCKED")
    if rra.get("holdout_opened") is not False:
        violations.append("RRA_HOLDOUT_UNEXPECTEDLY_OPEN")
    if rra.get("external_registration") is not None:
        violations.append("RRA_REGISTRATION_REQUIRES_INDEPENDENT_AUDIT")
    if pair.get("metaphysical_ground_truth") is not False:
        violations.append("METAPHYSICAL_GROUND_TRUTH_CLAIM")
    if pair.get("l3_validated_discriminator_present") is not False:
        violations.append("UNVERIFIED_L3_PROMOTION")
    if rra.get("exchangeability_status") != "NOT_ESTABLISHED":
        violations.append("RRA_EXCHANGEABILITY_CLAIM_REQUIRES_REVIEW")

    blockers = _list(rra.get("blockers"), "rra.blockers")
    if not all(isinstance(x, str) for x in blockers) or set(blockers) != REQUIRED_RRA_BLOCKERS or len(blockers) != 7:
        violations.append("RRA_SEVEN_BLOCKERS_MISMATCH")

    closure = _object(rra.get("closure_assessment"), "rra.closure_assessment")
    if (closure.get("requirements_total") != 7
            or closure.get("requirements_resolved") != 0
            or closure.get("empirical_execution_completed") is not False):
        violations.append("RRA_CLOSURE_RECEIPT_REQUIRES_REVIEW")
    if rra.get("negative_observation_periods_verified") != 0:
        violations.append("RRA_NEGATIVE_OBSERVATION_CLAIM_REQUIRES_REVIEW")

    candidate_cases = sum(counts.values())
    status = ("CONTRACT_VIOLATION" if violations
              else "REVIEW_REQUIRED" if candidate_cases
              else "NOT_READY")

    return {
        "schema_version": "ALMAS_EXTERNAL_READINESS_CROSS_MANIFEST_V1",
        "status": status,
        "mode": "SHADOW_READ_ONLY",
        "source_paths": list(SOURCE_FILES.values()),
        "declared_counts": counts,
        "rra_unresolved_requirements": len(blockers),
        "violations": sorted(violations),
        "independent_provenance_verified": False,
        "preregistration_verified": False,
        "confirmatory_execution_authorized": False,
        "empirical_utility_validated": False,
        "metaphysical_hypotheses_evaluable": False,
        "production_indices_modified": False,
        "note": "Coherencia interna de cuatro manifiestos; no auditoría externa ni certificado de potencia.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="Raíz local del repositorio; no incluye holdouts privados")
    args = parser.parse_args()
    try:
        report = audit_external_readiness(load_manifests(args.root))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "CONTRACT_VIOLATION", "error_type": type(exc).__name__,
                          "confirmatory_execution_authorized": False}, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 2 if report["status"] == "CONTRACT_VIOLATION" else 0


if __name__ == "__main__":
    raise SystemExit(main())
