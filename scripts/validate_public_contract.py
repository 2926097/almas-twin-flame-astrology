#!/usr/bin/env python3
from __future__ import annotations

import json
import re
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
    "docs/history/DUAL_ENGINE_ARCHITECTURE.md",
    "docs/MODULE_ARCHITECTURE.md",
    "docs/MODULE_EXECUTION_CONTRACT.md",
    "docs/ASTRONOMY_BACKEND_DECISION.md",
    "docs/history/SOURCE_INTEGRATION_PLAN_PHASE1.md",
    "docs/SOURCE_RESEARCH_BACKLOG.md",
    "docs/SOURCE_NORMALIZATION_REPORT.md",
    "docs/DOCTRINE_TO_ASTROLOGY.md",
    "docs/SOURCE_ANCHOR_POLICY.md",
    "examples/README.md",
    "public_cases/README.md",
    "pyproject.toml",
    "schemas/raw-input.schema.json",
    "schemas/canonical-analysis.schema.json",
    "schemas/natal-chart.schema.json",
    "schemas/synastry-output.schema.json",
    "schemas/natal-context-output.schema.json",
    "schemas/declination-output.schema.json",
    "schemas/antiscia-output.schema.json",
    "schemas/composite-output.schema.json",
    "schemas/davison-output.schema.json",
    "schemas/draconic-output.schema.json",
    "schemas/draconic-cross-output.schema.json",
    "schemas/lots-output.schema.json",
    "schemas/secondary-symbolic-output.schema.json",
    "schemas/independent-roots.schema.json",
    "schemas/counterevidence-output.schema.json",
    "schemas/structural-ablation-output.schema.json",
    "schemas/deduplicated-evidence.schema.json",
    "schemas/evidence-graph.schema.json",
    "schemas/module-execution.schema.json",
    "schemas/precomputed-pillars.schema.json",
    "schemas/precomputed-result.schema.json",
    "schemas/astrology-to-soul-contract.schema.json",
    "schemas/contrato-almico.schema.json",
    "schemas/source-registry.schema.json",
    "schemas/doctrinal-genealogy.schema.json",
    "schemas/doctrinal-claim.schema.json",
    "schemas/concept-registry.schema.json",
    "schemas/ontology-output.schema.json",
    "schemas/inferential-ceiling.schema.json",
    "schemas/preincarnation-contract-chain.schema.json",
    "schemas/preincarnation-causality.schema.json",
    "schemas/contract-ablation.schema.json",
    "schemas/contract-metrics.schema.json",
    "schemas/free-will-contract.schema.json",
    "schemas/contract-temporality-v2.schema.json",
    "schemas/documentary-event-ledger.schema.json",
    "schemas/preincarnation-reconstruction.schema.json",
    "schemas/origin-differential.schema.json",
    "schemas/agreement-motive-differential.schema.json",
    "schemas/role-selection-differential.schema.json",
    "schemas/encounter-conditions-differential.schema.json",
    "schemas/individual-tasks-differential.schema.json",
    "schemas/common-task-differential.schema.json",
    "schemas/clause-assembly.schema.json",
    "schemas/fulfillment-mechanisms.schema.json",
    "manifests/analysis-pipeline-manifest.json",
    "manifests/execution-registry.json",
    "manifests/almas-module-manifest.json",
    "manifests/causal-type-registry.json",
    "manifests/cross-model-discriminator-registry.json",
    "manifests/differential-discriminator-registry.json",
    "manifests/origin-model-registry.json",
    "manifests/origin-discriminator-registry.json",
    "manifests/agreement-motive-registry.json",
    "manifests/role-selection-registry.json",
    "manifests/encounter-conditions-registry.json",
    "manifests/individual-tasks-registry.json",
    "manifests/common-task-registry.json",
    "manifests/clause-registry.json",
    "manifests/fulfillment-mechanisms-registry.json",
    "manifests/preincarnation-pipeline-manifest.json",
    "reference/source-registry.json",
    "reference/source-normalization-audit.json",
    "reference/concept-registry.json",
    "reference/doctrinal-genealogy.json",
    "reference/twin-flame-genealogy-matrix.md",
    "reference/contemporary-phenomenology-matrix.md",
    "reference/doctrinal-gate.md",
    "reference/esoteric-draconic-astrology-matrix.md",
    "reference/lurianic-kabbalah-matrix.md",
    "reference/preincarnation-planning-matrix.md",
    "reference/ontology-registry.json",
    "reference/contract-causal-architecture-v2.md",
    "reference/preincarnation-causality-engine.md",
    "reference/contract-ablation.md",
    "reference/contract-metrics.md",
    "reference/contract-free-will.md",
    "reference/contract-temporality-v2.md",
    "reference/documentary-events.md",
    "reference/cross-model-differential.md",
    "reference/doctrine-to-astrology-map.json",
    "reference/contrato-almico.md",
    "reference/preincarnation-source-map.json",
    "reference/preincarnation-reconstruction.md",
    "reference/origin-differential.md",
    "reference/agreement-motive-differential.md",
    "reference/role-selection-differential.md",
    "reference/encounter-conditions-differential.md",
    "reference/individual-tasks-differential.md",
    "reference/common-task-differential.md",
    "reference/clause-assembly.md",
    "reference/fulfillment-mechanisms.md",
    "reference/roles-preencarnatorios.md",
    "skills/almas-soul-contract/SKILL.md",
    "skills/almas-soul-contract/VERSION",
    "skills/almas-soul-contract/CHANGELOG.md",
    "src/almas_tfa/core.py",
    "src/almas_tfa/analysis.py",
    "src/almas_tfa/cli.py",
    "src/almas_tfa/module_contract.py",
    "src/almas_tfa/orchestrator.py",
    "src/almas_tfa/handlers.py",
    "src/almas_tfa/astrology_backend.py",
    "src/almas_tfa/astrology_handlers.py",
    "src/almas_tfa/astrology_geometry.py",
    "src/almas_tfa/relational_handlers.py",
    "src/almas_tfa/symmetry_handlers.py",
    "src/almas_tfa/relationship_chart_handlers.py",
    "src/almas_tfa/draconic_handlers.py",
    "src/almas_tfa/lot_handlers.py",
    "src/almas_tfa/secondary_handlers.py",
    "src/almas_tfa/evidence_handlers.py",
    "src/almas_tfa/counterevidence_handlers.py",
    "src/almas_tfa/ablation_handlers.py",
    "tests/INVARIANTS.md",
    "tests/MODULE_ARCHITECTURE_INVARIANTS.md",
    "tests/DOCTRINAL_GENEALOGY_INVARIANTS.md",
    "tests/DOCTRINAL_GATE_INVARIANTS.md",
    "tests/ONTOLOGY_V2_INVARIANTS.md",
    "tests/CONTRACT_CAUSAL_CHAIN_V2_INVARIANTS.md",
    "tests/PREINCARNATION_CAUSALITY_INVARIANTS.md",
    "tests/CONTRACT_ABLATION_INVARIANTS.md",
    "tests/CONTRACT_METRICS_INVARIANTS.md",
    "tests/CONTRACT_FREE_WILL_INVARIANTS.md",
    "tests/CONTRACT_TEMPORALITY_V2_INVARIANTS.md",
    "tests/DOCUMENTARY_EVENT_INVARIANTS.md",
    "tests/CROSS_MODEL_DISCRIMINATOR_INVARIANTS.md",
    "tests/DOCTRINE_TO_ASTROLOGY_INVARIANTS.md",
    "tests/DOCTRINAL_CLAIM_V2_INVARIANTS.md",
    "tests/SOURCE_ANCHOR_INVARIANTS.md",
    "tests/INFERENTIAL_CEILING_INVARIANTS.md",
    "tests/CONTRATO_ALMICO_INVARIANTS.md",
    "tests/PREINCARNATION_RECONSTRUCTION_INVARIANTS.md",
    "tests/ORIGIN_DIFFERENTIAL_INVARIANTS.md",
    "tests/AGREEMENT_MOTIVE_INVARIANTS.md",
    "tests/ROLE_SELECTION_INVARIANTS.md",
    "tests/ENCOUNTER_CONDITIONS_INVARIANTS.md",
    "tests/INDIVIDUAL_TASKS_INVARIANTS.md",
    "tests/COMMON_TASK_INVARIANTS.md",
    "tests/CLAUSE_ASSEMBLY_INVARIANTS.md",
    "tests/FULFILLMENT_MECHANISMS_INVARIANTS.md",
    "reference/causa-contractual.md",
    "tests/CAUSA_CONTRACTUAL_INVARIANTS.md",
    "tests/ROLES_PREENCARNATORIOS_INVARIANTS.md",
    "tests/test_core.py",
    "tests/test_analysis.py",
    "tests/test_orchestrator.py",
    "tests/test_handlers.py",
    "tests/test_astrology_backend.py",
    "tests/test_relational_handlers.py",
    "tests/test_symmetry_handlers.py",
    "tests/test_relationship_charts.py",
    "tests/test_draconic_handlers.py",
    "tests/test_lot_handlers.py",
    "tests/test_secondary_handlers.py",
    "tests/test_evidence_handlers.py",
    "tests/test_counterevidence_handlers.py",
    "tests/test_ablation_handlers.py",
    "examples/precomputed-pillars.json",
    "examples/precomputed-result.json",
    "examples/doctrinal-claims.synthetic.json",
    "examples/inferential-ceiling.synthetic.json",
    "examples/preincarnation-reconstruction.synthetic.json",
    "examples/origin-differential.synthetic.json",
    "examples/agreement-motive.synthetic.json",
    "examples/role-selection.synthetic.json",
    "examples/encounter-conditions.synthetic.json",
    "examples/individual-tasks.synthetic.json",
    "examples/common-task.synthetic.json",
    "examples/clause-assembly.synthetic.json",
    "examples/fulfillment-mechanisms.synthetic.json",
    "examples/preincarnation-contract-chain.synthetic.json",
    "examples/contract-ablation.synthetic.json",
    "examples/documentary-event-ledger.synthetic.json",
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
    if re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        fail(f"root VERSION is not semantic versioning: {version}")

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

    contract_module = (ROOT / "skills/almas-soul-contract/SKILL.md").read_text(encoding="utf-8")
    contract_module_version = (ROOT / "skills/almas-soul-contract/VERSION").read_text(encoding="utf-8").strip()
    if contract_module_version != version:
        fail("contract module VERSION must inherit root VERSION")
    for needle in [
        "name: almas-preincarnation-contract-module",
        f"version: {version}",
        "kind: internal_module",
        "independent_versioning: false",
        "Módulo de Contrato Preencarnatorio",
        "A_EN_B",
        "B_EN_A",
        "CAMPO_COMUN",
    ]:
        if needle not in contract_module:
            fail(f"contract module missing token: {needle}")

    raw_schema = load_json("schemas/raw-input.schema.json")
    canonical_schema = load_json("schemas/canonical-analysis.schema.json")
    natal_chart_schema = load_json("schemas/natal-chart.schema.json")
    synastry_schema = load_json("schemas/synastry-output.schema.json")
    natal_context_schema = load_json("schemas/natal-context-output.schema.json")
    declination_schema = load_json("schemas/declination-output.schema.json")
    antiscia_schema = load_json("schemas/antiscia-output.schema.json")
    composite_schema = load_json("schemas/composite-output.schema.json")
    davison_schema = load_json("schemas/davison-output.schema.json")
    draconic_schema = load_json("schemas/draconic-output.schema.json")
    draconic_cross_schema = load_json("schemas/draconic-cross-output.schema.json")
    lots_schema = load_json("schemas/lots-output.schema.json")
    secondary_symbolic_schema = load_json("schemas/secondary-symbolic-output.schema.json")
    evidence_graph_schema = load_json("schemas/evidence-graph.schema.json")
    deduplicated_evidence_schema = load_json("schemas/deduplicated-evidence.schema.json")
    independent_roots_schema = load_json("schemas/independent-roots.schema.json")
    counterevidence_output_schema = load_json("schemas/counterevidence-output.schema.json")
    structural_ablation_schema = load_json("schemas/structural-ablation-output.schema.json")
    module_execution_schema = load_json("schemas/module-execution.schema.json")
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
    encounter_conditions_schema = load_json("schemas/encounter-conditions-differential.schema.json")
    encounter_conditions_registry = load_json("manifests/encounter-conditions-registry.json")
    encounter_conditions_example = load_json("examples/encounter-conditions.synthetic.json")
    individual_tasks_schema = load_json("schemas/individual-tasks-differential.schema.json")
    individual_tasks_registry = load_json("manifests/individual-tasks-registry.json")
    individual_tasks_example = load_json("examples/individual-tasks.synthetic.json")
    common_task_schema = load_json("schemas/common-task-differential.schema.json")
    common_task_registry = load_json("manifests/common-task-registry.json")
    common_task_example = load_json("examples/common-task.synthetic.json")
    clause_assembly_schema = load_json("schemas/clause-assembly.schema.json")
    clause_registry = load_json("manifests/clause-registry.json")
    clause_assembly_example = load_json("examples/clause-assembly.synthetic.json")
    fulfillment_schema = load_json("schemas/fulfillment-mechanisms.schema.json")
    fulfillment_registry = load_json("manifests/fulfillment-mechanisms-registry.json")
    fulfillment_example = load_json("examples/fulfillment-mechanisms.synthetic.json")
    pipeline_manifest = load_json("manifests/preincarnation-pipeline-manifest.json")
    analysis_pipeline_manifest = load_json("manifests/analysis-pipeline-manifest.json")
    execution_registry = load_json("manifests/execution-registry.json")
    discriminator_registry = load_json("manifests/differential-discriminator-registry.json")
    source_registry = load_json("reference/source-registry.json")
    source_audit = load_json("reference/source-normalization-audit.json")
    source_schema = load_json("schemas/source-registry.schema.json")
    concept_schema = load_json("schemas/concept-registry.schema.json")
    genealogy_schema = load_json("schemas/doctrinal-genealogy.schema.json")
    concept_registry = load_json("reference/concept-registry.json")
    doctrinal_genealogy = load_json("reference/doctrinal-genealogy.json")
    ontology_registry = load_json("reference/ontology-registry.json")
    contract_chain_schema = load_json("schemas/preincarnation-contract-chain.schema.json")
    contract_chain_example = load_json("examples/preincarnation-contract-chain.synthetic.json")
    contract_ablation_example = load_json("examples/contract-ablation.synthetic.json")
    doctrine_map = load_json("reference/doctrine-to-astrology-map.json")
    doctrinal_claim_schema = load_json("schemas/doctrinal-claim.schema.json")
    doctrinal_claim_fixture = load_json("examples/doctrinal-claims.synthetic.json")
    inferential_ceiling_fixture = load_json("examples/inferential-ceiling.synthetic.json")
    causal_registry = load_json("manifests/causal-type-registry.json")
    cross_discriminators = load_json("manifests/cross-model-discriminator-registry.json")
    almas_module_manifest = load_json("manifests/almas-module-manifest.json")
    example_input = load_json("examples/precomputed-pillars.json")
    example_result = load_json("examples/precomputed-result.json")
    preincarnation_source_map = load_json("reference/preincarnation-source-map.json")
    preincarnation_example = load_json("examples/preincarnation-reconstruction.synthetic.json")

    if canonical_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("canonical astrology schema contract must remain 1.0.0")

    natal_required = set(natal_chart_schema.get("required", []))
    if not {"subject_id", "timed", "backend_id", "backend_version", "positions"}.issubset(natal_required):
        fail("natal chart schema lacks required canonical fields")

    syn_required = set(synastry_schema.get("required", []))
    if not {"subjects", "aspect_policy", "contacts", "contact_count"}.issubset(syn_required):
        fail("synastry schema lacks required canonical fields")

    if "subjects" not in natal_context_schema.get("required", []):
        fail("natal context schema must require subjects")

    if "contacts" not in declination_schema.get("required", []):
        fail("declination schema must require contacts")
    if "contacts" not in antiscia_schema.get("required", []):
        fail("antiscia schema must require contacts")

    if "positions" not in composite_schema.get("required", []):
        fail("composite schema must require positions")
    if "chart" not in davison_schema.get("required", []):
        fail("davison schema must require chart")

    if "charts" not in draconic_schema.get("required", []):
        fail("draconic schema must require charts")
    if "contacts" not in draconic_cross_schema.get("required", []):
        fail("draconic cross schema must require contacts")

    if "subjects" not in lots_schema.get("required", []):
        fail("lots schema must require subjects")

    if secondary_symbolic_schema.get("properties", {}).get("support_only", {}).get("const") is not True:
        fail("secondary symbolic schema must freeze support_only=true")

    if evidence_graph_schema.get("properties", {}).get("strength_policy_applied", {}).get("const") is not False:
        fail("evidence graph must declare strength_policy_applied=false")
    if "retained" not in deduplicated_evidence_schema.get("required", []):
        fail("deduplicated evidence schema must require retained")
    if independent_roots_schema.get("properties", {}).get("strength_policy_applied", {}).get("const") is not False:
        fail("independent roots must remain unweighted until an explicit strength policy exists")

    if counterevidence_output_schema.get("properties", {}).get("missing_data_penalized", {}).get("const") is not False:
        fail("counterevidence schema must forbid missing-data penalty")

    if structural_ablation_schema.get("properties", {}).get("structural_only", {}).get("const") is not True:
        fail("structural ablation must declare structural_only=true")
    if structural_ablation_schema.get("properties", {}).get("dependency_classes_assigned", {}).get("const") is not False:
        fail("structural ablation must not assign contractual dependency classes")

    if result_schema.get("properties", {}).get("public_version", {}).get("const") != version:
        fail("precomputed result public_version diverges from root VERSION")

    if bridge_schema.get("properties", {}).get("bridge_version", {}).get("const") != "1.0.0":
        fail("astrology-to-soul-contract bridge must expose bridge_version 1.0.0")

    if doctrinal_claim_schema.get("properties", {}).get("schema_version", {}).get("const") != "2.0.0":
        fail("doctrinal claim schema must expose 2.0.0")


    if contract_chain_schema.get("properties", {}).get("schema_version", {}).get("const") != "2.0.0":
        fail("contract causal chain schema must expose 2.0.0")
    if contract_chain_example.get("literal_content_state") != "NOT_EVALUABLE":
        fail("synthetic contract chain must keep literal pre-birth content NOT_EVALUABLE")

    ab_runs = set(contract_ablation_example.get("runs", []))
    if not {"AB1_NO_ASTEROIDS","AB2_NO_TEMPORALITY","AB8_INDIVIDUAL_ONLY"}.issubset(ab_runs):
        fail("contract ablation fixture must include AB1 and AB2 and AB8")

    preincarnation_schema_version = (
        preincarnation_schema.get("properties", {})
        .get("schema_version", {})
        .get("const")
    )
    if not preincarnation_schema_version:
        fail("preincarnation reconstruction schema lacks schema_version const")
    if preincarnation_example.get("schema_version") != preincarnation_schema_version:
        fail(
            "preincarnation synthetic fixture version diverges from "
            f"preincarnation schema: {preincarnation_example.get('schema_version')} "
            f"!= {preincarnation_schema_version}"
        )

    clause_schema_version = (
        clause_assembly_schema.get("properties", {})
        .get("schema_version", {})
        .get("const")
    )
    if not clause_schema_version:
        fail("clause assembly schema lacks schema_version const")
    if clause_assembly_example.get("schema_version") != clause_schema_version:
        fail("clause assembly fixture version diverges from clause schema")
    required_clause_fields = {
        "resolution_level",
        "reconstructed_contract_content",
        "activation_mechanism",
        "contract_test",
        "claim_refs",
        "allowed_conclusion",
        "inferential_ceiling",
    }
    for clause in clause_assembly_example.get("clauses", []):
        missing = required_clause_fields - set(clause)
        if missing:
            fail(f"clause fixture missing causal fields for {clause.get('id')}: {sorted(missing)}")
        if clause.get("resolution_level") == "R4_LITERAL_CONTENT":
            fail(f"synthetic clause must not assert R4 literal content: {clause.get('id')}")
        if clause.get("inferential_ceiling") == "R2_RELATIONAL_PREINCARNATIONAL_FUNCTION":
            if clause.get("allowed_conclusion") != "R2_RELATIONAL_PREINCARNATIONAL_FUNCTION":
                fail(f"clause allowed conclusion exceeds or disagrees with R2 ceiling: {clause.get('id')}")
        for claim_ref in clause.get("claim_refs", []):
            if claim_ref not in {x.get("claim_id") for x in doctrinal_claim_fixture.get("claims", [])}:
                fail(f"clause references unknown doctrinal claim: {clause.get('id')} -> {claim_ref}")

    nested_clause = preincarnation_example.get("clause_assembly", {})
    if nested_clause.get("schema_version") != clause_schema_version:
        fail("nested clause assembly fixture version diverges from clause schema")

    if analysis_pipeline_manifest.get("manifest_version") != "1.0.0":
        fail("analysis pipeline manifest must expose manifest_version 1.0.0")
    if analysis_pipeline_manifest.get("mode") != "FULL":
        fail("analysis pipeline manifest must expose FULL mode")
    modules = analysis_pipeline_manifest.get("modules", [])
    ids = [m.get("id") for m in modules]
    expected_ids = [f"M{i:02d}" for i in range(32)]
    if ids != expected_ids:
        fail("analysis pipeline manifest must contain ordered M00..M31 exactly once")

    execution_ids = [m.get("id") for m in execution_registry.get("modules", [])]
    if execution_registry.get("registry_version") != "1.0.0":
        fail("execution registry must expose registry_version 1.0.0")
    if execution_registry.get("almas_public_version") != version:
        fail("execution registry version diverges from VERSION")
    if execution_ids != expected_ids:
        fail("execution registry must contain ordered M00..M31 exactly once")
    allowed_execution_status = {"ORCHESTRATOR_NATIVE", "EXECUTABLE_HANDLER", "BACKEND_REQUIRED", "LIBRARY_AVAILABLE", "SPECIFIED"}
    for module in execution_registry.get("modules", []):
        if module.get("status") not in allowed_execution_status:
            fail(f"unknown execution registry status: {module.get('id')} -> {module.get('status')}")
        if module.get("status") in {"ORCHESTRATOR_NATIVE", "EXECUTABLE_HANDLER", "BACKEND_REQUIRED", "LIBRARY_AVAILABLE"} and not module.get("implementation"):
            fail(f"implemented execution entry lacks implementation reference: {module.get('id')}")

    module_status_enum = set(
        module_execution_schema.get("properties", {}).get("status", {}).get("enum", [])
    )
    expected_module_status = {
        "COMPLETED", "SKIPPED", "NOT_APPLICABLE", "NOT_EVALUABLE", "FAILED"
    }
    if module_status_enum != expected_module_status:
        fail("module execution schema status enum diverges from runtime contract")

    discriminators = discriminator_registry.get("discriminators", [])
    if not discriminators:
        fail("discriminator registry is empty")
    for d in discriminators:
        if d.get("status") == "VALIDATED" and not d.get("validation_reference"):
            fail(f"validated discriminator lacks validation reference: {d.get('id')}")

    if not source_registry.get("entries"):
        fail("source registry is empty")

    if source_registry.get("registry_version") != version:
        fail("source registry version diverges from root VERSION")

    if almas_module_manifest.get("architecture") != "single_skill_modular":
        fail("ALMAS architecture must be single_skill_modular")
    if almas_module_manifest.get("almas_public_version") != version:
        fail("ALMAS module manifest version diverges from VERSION")

    source_ids_list = [entry.get("id") for entry in source_registry.get("entries", [])]
    if len(source_ids_list) != len(set(source_ids_list)):
        fail("source registry contains duplicate ids")
    source_ids = set(source_ids_list)

    required_source_fields = {"id", "priority", "author", "work", "supports", "does_not_support"}
    for entry in source_registry.get("entries", []):
        missing = required_source_fields - set(entry)
        if missing:
            fail(f"source entry {entry.get('id')} missing fields: {sorted(missing)}")
        if not entry.get("supports") or not entry.get("does_not_support"):
            fail(f"source entry {entry.get('id')} must define supports and does_not_support")

    concept_ids_list = [c.get("id") for c in concept_registry.get("concepts", [])]
    if len(concept_ids_list) != len(set(concept_ids_list)):
        fail("concept registry contains duplicate ids")
    concept_ids = set(concept_ids_list)
    for concept in concept_registry.get("concepts", []):
        for key in ("primary_sources", "academic_sources", "method_sources"):
            for source_id in concept.get(key, []):
                if source_id not in source_ids:
                    fail(f"unknown source id in concept {concept.get('id')}: {source_id}")

    for entry in source_registry.get("entries", []):
        for concept_id in entry.get("concepts", []):
            if concept_id not in concept_ids:
                fail(f"source entry references unknown concept: {entry.get('id')} -> {concept_id}")
        if not entry.get("tradition"):
            fail(f"source entry lacks tradition: {entry.get('id')}")
        if not entry.get("verification_status"):
            fail(f"source entry lacks verification status: {entry.get('id')}")

    for edge in doctrinal_genealogy.get("edges", []):
        if edge.get("from") not in concept_ids or edge.get("to") not in concept_ids:
            fail(f"doctrinal genealogy edge references unknown concept: {edge}")

    allowed_concept_classes = set(
        concept_schema["properties"]["concepts"]["items"]["properties"]["concept_class"]["enum"]
    )
    for concept in concept_registry.get("concepts", []):
        if concept.get("concept_class") not in allowed_concept_classes:
            fail(f"concept class not admitted by schema: {concept.get('id')} -> {concept.get('concept_class')}")

    allowed_relations = set(
        genealogy_schema["properties"]["edges"]["items"]["properties"]["relation"]["enum"]
    )
    allowed_genealogy_states = set(
        genealogy_schema["properties"]["edges"]["items"]["properties"]["status"]["enum"]
    )
    for edge in doctrinal_genealogy.get("edges", []):
        if edge.get("relation") not in allowed_relations:
            fail(f"genealogy relation not admitted by schema: {edge.get('relation')}")
        if edge.get("status") not in allowed_genealogy_states:
            fail(f"genealogy status not admitted by schema: {edge.get('status')}")

    partial_sources = [
        entry.get("id")
        for entry in source_registry.get("entries", [])
        if entry.get("verification_status") == "PARTIAL"
    ]
    if partial_sources:
        fail(f"source normalization baseline contains PARTIAL entries: {partial_sources}")

    actual_counts = {
        "sources_total": len(source_registry.get("entries", [])),
        "concepts_total": len(concept_registry.get("concepts", [])),
        "genealogy_edges_total": len(doctrinal_genealogy.get("edges", [])),
    }
    for key, value in actual_counts.items():
        if source_audit.get(key) != value:
            fail(f"source audit count mismatch for {key}: audit={source_audit.get(key)} actual={value}")
    if source_audit.get("integrity", {}).get("unknown_concepts_from_sources") != 0:
        fail("source audit must report zero unknown concepts from sources")
    if source_audit.get("integrity", {}).get("unknown_sources_from_concepts") != 0:
        fail("source audit must report zero unknown sources from concepts")
    if source_audit.get("integrity", {}).get("broken_genealogy_edges") != 0:
        fail("source audit must report zero broken genealogy edges")

    edge_keys = {
        (edge.get("from"), edge.get("to"), edge.get("relation"))
        for edge in doctrinal_genealogy.get("edges", [])
    }
    required_non_equivalences = {
        ("ZIVUG", "TWIN_FLAME_ORIGIN", "NON_EQUIVALENT"),
        ("SOUL_ROOT", "MONAD", "NON_EQUIVALENT"),
        ("THEOSOPHICAL_MONAD", "TWIN_FLAME_ORIGIN", "NON_EQUIVALENT"),
        ("BAT_ZUG", "TWIN_FLAME_ORIGIN", "NON_EQUIVALENT"),
    }
    missing_edges = required_non_equivalences - edge_keys
    if missing_edges:
        fail(f"missing mandatory doctrinal non-equivalence edges: {sorted(missing_edges)}")

    if not any(
        edge.get("from") == "TWIN_FLAME_LITERARY_GENEALOGY"
        and edge.get("to") == "TWIN_FLAME_ORIGIN"
        and edge.get("relation") == "TERMINOLOGICAL_ANTECEDENT_NOT_DOCTRINAL_IDENTITY"
        for edge in doctrinal_genealogy.get("edges", [])
    ):
        fail("Victorian twin-flame terminology must remain separate from later doctrinal codification")

    ontology_axes = {a.get("id") for a in ontology_registry.get("axes", [])}
    required_axes = {
        "ORIGIN",
        "PREINCARNATION_CONTRACT",
        "HISTORY_CONTINUITY",
        "FUNCTION",
        "PHENOMENOLOGY",
        "POLARITY",
        "MODALITY",
        "PHASE",
        "REAL_VIABILITY",
        "RECIPROCITY",
    }
    if ontology_axes != required_axes:
        fail("ontology must define independent axes exactly once")
    for axis in ontology_registry.get("axes", []):
        for concept_id in axis.get("concept_ids", []):
            if concept_id not in concept_ids:
                fail(f"ontology axis references unknown concept: {axis.get('id')} -> {concept_id}")

    required_mapping_fields = {
        "concept_id",
        "metaphysical_variable",
        "source_basis",
        "operationalization_class",
        "admissible_astrology",
        "inadmissible_inferences",
        "source_alignment",
        "validation_state",
        "inferential_ceiling",
        "structural_score_policy",
        "dependencies",
        "required_gates",
        "discriminating_power",
        "forbidden_upgrade",
    }
    for mapping in doctrine_map.get("mappings", []):
        missing = required_mapping_fields - set(mapping)
        if missing:
            fail(f"doctrine-to-astrology mapping missing fields for {mapping.get('concept_id')}: {sorted(missing)}")
        if mapping.get("concept_id") not in concept_ids:
            fail(f"doctrine-to-astrology map references unknown concept: {mapping.get('concept_id')}")
        if not mapping.get("operationalization_class"):
            fail(f"doctrine-to-astrology mapping lacks operationalization_class: {mapping.get('concept_id')}")
        for source_id in mapping.get("source_basis", []):
            if source_id not in source_ids:
                fail(f"doctrine-to-astrology mapping references unknown source: {source_id}")
            source_entry = next(
                (entry for entry in source_registry.get("entries", []) if entry.get("id") == source_id),
                None,
            )
            if not source_entry.get("verification_anchor") or not source_entry.get("verification_anchor_type"):
                fail(f"mapped source lacks verification anchor: {source_id}")
            if not source_entry.get("evidence_scope"):
                fail(f"mapped source lacks evidence_scope: {source_id}")


    draconic_mapping = next(
        (m for m in doctrine_map.get("mappings", []) if m.get("concept_id") == "DRACONIC_ASTROLOGY"),
        None,
    )
    if draconic_mapping is None:
        fail("DRACONIC_ASTROLOGY mapping missing")
    if "blaquier_draconic_astrology_2017_2021" not in draconic_mapping.get("source_basis", []):
        fail("DRACONIC_ASTROLOGY must include Blaquier technical source for formula verification")
    if "mean_or_true_node_choice_recorded" not in draconic_mapping.get("required_gates", []):
        fail("DRACONIC_ASTROLOGY must record Mean/True Node choice")
    # Blaquier technical source verifies calculation, not metaphysical ontology.
    if draconic_mapping.get("inferential_ceiling") != "CORROBORATIVE_NODAL_REFRAMING":
        fail("Blaquier technical source must not raise draconic inferential ceiling")

    if doctrinal_claim_fixture.get("schema_version") != "2.0.0":
        fail("doctrinal claim fixture must expose schema_version 2.0.0")
    claim_ids = [x.get("claim_id") for x in doctrinal_claim_fixture.get("claims", [])]
    if len(claim_ids) != len(set(claim_ids)):
        fail("doctrinal claim fixture contains duplicate claim ids")
    required_claim_fields = {
        "schema_version",
        "claim_id",
        "statement",
        "epistemic_class",
        "claim_scope",
        "source_relation",
        "source_ids",
        "source_anchor_refs",
        "status",
        "limitations",
        "inferential_ceiling",
        "discriminator_state",
        "allowed_conclusion",
        "ceiling_enforced",
    }
    for claim in doctrinal_claim_fixture.get("claims", []):
        missing = required_claim_fields - set(claim)
        if missing:
            fail(f"doctrinal claim fixture missing fields for {claim.get('claim_id')}: {sorted(missing)}")
        if claim.get("ceiling_enforced") is not True:
            fail(f"doctrinal claim must enforce ceiling: {claim.get('claim_id')}")
        for source_id in claim.get("source_ids", []):
            if source_id not in source_ids:
                fail(f"doctrinal claim references unknown source: {source_id}")
        for source_id in claim.get("source_anchor_refs", []):
            source_entry = next(
                (entry for entry in source_registry.get("entries", []) if entry.get("id") == source_id),
                None,
            )
            if source_entry is None:
                fail(f"doctrinal claim anchor references unknown source: {source_id}")
            if not source_entry.get("verification_anchor") or not source_entry.get("verification_anchor_type"):
                fail(f"doctrinal claim anchor lacks verified source anchor: {source_id}")
        concept_id = claim.get("concept_id")
        if concept_id is not None and concept_id not in concept_ids:
            fail(f"doctrinal claim references unknown concept: {concept_id}")
        if claim.get("discriminator_state") == "NOT_VALIDATED":
            requested = claim.get("requested_conclusion")
            allowed = claim.get("allowed_conclusion")
            if requested and requested == allowed:
                fail(f"NOT_VALIDATED discriminator cannot leave requested upgrade unchanged: {claim.get('claim_id')}")

    mapping_ids = {m.get("concept_id") for m in doctrine_map.get("mappings", [])}
    coverage = doctrine_map.get("coverage", [])
    coverage_ids_list = [x.get("concept_id") for x in coverage]
    if len(coverage_ids_list) != len(set(coverage_ids_list)):
        fail("doctrine-to-astrology coverage contains duplicate concept ids")
    coverage_ids = set(coverage_ids_list)
    if coverage_ids != concept_ids:
        missing = concept_ids - coverage_ids
        extra_ids = coverage_ids - concept_ids
        fail(f"doctrine-to-astrology coverage must account for every concept exactly once; missing={sorted(missing)} extra={sorted(extra_ids)}")

    allowed_coverage_states = {
        "MAPPED",
        "CONTEXT_ONLY",
        "BOUNDARY_ONLY",
        "TECHNIQUE_CONTEXT_ONLY",
        "PROJECT_INTERNAL",
        "NOT_OPERATIONALIZED",
    }
    coverage_by_id = {x.get("concept_id"): x for x in coverage}
    for concept_id, item in coverage_by_id.items():
        state = item.get("coverage_state")
        if state not in allowed_coverage_states:
            fail(f"invalid doctrine-to-astrology coverage state: {concept_id} -> {state}")
        if state == "MAPPED" and concept_id not in mapping_ids:
            fail(f"coverage marks MAPPED without mapping: {concept_id}")
        if concept_id in mapping_ids and state != "MAPPED":
            fail(f"mapping exists but coverage is not MAPPED: {concept_id} -> {state}")
        if state == "BOUNDARY_ONLY" and concept_id in mapping_ids:
            fail(f"boundary concept must not generate astrological mapping: {concept_id}")


    if cross_discriminators.get("almas_version") != version:
        fail("cross-model discriminator registry version diverges from root VERSION")
    binding_ids = {x.get("concept_id") for x in cross_discriminators.get("ceiling_bindings", [])}
    required_ceiling_bindings = {
        "SOUL_CONTRACT",
        "TWIN_FLAME_ORIGIN",
        "ZIVUG",
        "SOUL_ROOT",
        "MONAD",
        "SPLIT_PRIMORDIAL_BEING",
        "GILGUL",
        "DRACONIC_ASTROLOGY",
    }
    if not required_ceiling_bindings.issubset(binding_ids):
        fail("cross-model discriminator registry lacks required inferential-ceiling bindings")

    ceiling_case_ids = {x.get("id") for x in inferential_ceiling_fixture.get("cases", [])}
    required_ceiling_case_ids = {
        "CEIL_TF_HIGH_SCORE_NO_DISCRIMINATOR",
        "CEIL_CONTRACT_STRONG_CHAIN_NO_LITERAL_AGREEMENT",
        "CEIL_DRACONIC_ONLY",
        "CEIL_SOUL_ROOT_NETWORK_TO_UNIQUE_DYAD",
        "CEIL_ZIVUG_TO_TWIN_FLAME",
        "CEIL_MONAD_TO_ROMANTIC_PAIR",
        "CEIL_PHENOMENOLOGY_TO_ONTOLOGY",
    }
    if not required_ceiling_case_ids.issubset(ceiling_case_ids):
        fail("inferential ceiling fixture lacks mandatory negative cases")
    for case in inferential_ceiling_fixture.get("cases", []):
        concept_id = case.get("concept_id")
        if concept_id not in concept_ids:
            fail(f"inferential ceiling fixture references unknown concept: {concept_id}")
        mapped = next((m for m in doctrine_map.get("mappings", []) if m.get("concept_id") == concept_id), None)
        if mapped is None:
            fail(f"inferential ceiling fixture concept lacks mapping: {concept_id}")
        if case.get("expected_ceiling") != mapped.get("inferential_ceiling"):
            fail(f"inferential ceiling fixture disagrees with mapping for {concept_id}")


    specificity_ids = {x.get("id") for x in causal_registry.get("specificity_levels", [])}
    if specificity_ids != {"C0_GENERIC","C1_TARGETED","C2_MULTIROOT","C3_PAIR_SPECIFIC_EMERGENT"}:
        fail("causal specificity registry must define C0..C3")

    if not cross_discriminators.get("discriminators"):
        fail("cross-model discriminator registry is empty")
    for d in cross_discriminators.get("discriminators", []):
        if d.get("status") not in {"OPERATIONAL","OPERATIONAL_FUNCTIONAL_ONLY","OPERATIONAL_EPISTEMIC","DOCTRINAL_ONLY","NOT_VALIDATED"}:
            fail(f"unknown cross-model discriminator status: {d.get('id')}")

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

    for stage_name, stage in preincarnation_source_map.get("stages", {}).items():
        for key in ("primary", "methods", "comparative"):
            for source_id in stage.get(key, []):
                if source_id not in source_ids:
                    fail(f"unknown source id in {stage_name}: {source_id}")

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

    if encounter_conditions_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("encounter conditions schema must expose schema_version 1.0.0")

    if individual_tasks_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("individual tasks schema must expose schema_version 1.0.0")
    if common_task_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("common task schema must expose schema_version 1.0.0")
    if fulfillment_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("fulfillment mechanisms schema must expose schema_version 1.0.0")

    if pipeline_manifest.get("pipeline_version") != "1.0.0":
        fail("preincarnation pipeline manifest must expose pipeline_version 1.0.0")
    if pipeline_manifest.get("almas_version") != version:
        fail("preincarnation pipeline almas_version diverges from root VERSION")
    if not pipeline_manifest.get("contract_engine_revision"):
        fail("preincarnation pipeline must expose contract_engine_revision")
    if pipeline_manifest.get("preincarnation_schema_version") != preincarnation_schema_version:
        fail("preincarnation pipeline schema version diverges from preincarnation schema")

    expected_pipeline_stages = [
        "ORIGIN",
        "AGREEMENT_MOTIVE",
        "ROLE_SELECTION",
        "ENCOUNTER_CONDITIONS",
        "INDIVIDUAL_TASKS",
        "COMMON_TASK",
        "CLAUSES",
        "FULFILLMENT_MECHANISMS",
    ]
    actual_pipeline_stages = [stage.get("id") for stage in pipeline_manifest.get("stages", [])]
    if actual_pipeline_stages != expected_pipeline_stages:
        fail("preincarnation pipeline stage order diverges from canonical eight-stage sequence")
    if [stage.get("order") for stage in pipeline_manifest.get("stages", [])] != list(range(1, 9)):
        fail("preincarnation pipeline stage order numbers must be 1..8")

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

    expected_encounter_condition_ids = {
        "EC_VENTANA_TEMPORAL","EC_CONTEXTO_GEOGRAFICO_SOCIAL","EC_LINEA_FAMILIAR_ENTORNO",
        "EC_MADUREZ_EVOLUTIVA","EC_ESTADO_RELACIONAL_PREVIO","EC_UMBRAL_CRISIS_CAMBIO",
        "EC_DISPARADOR_RECONOCIMIENTO","EC_BLOQUEO_RETRASO","EC_RUTA_ALTERNATIVA","EC_INDETERMINADA"
    }
    if set(encounter_conditions_registry.get("conditions", [])) != expected_encounter_condition_ids:
        fail("encounter conditions registry diverges from canonical condition set")
    for source_id in encounter_conditions_registry.get("source_ids", []):
        if source_id not in source_ids:
            fail(f"unknown source id in encounter-conditions registry: {source_id}")
    if encounter_conditions_example.get("schema_version") != "1.0.0":
        fail("synthetic encounter-conditions example must use schema_version 1.0.0")

    expected_individual_task_ids = {
        "IT_AUTONOMIA","IT_VINCULO","IT_CONFIANZA","IT_VULNERABILIDAD","IT_LIMITES",
        "IT_VERDAD","IT_COMUNICACION","IT_PODER","IT_ENTREGA","IT_RESPONSABILIDAD",
        "IT_ENCARNACION","IT_REPARACION","IT_SERVICIO","IT_INTEGRACION","IT_LIBERACION",
        "IT_MISION_INDIVIDUAL","IT_INDETERMINADA"
    }
    if set(individual_tasks_registry.get("tasks", [])) != expected_individual_task_ids:
        fail("individual tasks registry diverges from canonical task set")
    if individual_tasks_example.get("schema_version") != "1.0.0":
        fail("synthetic individual-tasks example must use schema_version 1.0.0")
    for subject in ("A","B"):
        for task in individual_tasks_example.get("subjects", {}).get(subject, {}).get("tasks", []):
            if task.get("id") not in expected_individual_task_ids:
                fail(f"unknown individual task in synthetic example: {task.get('id')}")

    expected_common_task_ids = {
        "CT_TIKKUN_CONJUNTO","CT_APRENDIZAJE_RECIPROCO","CT_INTEGRACION_POLARIDADES",
        "CT_MISION_SERVICIO","CT_CREACION_MATERIALIZACION","CT_TRANSMISION_ENSENANZA",
        "CT_SANACION_RELACIONAL","CT_TESTIMONIO","CT_CIERRE_CICLO","CT_INDETERMINADA"
    }
    if set(common_task_registry.get("tasks", [])) != expected_common_task_ids:
        fail("common task registry diverges from canonical common-task set")
    for source_id in common_task_registry.get("source_ids", []):
        if source_id not in source_ids:
            fail(f"unknown source id in common-task registry: {source_id}")
    if common_task_example.get("schema_version") != "1.0.0":
        fail("synthetic common-task example must use schema_version 1.0.0")
    for task in common_task_example.get("tasks", []):
        if task.get("id") not in expected_common_task_ids:
            fail(f"unknown common task in synthetic example: {task.get('id')}")
        if task.get("state") == "SUPPORTED" and task.get("emergence_test") != "PASSED":
            fail("SUPPORTED common task requires emergence_test PASSED")

    expected_clause_ids = {
        "CL_ENCUENTRO_RECONOCIMIENTO","CL_VINCULO_AMOROSO","CL_HERIDA_REPARACION",
        "CL_LIBERTAD_AUTONOMIA","CL_COMUNICACION_VERDAD","CL_TRANSFORMACION_PODER",
        "CL_INTEGRACION_ENCARNACION","CL_LIBERACION_CIERRE"
    }
    if set(clause_registry.get("clauses", [])) != expected_clause_ids:
        fail("clause registry diverges from canonical eight-clause set")
    for clause in clause_assembly_example.get("clauses", []):
        if clause.get("id") not in expected_clause_ids:
            fail(f"unknown clause in synthetic clause-assembly example: {clause.get('id')}")
        if clause.get("state") == "SUPPORTED":
            genealogy = clause.get("genealogy", {})
            if not genealogy.get("motive_refs") or not genealogy.get("individual_task_refs") or not clause.get("astrology_root_refs"):
                fail("SUPPORTED clause requires motive, individual-task and astrology-root genealogy")
            if not clause.get("fulfillment_signature"):
                fail("SUPPORTED clause requires preregistered fulfillment signature")

    expected_fulfillment_ids = {
        "FM_ACTIVACION","FM_REPETICION","FM_RECIPROCIDAD","FM_CATALISIS",
        "FM_ENCARNACION","FM_TIKKUN_REPARACION","FM_SERVICIO","FM_LIBERACION",
        "FM_TRANSFORMACION_MODALIDAD","FM_CIERRE","FM_RUTA_ALTERNATIVA","FM_APLAZAMIENTO"
    }
    if set(fulfillment_registry.get("mechanisms", [])) != expected_fulfillment_ids:
        fail("fulfillment mechanism registry diverges from canonical set")
    for source_id in fulfillment_registry.get("source_ids", []):
        if source_id not in source_ids:
            fail(f"unknown source id in fulfillment registry: {source_id}")
    if fulfillment_example.get("schema_version") != "1.0.0":
        fail("synthetic fulfillment example must use schema_version 1.0.0")
    factual_required_states = {"INTEGRADA","TRANSFORMADA","CERRADA"}
    for mechanism in fulfillment_example.get("mechanisms", []):
        if mechanism.get("id") not in expected_fulfillment_ids:
            fail(f"unknown fulfillment mechanism in synthetic example: {mechanism.get('id')}")
        if mechanism.get("functional_state") in factual_required_states and not mechanism.get("fact_refs"):
            fail("integrated/transformed/closed mechanism requires factual evidence")
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

    if "encounter_conditions_differential" not in preincarnation_example:
        fail("synthetic preincarnation example must embed encounter_conditions_differential")
    embedded_encounter = preincarnation_example.get("encounter_conditions_differential", {})
    if embedded_encounter.get("primary_conditions") != encounter_conditions_example.get("primary_conditions"):
        fail("embedded encounter conditions diverge from standalone synthetic example")
    if embedded_encounter.get("why_not_more_specific") != encounter_conditions_example.get("why_not_more_specific"):
        fail("embedded encounter-condition explanation diverges from standalone synthetic example")

    if "individual_tasks_differential" not in preincarnation_example:
        fail("synthetic preincarnation example must embed individual_tasks_differential")
    embedded_individual_tasks = preincarnation_example.get("individual_tasks_differential", {})
    for subject in ("A","B"):
        if embedded_individual_tasks.get("subjects", {}).get(subject, {}).get("primary_tasks") != individual_tasks_example.get("subjects", {}).get(subject, {}).get("primary_tasks"):
            fail(f"embedded individual tasks diverge for subject {subject}")

    if "common_task_differential" not in preincarnation_example:
        fail("synthetic preincarnation example must embed common_task_differential")
    embedded_common = preincarnation_example.get("common_task_differential", {})
    if embedded_common.get("primary_common_tasks") != common_task_example.get("primary_common_tasks"):
        fail("embedded common-task differential diverges from standalone synthetic example")
    if embedded_common.get("why_not_more_specific") != common_task_example.get("why_not_more_specific"):
        fail("embedded common-task explanation diverges from standalone synthetic example")

    if "clause_assembly" not in preincarnation_example:
        fail("synthetic preincarnation example must embed clause_assembly")
    embedded_clauses = preincarnation_example.get("clause_assembly", {})
    if embedded_clauses.get("essential_clauses") != clause_assembly_example.get("essential_clauses"):
        fail("embedded clause assembly diverges from standalone synthetic example")
    if embedded_clauses.get("vertical_coherence") != clause_assembly_example.get("vertical_coherence"):
        fail("embedded clause vertical coherence diverges from standalone example")

    if "fulfillment_mechanisms_differential" not in preincarnation_example:
        fail("synthetic preincarnation example must embed fulfillment_mechanisms_differential")
    embedded_fulfillment = preincarnation_example.get("fulfillment_mechanisms_differential", {})
    if [m.get("id") for m in embedded_fulfillment.get("mechanisms", [])] != [m.get("id") for m in fulfillment_example.get("mechanisms", [])]:
        fail("embedded fulfillment mechanisms diverge from standalone synthetic example")
    if embedded_fulfillment.get("why_not_more_specific") != fulfillment_example.get("why_not_more_specific"):
        fail("embedded fulfillment explanation diverges from standalone synthetic example")

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
    print(f"Contract module: {contract_module_version}")
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
