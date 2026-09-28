import unittest
from unittest.mock import patch

from almas_tfa.module_contract import ModuleContext
from almas_tfa.ontological_discriminator import discriminate_ontology
from almas_tfa.robustness_index_handlers import m25_robustness


def context(raw=None, canonical=None):
    return ModuleContext(
        module_id="M25",
        module_name="robustness",
        mode="FULL",
        raw_input=raw or {},
        canonical_snapshot=canonical or {},
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
                [
                    "SOULMATE_MODEL",
                    "MONADIC_ORIGIN"
                ]
            ],
            "root_key_prefix": "TEST_L3:",
            "frozen": {
                "almas_version": "TEST",
                "commit_sha": "test-sha",
                "rule_ref": "TEST-RULE",
                "schema_refs": [
                    "TEST-SCHEMA"
                ]
            },
            "validation_evidence": {
                "preregistration_refs": [
                    "PREREG-1"
                ],
                "independent_replication_refs": [
                    "REPL-1"
                ],
                "external_holdout_refs": [
                    "HOLDOUT-1"
                ],
                "negative_control_refs": [
                    "NEG-1"
                ],
                "leakage_audit_refs": [
                    "LEAK-1"
                ]
            },
            "discriminant_validation": {
                "policy_id": "ALMAS_DISCRIMINANT_VALIDATION_V1",
                "evaluation_refs": ["EVAL-1"],
                "development_evaluation_disjoint": True,
                "pairwise_results": [
                    {
                        "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                        "positive_model": "MONADIC_ORIGIN",
                        "tp": 240,
                        "tn": 480,
                        "fp": 10,
                        "fn": 20
                    }
                ],
                "false_specificity": {
                    "evaluable_count": 100,
                    "error_count": 0
                },
                "synthetic_adversarial": {
                    "evaluable_count": 100,
                    "false_specificity_count": 0
                },
                "calibration": {
                    "mode": "NOT_APPLICABLE_CATEGORICAL",
                    "passed": None,
                    "criterion_ref": None,
                    "refs": []
                }
            },
            "blinding_audit": {
                "policy_id": "ALMAS_BLINDING_LEAKAGE_V1",
                "audit_refs": ["BLIND-AUDIT-1"],
                "structural_input_refs": ["STRUCT-IN-1"],
                "structural_input_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "pre_reveal_output_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "post_reveal_structural_output_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "development_evaluation_disjoint": True,
                "labels_hidden": True,
                "narrative_hidden": True,
                "expected_result_hidden": True,
                "holdout_outcome_hidden": True,
                "late_reveal_performed": True,
                "structural_output_invariant_after_reveal": True,
                "forbidden_field_hits": 0,
                "label_leakage_count": 0,
                "narrative_leakage_count": 0,
                "case_fitting_count": 0,
                "post_holdout_rule_change_count": 0,
                "identity_visibility": "HIDDEN",
                "identity_risk_refs": [],
            },
            "uses_astrology": False,
            "astrology_validation": None,
            "block_reason": None
        }
    ]
}


def component(
    *,
    validation_level="L3_VALIDATED",
    root_key="TEST_L3:ROOT_1",
    source_module="M21",
    value=0.7,
    discriminator_id="TEST_L3",
    promotion_ref="PROMO:TEST_L3:1",
):
    return {
        "id": "ONTOLOGY_DISC",
        "kind": "VALIDATED_DISCRIMINATOR",
        "value": value,
        "source_module": source_module,
        "preregistration_ref": "PREREG-ONTOLOGY-001",
        "derivation_ref": root_key,
        "validation_level": validation_level,
        "root_key": root_key,
        "discriminator_id": discriminator_id,
        "promotion_ref": promotion_ref,
    }


def ontology_output(level, *, root_key="TEST_L3:ROOT_1", excluded="SOULMATE_MODEL"):
    return discriminate_ontology(
        [
            {
                "discriminator_id": "TEST_L3",
                "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                "validation_level": level,
                "result": "SEPARATES",
                "excluded_model": excluded,
                "root_key": root_key,
            }
        ],
        mode="EXPLORATORY" if level == "L2_EXPERIMENTAL" else "CONFIRMATORY",
    )


