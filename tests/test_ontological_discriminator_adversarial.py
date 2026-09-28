import copy
import unittest
from unittest.mock import patch

from almas_tfa.handlers import m21_differential_discrimination
from almas_tfa.module_contract import ModuleContext
from almas_tfa.ontological_discriminator import discriminate_ontology


MODELS = [
    "SOULMATE_MODEL",
    "MONADIC_ORIGIN",
    "SPLIT_SOUL",
    "TWIN_FLAME_MODEL",
]


def obs(
    discriminator_id,
    pair,
    validation_level,
    result,
    *,
    excluded_model=None,
    root_key=None,
    promotion_ref=None,
):
    value = {
        "discriminator_id": discriminator_id,
        "pair": list(pair),
        "validation_level": validation_level,
        "result": result,
    }
    if excluded_model is not None:
        value["excluded_model"] = excluded_model
    if root_key is not None:
        value["root_key"] = root_key
    if promotion_ref is not None:
        value["promotion_ref"] = promotion_ref
    return value


def m21_context(raw_input):
    return ModuleContext(
        module_id="M21",
        module_name="differential_attribution_discrimination",
        mode="FULL",
        raw_input=raw_input,
        canonical_snapshot={},
        prior_results={},
    )


def synthetic_l3_registry():
    return {
        "records": [
            {
                "discriminator_id": "TEST_L3",
                "current_status": "VALIDATED_DISCRIMINATOR",
                "l3_authorized": True,
                "promotion_ref": "PROMO:TEST_L3:1",
                "promoted_at": "2026-09-26T00:00:00Z",
                "validated_pairs": [
                    ["SOULMATE_MODEL", "MONADIC_ORIGIN"]
                ],
                "root_key_prefix": "TEST_L3:",
                "frozen": {
                    "almas_version": "TEST",
                    "commit_sha": "test-sha",
                    "rule_ref": "TEST-RULE",
                    "schema_refs": ["TEST-SCHEMA"],
                },
                "validation_evidence": {
                    "preregistration_refs": ["PREREG-1"],
                    "independent_replication_refs": ["REPL-1"],
                    "external_holdout_refs": ["HOLDOUT-1"],
                    "negative_control_refs": ["NEG-1"],
                    "leakage_audit_refs": ["LEAK-1"],
                },
                "block_reason": None,
            }
        ]
    }


def canonical_decision(output):
    return {
        "confirmed_exclusions": output["confirmed_exclusions"],
        "surviving_models": output["surviving_models"],
        "identifiability_state": output["identifiability_state"],
        "epistemic_state": output["epistemic_state"],
        "classification": output["classification"],
    }


