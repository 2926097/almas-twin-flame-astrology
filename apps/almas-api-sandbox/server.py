"""ALMAS isolated demonstration API.

Read-only, synthetic input ONLY. Authenticated before any ALMAS execution.
The output of analyze_precomputed is NOT canonical_analysis and never passes M30.
"""
from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "examples" / "precomputed-pillars.json"
EXPECTED_KIND = "ALMAS_SYNTHETIC_ENGINE_RESULT_V1"


def compute_synthetic():
    from almas_tfa.analysis import analyze_precomputed

    with FIXTURE.open("r", encoding="utf-8") as handle:
        fixture = json.load(handle)
    result = analyze_precomputed(fixture)
    # No external mutable input, no persisting results, no natal or identity data.
    if result.get("input_mode") != "PRECOMPUTED_PILLARS":
        raise RuntimeError("Unexpected ALMAS output mode")
    return {
        "kind": EXPECTED_KIND,
        "synthetic": True,
        "canonical_analysis": False,
        "m30_executed": False,
        "fixture": "examples/precomputed-pillars.json",
        "engine_result": result,
        "limitations": [
            "Demostración sintética sin astronomía ni documentos privados.",
            "No es un canonical_analysis ni valida M30/M31.",
            "No prueba identidad de pareja, exclusividad ni verdad metafísica.",
            "Atacires permanece desactivado en SHADOW / NO-GO.",
        ],
    }


def dispatch(method: str, target: str, authorization: str | None, expected_key: str, engine=compute_synthetic, canonical_engine=None):
    """Return (HTTP status, JSON payload). No user data is accepted."""
    if method != "GET":
        return 405, {"error": "METHOD_NOT_ALLOWED"}
    parts = urlsplit(target)
    if parts.query or parts.fragment or parts.scheme or parts.netloc:
        return 404, {"error": "NOT_FOUND"}
    if parts.path == "/_health":
        return 200, {"status": "ok", "scope": "synthetic_only"}
    if parts.path not in ("/v1/synthetic", "/v1/canonical-demo"):
        return 404, {"error": "NOT_FOUND"}
    if not expected_key or len(expected_key) < 32:
        return 503, {"error": "SERVICE_NOT_CONFIGURED"}
    supplied = authorization or ""
    if not hmac.compare_digest(supplied.encode("utf-8"), ("Bearer " + expected_key).encode("utf-8")):
        return 401, {"error": "UNAUTHORIZED"}
    if parts.path == "/v1/canonical-demo":
        if canonical_engine is None:
            from canonical_demo import evaluate_synthetic_canonical
            canonical_engine = evaluate_synthetic_canonical
        return 200, canonical_engine()
    return 200, engine()


class Handler(BaseHTTPRequestHandler):
    server_version = "ALMAS-Sandbox"
    sys_version = ""

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def do_DELETE(self):
        self._handle("DELETE")

    def _handle(self, method):
        try:
            code, body = dispatch(
                method, self.path, self.headers.get("Authorization"),
                os.environ.get("ALMAS_API_SHARED_SECRET", ""),
            )
        except Exception:
            # Never log canonical, token, user-supplied values or traces.
            code, body = 503, {"error": "ENGINE_UNAVAILABLE"}
        wire = json.dumps(body, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(wire)))
        self.end_headers()
        self.wfile.write(wire)

    def log_message(self, format, *args):
        # Do not log URL paths or authorization or IP addresses.
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
