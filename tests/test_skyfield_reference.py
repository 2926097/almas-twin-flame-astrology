from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from almas_tfa.skyfield_reference import (
    TARGET_CANDIDATES,
    file_sha256,
    parse_utc_case,
)


class SkyfieldReferenceContractTests(unittest.TestCase):
    def test_target_roster_is_exactly_ten_planetary_points(self):
        self.assertEqual(
            set(TARGET_CANDIDATES),
            {
                "SUN", "MOON", "MERCURY", "VENUS", "MARS",
                "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO",
            },
        )

    def test_hash_is_deterministic(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "de440.bsp"
            payload = b"synthetic-reference-kernel"
            path.write_bytes(payload)
            self.assertEqual(file_sha256(path), sha256(payload).hexdigest())

    def test_case_must_be_explicit_utc(self):
        case = {
            "case_id": "G",
            "birth_date": "2000-01-01",
            "birth_time": "12:00:00",
            "timezone": "UTC",
        }
        instant = parse_utc_case(case)
        self.assertEqual(instant.isoformat(), "2000-01-01T12:00:00+00:00")

        bad = dict(case)
        bad["timezone"] = "Europe/Madrid"
        with self.assertRaisesRegex(ValueError, "UTC"):
            parse_utc_case(bad)


if __name__ == "__main__":
    unittest.main()
