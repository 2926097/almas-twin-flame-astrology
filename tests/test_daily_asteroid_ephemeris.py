"""Offline regression checks for the ALMAS public-asteroid ephemeris builder."""
import importlib.util
from datetime import date
from pathlib import Path
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

    def test_motion_and_longitude(self):
        with mock.patch.object(m.swe, "calc_ut", return_value=((354.123, 1, 2, -0.23, 0, 0), m.swe.FLG_SWIEPH)):
            result = m.position(2847, date(2026, 10, 29))
            self.assertEqual(result["motion"], "R")
            self.assertAlmostEqual(result["longitude_deg"], 354.123)


if __name__ == "__main__":
    main()
