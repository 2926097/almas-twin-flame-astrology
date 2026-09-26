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
    "docs/ONTOLOGICAL_ADVERSARIAL_TEST_PLAN.md",
    "docs/ONTOLOGICAL_METAMORPHIC_TEST_PLAN.md",
    "docs/ASTROLOGICAL_DISCRIMINATOR_INDEPENDENCE.md",
    "docs/DISCRIMINANT_VALIDATION_POLICY.md",
    "docs/BLINDING_LEAKAGE_POLICY.md",
    "docs/PROMOTION_STATE_MACHINE.md",
    "docs/DISCRIMINATOR_PROMOTION_REPORTING.md",
    "docs/DISCRIMINATOR_SOURCE_GENEALOGY.md",
    "docs/PRIVATE_CASE_ISOLATION_POLICY.md",
    "docs/QUANTITATIVE_CLOSURE_1_13.md",
    "docs/RELEASE_AUDIT_1.13.0.md",
    "docs/SOURCE_ANCHOR_POLICY.md",
    "examples/README.md",
    "examples/manifest.json",
    "public_cases/README.md",
    "public_cases/manifest.json",
    "validation/holdouts/README.md",
    "validation/holdouts/manifest.json",
    "pyproject.toml",
    "schemas/raw-input.schema.json",
    "schemas/canonical-analysis.schema.json",
    "schemas/ontological-discriminator-output.schema.json",
    "schemas/discriminator-promotion-registry.schema.json",
    "schemas/discriminator-promotion-transition.schema.json",
    "schemas/discriminator-promotion-reporting.schema.json",
    "schemas/discriminator-source-genealogy.schema.json",
    "schemas/discriminator-source-genealogy-reporting.schema.json",
    "schemas/public-artifact-manifest.schema.json",
    "schemas/discriminant-validation-evidence.schema.json",
    "schemas/blinding-leakage-audit.schema.json",
    "schemas/operational-discriminator-candidates.schema.json",
    "schemas/natal-chart.schema.json",
    "schemas/synastry-output.schema.json",
    "schemas/natal-context-output.schema.json",
    "schemas/declination-output.schema.json",
    "schemas/antiscia-output.schema.json",
    "schemas/composite-output.schema.json",
    "schemas/davison-output.schema.json",
    "schemas/relationship-chart-consonance.schema.json",
    "schemas/draconic-output.schema.json",
    "schemas/draconic-cross-output.schema.json",
    "schemas/lots-output.schema.json",
    "schemas/secondary-symbolic-output.schema.json",
    "schemas/independent-roots.schema.json",
    "schemas/counterevidence-output.schema.json",
    "schemas/structural-ablation-output.schema.json",
    "schemas/time-sensitivity-output.schema.json",
    "schemas/null-model-output.schema.json",
    "schemas/robustness-output.schema.json",
    "schemas/temporal-activation-output.schema.json",
    "schemas/documentary-event-output.schema.json",
    "schemas/doctrine-hermeneutics-output.schema.json",
    "schemas/viability-reciprocity-assessment.schema.json",
    "schemas/viability-reciprocity-output.schema.json",
    "schemas/report-gate-output.schema.json",
    "schemas/report-document-model.schema.json",
    "schemas/final-pipeline-output.schema.json",
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
    "reference/operational-discriminator-candidates.json",
    "reference/contract-causal-architecture-v2.md",
    "reference/preincarnation-causality-engine.md",
    "reference/contract-ablation.md",
    "reference/contract-metrics.md",
    "reference/contract-free-will.md",
    "reference/contract-temporality-v2.md",
    "reference/documentary-events.md",
    "reference/viability-reciprocity.md",
    "reference/report-gate.md",
    "reference/report-document-model.md",
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
    "src/almas_tfa/discriminator_promotion_registry.py",
    "src/almas_tfa/discriminant_validation.py",
    "src/almas_tfa/blinding_leakage.py",
    "src/almas_tfa/promotion_state_machine.py",
    "src/almas_tfa/promotion_reporting.py",
    "src/almas_tfa/discriminator_source_genealogy.py",
    "src/almas_tfa/public_data_guard.py",
    "src/almas_tfa/data/discriminator-promotion-registry.json",
    "src/almas_tfa/data/discriminant-validation-policy.json",
    "src/almas_tfa/data/blinding-leakage-policy.json",
    "src/almas_tfa/data/promotion-state-machine-policy.json",
    "src/almas_tfa/data/discriminator-source-genealogy.json",
    "src/almas_tfa/data/public-data-isolation-policy.json",
    "src/almas_tfa/data/root-strength-policy.json",
    "src/almas_tfa/data/root-pillar-attribution-policy.json",
    "src/almas_tfa/data/model-attribution-policy.json",
    "src/almas_tfa/data/birth-time-perturbation-policy.json",
    "src/almas_tfa/data/robustness-q5-policy.json",
    "src/almas_tfa/data/null-within-year-policy.json",
    "src/almas_tfa/data/canonical-assembly-policy.json",
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
    "src/almas_tfa/relationship_consonance.py",
    "src/almas_tfa/draconic_handlers.py",
    "src/almas_tfa/lot_handlers.py",
    "src/almas_tfa/secondary_handlers.py",
    "src/almas_tfa/evidence_handlers.py",
    "src/almas_tfa/root_strengths.py",
    "src/almas_tfa/pillar_attribution.py",
    "src/almas_tfa/model_attribution.py",
    "src/almas_tfa/time_perturbation.py",
    "src/almas_tfa/robustness_quantification.py",
    "src/almas_tfa/null_generation.py",
    "src/almas_tfa/canonical_assembly.py",
    "src/almas_tfa/counterevidence_handlers.py",
    "src/almas_tfa/ablation_handlers.py",
    "src/almas_tfa/time_sensitivity_handlers.py",
    "src/almas_tfa/null_model_handlers.py",
    "src/almas_tfa/robustness_handlers.py",
    "src/almas_tfa/robustness_index_handlers.py",
    "src/almas_tfa/temporal_handlers.py",
    "src/almas_tfa/doctrine_handlers.py",
    "src/almas_tfa/reality_handlers.py",
    "src/almas_tfa/report_gate_handlers.py",
    "src/almas_tfa/report_model_handlers.py",
    "src/almas_tfa/final_handlers.py",
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
    "tests/VIABILITY_RECIPROCITY_INVARIANTS.md",
    "tests/REPORT_GATE_INVARIANTS.md",
    "tests/REPORT_DOCUMENT_MODEL_INVARIANTS.md",
    "tests/ONTOLOGICAL_DISCRIMINATOR_ADVERSARIAL_INVARIANTS.md",
    "tests/ONTOLOGICAL_DISCRIMINATOR_METAMORPHIC_INVARIANTS.md",
    "tests/ASTROLOGICAL_DISCRIMINATOR_INDEPENDENCE_INVARIANTS.md",
    "tests/DISCRIMINANT_VALIDATION_INVARIANTS.md",
    "tests/BLINDING_LEAKAGE_INVARIANTS.md",
    "tests/PROMOTION_STATE_MACHINE_INVARIANTS.md",
    "tests/DISCRIMINATOR_SOURCE_GENEALOGY_INVARIANTS.md",
    "tests/PRIVATE_CASE_ISOLATION_INVARIANTS.md",
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
    "tests/test_relationship_consonance.py",
    "tests/test_draconic_handlers.py",
    "tests/test_lot_handlers.py",
    "tests/test_secondary_handlers.py",
    "tests/test_evidence_handlers.py",
    "tests/test_counterevidence_handlers.py",
    "tests/test_ablation_handlers.py",
    "tests/test_time_sensitivity_handlers.py",
    "tests/test_null_model_handlers.py",
    "tests/test_robustness_handlers.py",
    "tests/test_temporal_handlers.py",
    "tests/test_final_handlers.py",
    "tests/test_full_pipeline.py",
    "tests/test_ontological_discriminator_adversarial.py",
    "tests/test_ontological_discriminator_metamorphic.py",
    "tests/test_astrological_discriminator_independence.py",
    "tests/test_discriminant_validation.py",
    "tests/test_blinding_leakage.py",
    "tests/test_promotion_state_machine.py",
    "tests/test_promotion_reporting.py",
    "tests/test_discriminator_source_genealogy.py",
    "tests/test_public_data_guard.py",
    "tests/test_root_strengths.py",
    "tests/test_pillar_attribution.py",
    "tests/test_model_attribution.py",
    "tests/test_m21_auto_idd.py",
    "tests/test_time_perturbation.py",
    "tests/test_robustness_q5.py",
    "tests/test_null_generation.py",
    "tests/test_canonical_assembly.py",
    "tests/test_m18_auto_pillars.py",
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
        "Enfoque de investigación metafísica",
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

    if "ya sean públicos" not in publication_policy:
        fail("la política de publicación debe definir la regla de datos ya públicos")
    if "ALMAS_PUBLIC_DATA_ISOLATION_V1" not in publication_policy:
        fail("publication policy missing public data isolation id")
    if "examples/manifest.json" not in examples_policy:
        fail("examples policy must require examples/manifest.json")
    if "public_cases/manifest.json" not in public_cases_policy:
        fail("public cases policy must require public_cases/manifest.json")
    if "sintétic" not in examples_policy.lower():
        fail("la política de ejemplos debe identificar los fixtures predeterminados como sintéticos")
    if "independientemente verificables" not in public_cases_policy:
        fail("la política de casos públicos debe exigir verificación independiente")

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
    ontological_discriminator_output_schema = load_json(
        "schemas/ontological-discriminator-output.schema.json"
    )
    discriminator_promotion_registry = load_json(
        "src/almas_tfa/data/discriminator-promotion-registry.json"
    )
    discriminant_validation_policy = load_json(
        "src/almas_tfa/data/discriminant-validation-policy.json"
    )
    blinding_leakage_policy = load_json(
        "src/almas_tfa/data/blinding-leakage-policy.json"
    )
    promotion_state_machine_policy = load_json(
        "src/almas_tfa/data/promotion-state-machine-policy.json"
    )
    discriminator_source_genealogy = load_json(
        "src/almas_tfa/data/discriminator-source-genealogy.json"
    )
    public_data_isolation_policy = load_json(
        "src/almas_tfa/data/public-data-isolation-policy.json"
    )
    root_strength_policy = load_json(
        "src/almas_tfa/data/root-strength-policy.json"
    )
    root_pillar_policy = load_json(
        "src/almas_tfa/data/root-pillar-attribution-policy.json"
    )
    model_attribution_policy = load_json(
        "src/almas_tfa/data/model-attribution-policy.json"
    )
    birth_time_perturbation_policy = load_json(
        "src/almas_tfa/data/birth-time-perturbation-policy.json"
    )
    robustness_q5_policy = load_json(
        "src/almas_tfa/data/robustness-q5-policy.json"
    )
    null_generation_policy = load_json(
        "src/almas_tfa/data/null-within-year-policy.json"
    )
    canonical_assembly_policy = load_json(
        "src/almas_tfa/data/canonical-assembly-policy.json"
    )
    public_artifact_manifest_schema = load_json(
        "schemas/public-artifact-manifest.schema.json"
    )
    examples_manifest = load_json("examples/manifest.json")
    public_cases_manifest = load_json("public_cases/manifest.json")
    public_holdouts_manifest = load_json("validation/holdouts/manifest.json")
    operational_discriminator_candidates = load_json(
        "reference/operational-discriminator-candidates.json"
    )
    natal_chart_schema = load_json("schemas/natal-chart.schema.json")
    synastry_schema = load_json("schemas/synastry-output.schema.json")
    natal_context_schema = load_json("schemas/natal-context-output.schema.json")
    declination_schema = load_json("schemas/declination-output.schema.json")
    antiscia_schema = load_json("schemas/antiscia-output.schema.json")
    composite_schema = load_json("schemas/composite-output.schema.json")
    davison_schema = load_json("schemas/davison-output.schema.json")
    relationship_chart_consonance_schema = load_json("schemas/relationship-chart-consonance.schema.json")
    draconic_schema = load_json("schemas/draconic-output.schema.json")
    draconic_cross_schema = load_json("schemas/draconic-cross-output.schema.json")
    lots_schema = load_json("schemas/lots-output.schema.json")
    secondary_symbolic_schema = load_json("schemas/secondary-symbolic-output.schema.json")
    evidence_graph_schema = load_json("schemas/evidence-graph.schema.json")
    deduplicated_evidence_schema = load_json("schemas/deduplicated-evidence.schema.json")
    independent_roots_schema = load_json("schemas/independent-roots.schema.json")
    counterevidence_output_schema = load_json("schemas/counterevidence-output.schema.json")
    structural_ablation_schema = load_json("schemas/structural-ablation-output.schema.json")
    time_sensitivity_schema = load_json("schemas/time-sensitivity-output.schema.json")
    null_model_schema = load_json("schemas/null-model-output.schema.json")
    robustness_output_schema = load_json("schemas/robustness-output.schema.json")
    null_model_output_schema = load_json("schemas/null-model-output.schema.json")
    temporal_activation_schema = load_json("schemas/temporal-activation-output.schema.json")
    documentary_event_output_schema = load_json("schemas/documentary-event-output.schema.json")
    doctrine_output_schema = load_json("schemas/doctrine-hermeneutics-output.schema.json")
    viability_input_schema = load_json("schemas/viability-reciprocity-assessment.schema.json")
    viability_output_schema = load_json("schemas/viability-reciprocity-output.schema.json")
    report_gate_schema = load_json("schemas/report-gate-output.schema.json")
    report_document_model_schema = load_json("schemas/report-document-model.schema.json")
    promotion_reporting_schema = load_json(
        "schemas/discriminator-promotion-reporting.schema.json"
    )
    source_genealogy_schema = load_json(
        "schemas/discriminator-source-genealogy.schema.json"
    )
    source_genealogy_reporting_schema = load_json(
        "schemas/discriminator-source-genealogy-reporting.schema.json"
    )
    final_pipeline_output_schema = load_json("schemas/final-pipeline-output.schema.json")
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

    if almas_module_manifest.get("almas_public_version") != version:
        fail("almas module manifest version diverges from VERSION")
    if discriminator_promotion_registry.get("target_almas_version") != version:
        fail("promotion registry target version diverges from VERSION")
    if discriminator_source_genealogy.get("target_almas_version") != version:
        fail("discriminator source genealogy target version diverges from VERSION")
    if operational_discriminator_candidates.get("target_almas_version") != version:
        fail("operational discriminator target version diverges from VERSION")

    if canonical_schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        fail("canonical astrology schema contract must remain 1.0.0")

    canonical_ontology_ref = (
        canonical_schema.get("properties", {})
        .get("ontological_discrimination", {})
        .get("$ref")
    )
    if canonical_ontology_ref != "ontological-discriminator-output.schema.json":
        fail("canonical analysis must expose ontological_discrimination via its canonical schema")

    if "promotion_trace" not in set(
        ontological_discriminator_output_schema.get("required", [])
    ):
        fail("ontological discriminator output must preserve promotion_trace")

    if "promotion_reporting" not in set(
        report_document_model_schema.get("required", [])
    ):
        fail("report document model must require promotion_reporting")
    if (
        report_document_model_schema.get("properties", {})
        .get("promotion_reporting", {})
        .get("$ref")
        != "discriminator-promotion-reporting.schema.json"
    ):
        fail("report document model promotion_reporting schema ref changed")
    source_genealogy_contract = (
        promotion_reporting_schema.get("properties", {})
        .get("source_genealogy", {})
        .get("anyOf", [])
    )
    if {
        "$ref": "discriminator-source-genealogy-reporting.schema.json"
    } not in source_genealogy_contract:
        fail("promotion reporting source_genealogy schema ref changed")
    if promotion_reporting_schema.get("properties", {}).get(
        "methodological_status_only", {}
    ).get("const") is not True:
        fail("promotion reporting must remain methodological_status_only")
    if promotion_reporting_schema.get("properties", {}).get(
        "ontological_inference_allowed", {}
    ).get("const") is not False:
        fail("promotion reporting must forbid ontological inference")
    if promotion_reporting_schema.get("properties", {}).get(
        "case_classification_mutated", {}
    ).get("const") is not False:
        fail("promotion reporting must not mutate case classification")
    if promotion_reporting_schema.get("properties", {}).get(
        "irc_mutated", {}
    ).get("const") is not False:
        fail("promotion reporting must not mutate IRC")

    registry_validated_ids = set(
        discriminator_promotion_registry.get("validated_discriminator_ids", [])
    )
    registry_authorized_ids = {
        record.get("discriminator_id")
        for record in discriminator_promotion_registry.get("records", [])
        if record.get("l3_authorized") is True
        and record.get("current_status") == "VALIDATED_DISCRIMINATOR"
    }
    if registry_validated_ids != registry_authorized_ids:
        fail("promotion registry validated_discriminator_ids diverges from authorized records")

    expected_current_promotion_states = {
        "OD01_PAIR_SPECIFICITY_NETWORK": "EXPLORATORY",
        "OD02_DYADIC_STRUCTURAL_ISOMORPHISM": "EXPLORATORY",
        "OD03_BLINDED_DOCTRINAL_CODING": "EXPLORATORY",
        "OD04_PROSPECTIVE_MODEL_PREDICTION": "EXPLORATORY",
        "OD05_PRIOR_UNITY_DIRECT": "BLOCKED",
        "OD06_MONADIC_HIERARCHY_DIRECT": "BLOCKED",
        "OD07_PHENOMENOLOGY_CLUSTER": "RETIRED",
    }
    actual_current_promotion_states = {
        record.get("discriminator_id"): record.get("current_status")
        for record in discriminator_promotion_registry.get("records", [])
    }
    if actual_current_promotion_states != expected_current_promotion_states:
        fail("productive promotion states changed during Step 16")
    if registry_validated_ids:
        fail("Step 16 must not create a productive L3 promotion")

    if discriminant_validation_policy.get("policy_id") != "ALMAS_DISCRIMINANT_VALIDATION_V1":
        fail("discriminant validation policy id changed")
    if discriminant_validation_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("discriminant validation thresholds must remain E_PROJECT_POLICY")
    if discriminant_validation_policy.get("confidence_level") != 0.95:
        fail("discriminant validation confidence level must remain 0.95")
    if discriminant_validation_policy.get("uncertainty_method") != "WILSON_SCORE":
        fail("discriminant validation uncertainty method must remain WILSON_SCORE")

    discriminant_minimums = discriminant_validation_policy.get("minimums", {})
    if discriminant_minimums.get("pairwise_sensitivity_ci_lower") != 0.60:
        fail("pairwise sensitivity CI lower threshold changed")
    if discriminant_minimums.get("pairwise_specificity_ci_lower") != 0.90:
        fail("pairwise specificity CI lower threshold changed")
    if discriminant_minimums.get("pairwise_balanced_accuracy") != 0.75:
        fail("pairwise balanced accuracy threshold changed")

    false_specificity_policy = discriminant_validation_policy.get(
        "false_specificity", {}
    )
    if false_specificity_policy.get("max_ci_upper") != 0.05:
        fail("FALSE_SPECIFICITY_RATE CI upper ceiling changed")
    if false_specificity_policy.get("synthetic_adversarial_max_rate") != 0.0:
        fail("synthetic/adversarial false specificity must remain zero")

    if blinding_leakage_policy.get("policy_id") != "ALMAS_BLINDING_LEAKAGE_V1":
        fail("blinding/leakage policy id changed")
    if blinding_leakage_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("blinding/leakage policy must remain E_PROJECT_POLICY")
    if blinding_leakage_policy.get("hash_algorithm") != "sha256":
        fail("blinding/leakage policy must use sha256")
    if blinding_leakage_policy.get("structural_stage") != "STEP_A_BLINDED":
        fail("structural blinding stage changed")
    if blinding_leakage_policy.get("late_reveal_stage") != "STEP_B_DOCUMENTARY_REVEAL":
        fail("late reveal stage changed")

    required_zero_counts = set(
        blinding_leakage_policy.get("required_zero_counts", [])
    )
    expected_zero_counts = {
        "forbidden_field_hits",
        "label_leakage_count",
        "narrative_leakage_count",
        "case_fitting_count",
        "post_holdout_rule_change_count",
    }
    if not expected_zero_counts.issubset(required_zero_counts):
        fail("blinding/leakage zero-count gates are incomplete")

    if promotion_state_machine_policy.get("policy_id") != "ALMAS_PROMOTION_STATE_MACHINE_V1":
        fail("promotion state-machine policy id changed")
    if promotion_state_machine_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("promotion state-machine policy must remain E_PROJECT_POLICY")

    expected_mainline = [
        "EXPLORATORY",
        "REPRODUCIBLE",
        "REPLICATION_READY",
        "CONFIRMATORY_ELIGIBLE",
        "VALIDATED_DISCRIMINATOR",
    ]
    if promotion_state_machine_policy.get("mainline_states") != expected_mainline:
        fail("promotion state-machine mainline changed")
    if promotion_state_machine_policy.get("forward_skips_allowed") is not False:
        fail("promotion state-machine must forbid forward skips")
    if promotion_state_machine_policy.get("validated_rollback_allowed") is not False:
        fail("validated discriminator rollback must remain forbidden")
    if promotion_state_machine_policy.get("retired_is_terminal") is not True:
        fail("RETIRED must remain terminal")
    if promotion_state_machine_policy.get("validated_invalidation_target") != "RETIRED":
        fail("invalidated L3 must retire")

    expected_forward = {
        "EXPLORATORY": "REPRODUCIBLE",
        "REPRODUCIBLE": "REPLICATION_READY",
        "REPLICATION_READY": "CONFIRMATORY_ELIGIBLE",
        "CONFIRMATORY_ELIGIBLE": "VALIDATED_DISCRIMINATOR",
    }
    if promotion_state_machine_policy.get("forward_transitions") != expected_forward:
        fail("promotion forward transitions changed")

    if discriminator_promotion_registry.get("state_machine_policy_id") != "ALMAS_PROMOTION_STATE_MACHINE_V1":
        fail("promotion registry is not bound to the state-machine policy")


    if discriminator_source_genealogy.get("authority") != "ALMAS_CANONICAL_DISCRIMINATOR_SOURCE_GENEALOGY":
        fail("discriminator source genealogy authority changed")
    if discriminator_source_genealogy.get("registry_version") != "1.0.0":
        fail("discriminator source genealogy registry version changed")


    if public_data_isolation_policy.get("policy_id") != "ALMAS_PUBLIC_DATA_ISOLATION_V1":
        fail("public data isolation policy id changed")
    if public_data_isolation_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("public data isolation policy must remain E_PROJECT_POLICY")
    if public_data_isolation_policy.get("repository_mode") != "PUBLIC":
        fail("public data isolation policy must remain PUBLIC")

    if root_strength_policy.get("policy_id") != "ALMAS_ROOT_STRENGTH_BASELINE_V1":
        fail("root strength policy id changed")
    if root_strength_policy.get("status") != "FROZEN_NEUTRAL_BASELINE":
        fail("root strength baseline must remain frozen and neutral")
    if root_strength_policy.get("principles", {}).get("case_fitting_forbidden") is not True:
        fail("root strength policy must forbid case fitting")

    if root_pillar_policy.get("policy_id") != "ALMAS_ROOT_PILLAR_ATTRIBUTION_V1":
        fail("root to pillar policy id changed")
    if root_pillar_policy.get("status") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("root to pillar policy must remain a frozen experimental baseline")
    if root_pillar_policy.get("epistemic_class") != "E_PROJECT_HYPOTHESIS":
        fail("root to pillar attribution must remain E_PROJECT_HYPOTHESIS")
    pillar_principles = root_pillar_policy.get("principles", {})
    if pillar_principles.get("case_fitting_forbidden") is not True:
        fail("root to pillar policy must forbid case fitting")
    if pillar_principles.get("single_semantic_primary_pillar") is not True:
        fail("root to pillar policy must keep semantic pillar exclusivity")
    if pillar_principles.get("pu_automatic_attribution_forbidden") is not True:
        fail("PU automatic attribution must remain forbidden")

    if model_attribution_policy.get("policy_id") != "ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V1":
        fail("model attribution policy id changed")
    if model_attribution_policy.get("status") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("model attribution policy must remain frozen")
    if model_attribution_policy.get("epistemic_class") != "E_PROJECT_HYPOTHESIS":
        fail("model attribution policy must remain E_PROJECT_HYPOTHESIS")
    if model_attribution_policy.get("value_function") != "IEM_PRE":
        fail("M21 automatic attribution must use IEM_PRE")
    attribution_principles = model_attribution_policy.get("principles", {})
    if attribution_principles.get("case_fitting_forbidden") is not True:
        fail("model attribution policy must forbid case fitting")
    if attribution_principles.get("idd_is_not_ontological_discriminator") is not True:
        fail("IDD must remain separated from ontological discrimination")
    if attribution_principles.get("ice_not_used_for_attribution") is not True:
        fail("ICE must remain outside Shapley attribution value function")

    if birth_time_perturbation_policy.get("policy_id") != "ALMAS_BIRTH_TIME_PERTURBATION_V1":
        fail("birth-time perturbation policy id changed")
    if birth_time_perturbation_policy.get("status") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("birth-time perturbation policy must remain frozen")
    if birth_time_perturbation_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("birth-time perturbation policy must remain E_PROJECT_POLICY")
    q4_principles = birth_time_perturbation_policy.get("principles", {})
    if q4_principles.get("case_fitting_forbidden") is not True:
        fail("birth-time perturbation policy must forbid case fitting")
    if q4_principles.get("all_generated_samples_must_be_evaluable") is not True:
        fail("Q4 must fail closed when a generated perturbation is not evaluable")
    q4_metric = birth_time_perturbation_policy.get("metric", {})
    if q4_metric.get("percentile_method") != "NEAREST_RANK":
        fail("Q4 percentile method must remain NEAREST_RANK")
    if q4_metric.get("preserved_fraction") != "MEAN_BASELINE_CORE_ROOT_RETENTION":
        fail("Q4 preserved_fraction metric changed")

    if robustness_q5_policy.get("policy_id") != "ALMAS_ROBUSTNESS_Q5_V1":
        fail("Q5 robustness policy id changed")
    if robustness_q5_policy.get("status") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("Q5 robustness policy must remain frozen")
    if robustness_q5_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("Q5 robustness policy must remain E_PROJECT_POLICY")
    q5_principles = robustness_q5_policy.get("principles", {})
    if q5_principles.get("case_fitting_forbidden") is not True:
        fail("Q5 robustness policy must forbid case fitting")
    if q5_principles.get("null_rarity_used") is not False:
        fail("Q5 must exclude null rarity from IRC")
    if q5_principles.get("validated_discriminator_auto_created") is not False:
        fail("Q5 must not auto-create L3 discriminator components")
    if robustness_q5_policy.get("parameter_perturbation", {}).get("orb_scale_factors") != [0.9, 0.95, 1.05, 1.1]:
        fail("Q5 orb perturbation factors changed")
    if robustness_q5_policy.get("idd_stability", {}).get("source_samples") != "PARAMETER_PERTURBATION":
        fail("Q5 IDD stability must reuse parameter perturbation samples")

    if null_generation_policy.get("policy_id") != "ALMAS_NULL_WITHIN_YEAR_V1":
        fail("Q6 null generation policy id changed")
    if null_generation_policy.get("status") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("Q6 null generation policy must remain frozen")
    if null_generation_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("Q6 null generation policy must remain E_PROJECT_POLICY")
    if null_generation_policy.get("null_model") != "WITHIN_YEAR":
        fail("Q6 self-contained generator must remain WITHIN_YEAR")
    q6_generator = null_generation_policy.get("generator", {})
    if q6_generator.get("name") != "DETERMINISTIC_STRATIFIED_CALENDAR_DATE":
        fail("Q6 generator identity changed")
    if q6_generator.get("samples_per_subject") != 32:
        fail("Q6 samples_per_subject changed")
    q6_principles = null_generation_policy.get("principles", {})
    if q6_principles.get("case_fitting_forbidden") is not True:
        fail("Q6 must forbid case fitting")
    if q6_principles.get("metaphysical_probability") is not False:
        fail("Q6 must forbid metaphysical probability")
    if q6_principles.get("null_rarity_used_as_irc") is not False:
        fail("Q6 null rarity must remain outside IRC")
    if q6_principles.get("no_external_population_claim") is not True:
        fail("Q6 self-contained null must not claim an external population")
    if q6_principles.get("combined_p_value_forbidden") is not True:
        fail("Q6 must forbid combined p-value")

    if canonical_assembly_policy.get("policy_id") != "ALMAS_CANONICAL_ASSEMBLY_V1":
        fail("Q7 canonical assembly policy id changed")
    if canonical_assembly_policy.get("status") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("Q7 canonical assembly policy must remain frozen")
    if canonical_assembly_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("Q7 canonical assembly policy must remain E_PROJECT_POLICY")
    q7_principles = canonical_assembly_policy.get("principles", {})
    if q7_principles.get("case_fitting_forbidden") is not True:
        fail("Q7 canonical assembly must forbid case fitting")
    if q7_principles.get("existing_canonical_never_overwritten") is not True:
        fail("Q7 must not overwrite an existing canonical_analysis")
    if q7_principles.get("assembler_recalculates_astrology") is not False:
        fail("Q7 assembler must not recalculate astrology")
    if q7_principles.get("assembler_recalculates_roots") is not False:
        fail("Q7 assembler must not recalculate roots")
    if q7_principles.get("assembler_recalculates_pillars") is not False:
        fail("Q7 assembler must not recalculate pillars")
    if canonical_assembly_policy.get("global_idd", {}).get("method") != "MIN_EVALUABLE_PAIRWISE_IDD":
        fail("Q7 global IDD aggregation changed")
    if canonical_assembly_policy.get("model_state", {}).get("supported_requires_evaluable_ice") is not True:
        fail("Q7 SUPPORTED must require evaluable ICE")
    q7_domains = canonical_assembly_policy.get("coverage", {}).get("domains", [])
    if len(q7_domains) != 7 or len(set(q7_domains)) != 7:
        fail("Q7 canonical coverage must retain seven unique domains")

    allowed_public_classes = set(
        public_data_isolation_policy.get("allowed_public_classifications", [])
    )
    if allowed_public_classes != {
        "SYNTHETIC",
        "PUBLIC_VERIFIABLE",
        "PUBLIC_METADATA_ONLY",
    }:
        fail("public data allowed classifications changed")

    forbidden_public_classes = set(
        public_data_isolation_policy.get("forbidden_public_classifications", [])
    )
    if forbidden_public_classes != {
        "PRIVATE_CASE",
        "PSEUDONYMIZED_PRIVATE",
        "PRIVATE_HOLDOUT",
        "CONFIDENTIAL",
    }:
        fail("public data forbidden classifications changed")

    privacy_scopes = public_data_isolation_policy.get("governed_scopes", {})
    expected_privacy_scopes = {
        "examples": {
            "root": "examples",
            "manifest": "examples/manifest.json",
            "allowed_classifications": ["SYNTHETIC"],
        },
        "public_cases": {
            "root": "public_cases",
            "manifest": "public_cases/manifest.json",
            "allowed_classifications": ["PUBLIC_VERIFIABLE"],
        },
        "public_holdouts": {
            "root": "validation/holdouts",
            "manifest": "validation/holdouts/manifest.json",
            "allowed_classifications": [
                "SYNTHETIC",
                "PUBLIC_VERIFIABLE",
                "PUBLIC_METADATA_ONLY",
            ],
        },
    }
    if privacy_scopes != expected_privacy_scopes:
        fail("public data governed scopes changed")

    privacy_manifests = {
        "examples": examples_manifest,
        "public_cases": public_cases_manifest,
        "public_holdouts": public_holdouts_manifest,
    }
    forbidden_payload_keys = {
        str(item).lower()
        for item in public_data_isolation_policy.get(
            "forbidden_public_payload_keys", []
        )
    }

    def iter_payload_keys(value, prefix=""):
        if isinstance(value, dict):
            for key, nested in value.items():
                key_text = str(key)
                path = f"{prefix}.{key_text}" if prefix else key_text
                yield path, key_text
                yield from iter_payload_keys(nested, path)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                path = f"{prefix}[{index}]" if prefix else f"[{index}]"
                yield from iter_payload_keys(nested, path)

    for scope_name, scope_policy in privacy_scopes.items():
        manifest = privacy_manifests[scope_name]
        if manifest.get("policy_id") != "ALMAS_PUBLIC_DATA_ISOLATION_V1":
            fail(f"privacy manifest policy mismatch: {scope_name}")
        if manifest.get("scope") != scope_name:
            fail(f"privacy manifest scope mismatch: {scope_name}")
        if manifest.get("root") != scope_policy["root"]:
            fail(f"privacy manifest root mismatch: {scope_name}")
        if manifest.get("allowed_classifications") != scope_policy[
            "allowed_classifications"
        ]:
            fail(f"privacy manifest classifications mismatch: {scope_name}")

        artifacts = manifest.get("artifacts", [])
        if not isinstance(artifacts, list):
            fail(f"privacy manifest artifacts invalid: {scope_name}")

        declared_paths = []
        by_path = {}
        for artifact in artifacts:
            path = artifact.get("path")
            if not isinstance(path, str) or not path:
                fail(f"privacy manifest path invalid: {scope_name}")
            declared_paths.append(path)
            if path in by_path:
                fail(f"privacy manifest duplicate path: {path}")
            by_path[path] = artifact

            classification = artifact.get("classification")
            if classification in forbidden_public_classes:
                fail(f"private classification committed publicly: {path}")
            if classification not in set(
                scope_policy["allowed_classifications"]
            ):
                fail(f"classification not allowed in scope: {path}")

            for key in (
                "contains_real_person_data",
                "contains_nonpublic_material",
                "derived_from_private_case",
                "reversible_from_private_case",
                "independently_verifiable",
            ):
                if not isinstance(artifact.get(key), bool):
                    fail(f"privacy metadata {key} invalid: {path}")

            refs = artifact.get("public_source_refs")
            if (
                not isinstance(refs, list)
                or not all(isinstance(item, str) and item for item in refs)
            ):
                fail(f"public_source_refs invalid: {path}")

            if classification == "SYNTHETIC":
                for key in (
                    "contains_real_person_data",
                    "contains_nonpublic_material",
                    "derived_from_private_case",
                    "reversible_from_private_case",
                ):
                    if artifact.get(key) is not False:
                        fail(f"synthetic privacy invariant failed {key}: {path}")
                if refs:
                    fail(f"synthetic fixture must not depend on real-case refs: {path}")

            if classification == "PUBLIC_VERIFIABLE":
                if artifact.get("independently_verifiable") is not True:
                    fail(f"public case not independently verifiable: {path}")
                if not refs:
                    fail(f"public case lacks source refs: {path}")
                for key in (
                    "contains_nonpublic_material",
                    "derived_from_private_case",
                    "reversible_from_private_case",
                ):
                    if artifact.get(key) is not False:
                        fail(f"public case privacy invariant failed {key}: {path}")

            if classification == "PUBLIC_METADATA_ONLY":
                for key in (
                    "contains_nonpublic_material",
                    "derived_from_private_case",
                    "reversible_from_private_case",
                ):
                    if artifact.get(key) is not False:
                        fail(f"public metadata privacy invariant failed {key}: {path}")

        scope_root = ROOT / scope_policy["root"]
        actual_paths = set()
        if scope_root.exists():
            for json_path in scope_root.rglob("*.json"):
                rel = json_path.relative_to(ROOT).as_posix()
                if rel == scope_policy["manifest"]:
                    continue
                actual_paths.add(rel)

        if actual_paths != set(declared_paths):
            fail(
                f"privacy manifest coverage mismatch {scope_name}: "
                f"actual={sorted(actual_paths)} declared={sorted(declared_paths)}"
            )

        for rel in sorted(actual_paths):
            payload = load_json(rel)
            forbidden_hits = [
                path
                for path, key in iter_payload_keys(payload)
                if key.lower() in forbidden_payload_keys
            ]
            if forbidden_hits:
                fail(
                    f"public payload contains forbidden private keys {rel}: "
                    + ", ".join(forbidden_hits)
                )

    for forbidden_path in public_data_isolation_policy.get(
        "forbidden_repository_paths", []
    ):
        if (ROOT / forbidden_path).exists():
            fail(f"private repository path present: {forbidden_path}")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required_gitignore_entries = {
        "private_cases/",
        "local_cases/",
        ".almas-private/",
        "private_holdouts/",
        "validation/private/",
        "holdouts/private/",
        "data/private/",
        "*.private-case.json",
        "*.private-holdout.json",
    }
    for entry in required_gitignore_entries:
        if entry not in gitignore:
            fail(f"private path missing from .gitignore: {entry}")

    artifact_props = (
        public_artifact_manifest_schema.get("properties", {})
        .get("artifacts", {})
        .get("items", {})
        .get("properties", {})
    )
    if "PRIVATE_CASE" in set(
        artifact_props.get("classification", {}).get("enum", [])
    ):
        fail("public artifact schema must not admit PRIVATE_CASE")

    source_entries = {
        entry.get("id"): entry
        for entry in source_registry.get("entries", [])
    }
    source_snapshots = {
        entry.get("id"): entry
        for entry in discriminator_source_genealogy.get("source_snapshots", [])
    }
    if len(source_snapshots) != len(
        discriminator_source_genealogy.get("source_snapshots", [])
    ):
        fail("duplicate source snapshot in discriminator genealogy")

    genealogy_records = {
        record.get("discriminator_id"): record
        for record in discriminator_source_genealogy.get("records", [])
    }
    operational_candidate_map = {
        item.get("id"): item
        for item in operational_discriminator_candidates.get("candidates", [])
    }
    if set(genealogy_records) != set(operational_candidate_map):
        fail(
            "discriminator source genealogy does not cover "
            "operational candidates exactly"
        )

    used_source_ids = set()
    snapshot_fields = (
        "priority",
        "source_role",
        "tradition",
        "author",
        "work",
        "date",
        "date_note",
        "passage",
        "pages",
        "verification_status",
        "verification_anchor",
        "verification_anchor_type",
        "verification_anchor_url",
        "evidence_scope",
        "concepts",
    )
    doctrinal_edge_set = {
        (
            edge.get("from"),
            edge.get("to"),
            edge.get("relation"),
            edge.get("status"),
        )
        for edge in doctrinal_genealogy.get("edges", [])
    }
    concept_map = {
        item.get("id"): item
        for item in concept_registry.get("concepts", [])
    }
    non_identity_relations = {
        "NON_EQUIVALENT",
        "COMPARATIVE_ANTECEDENT_ONLY",
        "COMPARATIVE_MOTIF_ONLY",
        "MODERN_REINTERPRETATION_NOT_IDENTITY",
        "TERMINOLOGICAL_ANTECEDENT_NOT_DOCTRINAL_IDENTITY",
        "PHENOMENOLOGY_NOT_ONTOLOGY",
        "SELF_LABEL_NOT_DOCTRINAL_VERIFICATION",
        "NON_DISCRIMINATING_PHENOMENOLOGY",
        "DOCTRINAL_NEIGHBOR_NOT_IDENTITY",
        "NO_DIRECT_DOCTRINAL_IDENTITY",
    }
    expected_genealogy_ceilings = {
        "OD01_PAIR_SPECIFICITY_NETWORK": "PROJECT_PROXY_ONLY",
        "OD02_DYADIC_STRUCTURAL_ISOMORPHISM": "PROJECT_PROXY_ONLY",
        "OD03_BLINDED_DOCTRINAL_CODING": "CONSTRUCT_SEPARABILITY_ONLY",
        "OD04_PROSPECTIVE_MODEL_PREDICTION": "PROJECT_PROXY_ONLY",
        "OD05_PRIOR_UNITY_DIRECT": "DOCTRINAL_CONCEPT_ONLY",
        "OD06_MONADIC_HIERARCHY_DIRECT": "DOCTRINAL_CONCEPT_ONLY",
        "OD07_PHENOMENOLOGY_CLUSTER": "PHENOMENOLOGY_ONLY",
    }

    for discriminator_id, record in genealogy_records.items():
        candidate = operational_candidate_map[discriminator_id]
        if record.get("derived_from") != candidate.get("derived_from"):
            fail(f"genealogy derived_from mismatch: {discriminator_id}")
        if record.get("epistemic_class") != candidate.get("epistemic_class"):
            fail(f"genealogy epistemic class mismatch: {discriminator_id}")
        if (
            record.get("epistemic_ceiling")
            != expected_genealogy_ceilings[discriminator_id]
        ):
            fail(f"genealogy epistemic ceiling mismatch: {discriminator_id}")

        for key in (
            "source_count_adds_weight",
            "source_priority_adds_ontological_weight",
            "cross_tradition_identity_allowed",
            "direct_case_evidence",
            "can_change_case_classification",
            "can_raise_irc",
        ):
            if record.get(key) is not False:
                fail(
                    f"genealogy firewall changed {key}: "
                    f"{discriminator_id}"
                )

        source_usage = record.get("source_usage", [])
        if not isinstance(source_usage, list) or not source_usage:
            fail(f"genealogy source_usage missing: {discriminator_id}")

        for usage in source_usage:
            source_id = usage.get("source_id")
            used_source_ids.add(source_id)
            source = source_entries.get(source_id)
            snapshot = source_snapshots.get(source_id)
            if not isinstance(source, dict) or not isinstance(snapshot, dict):
                fail(f"genealogy references unknown source: {source_id}")

            for field in snapshot_fields:
                if snapshot.get(field) != source.get(field):
                    fail(f"source snapshot drift {source_id}.{field}")

            source_concepts = set(source.get("concepts", []))
            if not set(usage.get("concept_refs", [])).issubset(
                source_concepts
            ):
                fail(
                    f"genealogy concept ref not present in source: "
                    f"{source_id}"
                )

            supports = source.get("supports", [])
            for index in usage.get("support_indexes", []):
                if (
                    not isinstance(index, int)
                    or index < 0
                    or index >= len(supports)
                ):
                    fail(f"invalid supports index for {source_id}")

            limitations = source.get("does_not_support", [])
            limitation_indexes = usage.get("does_not_support_indexes", [])
            if (
                not isinstance(limitation_indexes, list)
                or not limitation_indexes
            ):
                fail(
                    f"genealogy must preserve does_not_support "
                    f"for {source_id}"
                )
            for index in limitation_indexes:
                if (
                    not isinstance(index, int)
                    or index < 0
                    or index >= len(limitations)
                ):
                    fail(
                        f"invalid does_not_support index for {source_id}"
                    )

            if usage.get("direct_case_evidence") is not False:
                fail(
                    f"source usage became direct case evidence: "
                    f"{discriminator_id}"
                )
            if usage.get("ontological_validation") is not False:
                fail(
                    f"source usage became ontological validation: "
                    f"{discriminator_id}"
                )

            if (
                source.get("priority") == "P1_PRIMARY"
                and source.get("source_role") == "DOCTRINAL_PRIMARY"
                and usage.get("relation") in {
                    "DIRECT_DOCTRINAL_BASIS",
                    "MONADIC_DOCTRINAL_BASIS",
                }
            ):
                if not source.get("verification_anchor"):
                    fail(
                        f"P1 doctrinal genealogy source lacks anchor: "
                        f"{source_id}"
                    )
                if source.get("verification_anchor_type") not in {
                    "EXACT_PASSAGE",
                    "SECTION",
                    "CHAPTER",
                }:
                    fail(
                        f"P1 doctrinal genealogy source has weak anchor: "
                        f"{source_id}"
                    )
                if source.get("evidence_scope") != "DOCTRINAL_CLAIM":
                    fail(
                        f"P1 doctrinal genealogy source scope changed: "
                        f"{source_id}"
                    )

        for edge in record.get("required_genealogy_edges", []):
            signature = (
                edge.get("from"),
                edge.get("to"),
                edge.get("relation"),
                edge.get("status"),
            )
            if signature not in doctrinal_edge_set:
                fail(f"required genealogy edge missing: {signature}")

        for pair in record.get("forbidden_equivalences", []):
            if not isinstance(pair, list) or len(pair) != 2:
                fail(
                    f"invalid forbidden equivalence: {discriminator_id}"
                )
            a, b = pair
            concept_a = concept_map.get(a, {})
            concept_b = concept_map.get(b, {})
            concept_backed = (
                b in set(concept_a.get("not_equivalent_to", []))
                or a in set(concept_b.get("not_equivalent_to", []))
            )
            edge_backed = any(
                (
                    (
                        edge.get("from") == a
                        and edge.get("to") == b
                    )
                    or (
                        edge.get("from") == b
                        and edge.get("to") == a
                    )
                )
                and edge.get("relation") in non_identity_relations
                for edge in doctrinal_genealogy.get("edges", [])
            )
            if not (concept_backed or edge_backed):
                fail(
                    "forbidden equivalence lacks genealogical backing: "
                    f"{discriminator_id} {a}<->{b}"
                )

    if used_source_ids != set(source_snapshots):
        fail(
            "source genealogy snapshots must equal "
            "the exact used source set"
        )

    if (
        source_genealogy_schema.get("properties", {})
        .get("records", {})
        .get("items", {})
        .get("properties", {})
        .get("source_count_adds_weight", {})
        .get("const")
        is not False
    ):
        fail(
            "source genealogy schema must keep "
            "source_count_adds_weight=false"
        )

    if (
        source_genealogy_reporting_schema.get("properties", {})
        .get("source_count_adds_weight", {})
        .get("const")
        is not False
    ):
        fail(
            "source genealogy reporting must keep "
            "source_count_adds_weight=false"
        )
    if (
        source_genealogy_reporting_schema.get("properties", {})
        .get("source_priority_adds_ontological_weight", {})
        .get("const")
        is not False
    ):
        fail(
            "source genealogy reporting must keep priority weight false"
        )

    expected_promotion_evidence_keys = {
        "implementation_refs",
        "reproducibility_refs",
        "synthetic_test_refs",
        "preregistration_refs",
        "counterevidence_refs",
        "negative_control_plan_refs",
        "leakage_plan_refs",
        "independent_replication_refs",
        "negative_control_result_refs",
        "doctrine_gate_refs",
        "discriminator_evaluation_refs",
        "holdout_protocol_refs",
        "support_only_exclusion_refs",
    }

    for record in discriminator_promotion_registry.get("records", []):
        promotion_evidence = record.get("promotion_evidence")
        if not isinstance(promotion_evidence, dict):
            fail(
                f"promotion registry record lacks promotion_evidence: "
                f"{record.get('discriminator_id')}"
            )
        if set(promotion_evidence) != expected_promotion_evidence_keys:
            fail(
                f"promotion_evidence keys diverge: "
                f"{record.get('discriminator_id')}"
            )
        state_history = record.get("state_history")
        if not isinstance(state_history, list) or not state_history:
            fail(
                f"promotion registry record lacks state_history: "
                f"{record.get('discriminator_id')}"
            )
        if state_history[-1].get("to_status") != record.get("current_status"):
            fail(
                f"state_history current status mismatch: "
                f"{record.get('discriminator_id')}"
            )
        transition_ids = [event.get("transition_id") for event in state_history]
        if len(transition_ids) != len(set(transition_ids)):
            fail(
                f"duplicate promotion transition_id: "
                f"{record.get('discriminator_id')}"
            )
        if (
            record.get("current_status") != "VALIDATED_DISCRIMINATOR"
            and record.get("l3_authorized") is True
        ):
            fail(
                f"non-L3 record cannot be l3_authorized: "
                f"{record.get('discriminator_id')}"
            )
        if "discriminant_validation" not in record:
            fail(
                f"promotion registry record lacks discriminant_validation: "
                f"{record.get('discriminator_id')}"
            )
        if "blinding_audit" not in record:
            fail(
                f"promotion registry record lacks blinding_audit: "
                f"{record.get('discriminator_id')}"
            )
        if (
            record.get("l3_authorized") is True
            and record.get("current_status") == "VALIDATED_DISCRIMINATOR"
            and not isinstance(record.get("discriminant_validation"), dict)
        ):
            fail(
                f"authorized L3 lacks discriminant_validation: "
                f"{record.get('discriminator_id')}"
            )
        if (
            record.get("l3_authorized") is True
            and record.get("current_status") == "VALIDATED_DISCRIMINATOR"
            and not isinstance(record.get("blinding_audit"), dict)
        ):
            fail(
                f"authorized L3 lacks blinding_audit: "
                f"{record.get('discriminator_id')}"
            )

    discriminant_doc = (
        ROOT / "docs/DISCRIMINANT_VALIDATION_POLICY.md"
    ).read_text(encoding="utf-8")
    for token in (
        "ALMAS_DISCRIMINANT_VALIDATION_V1",
        "FALSE_SPECIFICITY_RATE",
        "WILSON_SCORE",
        "Paso 15",
    ):
        if token not in discriminant_doc:
            fail("discriminant validation policy documentation is incomplete")

    blinding_doc = (
        ROOT / "docs/BLINDING_LEAKAGE_POLICY.md"
    ).read_text(encoding="utf-8")
    for token in (
        "ALMAS_BLINDING_LEAKAGE_V1",
        "LABEL_LEAKAGE",
        "NARRATIVE_LEAKAGE",
        "CASE_FITTING",
        "Paso 16",
    ):
        if token not in blinding_doc:
            fail("blinding/leakage policy documentation is incomplete")

    blinding_invariants = (
        ROOT / "tests/BLINDING_LEAKAGE_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "STEP_A",
        "LABEL_LEAKAGE",
        "NARRATIVE_LEAKAGE",
        "CASE_FITTING",
        "fingerprint",
    ):
        if token not in blinding_invariants:
            fail("blinding/leakage invariants are incomplete")

    promotion_machine_doc = (
        ROOT / "docs/PROMOTION_STATE_MACHINE.md"
    ).read_text(encoding="utf-8")
    for token in (
        "ALMAS_PROMOTION_STATE_MACHINE_V1",
        "REPRODUCIBLE",
        "REPLICATION_READY",
        "CONFIRMATORY_ELIGIBLE",
        "Paso 17",
    ):
        if token not in promotion_machine_doc:
            fail("promotion state-machine documentation is incomplete")

    private_case_policy_doc = (
        ROOT / "docs/PRIVATE_CASE_ISOLATION_POLICY.md"
    ).read_text(encoding="utf-8")
    for token in (
        "ALMAS_PUBLIC_DATA_ISOLATION_V1",
        "PSEUDONYMIZED_PRIVATE",
        "PRIVACY_BREACH",
        "Paso 20",
    ):
        if token not in private_case_policy_doc:
            fail("private case isolation documentation is incomplete")

    private_case_invariants = (
        ROOT / "tests/PRIVATE_CASE_ISOLATION_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "PRIVATE_CASE",
        "PRIVATE_HOLDOUT",
        "public_source_refs",
        "PRIVACY_BREACH",
    ):
        if token not in private_case_invariants:
            fail("private case isolation invariants are incomplete")

    source_genealogy_doc = (
        ROOT / "docs/DISCRIMINATOR_SOURCE_GENEALOGY.md"
    ).read_text(encoding="utf-8")
    for token in (
        "ALMAS_CANONICAL_DISCRIMINATOR_SOURCE_GENEALOGY",
        "source_count_adds_weight=false",
        "does_not_support",
        "Paso 19",
    ):
        if token not in source_genealogy_doc:
            fail(
                "discriminator source genealogy documentation "
                "is incomplete"
            )

    source_genealogy_invariants = (
        ROOT / "tests/DISCRIMINATOR_SOURCE_GENEALOGY_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "derived_from",
        "does_not_support",
        "PROJECT_PROXY_ONLY",
        "PHENOMENOLOGY_ONLY",
    ):
        if token not in source_genealogy_invariants:
            fail(
                "discriminator source genealogy invariants "
                "are incomplete"
            )

    promotion_reporting_doc = (
        ROOT / "docs/DISCRIMINATOR_PROMOTION_REPORTING.md"
    ).read_text(encoding="utf-8")
    for token in (
        "METHODOLOGICAL_STATUS_ONLY",
        "ontological_inference_allowed=false",
        "can_raise_irc=false",
        "Paso 18",
    ):
        if token not in promotion_reporting_doc:
            fail("promotion reporting documentation is incomplete")

    report_model_invariants = (
        ROOT / "tests/REPORT_DOCUMENT_MODEL_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "promotion_reporting",
        "ontological_weight=0",
        "can_change_case_classification=false",
        "validated_discriminator_ids=[]",
    ):
        if token not in report_model_invariants:
            fail("report-document-model promotion invariants are incomplete")

    promotion_machine_invariants = (
        ROOT / "tests/PROMOTION_STATE_MACHINE_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "Ningún salto ascendente",
        "RETIRED es terminal",
        "transition_id",
        "validated_discriminator_ids",
    ):
        if token not in promotion_machine_invariants:
            fail("promotion state-machine invariants are incomplete")

    discriminant_invariants = (
        ROOT / "tests/DISCRIMINANT_VALIDATION_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "CI95 inferior de especificidad < 0.90",
        "FALSE_SPECIFICITY_RATE",
        "calibración",
    ):
        if token not in discriminant_invariants:
            fail("discriminant validation invariants are incomplete")

    astro_ids = {
        "OD01_PAIR_SPECIFICITY_NETWORK",
        "OD02_DYADIC_STRUCTURAL_ISOMORPHISM",
        "OD04_PROSPECTIVE_MODEL_PREDICTION",
    }
    promotion_records = {
        record.get("discriminator_id"): record
        for record in discriminator_promotion_registry.get("records", [])
    }
    for discriminator_id, record in promotion_records.items():
        if not isinstance(record.get("uses_astrology"), bool):
            fail(f"promotion registry record lacks uses_astrology boolean: {discriminator_id}")
        if "astrology_validation" not in record:
            fail(f"promotion registry record lacks astrology_validation: {discriminator_id}")

    for discriminator_id in astro_ids:
        record = promotion_records.get(discriminator_id)
        if not isinstance(record, dict):
            fail(f"missing astrological discriminator record: {discriminator_id}")
        if record.get("uses_astrology") is not True:
            fail(f"astrological discriminator not marked uses_astrology: {discriminator_id}")
        if record.get("l3_authorized") is True and not isinstance(
            record.get("astrology_validation"), dict
        ):
            fail(f"astrological L3 lacks astrology_validation: {discriminator_id}")

    required_astro_refs = {
        "non_astrological_criterion_refs",
        "astrology_ablation_refs",
        "matched_control_refs",
        "dependency_audit_refs",
        "out_of_sample_refs",
        "astrology_specific_replication_refs",
    }
    for discriminator_id, record in promotion_records.items():
        if record.get("uses_astrology") is not True:
            continue
        if (
            record.get("l3_authorized") is not True
            or record.get("current_status") != "VALIDATED_DISCRIMINATOR"
        ):
            continue
        validation = record.get("astrology_validation")
        if not isinstance(validation, dict):
            fail(f"astrological L3 lacks validation object: {discriminator_id}")
        for key in required_astro_refs:
            value = validation.get(key)
            if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item for item in value
            ):
                fail(f"astrological L3 lacks required refs {key}: {discriminator_id}")
        for key in (
            "single_feature_prohibition_acknowledged",
            "null_rarity_not_ontological",
            "temporal_activation_not_origin_proof",
        ):
            if validation.get(key) is not True:
                fail(f"astrological L3 lacks invariant {key}: {discriminator_id}")

    operational_candidates = {
        item.get("id"): item
        for item in operational_discriminator_candidates.get("candidates", [])
    }
    for discriminator_id in astro_ids:
        candidate = operational_candidates.get(discriminator_id)
        if not isinstance(candidate, dict):
            fail(f"missing operational astrological candidate: {discriminator_id}")
        if candidate.get("uses_astrology") is not True:
            fail(f"operational candidate astrology flag mismatch: {discriminator_id}")

    astrology_policy = operational_discriminator_candidates.get(
        "astrology_independence_policy", {}
    )
    if astrology_policy.get("single_feature_can_confirm") is not False:
        fail("single astrological feature must not confirm ontology")
    if astrology_policy.get("null_rarity_is_metaphysical_probability") is not False:
        fail("null rarity must not become metaphysical probability")
    if astrology_policy.get("temporal_activation_proves_origin") is not False:
        fail("temporal activation must not prove origin")

    astrology_doc = (
        ROOT / "docs/ASTROLOGICAL_DISCRIMINATOR_INDEPENDENCE.md"
    ).read_text(encoding="utf-8")
    for token in (
        "non_astrological_criterion_refs",
        "single_feature_prohibition_acknowledged",
        "Paso 14",
    ):
        if token not in astrology_doc:
            fail("astrological discriminator independence contract is incomplete")

    astrology_invariants = (
        ROOT / "tests/ASTROLOGICAL_DISCRIMINATOR_INDEPENDENCE_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "uses_astrology=true",
        "null_rarity_not_ontological",
        "M25",
    ):
        if token not in astrology_invariants:
            fail("astrological discriminator independence invariants are incomplete")

    adversarial_plan = (
        ROOT / "docs/ONTOLOGICAL_ADVERSARIAL_TEST_PLAN.md"
    ).read_text(encoding="utf-8")
    for token in (
        "Inflación",
        "Falsificación L3",
        "Paso 12",
    ):
        if token not in adversarial_plan:
            fail("adversarial ontology test plan must preserve L2 firewall and phase boundary")

    adversarial_invariants = (
        ROOT / "tests/ONTOLOGICAL_DISCRIMINATOR_ADVERSARIAL_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "observaciones L2",
        "GLOBAL",
        "promotion_ref",
    ):
        if token not in adversarial_invariants:
            fail("adversarial ontology invariants are incomplete")

    metamorphic_plan = (
        ROOT / "docs/ONTOLOGICAL_METAMORPHIC_TEST_PLAN.md"
    ).read_text(encoding="utf-8")
    for token in (
        "FULL_OUTPUT_IDENTITY",
        "SEMANTIC_DECISION_IDENTITY",
        "pair_coverage",
        "Paso 13",
    ):
        if token not in metamorphic_plan:
            fail("metamorphic ontology test plan is incomplete")

    metamorphic_invariants = (
        ROOT / "tests/ONTOLOGICAL_DISCRIMINATOR_METAMORPHIC_INVARIANTS.md"
    ).read_text(encoding="utf-8")
    for token in (
        "MR01",
        "MR09",
        "MR11",
        "L3",
    ):
        if token not in metamorphic_invariants:
            fail("metamorphic ontology invariants are incomplete")

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

    if relationship_chart_consonance_schema.get("properties", {}).get("dependency_family", {}).get("const") != "RELCHART":
        fail("M09 must remain in the single RELCHART dependency family")
    if relationship_chart_consonance_schema.get("properties", {}).get("score_state", {}).get("const") != "NOT_DEFINED":
        fail("M09 must not invent an unregistered consonance score")

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
    if independent_roots_schema.get("properties", {}).get("strength_policy_applied", {}).get("const") is not True:
        fail("independent roots must declare the frozen Q1 strength policy")
    if independent_roots_schema.get("properties", {}).get("strength_policy_id", {}).get("const") != "ALMAS_ROOT_STRENGTH_BASELINE_V1":
        fail("independent roots schema must bind ALMAS_ROOT_STRENGTH_BASELINE_V1")

    if counterevidence_output_schema.get("properties", {}).get("missing_data_penalized", {}).get("const") is not False:
        fail("counterevidence schema must forbid missing-data penalty")

    if structural_ablation_schema.get("properties", {}).get("structural_only", {}).get("const") is not True:
        fail("structural ablation must declare structural_only=true")
    if structural_ablation_schema.get("properties", {}).get("dependency_classes_assigned", {}).get("const") is not False:
        fail("structural ablation must not assign contractual dependency classes")

    if time_sensitivity_schema.get("properties", {}).get("perturbations_generated_by_m23", {}).get("type") != "boolean":
        fail("time sensitivity schema must distinguish automatic and legacy perturbation sources")
    if not {"preregistration_ref", "delta90", "preserved_fraction", "robustness_component"}.issubset(
        set(time_sensitivity_schema.get("required", []))
    ):
        fail("time sensitivity schema lacks preregistered robustness fields")

    if null_model_schema.get("properties", {}).get("metaphysical_probability", {}).get("const") is not False:
        fail("null model schema must forbid metaphysical probability")
    if null_model_schema.get("properties", {}).get("sampling_generated_by_m24", {}).get("type") != "boolean":
        fail("M24 schema must distinguish generated and legacy null sampling")
    null_runs = null_model_schema.get("properties", {}).get("runs", {})
    if null_runs.get("minItems") != 1:
        fail("null model schema must require at least one run")

    robustness_props = robustness_output_schema.get("properties", {})
    if robustness_props.get("null_model_rarity_used_as_robustness", {}).get("const") is not False:
        fail("M25 must forbid null-model rarity as robustness")
    if robustness_props.get("components", {}).get("minItems") != 1:
        fail("M25 robustness schema must require at least one component")
    allowed_m25_kinds = set(
        robustness_props.get("components", {})
        .get("items", {})
        .get("properties", {})
        .get("kind", {})
        .get("enum", [])
    )
    if "NULL_RARITY" in allowed_m25_kinds or "NULL_MODEL_FREQUENCY" in allowed_m25_kinds:
        fail("M25 must not admit null rarity as a robustness component")
    ablation_states = set(
        robustness_props.get("ablation_state", {}).get("enum", [])
    )
    if "INCLUDED_AUTO_Q5" not in ablation_states:
        fail("M25 schema must expose INCLUDED_AUTO_Q5")

    if "generator_policy_id" not in time_sensitivity_schema.get("properties", {}):
        fail("M23 automatic output must expose generator_policy_id")
    if null_model_output_schema.get("properties", {}).get("metaphysical_probability", {}).get("const") is not False:
        fail("M24 null-model output must forbid metaphysical probability")
    if "generator_policy_id" not in null_model_output_schema.get("properties", {}):
        fail("M24 automatic output must expose generator_policy_id")
    if null_model_output_schema.get("properties", {}).get("combined_p_value_state", {}).get("const") != "FORBIDDEN":
        fail("M24 must forbid combined p-value across null statistics")

    temporal_props = temporal_activation_schema.get("properties", {})
    if temporal_props.get("structural_score_modified", {}).get("const") is not False:
        fail("M26 must not modify structural scoring")
    if temporal_props.get("structural_roots_created", {}).get("const") is not False:
        fail("M26 must not create structural roots")
    if temporal_props.get("real_world_event_prediction_made", {}).get("const") is not False:
        fail("M26 must not predict real-world events")
    if temporal_props.get("aggregation_weights_applied", {}).get("type") != "boolean":
        fail("M26 aggregation_weights_applied must reflect whether preregistered weights were actually used")
    if "iat_policy" not in temporal_activation_schema.get("required", []):
        fail("M26 must expose the IAT aggregation policy when applicable")
    signal_props = (
        temporal_props.get("signals", {})
        .get("items", {})
        .get("properties", {})
    )
    if signal_props.get("creates_structural_root", {}).get("const") is not False:
        fail("M26 temporal signals must never create structural roots")
    if signal_props.get("predicts_real_world_event", {}).get("const") is not False:
        fail("M26 temporal signals must never predict real-world events")
    documentary_props = documentary_event_output_schema.get("properties", {})
    if documentary_props.get("structural_mutation_allowed", {}).get("const") is not False:
        fail("M27 must forbid retrospective structural mutation")
    if documentary_props.get("clause_creation_allowed", {}).get("const") is not False:
        fail("M27 must forbid retrospective clause creation")
    if documentary_props.get("origin_elevation_allowed", {}).get("const") is not False:
        fail("M27 must forbid origin elevation from documentary events")
    if documentary_props.get("astrology_backfill_allowed", {}).get("const") is not False:
        fail("M27 must forbid astrology backfill from known events")
    if documentary_props.get("append_only_validated", {}).get("const") is not True:
        fail("M27 must validate append-only event history")
    if documentary_props.get("public_export_policy_enforced", {}).get("const") is not True:
        fail("M27 must enforce public/private export policy")
    if documentary_props.get("analysis_freeze_reference_verified", {}).get("const") is not False:
        fail("M27 must not claim freeze verification before a canonical freeze registry exists")
    documentary_event_props = (
        documentary_props.get("events", {})
        .get("items", {})
        .get("properties", {})
    )
    for field in (
        "creates_structural_root",
        "creates_clause",
        "elevates_origin",
        "astrology_backfill_allowed",
    ):
        if documentary_event_props.get(field, {}).get("const") is not False:
            fail(f"M27 event field {field} must remain false")
    if documentary_event_props.get("fact_interpretation_separated", {}).get("const") is not True:
        fail("M27 must keep fact and interpretation separate")

    final_props = final_pipeline_output_schema.get("properties", {})
    doctrine_ref = final_props.get("doctrine_hermeneutics", {}).get("$ref")
    if doctrine_ref != "doctrine-hermeneutics-output.schema.json":
        fail("final pipeline must reference canonical M28 output schema")

    doctrine_props = doctrine_output_schema.get("properties", {})
    if doctrine_props.get("doctrine_adds_structural_score", {}).get("const") is not False:
        fail("M28 doctrine must not add structural score")
    if doctrine_props.get("source_count_used_as_structural_weight", {}).get("const") is not False:
        fail("M28 source count must not become structural weight")
    if doctrine_props.get("epistemic_separation_enforced", {}).get("const") is not True:
        fail("M28 must enforce A/B/C/D/E epistemic separation")
    if doctrine_props.get("non_equivalence_enforced", {}).get("const") is not True:
        fail("M28 must enforce non-equivalence across traditions")
    if doctrine_props.get("contemporary_usage_promoted_to_ontology", {}).get("const") is not False:
        fail("M28 contemporary usage must not become ontology")
    if doctrine_props.get("project_hypothesis_promoted_to_doctrine", {}).get("const") is not False:
        fail("M28 project hypothesis must not become doctrine")
    if doctrine_props.get("cross_tradition_identity_inferred", {}).get("const") is not False:
        fail("M28 must not infer cross-tradition doctrinal identity")
    viability_ref = final_props.get("viability_reciprocity", {}).get("$ref")
    if viability_ref != "viability-reciprocity-output.schema.json":
        fail("final pipeline must reference canonical M29 output schema")

    viability_props = viability_output_schema.get("properties", {})
    if viability_props.get("factual_basis_only", {}).get("const") is not True:
        fail("M29 must require factual basis only")
    for field in (
        "astrology_used_as_real_world_fact",
        "metaphysical_claim_used_as_real_world_fact",
        "phase_used_as_viability",
        "phenomenology_used_as_reciprocity_fact",
        "absence_used_as_asymmetry",
        "mental_states_inferred",
        "consent_inferred",
        "fidelity_inferred",
        "future_decisions_inferred",
    ):
        if viability_props.get(field, {}).get("const") is not False:
            fail(f"M29 firewall field {field} must remain false")

    viability_input_required = set(viability_input_schema.get("required", []))
    for field in ("assessment_ref", "as_of_date", "subjects", "real_viability", "reciprocity"):
        if field not in viability_input_required:
            fail(f"M29 input schema missing required field: {field}")
    subject_schema = viability_input_schema.get("properties", {}).get("subjects", {})
    if subject_schema.get("minItems") != 2 or subject_schema.get("maxItems") != 2:
        fail("M29 must require exactly two subjects")
    report_gate_ref = final_props.get("report_gate", {}).get("$ref")
    if report_gate_ref != "report-gate-output.schema.json":
        fail("final pipeline must reference canonical M30 report gate schema")

    report_gate_props = report_gate_schema.get("properties", {})
    if report_gate_props.get("canonical_values_mutated", {}).get("const") is not False:
        fail("M30 report gate must not mutate canonical values")
    if set(report_gate_props.get("state", {}).get("enum", [])) != {"READY", "PARTIAL", "BLOCKED"}:
        fail("M30 must expose READY/PARTIAL/BLOCKED states")
    if report_gate_props.get("canonical_source_conflict", {}).get("type") != "boolean":
        fail("M30 must expose canonical source conflict state")
    if "blocking_issues" not in report_gate_schema.get("required", []):
        fail("M30 must expose blocking issues")
    if "degradation_reasons" not in report_gate_schema.get("required", []):
        fail("M30 must expose degradation reasons")
    if "canonical_fingerprint" not in report_gate_schema.get("required", []):
        fail("M30 must fingerprint the canonical analysis")
    report_model_ref = final_props.get("report_document_model", {}).get("$ref")
    if report_model_ref != "report-document-model.schema.json":
        fail("final pipeline must reference canonical M31 report document model schema")

    ontological_pipeline_ref = (
        final_pipeline_output_schema.get("properties", {})
        .get("ontological_discrimination", {})
        .get("$ref")
    )
    if ontological_pipeline_ref != "ontological-discriminator-output.schema.json":
        fail("final pipeline must preserve ontological_discrimination")

    report_model_handler_text = (
        ROOT / "src/almas_tfa/report_model_handlers.py"
    ).read_text(encoding="utf-8")
    for required_path in (
        '"ontological_discrimination"',
        '"ontological_discrimination.promotion_trace"',
    ):
        if required_path not in report_model_handler_text:
            fail(f"M31 reporting paths missing: {required_path}")

    report_model_props = report_document_model_schema.get("properties", {})
    if report_model_props.get("canonical_source", {}).get("const") != "canonical_analysis":
        fail("M31 must reference canonical_analysis as its sole analytical source")
    if report_model_props.get("canonical_fingerprint_verified", {}).get("const") is not True:
        fail("M31 must verify the M30 canonical fingerprint")
    for field in (
        "canonical_values_embedded",
        "canonical_values_mutated",
        "prose_generated",
        "render_profile_selected",
        "rendered_document_created",
        "docx_created",
        "pdf_created",
        "pdf_preflight_performed",
    ):
        if report_model_props.get(field, {}).get("const") is not False:
            fail(f"M31 field {field} must remain false")
    if report_model_props.get("publication_pipeline_required", {}).get("const") is not True:
        fail("M31 must require a separate publication pipeline")
    section_schema = report_model_props.get("sections", {})
    if section_schema.get("minItems") != 11 or section_schema.get("maxItems") != 11:
        fail("M31 must expose exactly eleven report sections")
    section_props = section_schema.get("items", {}).get("properties", {})
    if section_props.get("canonical_values_embedded", {}).get("const") is not False:
        fail("M31 sections must reference paths without embedding canonical values")
    if section_props.get("narrative_generated", {}).get("const") is not False:
        fail("M31 sections must not generate narrative")

    if result_schema.get("properties", {}).get("public_version", {}).get("const") != version:
        fail("precomputed result public_version diverges from root VERSION")

    if bridge_schema.get("properties", {}).get("bridge_version", {}).get("const") != "1.0.0":
        fail("astrology-to-soul-contract bridge must expose bridge_version 1.0.0")

    if doctrinal_claim_schema.get("properties", {}).get("schema_version", {}).get("const") != "2.0.0":
        fail("doctrinal claim schema must expose 2.0.0")

    claim_props = doctrinal_claim_schema.get("properties", {})
    if "source_support_refs" not in claim_props or "does_not_support_checked" not in claim_props:
        fail("DIRECT_DOCTRINE claim contract must require source support traceability fields")
    if "identity_target_concept_id" not in claim_props:
        fail("doctrinal identity claims must declare an identity target concept")


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
        resolved_spec = spec
        ref = spec.get("$ref")
        if ref == "#/$defs/model_result":
            resolved_spec = canonical_schema.get("$defs", {}).get("model_result", {})
        state_enum = (
            resolved_spec.get("properties", {})
            .get("state", {})
            .get("enum", [])
        )
        if set(state_enum) != EXPECTED_STATES:
            fail(f"{model} state enum diverges from normative states")
        required_model_fields = set(resolved_spec.get("required", []))
        if not {"iem", "state"}.issubset(required_model_fields):
            fail(f"{model} model contract must require iem and state")

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

    forbidden_schema_title_fragments = (
        " Output",
        " Input",
        " Differential",
        " Contract",
        " Registry",
        " Analysis",
        " Reconstruction",
        " Causality",
        " Selection",
        " Case",
        " Run",
        " Chart",
        " Contacts",
        " Layer",
        " Metrics",
    )
    for schema_path in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema_obj = load_json(schema_path)
        title = schema_obj.get("title")
        if not isinstance(title, str) or not title.startswith("ALMAS ·"):
            fail(f"el schema {schema_path.name} debe declarar un título humano español con prefijo 'ALMAS ·'")
        if any(fragment in title for fragment in forbidden_schema_title_fragments):
            fail(f"el schema {schema_path.name} conserva un título humano en inglés: {title}")

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
