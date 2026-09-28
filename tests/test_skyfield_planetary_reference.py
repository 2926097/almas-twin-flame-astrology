from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from almas_tfa.skyfield_planetary_reference import (
    EARTH_NAIF_ID,
    REFERENCE_METHOD_ID,
    TARGET_NAIF_IDS,
    SkyfieldPlanetaryReference,
    SkyfieldReferenceConfig,
)


class Angle:
    def __init__(self, degrees):
        self.degrees = degrees


class FakeApparent:
    def __init__(self, value):
        self.value = float(value)

    def frame_latlon(self, frame):
        if frame == "ECLIPTIC":
            return Angle(self.value / 10.0), Angle(self.value), None
        if frame == "EQUATORIAL":
            return Angle(self.value / 20.0), Angle(0.0), None
        raise AssertionError(frame)


class FakeAstrometric:
    def __init__(self, value):
        self.value = value

    def apparent(self):
        return FakeApparent(self.value)


class FakeObserver:
    def observe(self, target):
        return FakeAstrometric(target)


class FakeEarth:
    def at(self, time):
        if time != 2451545.25:
            raise AssertionError(time)
        return FakeObserver()


class FakeTimescale:
    def tt_jd(self, value):
        return float(value)


class SkyfieldPlanetaryReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = Path(self.tmp.name) / "de440s.bsp"
        self.kernel.write_bytes(b"synthetic-de440s")
        self.kernel_sha = sha256(self.kernel.read_bytes()).hexdigest()

    def reference(self):
        ephemeris = {EARTH_NAIF_ID: FakeEarth()}
        for index, target_id in enumerate(TARGET_NAIF_IDS.values(), start=1):
            ephemeris[target_id] = float(index * 20)
        return SkyfieldPlanetaryReference(
            SkyfieldReferenceConfig(
                kernel_path=str(self.kernel),
                kernel_sha256=self.kernel_sha,
            ),
            ephemeris=ephemeris,
            timescale=FakeTimescale(),
            ecliptic_frame="ECLIPTIC",
            equatorial_frame="EQUATORIAL",
            provider_version="1.55",
        )

    def test_target_identity_matches_moira_routes(self):
        self.assertEqual(TARGET_NAIF_IDS["SUN"], 10)
        self.assertEqual(TARGET_NAIF_IDS["MOON"], 301)
        self.assertEqual(TARGET_NAIF_IDS["MERCURY"], 199)
        self.assertEqual(TARGET_NAIF_IDS["VENUS"], 299)
        self.assertEqual(TARGET_NAIF_IDS["MARS"], 4)
        self.assertEqual(TARGET_NAIF_IDS["JUPITER"], 5)
        self.assertEqual(TARGET_NAIF_IDS["PLUTO"], 9)

    def test_reference_uses_common_tt_epoch_and_all_targets(self):
        reference = self.reference()
        positions = reference.calculate_at_tt_jd(2451545.25)
        self.assertEqual(set(positions), set(TARGET_NAIF_IDS))
        self.assertEqual(positions["SUN"]["longitude"], 20.0)
        self.assertEqual(positions["SUN"]["latitude"], 2.0)
        self.assertEqual(positions["SUN"]["declination"], 1.0)

    def test_provenance_is_explicit_and_offline(self):
        provenance = self.reference().provenance
        self.assertEqual(provenance["method_id"], REFERENCE_METHOD_ID)
        self.assertEqual(provenance["software_version"], "1.55")
        self.assertEqual(provenance["ephemeris_family"], "DE440")
        self.assertEqual(provenance["kernel_sha256"], self.kernel_sha)
        self.assertFalse(provenance["network_io_used"])

    def test_kernel_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "KERNEL_SHA256_MISMATCH"):
            SkyfieldPlanetaryReference(
                SkyfieldReferenceConfig(
                    kernel_path=str(self.kernel),
                    kernel_sha256="0" * 64,
                ),
                ephemeris={},
                timescale=FakeTimescale(),
                ecliptic_frame="ECLIPTIC",
                equatorial_frame="EQUATORIAL",
                provider_version="1.55",
            )


if __name__ == "__main__":
    unittest.main()
