import unittest

from almas_tfa.discriminator_source_genealogy import (
    build_discriminator_source_genealogy_reporting,
    get_discriminator_source_genealogy,
    load_discriminator_source_genealogy,
)


class TestDiscriminatorSourceGenealogy(unittest.TestCase):

    def test_packaged_registry_covers_all_od_candidates(self):
        registry = load_discriminator_source_genealogy()
        ids = {
            record["discriminator_id"]
            for record in registry["records"]
        }
        self.assertEqual(
            ids,
            {
                "OD01_PAIR_SPECIFICITY_NETWORK",
                "OD02_DYADIC_STRUCTURAL_ISOMORPHISM",
                "OD03_BLINDED_DOCTRINAL_CODING",
                "OD04_PROSPECTIVE_MODEL_PREDICTION",
                "OD05_PRIOR_UNITY_DIRECT",
                "OD06_MONADIC_HIERARCHY_DIRECT",
                "OD07_PHENOMENOLOGY_CLUSTER",
            },
        )

    def test_runtime_reporting_never_adds_ontological_weight(self):
        report = build_discriminator_source_genealogy_reporting()

        self.assertTrue(report["methodological_provenance_only"])
        self.assertFalse(report["ontological_inference_allowed"])
        self.assertFalse(report["source_count_adds_weight"])
        self.assertFalse(
            report["source_priority_adds_ontological_weight"]
        )
        self.assertFalse(report["cross_tradition_identity_allowed"])

        for record in report["records"]:
            self.assertFalse(record["source_count_adds_weight"])
            self.assertFalse(
                record["source_priority_adds_ontological_weight"]
            )
            self.assertFalse(record["cross_tradition_identity_allowed"])
            self.assertFalse(record["direct_case_evidence"])
            self.assertFalse(record["can_change_case_classification"])
            self.assertFalse(record["can_raise_irc"])

    def test_sources_preserve_documentary_metadata(self):
        report = build_discriminator_source_genealogy_reporting()
        od06 = next(
            item for item in report["records"]
            if item["discriminator_id"] == "OD06_MONADIC_HIERARCHY_DIRECT"
        )
        by_id = {item["source_id"]: item for item in od06["sources"]}

        self.assertEqual(
            by_id["blavatsky_secret_doctrine_monads"]["priority"],
            "P1_PRIMARY",
        )
        self.assertEqual(
            by_id["bailey_esoteric_psychology_soul"]["source_role"],
            "DOCTRINAL_PRIMARY",
        )
        self.assertEqual(
            by_id["bailey_esoteric_psychology_soul"][
                "verification_anchor_type"
            ],
            "CHAPTER",
        )
        self.assertEqual(
            by_id["bailey_esoteric_psychology_soul"]["evidence_scope"],
            "DOCTRINAL_CLAIM",
        )

    def test_od03_ceiling_is_construct_separability_only(self):
        record = get_discriminator_source_genealogy(
            "OD03_BLINDED_DOCTRINAL_CODING"
        )
        self.assertEqual(
            record["epistemic_ceiling"],
            "CONSTRUCT_SEPARABILITY_ONLY",
        )
        self.assertEqual(
            record["provenance_class"],
            "DOCTRINAL_SEPARABILITY_METHOD",
        )

    def test_od05_and_od06_remain_nonobservable_doctrinal_constructs(self):
        for discriminator_id in (
            "OD05_PRIOR_UNITY_DIRECT",
            "OD06_MONADIC_HIERARCHY_DIRECT",
        ):
            with self.subTest(discriminator_id=discriminator_id):
                record = get_discriminator_source_genealogy(
                    discriminator_id
                )
                self.assertEqual(
                    record["provenance_class"],
                    "NONOBSERVABLE_DOCTRINAL_CONSTRUCT",
                )
                self.assertEqual(
                    record["epistemic_ceiling"],
                    "DOCTRINAL_CONCEPT_ONLY",
                )
                self.assertFalse(record["direct_case_evidence"])

    def test_od07_is_phenomenology_only(self):
        record = get_discriminator_source_genealogy(
            "OD07_PHENOMENOLOGY_CLUSTER"
        )
        self.assertEqual(
            record["provenance_class"],
            "CONTEMPORARY_PHENOMENOLOGY",
        )
        self.assertEqual(record["epistemic_ceiling"], "PHENOMENOLOGY_ONLY")
        self.assertIn(
            ["SOULMATE_EXPERIENCE", "TWIN_FLAME_ORIGIN"],
            record["forbidden_equivalences"],
        )

    def test_required_non_equivalence_edges_are_exposed(self):
        report = build_discriminator_source_genealogy_reporting()
        od03 = next(
            item for item in report["records"]
            if item["discriminator_id"] == "OD03_BLINDED_DOCTRINAL_CODING"
        )
        relations = {
            (
                edge["from"],
                edge["to"],
                edge["relation"],
            )
            for edge in od03["required_genealogy_edges"]
        }
        self.assertIn(
            (
                "SPLIT_PRIMORDIAL_BEING",
                "TWIN_FLAME_ORIGIN",
                "COMPARATIVE_ANTECEDENT_ONLY",
            ),
            relations,
        )
        self.assertIn(
            (
                "MONAD_SOUL_PERSONALITY",
                "TWIN_FLAME_ORIGIN",
                "NON_EQUIVALENT",
            ),
            relations,
        )


if __name__ == "__main__":
    unittest.main()
