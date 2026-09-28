from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

from almas_tfa.canonical_assembly import assemble_canonical_analysis
from test_canonical_assembly import canonical_base, prior_all


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"


def local_schema_registry() -> Registry:
    registry = Registry()
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        with path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        schema_id = schema.get("$id")
        if isinstance(schema_id, str) and schema_id:
            registry = registry.with_resource(
                schema_id,
                Resource.from_contents(schema),
            )
    return registry


def canonical_validator() -> Draft202012Validator:
    with (SCHEMA_DIR / "canonical-analysis.schema.json").open(
        "r",
        encoding="utf-8",
    ) as handle:
        schema = json.load(handle)
    return Draft202012Validator(
        schema,
        registry=local_schema_registry(),
    )


def valid_canonical_analysis() -> dict:
    result = assemble_canonical_analysis(
        canonical_base(),
        prior_all(),
    )
    if result.get("state") != "EVALUABLE":
        raise AssertionError("Synthetic canonical assembly must be evaluable.")
    return result["canonical_analysis"]


class CanonicalAnalysisSchemaValidationTests(unittest.TestCase):
    def setUp(self):
        self.validator = canonical_validator()

    def test_m30_synthetic_output_validates_against_canonical_schema(self):
        self.validator.validate(valid_canonical_analysis())

    def test_unknown_root_namespace_is_rejected(self):
        payload = valid_canonical_analysis()
        payload["unexpected_namespace"] = {}
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_unexpected_model_field_is_rejected(self):
        payload = valid_canonical_analysis()
        payload["models"]["AF"]["unexpected"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_incomplete_production_astronomy_provenance_is_rejected(self):
        payload = valid_canonical_analysis()
        payload["astronomy_backend"] = {
            "state": "AVAILABLE",
            "backend_id": "MOIRA_JPL_SPK",
            "backend_version": "6.8.2",
            "provenance_state": "DECLARED",
            "provenance": {
                "policy_id": "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1"
            },
        }
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_counterevidence_state_rejects_map_when_ice_not_evaluable(self):
        payload = valid_canonical_analysis()
        payload["counterevidence_state"]["ice_evaluable"] = False
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_model_rejects_numeric_ice_when_state_not_evaluable(self):
        payload = valid_canonical_analysis()
        payload["models"]["AF"]["ice_state"] = "NOT_EVALUABLE"
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)


if __name__ == "__main__":
    unittest.main()
