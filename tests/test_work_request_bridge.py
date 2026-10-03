import unittest

from almas_tfa.work_request import (
    WorkRequestError,
    assess_work_request,
    build_raw_input_from_work_request,
)


def envelope():
    return {
        "case_title": "Synthetic relational case",
        "research_question": "Synthetic research question",
        "request": {
            "format": "ALMAS_WORK_REQUEST",
            "public_version": "1.25.0",
            "type": "RELATIONAL",
            "analysis_profile": "FULL_ASTROLOGY",
            "subjects": [
                {
                    "id": "SYNTH-A",
                    "display_name": "Synthetic A",
                    "birth_date": "1977-03-20",
                    "birth_time": "17:45",
                    "timezone": "Europe/Madrid",
                    "place": "Synthetic Place A",
                    "latitude": 41.65,
                    "longitude": -0.88,
                    "time_reliability": "D",
                    "birth_time_source_class": "DOCUMENTARY",
                },
                {
                    "id": "SYNTH-B",
                    "display_name": "Synthetic B",
                    "birth_date": "1991-05-23",
                    "birth_time": "04:15",
                    "timezone": "America/Santo_Domingo",
                    "place": "Synthetic Place B",
                    "latitude": 18.45,
                    "longitude": -69.31,
                    "time_reliability": "B",
                    "birth_time_source_class": "REPORTED",
                },
            ],
            "situation_location": {
                "place": "Synthetic Situation",
                "latitude": "41.65606",
                "longitude": "-0.87734",
                "timezone": "Europe/Madrid",
            },
            "research_question": "Synthetic research question",
            "events": [],
            "execution_state": "REQUEST_ONLY",
        },
        "chronology": [],
    }


def explicit_policies():
    aspect_policy = {
        "CONJUNCTION": {"angle": 0, "orb": 6},
        "OPPOSITION": {"angle": 180, "orb": 6},
        "TRINE": {"angle": 120, "orb": 5},
        "SQUARE": {"angle": 90, "orb": 5},
        "SEXTILE": {"angle": 60, "orb": 4},
    }
    return {
        "schema_version": "1.0.0",
        "policy_bundle_id": "SYNTHETIC_RELATIONAL_POLICY_V1",
        "aspect_policy": aspect_policy,
        "declination_policy": {
            "parallel_orb": 1.0,
            "contra_parallel_orb": 1.0,
        },
        "antiscia_policy": {
            "antiscia_orb": 3.0,
            "contra_antiscia_orb": 3.0,
        },
        "relationship_chart_consonance_policy": {
            "point_ids": ["SUN", "MOON"],
            "aspect_policy": {
                "CONJUNCTION": {"angle": 0, "orb": 3}
            },
        },
        "draconic_aspect_policy": aspect_policy,
    }


