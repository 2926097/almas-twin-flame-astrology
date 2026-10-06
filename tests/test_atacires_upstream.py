"""Regression checks for C-N geometry and civil-time validation, no ephemeris claim."""
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import unittest
from almas_tfa.atacires import engine

ROOT = Path(__file__).resolve().parent / "fixtures" / "atacires"

def request(**changes):
    data = {"schema_version":"1.0", "technique":"UNIFORM_CYCLE",
            "datetime_local":"2000-01-01T00:00:00", "timezone_id":"Etc/UTC",
            "start_utc":"2000-01-01T00:00:00Z", "end_utc":"2002-01-01T00:00:00Z",
            "cycle_years":1, "year_days":360, "natal_points":{"P":0, "S":90},
            "positions_source":"Synthetic geometry fixture", "promissors":["P"],
            "significators":["S"], "aspects_deg":[0], "orb_deg":1}
    data.update(changes)
    return data

class ValidationTests(unittest.TestCase):
    def error(self, data, code):
        with self.assertRaises(engine.InputError) as ctx:
            engine.calculate(data)
        self.assertEqual(ctx.exception.code, code)

    def test_dst_overlap_requires_fold(self):
        self.error(request(datetime_local="2026-10-25T02:30:00", timezone_id="Europe/Madrid"), "AMBIGUOUS_LOCAL_TIME")
    def test_dst_two_occurrences(self):
        first=engine.local_to_utc("2026-10-25T02:30:00", "Europe/Madrid",0)
        second=engine.local_to_utc("2026-10-25T02:30:00", "Europe/Madrid",1)
        self.assertEqual(engine.iso(first),"2026-10-25T00:30:00.000000Z")
        self.assertEqual((second-first).total_seconds(),3600)
    def test_dst_gap(self):
        self.error(request(datetime_local="2026-03-29T02:30:00", timezone_id="Europe/Madrid"), "NONEXISTENT_LOCAL_TIME")
    def test_fold_boolean(self):
        self.error(request(fold=True),"INVALID_FOLD")
    def test_unknown_zone(self):
        self.error(request(timezone_id="Fake/Zone"),"INVALID_TIMEZONE")
    def test_local_with_offset(self):
        self.error(request(datetime_local="2000-01-01T00:00:00Z"),"OFFSET_NOT_ALLOWED")
    def test_date_only_rejected(self):
        self.error(request(start_utc="2000-01-01"),"INVALID_DATETIME")
    def test_interval_offset_required(self):
        self.error(request(start_utc="2000-01-01T00:00:00"),"TIMEZONE_REQUIRED")
    def test_before_birth(self):
        self.error(request(start_utc="1999-01-01T00:00:00Z"),"INVALID_INTERVAL")
    def test_negative_interval(self):
        self.error(request(end_utc="1999-01-01T00:00:00Z"),"INVALID_INTERVAL")
    def test_unsupported(self):
        self.error(request(technique="SOLAR_ARC"),"UNSUPPORTED_TECHNIQUE")
    def test_unknown_field(self):
        self.error(request(house_system="P"),"UNKNOWN_FIELDS")
    def test_cycle_zero(self):
        self.error(request(cycle_years=0),"INVALID_NUMBER")
    def test_nan(self):
        self.error(request(orb_deg=float("nan")),"INVALID_NUMBER")
    def test_numeric_boolean(self):
        self.error(request(cycle_years=True),"INVALID_NUMBER")
    def test_missing_source(self):
        self.error(request(positions_source=""),"POSITIONS_SOURCE_REQUIRED")
    def test_unknown_point(self):
        self.error(request(promissors=["X"]),"INVALID_SELECTION")
    def test_unhashable_point(self):
        self.error(request(promissors=[{}]),"INVALID_SELECTION")
    def test_bad_longitude(self):
        self.error(request(natal_points={"P":360,"S":90}),"INVALID_NUMBER")
    def test_unknown_schema(self):
        self.error(request(schema_version="2.0"),"UNSUPPORTED_SCHEMA")
    def test_event_limit(self):
        self.error(request(cycle_years=.0001),"EVENT_LIMIT_EXCEEDED")
    def test_self_default(self):
        output=engine.calculate(request(natal_points={"P":0},promissors=["P"],significators=["P"]))
        self.assertEqual(output["hits"],[])
    def test_self_opt_in(self):
        hits=engine.calculate(request(natal_points={"P":0},promissors=["P"],significators=["P"],include_self=True))["hits"]
        self.assertEqual(len(hits),3)
    def test_opposition_single_branch(self):
        hits=engine.calculate(request(natal_points={"P":0,"S":0},aspects_deg=[180],end_utc="2001-01-01T00:00:00Z"))["hits"]
        self.assertEqual(len(hits),1)
    def test_quadrature_both_branches(self):
        hits=engine.calculate(request(natal_points={"P":0,"S":0},aspects_deg=[90],end_utc="2001-01-01T00:00:00Z"))["hits"]
        origin=datetime(2000,1,1,tzinfo=timezone.utc)
        self.assertEqual([(engine.utc_datetime(h["date_exact_utc"],"x")-origin).days for h in hits],[90,270])
    def test_multiple_turns(self):
        output=engine.calculate(request())
        self.assertEqual(len(output["hits"]),2)
    def test_zero_orb(self):
        hits=engine.calculate(request(orb_deg=0))["hits"]
        self.assertTrue(all(h["window_start_utc"]==h["window_end_utc"] for h in hits))
    def test_timezone_hash(self):
        out=engine.calculate(request())
        self.assertEqual(len(out["calculation"]["timezone_provenance"]["Etc/UTC"]["tzif_sha256"]),64)
    def test_no_prediction_score(self):
        self.assertIsNone(engine.calculate(request())["quality"]["interpretative_probability"])
    def test_example_17_25_years(self):
        self.assertAlmostEqual(engine.rotate({"P":42.5},17.25,60)["P"],146)
    def test_window_C60(self):
        self.assertAlmostEqual(engine.calculate(request(natal_points={"P":0,"S":1},cycle_years=60,year_days=365.2422))["hits"][0]["window_half_days"],60.8737)
    def test_boundary_event(self):
        data=request(natal_points={"P":0,"S":90},start_utc="2000-03-31T00:00:00Z",end_utc="2000-03-31T00:00:00Z")
        self.assertEqual(len(engine.calculate(data)["hits"]),1)
    def test_cli_reject_duplicate(self):
        result=subprocess.run([sys.executable,"-m", "almas_tfa.atacires.engine"],input='{"schema_version":"1.0","schema_version":"1.0"}',text=True,capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(json.loads(result.stdout)["error"]["code"],"DUPLICATE_JSON_KEY")
    def test_cli_nan(self):
        result=subprocess.run([sys.executable,"-m", "almas_tfa.atacires.engine"],input='{"orb_deg":NaN}',text=True,capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(json.loads(result.stdout)["error"]["code"],"INVALID_JSON_NUMBER")
    def test_cli_success(self):
        result=subprocess.run([sys.executable,"-m", "almas_tfa.atacires.engine"],input=json.dumps(request()),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIsInstance(json.loads(result.stdout)["hits"],list)

class AnalyticReferenceTests(unittest.TestCase):
    pass

cases=json.loads((ROOT/"reference-cases.json").read_text())
for case in cases:
    def check(self,case=copy.deepcopy(case)):
        if case["kind"]=="rotation":
            out=engine.rotate({"P":case["longitude"]},case["age_years"],case["cycle_years"],case["direction"])
            self.assertAlmostEqual(out["P"],case["expected_longitude"],places=8)
        else:
            data=request(natal_points={"P":case["p"],"S":case["s"]},cycle_years=case["cycle_years"],direction=case["direction"],end_utc="2005-01-01T00:00:00Z")
            hit=engine.calculate(data)["hits"][0]
            instant=engine.utc_datetime(hit["date_exact_utc"],"case")
            self.assertAlmostEqual((instant-datetime(2000,1,1,tzinfo=timezone.utc)).total_seconds()/86400,case["expected_first_days"],places=8)
            self.assertLess(hit["angular_residual_deg"],1e-8)
    setattr(AnalyticReferenceTests,"test_"+case["id"],check)

if __name__=="__main__":
    unittest.main(verbosity=2)

