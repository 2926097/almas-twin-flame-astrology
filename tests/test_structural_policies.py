from __future__ import annotations

import unittest

from almas_tfa.evidence_handlers import m15_evidence_extraction
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.root_strengths import load_root_strength_policy
from almas_tfa.structural_policies import (
    load_declared_orb_contract_policy,
    load_structural_loading_policy,
    load_technique_dependency_registry,
    validate_declared_aspect_policy,
)


EXPECTED_BINDINGS = {
    "synastry": ("M03", "SYN", "SYN", False, True, False),
    "declinations": (
        "M05", "DECLINATION", "DECLINATION", False, True, False
    ),
    "antiscia": ("M06", "ANTISCIA", "ANTISCIA", False, True, False),
    "relationship_chart_consonance": (
        "M09", "RELCHART", "RELCHART", False, True, False
    ),
    "natal_draconic_cross": (
        "M11", "NATAL_DRACONIC", "NATAL_DRACONIC", False, True, True
    ),
    "draconic_draconic": (
        "M12", "DRACONIC_DD", "DRACONIC_DD", True, False, False
    ),
    "secondary_symbolic": (
        "M14", "SECONDARY", "SECONDARY", True, False, False
    ),
}


class StructuralPolicyManifestTests(unittest.TestCase):
    def test_technique_registry_preserves_116_taxonomy(self):
        registry = load_technique_dependency_registry()
        self.assertEqual(
            registry["registry_id"],
            "ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1",
        )
        bindings = registry["source_bindings"]
        self.assertEqual(set(bindings), set(EXPECTED_BINDINGS))
        for source, expected in EXPECTED_BINDINGS.items():
            spec = bindings[source]
            actual = (
                spec["module_id"],
                spec["technique_family"],
                spec["dependency_family"],
                spec["support_only"],
                spec["core_eligible"],
                spec["directional"],
            )
            self.assertEqual(actual, expected)

    def test_support_only_bindings_never_core_eligible(self):
        registry = load_technique_dependency_registry()
        for spec in registry["source_bindings"].values():
            if spec["support_only"]:
                self.assertFalse(spec["core_eligible"])

    def test_root_strength_policy_covers_registry_families(self):
        registry = load_technique_dependency_registry()
        strength = load_root_strength_policy()
        declared = set(strength["technique_reliability"])
        families = {
            spec["technique_family"]
            for spec in registry["source_bindings"].values()
        }
        self.assertTrue(families.issubset(declared))
        self.assertTrue(
            all(strength["technique_reliability"][family] == 1.0
                for family in families)
        )

    def test_structural_loading_links_existing_frozen_policies(self):
        policy = load_structural_loading_policy()
        self.assertEqual(
            policy["root_strength_policy_id"],
            "ALMAS_ROOT_STRENGTH_BASELINE_V1",
        )
        self.assertEqual(
            policy["root_pillar_policy_id"],
            "ALMAS_ROOT_PILLAR_ATTRIBUTION_V2",
        )
        self.assertFalse(
            policy["loading_constraints"]["support_only_can_create_core"]
        )
        self.assertTrue(
            policy["principles"][
                "birth_time_uncertainty_handled_by_m23_m25"
            ]
        )

    def test_declared_orb_contract_forbids_implicit_orbs(self):
        policy = load_declared_orb_contract_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_DECLARED_ORB_CONTRACT_V1",
        )
        self.assertTrue(policy["principles"]["implicit_orbs_forbidden"])
        self.assertTrue(
            policy["principles"]["overlap_resolution_deterministic"]
        )

    def test_valid_declared_aspect_policy_passes(self):
        validate_declared_aspect_policy(
            {
                "CONJUNCTION": {"angle": 0, "orb": 6},
                "OPPOSITION": {"angle": 180.0, "orb": 4.5},
            }
        )

    def test_declared_aspect_policy_rejects_incomplete_or_extra_fields(self):
        with self.assertRaises(ValueError):
            validate_declared_aspect_policy(
                {"CONJUNCTION": {"angle": 0}}
            )
        with self.assertRaises(ValueError):
            validate_declared_aspect_policy(
                {
                    "CONJUNCTION": {
                        "angle": 0,
                        "orb": 6,
                        "weight": 2,
                    }
                }
            )

    def test_declared_aspect_policy_rejects_non_numeric_and_out_of_range(self):
        invalid = [
            {"CONJUNCTION": {"angle": "0", "orb": 6}},
            {"CONJUNCTION": {"angle": True, "orb": 6}},
            {"CONJUNCTION": {"angle": 181, "orb": 6}},
            {"CONJUNCTION": {"angle": 0, "orb": -1}},
        ]
        for policy in invalid:
            with self.subTest(policy=policy):
                with self.assertRaises(ValueError):
                    validate_declared_aspect_policy(policy)

    def test_m15_exposes_registry_provenance_without_score_change(self):
        context = ModuleContext(
            module_id="M15",
            module_name="evidence",
            mode="FULL",
            raw_input={},
            canonical_snapshot={
                "synastry": {
                    "contacts": [
                        {
                            "subject_a": "A",
                            "point_a": "SUN",
                            "subject_b": "B",
                            "point_b": "MOON",
                            "aspect": "CONJUNCTION",
                            "angle": 0,
                            "exactness": 0.75,
                        }
                    ]
                },
                "draconic_draconic": {
                    "contacts": [
                        {
                            "subject_a": "A",
                            "point_a": "VENUS",
                            "subject_b": "B",
                            "point_b": "MARS",
                            "aspect": "TRINE",
                            "angle": 120,
                            "exactness": 0.6,
                        }
                    ]
                },
            },
            prior_results={},
        )
        result = m15_evidence_extraction(context)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.payload
        self.assertEqual(
            output["technique_dependency_registry_id"],
            "ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1",
        )
        items = {item["canonical_source"]: item for item in output["items"]}
        self.assertEqual(items["synastry"]["technique_family"], "SYN")
        self.assertEqual(items["synastry"]["exactness"], 0.75)
        self.assertTrue(items["synastry"]["core_eligible"])
        self.assertEqual(
            items["draconic_draconic"]["technique_family"],
            "DRACONIC_DD",
        )
        self.assertTrue(items["draconic_draconic"]["support_only"])
        self.assertFalse(items["draconic_draconic"]["core_eligible"])


if __name__ == "__main__":
    unittest.main()
