#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "SKILL.md",
    "CHANGELOG.md",
    "VERSION",
    "VALIDATION_STATUS.md",
    "pyproject.toml",
    "schemas/raw-input.schema.json",
    "schemas/canonical-analysis.schema.json",
    "schemas/precomputed-pillars.schema.json",
    "schemas/precomputed-result.schema.json",
    "manifests/module-manifest.json",
    "manifests/differential-discriminator-registry.json",
    "reference/source-registry.json",
    "src/almas_tfa/core.py",
    "src/almas_tfa/analysis.py",
    "src/almas_tfa/cli.py",
    "tests/INVARIANTS.md",
    "tests/test_core.py",
    "tests/test_analysis.py",
    "examples/precomputed-pillars.json",
    "examples/precomputed-result.json",
]

EXPECTED_STATES = {
    "SUPPORTED",
    "COMPATIBLE",
    "INSUFFICIENT",
    "CONTRADICTED",
    "NOT_EVALUABLE",
}


def fail(msg: str) -> None:
    raise AssertionError(msg)


def load_json(rel: str):
    with (ROOT / rel).open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != "1.0.0":
        fail(f"unexpected VERSION: {version}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    for needle in [
        "version: 1.0.0",
        "IEM",
        "IDD",
        "IRC",
        "IAT",
        "ICC",
        "ICE",
        "SUPPORTED",
        "COMPATIBLE",
        "INSUFFICIENT",
        "CONTRADICTED",
        "NOT_EVALUABLE",
        "canonical_analysis.json",
    ]:
        if needle not in skill:
            fail(f"SKILL.md missing contract token: {needle}")

    if "1.0.0" not in readme:
        fail("README.md does not identify v1.0.0")

    if 'version = "1.0.0"' not in pyproject:
        fail("pyproject.toml version diverges from VERSION")

    if 'almas-score = "almas_tfa.cli:main"' not in pyproject:
        fail("pyproject.toml does not expose almas-score")

    raw_schema = load_json("schemas/raw-input.schema.json")
    canonical_schema = load_json("schemas/canonical-analysis.schema.json")
    precomputed_schema = load_json("schemas/precomputed-pillars.schema.json")
    result_schema = load_json("schemas/precomputed-result.schema.json")
    module_manifest = load_json("manifests/module-manifest.json")
    discriminator_registry = load_json(
        "manifests/differential-discriminator-registry.json"
    )
    source_registry = load_json("reference/source-registry.json")
    example_input = load_json("examples/precomputed-pillars.json")
    example_result = load_json("examples/precomputed-result.json")

    if canonical_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("canonical schema version is not 1.0.0")

    if result_schema.get("properties", {}).get("public_version", {}).get("const") != "1.0.0":
        fail("precomputed result schema version is not 1.0.0")

    modules = module_manifest.get("modules", [])
    ids = [m.get("id") for m in modules]
    expected_ids = [f"M{i:02d}" for i in range(32)]
    if ids != expected_ids:
        fail("module manifest must contain ordered M00..M31 exactly once")

    discriminators = discriminator_registry.get("discriminators", [])
    if not discriminators:
        fail("discriminator registry is empty")

    for d in discriminators:
        if d.get("status") == "VALIDATED" and not d.get("validation_reference"):
            fail(
                f"validated discriminator lacks validation reference: {d.get('id')}"
            )

    if not source_registry.get("entries"):
        fail("source registry is empty")

    model_props = (
        canonical_schema.get("properties", {})
        .get("models", {})
        .get("properties", {})
    )
    if set(model_props) != {"AF", "KA", "AG", "LG"}:
        fail("canonical schema must expose exactly AF, KA, AG, LG model slots")

    for model, spec in model_props.items():
        state_enum = (
            spec.get("properties", {})
            .get("state", {})
            .get("enum", [])
        )
        if set(state_enum) != EXPECTED_STATES:
            fail(f"{model} state enum diverges from normative states")

    subject_items = raw_schema.get("properties", {}).get("subjects", {})
    if subject_items.get("minItems") != 2 or subject_items.get("maxItems") != 2:
        fail("raw input schema must require exactly two subjects")

    pillar_props = (
        precomputed_schema.get("properties", {})
        .get("pillars", {})
        .get("properties", {})
    )
    if set(pillar_props) != {"PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU"}:
        fail("precomputed pillar schema must expose PA/PK/PE/PR/PX/PT/PS/PU")

    if set(example_input.get("pillars", {})) != {
        "PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU"
    }:
        fail("example precomputed input does not cover all public pillars")

    if set(example_result.get("models", {})) != {"AF", "KA", "AG", "LG"}:
        fail("example precomputed result does not contain all four models")

    print("ALMAS public contract validation: PASS")
    print(f"Version: {version}")
    print(f"Modules: {len(modules)}")
    print(f"Discriminators registered: {len(discriminators)}")
    print(f"Source entries: {len(source_registry.get('entries', []))}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ALMAS public contract validation: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
