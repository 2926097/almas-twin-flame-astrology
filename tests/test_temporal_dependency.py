"""Paso 16: separar técnicas relacionadas sin doble conteo."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from almas_tfa.temporal_dependency import summarize_temporal_dependencies

ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads((ROOT/"reference/temporal-dependency-policy.json").read_text())
SCHEMA=json.loads((ROOT/"schemas/temporal-dependency-result.schema.json").read_text())

class TemporalDependencyTests(unittest.TestCase):
    def test_c360_and_solar_arc_remain_distinct_but_share_one_dependency_unit(self):
        result=summarize_temporal_dependencies([
            {"signal_id":"C360-1","root_id":"ROOT_SOL_PLUTO","temporal_family":"TATACIR","technique":"C360"},
            {"signal_id":"SA-1","root_id":"ROOT_SOL_PLUTO","temporal_family":"TDIR","technique":"SOLAR_ARC"},
        ])
        Draft202012Validator(SCHEMA).validate(result)
        self.assertEqual(len(result["signals"]),2)
        self.assertEqual(len(result["dependency_units"]),1)
        self.assertEqual(result["dependency_units"][0]["techniques"],["C360","SOLAR_ARC"])
        self.assertEqual(result["dependency_units"][0]["independent_unit_count"],1)
        self.assertFalse(result["score_created"])
        self.assertFalse(result["legacy_iat_modified"])

    def test_distinct_roots_produce_distinct_units(self):
        result=summarize_temporal_dependencies([
            {"signal_id":"C1","root_id":"ROOT_A","temporal_family":"TATACIR"},
            {"signal_id":"S1","root_id":"ROOT_B","temporal_family":"TDIR"}])
        self.assertEqual(len(result["dependency_units"]),2)

    def test_unanchored_signals_do_not_create_shared_recurrence(self):
        result=summarize_temporal_dependencies([
            {"signal_id":"C1","root_id":None,"temporal_family":"TATACIR"},
            {"signal_id":"S1","root_id":None,"temporal_family":"TDIR"}])
        self.assertEqual(len(result["dependency_units"]),2)

    def test_duplicate_ids_and_invalid_families_fail_closed(self):
        with self.assertRaises(ValueError):
            summarize_temporal_dependencies([{"signal_id":"X","temporal_family":"TDIR"},{"signal_id":"X","temporal_family":"TATACIR"}])
        with self.assertRaises(ValueError):
            summarize_temporal_dependencies([{"signal_id":"X","temporal_family":""}])

if __name__=="__main__":
    unittest.main()
