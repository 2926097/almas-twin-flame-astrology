"""Regression tests for the offline authoritative canonical schema gate.

These are negative-path schema tests, not synthetic valid ALMAS analyses.
"""
import sys
import unittest
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = WEB_DIR.parents[1]
sys.path.insert(0, str(WEB_DIR))

from schema_gate import build_validator, validate_document  # noqa: E402


class CanonicalSchemaGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = build_validator(REPO_ROOT)

    def test_authoritative_schema_version(self):
        self.assertEqual(self.validator.schema["$id"], "https://example.invalid/almas/canonical-analysis.schema.json")
        self.assertEqual(self.validator.schema["properties"]["schema_version"]["const"], "1.0.0")

    def test_missing_required_fields_rejected(self):
        errors = validate_document(self.validator, {})
        self.assertTrue(any(e["constraint"] == "required" for e in errors))

    def test_wrong_schema_version_rejected(self):
        errors = validate_document(self.validator, {"schema_version": "9.9.9"})
        self.assertTrue(any(e["constraint"] == "const" for e in errors))

    def test_additional_property_rejected(self):
        errors = validate_document(self.validator, {"unreviewed_override": 100})
        self.assertTrue(any(e["constraint"] == "additionalProperties" for e in errors))

    def test_error_reports_never_contain_payload_values(self):
        marker = "PRIVATE_BIRTH_DETAILS_NEVER_ECHO"
        errors = validate_document(self.validator, {"unreviewed_override": marker})
        self.assertNotIn(marker, str(errors))


if __name__ == "__main__":
    unittest.main()
