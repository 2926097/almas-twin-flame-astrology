"""Contract, engine and CSRF regression for loopback-only personal execution."""
from __future__ import annotations

import http.client
import json
from hashlib import sha256
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "apps" / "almas-web-preview"
sys.path.insert(0, str(WEB))
sys.path.insert(0, str(ROOT / "src"))
from local_engine_server import (  # noqa: E402
    LocalEngineServer, process_locally, strict_object_pairs, validate_request,
)

A = dict(id="A", birth_date="1988-06-17", birth_time="13:20",
    time_reliability="A", timezone="Europe/Madrid", latitude=40.4168, longitude=-3.7038)
B = dict(id="B", birth_date="1990-11-06", birth_time="09:10",
    time_reliability="B", timezone="America/Chicago", latitude=41.8781, longitude=-87.6298)

def request():
    return dict(format="ALMAS_WORK_REQUEST", type="RELATIONAL",
        execution_state="REQUEST_ONLY", public_version="1.26.0",
        analysis_profile="FULL_MULTIDISCIPLINARY",
        analysis_policy_profile="ALMAS_RELATIONAL_STRICT_RESEARCH_V1",
        subjects=[dict(A), dict(B)], events=[])

class LocalEngineContractTests(unittest.TestCase):
    def test_request_acceptance_and_no_secret_remote_options(self):
        self.assertEqual(validate_request(request())["subjects"][0]["id"], "A")
        for key, val in (
            ("analysis_policy_profile", "UNVERIFIED"),
            ("execution_state", "RUN"),
            ("events", [{"name": "personal"}]),
        ):
            candidate = request()
            candidate[key] = val
            with self.assertRaises(ValueError):
                validate_request(candidate)
        candidate = request()
        candidate["atacires_requests"] = [{}]
        with self.assertRaises(ValueError):
            validate_request(candidate)

    def test_invalid_dst_and_date_and_unsafe_coordinates(self):
        candidate = request()
        candidate["subjects"][0]["birth_date"] = "2026-02-29"
        with self.assertRaises(ValueError):
            validate_request(candidate)
        candidate = request()
        candidate["subjects"][0]["birth_date"] = "2026-03-29"
        candidate["subjects"][0]["birth_time"] = "02:30"  # Europe/Madrid DST gap
        with self.assertRaisesRegex(ValueError, "DST_TIME_NONEXISTENT_OR_AMBIGUOUS"):
            validate_request(candidate)
        candidate = request()
        candidate["subjects"][0]["birth_date"] = "2026-10-25"
        candidate["subjects"][0]["birth_time"] = "02:30"  # Europe/Madrid DST fold
        with self.assertRaisesRegex(ValueError, "DST_TIME_NONEXISTENT_OR_AMBIGUOUS"):
            validate_request(candidate)
        candidate = request()
        candidate["subjects"][0]["latitude"] = float("nan")
        with self.assertRaises(ValueError):
            validate_request(candidate)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            json.loads('{"subjects":[{"id":"A","id":"B"}]}', object_pairs_hook=strict_object_pairs)

    def test_official_m30_m31_atlas_and_fingerprint(self):
        canonical = {"models": {}, "evidence": [], "counterevidence": [], "indices": {}}
        fingerprint = sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        gate = dict(state="PARTIAL", reportable=True, canonical_fingerprint=fingerprint)
        model = dict(report_state="PARTIAL", canonical_fingerprint=fingerprint,
            canonical_fingerprint_verified=True, canonical_values_mutated=False,
            canonical_values_embedded=False, prose_generated=False, sections=[])
        statuses = {"M%02d" % i: "COMPLETED" for i in range(32)}
        def runner(_request, _manifest, **kwargs):
            self.assertIs(kwargs["astrology_backend"], kwargs["davison_backend"])
            return {"canonical_analysis": canonical, "orchestration_run":
                {"canonical": {"report_gate": gate, "report_document_model": model}},
                "execution_receipt": {"module_statuses": statuses, "failed_modules": []}}
        with patch("almas_tfa.relational_request_pipeline.assess_relational_work_request",
            return_value={"ready_for_raw_input": True}):
            result = process_locally(request(), backend_factory=lambda: object(),
                runner=runner, schema_check=lambda *_args: None)
            self.assertEqual(result["state"], "PARTIAL")
            self.assertEqual(result["m31"]["report_state"], "PARTIAL")
            self.assertEqual(result["atlas"]["canonical_fingerprint"], fingerprint)
            self.assertEqual(len(result["module_statuses"]), 32)
            self.assertNotIn("raw_input", result)
            model["canonical_fingerprint"] = "f" * 64
            with self.assertRaisesRegex(ValueError, "FINGERPRINT"):
                process_locally(request(), backend_factory=lambda: object(),
                    runner=runner, schema_check=lambda *_args: None)
            model["canonical_fingerprint"] = fingerprint
            statuses["M02"] = "FAILED"
            def failed_runner(*_args, **_kwargs):
                return {"execution_receipt": {"module_statuses": statuses,
                    "failed_modules": ["M02"]}, "canonical_analysis": None}
            blocked = process_locally(request(), backend_factory=lambda: object(),
                runner=failed_runner)
            self.assertEqual(blocked["state"], "BLOCKED")
            self.assertIsNone(blocked["canonical_analysis"])

    def test_loopback_csrf_origin_get_and_post_rejection(self):
        with LocalEngineServer(("127.0.0.1", 0), backend_factory=lambda: object()) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                port = server.server_address[1]
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request("GET", "/local/capabilities", headers={"Host": f"127.0.0.1:{port}"})
                response = conn.getresponse()
                self.assertEqual(response.status, 200)
                capability = json.loads(response.read())
                self.assertTrue(capability["loopback_only"])
                headers = {"Host": f"127.0.0.1:{port}",
                    "Origin": "https://remote.example",
                    "X-ALMAS-CSRF": capability["csrf_token"],
                    "Content-Type": "application/json"}
                wire = json.dumps(request()).encode()
                conn.request("POST", "/local/analyze", body=wire, headers=headers)
                response = conn.getresponse()
                self.assertEqual(response.status, 403)
                self.assertNotIn("birth_date", response.read().decode())
                headers["Origin"] = f"http://127.0.0.1:{port}"
                headers["X-ALMAS-CSRF"] = "forged"
                conn.request("POST", "/local/analyze", body=wire, headers=headers)
                response = conn.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
                conn.close()
            finally:
                server.shutdown()
                worker.join(timeout=3)

if __name__ == "__main__":
    unittest.main()
