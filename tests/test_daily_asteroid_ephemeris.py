"""Offline regression checks for the ALMAS public-asteroid ephemeris builder."""
import importlib.util
from datetime import date
from pathlib import Path
import socket
from urllib.error import URLError
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock

path = Path(__file__).resolve().parents[1] / "tools/daily_asteroid_ephemeris.py"
spec = importlib.util.spec_from_file_location("daily_asteroids", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestAsteroids(TestCase):
    def test_numbered_file_paths(self):
        self.assertEqual(m.asteroid_file(2847), "ast2/se02847s.se1")
        self.assertEqual(m.asteroid_file(4227), "ast4/se04227s.se1")
        self.assertEqual(m.asteroid_file(16), "ast0/se00016s.se1")

    def test_09_utc_reference(self):
        jd = m.swe.julday(2026, 10, 29, 9.0, m.swe.GREG_CAL)
        self.assertAlmostEqual(m.swe.revjul(jd)[3], 9.0)

    def test_reject_silent_moshier_fallback(self):
        with mock.patch.object(m.swe, "calc_ut", return_value=((30, 0, 1, 0.1, 0, 0), m.swe.FLG_MOSEPH)):
            with self.assertRaisesRegex(RuntimeError, "Swiss calculation unavailable"):
                m.position(2847, date(2026, 10, 29))

    def test_chiron_uses_dedicated_body_and_rejects_fallback(self):
        with mock.patch.object(m.swe, "calc_ut", return_value=((15, 0, 10, -0.01, 0, 0), m.swe.FLG_SWIEPH)) as calc:
            result = m.chiron_position(date(2026, 10, 30))
            self.assertEqual(calc.call_args.args[1], m.swe.CHIRON)
            self.assertEqual(result["motion"], "R")
        with mock.patch.object(m.swe, "calc_ut", return_value=((15, 0, 10, -0.01, 0, 0), m.swe.FLG_MOSEPH)):
            with self.assertRaisesRegex(RuntimeError, "Chiron 2060: Swiss calculation unavailable"):
                m.chiron_position(date(2026, 10, 30))

    def test_chiron_is_mandatory_for_publication(self):
        valid = {"longitude_deg": 15.0, "latitude_deg": 0, "distance_au": 10,
                 "speed_deg_per_day": -0.01, "motion": "R", "flags_requested": 258,
                 "flags_returned": m.swe.FLG_SWIEPH}
        with (
            mock.patch.object(m, "obtain", return_value={"path": "mock", "source": "local_cache", "sha256": "mock"}),
            mock.patch.object(m, "position", return_value=valid),
            mock.patch.object(m, "chiron_position", side_effect=RuntimeError("Swiss missing")),
        ):
            with self.assertRaisesRegex(RuntimeError, "chiron_2060"):
                m.calculate(date(2026, 10, 30), Path("/tmp/unused"))

    def test_planets_are_required_and_moshier_rejected(self):
        with mock.patch.object(m.swe, "calc_ut", return_value=((28.5, 0, 2, -0.03, 0, 0), m.swe.FLG_SWIEPH)) as calc:
            result = m.planet_position("true_node", date(2026, 10, 31))
            self.assertEqual(calc.call_args.args[1], m.swe.TRUE_NODE)
            self.assertEqual(result["motion"], "R")
        with mock.patch.object(m.swe, "calc_ut", return_value=((28.5, 0, 2, -0.03, 0, 0), m.swe.FLG_MOSEPH)):
            with self.assertRaisesRegex(RuntimeError, "Swiss calculation unavailable"):
                m.planet_position("moon", date(2026, 10, 31))

    def test_network_dns_classification(self):
        error = URLError(socket.gaierror(-3, "Temporary failure in name resolution"))
        self.assertEqual(m._network_error(error), "DNS_RESOLUTION")

    def test_cache_avoids_network(self):
        with TemporaryDirectory() as folder:
            cache = Path(folder)
            target = cache / m.asteroid_file(2847)
            target.parent.mkdir(parents=True)
            target.write_bytes(b"SWISSEPH" + b"X" * 2048)
            with mock.patch.object(m, "urlopen", side_effect=AssertionError("network must not be used")):
                result = m.obtain(m.asteroid_file(2847), cache)
            self.assertEqual(result["source"], "local_cache")

    def test_complete_publication_contains_planets_chiron_and_priority(self):
        record = {"longitude_deg": 15.0, "latitude_deg": 0, "distance_au": 10,
                  "speed_deg_per_day": -0.01, "motion": "R", "flags_requested": 258,
                  "flags_returned": m.swe.FLG_SWIEPH | m.swe.FLG_SPEED}
        with (
            mock.patch.object(m, "obtain", return_value={"path": "mock", "source": "local_cache", "sha256": "mock"}),
            mock.patch.object(m, "position", return_value=record),
            mock.patch.object(m, "chiron_position", return_value=record),
            mock.patch.object(m, "planet_position", return_value=record),
        ):
            result = m.calculate(date(2026, 10, 31), Path("/tmp/unused"))
        self.assertEqual(result["schema_version"], "1.2")
        self.assertEqual(result["checked_days"], ["2026-10-30", "2026-10-31"])
        self.assertTrue(result["verified_complete"])
        self.assertEqual(len(result["planets"]), len(m.PLANETS))
        self.assertEqual(len(result["asteroids"]), len(m.ASTEROIDS))
        self.assertEqual(result["chiron"]["number"], 2060)
        self.assertTrue(all(str(n) in result["asteroids"] for n in m.PRIORITY))

    def test_optional_download_failure_does_not_block_priority_publication(self):
        record = {"longitude_deg": 15.0, "latitude_deg": 0, "distance_au": 10,
                  "speed_deg_per_day": -0.01, "motion": "R", "flags_requested": 258,
                  "flags_returned": m.swe.FLG_SWIEPH | m.swe.FLG_SPEED}
        def file_or_fail(name, cache):
            if name == m.asteroid_file(6583):
                raise RuntimeError("HTTP_404 optional")
            return {"path": name, "source": "local_cache", "sha256": "mock"}
        with (
            mock.patch.object(m, "obtain", side_effect=file_or_fail),
            mock.patch.object(m, "position", return_value=record),
            mock.patch.object(m, "chiron_position", return_value=record),
            mock.patch.object(m, "planet_position", return_value=record),
        ):
            result = m.calculate(date(2026, 10, 31), Path("/tmp/unused"))
        self.assertTrue(result["verified_complete"])
        self.assertEqual(len(result["asteroids"]), len(m.ASTEROIDS) - 1)
        self.assertIn(m.asteroid_file(6583), result["optional_missing"])

    def test_motion_and_longitude(self):
        with mock.patch.object(m.swe, "calc_ut", return_value=((354.123, 1, 2, -0.23, 0, 0), m.swe.FLG_SWIEPH)):
            result = m.position(2847, date(2026, 10, 29))
            self.assertEqual(result["motion"], "R")
            self.assertAlmostEqual(result["longitude_deg"], 354.123)


if __name__ == "__main__":
    main()
