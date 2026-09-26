import unittest

from almas_tfa.astrology_backend import NatalRequest
from almas_tfa.handlers import configured_handlers
from almas_tfa.module_contract import ExecutionStatus
from almas_tfa.orchestrator import Orchestrator
from almas_tfa.relationship_chart_handlers import DavisonRequest


def full_manifest():
    return {
        "mode": "FULL",
        "manifest_version": "1.0.0",
        "modules": [
            {"id": f"M{i:02d}", "name": f"module_{i:02d}"}
            for i in range(32)
        ],
    }


class SyntheticNatalBackend:
    backend_id = "SYNTH_NATAL"
    backend_version = "1"

    def calculate_natal(self, request: NatalRequest):
        if request.subject_id == "A":
            positions = {
                "SUN": {
                    "longitude": 10.0,
                    "declination": 5.0,
                    "point_type": "LUMINARY",
                },
                "MOON": {
                    "longitude": 40.0,
                    "declination": 10.0,
                    "point_type": "LUMINARY",
                },
                "MARS": {
                    "longitude": 80.0,
                    "declination": 12.0,
                    "point_type": "PLANET",
                },
                "NORTH_NODE": {
                    "longitude": 100.0,
                    "declination": 2.0,
                    "point_type": "NODE",
                },
                "SOUTH_NODE": {
                    "longitude": 280.0,
                    "declination": -2.0,
                    "point_type": "NODE",
                },
                "JUNO": {
                    "longitude": 50.0,
                    "declination": 4.0,
                    "point_type": "ASTEROID",
                },
            }
            angles = {"ASC": 20.0, "MC": 110.0}
            houses = {
                str(i): float((20 + (i - 1) * 30) % 360)
                for i in range(1, 13)
            }
        else:
            positions = {
                "SUN": {
                    "longitude": 14.0,
                    "declination": 5.5,
                    "point_type": "LUMINARY",
                },
                "MOON": {
                    "longitude": 42.0,
                    "declination": -5.2,
                    "point_type": "LUMINARY",
                },
                "VENUS": {
                    "longitude": 82.0,
                    "declination": 11.5,
                    "point_type": "PLANET",
                },
                "NORTH_NODE": {
                    "longitude": 200.0,
                    "declination": -2.0,
                    "point_type": "NODE",
                },
                "SOUTH_NODE": {
                    "longitude": 20.0,
                    "declination": 2.0,
                    "point_type": "NODE",
                },
                "EROS": {
                    "longitude": 52.0,
                    "declination": 4.3,
                    "point_type": "ASTEROID",
                },
            }
            angles = {"ASC": 24.0, "MC": 114.0}
            houses = {
                str(i): float((24 + (i - 1) * 30) % 360)
                for i in range(1, 13)
            }

        return {
            "subject_id": request.subject_id,
            "timed": request.timed,
            "positions": positions,
            "angles": angles,
            "houses": houses,
        }


class SyntheticDavisonBackend:
    backend_id = "SYNTH_DAVISON"
    backend_version = "1"

    def calculate_davison(self, request: DavisonRequest):
        return {
            "positions": {
                "SUN": {"longitude": 12.0, "point_type": "LUMINARY"},
                "MOON": {"longitude": 41.0, "point_type": "LUMINARY"},
                "MARS": {"longitude": 81.0, "point_type": "PLANET"},
            },
            "angles": {"ASC": 22.0, "MC": 112.0},
        }


