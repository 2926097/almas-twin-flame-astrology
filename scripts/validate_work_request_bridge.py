#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from almas_tfa.work_request import (
    RELATIONAL_ORB_PRESET_ID,
    WorkRequestError,
    assess_work_request,
    build_raw_input_from_work_request,
)


def _version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def _envelope() -> dict:
    return {
        "case_title": "Synthetic bridge validation",
        "request": {
            "format": "ALMAS_WORK_REQUEST",
            "public_version": _version(),
            "type": "RELATIONAL",
            "analysis_profile": "FULL_ASTROLOGY",
            "subjects": [
                {
                    "id": "SYNTH-A",
                    "birth_date": "1977-03-20",
                    "birth_time": "17:45",
                    "timezone": "Europe/Madrid",
                    "place": "Synthetic A",
                    "latitude": 41.65,
                    "longitude": -0.88,
                    "time_reliability": "D",
                },
                {
                    "id": "SYNTH-B",
                    "birth_date": "1991-05-23",
                    "birth_time": "04:15",
                    "timezone": "America/Santo_Domingo",
                    "place": "Synthetic B",
                    "latitude": 18.45,
                    "longitude": -69.31,
                    "time_reliability": "B",
                },
            ],
            "analysis_policies": {
                "schema_version": "1.0.0",
                "policy_bundle_id": RELATIONAL_ORB_PRESET_ID,
                "preset_ref": RELATIONAL_ORB_PRESET_ID,
            },
            "situation_location": {
                "latitude": "41.65606",
                "longitude": "-0.87734",
                "timezone": "Europe/Madrid",
            },
            "events": [],
            "execution_state": "REQUEST_ONLY",
        },
        "chronology": [],
    }


def main() -> int:
    version = _version()
    with patch("almas_tfa.work_request.metadata.version", return_value=version):
        envelope = _envelope()
        assessment = assess_work_request(envelope)
        if assessment["execution_ready"] is not True:
            raise AssertionError(assessment)
        if assessment["implicit_orbs_used"] is not False:
            raise AssertionError("El preset no puede marcar orbes implícitos.")
        if assessment["case_fitting_used"] is not False:
            raise AssertionError("El preset no puede marcar case fitting.")
        if assessment["preset_ref"] != RELATIONAL_ORB_PRESET_ID:
            raise AssertionError("preset_ref no preservado.")

        policies = assessment["analysis_policies"]
        if policies["aspect_policy"]["CONJUNCTION"] != {"angle": 0, "orb": 6}:
            raise AssertionError("Baseline tropical inesperada.")
        if policies["declination_policy"]["parallel_orb"] != 1.0:
            raise AssertionError("Baseline de declinación inesperada.")
        if policies["antiscia_policy"]["antiscia_orb"] != 1.0:
            raise AssertionError("Baseline de antiscios inesperada.")
        if set(policies["draconic_aspect_policy"]) != {
            "CONJUNCTION", "OPPOSITION"
        }:
            raise AssertionError("La baseline dracónica debe ser estricta.")

        raw = build_raw_input_from_work_request(envelope)
        if raw["analysis_policy_bundle"]["preset_epistemic_class"] != "E_PROJECT_POLICY":
            raise AssertionError("El preset debe conservar clase E.")
        if raw["analysis_policy_bundle"]["preset_external_validation_status"] != "NOT_PERFORMED":
            raise AssertionError("El preset no puede simular validación externa.")
        if not isinstance(raw["situation_location"]["latitude"], float):
            raise AssertionError("La localización debe normalizar coordenadas.")

        incomplete = _envelope()
        incomplete["request"].pop("analysis_policies")
        check = assess_work_request(incomplete)
        if check["execution_ready"] is not False:
            raise AssertionError("Un request sin orbes explícitos debe fallar cerrado.")
        if "aspect_policy" not in check["missing_policies"]:
            raise AssertionError("Debe declararse la ausencia de aspect_policy.")

        overridden = _envelope()
        overridden["request"]["analysis_policies"]["aspect_policy"] = {
            "CONJUNCTION": {"angle": 0, "orb": 9}
        }
        check = assess_work_request(overridden)
        if check["execution_ready"] is not False:
            raise AssertionError("Un preset con override inline debe rechazarse.")
        if not any("no admite overrides inline" in item for item in check["policy_errors"]):
            raise AssertionError("No se trazó el override prohibido.")

        try:
            build_raw_input_from_work_request(incomplete)
        except WorkRequestError:
            pass
        else:
            raise AssertionError("build_raw_input debe fallar cerrado.")

    print("ALMAS work request bridge validation: PASS")
    print(f"Preset: {RELATIONAL_ORB_PRESET_ID}")
    print("Implicit orbs: false")
    print("Case fitting: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
