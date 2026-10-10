import unittest
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

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
            "birth_date": "2001-02-03",
            "birth_time": "09:30",
            "timezone": "Europe/Paris",
            "place": "Ciudad Sintética A",
            "latitude": 40.0,
            "longitude": -3.0,
            "time_reliability": "D",
            "birth_time_source_class": "DOCUMENTARY",
        },
        {
            "id": "B",
            "display_name": "Caso B",
            "birth_date": "2002-04-05",
            "birth_time": "08:20",
            "timezone": "America/New_York",
            "place": "Ciudad Sintética B",
            "latitude": 10.0,
            "longitude": 20.0,
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
    def test_current_version_and_legacy_optional_extension_inputs_are_accepted(self):
        for version in ("1.25.0", "1.26.0"):
            payload = work_request()
            payload["request"]["public_version"] = version
            self.assertTrue(assess_relational_work_request(payload)["ready_for_raw_input"])

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

    def test_positional_policy_extensions_are_preserved(self):
        payload = work_request()
        payload["request"]["analysis_policies"].update({
            "rulership_policy_id": "HELLENISTIC_WHOLE_SIGN_V1",
            "rulership_policy": {"TAURUS": ["VENUS"]},
            "decan_rulership_policy": {
                "policy_id": "CHALDEAN_FACES_V1",
                "rulers_by_sign": {"TAURUS": ["MERCURY", "MOON", "SATURN"]},
            },
            "maximum_definition_context": True,
        })
        raw = prepare_relational_raw_input(payload)
        self.assertEqual(raw["rulership_policy_id"], "HELLENISTIC_WHOLE_SIGN_V1")
        self.assertEqual(raw["decan_rulership_policy"]["policy_id"], "CHALDEAN_FACES_V1")
        self.assertTrue(raw["maximum_definition_context"])

        schema_dir = Path(__file__).resolve().parents[1] / "schemas"
        registry = Registry()
        for path in schema_dir.glob("*.schema.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            if schema.get("$id"):
                registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
        request_schema = json.loads((schema_dir / "relational-work-request.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(request_schema, registry=registry).validate(payload)

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

    def test_explicit_policy_profile_materializes_required_orbs(self):
        payload = work_request(include_policies=False)
        payload["request"]["analysis_policy_profile"] = (
            "ALMAS_RELATIONAL_STRICT_RESEARCH_V1"
        )

        assessment = assess_relational_work_request(payload)
        self.assertTrue(assessment["ready_for_raw_input"])
        self.assertEqual(
            assessment["policy_source"],
            "EXPLICIT_PRESET",
        )

        raw = prepare_relational_raw_input(payload)
        self.assertEqual(raw["aspect_policy"]["CONJUNCTION"]["orb"], 3.5)
        self.assertEqual(
            raw["declination_policy"]["parallel_orb"],
            1.0,
        )
        self.assertEqual(
            raw["draconic_aspect_policy"]["CONJUNCTION"]["orb"],
            3.0,
        )
        self.assertEqual(
            raw["request_adapter_trace"]["analysis_policy_profile"],
            "ALMAS_RELATIONAL_STRICT_RESEARCH_V1",
        )
        self.assertFalse(
            raw["request_adapter_trace"]["implicit_orbs_used"]
        )
        self.assertEqual(
            len(raw["request_adapter_trace"]["analysis_policy_fingerprint"]),
            64,
        )

    def test_policy_profile_rejects_inline_orb_overrides(self):
        payload = work_request()
        payload["request"]["analysis_policy_profile"] = (
            "ALMAS_RELATIONAL_STRICT_RESEARCH_V1"
        )
        with self.assertRaisesRegex(
            RelationalWorkRequestError,
            "No se puede combinar",
        ):
            prepare_relational_raw_input(payload)

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

    def test_maximum_definition_context_requires_a_boolean(self):
        for value in ("true", 0, 1, None, [], {}):
            payload = work_request()
            payload["request"]["analysis_policies"]["maximum_definition_context"] = value
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    RelationalWorkRequestError,
                    "maximum_definition_context debe ser booleano",
                ):
                    prepare_relational_raw_input(payload)



if __name__ == "__main__":
    unittest.main()
