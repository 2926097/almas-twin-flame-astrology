from __future__ import annotations

import unittest

from almas_tfa.canonical_assembly import (
    assemble_canonical_analysis,
    derive_canonical_coverage,
    load_canonical_assembly_policy,
)
from almas_tfa.module_contract import ExecutionStatus, ModuleContext, ModuleResult
from almas_tfa.report_gate_handlers import make_m30_report_gate_auto


def completed(module_id: str) -> ModuleResult:
    return ModuleResult(
        module_id=module_id,
        status=ExecutionStatus.COMPLETED,
    )


def prior_all():
    return {
        f"M{i:02d}": completed(f"M{i:02d}")
        for i in range(30)
    }


def natal_context():
    houses = {str(i): {"longitude": float(i * 30)} for i in range(1, 13)}
    return {
        "subjects": {
            "A": {
                "timed": True,
                "point_signs": {"SUN": "ARIES", "MOON": "TAURUS"},
                "nodes": {"NORTH_NODE": {"sign": "GEMINI"}},
                "angles": {"ASC": {"longitude": 10.0}, "MC": {"longitude": 100.0}},
                "house_cusps": houses,
                "house_placements": {"SUN": 1, "MOON": 2},
                "rulerships": {"ASC": "MARS"},
            },
            "B": {
                "timed": True,
                "point_signs": {"SUN": "LIBRA", "MOON": "SCORPIO"},
                "nodes": {"NORTH_NODE": {"sign": "SAGITTARIUS"}},
                "angles": {"ASC": {"longitude": 20.0}, "MC": {"longitude": 110.0}},
                "house_cusps": houses,
                "house_placements": {"SUN": 7, "MOON": 8},
                "rulerships": {"ASC": "VENUS"},
            },
        },
        "cross_house_placements": {
            "A_IN_B": {
                "source_subject": "A",
                "target_subject": "B",
                "placements": {
                    "SUN": {"house": 7, "longitude": 10.0},
                },
            },
            "B_IN_A": {
                "source_subject": "B",
                "target_subject": "A",
                "placements": {
                    "MOON": {"house": 1, "longitude": 12.0},
                },
            },
        },
    }


def canonical_base(*, with_ice=True):
    roots = {
        "roots": [
            {
                "root_id": "R0001",
                "root_key": "A:SUN|B:MOON|TRINE",
                "strength": 0.9,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "dependency_families": ["SYN"],
                "independent_family_count": 1,
                "point_ids": ["MOON", "SUN"],
                "relation_ids": ["TRINE"],
                "max_exactness": 0.98,
            }
        ],
        "root_count": 1,
        "strength_policy_applied": True,
        "strength_policy_id": "ALMAS_ROOT_STRENGTH_BASELINE_V1",
    }
    counter = {
        "models": {
            model: {
                "items": [],
                "contradiction_count": 0,
                "essential_contradiction": False,
            }
            for model in ("AF", "KA", "AG", "LG")
        },
        "suppressed": [],
        "ice_state": "PRECOMPUTED" if with_ice else "NOT_CALCULATED",
        "ice_by_model": (
            {model: 0.0 for model in ("AF", "KA", "AG", "LG")}
            if with_ice
            else None
        ),
        "missing_data_penalized": False,
    }
    return {
        "natal_context": natal_context(),
        "relationship_chart_consonance": {
            "field_context": {
                "authoring_only": True,
                "structural_evidence_used": False,
                "creates_independent_roots": False,
                "aspect_policy_source": (
                    "relationship_chart_consonance_policy.aspect_policy"
                ),
                "point_ids": ["SUN", "MOON"],
                "composite": {
                    "positions": {},
                    "angles": {},
                    "internal_contacts": [],
                    "angle_contacts": [],
                    "houses_calculated": False,
                },
                "davison": {
                    "positions": {},
                    "angles": {},
                    "house_cusps": {},
                    "house_placements": {},
                    "internal_contacts": [],
                    "angle_contacts": [],
                },
                "cross_consonance_contact_count": 0,
            }
        },
        "independent_roots": roots,
        "pillars": {
            "PA": 90.0,
            "PK": 90.0,
            "PE": 90.0,
            "PR": 90.0,
            "PX": 90.0,
            "PT": 90.0,
            "PS": 90.0,
            "PU": None,
        },
        "structural_model_indices": {
            model: {
                "core": 0.9,
                "support": 0.9,
                "iem_pre": 89.1,
                "ice": 0.0,
                "iem_final": 89.1,
                "essential_evaluable": True,
                "supported_gate": None,
            }
            for model in ("AF", "KA", "AG", "LG")
        },
        "counterevidence": counter,
        "pairwise_idd": {
            "AF_vs_KA": {"idd": 35.0, "band": "MATERIAL"},
            "AF_vs_AG": {"idd": 20.0, "band": "TRANSITION"},
            "AG_vs_LG": {"idd": 12.0, "band": "OVERLAP"},
        },
        "robustness_index": {
            "irc": 90.0,
            "r_min": 0.8,
            "components": [
                {
                    "id": "BIRTH_TIME",
                    "kind": "BIRTH_TIME",
                    "value": 0.9,
                    "source_module": "M23",
                    "preregistration_ref": "SYNTHETIC-ROBUSTNESS",
                    "derivation_ref": "SYNTHETIC",
                    "note": None,
                    "auto_derived": True,
                }
            ],
            "component_count": 1,
        },
    }