class TestFullPipelineSynthetic(unittest.TestCase):
    def test_m00_m31_complete_with_explicit_inputs(self):
        subjects = [
            {
                "id": "A",
                "birth_date": "1977-03-20",
                "birth_time": "17:45",
                "timezone": "Europe/Madrid",
                "latitude": 41.65,
                "longitude": -0.88,
                "time_reliability": "A",
            },
            {
                "id": "B",
                "birth_date": "1980-01-01",
                "birth_time": "12:00",
                "timezone": "America/Santo_Domingo",
                "latitude": 18.48,
                "longitude": -69.91,
                "time_reliability": "A",
            },
        ]

        aspect_policy = {
            "CONJUNCTION": {"angle": 0, "orb": 6},
            "OPPOSITION": {"angle": 180, "orb": 6},
            "TRINE": {"angle": 120, "orb": 5},
            "SQUARE": {"angle": 90, "orb": 5},
            "SEXTILE": {"angle": 60, "orb": 4},
        }

        canonical_analysis = {
            "schema_version": "1.0.0",
            "analysis_mode": "FULL",
            "evidence": [
                {
                    "evidence_id": "CANONICAL_E1",
                    "source_module": "M17",
                    "root_id": "R0001",
                    "note": "Synthetic canonical evidence for report-gate traceability."
                }
            ],
            "models": {
                "AF": {"iem": 80, "state": "COMPATIBLE"},
                "KA": {"iem": 70, "state": "COMPATIBLE"},
                "AG": {"iem": 82, "state": "COMPATIBLE"},
                "LG": {"iem": 79, "state": "INSUFFICIENT"},
            },
            "indices": {
                "IDD": 35,
                "IAT": None,
                "ICC": 90,
                "IRC": 80,
                "ICE": 5,
            },
            "coverage": {"ICC": 90},
            "robustness": {"IRC": 80},
            "counterevidence": [],
            "ontology": {},
            "doctrine": [],
            "temporal": {},
            "limitations": [],
        }

        raw = {
            "mode": "FULL",
            "subjects": subjects,
            "aspect_policy": aspect_policy,
            "rulership_policy": {
                "ARIES": ["MARS"],
                "TAURUS": ["VENUS"],
                "GEMINI": ["MERCURY"],
                "CANCER": ["MOON"],
                "LEO": ["SUN"],
                "VIRGO": ["MERCURY"],
                "LIBRA": ["VENUS"],
                "SCORPIO": ["MARS"],
                "SAGITTARIUS": ["JUPITER"],
                "CAPRICORN": ["SATURN"],
                "AQUARIUS": ["SATURN"],
                "PISCES": ["JUPITER"],
            },
            "declination_policy": {
                "parallel_orb": 1.0,
                "contra_parallel_orb": 1.0,
            },
            "antiscia_policy": {
                "antiscia_orb": 3.0,
                "contra_antiscia_orb": 3.0,
            },
            "composite_policy": {
                "midpoint_mode": "SHORTEST_ARC",
                "opposition_tie_break": "NOT_EVALUABLE",
            },
            "davison_policy": {
                "time_midpoint": "UTC_INSTANT",
                "geographic_midpoint": "BACKEND_DECLARED",
            },
            "relationship_chart_consonance_policy": {
                "point_ids": ["SUN", "MOON", "MARS"],
                "aspect_policy": {
                    "CONJUNCTION": {"angle": 0, "orb": 3}
                },
            },
            "draconic_policy": {
                "node_id": "NORTH_NODE",
                "transform": "NORTH_NODE_TO_ZERO",
                "include_angles": True,
                "include_houses": True,
            },
            "draconic_aspect_policy": aspect_policy,
            "lot_policy": {
                "sect_by_subject": {"A": "DAY", "B": "NIGHT"},
                "lots": [
                    {
                        "id": "FORTUNE",
                        "source_ref": "SYNTH_LOT_SOURCE",
                        "variants": {
                            "DAY": {
                                "base": "ASC",
                                "add": ["MOON"],
                                "subtract": ["SUN"],
                            },
                            "NIGHT": {
                                "base": "ASC",
                                "add": ["SUN"],
                                "subtract": ["MOON"],
                            },
                        },
                    }
                ],
            },
            "secondary_symbolic_policy": {
                "point_ids": ["JUNO", "EROS"],
                "support_only": True,
                "aspect_policy": aspect_policy,
            },
            "root_strengths": {
                "PA": [0.9, 0.8, 0.7],
                "PK": [0.7, 0.6, 0.5],
                "PE": [0.9, 0.8, 0.6],
                "PR": [0.9, 0.85, 0.75],
                "PX": [0.8, 0.7, 0.6],
                "PT": [0.75, 0.7, 0.65],
                "PS": [0.6, 0.55, 0.5],
                "PU": [0.4, 0.3, 0.2],
            },
            "ice_by_model": {"AF": 0, "KA": 5, "AG": 5, "LG": 10},
            "icc": 90,
            "irc": 80,
            "r_min": 0.8,
            "essential_contradictions": {},
            "counterevidence_items": [
                {
                    "id": "CE1",
                    "kind": "STRUCTURAL_INCOMPATIBILITY",
                    "models": ["LG"],
                    "contradiction_key": "SYNTH_LIMIT",
                    "dependency_family": "SYNTH",
                    "essential": False,
                    "severity": 0.2,
                }
            ],
            "attributions": {
                "AF": {"r1": 1.0, "r2": 0.5},
                "KA": {"r3": 1.0, "r4": 0.5},
                "AG": {"r1": 0.5, "r5": 1.0},
                "LG": {"r1": 0.3, "r6": 1.0},
            },
            "time_sensitivity_summary": {
                "preregistration_ref": "TS-FULL-001",
                "subject_scope": "BOTH",
                "perturbation_rule": "synthetic",
                "metric": "IEM_BAND",
                "delta90": 5,
                "preserved_fraction": 0.9,
                "perturbation_count": 100,
            },
            "null_model_runs": [
                {
                    "id": "NULL1",
                    "null_model": "PAIR_SHUFFLE",
                    "preregistration_ref": "NULL-FULL-001",
                    "feature_set_ref": "FEATURES-FULL-001",
                    "orb_policy_ref": "ORBS-FULL-001",
                    "event_set_ref": "EVENTS-FULL-001",
                    "generator_ref": "GEN-FULL-001",
                    "statistic_id": "ROOT_COUNT",
                    "observed_value": 88,
                    "tail": "GREATER_OR_EQUAL",
                    "n": 1000,
                    "extreme_count": 50,
                }
            ],
            "robustness_component_summaries": [
                {
                    "id": "ABLATION_CORE",
                    "kind": "ABLATION",
                    "value": 0.85,
                    "source_module": "M22",
                    "preregistration_ref": "ROB-FULL-AB",
                    "derivation_ref": "ABLATION-RULE-FULL",
                },
                {
                    "id": "PARAMETER",
                    "kind": "PARAMETER_PERTURBATION",
                    "value": 0.9,
                    "source_module": "EXTERNAL",
                    "preregistration_ref": "ROB-FULL-P",
                    "derivation_ref": "PARAM-RULE-FULL",
                },
            ],
            "temporal_signals": [
                {
                    "signal_id": "T1",
                    "root_id": "R0001",
                    "temporal_family": "TTRANSIT",
                    "activation_class": "DIRECT_REPETITION",
                    "strength": 0.9,
                    "window_status": "CURRENT_ACTIVE",
                    "preregistered": True,
                    "date_or_period": "2030-04",
                }
            ],
            "documentary_event_ledger": {
                "schema_version": "1.0.0",
                "analysis_freeze_ref": "FREEZE-FULL-001",
                "events": [
                    {
                        "event_id": "E1",
                        "subjects": ["A", "B"],
                        "event_type": "RELATIONSHIP_CHANGE",
                        "date": "2030-04-12",
                        "date_precision": "EXACT_DATE",
                        "fact_statement": "Synthetic viability fact.",
                        "documentary_quality": "DQ3_CORROBORATED_REPORT",
                        "source_refs": ["S1", "S1B"],
                        "source_independence_declared": True,
                        "privacy_class": "SYNTHETIC",
                        "evidence_roles": [
                            "ACTIVATION_CORROBORATION",
                            "VIABILITY_FACT",
                        ],
                        "linked_root_refs": ["R0001"],
                    },
                    {
                        "event_id": "E2",
                        "subjects": ["A", "B"],
                        "event_type": "COMMITMENT",
                        "date": "2030-05-01",
                        "date_precision": "EXACT_DATE",
                        "fact_statement": "Synthetic reciprocity fact.",
                        "documentary_quality": "DQ3_CORROBORATED_REPORT",
                        "source_refs": ["S2", "S2B"],
                        "source_independence_declared": True,
                        "privacy_class": "SYNTHETIC",
                        "evidence_roles": ["RECIPROCITY_FACT"],
                        "linked_root_refs": ["R0001"],
                    },
                ],
            },
            "doctrinal_claims": [
                {
                    "schema_version": "2.0.0",
                    "claim_id": "D1",
                    "statement": "Synthetic doctrinal statement.",
                    "epistemic_class": "C_DOCTRINE",
                    "claim_scope": "DOCTRINAL_ATTRIBUTION",
                    "concept_id": "SYNTHETIC_DOCTRINE",
                    "source_relation": "DIRECT_DOCTRINE",
                    "source_ids": ["SRC1"],
                    "source_anchor_refs": ["SRC1"],
                    "source_support_refs": [
                        {"source_id": "SRC1", "support_index": 0}
                    ],
                    "does_not_support_checked": True,
                    "asserts_doctrinal_identity": False,
                    "astrological_refs": [],
                    "status": "SUPPORTED",
                    "requested_conclusion": "SYNTHETIC_DOCTRINAL_ATTRIBUTION",
                    "allowed_conclusion": "SYNTHETIC_DOCTRINAL_ATTRIBUTION",
                    "inferential_ceiling": "DIRECT_DOCTRINE_ONLY",
                    "discriminator_id": None,
                    "discriminator_state": "DOCTRINAL_ONLY",
                    "ceiling_enforced": True,
                    "alternatives": [],
                    "limitations": ["Synthetic doctrine fixture only."],
                }
            ],
            "source_registry": {
                "registry_version": "TEST-1",
                "entries": [
                    {
                        "id": "SRC1",
                        "priority": "P1_PRIMARY",
                        "source_role": "DOCTRINAL_PRIMARY",
                        "tradition": "Synthetic tradition",
                        "author": "Synthetic Author",
                        "work": "Synthetic Work",
                        "concepts": ["SYNTHETIC_DOCTRINE"],
                        "supports": ["Synthetic doctrinal statement."],
                        "does_not_support": ["Cross-tradition identity."],
                        "verification_status": "VERIFIED_PRIMARY",
                        "verification_anchor": "Synthetic exact passage.",
                        "verification_anchor_type": "EXACT_PASSAGE",
                        "evidence_scope": "DOCTRINAL_CLAIM",
                    }
                ],
            },
            "viability_reciprocity_assessment": {
                "assessment_ref": "VR-FULL-001",
                "as_of_date": "2030-05-01",
                "subjects": ["A", "B"],
                "real_viability": "STABLE",
                "reciprocity": "BILATERAL",
                "viability_basis": [
                    {
                        "event_id": "E1",
                        "basis_kind": "OBSERVED_STABLE_RELATIONSHIP",
                        "observation_type": "DOCUMENTED_STATUS",
                        "subject_ids": ["A", "B"],
                    }
                ],
                "reciprocity_basis": [
                    {
                        "event_id": "E2",
                        "basis_kind": "DOCUMENTED_BILATERALITY",
                        "observation_type": "MUTUAL_AGREEMENT",
                        "subject_ids": ["A", "B"],
                    }
                ],
            },
            "canonical_analysis": canonical_analysis,
        }

        handlers = configured_handlers(
            astrology_backend=SyntheticNatalBackend(),
            davison_backend=SyntheticDavisonBackend(),
        )
        run = Orchestrator(handlers).run(
            raw,
            full_manifest(),
            stop_on_failure=True,
        )

        statuses = {
            module_id: result.status for module_id, result in run.results.items()
        }
        self.assertEqual(set(statuses), {f"M{i:02d}" for i in range(32)})
        self.assertTrue(
            all(status is ExecutionStatus.COMPLETED for status in statuses.values()),
            msg=statuses,
        )

        self.assertIn("report_document_model", run.canonical)
        self.assertIn("independent_roots", run.canonical)
        self.assertIn("temporal_activation", run.canonical)
        self.assertIn("documentary_events", run.canonical)
        report_model = run.canonical["report_document_model"]
        self.assertEqual(report_model["report_state"], "READY")
        self.assertTrue(report_model["canonical_fingerprint_verified"])
        self.assertEqual(
            report_model["canonical_fingerprint"],
            run.canonical["report_gate"]["canonical_fingerprint"],
        )
        self.assertEqual(len(report_model["sections"]), 11)
        self.assertEqual(
            sum(report_model["section_counts"].values()),
            11,
        )
        self.assertFalse(report_model["canonical_values_embedded"])
        self.assertFalse(report_model["canonical_values_mutated"])
        self.assertFalse(report_model["prose_generated"])
        self.assertFalse(report_model["rendered_document_created"])
        self.assertFalse(report_model["docx_created"])
        self.assertFalse(report_model["pdf_created"])
        self.assertIn("promotion_reporting", report_model)
        promotion_reporting = report_model["promotion_reporting"]
        self.assertTrue(promotion_reporting["methodological_status_only"])
        self.assertFalse(promotion_reporting["ontological_inference_allowed"])
        self.assertFalse(promotion_reporting["case_classification_mutated"])
        self.assertFalse(promotion_reporting["irc_mutated"])
        self.assertEqual(
            promotion_reporting["summary_counts"]["VALIDATED_DISCRIMINATOR"],
            0,
        )
        source_genealogy = promotion_reporting["source_genealogy"]
        self.assertIsInstance(source_genealogy, dict)
        self.assertEqual(
            source_genealogy["authority"],
            "ALMAS_CANONICAL_DISCRIMINATOR_SOURCE_GENEALOGY",
        )
        self.assertTrue(source_genealogy["methodological_provenance_only"])
        self.assertFalse(source_genealogy["ontological_inference_allowed"])
        self.assertFalse(source_genealogy["source_count_adds_weight"])
        self.assertFalse(
            source_genealogy["source_priority_adds_ontological_weight"]
        )
        self.assertEqual(len(source_genealogy["records"]), 7)
        self.assertTrue(
            all(
                record["can_change_case_classification"] is False
                and record["can_raise_irc"] is False
                for record in source_genealogy["records"]
            )
        )
        by_section = {
            section["section_id"]: section
            for section in report_model["sections"]
        }
        self.assertEqual(
            by_section["S08_ROBUSTNESS"]["methodological_reporting_paths"],
            ["promotion_reporting"],
        )
        self.assertEqual(
            by_section["S11_SOURCES_APPENDICES"]["methodological_reporting_paths"],
            ["promotion_reporting"],
        )


if __name__ == "__main__":
    unittest.main()
