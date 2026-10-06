#!/usr/bin/env python3
from __future__ import annotations

from almas_tfa.pair_identity_validation import (
    CROSS_DYAD_OPPOSITE_POLARITY,
    DECLARED_MATCHED_DYAD,
    build_blinded_pair_identity_matrix,
    evaluate_pair_identity_holdout,
)


def main() -> int:
    dyads = [
        {
            "dyad_ref": f"D{i:03d}",
            "df_ref": f"PERSON-A-{i:03d}",
            "dm_ref": f"PERSON-B-{i:03d}",
        }
        for i in range(120)
    ]
    bundle = build_blinded_pair_identity_matrix(
        dyads,
        blinding_secret="synthetic-ci-secret",
    )

    forbidden = {
        "stratum",
        "declared_match",
        "subject_a_dyad_id",
        "subject_b_dyad_id",
        "polarity_pattern",
        "query_subject_id",
    }
    for item in bundle["blinded_pairs"]:
        if forbidden.intersection(item):
            raise AssertionError("truth leakage in blinded pair")

    scores = []
    for item in bundle["sealed_truth"]["records"]:
        if item["stratum"] == DECLARED_MATCHED_DYAD:
            score = 1.0
        elif item["stratum"] == CROSS_DYAD_OPPOSITE_POLARITY:
            score = 0.0
        else:
            score = -0.5
        scores.append({"pair_id": item["pair_id"], "score": score})

    result = evaluate_pair_identity_holdout(
        scores,
        bundle["sealed_truth"],
        threshold=0.5,
    )
    if result["confirmatory_gate"]["state"] != "PASS_OPERATIONAL_GATE":
        raise AssertionError("synthetic perfect separation must pass")
    if result["confirmatory_gate"]["l3_promotion_authorized"] is not False:
        raise AssertionError("pair identity validation must not auto-promote L3")
    if result["declared_match_is_metaphysical_ground_truth"] is not False:
        raise AssertionError("documentary label cannot become metaphysical truth")

    print("PAIR_IDENTITY_PROTOCOL_SYNTHETIC_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
