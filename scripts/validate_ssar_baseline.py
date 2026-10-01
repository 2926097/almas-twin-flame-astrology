#!/usr/bin/env python3
"""Captura y compara salidas legacy; no ejecuta ni habilita SSAR."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE_COMMIT = "e0e8db8c2aab7484ffaf628a8c24f2dbb18a3e09"
DEFAULT_BASELINE = ROOT / "reference/ssar-baseline-1.24.1.json"
CORE_NAMESPACES = (
    "independent_roots", "pillars", "structural_model_indices",
    "model_attributions", "pairwise_idd", "robustness_index",
    "temporal_activation", "counterevidence",
)
CANONICAL_FIELDS = (
    "models", "indices", "pairwise_idd", "ontology", "evidence",
    "robustness", "counterevidence", "counterevidence_state", "temporal",
)
PROTECTED_FILES = (
    "src/almas_tfa/core.py",
    "src/almas_tfa/quantitative_contracts.py",
    "src/almas_tfa/root_strengths.py",
    "src/almas_tfa/pillar_attribution.py",
    "src/almas_tfa/model_attribution.py",
    "src/almas_tfa/counterevidence_handlers.py",
    "src/almas_tfa/robustness_index_handlers.py",
    "src/almas_tfa/data/model-attribution-policy.json",
    "src/almas_tfa/data/technique-dependency-registry.json",
    "src/almas_tfa/data/declared-orb-contract-policy.json",
    "src/almas_tfa/data/structural-loading-policy.json",
    "src/almas_tfa/data/root-strength-policy.json",
    "src/almas_tfa/data/root-pillar-attribution-policy.json",
)


def collect_outputs() -> dict:
    from almas_tfa.analysis import analyze_precomputed
    from almas_tfa.orchestrator import Orchestrator

    sys.path.insert(0, str(ROOT / "tests"))
    from test_full_pipeline import TestFullPipelineSynthetic

    # Se reutiliza la construcción pública del fixture, sin serializar datos natales.
    # La captura termina antes de assertions de informe que podrán evolucionar.
    class CapturedFixture(Exception):
        pass

    captured = []
    original_run = Orchestrator.run

    def capture(self, *args, **kwargs):
        result = original_run(self, *args, **kwargs)
        captured.append(result)
        raise CapturedFixture

    case = TestFullPipelineSynthetic("test_m00_m31_complete_with_explicit_inputs")
    with patch.object(Orchestrator, "run", capture):
        try:
            case.test_m00_m31_complete_with_explicit_inputs()
        except CapturedFixture:
            pass
    if len(captured) != 1:
        raise RuntimeError("El fixture debe producir exactamente una ejecución.")
    run = captured[0]
    canonical = run.canonical["canonical_analysis"]
    if any(result.status.value != "COMPLETED" for result in run.results.values()):
        raise RuntimeError("La ejecución de referencia tiene módulos incompletos.")
    if any(key not in run.canonical for key in CORE_NAMESPACES):
        raise RuntimeError("Falta una salida core de referencia.")
    full = {
        "fixture_ref": "tests/test_full_pipeline.py::test_m00_m31_complete_with_explicit_inputs",
        "module_statuses": {
            key: result.status.value for key, result in sorted(run.results.items())
        },
        "core_namespaces": {key: run.canonical[key] for key in CORE_NAMESPACES},
        "canonical_core": {key: canonical[key] for key in CANONICAL_FIELDS},
    }
    payload = json.loads((ROOT / "examples/precomputed-pillars.json").read_text())
    precomputed = analyze_precomputed(payload)
    legacy_metadata = {"precomputed_public_version": precomputed.pop("public_version")}
    missing_ice = analyze_precomputed({"pillars": dict(payload["pillars"])})
    missing_ice.pop("public_version")
    return {
        "outputs": {
            "full_pipeline": full,
            "precomputed_complete": precomputed,
            "precomputed_missing_ice": missing_ice,
        },
        "legacy_metadata": legacy_metadata,
    }


def artifact() -> dict:
    return {
        "baseline_id": "SSAR_BASELINE_ALMAS_1.24.1_V1",
        "base_commit": BASE_COMMIT,
        "comparison": "EXACT_DETERMINISTIC_VALUES",
        "astronomical_tolerance": None,
        "fixture_kind": "EXISTING_SYNTHETIC",
        "production_ephemerides_executed": False,
        "external_validation_status": "NOT_PERFORMED",
        "protected_file_sha256": {
            path: sha256((ROOT / path).read_bytes()).hexdigest()
            for path in PROTECTED_FILES
        },
        **collect_outputs(),
    }


def first_difference(expected, actual, path="outputs") -> str | None:
    if type(expected) is not type(actual):
        return path + ": tipo diferente"
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            return path + ": claves diferentes"
        for key in expected:
            mismatch = first_difference(expected[key], actual[key], path + "." + key)
            if mismatch:
                return mismatch
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            return path + ": longitud diferente"
        for index, (a, b) in enumerate(zip(expected, actual)):
            mismatch = first_difference(a, b, f"{path}[{index}]")
            if mismatch:
                return mismatch
    elif expected != actual:
        return path + ": valor diferente"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--write", action="store_true", help="Crear una referencia nueva; nunca sobrescribir.")
    args = parser.parse_args()
    if args.write and args.baseline.exists():
        parser.error("La referencia ya existe; su sobrescritura está prohibida.")
    actual = artifact()
    if args.write:
        with args.baseline.open("x", encoding="utf-8") as handle:
            json.dump(actual, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        print("Referencia SSAR creada; SSAR permanece sin implementar.")
        return 0
    expected = json.loads(args.baseline.read_text(encoding="utf-8"))
    mismatch = first_difference(expected["outputs"], actual["outputs"])
    changed = [
        path for path, digest in expected["protected_file_sha256"].items()
        if actual["protected_file_sha256"].get(path) != digest
    ]
    if mismatch or changed:
        print("Regresión SSAR: FAIL", mismatch or "", ", ".join(changed))
        return 1
    if expected["legacy_metadata"] != actual["legacy_metadata"]:
        print("Metadatos legacy diferentes; revisar por separado.")
    print("Regresión SSAR: PASS; salidas deterministas y archivos protegidos idénticos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
