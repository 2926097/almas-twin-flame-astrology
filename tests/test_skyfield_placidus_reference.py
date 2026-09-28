from __future__ import annotations

from math import cos, radians, sin
import unittest

from almas_tfa.skyfield_placidus_reference import (
    REFERENCE_METHOD_ID,
    SkyfieldPlacidusReference,
    placidus_from_armc,
    true_obliquity_from_frames_deg,
)


def rotation_x_for_relative_frame(epsilon_deg):
    eps = radians(epsilon_deg)
    return (
        (1.0, 0.0, 0.0),
        (0.0, cos(eps), sin(eps)),
        (0.0, -sin(eps), cos(eps)),
    )


IDENTITY = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)


class FakeFrame:
    def __init__(self, matrix):
        self.matrix = matrix

    def rotation_at(self, time):
        return self.matrix


class FakeTime:
    def __init__(self, jd_ut, delta_t):
        self.ut1 = float(jd_ut)
        self.tt = float(jd_ut) + float(delta_t) / 86400.0
        self.gast = 4.0


class FakeTimescale:
    def __init__(self, delta_t):
        self.delta_t = float(delta_t)

    def ut1_jd(self, jd_ut):
        return FakeTime(jd_ut, self.delta_t)


class SkyfieldPlacidusReferenceTests(unittest.TestCase):
    def test_true_obliquity_is_recovered_from_relative_frames(self):
        epsilon = true_obliquity_from_frames_deg(
            IDENTITY,
            rotation_x_for_relative_frame(23.44),
        )
        self.assertAlmostEqual(epsilon, 23.44, places=10)

    def test_equator_has_exact_opposite_cusps(self):
        result = placidus_from_armc(0.0, 0.0, 23.44)
        houses = result["houses"]
        self.assertAlmostEqual(result["angles"]["ASC"], 90.0)
        self.assertAlmostEqual(result["angles"]["MC"], 0.0)
        for a, b in ((1, 7), (2, 8), (3, 9), (4, 10), (5, 11), (6, 12)):
            self.assertAlmostEqual(
                (houses[f"H{b}"] - houses[f"H{a}"]) % 360.0,
                180.0,
                places=9,
            )

    def test_polar_placidus_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "círculo polar"):
            placidus_from_armc(0.0, 70.0, 23.44)

    def test_reference_uses_gast_longitude_and_backend_delta_t(self):
        def factory(delta_t):
            return FakeTimescale(delta_t)

        reference = SkyfieldPlacidusReference(
            provider_version="1.55",
            timescale_factory=factory,
            equatorial_frame=FakeFrame(IDENTITY),
            ecliptic_frame=FakeFrame(rotation_x_for_relative_frame(23.44)),
        )
        result = reference.calculate(
            jd_ut=2451545.0,
            delta_t_seconds=64.0,
            latitude=0.0,
            longitude=15.0,
        )
        self.assertAlmostEqual(result["armc"], 75.0)
        self.assertAlmostEqual(
            result["jd_tt"],
            2451545.0 + 64.0 / 86400.0,
        )
        self.assertEqual(reference.provenance["method_id"], REFERENCE_METHOD_ID)
        self.assertFalse(reference.provenance["network_io_used"])


if __name__ == "__main__":
    unittest.main()
