import unittest

from almas_tfa.relational_request_pipeline import (
    RelationalWorkRequestError,
    assess_relational_work_request,
    prepare_relational_raw_input,
)


def subjects():
    return [
        {
            "id": "A",
            "display_name": "Caso A",
            "birth_date": "1977-03-20",
            "birth_time": "17:45",
            "timezone": "Europe/Madrid",
            "place": "Zaragoza",
            "latitude": 41.65606,
            "longitude": -0.87734,
            "time_reliability": "D",
            "birth_time_source_class": "DOCUMENTARY",
        },
        {
            "id": "B",
            "display_name": "Caso B",
            "birth_date": "1991-05-23",
            "birth_time": "04:15",
            "timezone": "America/Santo_Domingo",
            "place": "San Pedro de Macoris",
            "latitude": 18.4539,
            "longitude": -69.30864,
            "time_reliability": "B",
            "birth_time_source_class": "REPORTED",
        },
    ]


def declared_policies():
    aspect = {
        "CONJUNCTION": {"angle": 0, "orb": 6},
        "OPPOSITION": {"angle": 180, "orb": 6},
    }
    return {
        "aspect_policy": aspect,
        "declination_policy": {
            "parallel_orb": 1.0,
            "contra_parallel_orb": 1.0,
        },
        "antiscia_policy": {
            "antiscia_orb": 2.0,
            "contra_antiscia_orb": 2.0,
        },
        "relationship_chart_consonance_policy": {
            "point_ids": ["SUN", "MOON"],
            "aspect_policy": {
                "CONJUNCTION": {"angle": 0, "orb": 3}
            },
        },
        "draconic_aspect_policy": aspect,
    }


def work_request(include_policies=True):
    request = {
        "format": "ALMAS_WORK_REQUEST",
        "public_version": "1.25.0",
        "type": "RELATIONAL",
        "analysis_profile": "FULL_ASTROLOGY",
        "subjects": subjects(),
        "events": [],
        "execution_state": "REQUEST_ONLY",
    }
    if include_policies:
        request["analysis_policies"] = declared_policies()
    return {
        "case_title": "synthetic",
        "research_question": "synthetic",
        "request": request,
        "situation": {},
        "chronology": [],
    }


class RelationalRequestPipelineTests(unittest.TestCase):
    def test_complete_request_is_ready_and_flattens_policies(self):
        assessment = assess_relational_work_request(work_request())
        self.assertTrue(assessment["ready_for_raw_input"])

        raw = prepare_relational_raw_input(work_request())
        self.assertEqual(raw["mode"], "FULL")
        self.assertEqual(raw["analysis_profile"], "FULL_ASTROLOGY")
        self.assertEqual(raw["subjects"][0]["time_reliability"], "D")
        self.assertEqual(raw["subjects"][1]["time_reliability"], "B")
        self.assertEqual(
            raw["davison_policy"]["geographic_midpoint"],
            "SPHERICAL_GREAT_CIRCLE",
        )
        self.assertEqual(
            raw["draconic_policy"]["transform"],
            "NORTH_NODE_TO_ZERO",
        )
        self.assertFalse(raw["request_adapter_trace"]["implicit_orbs_used"])

    def test_missing_declared_orbs_fail_closed(self):
        assessment = assess_relational_work_request(
            work_request(include_policies=False)
        )
        self.assertFalse(assessment["ready_for_raw_input"])
        self.assertIn(
            "aspect_policy",
            assessment["missing_declared_policies"],
        )
        with self.assertRaisesRegex(
            RelationalWorkRequestError,
            "ALMAS no infiere orbes",
        ):
            prepare_relational_raw_input(
                work_request(include_policies=False)
            )

    def test_incomplete_preview_does_not_invent_orbs(self):
        raw = prepare_relational_raw_input(
            work_request(include_policies=False),
            require_complete=False,
        )
        self.assertNotIn("aspect_policy", raw)
        self.assertNotIn("draconic_aspect_policy", raw)
        self.assertIn("composite_policy", raw)
        self.assertTrue(
            raw["request_adapter_trace"]["missing_declared_policies"]
        )

    def test_fixed_policy_conflict_is_rejected(self):
        payload = work_request()
        payload["request"]["analysis_policies"]["davison_policy"] = {
            "time_midpoint": "LOCAL_TIME",
            "geographic_midpoint": "SPHERICAL_GREAT_CIRCLE",
        }
        with self.assertRaisesRegex(
            RelationalWorkRequestError,
            "contradice la convención congelada",
        ):
            prepare_relational_raw_input(payload)

    def test_version_mismatch_is_rejected(self):
        payload = work_request()
        payload["request"]["public_version"] = "9.9.9"
        with self.assertRaisesRegex(
            RelationalWorkRequestError,
            "public_version incompatible",
        ):
            prepare_relational_raw_input(payload)

    def test_invalid_declared_orb_is_rejected(self):
        payload = work_request()
        payload["request"]["analysis_policies"]["aspect_policy"] = {
            "CONJUNCTION": {"angle": 0, "orb": -1}
        }
        with self.assertRaises(RelationalWorkRequestError):
            prepare_relational_raw_input(payload)


if __name__ == "__main__":
    unittest.main()
