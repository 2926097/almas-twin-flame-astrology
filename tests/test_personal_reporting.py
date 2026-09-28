import unittest

from almas_tfa.personal_reporting import (
    PROFILE_SECTIONS,
    build_personal_report_document_model,
    personal_canonical_fingerprint,
    route_personal_reference_domains,
    validate_personal_canonical,
)


def production_provenance():
    return {
        "policy_id": "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1",
        "adapter_id": "ALMAS_MOIRA_JPL_SPK_V1",
        "backend_id": "MOIRA_JPL_SPK",
        "backend_version": "6.8.2",
        "provider_package": "moira-astro",
        "provider_version": "6.8.2",
        "kernel_filename": "de440s.bsp",
        "kernel_family": "DE440",
        "kernel_sha256": "a" * 64,
        "house_system": "PLACIDUS",
        "node_mode": "TRUE_NODE",
        "zodiac": "TROPICAL",
        "coordinate_origin": "GEOCENTRIC",
        "reference_frame": "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
        "apparent_reduction": True,
        "topocentric_positions": False,
        "network_io_used": False,
        "geocoding_used": False,
    }


def canonical(quality="A"):
    return {
        "schema_version": "1.0.0",
        "analysis_type": "PERSONAL_NATAL",
        "subject": {"subject_id": "SYNTHETIC-A"},
        "data_quality": {
            "birth_time_quality": quality,
            "timed": True,
            "birth_time_source_class": "DOCUMENTARY",
        },
        "natal": {
            "subject_id": "SYNTHETIC-A",
            "timed": True,
            "backend_id": "MOIRA_JPL_SPK",
            "backend_version": "6.8.2",
            "zodiac": "TROPICAL",
            "positions": {
                "SUN": {"longitude": 120.0},
                "MOON": {"longitude": 42.0},
            },
            "angles": {"ASC": 12.0, "MC": 101.0},
            "houses": {"1": 12.0, "10": 101.0},
            "backend_provenance": production_provenance(),
        },
        "structural_layers": {
            "evolutionary": {"available": True},
            "karmic": {"available": True},
            "esoteric": {"available": False},
        },
        "secondary_layers": {
            "draconic": {"available": True},
            "lots": {"available": True},
            "declinations": {"available": True},
            "asteroids": {"available": False},
        },
        "temporal": {
            "returns": [
                {
                    "kind": "SOLAR_RETURN",
                    "houses_included": False,
                    "location_documented": False,
                }
            ]
        },
        "doctrine": [{"claim_id": "KABBALAH_DEMO", "tradition": "KABBALAH"}],
        "hypotheses": [],
        "counterevidence": [],
        "limitations": [],
        "source_trace": [],
    }


class PersonalReportingTests(unittest.TestCase):
    def test_ready_canonical_is_fingerprintable(self):
        data = canonical()
        gate = validate_personal_canonical(data)
        self.assertEqual(gate["state"], "READY")
        self.assertTrue(gate["reportable"])
        self.assertEqual(
            gate["canonical_fingerprint"],
            personal_canonical_fingerprint(data),
        )

    def test_low_reliability_degrades_without_blocking(self):
        gate = validate_personal_canonical(canonical("C"))
        self.assertEqual(gate["state"], "PARTIAL")
        self.assertTrue(gate["reportable"])
        self.assertIn(
            "TIME_SENSITIVE_FACTORS_REQUIRE_DOWNGRADE",
            gate["degradation_reasons"],
        )

    def test_subject_mismatch_blocks(self):
        data = canonical()
        data["natal"]["subject_id"] = "OTHER"
        gate = validate_personal_canonical(data)
        self.assertEqual(gate["state"], "BLOCKED")
        self.assertIn("NATAL_SUBJECT_ID_MISMATCH", gate["blocking_issues"])

    def test_backend_provenance_is_mandatory(self):
        data = canonical()
        data["natal"].pop("backend_provenance")
        gate = validate_personal_canonical(data)
        self.assertFalse(gate["reportable"])
        self.assertIn("BACKEND_PROVENANCE_REQUIRED", gate["blocking_issues"])

    def test_return_houses_require_documented_location(self):
        data = canonical()
        data["temporal"]["returns"][0]["houses_included"] = True
        gate = validate_personal_canonical(data)
        self.assertFalse(gate["reportable"])
        self.assertIn(
            "RETURN_0:HOUSES_WITHOUT_DOCUMENTED_LOCATION",
            gate["blocking_issues"],
        )

    def test_reference_router_only_adds_active_domains(self):
        domains = route_personal_reference_domains(canonical())
        for expected in (
            "foundations",
            "traditional",
            "modern_psychological",
            "evolutionary",
            "karmic",
            "draconic",
            "lots",
            "symmetry",
            "timing",
            "kabbalah",
            "publication",
        ):
            self.assertIn(expected, domains)
        self.assertNotIn("asteroids", domains)

    def test_full_profile_preserves_personal_section_order(self):
        data = canonical()
        model = build_personal_report_document_model(
            data,
            "FULL_CRITICAL_REPORT",
        )
        self.assertEqual(
            [item["section_id"] for item in model["sections"]],
            list(PROFILE_SECTIONS["FULL_CRITICAL_REPORT"]),
        )
        self.assertEqual(model["report_state"], "READY")
        self.assertTrue(model["canonical_fingerprint_verified"])
        self.assertTrue(
            model["publication_contract"][
                "reuse_existing_publication_infrastructure"
            ]
        )
        self.assertEqual(
            model["publication_contract"]["adapter_status"],
            "PENDING_ADAPTER",
        )

    def test_model_rejects_blocked_canonical(self):
        data = canonical()
        data["natal"]["backend_provenance"]["network_io_used"] = True
        with self.assertRaises(ValueError):
            build_personal_report_document_model(data)


if __name__ == "__main__":
    unittest.main()