class TestM25ValidatedOntologicalDiscriminator(unittest.TestCase):

    def test_l1_cannot_enter_irc_as_validated_discriminator(self):
        raw = {
            "robustness_component_summaries": [
                component(validation_level="L1_DOCTRINAL")
            ]
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw=raw))

    def test_l2_cannot_enter_irc_even_if_present_in_m21_exploratory_view(self):
        raw = {
            "robustness_component_summaries": [
                component(
                    validation_level="L2_EXPERIMENTAL",
                    root_key="TEST_L3:ROOT_L2",
                )
            ]
        }
        canonical = {
            "ontological_discrimination": ontology_output(
                "L2_EXPERIMENTAL",
                root_key="TEST_L3:ROOT_L2",
            )
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_l3_requires_canonical_m21_support(self):
        raw = {
            "robustness_component_summaries": [
                component()
            ]
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw=raw))

    def test_l3_requires_matching_validated_root(self):
        raw = {
            "robustness_component_summaries": [
                component(root_key="TEST_L3:ROOT_NOT_PRESENT")
            ]
        }
        canonical = {
            "ontological_discrimination": ontology_output(
                "L3_VALIDATED",
                root_key="TEST_L3:ROOT_REAL",
            )
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_l3_must_come_from_m21(self):
        raw = {
            "robustness_component_summaries": [
                component(source_module="EXTERNAL")
            ]
        }
        canonical = {
            "ontological_discrimination": ontology_output(
                "L3_VALIDATED",
            )
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_unregistered_l3_is_rejected_even_with_confirmatory_m21_root(self):
        raw = {
            "robustness_component_summaries": [
                component(
                    discriminator_id="OD01_PAIR_SPECIFICITY_NETWORK",
                    promotion_ref="FAKE",
                    root_key="OD01:ROOT_1",
                )
            ]
        }
        canonical = {
            "ontological_discrimination": discriminate_ontology(
                [
                    {
                        "discriminator_id": "OD01_PAIR_SPECIFICITY_NETWORK",
                        "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                        "validation_level": "L3_VALIDATED",
                        "result": "SEPARATES",
                        "excluded_model": "SOULMATE_MODEL",
                        "root_key": "OD01:ROOT_1",
                    }
                ]
            )
        }

        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_conflicting_l3_pair_does_not_authorize_irc_component(self):
        ontology = discriminate_ontology(
            [
                {
                    "discriminator_id": "TEST_L3",
                    "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                    "validation_level": "L3_VALIDATED",
                    "result": "SEPARATES",
                    "excluded_model": "SOULMATE_MODEL",
                    "root_key": "TEST_L3:ROOT_A",
                },
                {
                    "discriminator_id": "TEST_L3",
                    "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                    "validation_level": "L3_VALIDATED",
                    "result": "SEPARATES",
                    "excluded_model": "MONADIC_ORIGIN",
                    "root_key": "TEST_L3:ROOT_B",
                },
            ]
        )
        raw = {
            "robustness_component_summaries": [
                component(root_key="TEST_L3:ROOT_A")
            ]
        }
        canonical = {"ontological_discrimination": ontology}

        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_matching_registered_l3_root_can_enter_irc(self):
        raw = {
            "robustness_component_summaries": [
                component(value=0.64)
            ]
        }
        canonical = {
            "ontological_discrimination": ontology_output(
                "L3_VALIDATED",
            )
        }

        with patch(
            "almas_tfa.discriminator_promotion_registry."
            "load_discriminator_promotion_registry",
            return_value=synthetic_l3_registry(),
        ):
            result = m25_robustness(context(raw, canonical))

        output = result.canonical_updates["robustness_index"]

        self.assertEqual(output["component_count"], 1)
        self.assertAlmostEqual(output["irc"], 64.0)
        self.assertAlmostEqual(output["r_min"], 0.64)
        self.assertEqual(
            output["components"][0]["kind"],
            "VALIDATED_DISCRIMINATOR",
        )
        self.assertEqual(
            output["components"][0]["source_module"],
            "M21",
        )

    def test_non_discriminator_components_keep_previous_behavior(self):
        raw = {
            "robustness_component_summaries": [
                {
                    "id": "PARAMETERS",
                    "kind": "PARAMETER_PERTURBATION",
                    "value": 0.81,
                    "source_module": "EXTERNAL",
                    "preregistration_ref": "PREREG-PARAM",
                    "derivation_ref": "PARAM-RULE",
                }
            ]
        }

        result = m25_robustness(context(raw=raw))
        output = result.canonical_updates["robustness_index"]

        self.assertAlmostEqual(output["irc"], 81.0)
        self.assertAlmostEqual(output["r_min"], 0.81)


if __name__ == "__main__":
    unittest.main()
