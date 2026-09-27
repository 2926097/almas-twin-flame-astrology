import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.relationship_consonance import m09_relationship_chart_consonance


class TestRelationshipChartConsonance(unittest.TestCase):
    def test_requires_both_relationship_charts(self):
        context = ModuleContext(
            module_id="M09",
            module_name="relchart",
            mode="FULL",
            raw_input={},
            canonical_snapshot={"composite": {}},
            prior_results={},
        )
        result = m09_relationship_chart_consonance(context)
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_compares_shared_points_under_declared_orb(self):
        canonical = {
            "composite": {
                "positions": {
                    "SUN": {"longitude": 10.0},
                    "MOON": {"longitude": 90.0},
                },
                "angles": {
                    "ASC": {"longitude": 5.0, "ambiguous": False},
                },
                "houses_calculated": False,
            },
            "davison": {
                "chart": {
                    "positions": {
                        "SUN": {"longitude": 12.0},
                        "MOON": {"longitude": 270.0},
                    },
                    "angles": {"ASC": 15.0},
                    "houses": {
                        "1": 15.0,
                        "2": 45.0,
                    },
                }
            },
        }
        raw = {
            "relationship_chart_consonance_policy": {
                "point_ids": ["SUN", "MOON"],
                "aspect_policy": {
                    "CONJUNCTION": {"angle": 0, "orb": 3},
                    "OPPOSITION": {"angle": 180, "orb": 3},
                },
            }
        }
        context = ModuleContext(
            module_id="M09",
            module_name="relchart",
            mode="FULL",
            raw_input=raw,
            canonical_snapshot=canonical,
            prior_results={},
        )
        result = m09_relationship_chart_consonance(context)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["relationship_chart_consonance"]
        self.assertEqual(output["dependency_family"], "RELCHART")
        self.assertEqual(output["contact_count"], 2)
        self.assertIsNone(output["consonance_score"])
        self.assertEqual(output["score_state"], "NOT_DEFINED")

        field = output["field_context"]
        self.assertTrue(field["authoring_only"])
        self.assertFalse(field["structural_evidence_used"])
        self.assertFalse(field["creates_independent_roots"])
        self.assertEqual(
            field["composite"]["positions"]["SUN"]["sign"],
            "ARIES",
        )
        self.assertEqual(
            field["davison"]["positions"]["MOON"]["sign"],
            "CAPRICORN",
        )
        self.assertFalse(field["composite"]["houses_calculated"])
        self.assertEqual(
            field["davison"]["house_cusps"]["1"]["sign"],
            "ARIES",
        )
        self.assertEqual(field["davison"]["house_placements"], {})
        self.assertEqual(field["cross_consonance_contact_count"], 2)

    def test_field_context_assigns_davison_points_to_precomputed_houses(self):
        houses = {
            str(index): float((index - 1) * 30)
            for index in range(1, 13)
        }
        canonical = {
            "composite": {
                "positions": {
                    "SUN": {"longitude": 12.0},
                    "MOON": {"longitude": 270.0},
                },
                "angles": {},
                "houses_calculated": False,
            },
            "davison": {
                "chart": {
                    "positions": {
                        "SUN": {"longitude": 12.0},
                        "MOON": {"longitude": 270.0},
                    },
                    "angles": {},
                    "houses": houses,
                }
            },
        }
        raw = {
            "relationship_chart_consonance_policy": {
                "point_ids": ["SUN", "MOON"],
                "aspect_policy": {
                    "CONJUNCTION": {"angle": 0, "orb": 3},
                    "OPPOSITION": {"angle": 180, "orb": 3},
                },
            }
        }

        result = m09_relationship_chart_consonance(
            ModuleContext(
                module_id="M09",
                module_name="relchart",
                mode="FULL",
                raw_input=raw,
                canonical_snapshot=canonical,
                prior_results={},
            )
        )
        placements = result.canonical_updates[
            "relationship_chart_consonance"
        ]["field_context"]["davison"]["house_placements"]

        self.assertEqual(placements["SUN"], 1)
        self.assertEqual(placements["MOON"], 10)

    def test_field_context_calculates_position_angle_contacts_without_structural_evidence(self):
        canonical = {
            "composite": {
                "positions": {
                    "SUN": {"longitude": 10.0},
                },
                "angles": {
                    "ASC": {"longitude": 12.0, "ambiguous": False},
                },
                "houses_calculated": False,
            },
            "davison": {
                "chart": {
                    "positions": {
                        "SUN": {"longitude": 20.0},
                    },
                    "angles": {"MC": 110.0},
                    "houses": {},
                }
            },
        }
        raw = {
            "relationship_chart_consonance_policy": {
                "point_ids": ["SUN"],
                "aspect_policy": {
                    "CONJUNCTION": {"angle": 0, "orb": 3},
                    "SQUARE": {"angle": 90, "orb": 3},
                },
            }
        }
        result = m09_relationship_chart_consonance(
            ModuleContext(
                module_id="M09",
                module_name="relchart",
                mode="FULL",
                raw_input=raw,
                canonical_snapshot=canonical,
                prior_results={},
            )
        )
        output = result.canonical_updates["relationship_chart_consonance"]

        self.assertEqual(output["contacts"], [])
        self.assertEqual(output["contact_count"], 0)

        composite_contact = output["field_context"]["composite"][
            "angle_contacts"
        ][0]
        self.assertEqual(composite_contact["point_a"], "SUN")
        self.assertEqual(composite_contact["point_b"], "ASC")
        self.assertEqual(composite_contact["aspect"], "CONJUNCTION")

        davison_contact = output["field_context"]["davison"][
            "angle_contacts"
        ][0]
        self.assertEqual(davison_contact["point_a"], "SUN")
        self.assertEqual(davison_contact["point_b"], "MC")
        self.assertEqual(davison_contact["aspect"], "SQUARE")

        self.assertTrue(output["field_context"]["authoring_only"])
        self.assertFalse(output["field_context"]["structural_evidence_used"])
        self.assertFalse(output["field_context"]["creates_independent_roots"])

    def test_field_context_calculates_internal_aspects_without_structural_contacts(self):
        canonical = {
            "composite": {
                "positions": {
                    "SUN": {"longitude": 0.0},
                    "VENUS": {"longitude": 2.0},
                },
                "angles": {},
                "houses_calculated": False,
            },
            "davison": {
                "chart": {
                    "positions": {
                        "SUN": {"longitude": 0.0},
                        "VENUS": {"longitude": 120.0},
                    },
                    "angles": {},
                    "houses": {},
                }
            },
        }
        raw = {
            "relationship_chart_consonance_policy": {
                "point_ids": ["SUN", "VENUS"],
                "aspect_policy": {
                    "CONJUNCTION": {"angle": 0, "orb": 3},
                    "TRINE": {"angle": 120, "orb": 3},
                },
            }
        }
        result = m09_relationship_chart_consonance(
            ModuleContext(
                module_id="M09",
                module_name="relchart",
                mode="FULL",
                raw_input=raw,
                canonical_snapshot=canonical,
                prior_results={},
            )
        )
        output = result.canonical_updates["relationship_chart_consonance"]

        self.assertEqual(output["contact_count"], 2)
        self.assertTrue(
            all(
                item["point_a"] == item["point_b"]
                for item in output["contacts"]
            )
        )
        field = output["field_context"]
        self.assertEqual(
            field["composite"]["internal_contacts"][0]["aspect"],
            "CONJUNCTION",
        )
        self.assertEqual(
            field["davison"]["internal_contacts"][0]["aspect"],
            "TRINE",
        )
        self.assertNotEqual(
            field["composite"]["internal_contacts"],
            output["contacts"],
        )


if __name__ == "__main__":
    unittest.main()
