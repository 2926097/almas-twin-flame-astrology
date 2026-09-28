import unittest

from almas_tfa.astrology_backend import (
    AstronomyBackendNotEvaluableError,
)
from almas_tfa.personal_request_pipeline import (
    PersonalRequestError,
    build_personal_canonical_from_request,
    build_personal_report_context_from_request,
)
from almas_tfa.personal_reporting import validate_personal_canonical


def provenance():
    return {
        "policy_id": "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1",
        "adapter_id": "ALMAS_MOIRA_JPL_SPK_V1",
        "backend_id": "FAKE_PERSONAL",
        "backend_version": "1",
        "provider_package": "synthetic-test-backend",
        "provider_version": "1",
        "kernel_filename": "synthetic.bsp",
        "kernel_family": "DE440",
        "kernel_sha256": "e" * 64,
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


class FakePersonalBackend:
    backend_id = "FAKE_PERSONAL"
    backend_version = "1"

    @property
    def provenance(self):
        return provenance()

    def calculate_natal(self, request):
        if request.birth_date == "1900-01-01":
            raise AstronomyBackendNotEvaluableError("synthetic failure")
        return {
            "subject_id": request.subject_id,
            "timed": request.timed,
            "backend_id": self.backend_id,
            "backend_version": self.backend_version,
            "zodiac": "TROPICAL",
            "positions": {
                "SUN": {"longitude": 120.0},
                "MOON": {"longitude": 42.0},
            },
            "angles": {"ASC": 11.0, "MC": 101.0},
            "houses": {"1": 11.0, "10": 101.0},
            "metadata": {
                "utc_instant": "2030-01-01T00:00:00+00:00",
                "jd_ut": 2462502.5,
                "jd_tt": 2462502.5008,
                "latitude": request.latitude,
                "longitude": request.longitude,
            },
        }


class NoProvenanceBackend:
    backend_id = "NO_PROVENANCE"
    backend_version = "1"

    def calculate_natal(self, request):
        return {
            "subject_id": request.subject_id,
            "timed": request.timed,
            "positions": {"SUN": {"longitude": 1.0}},
        }


def request(quality="A"):
    return {
        "schema_version": "1.0.0",
        "subject": {
            "id": "SYNTHETIC-REQUEST",
            "display_name": "Caso sintético",
            "birth_date": "2030-01-01",
            "birth_time": "12:30",
            "timezone": "Europe/Madrid",
            "place": "Synthetic City",
            "latitude": 40.0,
            "longitude": -3.0,
            "time_reliability": quality,
            "birth_time_source_class": "DOCUMENTARY",
        },
        "report_profile": "FULL_CRITICAL_REPORT",
    }


class PersonalRequestPipelineTests(unittest.TestCase):
    def test_request_builds_reportable_minimized_canonical(self):
        canonical = build_personal_canonical_from_request(
            request(),
            FakePersonalBackend(),
        )
        gate = validate_personal_canonical(canonical)

        self.assertEqual(gate["state"], "READY")
        self.assertTrue(gate["reportable"])
        self.assertEqual(
            canonical["subject"]["subject_id"],
            "SYNTHETIC-REQUEST",
        )
        self.assertEqual(
            canonical["subject"]["display_name"],
            "Caso sintético",
        )
        self.assertNotIn("birth_date", canonical["subject"])
        self.assertNotIn("birth_time", canonical["subject"])
        self.assertNotIn("timezone", canonical["subject"])
        self.assertNotIn("place", canonical["subject"])
        self.assertNotIn("metadata", canonical["natal"])
        self.assertIn("backend_provenance", canonical["natal"])

    def test_backend_metadata_cannot_leak_coordinates_or_jd(self):
        canonical = build_personal_canonical_from_request(
            request(),
            FakePersonalBackend(),
        )
        natal = canonical["natal"]
        self.assertNotIn("metadata", natal)
        self.assertNotIn("latitude", natal)
        self.assertNotIn("longitude", natal)

    def test_missing_time_reliability_is_rejected_without_invention(self):
        payload = request()
        payload["subject"].pop("time_reliability")
        with self.assertRaises(PersonalRequestError):
            build_personal_canonical_from_request(
                payload,
                FakePersonalBackend(),
            )

    def test_backend_without_provenance_fails_closed(self):
        with self.assertRaisesRegex(
            PersonalRequestError,
            "backend_provenance",
        ):
            build_personal_canonical_from_request(
                request(),
                NoProvenanceBackend(),
            )

    def test_low_quality_time_remains_reportable_but_partial(self):
        canonical = build_personal_canonical_from_request(
            request("C"),
            FakePersonalBackend(),
        )
        gate = validate_personal_canonical(canonical)
        self.assertEqual(gate["state"], "PARTIAL")
        self.assertTrue(gate["reportable"])
        self.assertTrue(canonical["limitations"])

    def test_context_builds_canonical_and_requested_profile_model(self):
        payload = request()
        payload["report_profile"] = "EXECUTIVE_PERSONAL_REPORT"
        context = build_personal_report_context_from_request(
            payload,
            FakePersonalBackend(),
        )

        self.assertIn("personal_canonical_analysis", context)
        model = context["personal_report_document_model"]
        self.assertEqual(
            model["report_profile"],
            "EXECUTIVE_PERSONAL_REPORT",
        )
        self.assertEqual(model["report_state"], "READY")
        self.assertEqual(len(model["sections"]), 6)

    def test_unknown_profile_is_rejected_before_calculation(self):
        payload = request()
        payload["report_profile"] = "UNKNOWN"
        with self.assertRaises(PersonalRequestError):
            build_personal_report_context_from_request(
                payload,
                FakePersonalBackend(),
            )

    def test_backend_not_evaluable_error_is_preserved(self):
        payload = request()
        payload["subject"]["birth_date"] = "1900-01-01"
        with self.assertRaises(AstronomyBackendNotEvaluableError):
            build_personal_canonical_from_request(
                payload,
                FakePersonalBackend(),
            )


if __name__ == "__main__":
    unittest.main()
