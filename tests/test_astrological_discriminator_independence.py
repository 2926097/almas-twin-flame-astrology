import copy
import unittest

from almas_tfa.discriminator_promotion_registry import (
    authorize_l3_observation,
    authorize_promoted_discriminator_component,
    load_discriminator_promotion_registry,
)


def base_record(*, uses_astrology):
    return {
        "discriminator_id": "ASTRO_TEST" if uses_astrology else "NON_ASTRO_TEST",
        "current_status": "VALIDATED_DISCRIMINATOR",
        "l3_authorized": True,
        "promotion_ref": "PROMO:ASTRO:1" if uses_astrology else "PROMO:NONASTRO:1",
        "promoted_at": "2026-09-26T00:00:00Z",
        "validated_pairs": [["SOULMATE_MODEL", "TWIN_FLAME_MODEL"]],
        "root_key_prefix": "ASTRO:" if uses_astrology else "NONASTRO:",
        "frozen": {
            "almas_version": "TEST",
            "commit_sha": "test-sha",
            "rule_ref": "RULE-ASTRO" if uses_astrology else "RULE-NONASTRO",
            "schema_refs": ["SCHEMA-1"],
        },
        "validation_evidence": {
            "preregistration_refs": ["PREREG-1"],
            "independent_replication_refs": ["REPL-1"],
            "external_holdout_refs": ["HOLDOUT-1"],
            "negative_control_refs": ["NEG-1"],
            "leakage_audit_refs": ["LEAK-1"],
        },
        "uses_astrology": uses_astrology,
        "astrology_validation": (
            {
                "non_astrological_criterion_refs": ["CRITERION-1"],
                "astrology_ablation_refs": ["ABLATION-1"],
                "matched_control_refs": ["CONTROL-1"],
                "dependency_audit_refs": ["DEPENDENCY-1"],
                "out_of_sample_refs": ["OOS-1"],
                "astrology_specific_replication_refs": ["ASTRO-REPL-1"],
                "single_feature_prohibition_acknowledged": True,
                "null_rarity_not_ontological": True,
                "temporal_activation_not_origin_proof": True,
            }
            if uses_astrology
            else None
        ),
        "block_reason": None,
    }


def registry(record):
    return {"records": [record]}


def observation(record):
    return {
        "discriminator_id": record["discriminator_id"],
        "promotion_ref": record["promotion_ref"],
        "pair": ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
        "validation_level": "L3_VALIDATED",
        "result": "SEPARATES",
        "excluded_model": "SOULMATE_MODEL",
        "root_key": record["root_key_prefix"] + "ROOT_1",
    }


class TestAstrologicalDiscriminatorIndependence(unittest.TestCase):

    def test_packaged_astrological_candidates_are_not_l3_authorized(self):
        packaged = load_discriminator_promotion_registry()
        records = {
            record["discriminator_id"]: record
            for record in packaged["records"]
        }

        for discriminator_id in (
            "OD01_PAIR_SPECIFICITY_NETWORK",
            "OD02_DYADIC_STRUCTURAL_ISOMORPHISM",
            "OD04_PROSPECTIVE_MODEL_PREDICTION",
        ):
            self.assertTrue(records[discriminator_id]["uses_astrology"])
            self.assertIsNone(records[discriminator_id]["astrology_validation"])
            self.assertFalse(records[discriminator_id]["l3_authorized"])

    def test_complete_astrology_validation_can_authorize_registered_l3(self):
        record = base_record(uses_astrology=True)
        result = authorize_l3_observation(
            observation(record),
            registry=registry(record),
        )

        self.assertTrue(result["uses_astrology"])
        self.assertIsNotNone(result["astrology_validation"])

    def test_astrology_l3_without_astrology_validation_is_rejected(self):
        record = base_record(uses_astrology=True)
        record["astrology_validation"] = None

        with self.assertRaises(ValueError):
            authorize_l3_observation(
                observation(record),
                registry=registry(record),
            )

    def test_each_astrology_validation_reference_family_is_mandatory(self):
        keys = (
            "non_astrological_criterion_refs",
            "astrology_ablation_refs",
            "matched_control_refs",
            "dependency_audit_refs",
            "out_of_sample_refs",
            "astrology_specific_replication_refs",
        )

        for key in keys:
            with self.subTest(key=key):
                record = base_record(uses_astrology=True)
                record["astrology_validation"][key] = []
                with self.assertRaises(ValueError):
                    authorize_l3_observation(
                        observation(record),
                        registry=registry(record),
                    )

    def test_single_feature_firewall_acknowledgements_are_mandatory(self):
        keys = (
            "single_feature_prohibition_acknowledged",
            "null_rarity_not_ontological",
            "temporal_activation_not_origin_proof",
        )

        for key in keys:
            with self.subTest(key=key):
                record = base_record(uses_astrology=True)
                record["astrology_validation"][key] = False
                with self.assertRaises(ValueError):
                    authorize_l3_observation(
                        observation(record),
                        registry=registry(record),
                    )

    def test_non_astrological_l3_does_not_require_astrology_validation(self):
        record = base_record(uses_astrology=False)
        result = authorize_l3_observation(
            observation(record),
            registry=registry(record),
        )

        self.assertFalse(result["uses_astrology"])
        self.assertIsNone(result["astrology_validation"])

    def test_m25_component_authorization_uses_same_astrology_firewall(self):
        record = base_record(uses_astrology=True)
        authorized = authorize_promoted_discriminator_component(
            discriminator_id=record["discriminator_id"],
            promotion_ref=record["promotion_ref"],
            pair=["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
            root_key="ASTRO:ROOT_1",
            registry=registry(record),
        )
        self.assertTrue(authorized["uses_astrology"])

        broken = copy.deepcopy(record)
        broken["astrology_validation"]["non_astrological_criterion_refs"] = []

        with self.assertRaises(ValueError):
            authorize_promoted_discriminator_component(
                discriminator_id=broken["discriminator_id"],
                promotion_ref=broken["promotion_ref"],
                pair=["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
                root_key="ASTRO:ROOT_1",
                registry=registry(broken),
            )

    def test_isolated_astrology_cannot_self_promote_current_od02(self):
        packaged = load_discriminator_promotion_registry()
        observation_value = {
            "discriminator_id": "OD02_DYADIC_STRUCTURAL_ISOMORPHISM",
            "promotion_ref": "FAKE-ASTRO-PROMOTION",
            "pair": ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
            "validation_level": "L3_VALIDATED",
            "result": "SEPARATES",
            "excluded_model": "SOULMATE_MODEL",
            "root_key": "OD02:ISOLATED_ASPECT",
        }

        with self.assertRaises(ValueError):
            authorize_l3_observation(
                observation_value,
                registry=packaged,
            )


if __name__ == "__main__":
    unittest.main()
