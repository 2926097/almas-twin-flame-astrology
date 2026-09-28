import copy
import itertools
import unittest

from almas_tfa.ontological_discriminator import (
    PairObservation,
    discriminate_ontology,
)


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
    note=None,
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
    if promotion_ref is not None:
        payload["promotion_ref"] = promotion_ref
    if note is not None:
        payload["note"] = note
    return payload


def base_observations():
    return [
        obs(
            "L3-SM",
            ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
            "L3_VALIDATED",
            "SEPARATES",
            excluded_model="SOULMATE_MODEL",
            root_key="ROOT-SM",
            promotion_ref="PROMO-SM",
        ),
        obs(
            "L3-MP",
            ("MONADIC_ORIGIN", "SPLIT_SOUL"),
            "L3_VALIDATED",
            "NO_SEPARATION",
            root_key="ROOT-MP",
            promotion_ref="PROMO-MP",
        ),
        obs(
            "L2-PT",
            ("SPLIT_SOUL", "TWIN_FLAME_MODEL"),
            "L2_EXPERIMENTAL",
            "SEPARATES",
            excluded_model="SPLIT_SOUL",
            root_key="ROOT-PT",
        ),
        obs(
            "L1-ST",
            ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
            "L1_DOCTRINAL",
            "NO_SEPARATION",
            root_key="ROOT-ST",
        ),
    ]


def canonical_decision(output):
    return {
        "confirmed_exclusions": frozenset(output["confirmed_exclusions"]),
        "surviving_models": frozenset(output["surviving_models"]),
        "identifiability_state": output["identifiability_state"],
        "epistemic_state": output["epistemic_state"],
        "classification": output["classification"],
        "false_specificity_guard": output["false_specificity_guard"],
    }


def normalized_pairwise(output):
    normalized = {}
    for assessment in output["pairwise_matrix"].values():
        key = tuple(sorted(assessment["pair"]))
        normalized[key] = {
            "coverage": assessment["coverage"],
            "confirmatory_status": assessment["confirmatory_status"],
            "exploratory_status": assessment["exploratory_status"],
            "confirmed_excluded_model": assessment[
                "confirmed_excluded_model"
            ],
            "exploratory_excluded_model": assessment[
                "exploratory_excluded_model"
            ],
            "validated_roots": tuple(sorted(assessment["validated_roots"])),
            "experimental_roots": tuple(
                sorted(assessment["experimental_roots"])
            ),
        }
    return normalized


def normalized_promotion_trace(output):
    return {
        (
            item["discriminator_id"],
            item["promotion_ref"],
            item["root_key"],
            tuple(sorted(item["pair"])),
        )
        for item in output["promotion_trace"]
    }


def semantic_signature(output):
    return {
        "decision": canonical_decision(output),
        "pairwise": normalized_pairwise(output),
        "promotion_trace": normalized_promotion_trace(output),
        "rules": copy.deepcopy(output["rules"]),
    }


