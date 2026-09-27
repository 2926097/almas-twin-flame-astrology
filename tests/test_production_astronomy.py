from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest

from almas_tfa.astrology_backend import (
    AstronomyBackendNotEvaluableError,
    NatalRequest,
)
from almas_tfa.astrology_handlers import make_m02_natal
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.production_astronomy import (
    MoiraBackendConfig,
    MoiraProductionBackend,
    load_production_astronomy_backend_policy,
)
from almas_tfa.relationship_chart_handlers import (
    DavisonRequest,
    make_m08_davison,
)


PLANET_LONGITUDES = {
    "Sun": 10.0,
    "Moon": 25.0,
    "Mercury": 40.0,
    "Venus": 55.0,
    "Mars": 70.0,
    "Jupiter": 85.0,
    "Saturn": 100.0,
    "Uranus": 115.0,
    "Neptune": 130.0,
    "Pluto": 145.0,
}


class FakeFacade:
    def __init__(self, *, fallback=False, effective_system="PLACIDUS"):
        self.fallback = fallback
        self.effective_system = effective_system
        self.chart_calls = []
        self.house_calls = []

    def chart(self, instant, **kwargs):
        self.chart_calls.append((instant, kwargs))
        planets = {
            name: SimpleNamespace(
                longitude=longitude,
                latitude=1.0,
                speed=-0.2 if name == "Mercury" else 0.5,
                retrograde=name == "Mercury",
            )
            for name, longitude in PLANET_LONGITUDES.items()
        }
        return SimpleNamespace(
            planets=planets,
            nodes={
                "True Node": SimpleNamespace(
                    longitude=200.0,
                    speed=-0.05,
                )
            },
            obliquity=23.44,
        )

    def houses(self, instant, **kwargs):
        self.house_calls.append((instant, kwargs))
        return SimpleNamespace(
            cusps=[float(i * 30) % 360.0 for i in range(12)],
            asc=12.0,
            mc=102.0,
            fallback=self.fallback,
            effective_system=self.effective_system,
        )


def request(
    subject_id="A",
    *,
    birth_date="1977-03-20",
    birth_time="17:37",
    timezone="Europe/Madrid",
    latitude=41.65,
    longitude=-0.88,
):
    return NatalRequest(
        subject_id=subject_id,
        birth_date=birth_date,
        birth_time=birth_time,
        timezone=timezone,
        place=None,
        latitude=latitude,
        longitude=longitude,
        time_reliability="A",
    )


class ProductionAstronomyBackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        kernel = Path(self.tmp.name) / "de440.bsp"
        kernel.write_bytes(b"synthetic-kernel-for-contract-tests")
        self.kernel = kernel
        self.kernel_sha = sha256(kernel.read_bytes()).hexdigest()

    def backend(self, facade=None, **kwargs):
        config = MoiraBackendConfig(
            kernel_path=str(self.kernel),
            kernel_sha256=self.kernel_sha,
            kernel_family="DE440",
            house_system="PLACIDUS",
        )
        return MoiraProductionBackend(
            config,
            facade=facade or FakeFacade(),
            house_system_token="PLACIDUS",
            provider_version="6.8.2",
            **kwargs,
        )

    def test_policy_pins_provider_and_forbids_hidden_io(self):
        policy = load_production_astronomy_backend_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1",
        )
        self.assertEqual(policy["provider"]["pinned_version"], "6.8.2")
        self.assertEqual(policy["provider"]["license"], "MIT")
        self.assertFalse(
            policy["kernel"]["network_download_during_calculation"]
        )
        self.assertFalse(policy["location"]["hidden_geocoding"])
        self.assertEqual(policy["time"]["ambiguous_local_time"], "FAIL_CLOSED")

    def test_kernel_fingerprint_mismatch_fails_before_runtime(self):
        config = MoiraBackendConfig(
            kernel_path=str(self.kernel),
            kernel_sha256="0" * 64,
            kernel_family="DE440",
            house_system="PLACIDUS",
        )
        with self.assertRaisesRegex(ValueError, "KERNEL_SHA256_MISMATCH"):
            MoiraProductionBackend(
                config,
                facade=FakeFacade(),
                house_system_token="PLACIDUS",
                provider_version="6.8.2",
            )

    def test_natal_maps_planets_nodes_houses_and_provenance(self):
        backend = self.backend()
        chart = backend.calculate_natal(request())
        self.assertEqual(chart["backend_id"], "MOIRA_JPL_SPK")
        self.assertEqual(chart["backend_version"], "6.8.2")
        self.assertEqual(chart["zodiac"], "TROPICAL")
        self.assertEqual(set(PLANET_LONGITUDES), {
            "Sun", "Moon", "Mercury", "Venus", "Mars",
            "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
        })
        self.assertEqual(len(chart["houses"]), 12)
        self.assertEqual(set(chart["angles"]), {"ASC", "DSC", "MC", "IC"})
        self.assertIn("NORTH_NODE", chart["positions"])
        self.assertIn("SOUTH_NODE", chart["positions"])
        self.assertAlmostEqual(
            (
                chart["positions"]["SOUTH_NODE"]["longitude"]
                - chart["positions"]["NORTH_NODE"]["longitude"]
            ) % 360.0,
            180.0,
        )
        self.assertIsInstance(chart["positions"]["SUN"]["declination"], float)
        self.assertTrue(chart["positions"]["MERCURY"]["retrograde"])
        provenance = chart["backend_provenance"]
        self.assertEqual(provenance["kernel_sha256"], self.kernel_sha)
        self.assertEqual(provenance["coordinate_origin"], "GEOCENTRIC")
        self.assertEqual(
            provenance["reference_frame"],
            "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
        )
        self.assertTrue(provenance["apparent_reduction"])
        self.assertFalse(provenance["topocentric_positions"])
        self.assertFalse(provenance["network_io_used"])
        self.assertFalse(provenance["geocoding_used"])
        self.assertEqual(len(backend._facade.chart_calls), 1)
        _, chart_kwargs = backend._facade.chart_calls[0]
        self.assertNotIn("observer_lat", chart_kwargs)
        self.assertNotIn("observer_lon", chart_kwargs)

    def test_missing_coordinates_are_not_geocoded(self):
        backend = self.backend()
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "coordenadas numéricas",
        ):
            backend.calculate_natal(
                request(latitude=None, longitude=None)
            )

    def test_untimed_natal_is_not_evaluable(self):
        backend = self.backend()
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "no inventa hora natal",
        ):
            backend.calculate_natal(request(birth_time=None))

    def test_dst_gap_and_overlap_fail_closed(self):
        backend = self.backend()
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "inexistente",
        ):
            backend.calculate_natal(
                request(
                    birth_date="2026-03-29",
                    birth_time="02:30",
                    timezone="Europe/Madrid",
                )
            )
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "ambigua",
        ):
            backend.calculate_natal(
                request(
                    birth_date="2026-10-25",
                    birth_time="02:30",
                    timezone="Europe/Madrid",
                )
            )

    def test_house_fallback_is_rejected(self):
        backend = self.backend(FakeFacade(fallback=True))
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "fallback polar",
        ):
            backend.calculate_natal(request())

    def test_house_effective_system_must_match_requested(self):
        backend = self.backend(
            FakeFacade(effective_system="PORPHYRY")
        )
        with self.assertRaisesRegex(
            AstronomyBackendNotEvaluableError,
            "efectivo difiere",
        ):
            backend.calculate_natal(request())

    def test_davison_uses_utc_and_spherical_midpoints(self):
        backend = self.backend()
        result = backend.calculate_davison(
            DavisonRequest(
                subject_a=request(
                    "A",
                    birth_date="2000-01-01",
                    birth_time="00:00",
                    timezone="UTC",
                    latitude=0.0,
                    longitude=170.0,
                ),
                subject_b=request(
                    "B",
                    birth_date="2000-01-03",
                    birth_time="00:00",
                    timezone="UTC",
                    latitude=0.0,
                    longitude=-170.0,
                ),
                policy={
                    "time_midpoint": "UTC_INSTANT",
                    "geographic_midpoint": "BACKEND_DECLARED",
                },
            )
        )
        self.assertEqual(
            result["davison"]["geographic_midpoint"],
            "SPHERICAL_GREAT_CIRCLE",
        )
        self.assertEqual(
            result["davison"]["midpoint_utc"],
            "2000-01-02T00:00:00+00:00",
        )
        self.assertAlmostEqual(
            abs(result["davison"]["midpoint_longitude"]),
            180.0,
        )

    def test_m02_converts_backend_boundary_to_not_evaluable(self):
        backend = self.backend()
        context = ModuleContext(
            module_id="M02",
            module_name="natal",
            mode="FULL",
            raw_input={
                "subjects": [
                    {
                        "id": "A",
                        "birth_date": "1977-03-20",
                        "birth_time": None,
                        "timezone": "Europe/Madrid",
                        "latitude": 41.65,
                        "longitude": -0.88,
                    },
                    {
                        "id": "B",
                        "birth_date": "1980-01-01",
                        "birth_time": "12:00",
                        "timezone": "UTC",
                        "latitude": 18.48,
                        "longitude": -69.91,
                    },
                ]
            },
            canonical_snapshot={},
            prior_results={},
        )
        result = make_m02_natal(backend)(context)
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_m08_converts_backend_policy_boundary_to_not_evaluable(self):
        backend = self.backend()
        context = ModuleContext(
            module_id="M08",
            module_name="davison",
            mode="FULL",
            raw_input={
                "subjects": [
                    {
                        "id": "A",
                        "birth_date": "2000-01-01",
                        "birth_time": "12:00",
                        "timezone": "UTC",
                        "latitude": 41.65,
                        "longitude": -0.88,
                    },
                    {
                        "id": "B",
                        "birth_date": "2000-01-02",
                        "birth_time": "12:00",
                        "timezone": "UTC",
                        "latitude": 18.48,
                        "longitude": -69.91,
                    },
                ],
                "davison_policy": {
                    "time_midpoint": "LOCAL_CLOCK",
                    "geographic_midpoint": "BACKEND_DECLARED",
                },
            },
            canonical_snapshot={},
            prior_results={},
        )
        result = make_m08_davison(backend)(context)
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)


if __name__ == "__main__":
    unittest.main()
