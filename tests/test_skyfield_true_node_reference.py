from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from almas_tfa.skyfield_true_node_reference import (
    EARTH_NAIF_ID,
    MOON_NAIF_ID,
    REFERENCE_METHOD_ID,
    SkyfieldTrueNodeReference,
    SkyfieldTrueNodeReferenceConfig,
    ascending_node_longitude_from_state,
)


IDENTITY = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)


class FakeBody:
    def __init__(self, position, velocity):
        self._position = position
        self._velocity = velocity

    def at(self, time):
        return FakePosition(self._position, self._velocity, time)


class FakePosition:
    def __init__(self, position, velocity, time):
        self.xyz = SimpleNamespace(au=position)
        self.velocity = SimpleNamespace(au_per_d=velocity)
        self.t = time

    def __sub__(self, other):
        return FakePosition(
            tuple(a - b for a, b in zip(self.xyz.au, other.xyz.au)),
            tuple(
                a - b
                for a, b in zip(
                    self.velocity.au_per_d,
                    other.velocity.au_per_d,
                )
            ),
            self.t,
        )


class FakeTimescale:
    def tt_jd(self, value):
        return float(value)


class FakeFrame:
    def rotation_at(self, time):
        if time != 2451545.25:
            raise AssertionError(time)
        return IDENTITY


class SkyfieldTrueNodeReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = Path(self.tmp.name) / "de440s.bsp"
        self.kernel.write_bytes(b"synthetic-de440s-node")
        self.kernel_sha = sha256(self.kernel.read_bytes()).hexdigest()

    def test_first_principles_node_orientation(self):
        # r=(1,0,0), v=(0,0,1) -> h=(0,-1,0), n=(1,0,0) => 0 deg.
        longitude = ascending_node_longitude_from_state(
            (1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            IDENTITY,
        )
        self.assertAlmostEqual(longitude, 0.0)

    def test_quarter_turn_node_orientation(self):
        # r=(0,1,0), v=(0,0,1) -> h=(1,0,0), n=(0,1,0) => 90 deg.
        longitude = ascending_node_longitude_from_state(
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            IDENTITY,
        )
        self.assertAlmostEqual(longitude, 90.0)

    def test_reference_uses_simultaneous_moon_minus_earth_state(self):
        ephemeris = {
            MOON_NAIF_ID: FakeBody((2.0, 0.0, 0.0), (0.0, 0.0, 2.0)),
            EARTH_NAIF_ID: FakeBody((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
        }
        reference = SkyfieldTrueNodeReference(
            SkyfieldTrueNodeReferenceConfig(
                kernel_path=str(self.kernel),
                kernel_sha256=self.kernel_sha,
            ),
            ephemeris=ephemeris,
            timescale=FakeTimescale(),
            ecliptic_frame=FakeFrame(),
            provider_version="1.55",
        )
        self.assertAlmostEqual(reference.calculate_at_tt_jd(2451545.25), 0.0)

    def test_provenance_is_explicit(self):
        ephemeris = {
            MOON_NAIF_ID: FakeBody((2.0, 0.0, 0.0), (0.0, 0.0, 2.0)),
            EARTH_NAIF_ID: FakeBody((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
        }
        reference = SkyfieldTrueNodeReference(
            SkyfieldTrueNodeReferenceConfig(
                kernel_path=str(self.kernel),
                kernel_sha256=self.kernel_sha,
            ),
            ephemeris=ephemeris,
            timescale=FakeTimescale(),
            ecliptic_frame=FakeFrame(),
            provider_version="1.55",
        )
        provenance = reference.provenance
        self.assertEqual(provenance["method_id"], REFERENCE_METHOD_ID)
        self.assertEqual(provenance["software_version"], "1.55")
        self.assertFalse(provenance["network_io_used"])


if __name__ == "__main__":
    unittest.main()
