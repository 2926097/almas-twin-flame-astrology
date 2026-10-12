"""Loopback-only ALMAS relational engine. Not deployed in Vercel or Render.

The same-origin browser sends births only to a locally running Python instance.
No persistence, telemetry, public bindings or remote personal-data endpoint.
Requires explicitly pinned Moira/JPL kernel and official M00-M31 manifest.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from math import isfinite
from pathlib import Path
import secrets
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parent / "public"
MANIFEST = REPO_ROOT / "manifests" / "analysis-pipeline-manifest.json"
POLICY_PRESET = "ALMAS_RELATIONAL_STRICT_RESEARCH_V1"
REQUEST_KEYS = frozenset(("format", "type", "execution_state", "public_version",
    "analysis_profile", "analysis_policy_profile", "subjects", "events"))
SUBJECT_KEYS = frozenset(("id", "display_name", "birth_date", "birth_time",
    "time_reliability", "timezone", "latitude", "longitude"))
ALLOWED_ASSETS = frozenset(("index.html", "app.mjs", "validator.mjs",
    "local-inspection.mjs", "evidence-graph.mjs", "astrology-view.mjs",
    "report-view.mjs", "json-lexical-digest.mjs", "full-schema-validator.mjs",
    "birth-request.mjs", "birth-ui.mjs", "birth-geocoding.mjs", "symbolic-reading.mjs"))
MAX_REQUEST_BYTES = 64 * 1024


def strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def _validate_birth(subject: Mapping[str, Any], expected: str) -> None:
    if not isinstance(subject, dict) or set(subject) - SUBJECT_KEYS:
        raise ValueError("SUBJECT_FIELDS_INVALID")
    if subject.get("id") != expected:
        raise ValueError("SUBJECT_IDS_MUST_BE_A_B")
    raw_date = subject.get("birth_date")
    if not isinstance(raw_date, str):
        raise ValueError("BIRTH_DATE_REQUIRED")
    try:
        parsed = date.fromisoformat(raw_date)
    except ValueError as exc:
        raise ValueError("INVALID_BIRTH_DATE") from exc
    if parsed.isoformat() != raw_date or not 1600 <= parsed.year <= 2200:
        raise ValueError("INVALID_BIRTH_DATE")
    quality = subject.get("time_reliability")
    if quality not in ("A", "B", "C", "D"):
        raise ValueError("TIME_RELIABILITY_REQUIRED")
    for key, lower, upper in (("latitude", -90, 90), ("longitude", -180, 180)):
        x = subject.get(key)
        if isinstance(x, bool) or not isinstance(x, (float, int)) or not isfinite(x) or not lower <= x <= upper:
            raise ValueError("INVALID_" + key.upper())
    birth_time = subject.get("birth_time")
    if not birth_time:
        if quality in ("A", "B") or "timezone" in subject:
            raise ValueError("TIMED_BIRTH_REQUIRED_OR_TIMEZONE_ORPHAN")
        return
    if not isinstance(birth_time, str) or len(birth_time) != 5:
        raise ValueError("INVALID_BIRTH_TIME")
    try:
        naive = datetime.fromisoformat(raw_date + "T" + birth_time)
    except ValueError as exc:
        raise ValueError("INVALID_BIRTH_TIME") from exc
    if naive.strftime("%H:%M") != birth_time:
        raise ValueError("INVALID_BIRTH_TIME")
    tz_name = subject.get("timezone")
    if not isinstance(tz_name, str) or not tz_name:
        raise ValueError("IANA_TIMEZONE_REQUIRED")
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("IANA_TIMEZONE_UNKNOWN") from exc
    instants = set()
    for fold in (0, 1):
        utc = naive.replace(tzinfo=tz, fold=fold).astimezone(timezone.utc)
        if utc.astimezone(tz).replace(tzinfo=None) == naive:
            instants.add(utc)
    if len(instants) != 1:
        raise ValueError("DST_TIME_NONEXISTENT_OR_AMBIGUOUS")


def validate_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict) or set(request) != REQUEST_KEYS:
        raise ValueError("REQUEST_FIELDS_INVALID")
    if request.get("format") != "ALMAS_WORK_REQUEST" or request.get("type") != "RELATIONAL":
        raise ValueError("REQUEST_KIND_INVALID")
    if request.get("execution_state") != "REQUEST_ONLY" or request.get("public_version") != "1.26.0":
        raise ValueError("REQUEST_VERSION_INVALID")
    if request.get("analysis_policy_profile") != POLICY_PRESET:
        raise ValueError("EXPLICIT_PRESET_REQUIRED")
    if request.get("analysis_profile") not in (
        "FULL_ASTROLOGY", "FULL_MULTIDISCIPLINARY", "TEMPORAL", "SOUL_CONTRACT"
    ):
        raise ValueError("ANALYSIS_PROFILE_INVALID")
    if request.get("events") != []:
        raise ValueError("EVENTS_NOT_AUTHORIZED_IN_LOCAL_INTAKE")
    subjects = request.get("subjects")
    if not isinstance(subjects, list) or len(subjects) != 2:
        raise ValueError("TWO_SUBJECTS_REQUIRED")
    for item, sid in zip(subjects, ("A", "B")):
        _validate_birth(item, sid)
    return request


def process_locally(request: dict[str, Any], *, backend_factory: Callable[[], Any] | None = None,
                    runner: Callable[..., Any] | None = None,
                    schema_check: Callable[[str, Mapping[str, Any]], None] | None = None) -> dict[str, Any]:
    """Execute only official modules; fail closed on invalid official outputs."""
    validate_request(request)
    from almas_tfa.relational_request_pipeline import assess_relational_work_request
    from almas_tfa.relational_execution import execute_relational_work_request
    from almas_tfa.interpretive_atlas import build_interpretive_atlas
    assessment = assess_relational_work_request(request)
    if not assessment["ready_for_raw_input"]:
        raise ValueError("POLICY_NOT_READY")
    if backend_factory is None:
        raise RuntimeError("LOCAL_BACKEND_NOT_CONFIGURED")
    backend = backend_factory()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    run = (runner or execute_relational_work_request)(
        request, manifest, astrology_backend=backend, davison_backend=backend, stop_on_failure=False)
    receipt = run["execution_receipt"]
    module_statuses = receipt["module_statuses"]
    if receipt["failed_modules"]:
        return {"state": "BLOCKED", "reason": "MODULE_FAILURE",
                "module_statuses": module_statuses, "canonical_analysis": None}
    canonical = run["canonical_analysis"]
    if not isinstance(canonical, dict):
        return {"state": "NOT_EVALUABLE", "reason": "M30_CANONICAL_UNAVAILABLE",
                "module_statuses": module_statuses, "canonical_analysis": None}
    assembled = run["orchestration_run"]["canonical"]
    gate, model = assembled.get("report_gate"), assembled.get("report_document_model")
    if not isinstance(gate, dict) or not isinstance(model, dict):
        raise ValueError("OFFICIAL_M30_M31_MISSING")
    if schema_check is None:
        import sys
        web_dir = str(Path(__file__).resolve().parent)
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)
        from schema_gate import build_validator, validate_document

        def schema_check(name: str, value: Mapping[str, Any]) -> None:
            errors = validate_document(build_validator(REPO_ROOT, name), value)
            if errors:
                raise ValueError("OFFICIAL_SCHEMA_INVALID:" + name)
    schema_check("canonical-analysis.schema.json", canonical)
    schema_check("report-gate-output.schema.json", gate)
    schema_check("report-document-model.schema.json", model)
    fingerprint = sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()
    if (gate.get("canonical_fingerprint") != fingerprint
        or model.get("canonical_fingerprint") != fingerprint
        or model.get("canonical_fingerprint_verified") is not True
        or model.get("canonical_values_mutated") is not False
        or model.get("canonical_values_embedded") is not False
        or model.get("prose_generated") is not False
        or gate.get("state") not in ("READY", "PARTIAL")
        or not gate.get("reportable")
        or model.get("report_state") != gate.get("state")):
        raise ValueError("M30_M31_FINGERPRINT_OR_REPORT_GATE_INVALID")
    atlas = build_interpretive_atlas(canonical)
    if atlas["canonical_fingerprint"] != fingerprint:
        raise ValueError("ATLAS_FINGERPRINT_MISMATCH")
    return {
        "state": gate["state"], "canonical_analysis": canonical,
        "m30": gate, "m31": model, "atlas": atlas,
        "assessment": assessment, "module_statuses": module_statuses,
        "limitations": ["Interpretación editorial no generada; M31 es documental.",
            "La lectura astrológica no demuestra categorías metafísicas.",
            "Atacires SHADOW/NO-GO: sin promoción a puntuaciones."],
    }


class LocalEngineServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, *, backend_factory, runner=None, schema_check=None):
        super().__init__(address, LocalHandler)
        if self.server_address[0] not in ("127.0.0.1", "::1"):
            self.server_close()
            raise ValueError("LOOPBACK_REQUIRED")
        self.csrf_token = secrets.token_urlsafe(32)
        self.backend_factory = backend_factory
        self.runner = runner
        self.schema_check = schema_check


class LocalHandler(BaseHTTPRequestHandler):
    server_version = "ALMAS-Local"
    sys_version = ""

    def log_message(self, *_args):
        pass

    def _headers(self, code: int, ctype: str, length: int) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
            " connect-src 'self' https://geocoding-api.open-meteo.com;"
            " object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()

    def _send(self, code: int, payload: Mapping[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self._headers(code, "application/json; charset=utf-8", len(encoded))
        self.wfile.write(encoded)

    def _same_origin(self) -> bool:
        host = self.headers.get("Host", "")
        return host == f"127.0.0.1:{self.server.server_address[1]}" and self.headers.get("Origin", "") == f"http://{host}"

    def do_GET(self):
        parsed = urlsplit(self.path)
        host = self.headers.get("Host", "")
        if host != f"127.0.0.1:{self.server.server_address[1]}" or parsed.query or parsed.fragment:
            self._send(403, {"error": "LOCAL_HOST_REQUIRED"})
            return
        if parsed.path == "/local/capabilities":
            self._send(200, {"kind": "ALMAS_LOCAL_ENGINE_V1", "private": True,
                "loopback_only": True, "csrf_token": self.server.csrf_token,
                "backend_configured": self.server.backend_factory is not None})
            return
        asset = "index.html" if parsed.path == "/" else parsed.path.removeprefix("/")
        if asset not in ALLOWED_ASSETS or not (STATIC / asset).is_file():
            self._send(404, {"error": "NOT_FOUND"})
            return
        data = (STATIC / asset).read_bytes()
        ctype = "text/html; charset=utf-8" if asset.endswith(".html") else "text/javascript; charset=utf-8"
        self._headers(200, ctype, len(data))
        self.wfile.write(data)

    def do_POST(self):
        if urlsplit(self.path).path != "/local/analyze":
            self._send(404, {"error": "NOT_FOUND"})
            return
        if not self._same_origin() or self.headers.get("X-ALMAS-CSRF") != self.server.csrf_token:
            self._send(403, {"error": "LOCAL_ORIGIN_OR_CSRF_REQUIRED"})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self._send(415, {"error": "JSON_ONLY"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length < 2 or length > MAX_REQUEST_BYTES or self.headers.get("Transfer-Encoding"):
            self._send(413, {"error": "REQUEST_SIZE_OR_FRAMING_INVALID"})
            return
        raw = self.rfile.read(length)
        try:
            request = json.loads(raw.decode("utf-8"), object_pairs_hook=strict_object_pairs,
                parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
            result = process_locally(request, backend_factory=self.server.backend_factory,
                runner=self.server.runner, schema_check=self.server.schema_check)
        except (ValueError, TypeError) as exc:
            # Only fixed error-code tokens: never echo any raw personal input.
            reason = str(exc)
            safe = reason if reason.isupper() and all(c.isupper() or c.isdigit() or c in "_:" for c in reason) else "INVALID_REQUEST_OR_ENGINE_RESULT"
            self._send(422, {"error": safe[:120]})
            return
        except Exception:
            self._send(503, {"error": "LOCAL_ENGINE_UNAVAILABLE"})
            return
        self._send(200, result)

    def do_OPTIONS(self):
        self._send(405, {"error": "METHOD_NOT_ALLOWED"})


def main() -> int:
    parser = argparse.ArgumentParser(description="ALMAS private loopback-only Web engine")
    parser.add_argument("--kernel-path", type=Path, required=True)
    parser.add_argument("--kernel-sha256", required=True)
    parser.add_argument("--kernel-family", choices=("DE430", "DE440", "DE441"), required=True)
    parser.add_argument("--house-system", required=True)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--preflight-only", action="store_true",
        help="Check kernel SHA, provider version and Placidus policy without starting the server")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be 1024..65535")
    from local_astronomy_preflight import assess_local_astronomy_runtime, LocalAstronomyNotReady
    try:
        receipt = assess_local_astronomy_runtime(args.kernel_path, args.kernel_sha256,
            args.kernel_family, args.house_system)
    except LocalAstronomyNotReady as exc:
        parser.error("Private astronomy runtime NOT READY: " + str(exc))
    if args.preflight_only:
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
        return 0
    if not STATIC.joinpath("index.html").is_file():
        parser.error("Run 'npm run build' in apps/almas-web-preview first")
    from almas_tfa.production_astronomy import MoiraBackendConfig, MoiraProductionBackend
    config = MoiraBackendConfig(kernel_path=str(args.kernel_path),
        kernel_sha256=args.kernel_sha256, kernel_family=args.kernel_family,
        house_system=args.house_system)
    def backend_factory():
        return MoiraProductionBackend(config)
    with LocalEngineServer(("127.0.0.1", args.port), backend_factory=backend_factory) as server:
        print(f"ALMAS local-only: http://127.0.0.1:{args.port}/")
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
