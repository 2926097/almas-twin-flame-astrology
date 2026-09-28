from __future__ import annotations

from collections import Counter
from importlib import resources
import json
from typing import Any, Mapping


POLICY_RESOURCE = "external-recurrence-cohort-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_external_recurrence_cohort_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        POLICY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_EXTERNAL_RECURRENCE_COHORT_V1":
        raise ValueError("Política de cohorte externa desconocida.")
    return policy


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} debe ser un string no vacío.")
    return value.strip()


def _count_zero(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} debe ser entero >= 0.")
    return int(value)


def _snapshot_valid(sample: Mapping[str, Any]) -> bool:
    snapshot = sample.get("recurrence_snapshot")
    if not isinstance(snapshot, Mapping):
        return False
    pillar = snapshot.get("pillar_attribution")
    if not isinstance(pillar, Mapping):
        return False
    return (
        isinstance(pillar.get("semantic_motifs"), Mapping)
        and isinstance(pillar.get("recurrence_quality"), Mapping)
    )


def validate_external_recurrence_cohort(
    cohort: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Valida procedencia/contaminación sin publicar snapshots privados."""

    if policy is None:
        policy = load_external_recurrence_cohort_policy()

    for field in (
        "cohort_id",
        "preregistration_ref",
        "frozen_almas_version",
        "frozen_commit_sha",
        "feature_set_ref",
        "orb_policy_ref",
        "pairing_rule_ref",
        "inclusion_rule_ref",
    ):
        _nonempty_string(cohort.get(field), field)

    null_model = cohort.get("null_model")
    if null_model not in policy["allowed_null_models"]:
        raise ValueError("null_model no admitido por S4.")

    samples = cohort.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("samples debe contener al menos una muestra.")

    seen_refs: set[str] = set()
    validation_counts: Counter[str] = Counter()
    selection_counts: Counter[str] = Counter()
    blinding_counts: Counter[str] = Counter()
    external_candidate_count = 0
    external_candidate_clean_count = 0
    contamination_count = 0
    leakage_count = 0
    invalid_snapshot_count = 0

    for index, sample in enumerate(samples):
        if not isinstance(sample, Mapping):
            raise ValueError(f"samples[{index}] debe ser un objeto.")

        sample_ref = _nonempty_string(
            sample.get("sample_ref"),
            f"samples[{index}].sample_ref",
        )
        if sample_ref in seen_refs:
            raise ValueError(f"sample_ref duplicado: {sample_ref}.")
        seen_refs.add(sample_ref)

        status = sample.get("validation_status")
        if status not in policy["allowed_validation_statuses"]:
            raise ValueError(f"{sample_ref}: validation_status inválido.")
        selection = sample.get("selection_status")
        if selection not in policy["allowed_selection_statuses"]:
            raise ValueError(f"{sample_ref}: selection_status inválido.")
        blinding = sample.get("label_blinding")
        if blinding not in policy["allowed_label_blinding"]:
            raise ValueError(f"{sample_ref}: label_blinding inválido.")

        contamination = sample.get("contamination")
        if not isinstance(contamination, bool):
            raise ValueError(f"{sample_ref}: contamination debe ser boolean.")
        if contamination:
            contamination_count += 1

        leakage_fields = (
            "forbidden_field_hits",
            "label_leakage_count",
            "narrative_leakage_count",
            "case_fitting_count",
        )
        leakage_values = {
            field: _count_zero(sample.get(field), f"{sample_ref}.{field}")
            for field in leakage_fields
        }
        has_leakage = any(value > 0 for value in leakage_values.values())
        if has_leakage:
            leakage_count += 1

        snapshot_ok = _snapshot_valid(sample)
        if not snapshot_ok:
            invalid_snapshot_count += 1

        validation_counts[str(status)] += 1
        selection_counts[str(selection)] += 1
        blinding_counts[str(blinding)] += 1

        if status in policy["external_candidate_statuses"]:
            external_candidate_count += 1
            clean = (
                selection == "PREREGISTERED"
                and not contamination
                and not has_leakage
                and snapshot_ok
            )
            if clean:
                external_candidate_clean_count += 1

    all_snapshots_valid = invalid_snapshot_count == 0
    all_external_candidates_clean = (
        external_candidate_count > 0
        and external_candidate_clean_count == external_candidate_count
    )

    return {
        "state": (
            "PROTOCOL_READY"
            if all_snapshots_valid
            else "NOT_EVALUABLE"
        ),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "cohort_id": str(cohort["cohort_id"]),
        "null_model": str(null_model),
        "sample_count": len(samples),
        "validation_status_counts": dict(sorted(validation_counts.items())),
        "selection_status_counts": dict(sorted(selection_counts.items())),
        "label_blinding_counts": dict(sorted(blinding_counts.items())),
        "contamination_count": contamination_count,
        "leakage_sample_count": leakage_count,
        "invalid_snapshot_count": invalid_snapshot_count,
        "external_candidate_count": external_candidate_count,
        "external_candidate_clean_count": external_candidate_clean_count,
        "all_external_candidates_clean": all_external_candidates_clean,
        "preregistration_ref": str(cohort["preregistration_ref"]),
        "frozen_almas_version": str(cohort["frozen_almas_version"]),
        "frozen_commit_sha": str(cohort["frozen_commit_sha"]),
        "feature_set_ref": str(cohort["feature_set_ref"]),
        "orb_policy_ref": str(cohort["orb_policy_ref"]),
        "pairing_rule_ref": str(cohort["pairing_rule_ref"]),
        "inclusion_rule_ref": str(cohort["inclusion_rule_ref"]),
        "private_sample_refs_exposed": False,
        "sample_snapshots_exposed": False,
        "public_output_aggregate_only": True,
        "used_for_weighting": False,
        "used_in_px_score": False,
        "used_in_ps_score": False,
        "used_in_iem": False,
        "used_in_idd": False,
        "used_in_irc": False,
        "used_in_ontology": False,
        "metaphysical_probability": False,
        "l3_validation": False,
        "candidate_weighting_enabled": False,
    }


def extract_validated_external_snapshots(
    cohort: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> list[Mapping[str, Any]]:
    """Runtime-only: devuelve snapshots tras validación; no para serialización pública."""

    summary = validate_external_recurrence_cohort(
        cohort,
        policy=policy,
    )
    if summary["state"] != "PROTOCOL_READY":
        return []

    snapshots = []
    for sample in cohort["samples"]:
        if not isinstance(sample, Mapping):
            continue
        if not _snapshot_valid(sample):
            continue
        snapshots.append(sample["recurrence_snapshot"])
    return snapshots



def extract_clean_external_candidate_snapshots(
    cohort: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> list[Mapping[str, Any]]:
    """Runtime-only: extrae únicamente holdouts externos limpios y preregistrados."""

    if policy is None:
        policy = load_external_recurrence_cohort_policy()

    summary = validate_external_recurrence_cohort(
        cohort,
        policy=policy,
    )
    if summary["state"] != "PROTOCOL_READY":
        return []

    snapshots: list[Mapping[str, Any]] = []
    for sample in cohort["samples"]:
        if not isinstance(sample, Mapping):
            continue
        if sample.get("validation_status") not in policy[
            "external_candidate_statuses"
        ]:
            continue
        if sample.get("selection_status") != "PREREGISTERED":
            continue
        if sample.get("contamination") is not False:
            continue
        if any(
            int(sample.get(field, 0)) != 0
            for field in (
                "forbidden_field_hits",
                "label_leakage_count",
                "narrative_leakage_count",
                "case_fitting_count",
            )
        ):
            continue
        if not _snapshot_valid(sample):
            continue
        snapshots.append(sample["recurrence_snapshot"])

    return snapshots