class TestOntologicalDiscriminatorAdversarial(unittest.TestCase):

    def test_l2_flood_cannot_create_confirmatory_exclusion(self):
        attack_pairs = [
            (
                ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                "SOULMATE_MODEL",
            ),
            (
                ("MONADIC_ORIGIN", "SPLIT_SOUL"),
                "MONADIC_ORIGIN",
            ),
            (
                ("SPLIT_SOUL", "TWIN_FLAME_MODEL"),
                "SPLIT_SOUL",
            ),
            (
                ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                "TWIN_FLAME_MODEL",
            ),
        ]
        observations = []
        index = 0
        for pair, excluded_model in attack_pairs:
            for _ in range(12):
                observations.append(
                    obs(
                        f"L2-{index}",
                        pair,
                        "L2_EXPERIMENTAL",
                        "SEPARATES",
                        excluded_model=excluded_model,
                        root_key=f"L2ROOT-{index}",
                    )
                )
                index += 1

        result = discriminate_ontology(
            observations,
            mode="EXPLORATORY",
        )

        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertEqual(result["surviving_models"], MODELS)
        self.assertEqual(result["classification"], "INDETERMINATE")
        self.assertEqual(result["identifiability_state"], "NON_IDENTIFIABLE")
        self.assertEqual(result["epistemic_state"], "INSUFFICIENT")
        self.assertTrue(result["exploratory_view"]["conflict"])
        self.assertEqual(
            result["exploratory_view"]["surviving_models"],
            MODELS,
        )
        self.assertTrue(
            result["exploratory_view"]["canonical_decision_unchanged"]
        )

    def test_l1_flood_cannot_create_confirmatory_exclusion(self):
        observations = [
            obs(
                f"L1-{i}",
                ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                "L1_DOCTRINAL",
                "SEPARATES",
                excluded_model="SOULMATE_MODEL",
                root_key=f"L1ROOT-{i}",
            )
            for i in range(100)
        ]

        result = discriminate_ontology(observations)

        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertEqual(result["surviving_models"], MODELS)
        self.assertEqual(result["classification"], "INDETERMINATE")

    def test_repeating_same_l3_root_does_not_create_independent_roots(self):
        observations = [
            obs(
                f"L3-ALIAS-{i}",
                ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                "L3_VALIDATED",
                "SEPARATES",
                excluded_model="SOULMATE_MODEL",
                root_key="ONE_VALIDATED_ROOT",
            )
            for i in range(25)
        ]

        result = discriminate_ontology(observations)
        pair = result["pairwise_matrix"][
            "SOULMATE_MODEL_vs_MONADIC_ORIGIN"
        ]

        self.assertEqual(pair["confirmatory_status"], "SEPARABLE_VALIDATED")
        self.assertEqual(pair["validated_roots"], ["ONE_VALIDATED_ROOT"])
        self.assertEqual(
            result["surviving_models"],
            ["MONADIC_ORIGIN", "SPLIT_SOUL", "TWIN_FLAME_MODEL"],
        )
        self.assertEqual(
            result["classification"],
            "SHARED_ORIGIN_UNDIFFERENTIATED",
        )

    def test_same_root_l3_internal_conflict_cannot_exclude(self):
        result = discriminate_ontology(
            [
                obs(
                    "L3-A",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="SAME_ROOT",
                ),
                obs(
                    "L3-B",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "NO_SEPARATION",
                    root_key="SAME_ROOT",
                ),
            ]
        )

        pair = result["pairwise_matrix"][
            "SOULMATE_MODEL_vs_TWIN_FLAME_MODEL"
        ]
        self.assertEqual(pair["confirmatory_status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertEqual(result["surviving_models"], MODELS)
        self.assertTrue(pair["conflicts"])
        self.assertEqual(result["epistemic_state"], "INSUFFICIENT")

    def test_global_elimination_cycle_is_revoked(self):
        result = discriminate_ontology(
            [
                obs(
                    "L3-SM",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="R-SM",
                ),
                obs(
                    "L3-MP",
                    ("MONADIC_ORIGIN", "SPLIT_SOUL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="MONADIC_ORIGIN",
                    root_key="R-MP",
                ),
                obs(
                    "L3-PT",
                    ("SPLIT_SOUL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SPLIT_SOUL",
                    root_key="R-PT",
                ),
                obs(
                    "L3-ST",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="TWIN_FLAME_MODEL",
                    root_key="R-ST",
                ),
            ]
        )

        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertEqual(result["surviving_models"], MODELS)
        self.assertEqual(result["classification"], "INDETERMINATE")
        self.assertEqual(result["identifiability_state"], "NON_IDENTIFIABLE")
        self.assertTrue(
            any(
                conflict["root_key"] == "GLOBAL_ELIMINATION_CYCLE"
                for conflict in result["conflicts"]
            )
        )

    def test_not_evaluable_noise_does_not_become_counterevidence(self):
        baseline = discriminate_ontology([])
        noisy = discriminate_ontology(
            [
                obs(
                    f"NE-{i}",
                    ("MONADIC_ORIGIN", "SPLIT_SOUL"),
                    "L3_VALIDATED",
                    "NOT_EVALUABLE",
                    root_key=f"NE-{i}",
                )
                for i in range(50)
            ]
        )

        self.assertEqual(
            canonical_decision(noisy),
            canonical_decision(baseline),
        )
        self.assertEqual(noisy["confirmed_exclusions"], [])

    def test_complete_l3_no_separation_is_not_overridden_by_l2_flood(self):
        observations = [
            obs(
                "L3-NO-SEP",
                ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                "L3_VALIDATED",
                "NO_SEPARATION",
                root_key="L3-NO-SEP",
            )
        ]
        observations.extend(
            obs(
                f"L2-SEP-{i}",
                ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                "L2_EXPERIMENTAL",
                "SEPARATES",
                excluded_model="SOULMATE_MODEL",
                root_key=f"L2-SEP-{i}",
            )
            for i in range(50)
        )

        result = discriminate_ontology(
            observations,
            mode="EXPLORATORY",
            pair_coverage={
                "SOULMATE_MODEL_vs_TWIN_FLAME_MODEL": "COMPLETE",
            },
        )

        pair = result["pairwise_matrix"][
            "SOULMATE_MODEL_vs_TWIN_FLAME_MODEL"
        ]
        self.assertEqual(
            pair["confirmatory_status"],
            "OBSERVATIONALLY_EQUIVALENT",
        )
        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertIn("SOULMATE_MODEL", result["surviving_models"])

    def test_l3_for_one_pair_does_not_validate_unrelated_pairs(self):
        result = discriminate_ontology(
            [
                obs(
                    "L3-SM",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="ONLY-SM",
                )
            ]
        )

        unrelated = result["pairwise_matrix"][
            "MONADIC_ORIGIN_vs_SPLIT_SOUL"
        ]
        self.assertEqual(
            unrelated["confirmatory_status"],
            "INSUFFICIENT_EVIDENCE",
        )
        self.assertEqual(unrelated["validated_roots"], [])
        self.assertEqual(
            result["classification"],
            "SHARED_ORIGIN_UNDIFFERENTIATED",
        )

    def test_minimum_data_failure_defeats_l3_flood(self):
        observations = [
            obs(
                f"L3-{i}",
                ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                "L3_VALIDATED",
                "SEPARATES",
                excluded_model="SOULMATE_MODEL",
                root_key=f"L3ROOT-{i}",
            )
            for i in range(50)
        ]

        result = discriminate_ontology(
            observations,
            minimum_data_evaluable=False,
        )

        self.assertEqual(result["confirmed_exclusions"], [])
        self.assertEqual(result["surviving_models"], MODELS)
        self.assertEqual(result["classification"], "INDETERMINATE")
        self.assertEqual(result["identifiability_state"], "NOT_EVALUABLE")
        self.assertEqual(result["epistemic_state"], "NOT_EVALUABLE")

    def test_narrative_contamination_cannot_change_m21_ontology(self):
        ontology_input = {
            "mode": "EXPLORATORY",
            "observations": [
                obs(
                    "OD01",
                    ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
                    "L2_EXPERIMENTAL",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="OD01:ROOT",
                )
            ],
        }
        clean = m21_differential_discrimination(
            m21_context(
                {
                    "attributions": {
                        "AG": {"same": 1.0},
                        "LG": {"same": 1.0},
                    },
                    "ontological_discriminator_input": ontology_input,
                }
            )
        )
        polluted_raw = {
            "attributions": {
                "AG": {"same": 1.0},
                "LG": {"same": 1.0},
            },
            "ontological_discriminator_input": copy.deepcopy(ontology_input),
            "self_label": "TWIN_FLAME",
            "runner_chaser": True,
            "synchronicity_count": 999999,
            "subjective_intensity": 100,
            "destiny_certainty": 100,
            "astrological_rarity": 0.000001,
            "temporal_activation_claim": "REUNION_IMMINENT",
            "narrative": "La historia exige una categoría específica.",
        }
        polluted = m21_differential_discrimination(
            m21_context(polluted_raw)
        )

        self.assertEqual(
            clean.canonical_updates["ontological_discrimination"],
            polluted.canonical_updates["ontological_discrimination"],
        )

    def test_registry_rejects_wrong_validated_pair(self):
        registry = synthetic_l3_registry()
        with patch(
            "almas_tfa.discriminator_promotion_registry."
            "load_discriminator_promotion_registry",
            return_value=registry,
        ):
            with self.assertRaises(ValueError):
                m21_differential_discrimination(
                    m21_context(
                        {
                            "ontological_discriminator_input": {
                                "observations": [
                                    obs(
                                        "TEST_L3",
                                        (
                                            "SOULMATE_MODEL",
                                            "TWIN_FLAME_MODEL",
                                        ),
                                        "L3_VALIDATED",
                                        "SEPARATES",
                                        excluded_model="SOULMATE_MODEL",
                                        root_key="TEST_L3:ROOT",
                                        promotion_ref="PROMO:TEST_L3:1",
                                    )
                                ]
                            }
                        }
                    )
                )

    def test_registry_rejects_wrong_root_family(self):
        registry = synthetic_l3_registry()
        with patch(
            "almas_tfa.discriminator_promotion_registry."
            "load_discriminator_promotion_registry",
            return_value=registry,
        ):
            with self.assertRaises(ValueError):
                m21_differential_discrimination(
                    m21_context(
                        {
                            "ontological_discriminator_input": {
                                "observations": [
                                    obs(
                                        "TEST_L3",
                                        (
                                            "SOULMATE_MODEL",
                                            "MONADIC_ORIGIN",
                                        ),
                                        "L3_VALIDATED",
                                        "SEPARATES",
                                        excluded_model="SOULMATE_MODEL",
                                        root_key="FORGED:ROOT",
                                        promotion_ref="PROMO:TEST_L3:1",
                                    )
                                ]
                            }
                        }
                    )
                )

    def test_registry_rejects_incomplete_validation_evidence(self):
        registry = synthetic_l3_registry()
        registry["records"][0]["validation_evidence"][
            "external_holdout_refs"
        ] = []

        with patch(
            "almas_tfa.discriminator_promotion_registry."
            "load_discriminator_promotion_registry",
            return_value=registry,
        ):
            with self.assertRaises(ValueError):
                m21_differential_discrimination(
                    m21_context(
                        {
                            "ontological_discriminator_input": {
                                "observations": [
                                    obs(
                                        "TEST_L3",
                                        (
                                            "SOULMATE_MODEL",
                                            "MONADIC_ORIGIN",
                                        ),
                                        "L3_VALIDATED",
                                        "SEPARATES",
                                        excluded_model="SOULMATE_MODEL",
                                        root_key="TEST_L3:ROOT",
                                        promotion_ref="PROMO:TEST_L3:1",
                                    )
                                ]
                            }
                        }
                    )
                )


if __name__ == "__main__":
    unittest.main()
