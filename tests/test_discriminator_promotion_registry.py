import unittest

from almas_tfa.discriminator_promotion_registry import (
    authorize_l3_observation,
    load_discriminator_promotion_registry,
    validate_l3_observations,
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


class TestDiscriminatorPromotionRegistry(unittest.TestCase):

    def test_packaged_registry_has_no_current_l3_promotions(self):
        registry = load_discriminator_promotion_registry()

        self.assertEqual(
            registry["authority"],
            "ALMAS_CANONICAL_DISCRIMINATOR_PROMOTION_REGISTRY",
        )
        self.assertEqual(registry["validated_discriminator_ids"], [])
        self.assertEqual(
            registry["status"],
            "ACTIVE_NO_L3_PROMOTIONS",
        )
        self.assertTrue(
            all(not record["l3_authorized"] for record in registry["records"])
        )

    def test_current_od01_cannot_be_self_declared_as_l3(self):
        observation = {
            "discriminator_id": "OD01_PAIR_SPECIFICITY_NETWORK",
            "promotion_ref": "FAKE",
            "pair": ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
            "validation_level": "L3_VALIDATED",
            "result": "SEPARATES",
            "excluded_model": "SOULMATE_MODEL",
            "root_key": "OD01:FAKE",
        }
        with self.assertRaises(ValueError):
            authorize_l3_observation(observation)

    def test_complete_synthetic_promotion_authorizes_only_registered_scope(self):
        registry = synthetic_l3_registry()
        observation = {
            "discriminator_id": "TEST_L3",
            "promotion_ref": "PROMO:TEST_L3:1",
            "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
            "validation_level": "L3_VALIDATED",
            "result": "SEPARATES",
            "excluded_model": "SOULMATE_MODEL",
            "root_key": "TEST_L3:ROOT_1",
        }

        record = authorize_l3_observation(observation, registry=registry)
        self.assertEqual(record["current_status"], "VALIDATED_DISCRIMINATOR")

        wrong_pair = dict(observation)
        wrong_pair["pair"] = ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"]
        with self.assertRaises(ValueError):
            authorize_l3_observation(wrong_pair, registry=registry)

        wrong_root = dict(observation)
        wrong_root["root_key"] = "OTHER:ROOT"
        with self.assertRaises(ValueError):
            authorize_l3_observation(wrong_root, registry=registry)

    def test_incomplete_promotion_record_cannot_authorize_l3(self):
        registry = synthetic_l3_registry()
        registry["records"][0]["validation_evidence"]["external_holdout_refs"] = []

        observation = {
            "discriminator_id": "TEST_L3",
            "promotion_ref": "PROMO:TEST_L3:1",
            "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
            "validation_level": "L3_VALIDATED",
            "root_key": "TEST_L3:ROOT_1",
        }

        with self.assertRaises(ValueError):
            authorize_l3_observation(observation, registry=registry)

    def test_l2_does_not_require_promotion_registry(self):
        validate_l3_observations(
            [
                {
                    "discriminator_id": "OD01_PAIR_SPECIFICITY_NETWORK",
                    "pair": ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
                    "validation_level": "L2_EXPERIMENTAL",
                    "result": "SEPARATES",
                    "excluded_model": "SOULMATE_MODEL",
                    "root_key": "OD01:L2",
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
