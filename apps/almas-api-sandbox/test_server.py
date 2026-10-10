"""Safety, auth and core-integration tests for the synthetic-only HTTP boundary."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "apps" / "almas-api-sandbox"))
from server import EXPECTED_KIND, FIXTURE, compute_synthetic, dispatch  # noqa: E402
from almas_tfa.analysis import analyze_precomputed  # noqa: E402

KEY = "test_only_valid_64_character_key_that_is_never_a_deployment_secret_1234"


class SandboxApiTests(unittest.TestCase):
    def test_health_contains_no_private_data(self):
        status, body = dispatch("GET", "/_health", None, KEY)
        self.assertEqual(status, 200)
        self.assertEqual(body, {"status": "ok", "scope": "synthetic_only"})

    def test_no_auth_denied_without_invoking_engine(self):
        calls = []
        def engine():
            calls.append("invoked")
            return {"invalid": True}
        for auth in (None, "", "Bearer wrong", "Basic anything"):
            status, response = dispatch("GET", "/v1/synthetic", auth, KEY, engine)
            self.assertEqual(status, 401)
            self.assertEqual(response, {"error": "UNAUTHORIZED"})
        self.assertEqual(calls, [])

    def test_no_config_fail_closed(self):
        status, body = dispatch("GET", "/v1/synthetic", "Bearer anything", "", lambda: {})
        self.assertEqual(status, 503)
        self.assertEqual(body, {"error": "SERVICE_NOT_CONFIGURED"})

    def test_non_get_methods_never_run_engine(self):
        for method in ("POST", "PUT", "DELETE"):
            status, _ = dispatch(method, "/v1/synthetic", "Bearer " + KEY, KEY, lambda: self.fail("run"))
            self.assertEqual(status, 405)

    def test_query_and_unknown_path_never_run_engine(self):
        for target in ("/v1/synthetic?private=1", "/v1/person", "/v1/synthetic/"):
            status, _ = dispatch("GET", target, "Bearer " + KEY, KEY, lambda: self.fail("run"))
            self.assertEqual(status, 404)

    def test_authenticated_demo_matches_unmodified_library(self):
        before_bytes = FIXTURE.read_bytes()
        fixture = json.loads(before_bytes)
        copy_fixture = copy.deepcopy(fixture)
        expected = analyze_precomputed(fixture)
        status, body = dispatch("GET", "/v1/synthetic", "Bearer " + KEY, KEY)
        self.assertEqual(status, 200)
        self.assertEqual(body["kind"], EXPECTED_KIND)
        self.assertEqual(body["engine_result"], expected)
        self.assertEqual(body["engine_result"]["input_mode"], "PRECOMPUTED_PILLARS")
        self.assertEqual(body["canonical_analysis"], False)
        self.assertEqual(body["m30_executed"], False)
        self.assertEqual(copy_fixture, fixture)
        self.assertEqual(hashlib.sha256(before_bytes).hexdigest(), hashlib.sha256(FIXTURE.read_bytes()).hexdigest())

    def test_no_private_labels_in_demo(self):
        doc = json.dumps(compute_synthetic(), ensure_ascii=False)
        self.assertNotIn("birth_time", doc)
        self.assertNotIn("birth_place", doc)
        self.assertNotIn("subject_id", doc)
        self.assertNotIn("raw_input", doc)


if __name__ == "__main__":
    unittest.main()
