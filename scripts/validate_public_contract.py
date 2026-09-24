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
    "docs/PUBLICATION_POLICY.md",
    "docs/DUAL_ENGINE_ARCHITECTURE.md",
    "examples/README.md",
    "public_cases/README.md",
    "pyproject.toml",
    "schemas/raw-input.schema.json",
    "schemas/canonical-analysis.schema.json",
    "schemas/precomputed-pillars.schema.json",
    "schemas/precomputed-result.schema.json",
    "schemas/astrology-to-soul-contract.schema.json",
    "schemas/contrato-almico.schema.json",
    "schemas/preincarnation-reconstruction.schema.json",
    "schemas/origin-differential.schema.json",
    "schemas/agreement-motive-differential.schema.json",
    "schemas/role-selection-differential.schema.json",
    "manifests/module-manifest.json",
    "manifests/differential-discriminator-registry.json",
    "manifests/origin-model-registry.json",
    "manifests/origin-discriminator-registry.json",
    "manifests/agreement-motive-registry.json",
    "manifests/role-selection-registry.json",
    "reference/source-registry.json",
    "reference/contrato-almico.md",
    "reference/preincarnation-source-map.json",
    "reference/preincarnation-reconstruction.md",
    "reference/origin-differential.md",
    "reference/agreement-motive-differential.md",
    "reference/role-selection-differential.md",
    "reference/roles-preencarnatorios.md",
    "skills/almas-soul-contract/SKILL.md",
    "skills/almas-soul-contract/VERSION",
    "skills/almas-soul-contract/CHANGELOG.md",
    "src/almas_tfa/core.py",
    "src/almas_tfa/analysis.py",
    "src/almas_tfa/cli.py",
    "tests/INVARIANTS.md",
    "tests/CONTRATO_ALMICO_INVARIANTS.md",
    "tests/PREINCARNATION_RECONSTRUCTION_INVARIANTS.md",
    "tests/ORIGIN_DIFFERENTIAL_INVARIANTS.md",
    "tests/AGREEMENT_MOTIVE_INVARIANTS.md",
    "tests/ROLE_SELECTION_INVARIANTS.md",
    "reference/causa-contractual.md",
    "tests/CAUSA_CONTRACTUAL_INVARIANTS.md",
    "tests/ROLES_PREENCARNATORIOS_INVARIANTS.md",
    "tests/test_core.py",
    "tests/test_analysis.py",
    "examples/precomputed-pillars.json",
    "examples/precomputed-result.json",
    "examples/preincarnation-reconstruction.synthetic.json",
    "examples/origin-differential.synthetic.json",
    "examples/agreement-motive.synthetic.json",
    "examples/role-selection.synthetic.json",
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
    if version != "1.3.1":
        fail(f"unexpected root VERSION: {version}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    for needle in [
        f"version: {version}",
        "Metaphysical research stance",
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
        "Interoperabilidad con ALMAS Contrato Álmico",
    ]:
        if needle not in skill:
            fail(f"SKILL.md missing contract token: {needle}")

    if version not in readme:
        fail(f"README.md does not identify v{version}")

    if f'version = "{version}"' not in pyproject:
        fail("pyproject.toml version diverges from VERSION")

    if 'almas-score = "almas_tfa.cli:main"' not in pyproject:
        fail("pyproject.toml does not expose almas-score")

    publication_policy = (ROOT / "docs/PUBLICATION_POLICY.md").read_text(encoding="utf-8")
    examples_policy = (ROOT / "examples/README.md").read_text(encoding="utf-8")
    public_cases_policy = (ROOT / "public_cases/README.md").read_text(encoding="utf-8")

    if "already public" not in publication_policy:
        fail("publication policy must define the already-public case rule")
    if "synthetic" not in examples_policy.lower():
        fail("examples policy must identify default fixtures as synthetic")
    if "independently verifiable" not in public_cases_policy:
        fail("public case policy must require independent verification")

    soul_skill = (ROOT / "skills/almas-soul-contract/SKILL.md").read_text(encoding="utf-8")
    soul_version = (ROOT / "skills/almas-soul-contract/VERSION").read_text(encoding="utf-8").strip()
    if soul_version != "1.4.0":
        fail(f"unexpected soul-contract VERSION: {soul_version}")
    for needle in [
        "name: almas-soul-contract",
        "version: 1.4.0",
        "ALMAS Soul Contract",
        "método metafísico",
        "A_EN_B",
        "B_EN_A",
        "CAMPO_COMUN",
    ]:
        if needle not in soul_skill:
            fail(f"soul-contract SKILL missing token: {needle}")

    raw_schema = load_json("schemas/raw-input.schema.json")
    canonical_schema = load_json("schemas/canonical-analysis.schema.json")
    precomputed_schema = load_json("schemas/precomputed-pillars.schema.json")
    result_schema = load_json("schemas/precomputed-result.schema.json")
    bridge_schema = load_json("schemas/astrology-to-soul-contract.schema.json")
    preincarnation_schema = load_json("schemas/preincarnation-reconstruction.schema.json")
    origin_schema = load_json("schemas/origin-differential.schema.json")
    origin_registry = load_json("manifests/origin-model-registry.json")
    origin_discriminator_registry = load_json("manifests/origin-discriminator-registry.json")
    origin_example = load_json("examples/origin-differential.synthetic.json")
    agreement_motive_schema = load_json("schemas/agreement-motive-differential.schema.json")
    agreement_motive_registry = load_json("manifests/agreement-motive-registry.json")
    agreement_motive_example = load_json("examples/agreement-motive.synthetic.json")
    role_selection_schema = load_json("schemas/role-selection-differential.schema.json")
    role_selection_registry = load_json("manifests/role-selection-registry.json")
    role_selection_example = load_json("examples/role-selection.synthetic.json")
    module_manifest = load_json("manifests/module-manifest.json")
    discriminator_registry = load_json("manifests/differential-discriminator-registry.json")
    source_registry = load_json("reference/source-registry.json")
    example_input = load_json("examples/precomputed-pillars.json")
    example_result = load_json("examples/precomputed-result.json")
    preincarnation_source_map = load_json("reference/preincarnation-source-map.json")
    preincarnation_example = load_json("examples/preincarnation-reconstruction.synthetic.json")

    if canonical_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("canonical astrology schema contract must remain 1.0.0")

    if result_schema.get("properties", {}).get("public_version", {}).get("const") != version:
        fail("precomputed result public_version diverges from root VERSION")

    if bridge_schema.get("properties", {}).get("bridge_version", {}).get("const") != "1.0.0":
        fail("astrology-to-soul-contract bridge must expose bridge_version 1.0.0")

    if preincarnation_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.3.0":
        fail("preincarnation reconstruction schema must expose schema_version 1.3.0")

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
            fail(f"validated discriminator lacks validation reference: {d.get('id')}")

    if not source_registry.get("entries"):
        fail("source registry is empty")

    expected_preincarnation_stages = {
        "ORIGIN",
        "AGREEMENT_MOTIVE",
        "ROLE_SELECTION",
        "ENCOUNTER_CONDITIONS",
        "INDIVIDUAL_TASKS",
        "COMMON_TASK",
        "CLAUSES",
        "FULFILLMENT_MECHANISMS",
    }
    source_map_stages = set(preincarnation_source_map.get("stages", {}))
    if source_map_stages != expected_preincarnation_stages:
        fail("preincarnation source map must expose exactly eight canonical stages")

    source_ids = {entry.get("id") for entry in source_registry.get("entries", [])}
    for stage_name, stage in preincarnation_source_map.get("stages", {}).items():
        for key in ("primary", "methods", "comparative"):
            for source_id in stage.get(key, []):
                if source_id not in source_ids:
                    fail(f"unknown source id in {stage_name}: {source_id}")

    if preincarnation_example.get("schema_version") != "1.3.0":
        fail("synthetic preincarnation example must use schema_version 1.3.0")

    required_example_keys = {
        "origin",
        "agreement_motive",
        "role_selection",
        "encounter_conditions",
        "individual_tasks",
        "common_task",
        "clauses",
        "fulfillment_mechanisms",
    }
    if not required_example_keys.issubset(preincarnation_example):
        fail("synthetic preincarnation example is missing one or more canonical stages")

    if origin_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("origin differential schema must expose schema_version 1.0.0")

    if agreement_motive_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("agreement motive schema must expose schema_version 1.0.0")

    if role_selection_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("role selection schema must expose schema_version 1.0.0")

    expected_origin_models = {
        "INDEPENDENT_SOULS",
        "SOUL_FAMILY_GROUP",
        "RELATED_SOUL_ROOTS",
        "ZIVUG_TRUE_PAIR",
        "SHARED_ORIGIN_UNDIFFERENTIATED",
        "MONADIC_COMMON_SOURCE",
        "SPLIT_SOUL",
        "TWIN_SOUL",
        "TWIN_FLAME_MODEL",
    }
    origin_models = {m.get("id") for m in origin_registry.get("models", [])}
    if origin_models != expected_origin_models:
        fail("origin model registry diverges from canonical model set")

    expected_resolution_levels = {
        "O1_CONTINUITY",
        "O2_ROOT_FAMILY",
        "O3_UNIQUE_DYADIC",
        "UNRESOLVED",
    }
    for model in origin_registry.get("models", []):
        level = model.get("max_resolution_claim")
        if level not in expected_resolution_levels:
            fail(f"origin model {model.get('id')} has invalid max_resolution_claim: {level}")

    for model in origin_registry.get("models", []):
        for source_id in model.get("source_ids", []):
            if source_id not in source_ids:
                fail(f"unknown source id in origin model {model.get('id')}: {source_id}")

    astro_discriminators = [
        d for d in origin_registry.get("discriminators", [])
        if d.get("kind") == "ASTROLOGICAL"
    ]

    canonical_astrology_discriminator_ids = {
        d.get("id") for d in origin_discriminator_registry.get("astrology_discriminators", [])
    }
    registry_astrology_discriminator_ids = {d.get("id") for d in astro_discriminators}
    if canonical_astrology_discriminator_ids != registry_astrology_discriminator_ids:
        fail("origin model registry and origin discriminator registry disagree on A_* identifiers")
    if not astro_discriminators:
        fail("origin registry must declare astrological discriminator status")
    for d in astro_discriminators:
        if d.get("status") == "VALIDATED" and not d.get("validation_reference"):
            fail(f"validated origin discriminator lacks validation reference: {d.get('id')}")

    if origin_example.get("schema_version") != "1.0.0":
        fail("synthetic origin example must use schema_version 1.0.0")

    if origin_example.get("resolution_level") not in expected_resolution_levels:
        fail("synthetic origin example has invalid resolution_level")

    if not origin_example.get("why_not_more_specific"):
        fail("synthetic origin example must explain why it cannot be more specific")

    for discriminator_id in origin_example.get("astrology_discriminators", []):
        if discriminator_id not in canonical_astrology_discriminator_ids:
            fail(f"unknown A_* discriminator in synthetic origin example: {discriminator_id}")

    for result in origin_example.get("models", []):
        if result.get("model_id") not in expected_origin_models:
            fail(f"unknown model in synthetic origin example: {result.get('model_id')}")
        if result.get("state") == "SUPPORTED":
            used = set(result.get("discriminators_used", []))
            validated = {
                d.get("id") for d in astro_discriminators
                if d.get("status") == "VALIDATED"
            }
            if not (used & validated):
                fail("SUPPORTED origin subtype requires at least one VALIDATED astrological discriminator")

    if "origin_differential" not in preincarnation_example:
        fail("synthetic preincarnation example must embed origin_differential")

    expected_motive_ids = {
        "M_TIKKUN_PROPIO",
        "M_TIKKUN_DEL_OTRO",
        "M_EQUILIBRIO_KARMICO",
        "M_COMPLETAR_TAREA_PENDIENTE",
        "M_RECONOCIMIENTO_REENCUENTRO",
        "M_APRENDIZAJE_MUTUO",
        "M_CATALISIS_TRANSFORMACION",
        "M_ENCARNACION_MATERIALIZACION",
        "M_RECIPROCIDAD",
        "M_VERDAD_COMUNICACION",
        "M_MISION_SERVICIO",
        "M_INTEGRACION",
        "M_LIBERACION_CIERRE",
        "M_INDETERMINADO",
    }
    registry_motives = {m.get("id") for m in agreement_motive_registry.get("motives", [])}
    if registry_motives != expected_motive_ids:
        fail("agreement motive registry diverges from canonical motive set")

    for motive in agreement_motive_registry.get("motives", []):
        for source_id in motive.get("source_ids", []):
            if source_id not in source_ids:
                fail(f"unknown source id in agreement motive {motive.get('id')}: {source_id}")

    expected_am_discriminators = {f"AM{i}_" for i in range(1, 9)}
    am_ids = [d.get("id", "") for d in agreement_motive_registry.get("discriminators", [])]
    if len(am_ids) != 8 or any(not any(x.startswith(prefix) for x in am_ids) for prefix in expected_am_discriminators):
        fail("agreement motive registry must contain AM1-AM8 discriminators")

    if agreement_motive_example.get("schema_version") != "1.0.0":
        fail("synthetic agreement motive example must use schema_version 1.0.0")

    expected_role_ids = {
        "ACTIVADOR","CATALIZADOR","ESPEJO","MEMORIA","ESTRUCTURADOR","LIBERADOR",
        "CONFRONTADOR","PORTADOR_DE_VULNERABILIDAD","INTEGRADOR","MEDIADOR","TESTIGO",
        "COMPANERO_DE_APRENDIZAJE"
    }
    if set(role_selection_registry.get("roles", [])) != expected_role_ids:
        fail("role selection registry diverges from canonical role set")

    for mechanism in role_selection_registry.get("mechanisms", []):
        for source_id in mechanism.get("source_ids", []):
            if source_id not in source_ids:
                fail(f"unknown source id in role-selection mechanism {mechanism.get('id')}: {source_id}")

    rsd_ids = {d.get("id") for d in role_selection_registry.get("discriminators", [])}
    expected_rsd_ids = {f"RSD{i}_{suffix}" for i, suffix in [
        (1,"ROLE_VS_TRAIT"),(2,"DIRECTION"),(3,"PRIMARY_VS_SECONDARY"),
        (4,"INDIVIDUAL_VS_COMMON_FIELD"),(5,"REQUESTED_VS_MUTUAL"),
        (6,"KARMIC_VS_VOLUNTARY"),(7,"FIXED_VS_PHASE_DEPENDENT"),(8,"UNIQUE_ROLE")
    ]}
    if rsd_ids != expected_rsd_ids:
        fail("role selection registry must contain canonical RSD1-RSD8 discriminators")

    if role_selection_example.get("schema_version") != "1.0.0":
        fail("synthetic role-selection example must use schema_version 1.0.0")
    for role in role_selection_example.get("roles", []):
        if role.get("id") not in expected_role_ids:
            fail(f"unknown role in synthetic role-selection example: {role.get('id')}")
    if not set(agreement_motive_example.get("primary_motives", [])).issubset(expected_motive_ids):
        fail("synthetic agreement motive example contains unknown primary motive")
    if "agreement_motive_differential" not in preincarnation_example:
        fail("synthetic preincarnation example must embed agreement_motive_differential")

    embedded_origin = preincarnation_example.get("origin_differential", {})
    if embedded_origin.get("resolution_level") != origin_example.get("resolution_level"):
        fail("embedded origin differential diverges from standalone synthetic origin example")
    if embedded_origin.get("why_not_more_specific") != origin_example.get("why_not_more_specific"):
        fail("embedded origin differential explanation diverges from standalone example")

    embedded_motive = preincarnation_example.get("agreement_motive_differential", {})
    if embedded_motive.get("primary_motives") != agreement_motive_example.get("primary_motives"):
        fail("embedded agreement motive differential diverges from standalone synthetic example")
    if embedded_motive.get("why_not_more_specific") != agreement_motive_example.get("why_not_more_specific"):
        fail("embedded motive explanation diverges from standalone synthetic example")

    if "role_selection_differential" not in preincarnation_example:
        fail("synthetic preincarnation example must embed role_selection_differential")
    embedded_roles = preincarnation_example.get("role_selection_differential", {})
    if embedded_roles.get("primary_roles") != role_selection_example.get("primary_roles"):
        fail("embedded role-selection differential diverges from standalone synthetic example")
    if embedded_roles.get("why_not_more_specific") != role_selection_example.get("why_not_more_specific"):
        fail("embedded role-selection explanation diverges from standalone synthetic example")

    model_props = canonical_schema.get("properties", {}).get("models", {}).get("properties", {})
    if set(model_props) != {"AF", "KA", "AG", "LG"}:
        fail("canonical schema must expose exactly AF, KA, AG, LG model slots")

    for model, spec in model_props.items():
        state_enum = spec.get("properties", {}).get("state", {}).get("enum", [])
        if set(state_enum) != EXPECTED_STATES:
            fail(f"{model} state enum diverges from normative states")

    subject_items = raw_schema.get("properties", {}).get("subjects", {})
    if subject_items.get("minItems") != 2 or subject_items.get("maxItems") != 2:
        fail("raw input schema must require exactly two subjects")

    pillar_props = precomputed_schema.get("properties", {}).get("pillars", {}).get("properties", {})
    if set(pillar_props) != {"PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU"}:
        fail("precomputed pillar schema must expose PA/PK/PE/PR/PX/PT/PS/PU")

    if set(example_input.get("pillars", {})) != {"PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU"}:
        fail("example precomputed input does not cover all public pillars")

    if example_result.get("public_version") != version:
        fail("example precomputed result version diverges from VERSION")

    if set(example_result.get("models", {})) != {"AF", "KA", "AG", "LG"}:
        fail("example precomputed result does not contain all four models")

    print("ALMAS public contract validation: PASS")
    print(f"Astrology package: {version}")
    print(f"Soul-contract skill: {soul_version}")
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
