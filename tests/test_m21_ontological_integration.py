import unittest

from almas_tfa.handlers import m21_differential_discrimination
from almas_tfa.module_contract import ExecutionStatus, ModuleContext


def context(raw_input):
    return ModuleContext(
        module_id="M21",
        module_name="differential_attribution_discrimination",
        mode="FULL",
        raw_input=raw_input,
        canonical_snapshot={},
        prior_results={},
    )


class TestM21OntologicalIntegration(unittest.TestCase):

    def test_legacy_m21_shape_is_preserved_without_ontology_input(self):
        result = m21_differential_discrimination(
            context(
                {
                    "attributions": {
                        "AG": {"r1": 1.0},
                        "LG": {"r2": 1.0},
                    }
                }
            )
        )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertEqual(
            set(result.canonical_updates),
            {"pairwise_idd"},
        )
        self.assertNotIn("ontological_discrimination", result.canonical_updates)
        self.assertIn("AG_vs_LG", result.payload)
        self.assertEqual(result.limitations, ())
        self.assertEqual(result.diagnostics, ())

    def test_high_idd_cannot_promote_l2_ontology(self):
        result = m21_differential_discrimination(
            context(
                {
                    "attributions": {
                        "AG": {"ag_root": 1.0},
                        "LG": {"lg_root": 1.0},
                    },
                    "ontological_discriminator_input": {
                        "mode": "EXPLORATORY",
                        "observations": [
                            {
                                "discriminator_id": "OD01",
                                "pair": [
                                    "SOULMATE_MODEL",
                                    "TWIN_FLAME_MODEL",
                                ],
                                "validation_level": "L2_EXPERIMENTAL",
                                "result": "SEPARATES",
                                "excluded_model": "SOULMATE_MODEL",
                                "root_key": "PAIR_SPECIFICITY",
                            }
                        ],
                    },
                }
            )
        )

        self.assertEqual(
            result.canonical_updates["pairwise_idd"]["AG_vs_LG"]["idd"],
            100.0,
        )

        ontology = result.canonical_updates["ontological_discrimination"]
        self.assertEqual(ontology["confirmed_exclusions"], [])
        self.assertEqual(len(ontology["surviving_models"]), 4)
        self.assertEqual(
            ontology["identifiability_state"],
            "NON_IDENTIFIABLE",
        )
        self.assertEqual(
            ontology["exploratory_view"]["experimental_only_exclusions"],
            ["SOULMATE_MODEL"],
        )
        self.assertFalse(ontology["rules"]["l2_can_confirm"])
        self.assertFalse(ontology["rules"]["scores_can_break_equivalence"])

    def test_ontology_can_be_evaluated_when_idd_is_not_available(self):
        result = m21_differential_discrimination(
            context(
                {
                    "ontological_discriminator_input": {
                        "observations": [
                            {
                                "discriminator_id": "L3-SM",
                                "pair": [
                                    "SOULMATE_MODEL",
                                    "MONADIC_ORIGIN",
                                ],
                                "validation_level": "L3_VALIDATED",
                                "result": "SEPARATES",
                                "excluded_model": "SOULMATE_MODEL",
                                "root_key": "VALIDATED_ROOT",
                            }
                        ]
                    }
                }
            )
        )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertNotIn("pairwise_idd", result.canonical_updates)

        ontology = result.canonical_updates["ontological_discrimination"]
        self.assertEqual(
            ontology["surviving_models"],
            ["MONADIC_ORIGIN", "SPLIT_SOUL", "TWIN_FLAME_MODEL"],
        )
        self.assertEqual(
            ontology["classification"],
            "SHARED_ORIGIN_UNDIFFERENTIATED",
        )
        self.assertEqual(
            ontology["epistemic_state"],
            "INSUFFICIENT",
        )

    def test_ontology_result_is_invariant_to_idd_geometry(self):
        ontology_input = {
            "observations": [
                {
                    "discriminator_id": "OD01",
                    "pair": ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
                    "validation_level": "L2_EXPERIMENTAL",
                    "result": "SEPARATES",
                    "excluded_model": "SOULMATE_MODEL",
                    "root_key": "PAIR_SPECIFICITY",
                }
            ]
        }

        high_idd = m21_differential_discrimination(
            context(
                {
                    "attributions": {
                        "AG": {"a": 1.0},
                        "LG": {"b": 1.0},
                    },
                    "ontological_discriminator_input": ontology_input,
                }
            )
        )

        zero_idd = m21_differential_discrimination(
            context(
                {
                    "attributions": {
                        "AG": {"same": 1.0},
                        "LG": {"same": 1.0},
                    },
                    "ontological_discriminator_input": ontology_input,
                }
            )
        )

        self.assertEqual(
            high_idd.canonical_updates["pairwise_idd"]["AG_vs_LG"]["idd"],
            100.0,
        )
        self.assertEqual(
            zero_idd.canonical_updates["pairwise_idd"]["AG_vs_LG"]["idd"],
            0.0,
        )
        self.assertEqual(
            high_idd.canonical_updates["ontological_discrimination"],
            zero_idd.canonical_updates["ontological_discrimination"],
        )

    def test_invalid_ontology_config_is_rejected_explicitly(self):
        with self.assertRaises(ValueError):
            m21_differential_discrimination(
                context(
                    {
                        "attributions": {
                            "AG": {"r1": 1.0},
                            "LG": {"r2": 1.0},
                        },
                        "ontological_discriminator_input": [],
                    }
                )
            )


if __name__ == "__main__":
    unittest.main()
