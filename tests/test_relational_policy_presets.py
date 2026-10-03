import unittest

from almas_tfa.relational_policy_presets import (
    RelationalPolicyPresetError,
    load_relational_policy_preset_registry,
    resolve_relational_policy_preset,
)


class RelationalPolicyPresetTests(unittest.TestCase):
    def test_registry_loads_and_is_explicit_experimental_policy(self):
        registry = load_relational_policy_preset_registry()
        self.assertEqual(
            registry["registry_id"],
            "ALMAS_RELATIONAL_POLICY_PRESET_REGISTRY_V1",
        )
        self.assertEqual(
            registry["epistemic_class"],
            "E_PROJECT_POLICY",
        )
        self.assertTrue(
            registry["principles"]["explicit_selection_required"]
        )
        self.assertTrue(
            registry["principles"]["case_fitting_forbidden"]
        )

    def test_strict_research_profile_resolves(self):
        result = resolve_relational_policy_preset(
            "ALMAS_RELATIONAL_STRICT_RESEARCH_V1",
            analysis_profile="FULL_ASTROLOGY",
        )
        self.assertEqual(
            result["policies"]["declination_policy"]["parallel_orb"],
            1.0,
        )
        self.assertEqual(
            result["policies"]["antiscia_policy"]["antiscia_orb"],
            1.0,
        )
        self.assertEqual(
            set(result["policies"]["draconic_aspect_policy"]),
            {"CONJUNCTION", "OPPOSITION"},
        )
        self.assertFalse(result["implicit_orbs_used"])
        self.assertFalse(result["case_fitting_used"])
        self.assertEqual(len(result["policy_fingerprint"]), 64)
        int(result["policy_fingerprint"], 16)

    def test_unknown_preset_fails_closed(self):
        with self.assertRaisesRegex(
            RelationalPolicyPresetError,
            "desconocido",
        ):
            resolve_relational_policy_preset(
                "UNKNOWN",
                analysis_profile="FULL_ASTROLOGY",
            )

    def test_profile_scope_is_enforced(self):
        registry = load_relational_policy_preset_registry()
        registry["presets"][
            "ALMAS_RELATIONAL_STRICT_RESEARCH_V1"
        ]["analysis_profiles"] = ["FULL_ASTROLOGY"]
        with self.assertRaisesRegex(
            RelationalPolicyPresetError,
            "no admite",
        ):
            resolve_relational_policy_preset(
                "ALMAS_RELATIONAL_STRICT_RESEARCH_V1",
                analysis_profile="TEMPORAL",
                registry=registry,
            )


if __name__ == "__main__":
    unittest.main()
