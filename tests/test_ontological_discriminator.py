import unittest

from almas_tfa.ontological_discriminator import discriminate_ontology


def observation(
    discriminator_id,
    pair,
    validation_level,
    result,
    *,
    excluded_model=None,
    root_key=None,
):
    payload = {
        "discriminator_id": discriminator_id,
        "pair": list(pair),
        "validation_level": validation_level,
        "result": result,
    }
    if excluded_model is not None:
        payload["excluded_model"] = excluded_model
    if root_key is not None:
        payload["root_key"] = root_key
    return payload


class TestOntologicalDiscriminator(unittest.TestCase):

    def test_l2_never_excludes_in_confirmatory_mode(self):
        result = discriminate_ontology(
            [
                observation(
                    "OD01",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L2_EXPERIMENTAL",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="PAIR_SPECIFICITY",
                )
            ]
        )

        pair = result["pairwise_matrix"]["SOULMATE_MODEL_vs_TWIN_FLAME_MODEL"]

        self.assertEqual(pair["confirmatory_status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(pair["exploratory_status"], "SEPARABLE_EXPERIMENTAL")
        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertEqual(len(result["surviving_models"]), 4)
        self.assertEqual(result["identifiability_state"], "NON_IDENTIFIABLE")
        self.assertEqual(result["epistemic_state"], "INSUFFICIENT")

    def test_exploratory_projection_never_changes_canonical_decision(self):
        result = discriminate_ontology(
            [
                observation(
                    "OD01",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L2_EXPERIMENTAL",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                )
            ],
            mode="EXPLORATORY",
        )

        self.assertIn("SOULMATE_MODEL", result["surviving_models"])
        self.assertNotIn(
            "SOULMATE_MODEL",
            result["exploratory_view"]["surviving_models"],
        )
        self.assertTrue(
            result["exploratory_view"]["canonical_decision_unchanged"]
        )
        self.assertEqual(
            result["exploratory_view"]["experimental_only_exclusions"],
            ["SOULMATE_MODEL"],
        )

    def test_shared_origin_undifferentiated_after_partial_exclusion(self):
        result = discriminate_ontology(
            [
                observation(
                    "L3-S-v-M",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                )
            ]
        )

        self.assertEqual(
            result["surviving_models"],
            ["MONADIC_ORIGIN", "SPLIT_SOUL", "TWIN_FLAME_MODEL"],
        )
        self.assertEqual(
            result["classification"],
            "SHARED_ORIGIN_UNDIFFERENTIATED",
        )
        self.assertEqual(
            result["identifiability_state"],
            "PARTIALLY_IDENTIFIABLE",
        )
        self.assertEqual(result["epistemic_state"], "INSUFFICIENT")

    def test_single_survivor_is_identifiable_but_not_supported(self):
        result = discriminate_ontology(
            [
                observation(
                    "L3-SM",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="MONADIC_ORIGIN",
                ),
                observation(
                    "L3-SP",
                    ("SOULMATE_MODEL", "SPLIT_SOUL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SPLIT_SOUL",
                ),
                observation(
                    "L3-ST",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="TWIN_FLAME_MODEL",
                ),
            ]
        )

        self.assertEqual(result["surviving_models"], ["SOULMATE_MODEL"])
        self.assertEqual(result["classification"], "SOULMATE_MODEL")
        self.assertEqual(result["identifiability_state"], "IDENTIFIABLE")
        self.assertEqual(result["epistemic_state"], "COMPATIBLE")
        self.assertNotEqual(result["epistemic_state"], "SUPPORTED")

    def test_conflicting_validated_evidence_does_not_eliminate(self):
        result = discriminate_ontology(
            [
                observation(
                    "L3-A",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="ROOT_A",
                ),
                observation(
                    "L3-B",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="TWIN_FLAME_MODEL",
                    root_key="ROOT_B",
                ),
            ]
        )

        pair = result["pairwise_matrix"]["SOULMATE_MODEL_vs_TWIN_FLAME_MODEL"]

        self.assertEqual(pair["confirmatory_status"], "CONFLICTING_EVIDENCE")
        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertGreaterEqual(len(result["conflicts"]), 1)
        self.assertEqual(result["epistemic_state"], "INSUFFICIENT")

    def test_same_root_is_deduplicated_at_highest_validation_level(self):
        result = discriminate_ontology(
            [
                observation(
                    "OD01-exp",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L2_EXPERIMENTAL",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="UNIQUE_ROOT",
                ),
                observation(
                    "OD01-val",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="UNIQUE_ROOT",
                ),
            ]
        )

        pair = result["pairwise_matrix"]["SOULMATE_MODEL_vs_TWIN_FLAME_MODEL"]

        self.assertEqual(pair["confirmatory_status"], "SEPARABLE_VALIDATED")
        self.assertEqual(pair["validated_roots"], ["UNIQUE_ROOT"])
        self.assertEqual(pair["experimental_roots"], [])

    def test_complete_pair_coverage_can_record_observational_equivalence(self):
        result = discriminate_ontology(
            [
                observation(
                    "L3-NO-SEP",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "NO_SEPARATION",
                )
            ],
            pair_coverage={
                "SOULMATE_MODEL_vs_TWIN_FLAME_MODEL": "COMPLETE",
            },
        )

        pair = result["pairwise_matrix"]["SOULMATE_MODEL_vs_TWIN_FLAME_MODEL"]
        self.assertEqual(
            pair["confirmatory_status"],
            "OBSERVATIONALLY_EQUIVALENT",
        )

    def test_missing_minimum_data_is_not_evaluable(self):
        result = discriminate_ontology(
            [],
            minimum_data_evaluable=False,
        )

        self.assertEqual(result["identifiability_state"], "NOT_EVALUABLE")
        self.assertEqual(result["epistemic_state"], "NOT_EVALUABLE")
        self.assertEqual(result["classification"], "INDETERMINATE")
        self.assertEqual(result["equivalence_classes"], [])

    def test_all_shared_origin_survivors_never_force_specific_model(self):
        result = discriminate_ontology(
            [
                observation(
                    "L3-SM",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                )
            ],
            mode="EXPLORATORY",
        )

        self.assertTrue(result["false_specificity_guard"])
        self.assertEqual(
            result["classification"],
            "SHARED_ORIGIN_UNDIFFERENTIATED",
        )


if __name__ == "__main__":
    unittest.main()
