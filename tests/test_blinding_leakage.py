import unittest

from almas_tfa.blinding_leakage import (
    assert_late_reveal_invariance,
    assert_no_forbidden_structural_fields,
    canonical_sha256,
    evaluate_blinding_audit,
    load_blinding_leakage_policy,
)


def valid_audit():
    return {
        "policy_id": "ALMAS_BLINDING_LEAKAGE_V1",
        "audit_refs": ["BLIND-AUDIT-1"],
        "structural_input_refs": ["STRUCT-IN-1"],
        "structural_input_sha256": "a" * 64,
        "pre_reveal_output_sha256": "b" * 64,
        "post_reveal_structural_output_sha256": "b" * 64,
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
    }


class TestBlindingLeakage(unittest.TestCase):

    def test_policy_is_explicit_project_policy(self):
        policy = load_blinding_leakage_policy()
        self.assertEqual(policy["policy_id"], "ALMAS_BLINDING_LEAKAGE_V1")
        self.assertEqual(policy["epistemic_class"], "E_PROJECT_POLICY")
        self.assertEqual(policy["hash_algorithm"], "sha256")

    def test_valid_audit_passes(self):
        result = evaluate_blinding_audit(valid_audit())
        self.assertTrue(result["late_reveal_invariant"])
        self.assertEqual(result["label_leakage_count"], 0)
        self.assertEqual(result["narrative_leakage_count"], 0)
        self.assertEqual(result["case_fitting_count"], 0)

    def test_label_leakage_blocks(self):
        audit = valid_audit()
        audit["label_leakage_count"] = 1
        with self.assertRaises(ValueError):
            evaluate_blinding_audit(audit)

    def test_narrative_leakage_blocks(self):
        audit = valid_audit()
        audit["narrative_leakage_count"] = 1
        with self.assertRaises(ValueError):
            evaluate_blinding_audit(audit)

    def test_case_fitting_blocks(self):
        audit = valid_audit()
        audit["case_fitting_count"] = 1
        with self.assertRaises(ValueError):
            evaluate_blinding_audit(audit)

    def test_post_holdout_rule_change_blocks(self):
        audit = valid_audit()
        audit["post_holdout_rule_change_count"] = 1
        with self.assertRaises(ValueError):
            evaluate_blinding_audit(audit)

    def test_fingerprint_mismatch_blocks(self):
        audit = valid_audit()
        audit["post_reveal_structural_output_sha256"] = "c" * 64
        with self.assertRaises(ValueError):
            evaluate_blinding_audit(audit)

    def test_public_identity_requires_risk_reference(self):
        audit = valid_audit()
        audit["identity_visibility"] = "UNAVOIDABLE_PUBLIC"
        with self.assertRaises(ValueError):
            evaluate_blinding_audit(audit)
        audit["identity_risk_refs"] = ["IDENTITY-RISK-1"]
        result = evaluate_blinding_audit(audit)
        self.assertEqual(result["identity_visibility"], "UNAVOIDABLE_PUBLIC")

    def test_structural_payload_rejects_forbidden_fields_recursively(self):
        payload = {
            "observations": [
                {
                    "discriminator_id": "OD01",
                    "relationship_narrative": "texto que no debe entrar",
                }
            ]
        }
        with self.assertRaises(ValueError):
            assert_no_forbidden_structural_fields(payload)

    def test_model_names_in_pair_are_not_label_leakage(self):
        payload = {
            "observations": [
                {
                    "discriminator_id": "OD01",
                    "pair": ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"],
                    "note": "anotación semánticamente inerte",
                }
            ]
        }
        assert_no_forbidden_structural_fields(payload)

    def test_late_reveal_invariance_uses_canonical_fingerprint(self):
        before = {"b": 2, "a": [1, 3]}
        after = {"a": [1, 3], "b": 2}
        fingerprint = assert_late_reveal_invariance(before, after)
        self.assertEqual(fingerprint, canonical_sha256(before))

    def test_late_reveal_structural_mutation_is_rejected(self):
        before = {"classification": "SHARED_ORIGIN_UNDIFFERENTIATED"}
        after = {"classification": "TWIN_FLAME_MODEL"}
        with self.assertRaises(ValueError):
            assert_late_reveal_invariance(before, after)

    def test_hidden_flags_are_mandatory(self):
        for key in (
            "labels_hidden",
            "narrative_hidden",
            "expected_result_hidden",
            "holdout_outcome_hidden",
            "development_evaluation_disjoint",
        ):
            with self.subTest(key=key):
                audit = valid_audit()
                audit[key] = False
                with self.assertRaises(ValueError):
                    evaluate_blinding_audit(audit)


if __name__ == "__main__":
    unittest.main()
