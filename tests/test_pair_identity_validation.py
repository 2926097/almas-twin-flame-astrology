import copy
import json
import unittest

from almas_tfa.pair_identity_validation import (
    CROSS_DYAD_OPPOSITE_POLARITY,
    CROSS_DYAD_SAME_POLARITY_DF,
    CROSS_DYAD_SAME_POLARITY_DM,
    DECLARED_MATCHED_DYAD,
    build_blinded_pair_identity_matrix,
    evaluate_pair_identity_holdout,
    load_pair_identity_validation_policy,
    validate_partition_disjointness,
)


def dyads(n=4):
    return [
        {
            "dyad_ref": f"D{i:03d}",
            "df_ref": f"A{i:03d}",
            "dm_ref": f"B{i:03d}",
        }
        for i in range(n)
    ]


def bundle(n=4):
    return build_blinded_pair_identity_matrix(
        dyads(n),
        blinding_secret="unit-test-secret",
    )


def perfect_scores(data):
    values = []
    for item in data["sealed_truth"]["records"]:
        if item["stratum"] == DECLARED_MATCHED_DYAD:
            score = 1.0
        elif item["stratum"] == CROSS_DYAD_OPPOSITE_POLARITY:
            score = 0.0
        else:
            score = -1.0
        values.append({"pair_id": item["pair_id"], "score": score})
    return values


