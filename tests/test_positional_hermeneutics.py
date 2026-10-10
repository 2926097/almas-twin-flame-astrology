import unittest

from almas_tfa.positional_hermeneutics import build_position_profile
from almas_tfa.module_contract import ModuleContext
from almas_tfa.relational_handlers import m04_nodes_angles_houses_regencies
from almas_tfa.interpretive_atlas import build_interpretive_atlas
from almas_tfa.interpretive_atlas import resolve_pointer


class TestPositionalHermeneutics(unittest.TestCase):
    def test_m04_publishes_profiles_only_when_maximum_definition_is_enabled(self):
        charts = {
            "A": {
                "timed": True,
                "zodiac": "TROPICAL",
                "positions": {
                    "SUN": {"longitude": 40.0, "point_type": "LUMINARY", "retrograde": False},
                    "VENUS": {"longitude": 220.0, "point_type": "PLANET", "retrograde": True},
                },
                "houses": {str(i): (i - 1) * 30.0 for i in range(1, 13)},
            },
            "B": {"timed": False, "positions": {"MOON": {"longitude": 100.0, "point_type": "LUMINARY"}}},
        }

        def run(raw):
            context = ModuleContext(
                module_id="M04", module_name="M04", mode="FULL", raw_input=raw,
                canonical_snapshot={"natal": {"charts": charts}}, prior_results={},
            )
            return m04_nodes_angles_houses_regencies(context).canonical_updates["natal_context"]

        default_context = run({})
        detailed_context = run({
            "maximum_definition_context": True,
            "rulership_policy": {"TAURUS": ["VENUS"], "SCORPIO": ["MARS"]},
            "decan_rulership_policy": {
                "policy_id": "CHALDEAN_FACES_TEST_V1",
                "rulers_by_sign": {"TAURUS": ["MERCURY", "MOON", "SATURN"]},
            },
        })
        self.assertNotIn("position_profiles", default_context["subjects"]["A"])
        sun = detailed_context["subjects"]["A"]["position_profiles"]["SUN"]
        self.assertEqual(sun["decan"]["number"], 2)
        self.assertEqual(sun["decan"]["rulers"], ["MOON"])
        self.assertEqual(sun["house"], 2)
        self.assertEqual(sun["house_state"], "SYSTEM_UNSPECIFIED")
        self.assertEqual(sun["sign_rulers"]["rulers"], ["VENUS"])
        self.assertEqual(sun["sign_rulers"]["ruler_profile_refs"], [
            "/natal_context/subjects/A/position_profiles/VENUS"
        ])
        self.assertEqual(sun["dispositor_chains"][0]["path"], ["SUN", "VENUS", "MARS"])
        self.assertEqual(sun["motion"]["state"], "DIRECT")

        canonical = {"natal_context": detailed_context}
        atlas = build_interpretive_atlas(canonical)
        self.assertEqual(resolve_pointer(canonical, sun["sign_rulers"]["ruler_profile_refs"][0])["sign"], "SCORPIO")
        entry = next(item for item in atlas["entries"] if item["kind"] == "position_profile")
        self.assertEqual(entry["data_ref"], "/natal_context/subjects/A/position_profiles/SUN")
        self.assertEqual(entry["missing_dimensions"], ["house_system"])
        import json
        from pathlib import Path
        import jsonschema
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "schemas/positional-hermeneutics.schema.json").read_text())
        jsonschema.validate(sun, schema)
        policy_schema = json.loads((root / "schemas/decan-rulership-policy.schema.json").read_text())
        jsonschema.Draft202012Validator.check_schema(policy_schema)
        jsonschema.validate({
            "policy_id": "TEST_FACES_V1",
            "rulers_by_sign": {"TAURUS": ["MERCURY", "MOON", "SATURN"]},
        }, policy_schema)

    def test_derives_sign_house_decan_and_declared_decan_ruler(self):
        profile = build_position_profile(
            point_id="SUN",
            point_type="LUMINARY",
            longitude=40.0,
            house=2,
            positions={"SUN": {"longitude": 40.0}},
            rulership_policy={"TAURUS": ["VENUS"]},
            decan_rulership_policy={
                "policy_id": "TEST_FACES_V1",
                "rulers_by_sign": {"TAURUS": ["MERCURY", "MOON", "SATURN"]},
            },
            retrograde=False,
            speed=0.98,
        )
        self.assertEqual(profile["position"]["sign"], "TAURUS")
        self.assertEqual(profile["position"]["degree_in_sign"], 10.0)
        self.assertEqual(profile["house"], 2)
        self.assertEqual(profile["decan"]["number"], 2)
        self.assertEqual(profile["decan"]["rulers"], ["MOON"])
        self.assertEqual(profile["sign_rulers"]["rulers"], ["VENUS"])
        self.assertEqual(profile["motion"]["state"], "DIRECT")
        self.assertEqual(profile["motion"]["interpretation_state"], "NOT_AUTHORED")

    def test_traces_dispositor_chain_and_stops_at_self_dispositor(self):
        positions = {
            "SUN": {"longitude": 40.0},
            "VENUS": {"longitude": 220.0},
            "MARS": {"longitude": 10.0},
        }
        rulers = {"TAURUS": ["VENUS"], "SCORPIO": ["MARS"], "ARIES": ["MARS"]}
        profile = build_position_profile(
            point_id="SUN", point_type="LUMINARY", longitude=40.0, house=2,
            positions=positions, rulership_policy=rulers,
        )
        self.assertEqual(profile["dispositor_chains"], [{
            "path": ["SUN", "VENUS", "MARS"], "state": "SELF_DISPOSITOR"
        }])

    def test_multiple_rulers_preserve_branches_and_cycles(self):
        positions = {
            "POINT": {"longitude": 40.0},
            "VENUS": {"longitude": 220.0},
            "MARS": {"longitude": 40.0},
        }
        profile = build_position_profile(
            point_id="POINT", point_type="OTHER", longitude=40.0, house=None,
            positions=positions,
            rulership_policy={"TAURUS": ["VENUS", "MARS"], "SCORPIO": ["MARS"]},
        )
        self.assertEqual(profile["dispositor_chains"], [
            {"path": ["POINT", "VENUS", "MARS", "VENUS"], "state": "CYCLE"},
            {"path": ["POINT", "VENUS", "MARS"], "state": "SELF_DISPOSITOR"},
            {"path": ["POINT", "MARS", "VENUS", "MARS"], "state": "CYCLE"},
            {"path": ["POINT", "MARS"], "state": "SELF_DISPOSITOR"},
        ])

    def test_retrograde_applicability_is_type_aware_and_doctrine_neutral(self):
        point = build_position_profile(
            point_id="VESTA", point_type="ASTEROID", longitude=110.0, house=None,
            positions={"VESTA": {"longitude": 110.0}}, retrograde=True, speed=-0.2,
        )
        angle = build_position_profile(
            point_id="ASC", point_type="ANGLE", longitude=110.0, house=None,
            positions={"ASC": {"longitude": 110.0}},
        )
        unknown = build_position_profile(
            point_id="P_X", point_type="OTHER", longitude=110.0, house=None,
            positions={"P_X": {"longitude": 110.0}},
        )
        self.assertEqual(point["motion"]["state"], "RETROGRADE")
        self.assertEqual(point["motion"]["interpretation_state"], "NOT_AUTHORED")
        self.assertEqual(angle["motion"]["state"], "NOT_APPLICABLE")
        self.assertEqual(unknown["motion"]["state"], "NOT_EVALUABLE")
        station = build_position_profile(
            point_id="MERCURY", point_type="PLANET", longitude=15.0, house=None,
            positions={"MERCURY": {"longitude": 15.0}}, retrograde=False, speed=0.0,
        )
        self.assertEqual(station["motion"]["state"], "DIRECT")
        self.assertEqual(station["motion"]["station_state"], "NOT_EVALUATED")

    def test_rejects_conflicting_retrograde_for_angle_and_bad_decan_policy(self):
        with self.assertRaisesRegex(ValueError, "ANGLE no admite retrogradación"):
            build_position_profile(
                point_id="ASC", point_type="ANGLE", longitude=20.0, house=None,
                positions={"ASC": {"longitude": 20.0}}, retrograde=True,
            )
        with self.assertRaisesRegex(ValueError, "tres regentes"):
            build_position_profile(
                point_id="SUN", point_type="LUMINARY", longitude=20.0, house=None,
                positions={"SUN": {"longitude": 20.0}},
                decan_rulership_policy={"policy_id": "BROKEN", "rulers_by_sign": {"ARIES": ["MARS"]}},
            )


if __name__ == "__main__":
    unittest.main()