class TestCanonicalAssemblyQ7(unittest.TestCase):
    def test_policy_is_frozen_and_case_fit_forbidden(self):
        policy = load_canonical_assembly_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_CANONICAL_ASSEMBLY_V2",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertFalse(
            policy["principles"]["assembler_recalculates_astrology"]
        )
        self.assertEqual(
            policy["global_idd"]["method"],
            "MIN_EVALUABLE_PAIRWISE_IDD",
        )

    def test_full_structural_coverage_is_100(self):
        result = derive_canonical_coverage(
            canonical_base(),
            prior_all(),
        )
        self.assertAlmostEqual(result["ICC"], 100.0)
        self.assertTrue(
            all(
                domain["q"] == 1.0
                for domain in result["domains"].values()
            )
        )

    def test_global_idd_uses_weakest_pair(self):
        result = assemble_canonical_analysis(
            canonical_base(),
            prior_all(),
        )
        self.assertEqual(result["state"], "EVALUABLE")
        canonical = result["canonical_analysis"]
        self.assertAlmostEqual(canonical["indices"]["IDD"], 12.0)
        self.assertEqual(
            canonical["assembly"]["policy_id"],
            "ALMAS_CANONICAL_ASSEMBLY_V2",
        )

    def test_canonical_preserves_natal_context_without_recalculation(self):
        source = canonical_base()
        expected = source["natal_context"]

        result = assemble_canonical_analysis(
            source,
            prior_all(),
        )
        canonical = result["canonical_analysis"]

        self.assertEqual(canonical["natal_context"], expected)
        self.assertIsNot(canonical["natal_context"], expected)

    def test_canonical_natal_context_is_optional(self):
        source = canonical_base()
        del source["natal_context"]

        result = assemble_canonical_analysis(
            source,
            prior_all(),
        )

        self.assertNotIn("natal_context", result["canonical_analysis"])

    def test_canonical_projects_relationship_field_without_recalculation(self):
        source = canonical_base()
        expected = source["relationship_chart_consonance"]["field_context"]

        result = assemble_canonical_analysis(
            source,
            prior_all(),
        )
        canonical = result["canonical_analysis"]

        self.assertEqual(canonical["relationship_field"], expected)
        self.assertIsNot(canonical["relationship_field"], expected)
        self.assertTrue(canonical["relationship_field"]["authoring_only"])
        self.assertFalse(
            canonical["relationship_field"]["structural_evidence_used"]
        )

    def test_canonical_relationship_field_is_optional(self):
        source = canonical_base()
        del source["relationship_chart_consonance"]

        result = assemble_canonical_analysis(
            source,
            prior_all(),
        )

        self.assertNotIn("relationship_field", result["canonical_analysis"])

    def test_canonical_evidence_preserves_root_interpretive_context(self):
        result = assemble_canonical_analysis(
            canonical_base(),
            prior_all(),
        )
        evidence = result["canonical_analysis"]["evidence"]
        self.assertEqual(len(evidence), 1)
        root = evidence[0]
        self.assertEqual(root["root_id"], "R0001")
        self.assertEqual(root["point_ids"], ["MOON", "SUN"])
        self.assertEqual(root["relation_ids"], ["TRINE"])
        self.assertEqual(root["independent_family_count"], 1)
        self.assertAlmostEqual(root["max_exactness"], 0.98)
        self.assertEqual(root["root_key"], "A:SUN|B:MOON|TRINE")
        self.assertEqual(
            root["house_overlays"],
            [
                {
                    "source_subject": "A",
                    "point_id": "SUN",
                    "target_subject": "B",
                    "house": 7,
                },
                {
                    "source_subject": "B",
                    "point_id": "MOON",
                    "target_subject": "A",
                    "house": 1,
                },
            ],
        )

    def test_concrete_axis_contact_resolves_house_without_changing_root_key(self):
        canonical = canonical_base()
        cross = canonical["natal_context"]["cross_house_placements"]
        cross["A_IN_B"]["placements"]["ASC"] = {
            "house": 1,
            "longitude": 10.0,
        }
        cross["B_IN_A"]["placements"]["SUN"] = {
            "house": 7,
            "longitude": 20.0,
        }

        root = canonical["independent_roots"]["roots"][0]
        root["root_key"] = "A:AXIS_HORIZON|B:SUN|AXIS_ANGLE:0.000000"
        root["point_ids"] = ["AXIS_HORIZON", "SUN"]
        root["relation_ids"] = ["CONJUNCTION"]
        root["concrete_contacts"] = [
            {
                "evidence_id": "E-M03-0001",
                "source_module": "M03",
                "dependency_family": "SYN",
                "directional": False,
                "subject_a": "A",
                "point_a": "ASC",
                "subject_b": "B",
                "point_b": "SUN",
                "relation_id": "CONJUNCTION",
                "layer_a": "",
                "layer_b": "",
                "exactness": 0.98,
            }
        ]

        result = assemble_canonical_analysis(canonical, prior_all())
        evidence = result["canonical_analysis"]["evidence"][0]

        self.assertEqual(
            evidence["root_key"],
            "A:AXIS_HORIZON|B:SUN|AXIS_ANGLE:0.000000",
        )
        self.assertEqual(
            evidence["concrete_contacts"][0]["point_a"],
            "ASC",
        )
        self.assertEqual(
            evidence["house_overlays"],
            [
                {
                    "source_subject": "A",
                    "point_id": "ASC",
                    "target_subject": "B",
                    "house": 1,
                },
                {
                    "source_subject": "B",
                    "point_id": "SUN",
                    "target_subject": "A",
                    "house": 7,
                },
            ],
        )

    def test_house_overlays_are_not_attached_to_draconic_roots(self):
        canonical = canonical_base()
        root = canonical["independent_roots"]["roots"][0]
        root["root_key"] = "A:SUN|B:MOON|CONJUNCTION|NATAL>DRACONIC"
        root["dependency_families"] = ["NATAL_DRACONIC"]
        root["relation_ids"] = ["CONJUNCTION"]

        result = assemble_canonical_analysis(canonical, prior_all())
        evidence = result["canonical_analysis"]["evidence"]

        self.assertEqual(evidence[0]["house_overlays"], [])

    def test_house_overlays_are_not_attached_to_antiscia_only_roots(self):
        canonical = canonical_base()
        root = canonical["independent_roots"]["roots"][0]
        root["root_key"] = "A:SUN|B:MOON|CONJUNCTION"
        root["dependency_families"] = ["ANTISCIA"]
        root["relation_ids"] = ["CONJUNCTION"]

        result = assemble_canonical_analysis(canonical, prior_all())
        evidence = result["canonical_analysis"]["evidence"]

        self.assertEqual(evidence[0]["house_overlays"], [])

    def test_declination_root_can_use_natal_house_context(self):
        canonical = canonical_base()
        root = canonical["independent_roots"]["roots"][0]
        root["root_key"] = "A:SUN|B:MOON|PARALLEL"
        root["dependency_families"] = ["DECLINATION"]
        root["relation_ids"] = ["PARALLEL"]

        result = assemble_canonical_analysis(canonical, prior_all())
        evidence = result["canonical_analysis"]["evidence"]

        self.assertEqual(
            evidence[0]["house_overlays"],
            [
                {
                    "source_subject": "A",
                    "point_id": "SUN",
                    "target_subject": "B",
                    "house": 7,
                },
                {
                    "source_subject": "B",
                    "point_id": "MOON",
                    "target_subject": "A",
                    "house": 1,
                },
            ],
        )

    def test_canonical_records_missing_backend_trace_explicitly(self):
        result = assemble_canonical_analysis(
            canonical_base(),
            prior_all(),
        )
        trace = result["canonical_analysis"]["astronomy_backend"]
        self.assertEqual(trace["state"], "NOT_AVAILABLE")
        self.assertEqual(trace["provenance_state"], "NOT_AVAILABLE")
        self.assertIsNone(trace["backend_id"])
        self.assertIsNone(trace["provenance"])

    def test_canonical_propagates_production_astronomy_provenance(self):
        canonical = canonical_base()
        provenance = {
            "policy_id": "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1",
            "adapter_id": "ALMAS_MOIRA_JPL_SPK_V1",
            "backend_id": "MOIRA_JPL_SPK",
            "backend_version": "6.8.2",
            "provider_package": "moira-astro",
            "provider_version": "6.8.2",
            "kernel_filename": "de440s.bsp",
            "kernel_sha256": "a" * 64,
            "house_system": "PLACIDUS",
            "node_mode": "TRUE_NODE",
            "zodiac": "TROPICAL",
            "coordinate_origin": "GEOCENTRIC",
            "reference_frame": "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
            "apparent_reduction": True,
            "topocentric_positions": False,
            "network_io_used": False,
            "geocoding_used": False,
        }
        canonical["natal"] = {
            "backend": {
                "id": "MOIRA_JPL_SPK",
                "version": "6.8.2",
                "provenance": provenance,
            },
            "charts": {},
        }
        result = assemble_canonical_analysis(canonical, prior_all())
        trace = result["canonical_analysis"]["astronomy_backend"]
        self.assertEqual(trace["state"], "AVAILABLE")
        self.assertEqual(trace["backend_id"], "MOIRA_JPL_SPK")
        self.assertEqual(trace["backend_version"], "6.8.2")
        self.assertEqual(trace["provenance_state"], "DECLARED")
        self.assertEqual(trace["provenance"], provenance)

    def test_supported_requires_evaluable_ice(self):
        result = assemble_canonical_analysis(
            canonical_base(with_ice=False),
            prior_all(),
        )
        self.assertEqual(result["state"], "EVALUABLE")
        canonical = result["canonical_analysis"]
        self.assertIsNone(canonical["indices"]["ICE"])
        for model in ("AF", "KA", "AG", "LG"):
            self.assertNotEqual(
                canonical["models"][model]["state"],
                "SUPPORTED",
            )
            self.assertEqual(
                canonical["models"][model]["state"],
                "COMPATIBLE",
            )
            self.assertEqual(
                canonical["models"][model]["ice_state"],
                "NOT_EVALUABLE",
            )

    def test_supported_gate_can_close_after_m25(self):
        result = assemble_canonical_analysis(
            canonical_base(with_ice=True),
            prior_all(),
        )
        canonical = result["canonical_analysis"]
        self.assertEqual(canonical["coverage"]["ICC"], 100.0)
        self.assertEqual(canonical["robustness"]["IRC"], 90.0)
        self.assertEqual(canonical["robustness"]["R_min"], 0.8)
        for model in ("AF", "KA", "AG", "LG"):
            self.assertEqual(
                canonical["models"][model]["state"],
                "SUPPORTED",
            )

    def test_full_astrology_profile_can_be_ready_with_excluded_layers_not_evaluable(self):
        prior = prior_all()
        for module_id in ("M20", "M28", "M29"):
            prior[module_id] = ModuleResult(
                module_id=module_id,
                status=ExecutionStatus.NOT_EVALUABLE,
            )

        handler = make_m30_report_gate_auto()
        result = handler(
            ModuleContext(
                module_id="M30",
                module_name="report_gate",
                mode="FULL",
                raw_input={"analysis_profile": "FULL_ASTROLOGY"},
                canonical_snapshot=canonical_base(with_ice=False),
                prior_results=prior,
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        gate = result.canonical_updates["report_gate"]
        self.assertEqual(gate["analysis_profile"], "FULL_ASTROLOGY")
        self.assertEqual(gate["state"], "READY")
        self.assertTrue(gate["reportable"])
        self.assertIn(
            "M28",
            gate["profile_assessment"]["ignored_not_evaluable"],
        )

    def test_auto_m30_builds_canonical_and_reaches_ready(self):
        handler = make_m30_report_gate_auto()
        result = handler(
            ModuleContext(
                module_id="M30",
                module_name="report_gate",
                mode="FULL",
                raw_input={},
                canonical_snapshot=canonical_base(with_ice=True),
                prior_results=prior_all(),
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertIn("canonical_analysis", result.canonical_updates)
        self.assertIn("report_gate", result.canonical_updates)
        gate = result.canonical_updates["report_gate"]
        self.assertEqual(gate["state"], "READY")
        self.assertTrue(gate["reportable"])
        self.assertEqual(gate["source"], "CANONICAL_SNAPSHOT")
        self.assertIn(
            "M30 source=AUTO_CANONICAL_ASSEMBLY_Q7",
            result.diagnostics,
        )


if __name__ == "__main__":
    unittest.main()
