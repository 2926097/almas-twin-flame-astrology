from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from almas_tfa.authored_report import (
    SECTION_ORDER,
    canonical_fingerprint,
    validate_authored_report_trace,
)


ROOT = Path(__file__).resolve().parents[1]


class AuthoredReportContractTests(unittest.TestCase):
    def canonical(self):
        return {
            "schema_version": "1.0.0",
            "analysis_mode": "FULL",
            "models": {},
            "evidence": [
                {"evidence_id": "ROOT:R1", "root_id": "R1"}
            ],
            "doctrine": [
                {
                    "claim_id": "D1",
                    "statement": "Doctrinal statement.",
                    "source_ids": ["SRC1"],
                }
            ],
        }

    def report_model(self, canonical):
        fingerprint = canonical_fingerprint(canonical)
        sections = []
        for section_id in SECTION_ORDER:
            sections.append(
                {
                    "section_id": section_id,
                    "section_state": "READY",
                    "available_paths": ["models", "evidence", "doctrine"],
                    "epistemic_classes_allowed": [
                        "A_CALCULATED",
                        "B_TECHNIQUE",
                        "C_DOCTRINE",
                        "D_CONTEMPORARY_USAGE",
                        "E_PROJECT_HYPOTHESIS",
                    ],
                }
            )
        return {
            "canonical_fingerprint": fingerprint,
            "canonical_fingerprint_verified": True,
            "report_state": "READY",
            "sections": sections,
        }

    def authored(self, canonical):
        fingerprint = canonical_fingerprint(canonical)
        sections = []
        for section_id in SECTION_ORDER:
            paths = ["models"]
            classes = ["A_CALCULATED"]
            claims = []
            evidence = []
            sources = []
            if section_id == "S04_STRUCTURE":
                paths = ["evidence"]
                evidence = ["ROOT:R1"]
            if section_id == "S09_DOCTRINE":
                paths = ["doctrine"]
                classes = ["C_DOCTRINE"]
                claims = ["D1"]
                sources = ["SRC1"]
            if section_id == "S10_FINAL_SYNTHESIS":
                paths = ["models", "evidence", "doctrine"]
                classes = [
                    "A_CALCULATED",
                    "C_DOCTRINE",
                    "E_PROJECT_HYPOTHESIS",
                ]
                claims = ["D1"]
                evidence = ["ROOT:R1"]
                sources = ["SRC1"]
            sections.append(
                {
                    "section_id": section_id,
                    "title": section_id,
                    "authoring_state": "AUTHORED",
                    "narrative": f"Narrativa sintética para {section_id}.",
                    "canonical_paths_used": paths,
                    "epistemic_classes_used": classes,
                    "doctrinal_claim_refs": claims,
                    "evidence_refs": evidence,
                    "source_refs": sources,
                    "limitations": [],
                }
            )
        return {
            "schema_version": "1.0.0",
            "document_kind": "ALMAS_AUTHORED_REPORT",
            "language": "es",
            "canonical_fingerprint": fingerprint,
            "report_state": "READY",
            "interpretive_center": (
                "ASTROLOGY_AND_SOURCE_BASED_METAPHYSICAL_HERMENEUTICS"
            ),
            "technical_role": "CALCULATION_TRACEABILITY_AND_QUALITY_CONTROL",
            "metaphysical_scientific_validation_claimed": False,
            "canonical_values_mutated": False,
            "new_calculations_performed": False,
            "new_scores_created": False,
            "sections": sections,
            "bibliography": [
                {
                    "source_id": "SRC1",
                    "citation_label": "Synthetic Source",
                    "source_scope": "DOCTRINE",
                    "author": "Synthetic Author",
                    "work": "Synthetic Work",
                    "tradition": "Synthetic",
                    "locator": "§1",
                    "url": None,
                    "verification_anchor": "Synthetic anchor.",
                }
            ],
        }

    def test_schema_and_trace_accept_valid_authored_report(self):
        canonical = self.canonical()
        authored = self.authored(canonical)
        schema = json.loads(
            (ROOT / "schemas/authored-report.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator(schema).validate(authored)
        validate_authored_report_trace(
            authored,
            self.report_model(canonical),
            canonical,
        )

    def test_rejects_canonical_fingerprint_mismatch(self):
        canonical = self.canonical()
        authored = self.authored(canonical)
        authored["canonical_fingerprint"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "no corresponde"):
            validate_authored_report_trace(
                authored,
                self.report_model(canonical),
                canonical,
            )

    def test_rejects_path_not_exposed_by_m31(self):
        canonical = self.canonical()
        authored = self.authored(canonical)
        authored["sections"][0]["canonical_paths_used"] = ["hidden_namespace"]
        with self.assertRaisesRegex(ValueError, "no autorizadas"):
            validate_authored_report_trace(
                authored,
                self.report_model(canonical),
                canonical,
            )

    def test_rejects_unknown_doctrinal_claim(self):
        canonical = self.canonical()
        authored = self.authored(canonical)
        authored["sections"][8]["doctrinal_claim_refs"] = ["UNKNOWN"]
        with self.assertRaisesRegex(ValueError, "doctrinal_claim_refs"):
            validate_authored_report_trace(
                authored,
                self.report_model(canonical),
                canonical,
            )

    def test_rejects_source_without_bibliography(self):
        canonical = self.canonical()
        authored = self.authored(canonical)
        authored["sections"][8]["source_refs"] = ["MISSING_SOURCE"]
        with self.assertRaisesRegex(ValueError, "sin entrada bibliográfica"):
            validate_authored_report_trace(
                authored,
                self.report_model(canonical),
                canonical,
            )

    def test_not_available_section_must_be_omitted(self):
        canonical = self.canonical()
        model = self.report_model(canonical)
        model["sections"][6]["section_state"] = "NOT_AVAILABLE"
        authored = self.authored(canonical)
        with self.assertRaisesRegex(ValueError, "NOT_AVAILABLE"):
            validate_authored_report_trace(authored, model, canonical)


if __name__ == "__main__":
    unittest.main()