class WorkRequestBridgeTests(unittest.TestCase):
    def test_request_only_reports_missing_explicit_policies(self):
        result = assess_work_request(envelope())

        self.assertFalse(result["execution_ready"])
        self.assertFalse(result["implicit_orbs_used"])
        self.assertFalse(result["case_fitting_used"])
        self.assertEqual(
            result["missing_policies"],
            [
                "antiscia_policy",
                "aspect_policy",
                "declination_policy",
                "draconic_aspect_policy",
                "relationship_chart_consonance_policy",
            ],
        )
        self.assertIn(
            "analysis_policies.policy_bundle_id es obligatorio.",
            result["policy_errors"],
        )

    def test_normative_non_orb_policies_are_injected(self):
        result = assess_work_request(envelope())
        policies = result["analysis_policies"]

        self.assertEqual(
            policies["composite_policy"]["midpoint_mode"],
            "SHORTEST_ARC",
        )
        self.assertEqual(
            policies["davison_policy"]["time_midpoint"],
            "UTC_INSTANT",
        )
        self.assertEqual(
            policies["davison_policy"]["geographic_midpoint"],
            "SPHERICAL_GREAT_CIRCLE",
        )
        self.assertEqual(
            policies["draconic_policy"]["node_id"],
            "NORTH_NODE",
        )

    def test_incomplete_request_fails_closed_when_building_raw_input(self):
        with self.assertRaisesRegex(
            WorkRequestError,
            "no está listo para ejecución",
        ):
            build_raw_input_from_work_request(envelope())

    def test_explicit_policy_bundle_builds_full_astrology_raw_input(self):
        payload = envelope()
        payload["request"]["analysis_policies"] = explicit_policies()

        assessment = assess_work_request(payload)
        self.assertTrue(assessment["execution_ready"])
        self.assertEqual(assessment["missing_policies"], [])
        self.assertEqual(assessment["policy_errors"], [])

        raw = build_raw_input_from_work_request(payload)
        self.assertEqual(raw["mode"], "FULL")
        self.assertEqual(raw["analysis_profile"], "FULL_ASTROLOGY")
        self.assertEqual(len(raw["subjects"]), 2)
        self.assertEqual(
            raw["analysis_policy_bundle"]["policy_bundle_id"],
            "SYNTHETIC_RELATIONAL_POLICY_V1",
        )
        self.assertFalse(
            raw["analysis_policy_bundle"]["implicit_orbs_used"]
        )
        self.assertEqual(
            raw["situation_location"]["latitude"],
            41.65606,
        )
        self.assertEqual(
            raw["situation_location"]["longitude"],
            -0.87734,
        )
        self.assertIn("aspect_policy", raw)
        self.assertIn("declination_policy", raw)
        self.assertIn("antiscia_policy", raw)
        self.assertIn("composite_policy", raw)
        self.assertIn("davison_policy", raw)
        self.assertIn("relationship_chart_consonance_policy", raw)
        self.assertIn("draconic_policy", raw)
        self.assertIn("draconic_aspect_policy", raw)

    def test_explicit_preset_ref_expands_to_reproducible_policies(self):
        payload = envelope()
        payload["request"]["analysis_policies"] = {
            "schema_version": "1.0.0",
            "policy_bundle_id": "ALMAS_RELATIONAL_ORB_BASELINE_V1",
            "preset_ref": "ALMAS_RELATIONAL_ORB_BASELINE_V1",
        }

        assessment = assess_work_request(payload)
        self.assertTrue(assessment["execution_ready"])
        self.assertEqual(
            assessment["preset_ref"],
            "ALMAS_RELATIONAL_ORB_BASELINE_V1",
        )
        self.assertEqual(
            assessment["analysis_policies"]["aspect_policy"]["CONJUNCTION"]["orb"],
            6,
        )
        self.assertEqual(
            assessment["analysis_policies"]["declination_policy"]["parallel_orb"],
            1.0,
        )
        self.assertEqual(
            assessment["analysis_policies"]["antiscia_policy"]["antiscia_orb"],
            1.0,
        )
        self.assertEqual(
            assessment["analysis_policies"]["draconic_aspect_policy"],
            {
                "CONJUNCTION": {"angle": 0, "orb": 3},
                "OPPOSITION": {"angle": 180, "orb": 3},
            },
        )

        raw = build_raw_input_from_work_request(payload)
        self.assertEqual(
            raw["analysis_policy_bundle"]["preset_ref"],
            "ALMAS_RELATIONAL_ORB_BASELINE_V1",
        )
        self.assertEqual(
            raw["analysis_policy_bundle"]["preset_epistemic_class"],
            "E_PROJECT_POLICY",
        )
        self.assertEqual(
            raw["analysis_policy_bundle"]["preset_external_validation_status"],
            "NOT_PERFORMED",
        )

    def test_preset_ref_rejects_inline_orb_overrides(self):
        payload = envelope()
        payload["request"]["analysis_policies"] = {
            "schema_version": "1.0.0",
            "policy_bundle_id": "ALMAS_RELATIONAL_ORB_BASELINE_V1",
            "preset_ref": "ALMAS_RELATIONAL_ORB_BASELINE_V1",
            "aspect_policy": {
                "CONJUNCTION": {"angle": 0, "orb": 9}
            },
        }
        result = assess_work_request(payload)
        self.assertFalse(result["execution_ready"])
        self.assertTrue(
            any("no admite overrides inline" in item for item in result["policy_errors"])
        )

    def test_relchart_policy_without_nested_aspects_is_rejected(self):
        payload = envelope()
        policies = explicit_policies()
        policies["relationship_chart_consonance_policy"] = {
            "point_ids": ["SUN", "MOON"]
        }
        payload["request"]["analysis_policies"] = policies

        result = assess_work_request(payload)
        self.assertFalse(result["execution_ready"])
        self.assertIn(
            "relationship_chart_consonance_policy.aspect_policy es obligatorio.",
            result["policy_errors"],
        )

    def test_normative_policy_override_is_rejected(self):
        payload = envelope()
        policies = explicit_policies()
        policies["davison_policy"] = {
            "time_midpoint": "LOCAL_TIME",
            "geographic_midpoint": "SPHERICAL_GREAT_CIRCLE",
        }
        payload["request"]["analysis_policies"] = policies

        result = assess_work_request(payload)
        self.assertFalse(result["execution_ready"])
        self.assertTrue(
            any("davison_policy diverge" in item for item in result["policy_errors"])
        )

    def test_negative_declination_orb_is_rejected(self):
        payload = envelope()
        policies = explicit_policies()
        policies["declination_policy"]["parallel_orb"] = -1
        payload["request"]["analysis_policies"] = policies

        result = assess_work_request(payload)
        self.assertFalse(result["execution_ready"])
        self.assertTrue(
            any("no puede ser negativo" in item for item in result["policy_errors"])
        )

    def test_other_profiles_fail_closed_in_bridge_v1(self):
        payload = envelope()
        payload["request"]["analysis_profile"] = "TEMPORAL"
        payload["request"]["analysis_policies"] = explicit_policies()

        result = assess_work_request(payload)
        self.assertFalse(result["bridge_profile_supported"])
        self.assertFalse(result["execution_ready"])
        self.assertTrue(
            any("sólo declara execution_ready para FULL_ASTROLOGY" in item for item in result["policy_errors"])
        )

    def test_version_mismatch_is_rejected(self):
        payload = envelope()
        payload["request"]["public_version"] = "9.9.9"
        with self.assertRaisesRegex(
            WorkRequestError,
            "Versión del request incompatible",
        ):
            assess_work_request(payload)


if __name__ == "__main__":
    unittest.main()