class TestOntologicalDiscriminatorMetamorphic(unittest.TestCase):

    def test_mr01_observation_permutations_preserve_full_output(self):
        observations = base_observations()
        coverage = {
            "MONADIC_ORIGIN_vs_SPLIT_SOUL": "COMPLETE",
        }
        baseline = discriminate_ontology(
            observations,
            mode="EXPLORATORY",
            pair_coverage=coverage,
        )

        for transformed in itertools.permutations(observations):
            self.assertEqual(
                discriminate_ontology(
                    transformed,
                    mode="EXPLORATORY",
                    pair_coverage=coverage,
                ),
                baseline,
            )

    def test_mr02_pair_orientation_preserves_full_output(self):
        observations = base_observations()
        reversed_pairs = []
        for item in observations:
            transformed = copy.deepcopy(item)
            transformed["pair"] = list(reversed(transformed["pair"]))
            reversed_pairs.append(transformed)

        baseline = discriminate_ontology(
            observations,
            mode="EXPLORATORY",
            pair_coverage={
                "MONADIC_ORIGIN_vs_SPLIT_SOUL": "COMPLETE",
            },
        )
        transformed = discriminate_ontology(
            reversed_pairs,
            mode="EXPLORATORY",
            pair_coverage={
                "SPLIT_SOUL_vs_MONADIC_ORIGIN": "COMPLETE",
            },
        )

        self.assertEqual(transformed, baseline)

    def test_mr03_duplicate_identical_observation_is_idempotent(self):
        observations = base_observations()
        baseline = discriminate_ontology(
            observations,
            mode="EXPLORATORY",
        )
        duplicated = discriminate_ontology(
            observations + [copy.deepcopy(observations[0])],
            mode="EXPLORATORY",
        )

        self.assertEqual(duplicated, baseline)

    def test_mr04_note_mutation_is_semantically_inert(self):
        observations = base_observations()
        mutated = copy.deepcopy(observations)
        for index, item in enumerate(mutated):
            item["note"] = f"narrativa-no-decisoria-{index}"

        self.assertEqual(
            discriminate_ontology(mutated, mode="EXPLORATORY"),
            discriminate_ontology(observations, mode="EXPLORATORY"),
        )

    def test_mr05_mode_case_normalization_is_idempotent(self):
        observations = base_observations()

        self.assertEqual(
            discriminate_ontology(observations, mode="confirmatory"),
            discriminate_ontology(observations, mode="CONFIRMATORY"),
        )

    def test_mr06_l1_noise_preserves_full_output(self):
        observations = base_observations()
        noise = [
            obs(
                f"L1-NOISE-{index}",
                ("MONADIC_ORIGIN", "TWIN_FLAME_MODEL"),
                "L1_DOCTRINAL",
                "NO_SEPARATION",
                root_key=f"L1-NOISE-ROOT-{index}",
            )
            for index in range(30)
        ]

        self.assertEqual(
            discriminate_ontology(
                observations + noise,
                mode="EXPLORATORY",
            ),
            discriminate_ontology(
                observations,
                mode="EXPLORATORY",
            ),
        )

    def test_mr07_l2_addition_preserves_confirmatory_decision(self):
        observations = base_observations()
        baseline = discriminate_ontology(
            observations,
            mode="EXPLORATORY",
        )
        transformed = discriminate_ontology(
            observations
            + [
                obs(
                    "L2-EXTRA",
                    ("MONADIC_ORIGIN", "TWIN_FLAME_MODEL"),
                    "L2_EXPERIMENTAL",
                    "SEPARATES",
                    excluded_model="MONADIC_ORIGIN",
                    root_key="L2-EXTRA-ROOT",
                )
            ],
            mode="EXPLORATORY",
        )

        self.assertEqual(
            canonical_decision(transformed),
            canonical_decision(baseline),
        )
        self.assertNotEqual(
            transformed["exploratory_view"],
            baseline["exploratory_view"],
        )

    def test_mr08_not_evaluable_noise_preserves_full_output(self):
        observations = base_observations()
        noise = [
            obs(
                f"NE-{index}",
                ("MONADIC_ORIGIN", "TWIN_FLAME_MODEL"),
                "L3_VALIDATED",
                "NOT_EVALUABLE",
                root_key=f"NE-ROOT-{index}",
            )
            for index in range(20)
        ]

        self.assertEqual(
            discriminate_ontology(
                observations + noise,
                mode="EXPLORATORY",
            ),
            discriminate_ontology(
                observations,
                mode="EXPLORATORY",
            ),
        )

    def test_mr09_model_order_preserves_semantic_signature(self):
        observations = base_observations()
        coverage = {
            "MONADIC_ORIGIN_vs_SPLIT_SOUL": "COMPLETE",
        }
        baseline = discriminate_ontology(
            observations,
            models=MODELS,
            mode="EXPLORATORY",
            pair_coverage=coverage,
        )
        baseline_signature = semantic_signature(baseline)

        for transformed_models in itertools.permutations(MODELS):
            transformed = discriminate_ontology(
                observations,
                models=transformed_models,
                mode="EXPLORATORY",
                pair_coverage=coverage,
            )
            self.assertEqual(
                semantic_signature(transformed),
                baseline_signature,
            )

    def test_mr10_reverse_coverage_key_preserves_full_output(self):
        observations = [
            obs(
                "L3-MP-NO-SEP",
                ("MONADIC_ORIGIN", "SPLIT_SOUL"),
                "L3_VALIDATED",
                "NO_SEPARATION",
                root_key="ROOT-MP",
            )
        ]

        forward = discriminate_ontology(
            observations,
            pair_coverage={
                "MONADIC_ORIGIN_vs_SPLIT_SOUL": "COMPLETE",
            },
        )
        reverse = discriminate_ontology(
            observations,
            pair_coverage={
                "SPLIT_SOUL_vs_MONADIC_ORIGIN": "COMPLETE",
            },
        )

        self.assertEqual(reverse, forward)
        self.assertEqual(
            forward["pairwise_matrix"][
                "MONADIC_ORIGIN_vs_SPLIT_SOUL"
            ]["confirmatory_status"],
            "OBSERVATIONALLY_EQUIVALENT",
        )

    def test_mr11_conflicting_bidirectional_coverage_is_rejected(self):
        with self.assertRaises(ValueError):
            discriminate_ontology(
                [],
                pair_coverage={
                    "MONADIC_ORIGIN_vs_SPLIT_SOUL": "COMPLETE",
                    "SPLIT_SOUL_vs_MONADIC_ORIGIN": "NONE",
                },
            )

    def test_mr12_mapping_and_dataclass_inputs_are_equivalent(self):
        mapped = obs(
            "L2-ST",
            ("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
            "L2_EXPERIMENTAL",
            "SEPARATES",
            excluded_model="SOULMATE_MODEL",
            root_key="ROOT-ST",
            note="texto",
        )
        dataclass_value = PairObservation(
            discriminator_id="L2-ST",
            pair=("SOULMATE_MODEL", "TWIN_FLAME_MODEL"),
            validation_level="L2_EXPERIMENTAL",
            result="SEPARATES",
            excluded_model="SOULMATE_MODEL",
            root_key="ROOT-ST",
            note="texto",
        )

        self.assertEqual(
            discriminate_ontology([mapped], mode="EXPLORATORY"),
            discriminate_ontology([dataclass_value], mode="EXPLORATORY"),
        )

    def test_mr13_discriminator_alias_same_root_preserves_full_output(self):
        baseline = discriminate_ontology(
            [
                obs(
                    "L3-A",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="ROOT-ONE",
                )
            ]
        )
        transformed = discriminate_ontology(
            [
                obs(
                    "L3-RENAMED",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="ROOT-ONE",
                )
            ]
        )

        self.assertEqual(transformed, baseline)

    def test_mr14_concordant_root_split_preserves_decision(self):
        baseline = discriminate_ontology(
            [
                obs(
                    "L3-A",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="ROOT-A",
                )
            ]
        )
        transformed = discriminate_ontology(
            [
                obs(
                    "L3-A",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="ROOT-A",
                ),
                obs(
                    "L3-B",
                    ("SOULMATE_MODEL", "MONADIC_ORIGIN"),
                    "L3_VALIDATED",
                    "SEPARATES",
                    excluded_model="SOULMATE_MODEL",
                    root_key="ROOT-B",
                ),
            ]
        )

        self.assertEqual(
            canonical_decision(transformed),
            canonical_decision(baseline),
        )
        self.assertNotEqual(
            normalized_pairwise(transformed),
            normalized_pairwise(baseline),
        )

    def test_mr15_repeated_execution_is_deterministic(self):
        observations = base_observations()
        first = discriminate_ontology(
            observations,
            mode="EXPLORATORY",
            pair_coverage={
                "MONADIC_ORIGIN_vs_SPLIT_SOUL": "COMPLETE",
            },
        )

        for _ in range(20):
            self.assertEqual(
                discriminate_ontology(
                    observations,
                    mode="EXPLORATORY",
                    pair_coverage={
                        "MONADIC_ORIGIN_vs_SPLIT_SOUL": "COMPLETE",
                    },
                ),
                first,
            )


if __name__ == "__main__":
    unittest.main()
