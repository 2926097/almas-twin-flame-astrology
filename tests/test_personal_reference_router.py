from copy import deepcopy
import json
from pathlib import Path
import unittest

from almas_tfa.personal_reference_router import (
    PersonalReferenceRouterError,
    enrich_personal_canonical_sources,
    load_personal_reference_router,
    route_personal_reference_sources,
)


ROOT = Path(__file__).resolve().parents[1]


def source_registry():
    return json.loads(
        (ROOT / "reference/source-registry.json").read_text(
            encoding="utf-8"
        )
    )


def canonical():
    return {
        "schema_version": "1.0.0",
        "analysis_type": "PERSONAL_NATAL",
        "subject": {"subject_id": "SYNTHETIC-SOURCE-ROUTER"},
        "data_quality": {
            "birth_time_quality": "A",
            "timed": True,
        },
        "natal": {
            "subject_id": "SYNTHETIC-SOURCE-ROUTER",
            "timed": True,
            "backend_id": "MOIRA_JPL_SPK",
            "backend_version": "6.8.2",
            "zodiac": "TROPICAL",
            "positions": {"SUN": {"longitude": 10.0}},
            "backend_provenance": {
                "policy_id": "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1",
                "adapter_id": "ALMAS_MOIRA_JPL_SPK_V1",
                "backend_id": "MOIRA_JPL_SPK",
                "backend_version": "6.8.2",
                "kernel_sha256": "f" * 64,
                "house_system": "PLACIDUS",
                "node_mode": "TRUE_NODE",
                "zodiac": "TROPICAL",
                "network_io_used": False,
                "geocoding_used": False,
            },
        },
        "counterevidence": [],
        "limitations": [],
    }


class PersonalReferenceRouterTests(unittest.TestCase):
    def test_manifest_sources_exist_in_canonical_registry(self):
        router = load_personal_reference_router()
        registry_ids = {
            item["id"]
            for item in source_registry()["entries"]
        }

        for domain, config in router["domains"].items():
            missing = set(config["source_ids"]) - registry_ids
            self.assertEqual(
                missing,
                set(),
                f"{domain}: fuentes inexistentes",
            )

    def test_base_route_resolves_foundational_corpus(self):
        result = route_personal_reference_sources(
            canonical(),
            source_registry(),
        )
        domains = {
            item["domain"]: item
            for item in result["domains"]
        }

        for expected in (
            "foundations",
            "traditional",
            "modern_psychological",
            "publication",
        ):
            self.assertIn(expected, domains)
        self.assertIn(
            "astrodienst_zodiac_sign",
            result["source_ids"],
        )
        self.assertEqual(result["source_gaps"], [])

    def test_optional_layers_add_matching_sources(self):
        data = canonical()
        data["structural_layers"] = {
            "karmic": {"available": True},
            "kabbalistic": {"available": True},
        }
        data["secondary_layers"] = {
            "draconic": {"available": True},
            "lots": {"available": True},
            "declinations": {"available": True},
            "asteroids": {"available": True},
        }
        data["temporal"] = {"signals": []}

        result = route_personal_reference_sources(
            data,
            source_registry(),
        )
        ids = set(result["source_ids"])

        for expected in (
            "arroyo_astrology_karma_transformation_1992",
            "zohar_lech_lecha_32_346_350",
            "crane_draconic_astrology_1987",
            "paulus_alexandrinus_introductory_matters_ch23",
            "boehrer_declination_other_dimension",
            "george_bloch_asteroid_goddesses_2003",
            "astrodienst_transit",
        ):
            self.assertIn(expected, ids)

    def test_fixed_stars_exposes_gap_without_inventing_source(self):
        data = canonical()
        data["secondary_layers"] = {
            "fixed_stars": {"available": True},
        }

        result = route_personal_reference_sources(
            data,
            source_registry(),
        )
        domains = {
            item["domain"]: item
            for item in result["domains"]
        }

        self.assertIn("fixed_stars", result["source_gaps"])
        self.assertEqual(
            domains["fixed_stars"]["status"],
            "SOURCE_GAP",
        )
        self.assertEqual(
            domains["fixed_stars"]["source_ids"],
            [],
        )

    def test_enrichment_adds_trace_without_mutating_canonical(self):
        data = canonical()
        snapshot = deepcopy(data)
        enriched = enrich_personal_canonical_sources(
            data,
            source_registry(),
        )

        self.assertEqual(data, snapshot)
        self.assertIn("source_trace", enriched)
        ids = {
            item["source_id"]
            for item in enriched["source_trace"]
        }
        self.assertIn("astrodienst_zodiac_sign", ids)
        self.assertNotIn("source_trace", data)

    def test_router_fails_if_manifest_references_unknown_source(self):
        router = load_personal_reference_router()
        broken = deepcopy(router)
        broken["domains"]["foundations"]["source_ids"].append(
            "NOT_REGISTERED"
        )

        with self.assertRaisesRegex(
            PersonalReferenceRouterError,
            "NOT_REGISTERED",
        ):
            route_personal_reference_sources(
                canonical(),
                source_registry(),
                router=broken,
            )


if __name__ == "__main__":
    unittest.main()
