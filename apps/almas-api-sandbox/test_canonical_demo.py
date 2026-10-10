"""Regression checks for the entirely synthetic M30/M31 HTTP sandbox."""
from __future__ import annotations

from copy import deepcopy
import http.client
import json
import os
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "almas-api-sandbox"))
sys.path.insert(0, str(ROOT / "apps" / "almas-web-preview"))
sys.path.insert(0, str(ROOT / "tests"))

from canonical_demo import KIND, _ctx, _fingerprint, evaluate_synthetic_canonical
from server import Handler, dispatch
from schema_gate import build_validator, validate_document
from test_canonical_schema_validation import valid_canonical_analysis
from almas_tfa.report_gate_handlers import m30_report_gate
from almas_tfa.report_model_handlers import m31_report

TEST_KEY = "synthetic_test_key_64_characters_long_only_for_tests_no_prod_1234567890"


class SyntheticCanonicalDemoTests(unittest.TestCase):
    def test_schema_and_m30_m31_report_contracts(self):
        result = evaluate_synthetic_canonical()
        self.assertEqual(result["kind"], KIND)
        self.assertTrue(result["synthetic"])
        self.assertTrue(result["m30_executed"])
        self.assertTrue(result["m31_executed"])
        self.assertFalse(result["canonical_returned"])
        self.assertEqual(result["schema_validation"], "PASS")
        self.assertIn(result["m30"]["state"], ["PARTIAL", "READY"])
        self.assertEqual(result["m30"]["state"], result["m31"]["report_state"])
        self.assertTrue(result["m31"]["canonical_fingerprint_verified"])
        self.assertFalse(result["m31"]["canonical_values_embedded"])
        self.assertFalse(result["m31"]["prose_generated"])
        self.assertEqual(len(result["m31"]["section_ids"]), 11)
        self.assertTrue(result["m30"]["reportable"])
        self.assertEqual(len(result["canonical_fingerprint"]), 64)

    def test_canonical_no_mutation_after_gate(self):
        canonical = valid_canonical_analysis()
        original = deepcopy(canonical)
        before = _fingerprint(canonical)
        m30 = m30_report_gate(_ctx("M30", {"canonical_analysis": canonical}, {}))
        gate = dict(m30.payload)
        attached = m30.canonical_updates["canonical_analysis"]
        m31 = m31_report(_ctx("M31", {}, {"canonical_analysis": attached, "report_gate": gate}))
        self.assertEqual(canonical, original)
        self.assertEqual(_fingerprint(canonical), before)
        self.assertEqual(gate["canonical_fingerprint"], before)
        self.assertEqual(m31.payload["canonical_fingerprint"], before)
        for filename, payload in (
            ("canonical-analysis.schema.json", canonical),
            ("report-gate-output.schema.json", gate),
            ("report-document-model.schema.json", dict(m31.payload)),
        ):
            self.assertEqual(validate_document(build_validator(ROOT, filename), payload), [])

    def test_tampering_after_m30_blocks_m31(self):
        canonical = valid_canonical_analysis()
        gate = m30_report_gate(_ctx("M30", {"canonical_analysis": canonical}, {})).payload
        corrupted = deepcopy(canonical)
        corrupted["indices"]["IDD"] = 99.0
        with self.assertRaises(ValueError):
            m31_report(_ctx("M31", {}, {"canonical_analysis": corrupted, "report_gate": gate}))

    def test_unknown_contract_schema_name_blocks(self):
        with self.assertRaises(ValueError):
            build_validator(ROOT, "../some-other-schema.json")

    def test_secret_and_fixed_route_required(self):
        denied = []
        def reject_engine():
            denied.append("called")
            return {}
        for header in (None, "Bearer invalid", ""):
            code, response = dispatch(
                "GET", "/v1/canonical-demo", header, TEST_KEY,
                canonical_engine=reject_engine,
            )
            self.assertEqual(code, 401)
            self.assertEqual(response["error"], "UNAUTHORIZED")
        self.assertEqual(denied, [])
        code, _ = dispatch("POST", "/v1/canonical-demo", "Bearer " + TEST_KEY, TEST_KEY, canonical_engine=reject_engine)
        self.assertEqual(code, 405)
        code, _ = dispatch("GET", "/v1/canonical-demo?analysis=private", "Bearer " + TEST_KEY, TEST_KEY, canonical_engine=reject_engine)
        self.assertEqual(code, 404)
        self.assertEqual(denied, [])

    def test_http_authenticated_synthetic_only(self):
        with patch.dict(os.environ, {"ALMAS_API_SHARED_SECRET": TEST_KEY}):
            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                port = server.server_address[1]
                for header, expected in (({}, 401), ({"Authorization": "Bearer " + TEST_KEY}, 200)):
                    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
                    connection.request("GET", "/v1/canonical-demo", headers=header)
                    response = connection.getresponse()
                    body = json.loads(response.read())
                    self.assertEqual(response.status, expected)
                    self.assertEqual(response.getheader("Cache-Control"), "no-store, max-age=0")
                    if expected == 200:
                        self.assertEqual(body["kind"], KIND)
                        self.assertNotIn("models", body)
                        self.assertNotIn("natal_context", body)
                        self.assertNotIn("canonical_analysis", body)
                    connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
