"""Synthetic-only, offline canonical → M30 → M31 demonstration.

This deliberately imports the repository's PUBLIC SYNTHETIC TEST FIXTURE.
Not a service for user-submitted analyses, natal details, or private data.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"
WEB = ROOT / "apps" / "almas-web-preview"
for directory in (str(TESTS), str(WEB)):
    if directory not in sys.path:
        sys.path.insert(0, directory)

from test_canonical_schema_validation import valid_canonical_analysis  # noqa: E402
from schema_gate import build_validator, validate_document  # noqa: E402
from almas_tfa.module_contract import ModuleContext, ExecutionStatus  # noqa: E402
from almas_tfa.report_gate_handlers import m30_report_gate  # noqa: E402
from almas_tfa.report_model_handlers import m31_report  # noqa: E402

KIND = "ALMAS_SYNTHETIC_CANONICAL_GATE_V1"


def _fingerprint(obj: object) -> str:
    wire = json.dumps(
        obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return sha256(wire).hexdigest()


def _ctx(name: str, raw: dict, snapshot: dict) -> ModuleContext:
    return ModuleContext(
        module_id=name,
        module_name="synthetic gate demonstration",
        mode="FULL",
        raw_input=raw,
        canonical_snapshot=snapshot,
        prior_results={},
    )


def evaluate_synthetic_canonical() -> dict:
    canonical = valid_canonical_analysis()  # no user-controlled input
    source = deepcopy(canonical)
    source_digest = _fingerprint(source)

    validator = build_validator(ROOT, "canonical-analysis.schema.json")
    if validate_document(validator, canonical):
        raise ValueError("Synthetic canonical does not pass authoritative schema")

    gate_run = m30_report_gate(_ctx("M30", {"canonical_analysis": canonical}, {}))
    if gate_run.status is not ExecutionStatus.COMPLETED:
        raise ValueError("M30 execution incomplete")
    gate = dict(gate_run.payload)
    gate_validator = build_validator(ROOT, "report-gate-output.schema.json")
    if validate_document(gate_validator, gate):
        raise ValueError("M30 schema check failed")
    if gate["state"] not in ("PARTIAL", "READY") or gate["reportable"] is not True:
        raise ValueError("Synthetic M30 not reportable")
    if gate.get("canonical_fingerprint") != source_digest:
        raise ValueError("M30 fingerprint does not match original canonical")

    attached = gate_run.canonical_updates.get("canonical_analysis")
    if attached is None or attached != canonical:
        raise ValueError("M30 canonical snapshot mismatch")
    doc_run = m31_report(
        _ctx("M31", {}, {"canonical_analysis": attached, "report_gate": gate})
    )
    if doc_run.status is not ExecutionStatus.COMPLETED:
        raise ValueError("M31 execution incomplete")
    model = dict(doc_run.payload)
    document_validator = build_validator(ROOT, "report-document-model.schema.json")
    if validate_document(document_validator, model):
        raise ValueError("M31 schema check failed")
    if (
        model.get("canonical_fingerprint") != source_digest
        or model.get("canonical_fingerprint_verified") is not True
        or model.get("canonical_values_embedded") is not False
        or model.get("canonical_values_mutated") is not False
        or model.get("prose_generated") is not False
        or model.get("report_state") != gate["state"]
    ):
        raise ValueError("M31 invariants violated")
    if canonical != source or _fingerprint(canonical) != source_digest:
        raise ValueError("Canonical changed during M30/M31 evaluation")

    # Deliberately return only a non-sensitive status summary. No
    # canonical values, natal details, documentary content, or prose.
    return {
        "kind": KIND,
        "synthetic": True,
        "schema_validation": "PASS",
        "m30_executed": True,
        "m31_executed": True,
        "canonical_returned": False,
        "canonical_fingerprint": source_digest,
        "m30": {
            "state": gate["state"],
            "reportable": gate["reportable"],
            "canonical_values_mutated": False,
            "execution_trace_state": gate["execution_trace_state"],
            "degradation_reasons": gate["degradation_reasons"],
        },
        "m31": {
            "report_state": model["report_state"],
            "canonical_fingerprint_verified": True,
            "canonical_values_embedded": False,
            "prose_generated": False,
            "section_ids": [s["section_id"] for s in model["sections"]],
            "partial_disclosure_required": model["partial_disclosure_required"],
        },
        "limitations": [
            "Fixture sintético del repositorio, sin datos personales.",
            "La conformidad técnica no demuestra la validez empírica o metafísica.",
            "El estado PARTIAL se conserva cuando falta la traza M00–M29.",
            "Atacires permanece SHADOW/NO-GO.",
        ],
    }
