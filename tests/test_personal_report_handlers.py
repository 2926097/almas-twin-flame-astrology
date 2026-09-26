import copy
import unittest

from almas_tfa.personal_report_handlers import (
    PROFILE_SECTIONS,
    build_personal_report_document_model,
    personal_canonical_fingerprint,
    route_personal_references,
    validate_personal_canonical,
)


class TestPersonalReporting(unittest.TestCase):
    def canonical(self):
        return {
            "schema_version": "1.0.0",
            "analysis_type": "PERSONAL_NATAL",
            "subject": {"id": "SYNTHETIC-A"},
            "data_quality": {"birth_time_quality": "A"},
            "calculation_provenance": {
                "engine": "synthetic-test-backend",
                "engine_version": "0",
                "ephemeris": "synthetic",
                "zodiac": "TROPICAL",
                "house_system": "TOPOCENTRIC",
                "node_type": "TRUE",
                "timezone": "Europe/Madrid",
                "coordinates": {"latitude": 40.0, "longitude": -1.0},
                "calculation_flags": [],
                "input_hash": "abc",
                "warnings": [],
            },
            "natal": {
                "positions": [{"body": "Sun", "longitude": 10.0}],
                "houses": [{"house": 1, "cusp": 20.0}],
                "angles": {"ASC": 20.0},
                "aspects": [],
                "configurations": [],
            },
            "structural_layers": {
                "traditional": {"available": True},
                "modern": {"available": True},
                "evolutionary": {"available": True},
                "kabbalistic": {"available": True},
            },
            "secondary_layers": {
                "draconic": {"available": True},
                "lots": {"available": True},
                "declinations": {"available": True},
                "fixed_stars": {"available": True},
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
            "doctrine": [{"tradition": "KABBALAH", "state": "COMPATIBLE"}],
            "hypotheses": [],
            "counterevidence": [],
            "limitations": [],
            "source_trace": [],
        }

    def test_valid_personal_canonical_is_ready(self):
        canonical = self.canonical()
        gate = validate_personal_canonical(canonical)
        self.assertEqual(gate["state"], "READY")
        self.assertTrue(gate["reportable"])
        self.assertEqual(
            gate["canonical_fingerprint"],
            personal_canonical_fingerprint(canonical),
        )

    def test_time_quality_c_degrades_but_does_not_block(self):
        canonical = self.canonical()
        canonical["data_quality"]["birth_time_quality"] = "C"
        gate = validate_personal_canonical(canonical)
        self.assertEqual(gate["state"], "PARTIAL")
        self.assertIn(
            "TIME_SENSITIVE_FACTORS_REQUIRE_DOWNGRADE",
            gate["degradation_reasons"],
        )

    def test_return_houses_require_documented_location(self):
        canonical = self.canonical()
        canonical["temporal"]["returns"][0]["houses_included"] = True
        gate = validate_personal_canonical(canonical)
        self.assertEqual(gate["state"], "BLOCKED")
        self.assertFalse(gate["reportable"])
        self.assertIn(
            "RETURN_0:HOUSES_WITHOUT_DOCUMENTED_LOCATION",
            gate["blocking_issues"],
        )

    def test_reference_router_is_layer_aware(self):
        domains = route_personal_references(self.canonical())
        for expected in (
            "foundations", "traditional", "modern_psychological",
            "evolutionary", "draconic", "lots", "symmetry",
            "fixed_stars", "timing", "kabbalah", "publication",
        ):
            self.assertIn(expected, domains)

    def test_full_model_never_embeds_canonical_values(self):
        canonical = self.canonical()
        before = copy.deepcopy(canonical)
        model = build_personal_report_document_model(
            canonical, "FULL_CRITICAL_REPORT"
        )
        self.assertEqual(canonical, before)
        self.assertFalse(model["canonical_values_embedded"])
        self.assertFalse(model["canonical_values_mutated"])
        self.assertFalse(model["prose_generated"])
        self.assertFalse(model["docx_created"])
        self.assertFalse(model["pdf_created"])
        self.assertFalse(model["pdf_preflight_performed"])
        self.assertTrue(model["canonical_fingerprint_verified"])

    def test_all_profiles_are_deterministic_and_nonempty(self):
        canonical = self.canonical()
        for profile, expected_ids in PROFILE_SECTIONS.items():
            model = build_personal_report_document_model(canonical, profile)
            ids = tuple(s["section_id"] for s in model["sections"])
            self.assertEqual(ids, expected_ids)
            self.assertGreater(len(ids), 0)

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            build_personal_report_document_model(
                self.canonical(), "UNKNOWN_PROFILE"
            )

    def test_calculation_warning_degrades(self):
        canonical = self.canonical()
        canonical["calculation_provenance"]["warnings"] = ["synthetic warning"]
        gate = validate_personal_canonical(canonical)
        self.assertEqual(gate["state"], "PARTIAL")
        self.assertIn("CALCULATION_WARNINGS_PRESENT", gate["degradation_reasons"])


if __name__ == "__main__":
    unittest.main()
