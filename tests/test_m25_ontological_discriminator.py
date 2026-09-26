import unittest

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


def component(
    *,
    validation_level="L3_VALIDATED",
    root_key="ROOT_L3",
    source_module="M21",
    value=0.7,
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
    }


def ontology_output(level, *, root_key="ROOT_L3", excluded="SOULMATE_MODEL"):
    return discriminate_ontology(
        [
            {
                "discriminator_id": "D-TEST",
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
                    root_key="ROOT_L2",
                )
            ]
        }
        canonical = {
            "ontological_discrimination": ontology_output(
                "L2_EXPERIMENTAL",
                root_key="ROOT_L2",
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
                component(root_key="ROOT_NOT_PRESENT")
            ]
        }
        canonical = {
            "ontological_discrimination": ontology_output(
                "L3_VALIDATED",
                root_key="ROOT_REAL",
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
                root_key="ROOT_L3",
            )
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_conflicting_l3_pair_does_not_authorize_irc_component(self):
        ontology = discriminate_ontology(
            [
                {
                    "discriminator_id": "D-A",
                    "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                    "validation_level": "L3_VALIDATED",
                    "result": "SEPARATES",
                    "excluded_model": "SOULMATE_MODEL",
                    "root_key": "ROOT_A",
                },
                {
                    "discriminator_id": "D-B",
                    "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                    "validation_level": "L3_VALIDATED",
                    "result": "SEPARATES",
                    "excluded_model": "MONADIC_ORIGIN",
                    "root_key": "ROOT_B",
                },
            ]
        )
        raw = {
            "robustness_component_summaries": [
                component(root_key="ROOT_A")
            ]
        }
        canonical = {"ontological_discrimination": ontology}

        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_matching_l3_root_can_enter_irc(self):
        raw = {
            "robustness_component_summaries": [
                component(value=0.64)
            ]
        }
        canonical = {
            "ontological_discrimination": ontology_output(
                "L3_VALIDATED",
                root_key="ROOT_L3",
            )
        }

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
