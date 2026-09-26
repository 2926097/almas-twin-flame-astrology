import json
import tempfile
import unittest
from pathlib import Path

from almas_tfa.public_data_guard import (
    audit_public_repository,
    validate_public_artifact_metadata,
    validate_public_artifact_payload,
)


def synthetic_artifact(path="examples/x.json"):
    return {
        "path": path,
        "classification": "SYNTHETIC",
        "purpose": "TEST",
        "contains_real_person_data": False,
        "contains_nonpublic_material": False,
        "derived_from_private_case": False,
        "reversible_from_private_case": False,
        "independently_verifiable": False,
        "public_source_refs": [],
    }


class TestPublicDataGuard(unittest.TestCase):

    def test_synthetic_metadata_passes(self):
        validate_public_artifact_metadata(synthetic_artifact())

    def test_private_classification_is_rejected(self):
        artifact = synthetic_artifact()
        artifact["classification"] = "PRIVATE_CASE"
        with self.assertRaises(ValueError):
            validate_public_artifact_metadata(artifact)

    def test_synthetic_cannot_contain_real_person_data(self):
        artifact = synthetic_artifact()
        artifact["contains_real_person_data"] = True
        with self.assertRaises(ValueError):
            validate_public_artifact_metadata(artifact)

    def test_synthetic_cannot_derive_from_private_case(self):
        artifact = synthetic_artifact()
        artifact["derived_from_private_case"] = True
        with self.assertRaises(ValueError):
            validate_public_artifact_metadata(artifact)

    def test_public_verifiable_requires_sources(self):
        artifact = synthetic_artifact("public_cases/x.json")
        artifact.update(
            {
                "classification": "PUBLIC_VERIFIABLE",
                "contains_real_person_data": True,
                "independently_verifiable": True,
            }
        )
        with self.assertRaises(ValueError):
            validate_public_artifact_metadata(artifact)

        artifact["public_source_refs"] = ["PUBLIC-SOURCE-1"]
        validate_public_artifact_metadata(artifact)

    def test_private_payload_key_is_rejected_recursively(self):
        payload = {
            "case": {
                "events": [
                    {"private_message": "dummy synthetic sentinel"}
                ]
            }
        }
        with self.assertRaises(ValueError):
            validate_public_artifact_payload(payload)

    def test_repository_audit_rejects_unregistered_json(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "examples").mkdir()
            (root / "public_cases").mkdir()
            (root / "validation/holdouts").mkdir(parents=True)

            (root / "examples/x.json").write_text(
                json.dumps({"synthetic": True}),
                encoding="utf-8",
            )
            (root / "examples/manifest.json").write_text(
                json.dumps(
                    {
                        "manifest_version": "1.0.0",
                        "policy_id": "ALMAS_PUBLIC_DATA_ISOLATION_V1",
                        "scope": "examples",
                        "root": "examples",
                        "allowed_classifications": ["SYNTHETIC"],
                        "artifacts": [],
                    }
                ),
                encoding="utf-8",
            )
            for path, scope, allowed in (
                (
                    root / "public_cases/manifest.json",
                    "public_cases",
                    ["PUBLIC_VERIFIABLE"],
                ),
                (
                    root / "validation/holdouts/manifest.json",
                    "public_holdouts",
                    [
                        "SYNTHETIC",
                        "PUBLIC_VERIFIABLE",
                        "PUBLIC_METADATA_ONLY",
                    ],
                ),
            ):
                path.write_text(
                    json.dumps(
                        {
                            "manifest_version": "1.0.0",
                            "policy_id": "ALMAS_PUBLIC_DATA_ISOLATION_V1",
                            "scope": scope,
                            "root": str(path.parent.relative_to(root)).replace("\\", "/"),
                            "allowed_classifications": allowed,
                            "artifacts": [],
                        }
                    ),
                    encoding="utf-8",
                )

            with self.assertRaises(ValueError):
                audit_public_repository(root)

    def test_repository_audit_rejects_private_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "private_cases").mkdir()
            with self.assertRaises(ValueError):
                audit_public_repository(root)

    def test_current_repository_passes_public_data_audit(self):
        root = Path(__file__).resolve().parents[1]
        result = audit_public_repository(root)
        self.assertEqual(
            result["policy_id"],
            "ALMAS_PUBLIC_DATA_ISOLATION_V1",
        )
        self.assertEqual(
            result["scopes"]["examples"]["artifact_count"],
            18,
        )
        self.assertEqual(
            result["scopes"]["public_cases"]["artifact_count"],
            0,
        )
        self.assertEqual(
            result["scopes"]["public_holdouts"]["artifact_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
