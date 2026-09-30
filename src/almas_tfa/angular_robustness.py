"""Diagnostic retention audit for angle-dependent roots under time shifts."""
from __future__ import annotations

from typing import Any, Mapping

TIME_OFFSETS = (-15, -10, -5, -2, 2, 5, 10, 15)
SUBJECTS = ("A", "B")


def evaluate_angular_robustness(
    baseline_angular_root_ids: list[str],
    perturbation_samples: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize preserved angle-root IDs across preregistered time shifts.

    This is an ordinal diagnostic only. It does not alter IRC, IAT, IEM,
    structural roots, or phase status. Samples must already have been
    recalculated by the caller under the same chart and aspect policies.
    """
    if not isinstance(baseline_angular_root_ids, list) or not isinstance(perturbation_samples, list):
        raise ValueError("baseline IDs and perturbation samples must be lists.")
    baseline = set()
    for root_id in baseline_angular_root_ids:
        if not isinstance(root_id, str) or not root_id.strip():
            raise ValueError("baseline angular root IDs must be non-empty text.")
        baseline.add(root_id)
    if not baseline:
        return {
            "status": "NOT_EVALUABLE",
            "angular_robustness": "NOT_EVALUABLE",
            "baseline_angular_root_count": 0,
            "sample_count": 0,
            "minimum_preserved_fraction": None,
            "samples": [],
            "threshold_policy_id": "ALMAS_ANGULAR_ROBUSTNESS_V1",
            "score_created": False,
        }

    sample_map: dict[tuple[str, int], set[str]] = {}
    for sample in perturbation_samples:
        if not isinstance(sample, Mapping):
            raise ValueError("each perturbation sample must be an object.")
        subject, offset = sample.get("subject"), sample.get("offset_minutes")
        roots = sample.get("surviving_angular_root_ids")
        if subject not in SUBJECTS or isinstance(offset, bool) or offset not in TIME_OFFSETS:
            raise ValueError("samples require subject A/B and offset ±2/5/10/15 minutes.")
        key = (subject, int(offset))
        if key in sample_map:
            raise ValueError("duplicate subject/time-offset sample.")
        if not isinstance(roots, list) or not all(isinstance(root, str) for root in roots):
            raise ValueError("surviving_angular_root_ids must be a list of IDs.")
        sample_map[key] = set(roots)

    expected = {(subject, offset) for subject in SUBJECTS for offset in TIME_OFFSETS}
    if set(sample_map) != expected:
        return {
            "status": "NOT_EVALUABLE",
            "angular_robustness": "NOT_EVALUABLE",
            "baseline_angular_root_count": len(baseline),
            "sample_count": len(sample_map),
            "minimum_preserved_fraction": None,
            "samples": [],
            "missing_samples": [f"{subject}:{offset}" for subject, offset in sorted(expected - set(sample_map))],
            "threshold_policy_id": "ALMAS_ANGULAR_ROBUSTNESS_V1",
            "score_created": False,
        }

    rows = []
    for (subject, offset), roots in sorted(sample_map.items()):
        fraction = len(baseline & roots) / len(baseline)
        rows.append({
            "subject": subject,
            "offset_minutes": offset,
            "preserved_fraction": fraction,
            "preserved_root_ids": sorted(baseline & roots),
        })
    minimum = min(item["preserved_fraction"] for item in rows)
    label = "HIGH" if minimum >= 0.8 else "MEDIUM" if minimum >= 0.5 else "LOW"
    return {
        "status": "CALCULATED",
        "angular_robustness": label,
        "baseline_angular_root_count": len(baseline),
        "sample_count": len(rows),
        "minimum_preserved_fraction": minimum,
        "samples": rows,
        "threshold_policy_id": "ALMAS_ANGULAR_ROBUSTNESS_V1",
        "score_created": False,
    }
