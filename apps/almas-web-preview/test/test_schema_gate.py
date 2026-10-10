"""Offline canonical schema and cross-language read-only integration tests.

The positive fixture is derived solely from the public synthetic ALMAS test suite.
No private-person data, date, address, identifier or raw natal record is used.
"""
import copy
import hashlib
import json
import subprocess
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

    def test_existing_synthetic_canonical_is_schema_valid(self):
        from test_canonical_schema_validation import valid_canonical_analysis
        canonical = valid_canonical_analysis()
        original = copy.deepcopy(canonical)
        original_wire = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(validate_document(self.validator, canonical), [])
        after_wire = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(hashlib.sha256(original_wire).hexdigest(), hashlib.sha256(after_wire).hexdigest())
        self.assertEqual(canonical, original)

    def test_browser_preflight_accepts_synthetic_canonical_without_mutation(self):
        from test_canonical_schema_validation import valid_canonical_analysis
        canonical = valid_canonical_analysis()
        self.assertEqual(validate_document(self.validator, canonical), [])
        script = (
            'import {structuralPreflight} from "./apps/almas-web-preview/validator.mjs";'
            'import {readFileSync} from "node:fs";'
            'import assert from "node:assert/strict";'
            'const source=readFileSync(0,"utf8");const doc=JSON.parse(source);'
            'const saved=JSON.stringify(doc);const result=structuralPreflight(doc);'
            'assert.deepStrictEqual(JSON.stringify(doc),saved);'
            'if(!result.ok){console.error(result.errors.map(e=>e.path).join(","));process.exit(3)}'
            'console.log("COMPATIBLE_AND_UNMODIFIED");'
        )
        res = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            input=json.dumps(canonical, ensure_ascii=False),
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=20,
        )
        # Diagnostic stderr contains only validation paths, never private data.
        self.assertEqual(res.returncode, 0, res.stderr[:1000])
        self.assertEqual(res.stdout.strip(), "COMPATIBLE_AND_UNMODIFIED")

    def test_tampered_model_score_is_rejected(self):
        from test_canonical_schema_validation import valid_canonical_analysis
        canonical = valid_canonical_analysis()
        canonical["models"]["LG"]["iem"] = 1000.0
        errors = validate_document(self.validator, canonical)
        self.assertTrue(any(e["constraint"] == "maximum" for e in errors))

    def test_error_reports_never_contain_payload_values(self):
        marker = "PRIVATE_BIRTH_DETAILS_NEVER_ECHO"
        errors = validate_document(self.validator, {"unreviewed_override": marker})
        self.assertNotIn(marker, str(errors))


if __name__ == "__main__":
    unittest.main()
