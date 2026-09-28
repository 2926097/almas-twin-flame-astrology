from __future__ import annotations

from contextlib import nullcontext
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest

from almas_tfa.astrology_backend import (
    AstronomyBackendNotEvaluableError,
    NatalRequest,
)
from almas_tfa.production_astronomy import (
    MoiraBackendConfig,
    MoiraProductionBackend,
    _canon_fingerprint,
)


def request(
    *,
    birth_time="12:00",
    latitude=41.65,
    longitude=-0.88,
):
    return NatalRequest(
        subject_id="SYNTHETIC",
        birth_date="2000-01-01",
        birth_time=birth_time,
        timezone="UTC",
        place=None,
        latitude=latitude,
        longitude=longitude,
        time_reliability="A",
    )


class FakeStarParanFacade:
    _reader = "FAKE_READER"

    def fixed_star(self, name, instant):
        return SimpleNamespace(
            name=name,
            nomenclature=f"{name}-NOM",
            longitude=123.0 if name == "Regulus" else 45.0,
            latitude=0.5,
            magnitude=1.2,
            source="SYNTHETIC",
            is_topocentric=False,
            computation_truth=SimpleNamespace(
                method="synthetic",
                epoch="of-date",
            ),
        )


class FakeParanApi:
    def __init__(
        self,
        *,
        reverse_canon=False,
        invalid_family=False,
    ):
        entries = [
            SimpleNamespace(
                name="Regulus",
                tiers=(
                    SimpleNamespace(value="working_canon"),
                    SimpleNamespace(value="royal"),
                    SimpleNamespace(value="ptolemaic"),
                ),
                default_enabled=True,
            ),
            SimpleNamespace(
                name="Spica",
                tiers=(
                    SimpleNamespace(value="working_canon"),
                    SimpleNamespace(value="behenian"),
                    SimpleNamespace(value="ptolemaic"),
                ),
                default_enabled=True,
            ),
        ]
        self.entries = list(reversed(entries)) if reverse_canon else entries
        self.invalid_family = invalid_family
        self.preset_requested = None
        self.find_call = None
        self.contact_call = None

    def list_paran_stars(self, *, tiers=None, available_only=True):
        self.list_call = {
            "tiers": tiers,
            "available_only": available_only,
        }
        return tuple(self.entries)

    def jd_from_datetime(self, instant):
        return 2451545.25

    def utc_to_ut1(self, jd):
        return float(jd) + 0.0001

    def paran_policy_preset(self, preset):
        self.preset_requested = preset
        return {"preset": preset}

    def find_parans(
        self,
        bodies,
        jd_day,
        lat,
        lon,
        *,
        orb_minutes,
        policy,
    ):
        self.find_call = {
            "bodies": list(bodies),
            "jd_day": jd_day,
            "lat": lat,
            "lon": lon,
            "orb_minutes": orb_minutes,
            "policy": policy,
        }
        return [
            SimpleNamespace(
                body1="Sun",
                body2="Regulus",
                circle1="Culminating",
                circle2="Rising",
                jd1=2451544.7,
                jd2=2451544.701,
                orb_min=1.44,
                signature=SimpleNamespace(
                    event_family="mc-rise",
                    axis_family="horizon-meridian",
                    body_family=(
                        "star-star"
                        if self.invalid_family
                        else "planet-star"
                    ),
                ),
            )
        ]

    def natal_angular_contacts(
        self,
        bodies,
        natal_jd,
        lat,
        lon,
        *,
        orb_minutes,
    ):
        self.contact_call = {
            "bodies": list(bodies),
            "natal_jd": natal_jd,
            "lat": lat,
            "lon": lon,
            "orb_minutes": orb_minutes,
        }
        return [
            SimpleNamespace(
                body="Spica",
                body_family="star",
                circle="Rising",
                crossing_jd=natal_jd + 1.0 / 1440.0,
                natal_jd=natal_jd,
                delta_minutes=1.0,
                absolute_delta_minutes=1.0,
            )
        ]

    def mapping(self):
        return {
            "find_parans": self.find_parans,
            "jd_from_datetime": self.jd_from_datetime,
            "list_paran_stars": self.list_paran_stars,
            "natal_angular_contacts": self.natal_angular_contacts,
            "paran_policy_preset": self.paran_policy_preset,
            "utc_to_ut1": self.utc_to_ut1,
        }


class FixedStarParanBackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = Path(self.tmp.name) / "de440.bsp"
        self.kernel.write_bytes(b"synthetic-kernel")
        self.kernel_sha = sha256(self.kernel.read_bytes()).hexdigest()

    def backend(self, api=None):
        api = api or FakeParanApi()
        backend = MoiraProductionBackend(
            MoiraBackendConfig(
                kernel_path=str(self.kernel),
                kernel_sha256=self.kernel_sha,
                kernel_family="DE440",
                house_system="PLACIDUS",
            ),
            facade=FakeStarParanFacade(),
            house_system_token="PLACIDUS",
            provider_version="6.8.2",
            paran_api=api.mapping(),
            reader_override_factory=lambda reader: nullcontext(),
        )
        return backend, api

    def test_calculation_is_support_only_and_uses_explicit_policy(self):
        backend, api = self.backend()
        result = backend.calculate_fixed_star_parans(request())

        self.assertEqual(result["structural_role"], "SUPPORT_ONLY")
        self.assertEqual(
            result["policy_id"],
            "ALMAS_FIXED_STAR_PARAN_POLICY_V1",
        )
        self.assertEqual(api.preset_requested, "star_planet_only")
        self.assertEqual(api.find_call["orb_minutes"], 4.0)
        self.assertEqual(api.contact_call["orb_minutes"], 2.0)
        self.assertEqual(
            api.list_call,
            {"tiers": None, "available_only": True},
        )
        self.assertIn("Sun", api.find_call["bodies"])
        self.assertIn("Regulus", api.find_call["bodies"])
        self.assertEqual(
            api.contact_call["bodies"],
            ["Regulus", "Spica"],
        )
        self.assertEqual(len(result["fixed_stars"]), 2)
        self.assertEqual(len(result["parans"]), 1)
        self.assertEqual(len(result["natal_angular_contacts"]), 1)
        self.assertEqual(
            result["parans"][0]["signature"]["body_family"],
            "planet-star",
        )
        self.assertFalse(result["metadata"]["network_io_used"])
        self.assertFalse(result["metadata"]["geocoding_used"])

    def test_canon_fingerprint_is_order_independent(self):
        first = [
            {
                "name": "Regulus",
                "tiers": ["royal", "working_canon"],
                "default_enabled": True,
            },
            {
                "name": "Spica",
                "tiers": ["behenian", "working_canon"],
                "default_enabled": True,
            },
        ]
        second = [
            {
                "name": "Spica",
                "tiers": ["working_canon", "behenian"],
                "default_enabled": True,
            },
            {
                "name": "Regulus",
                "tiers": ["working_canon", "royal"],
                "default_enabled": True,
            },
        ]
        self.assertEqual(
            _canon_fingerprint(first),
            _canon_fingerprint(second),
        )

    def test_provider_policy_leak_fails_closed(self):
        backend, _ = self.backend(FakeParanApi(invalid_family=True))
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "fuera de contrato",
        ):
            backend.calculate_fixed_star_parans(request())

    def test_missing_time_or_coordinates_fail_closed(self):
        backend, _ = self.backend()
        with self.assertRaises(AstronomyBackendNotEvaluableError):
            backend.calculate_fixed_star_parans(
                request(birth_time=None)
            )
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "coordenadas numéricas",
        ):
            backend.calculate_fixed_star_parans(
                request(latitude=None, longitude=None)
            )

    def test_missing_provider_surface_fails_closed(self):
        backend = MoiraProductionBackend(
            MoiraBackendConfig(
                kernel_path=str(self.kernel),
                kernel_sha256=self.kernel_sha,
                kernel_family="DE440",
                house_system="PLACIDUS",
            ),
            facade=FakeStarParanFacade(),
            house_system_token="PLACIDUS",
            provider_version="6.8.2",
        )
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "Superficie Moira",
        ):
            backend.calculate_fixed_star_parans(request())


if __name__ == "__main__":
    unittest.main()
