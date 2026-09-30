import unittest

from almas_tfa.personal_authored_report import (
    PersonalAuthoringError,
    validate_personal_authored_report_trace,
)
from almas_tfa.personal_reporting import (
    build_personal_report_document_model,
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
        "kernel_sha256": "b" * 64,
        "house_system": "PLACIDUS",
        "node_mode": "TRUE_NODE",
            "node_variants": ["TRUE", "MEAN"],
        "zodiac": "TROPICAL",
        "coordinate_origin": "GEOCENTRIC",
        "reference_frame": "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
        "apparent_reduction": True,
        "topocentric_positions": False,
        "network_io_used": False,
        "geocoding_used": False,
    }


def canonical():
    return {
        "schema_version": "1.0.0",
        "analysis_type": "PERSONAL_NATAL",
        "subject": {"subject_id": "SYNTHETIC-PERSON"},
        "data_quality": {
            "birth_time_quality": "A",
            "timed": True,
            "birth_time_source_class": "DOCUMENTARY",
        },
        "natal": {
            "subject_id": "SYNTHETIC-PERSON",
            "timed": True,
            "backend_id": "MOIRA_JPL_SPK",
            "backend_version": "6.8.2",
            "zodiac": "TROPICAL",
            "positions": {
                "SUN": {"longitude": 10.0},
                "MOON": {"longitude": 80.0},
            },
            "angles": {"ASC": 20.0, "MC": 110.0},
            "backend_provenance": production_provenance(),
        },
        "structural_layers": {
            "evolutionary": {"available": True},
            "karmic": {"available": True},
        },
        "secondary_layers": {
            "draconic": {"available": True},
        },
        "temporal": {"signals": []},
        "doctrine": [
            {
                "claim_id": "CLAIM-1",
                "source_refs": ["SRC-1"],
            }
        ],
        "hypotheses": [],
        "counterevidence": [],
        "limitations": [],
        "source_trace": [
            {
                "source_id": "SRC-1",
                "scope": "DOCTRINE",
            }
        ],
    }


def authored(data, model):
    sections = []
    for model_section in model["sections"]:
        if model_section["section_state"] == "NOT_AVAILABLE":
            sections.append(
                {
                    "section_id": model_section["section_id"],
                    "title": model_section["title"],
                    "authoring_state": "OMITTED_NOT_AVAILABLE",
                    "narrative": "",
                    "canonical_paths_used": [],
                    "epistemic_classes_used": [],
                    "doctrinal_claim_refs": [],
                    "source_refs": [],
                    "limitations": [],
                }
            )
            continue
        paths = model_section["available_paths"]
        sections.append(
            {
                "section_id": model_section["section_id"],
                "title": model_section["title"],
                "authoring_state": "AUTHORED",
                "narrative": "Lectura sintética trazada al canonical.",
                "canonical_paths_used": [paths[0]],
                "epistemic_classes_used": [
                    model_section["epistemic_classes_allowed"][0]
                ],
                "doctrinal_claim_refs": [],
                "source_refs": [],
                "limitations": [],
            }
        )

    return {
        "schema_version": "1.0.0",
        "document_kind": "ALMAS_PERSONAL_AUTHORED_REPORT",
        "language": "es",
        "report_profile": model["report_profile"],
        "canonical_fingerprint": model["canonical_fingerprint"],
        "report_state": model["report_state"],
        "interpretive_center": (
            "PERSONAL_ASTROLOGY_AND_SOURCE_BASED_HERMENEUTICS"
        ),
        "technical_role": "CALCULATION_TRACEABILITY_AND_QUALITY_CONTROL",
        "metaphysical_scientific_validation_claimed": False,
        "personal_data_minimized": True,
        "canonical_values_mutated": False,
        "new_calculations_performed": False,
        "new_scores_created": False,
        "sections": sections,
        "bibliography": [
            {
                "source_id": "SRC-1",
                "citation_label": "Fuente sintética",
                "source_scope": "DOCTRINE",
                "author": None,
                "work": None,
                "tradition": None,
                "locator": None,
                "url": None,
                "verification_anchor": None,
            }
        ],
    }


class PersonalAuthoredReportTests(unittest.TestCase):
    def setUp(self):
        self.canonical = canonical()
        self.model = build_personal_report_document_model(
            self.canonical,
            "FULL_CRITICAL_REPORT",
        )
        self.report = authored(self.canonical, self.model)

    def test_valid_report_preserves_trace(self):
        validate_personal_authored_report_trace(
            self.report,
            self.model,
            self.canonical,
        )

    def test_fingerprint_mismatch_is_rejected(self):
        self.report["canonical_fingerprint"] = "0" * 64
        with self.assertRaises(PersonalAuthoringError):
            validate_personal_authored_report_trace(
                self.report,
                self.model,
                self.canonical,
            )

    def test_profile_mismatch_is_rejected(self):
        self.report["report_profile"] = "TECHNICAL_ATLAS"
        with self.assertRaises(PersonalAuthoringError):
            validate_personal_authored_report_trace(
                self.report,
                self.model,
                self.canonical,
            )

    def test_section_order_must_match_model(self):
        self.report["sections"][0], self.report["sections"][1] = (
            self.report["sections"][1],
            self.report["sections"][0],
        )
        with self.assertRaises(PersonalAuthoringError):
            validate_personal_authored_report_trace(
                self.report,
                self.model,
                self.canonical,
            )

    def test_unknown_canonical_path_is_rejected(self):
        self.report["sections"][0]["canonical_paths_used"] = ["raw.birth_time"]
        with self.assertRaises(PersonalAuthoringError):
            validate_personal_authored_report_trace(
                self.report,
                self.model,
                self.canonical,
            )

    def test_untraced_bibliography_source_is_rejected(self):
        self.report["bibliography"][0]["source_id"] = "UNKNOWN"
        with self.assertRaises(PersonalAuthoringError):
            validate_personal_authored_report_trace(
                self.report,
                self.model,
                self.canonical,
            )

    def test_unknown_doctrinal_claim_is_rejected(self):
        self.report["sections"][0]["doctrinal_claim_refs"] = ["UNKNOWN"]
        with self.assertRaises(PersonalAuthoringError):
            validate_personal_authored_report_trace(
                self.report,
                self.model,
                self.canonical,
            )

    def test_authoring_cannot_disable_data_minimization(self):
        self.report["personal_data_minimized"] = False
        with self.assertRaises(PersonalAuthoringError):
            validate_personal_authored_report_trace(
                self.report,
                self.model,
                self.canonical,
            )


if __name__ == "__main__":
    unittest.main()
