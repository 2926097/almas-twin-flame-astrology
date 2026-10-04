import json
from pathlib import Path
import unittest

from almas_tfa.corpus_doctrine import assess_corpus_claim

ROOT = Path(__file__).resolve().parents[1]


class TwinFlameFlameGenealogyTests(unittest.TestCase):
    def _json(self, path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_ballard_direct_doctrine_supported_but_case_ontology_not_promoted(self):
        source = "ballard_magic_presence_1935_twin_rays"
        doctrinal = assess_corpus_claim(
            "DIVINE_FLAME_TWIN_RAY_PROJECTION", [source]
        )
        self.assertEqual(doctrinal["status"], "SUPPORTED")
        self.assertEqual(doctrinal["epistemic_class"], "C_DOCTRINE")
        self.assertFalse(doctrinal["pu_created"])
        self.assertFalse(doctrinal["iem_modified"])

        case = assess_corpus_claim(
            "DIVINE_FLAME_TWIN_RAY_PROJECTION",
            [source],
            scope="CASE_ONTOLOGY",
        )
        self.assertEqual(case["status"], "INSUFFICIENT")
        self.assertEqual(case["ontology_effect"], "NONE")

    def test_summit_white_fire_architecture_is_direct_doctrine_only(self):
        source = "summit_lighthouse_what_is_twin_flame"
        doctrinal = assess_corpus_claim(
            "WHITE_FIRE_BODY_DUAL_SPHERE_MODEL", [source]
        )
        self.assertEqual(doctrinal["status"], "SUPPORTED")
        case = assess_corpus_claim(
            "WHITE_FIRE_BODY_DUAL_SPHERE_MODEL",
            [source],
            scope="CASE_ONTOLOGY",
        )
        self.assertEqual(case["status"], "INSUFFICIENT")

    def test_corelli_does_not_support_literal_split_soul(self):
        claim = assess_corpus_claim(
            "SPLIT_SOUL", ["corelli_romance_two_worlds_1886"]
        )
        self.assertEqual(claim["status"], "INSUFFICIENT")

        registry = self._json("manifests/origin-model-registry.json")
        split = next(x for x in registry["models"] if x["id"] == "SPLIT_SOUL")
        self.assertNotIn(
            "corelli_romance_two_worlds_1886", split["source_ids"]
        )

    def test_three_flame_architectures_preserve_distinct_operators(self):
        registry = self._json("manifests/origin-model-registry.json")
        by_id = {x["id"]: x for x in registry["origin_architectures"]}
        self.assertEqual(
            by_id["DUAL_SOUL_HALF_FLAME_SIMILE"]["operator"],
            "DUALITY_AS_HALF_FLAME_SIMILE",
        )
        self.assertEqual(
            by_id["DIVINE_FLAME_TWIN_RAY_PROJECTION"]["operator"],
            "PROJECTS_TWO_RAYS",
        )
        self.assertEqual(
            by_id["WHITE_FIRE_BODY_DUAL_SPHERE"]["operator"],
            "DIVISION_OR_DIFFERENTIATION_INTO_TWO_SPHERES",
        )
        self.assertEqual(
            len({x["operator"] for x in registry["origin_architectures"]}), 3
        )

    def test_ballard_is_neighbor_not_summit_source_substitution(self):
        registry = self._json("manifests/origin-model-registry.json")
        twin = next(
            x for x in registry["models"] if x["id"] == "TWIN_FLAME_MODEL"
        )
        self.assertNotIn(
            "ballard_magic_presence_1935_twin_rays", twin["source_ids"]
        )

        genealogy = self._json("reference/doctrinal-genealogy.json")
        signatures = {
            (x["from"], x["to"], x["relation"], x["status"])
            for x in genealogy["edges"]
        }
        self.assertIn(
            (
                "DIVINE_FLAME_TWIN_RAY_PROJECTION",
                "TWIN_FLAME_ORIGIN",
                "DOCTRINAL_NEIGHBOR_NOT_IDENTITY",
                "COMPATIBLE",
            ),
            signatures,
        )

    def test_no_astrological_discriminator_is_created(self):
        origin = self._json("manifests/origin-model-registry.json")
        new_ids = {
            "D_ORIGIN_SUBSTRATE",
            "D_ORIGIN_OPERATOR",
            "D_METAPHOR_VS_LITERAL",
            "D_PROJECTION_VS_DIVISION",
        }
        by_id = {x["id"]: x for x in origin["discriminators"]}
        self.assertTrue(new_ids.issubset(by_id))
        self.assertTrue(all(by_id[x]["kind"] == "DOCTRINAL" for x in new_ids))
        self.assertTrue(
            all(
                x["case_level_discriminator_status"] == "NOT_VALIDATED"
                for x in origin["origin_architectures"]
            )
        )


if __name__ == "__main__":
    unittest.main()