class TestPairIdentityValidation(unittest.TestCase):

    def test_policy_is_explicit_project_policy_and_no_l3(self):
        policy = load_pair_identity_validation_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_PAIR_IDENTITY_VALIDATION_V1",
        )
        self.assertEqual(policy["epistemic_class"], "E_PROJECT_POLICY")
        self.assertTrue(
            policy["interpretive_firewall"][
                "declared_match_is_documentary_not_metaphysical_truth"
            ]
        )
        self.assertTrue(
            policy["interpretive_firewall"]["l3_promotion_is_not_automatic"]
        )

    def test_matrix_builds_primary_and_same_polarity_strata(self):
        data = bundle(4)
        counts = data["matrix_summary"]["stratum_counts"]
        self.assertEqual(counts[DECLARED_MATCHED_DYAD], 4)
        self.assertEqual(counts[CROSS_DYAD_OPPOSITE_POLARITY], 4)
        self.assertEqual(counts[CROSS_DYAD_SAME_POLARITY_DF], 2)
        self.assertEqual(counts[CROSS_DYAD_SAME_POLARITY_DM], 2)
        self.assertEqual(data["matrix_summary"]["pair_count"], 12)

    def test_blinded_pairs_contain_no_truth_or_original_refs(self):
        data = bundle(4)
        serialized = json.dumps(data["blinded_pairs"], sort_keys=True)
        for token in (
            "stratum",
            "declared_match",
            "polarity_pattern",
            "subject_a_dyad_id",
            "subject_b_dyad_id",
            "D000",
            "A000",
            "B000",
        ):
            self.assertNotIn(token, serialized)
        for item in data["blinded_pairs"]:
            self.assertEqual(
                set(item),
                {"pair_id", "subject_a_id", "subject_b_id"},
            )

    def test_cross_opposite_never_uses_same_declared_dyad(self):
        data = bundle(8)
        for item in data["sealed_truth"]["records"]:
            if item["stratum"] == CROSS_DYAD_OPPOSITE_POLARITY:
                self.assertNotEqual(
                    item["subject_a_dyad_id"],
                    item["subject_b_dyad_id"],
                )

    def test_odd_same_polarity_matrix_fails_closed(self):
        with self.assertRaises(ValueError):
            bundle(3)

    def test_extra_narrative_fields_are_rejected(self):
        bad = dyads(4)
        bad[0]["relationship_narrative"] = "should never enter builder"
        with self.assertRaises(ValueError):
            build_blinded_pair_identity_matrix(
                bad,
                blinding_secret="unit-test-secret",
            )

    def test_subject_reuse_between_declared_dyads_is_rejected(self):
        bad = dyads(4)
        bad[1]["df_ref"] = bad[0]["df_ref"]
        with self.assertRaises(ValueError):
            build_blinded_pair_identity_matrix(
                bad,
                blinding_secret="unit-test-secret",
            )

    def test_partitions_must_be_subject_disjoint(self):
        result = validate_partition_disjointness(
            {
                "development": ["S1", "S2"],
                "holdout": ["S3", "S4"],
                "replication": ["S5", "S6"],
            }
        )
        self.assertEqual(result["state"], "DISJOINT")
        with self.assertRaises(ValueError):
            validate_partition_disjointness(
                {
                    "development": ["S1", "S2"],
                    "holdout": ["S2", "S3"],
                }
            )

    def test_perfect_120_dyad_synthetic_holdout_passes_operational_gate(self):
        data = bundle(120)
        result = evaluate_pair_identity_holdout(
            perfect_scores(data),
            data["sealed_truth"],
            threshold=0.5,
        )
        primary = result["metrics_by_negative_stratum"][
            CROSS_DYAD_OPPOSITE_POLARITY
        ]
        self.assertEqual(primary["roc_auc"], 1.0)
        self.assertEqual(primary["fp"], 0)
        self.assertEqual(result["confirmatory_gate"]["state"], "PASS_OPERATIONAL_GATE")
        self.assertFalse(result["confirmatory_gate"]["l3_promotion_authorized"])
        self.assertFalse(result["confirmatory_gate"]["ontology_activation"])
        self.assertFalse(result["declared_match_is_metaphysical_ground_truth"])
        self.assertFalse(result["metaphysical_probability"])

    def test_one_false_positive_among_120_can_still_pass_wilson_ceiling(self):
        data = bundle(120)
        scores = perfect_scores(data)
        cross_ids = [
            item["pair_id"]
            for item in data["sealed_truth"]["records"]
            if item["stratum"] == CROSS_DYAD_OPPOSITE_POLARITY
        ]
        for item in scores:
            if item["pair_id"] == cross_ids[0]:
                item["score"] = 0.75
        result = evaluate_pair_identity_holdout(
            scores,
            data["sealed_truth"],
            threshold=0.5,
        )
        primary = result["metrics_by_negative_stratum"][
            CROSS_DYAD_OPPOSITE_POLARITY
        ]
        self.assertEqual(primary["fp"], 1)
        self.assertLessEqual(primary["false_specificity_ci95_upper"], 0.05)
        self.assertTrue(result["confirmatory_gate"]["passed"])

    def test_two_false_positives_among_120_fail_false_specificity_gate(self):
        data = bundle(120)
        scores = perfect_scores(data)
        cross_ids = [
            item["pair_id"]
            for item in data["sealed_truth"]["records"]
            if item["stratum"] == CROSS_DYAD_OPPOSITE_POLARITY
        ]
        changed = 0
        for item in scores:
            if item["pair_id"] in set(cross_ids[:2]):
                item["score"] = 0.75
                changed += 1
        self.assertEqual(changed, 2)
        result = evaluate_pair_identity_holdout(
            scores,
            data["sealed_truth"],
            threshold=0.5,
        )
        primary = result["metrics_by_negative_stratum"][
            CROSS_DYAD_OPPOSITE_POLARITY
        ]
        self.assertEqual(primary["fp"], 2)
        self.assertGreater(primary["false_specificity_ci95_upper"], 0.05)
        self.assertFalse(result["confirmatory_gate"]["passed"])

    def test_incomplete_score_coverage_fails_closed(self):
        data = bundle(4)
        scores = perfect_scores(data)[:-1]
        with self.assertRaises(ValueError):
            evaluate_pair_identity_holdout(
                scores,
                data["sealed_truth"],
                threshold=0.5,
            )

    def test_truth_stratum_and_declared_match_must_agree(self):
        data = bundle(4)
        tampered = copy.deepcopy(data["sealed_truth"])
        tampered["records"][0]["declared_match"] = not tampered["records"][0][
            "declared_match"
        ]
        with self.assertRaises(ValueError):
            evaluate_pair_identity_holdout(
                perfect_scores(data),
                tampered,
                threshold=0.5,
            )


if __name__ == "__main__":
    unittest.main()
