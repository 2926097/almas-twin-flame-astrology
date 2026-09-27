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
    "docs/ASTRONOMY_GOLDEN_VALIDATION.md",
    "docs/CANONICAL_SCHEMA_AUDIT_1.18.md",
    "reference/authored-report.md",
    "reference/angular-nodal-endpoint-hermeneutics.md",
    "reference/docx-publication.md",
    "reference/pdf-publication.md",
    ".github/workflows/astronomy-backend.yml",
    ".github/workflows/publication-docx.yml",
    ".github/workflows/publication-pdf.yml",
    "scripts/validate_astronomy_backend_runtime.py",
    "scripts/validate_skyfield_reference_runtime.py",
    "scripts/validate_astronomy_golden_result.py",
    "scripts/run_astronomy_golden_planetary.py",
    "scripts/run_astronomy_golden_true_node.py",
    "scripts/run_astronomy_golden_houses.py",
    "scripts/run_astronomy_golden_complete.py",
    "scripts/validate_authored_report.py",
    "scripts/render_authored_report_docx.py",
    "scripts/publish_authored_report_pdf.py",
    "validation/astronomy/golden-cases.v1.json",
    "validation/astronomy/planetary-stage-evidence.v1.json",
    "validation/astronomy/true-node-stage-evidence.v1.json",
    "validation/astronomy/house-stage-evidence.v1.json",
    "validation/astronomy/complete-stage-evidence.v1.json",
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
    "docs/RELEASE_AUDIT_1.14.0.md",
    "docs/RELEASE_AUDIT_1.15.0.md",
    "docs/RELEASE_AUDIT_1.16.0.md",
    "docs/RELEASE_AUDIT_1.17.0.md",
    "docs/RELEASE_AUDIT_1.18.0.md",
    "docs/RELEASE_AUDIT_1.19.0.md",
    "docs/EVOLUTION_1.15.0.md",
    "docs/EVOLUTION_1.16.0.md",
    "docs/EVOLUTION_1.17.0.md",
    "docs/EVOLUTION_1.18.0.md",
    "docs/EVOLUTION_1.19.0.md",
    "docs/SOURCE_ANCHOR_POLICY.md",
    "examples/README.md",
    "examples/manifest.json",
    "examples/authoring-canonical-context.synthetic.json",
    "examples/authoring-report-model-context.synthetic.json",
    "examples/authored-report.synthetic.json",
    "public_cases/README.md",
    "public_cases/manifest.json",
    "validation/holdouts/README.md",
    "validation/holdouts/manifest.json",
    "pyproject.toml",
    "schemas/raw-input.schema.json",
    "schemas/aspect-policy.schema.json",
    "schemas/structural-policy-manifest.schema.json",
    "schemas/canonical-analysis.schema.json",
    "schemas/semantic-motif-graph.schema.json",
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
    "schemas/astronomy-backend-provenance.schema.json",
    "schemas/astronomy-golden-result.schema.json",
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
    "schemas/external-recurrence-control-cohort.schema.json",
    "schemas/px-v3-candidate-registry.schema.json",
    "schemas/px-v3-promotion-evidence.schema.json",
    "schemas/validation-preregistration-bundle.schema.json",
    "schemas/holdout-open-record.schema.json",
    "schemas/validation-execution-ledger.schema.json",
    "schemas/validation-continuity-certificate.schema.json",
    "schemas/documentary-reveal-record.schema.json",
    "schemas/validation-closure-record.schema.json",
    "schemas/validation-release-audit-package.schema.json",
    "schemas/robustness-output.schema.json",
    "schemas/temporal-activation-output.schema.json",
    "schemas/documentary-event-output.schema.json",
    "schemas/doctrine-hermeneutics-output.schema.json",
    "schemas/viability-reciprocity-assessment.schema.json",
    "schemas/viability-reciprocity-output.schema.json",
    "schemas/report-gate-output.schema.json",
    "schemas/report-document-model.schema.json",
    "schemas/authored-report.schema.json",
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
    "manifests/structural-policy-manifest.json",
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
    "reference/interpretive-synthesis-protocol.md",
    "reference/relationship-field-hermeneutics.md",
    "reference/natal-substrate-hermeneutics.md",
    "reference/planetary-function-hermeneutics.md",
    "reference/aspect-geometry-hermeneutics.md",
    "reference/semantic-motif-hermeneutics.md",
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
    "src/almas_tfa/data/technique-dependency-registry.json",
    "src/almas_tfa/data/declared-orb-contract-policy.json",
    "src/almas_tfa/data/structural-loading-policy.json",
    "src/almas_tfa/data/production-astronomy-backend-policy.json",
    "src/almas_tfa/data/astronomy-golden-validation-policy.json",
    "src/almas_tfa/data/root-pillar-attribution-policy.json",
    "src/almas_tfa/data/semantic-motif-policy.json",
    "src/almas_tfa/data/recurrence-quality-policy.json",
    "src/almas_tfa/data/recurrence-null-calibration-policy.json",
    "src/almas_tfa/data/recurrence-synthetic-controls-policy.json",
    "src/almas_tfa/data/external-recurrence-cohort-policy.json",
    "src/almas_tfa/data/external-recurrence-calibration-policy.json",
    "src/almas_tfa/data/px-v3-candidate-freeze-policy.json",
    "src/almas_tfa/data/px-v3-candidate-registry.json",
    "src/almas_tfa/data/px-v3-holdout-evaluation-policy.json",
    "src/almas_tfa/data/px-v3-promotion-gate-policy.json",
    "src/almas_tfa/data/px-v3-activation-firewall-policy.json",
    "src/almas_tfa/data/validation-preregistration-bundle-policy.json",
    "src/almas_tfa/data/holdout-open-gate-policy.json",
    "src/almas_tfa/data/validation-execution-ledger-policy.json",
    "src/almas_tfa/data/validation-continuity-gate-policy.json",
    "src/almas_tfa/data/validation-closure-release-audit-policy.json",
    "src/almas_tfa/data/analysis-profile-policy.json",
    "src/almas_tfa/data/hellenistic-lots-policy.json",
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
    "src/almas_tfa/production_astronomy.py",
    "src/almas_tfa/astronomy_golden_validation.py",
    "src/almas_tfa/skyfield_planetary_reference.py",
    "src/almas_tfa/skyfield_true_node_reference.py",
    "src/almas_tfa/skyfield_placidus_reference.py",
    "src/almas_tfa/astrology_handlers.py",
    "src/almas_tfa/astrology_geometry.py",
    "src/almas_tfa/structural_policies.py",
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
    "src/almas_tfa/semantic_motifs.py",
    "src/almas_tfa/recurrence_quality.py",
    "src/almas_tfa/null_calibration.py",
    "src/almas_tfa/synthetic_controls.py",
    "src/almas_tfa/external_control_cohorts.py",
    "src/almas_tfa/external_recurrence_calibration.py",
    "src/almas_tfa/px_v3_candidates.py",
    "src/almas_tfa/px_v3_holdout.py",
    "src/almas_tfa/px_v3_promotion.py",
    "src/almas_tfa/px_v3_activation.py",
    "src/almas_tfa/validation_preregistration.py",
    "src/almas_tfa/holdout_open.py",
    "src/almas_tfa/validation_ledger.py",
    "src/almas_tfa/validation_continuity.py",
    "src/almas_tfa/validation_closure.py",
    "src/almas_tfa/analysis_profiles.py",
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
    "src/almas_tfa/authored_report.py",
    "src/almas_tfa/docx_publication.py",
    "src/almas_tfa/pdf_publication.py",
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
    "tests/test_authored_report_contract.py",
    "tests/test_docx_publication.py",
    "tests/test_pdf_publication.py",
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
    "tests/test_recurrence_quality.py",
    "tests/test_null_calibration.py",
    "tests/test_synthetic_controls.py",
    "tests/test_external_control_cohorts.py",
    "tests/test_external_recurrence_calibration.py",
    "tests/test_px_v3_candidates.py",
    "tests/test_px_v3_holdout.py",
    "tests/test_px_v3_promotion.py",
    "tests/test_px_v3_activation.py",
    "tests/test_validation_preregistration.py",
    "tests/test_holdout_open.py",
    "tests/test_validation_ledger.py",
    "tests/test_validation_continuity.py",
    "tests/test_validation_closure.py",
    "tests/test_structural_policies.py",
    "tests/test_production_astronomy.py",
    "tests/test_astronomy_golden_validation.py",
    "tests/test_skyfield_planetary_reference.py",
    "tests/test_skyfield_true_node_reference.py",
    "tests/test_skyfield_placidus_reference.py",
    "tests/test_analysis_profiles.py",
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

    if "\\n" in skill:
        fail("SKILL.md contains a literal newline escape")
    if "\\n" in readme:
        fail("README.md contains a literal newline escape")

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
        "authored_report",
        "ASTROLOGY_AND_SOURCE_BASED_METAPHYSICAL_HERMENEUTICS",
        "report_document_model + canonical_analysis → authored_report",
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
    astronomy_backend_provenance_schema = load_json(
        "schemas/astronomy-backend-provenance.schema.json"
    )
    astronomy_golden_result_schema = load_json(
        "schemas/astronomy-golden-result.schema.json"
    )
    astronomy_golden_policy = load_json(
        "src/almas_tfa/data/astronomy-golden-validation-policy.json"
    )
    astronomy_golden_cases = load_json(
        "validation/astronomy/golden-cases.v1.json"
    )
    astronomy_planetary_evidence = load_json(
        "validation/astronomy/planetary-stage-evidence.v1.json"
    )
    astronomy_true_node_evidence = load_json(
        "validation/astronomy/true-node-stage-evidence.v1.json"
    )
    astronomy_house_evidence = load_json(
        "validation/astronomy/house-stage-evidence.v1.json"
    )
    astronomy_complete_evidence = load_json(
        "validation/astronomy/complete-stage-evidence.v1.json"
    )
    aspect_policy_schema = load_json("schemas/aspect-policy.schema.json")
    structural_policy_manifest_schema = load_json("schemas/structural-policy-manifest.schema.json")
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
    technique_dependency_registry = load_json(
        "src/almas_tfa/data/technique-dependency-registry.json"
    )
    declared_orb_contract_policy = load_json(
        "src/almas_tfa/data/declared-orb-contract-policy.json"
    )
    structural_loading_policy = load_json(
        "src/almas_tfa/data/structural-loading-policy.json"
    )
    production_astronomy_backend_policy = load_json(
        "src/almas_tfa/data/production-astronomy-backend-policy.json"
    )
    root_pillar_policy = load_json(
        "src/almas_tfa/data/root-pillar-attribution-policy.json"
    )
    semantic_motif_policy = load_json(
        "src/almas_tfa/data/semantic-motif-policy.json"
    )
    recurrence_quality_policy = load_json(
        "src/almas_tfa/data/recurrence-quality-policy.json"
    )
    recurrence_null_calibration_policy = load_json(
        "src/almas_tfa/data/recurrence-null-calibration-policy.json"
    )
    recurrence_synthetic_controls_policy = load_json(
        "src/almas_tfa/data/recurrence-synthetic-controls-policy.json"
    )
    external_recurrence_cohort_policy = load_json(
        "src/almas_tfa/data/external-recurrence-cohort-policy.json"
    )
    external_recurrence_calibration_policy = load_json(
        "src/almas_tfa/data/external-recurrence-calibration-policy.json"
    )
    px_v3_candidate_freeze_policy = load_json(
        "src/almas_tfa/data/px-v3-candidate-freeze-policy.json"
    )
    px_v3_candidate_registry = load_json(
        "src/almas_tfa/data/px-v3-candidate-registry.json"
    )
    px_v3_holdout_evaluation_policy = load_json(
        "src/almas_tfa/data/px-v3-holdout-evaluation-policy.json"
    )
    px_v3_promotion_gate_policy = load_json(
        "src/almas_tfa/data/px-v3-promotion-gate-policy.json"
    )
    px_v3_activation_firewall_policy = load_json(
        "src/almas_tfa/data/px-v3-activation-firewall-policy.json"
    )
    validation_preregistration_bundle_policy = load_json(
        "src/almas_tfa/data/validation-preregistration-bundle-policy.json"
    )
    holdout_open_gate_policy = load_json(
        "src/almas_tfa/data/holdout-open-gate-policy.json"
    )
    validation_execution_ledger_policy = load_json(
        "src/almas_tfa/data/validation-execution-ledger-policy.json"
    )
    validation_continuity_gate_policy = load_json(
        "src/almas_tfa/data/validation-continuity-gate-policy.json"
    )
    validation_closure_release_audit_policy = load_json(
        "src/almas_tfa/data/validation-closure-release-audit-policy.json"
    )
    analysis_profile_policy = load_json(
        "src/almas_tfa/data/analysis-profile-policy.json"
    )
    hellenistic_lots_policy = load_json(
        "src/almas_tfa/data/hellenistic-lots-policy.json"
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
    external_recurrence_cohort_schema = load_json(
        "schemas/external-recurrence-control-cohort.schema.json"
    )
    px_v3_candidate_registry_schema = load_json(
        "schemas/px-v3-candidate-registry.schema.json"
    )
    px_v3_promotion_evidence_schema = load_json(
        "schemas/px-v3-promotion-evidence.schema.json"
    )
    validation_preregistration_bundle_schema = load_json(
        "schemas/validation-preregistration-bundle.schema.json"
    )
    holdout_open_record_schema = load_json(
        "schemas/holdout-open-record.schema.json"
    )
    validation_execution_ledger_schema = load_json(
        "schemas/validation-execution-ledger.schema.json"
    )
    validation_continuity_certificate_schema = load_json(
        "schemas/validation-continuity-certificate.schema.json"
    )
    documentary_reveal_record_schema = load_json(
        "schemas/documentary-reveal-record.schema.json"
    )
    validation_closure_record_schema = load_json(
        "schemas/validation-closure-record.schema.json"
    )
    validation_release_audit_package_schema = load_json(
        "schemas/validation-release-audit-package.schema.json"
    )
    temporal_activation_schema = load_json("schemas/temporal-activation-output.schema.json")
    documentary_event_output_schema = load_json("schemas/documentary-event-output.schema.json")
    doctrine_output_schema = load_json("schemas/doctrine-hermeneutics-output.schema.json")
    viability_input_schema = load_json("schemas/viability-reciprocity-assessment.schema.json")
    viability_output_schema = load_json("schemas/viability-reciprocity-output.schema.json")
    report_gate_schema = load_json("schemas/report-gate-output.schema.json")
    report_document_model_schema = load_json("schemas/report-document-model.schema.json")
    authored_report_schema = load_json("schemas/authored-report.schema.json")
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
    structural_policy_manifest = load_json("manifests/structural-policy-manifest.json")
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

    if production_astronomy_backend_policy.get("policy_id") != "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1":
        fail("production astronomy backend policy id changed")
    if production_astronomy_backend_policy.get("status") != "FROZEN_PRODUCTION_CONTRACT":
        fail("production astronomy backend policy must remain frozen")
    provider = production_astronomy_backend_policy.get("provider", {})
    if provider.get("package") != "moira-astro" or provider.get("pinned_version") != "6.8.2":
        fail("production astronomy provider/version changed")
    if provider.get("license") != "MIT":
        fail("production astronomy provider license declaration changed")
    kernel = production_astronomy_backend_policy.get("kernel", {})
    for key in (
        "required",
        "local_file_required",
        "sha256_required",
        "kernel_choice_is_part_of_result_identity",
    ):
        if kernel.get(key) is not True:
            fail(f"production astronomy kernel invariant failed: {key}")
    if kernel.get("network_download_during_calculation") is not False:
        fail("production astronomy backend must forbid network download during calculation")
    if set(kernel.get("allowed_families", [])) != {"DE430", "DE440", "DE441"}:
        fail("production astronomy allowed kernel families changed")
    time_policy = production_astronomy_backend_policy.get("time", {})
    if time_policy.get("timezone_standard") != "IANA":
        fail("production astronomy timezone standard changed")
    for key in ("hidden_timezone_lookup",):
        if time_policy.get(key) is not False:
            fail(f"production astronomy time invariant failed: {key}")
    if time_policy.get("ambiguous_local_time") != "FAIL_CLOSED":
        fail("production astronomy ambiguous time must fail closed")
    if time_policy.get("nonexistent_local_time") != "FAIL_CLOSED":
        fail("production astronomy nonexistent time must fail closed")
    location_policy = production_astronomy_backend_policy.get("location", {})
    if location_policy.get("numeric_coordinates_required_for_timed_chart") is not True:
        fail("production astronomy timed charts must require numeric coordinates")
    if location_policy.get("hidden_geocoding") is not False:
        fail("production astronomy backend must forbid hidden geocoding")
    natal_policy = production_astronomy_backend_policy.get("natal", {})
    if natal_policy.get("node_mode") != "TRUE_NODE":
        fail("production astronomy node mode changed")
    if natal_policy.get("house_system_must_be_explicit") is not True:
        fail("production astronomy house system must be explicit")
    if natal_policy.get("polar_house_fallback") != "FORBIDDEN":
        fail("production astronomy polar house fallback must remain forbidden")
    capabilities = production_astronomy_backend_policy.get("capabilities", {})
    for key in (
        "planetary_longitude",
        "ecliptic_latitude",
        "declination",
        "longitudinal_speed",
        "retrograde",
        "true_lunar_node",
        "houses",
        "angles",
        "davison",
    ):
        if capabilities.get(key) is not True:
            fail(f"production astronomy capability missing: {key}")
    for key in ("hidden_network_io", "hidden_geocoding"):
        if capabilities.get(key) is not False:
            fail(f"production astronomy capability firewall failed: {key}")

    provenance_props = astronomy_backend_provenance_schema.get("properties", {})
    if provenance_props.get("policy_id", {}).get("const") != "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1":
        fail("astronomy backend provenance schema policy id changed")
    if provenance_props.get("provider_version", {}).get("const") != "6.8.2":
        fail("astronomy backend provenance schema provider version changed")
    if "kernel_family" not in astronomy_backend_provenance_schema.get("required", []):
        fail("astronomy backend provenance must require kernel_family")
    for field in ("network_io_used", "geocoding_used"):
        if provenance_props.get(field, {}).get("const") is not False:
            fail(f"astronomy backend provenance must lock {field}=false")
    natal_backend_ref = (
        load_json("schemas/natal-chart.schema.json")
        .get("properties", {})
        .get("backend_provenance", {})
        .get("$ref")
    )
    if natal_backend_ref != "astronomy-backend-provenance.schema.json":
        fail("natal chart schema must reference astronomy backend provenance")

    if astronomy_golden_policy.get("policy_id") != "ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1":
        fail("astronomy golden validation policy id changed")
    if astronomy_golden_policy.get("status") != "PREREGISTERED_NOT_EXECUTED":
        fail("astronomy golden validation must remain preregistered until real execution")
    backend_contract = astronomy_golden_policy.get("backend_contract", {})
    expected_golden_geometry = {
        "adapter_id": "ALMAS_MOIRA_JPL_SPK_V1",
        "provider_version": "6.8.2",
        "kernel_family": "DE440",
        "coordinate_origin": "GEOCENTRIC",
        "reference_frame": "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
        "apparent_reduction": True,
        "topocentric_positions": False,
        "zodiac": "TROPICAL",
        "node_mode": "TRUE_NODE",
    }
    for key, expected in expected_golden_geometry.items():
        if backend_contract.get(key) != expected:
            fail(f"astronomy golden backend contract changed: {key}")
    golden_artifact = astronomy_golden_policy.get("kernel_artifact", {})
    expected_artifact = {
        "filename": "de440s.bsp",
        "family": "DE440",
        "sha256": "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2",
        "md5": "3917ee56769db332790c751e2168843d",
        "size_bytes": 32726016,
        "network_forbidden_during_calculation": True,
    }
    for key, expected in expected_artifact.items():
        if golden_artifact.get(key) != expected:
            fail(f"astronomy golden kernel artifact changed: {key}")
    expected_stages = {
        "PLANETARY_REFERENCE": {
            "planetary_longitude", "ecliptic_latitude", "declination"
        },
        "TRUE_NODE_REFERENCE": {"true_node_longitude"},
        "HOUSE_REFERENCE": {"angle_longitude", "house_cusp_longitude"},
        "COMPLETE_GATE": {
            "planetary_longitude", "ecliptic_latitude", "declination",
            "true_node_longitude", "angle_longitude",
            "house_cusp_longitude",
        },
    }
    actual_stages = astronomy_golden_policy.get("validation_stages", {})
    if set(actual_stages) != set(expected_stages):
        fail("astronomy golden validation stages changed")
    for stage_id, expected_metrics in expected_stages.items():
        if set(actual_stages.get(stage_id, [])) != expected_metrics:
            fail(f"astronomy golden stage metrics changed: {stage_id}")
    true_node_reference = astronomy_golden_policy.get("reference_contract", {}).get("true_node", {})
    expected_true_node_reference = {
        "method_family": "INDEPENDENT_OSCULATING_GEOMETRIC_NODE",
        "preferred_implementation": "SKYFIELD_DE440_FIRST_PRINCIPLES",
        "method_id": "ALMAS_SKYFIELD_DE440_TRUE_NODE_REFERENCE_V1",
        "definition": "INSTANTANEOUS_GEOCENTRIC_OSCULATING_LUNAR_PLANE_INTERSECTION_WITH_TRUE_ECLIPTIC_OF_DATE",
        "state_vectors": "SIMULTANEOUS_MOON_MINUS_EARTH",
        "orbital_normal": "ICRF_R_CROSS_V_THEN_ROTATE_TO_TRUE_ECLIPTIC_OF_DATE",
        "ascending_node_orientation": "K_CROSS_H",
        "time_alignment": "COMMON_TT_EPOCH_FROM_BACKEND_RECEIPT",
        "same_software_implementation_forbidden": True,
    }
    for key, expected in expected_true_node_reference.items():
        if true_node_reference.get(key) != expected:
            fail(f"astronomy true-node reference contract changed: {key}")
    house_reference = astronomy_golden_policy.get("reference_contract", {}).get("houses_and_angles", {})
    expected_house_reference = {
        "method_family": "INDEPENDENT_PLACIDUS_SEMI_ARC_IMPLEMENTATION",
        "preferred_implementation": "ALMAS_SKYFIELD_PLACIDUS_REFERENCE_V1",
        "method_id": "ALMAS_SKYFIELD_PLACIDUS_REFERENCE_V1",
        "house_system": "PLACIDUS",
        "house_code": "P",
        "armc": "GREENWICH_APPARENT_SIDEREAL_TIME_PLUS_GEOGRAPHIC_LONGITUDE",
        "time_alignment": "BACKEND_JD_UT_PLUS_BACKEND_DELTA_T",
        "delta_t_source": "BACKEND_RECEIPT",
        "obliquity": "TRUE_OBLIQUITY_FROM_SKYFIELD_TRUE_EQUATOR_AND_TRUE_ECLIPTIC_FRAMES",
        "intermediate_cusps": "CLASSIC_ITERATIVE_SEMI_ARC_TRISECTION",
        "convergence_threshold_deg": 1e-7,
        "max_iterations": 100,
        "polar_fallback": "FORBIDDEN",
        "same_software_implementation_forbidden": True,
    }
    for key, expected in expected_house_reference.items():
        if house_reference.get(key) != expected:
            fail(f"astronomy house reference contract changed: {key}")
    tolerances = astronomy_golden_policy.get("tolerances_arcsec", {})
    expected_defaults = {
        "planetary_longitude": 5.0,
        "ecliptic_latitude": 5.0,
        "declination": 10.0,
        "true_node_longitude": 60.0,
        "angle_longitude": 60.0,
        "house_cusp_longitude": 60.0,
    }
    for metric, expected in expected_defaults.items():
        if tolerances.get(metric, {}).get("default") != expected:
            fail(f"astronomy golden tolerance changed: {metric}")
    if tolerances.get("planetary_longitude", {}).get("overrides", {}).get("MOON") != 15.0:
        fail("astronomy golden Moon longitude tolerance changed")
    if tolerances.get("ecliptic_latitude", {}).get("overrides", {}).get("MOON") != 15.0:
        fail("astronomy golden Moon latitude tolerance changed")
    if tolerances.get("declination", {}).get("overrides", {}).get("MOON") != 20.0:
        fail("astronomy golden Moon declination tolerance changed")
    decision_rule = astronomy_golden_policy.get("decision_rule", {})
    for key in (
        "all_required_measurements_must_be_present",
        "all_required_measurements_must_be_within_tolerance",
        "threshold_change_after_observation_forbidden",
        "threshold_change_requires_new_policy_id",
    ):
        if decision_rule.get(key) is not True:
            fail(f"astronomy golden decision rule changed: {key}")
    if decision_rule.get("aggregation") != "NONE":
        fail("astronomy golden gate must not average failures")
    if astronomy_golden_cases.get("case_set_id") != "ALMAS_ASTRONOMY_GOLDEN_CASES_V1":
        fail("astronomy golden case set id changed")
    if astronomy_golden_cases.get("status") != "PREREGISTERED_INPUTS_ONLY":
        fail("astronomy golden cases must remain inputs-only before real execution")
    golden_cases = astronomy_golden_cases.get("cases", [])
    if len(golden_cases) != 6 or len({case.get("case_id") for case in golden_cases}) != 6:
        fail("astronomy golden case set must contain six unique preregistered cases")
    golden_schema_props = astronomy_golden_result_schema.get("properties", {})
    if golden_schema_props.get("policy_id", {}).get("const") != "ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1":
        fail("astronomy golden result schema policy id changed")
    if golden_schema_props.get("case_set_id", {}).get("const") != "ALMAS_ASTRONOMY_GOLDEN_CASES_V1":
        fail("astronomy golden result schema case set id changed")
    if golden_schema_props.get("reference_provenance", {}).get("type") != "array":
        fail("astronomy golden result must support multiple references")
    measurement_required = set(
        golden_schema_props.get("measurements", {})
        .get("items", {})
        .get("required", [])
    )
    if "reference_method_id" not in measurement_required:
        fail("astronomy golden measurements must identify reference method")

    if astronomy_planetary_evidence.get("evidence_id") != "ALMAS_ASTRONOMY_GOLDEN_PLANETARY_EVIDENCE_V1":
        fail("astronomy planetary evidence id changed")
    if astronomy_planetary_evidence.get("validation_stage") != "PLANETARY_REFERENCE":
        fail("astronomy planetary evidence stage changed")
    if astronomy_planetary_evidence.get("status") != "PASS":
        fail("astronomy planetary evidence must remain PASS")
    if astronomy_planetary_evidence.get("execution_commit") != "ff9252dce9db6f1654fe52aeb3de3448f5371edc":
        fail("astronomy planetary evidence execution commit changed")
    if astronomy_planetary_evidence.get("python_versions") != ["3.10", "3.12"]:
        fail("astronomy planetary evidence Python matrix changed")
    evidence_kernel = astronomy_planetary_evidence.get("kernel", {})
    if evidence_kernel.get("sha256") != expected_artifact["sha256"]:
        fail("astronomy planetary evidence kernel SHA diverges")
    if evidence_kernel.get("md5") != expected_artifact["md5"]:
        fail("astronomy planetary evidence kernel MD5 diverges")
    if astronomy_planetary_evidence.get("measurements_per_environment") != 180:
        fail("astronomy planetary evidence measurement count changed")
    evidence_repro = astronomy_planetary_evidence.get("reproducibility", {})
    if evidence_repro.get("identical_summaries_across_python_versions") is not True:
        fail("astronomy planetary evidence must reproduce across Python versions")
    if evidence_repro.get("failure_count") != 0:
        fail("astronomy planetary evidence contains failures")
    if evidence_repro.get("thresholds_modified_after_observation") is not False:
        fail("astronomy planetary evidence cannot alter preregistered thresholds")
    evidence_cases = astronomy_planetary_evidence.get("cases", [])
    if len(evidence_cases) != 6 or any(case.get("status") != "PASS" for case in evidence_cases):
        fail("all six astronomy planetary evidence cases must PASS")
    overall_max = astronomy_planetary_evidence.get("overall_max", {})
    if overall_max.get("delta_arcsec") != 0.9257480642418159:
        fail("astronomy planetary evidence maximum delta changed")
    if overall_max.get("tolerance_arcsec") != 15.0:
        fail("astronomy planetary evidence maximum tolerance changed")

    if astronomy_true_node_evidence.get("evidence_id") != "ALMAS_ASTRONOMY_GOLDEN_TRUE_NODE_EVIDENCE_V1":
        fail("astronomy true-node evidence id changed")
    if astronomy_true_node_evidence.get("validation_stage") != "TRUE_NODE_REFERENCE":
        fail("astronomy true-node evidence stage changed")
    if astronomy_true_node_evidence.get("status") != "PASS":
        fail("astronomy true-node evidence must remain PASS")
    if astronomy_true_node_evidence.get("execution_commit") != "25226b69c2fded6d167175dc20bf682d9f14879e":
        fail("astronomy true-node evidence execution commit changed")
    if astronomy_true_node_evidence.get("python_versions") != ["3.10", "3.12"]:
        fail("astronomy true-node evidence Python matrix changed")
    if astronomy_true_node_evidence.get("measurements_per_environment") != 6:
        fail("astronomy true-node evidence measurement count changed")
    true_node_repro = astronomy_true_node_evidence.get("reproducibility", {})
    if true_node_repro.get("identical_summaries_across_python_versions") is not True:
        fail("astronomy true-node evidence must reproduce across Python versions")
    if true_node_repro.get("failure_count") != 0:
        fail("astronomy true-node evidence contains failures")
    if true_node_repro.get("thresholds_modified_after_observation") is not False:
        fail("astronomy true-node evidence cannot alter preregistered thresholds")
    true_node_cases = astronomy_true_node_evidence.get("cases", [])
    if len(true_node_cases) != 6 or any(case.get("status") != "PASS" for case in true_node_cases):
        fail("all six astronomy true-node evidence cases must PASS")
    true_node_max = astronomy_true_node_evidence.get("overall_max", {})
    if true_node_max.get("delta_arcsec") != 0.005674621911566646:
        fail("astronomy true-node evidence maximum delta changed")
    if true_node_max.get("tolerance_arcsec") != 60.0:
        fail("astronomy true-node evidence tolerance changed")

    if astronomy_house_evidence.get("evidence_id") != "ALMAS_ASTRONOMY_GOLDEN_HOUSE_EVIDENCE_V1":
        fail("astronomy house evidence id changed")
    if astronomy_house_evidence.get("validation_stage") != "HOUSE_REFERENCE":
        fail("astronomy house evidence stage changed")
    if astronomy_house_evidence.get("status") != "PASS":
        fail("astronomy house evidence must remain PASS")
    if astronomy_house_evidence.get("execution_commit") != "f07696cee3e73f71032ea83f2eec24a3321e5f28":
        fail("astronomy house evidence execution commit changed")
    if astronomy_house_evidence.get("python_versions") != ["3.10", "3.12"]:
        fail("astronomy house evidence Python matrix changed")
    if astronomy_house_evidence.get("measurements_per_environment") != 96:
        fail("astronomy house evidence measurement count changed")
    house_repro = astronomy_house_evidence.get("reproducibility", {})
    if house_repro.get("identical_summaries_across_python_versions") is not True:
        fail("astronomy house evidence must reproduce across Python versions")
    if house_repro.get("failure_count") != 0:
        fail("astronomy house evidence contains failures")
    house_max = astronomy_house_evidence.get("overall_max", {})
    if house_max.get("delta_arcsec") != 39.89038871222874:
        fail("astronomy house evidence maximum delta changed")
    if house_max.get("tolerance_arcsec") != 60.0:
        fail("astronomy house evidence tolerance changed")

    if astronomy_complete_evidence.get("evidence_id") != "ALMAS_ASTRONOMY_GOLDEN_COMPLETE_EVIDENCE_V1":
        fail("astronomy complete evidence id changed")
    if astronomy_complete_evidence.get("validation_stage") != "COMPLETE_GATE":
        fail("astronomy complete evidence stage changed")
    if astronomy_complete_evidence.get("status") != "PASS":
        fail("astronomy complete gate must remain PASS")
    if astronomy_complete_evidence.get("execution_commit") != "40725734d15d83d0bb21b05c0e6496ef606ba8cb":
        fail("astronomy complete evidence execution commit changed")
    if astronomy_complete_evidence.get("python_versions") != ["3.10", "3.12"]:
        fail("astronomy complete evidence Python matrix changed")
    if astronomy_complete_evidence.get("measurements_per_case") != 47:
        fail("astronomy complete evidence per-case count changed")
    if astronomy_complete_evidence.get("measurements_per_environment") != 282:
        fail("astronomy complete evidence measurement count changed")
    complete_repro = astronomy_complete_evidence.get("reproducibility", {})
    if complete_repro.get("identical_summaries_across_python_versions") is not True:
        fail("astronomy complete evidence must reproduce across Python versions")
    if complete_repro.get("summary_sha256") != "dcc6d349e6eabc22f90c6911e3fbf466579872f6b186471d822a7a892a8faa9a":
        fail("astronomy complete summary fingerprint changed")
    if complete_repro.get("failure_count") != 0:
        fail("astronomy complete evidence contains failures")
    if complete_repro.get("thresholds_modified_after_observation") is not False:
        fail("astronomy complete evidence cannot alter preregistered thresholds")
    complete_cases = astronomy_complete_evidence.get("cases", [])
    if len(complete_cases) != 6 or any(case.get("status") != "PASS" for case in complete_cases):
        fail("all six astronomy complete evidence cases must PASS")
    if any(case.get("measurement_count") != 47 for case in complete_cases):
        fail("each astronomy complete case must contain 47 measurements")
    complete_max = astronomy_complete_evidence.get("overall_max", {})
    if complete_max.get("delta_arcsec") != 39.89038871222874:
        fail("astronomy complete evidence maximum delta changed")
    if complete_max.get("tolerance_arcsec") != 60.0:
        fail("astronomy complete evidence tolerance changed")
    if astronomy_complete_evidence.get("remaining_stages") != []:
        fail("astronomy complete evidence must close all golden stages")

    if 'astronomy-moira = ["moira-astro==6.8.2"]' not in pyproject:
        fail("pyproject must pin optional moira-astro 6.8.2 backend extra")
    if 'publication-docx = ["python-docx==1.2.0"]' not in pyproject:
        fail("pyproject must pin optional python-docx 1.2.0 publication extra")
    if 'publication-pdf = ["pypdf==6.19.0"]' not in pyproject:
        fail("pyproject must pin optional pypdf 6.19.0 publication extra")
    if 'astronomy-validation = ["skyfield==1.55"]' not in pyproject:
        fail("pyproject must pin optional skyfield 1.55 validation extra")
    if 'schema-validation = ["jsonschema==4.26.0"]' not in pyproject:
        fail("pyproject must pin jsonschema 4.26.0 validation extra")

    if structural_policy_manifest.get("almas_public_version") != version:
        fail("structural policy manifest version diverges from VERSION")
    if structural_policy_manifest.get("manifest_id") != "ALMAS_STRUCTURAL_POLICY_MANIFEST_V1":
        fail("structural policy manifest id changed")

    if structural_policy_manifest_schema.get("properties", {}).get("manifest_id", {}).get("const") != "ALMAS_STRUCTURAL_POLICY_MANIFEST_V1":
        fail("structural policy manifest schema id changed")
    if structural_policy_manifest_schema.get("properties", {}).get("almas_public_version", {}).get("const") != version:
        fail("structural policy manifest schema version diverges from VERSION")

    if technique_dependency_registry.get("registry_id") != "ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1":
        fail("technique/dependency registry id changed")
    if technique_dependency_registry.get("status") != "FROZEN_NORMATIVE":
        fail("technique/dependency registry must remain frozen normative")

    expected_structural_bindings = {
        "synastry": ("M03", "SYN", "SYN", False, True, False),
        "declinations": ("M05", "DECLINATION", "DECLINATION", False, True, False),
        "antiscia": ("M06", "ANTISCIA", "ANTISCIA", False, True, False),
        "relationship_chart_consonance": ("M09", "RELCHART", "RELCHART", False, True, False),
        "natal_draconic_cross": ("M11", "NATAL_DRACONIC", "NATAL_DRACONIC", False, True, True),
        "draconic_draconic": ("M12", "DRACONIC_DD", "DRACONIC_DD", True, False, False),
        "secondary_symbolic": ("M14", "SECONDARY", "SECONDARY", True, False, False),
    }
    bindings = technique_dependency_registry.get("source_bindings", {})
    if set(bindings) != set(expected_structural_bindings):
        fail("technique/dependency registry source set changed")
    for source, expected in expected_structural_bindings.items():
        spec = bindings.get(source, {})
        actual = (
            spec.get("module_id"),
            spec.get("technique_family"),
            spec.get("dependency_family"),
            spec.get("support_only"),
            spec.get("core_eligible"),
            spec.get("directional"),
        )
        if actual != expected:
            fail(f"technique/dependency binding changed: {source}")
        if spec.get("support_only") is True and spec.get("core_eligible") is True:
            fail(f"support-only binding became core eligible: {source}")

    technique_families = {
        spec.get("technique_family")
        for spec in bindings.values()
        if isinstance(spec, dict)
    }
    root_technique_weights = root_strength_policy.get("technique_reliability", {})
    if not technique_families.issubset(set(root_technique_weights)):
        fail("root strength policy does not cover all registered technique families")
    for family in technique_families:
        if root_technique_weights.get(family) != 1.0:
            fail(f"1.17 must not introduce technique weighting: {family}")

    if declared_orb_contract_policy.get("policy_id") != "ALMAS_DECLARED_ORB_CONTRACT_V1":
        fail("declared orb contract id changed")
    orb_principles = declared_orb_contract_policy.get("principles", {})
    for key in (
        "implicit_orbs_forbidden",
        "aspect_angle_must_be_declared",
        "aspect_orb_must_be_declared",
        "runtime_orb_inference_forbidden",
        "overlap_resolution_deterministic",
        "orb_rarity_not_ontological",
        "case_fitting_forbidden",
    ):
        if orb_principles.get(key) is not True:
            fail(f"declared orb invariant failed: {key}")

    aspect_items = aspect_policy_schema.get("additionalProperties", {})
    if set(aspect_items.get("required", [])) != {"angle", "orb"}:
        fail("aspect policy schema must require exactly angle and orb")
    if aspect_items.get("additionalProperties") is not False:
        fail("aspect policy schema must forbid undeclared aspect fields")
    raw_aspect_ref = raw_schema.get("properties", {}).get("aspect_policy", {}).get("$ref")
    if raw_aspect_ref != "aspect-policy.schema.json":
        fail("raw input aspect_policy must reference the canonical aspect policy schema")

    if structural_loading_policy.get("policy_id") != "ALMAS_STRUCTURAL_LOADING_CONTRACT_V1":
        fail("structural loading contract id changed")
    if structural_loading_policy.get("root_strength_policy_id") != root_strength_policy.get("policy_id"):
        fail("structural loading root-strength reference diverges")
    if structural_loading_policy.get("root_pillar_policy_id") != root_pillar_policy.get("policy_id"):
        fail("structural loading root-pillar reference diverges")
    loading_constraints = structural_loading_policy.get("loading_constraints", {})
    if loading_constraints.get("raw_loading_sum_max") != 1.0:
        fail("structural loading raw loading maximum changed")
    if loading_constraints.get("normalized_loading_sum_for_scored_unit") != 1.0:
        fail("structural loading normalized sum changed")
    if loading_constraints.get("support_only_can_create_core") is not False:
        fail("structural loading must forbid support-only core creation")

    contracts = structural_policy_manifest.get("contracts", {})
    expected_policy_paths = {
        "technique_dependency_registry": (
            "ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1",
            "src/almas_tfa/data/technique-dependency-registry.json",
        ),
        "declared_orb_contract": (
            "ALMAS_DECLARED_ORB_CONTRACT_V1",
            "src/almas_tfa/data/declared-orb-contract-policy.json",
        ),
        "structural_loading_contract": (
            "ALMAS_STRUCTURAL_LOADING_CONTRACT_V1",
            "src/almas_tfa/data/structural-loading-policy.json",
        ),
        "root_strength": (
            "ALMAS_ROOT_STRENGTH_BASELINE_V1",
            "src/almas_tfa/data/root-strength-policy.json",
        ),
        "root_pillar_attribution": (
            "ALMAS_ROOT_PILLAR_ATTRIBUTION_V2",
            "src/almas_tfa/data/root-pillar-attribution-policy.json",
        ),
    }
    for key, (policy_id, path) in expected_policy_paths.items():
        contract = contracts.get(key, {})
        if contract.get("policy_id") != policy_id or contract.get("path") != path:
            fail(f"structural policy manifest contract mismatch: {key}")
    manifest_invariants = structural_policy_manifest.get("invariants", {})
    for key in (
        "no_new_analytical_module",
        "no_score_change",
        "no_implicit_orbs",
        "no_runtime_case_fitting",
        "support_only_cannot_create_core",
        "dependency_deduplication_precedes_root_construction",
        "birth_time_robustness_remains_m23_m25",
    ):
        if manifest_invariants.get(key) is not True:
            fail(f"structural policy manifest invariant failed: {key}")

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

    if root_pillar_policy.get("policy_id") != "ALMAS_ROOT_PILLAR_ATTRIBUTION_V2":
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
    if pillar_principles.get("px_derived_from_semantic_motifs") is not True:
        fail("PX must be derived from semantic motif recurrence in 1.14")
    if pillar_principles.get("ps_derived_from_mission_motifs") is not True:
        fail("PS must be derived from mission motif recurrence in 1.14")

    if semantic_motif_policy.get("policy_id") != "ALMAS_SEMANTIC_MOTIF_V2":
        fail("semantic motif policy id changed")
    if semantic_motif_policy.get("status") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("semantic motif policy must remain frozen")
    motif_principles = semantic_motif_policy.get("principles", {})
    if motif_principles.get("case_fitting_forbidden") is not True:
        fail("semantic motif policy must forbid case fitting")
    if motif_principles.get("root_identity_remains_geometric") is not True:
        fail("semantic recurrence must not rewrite root identity")
    if motif_principles.get("support_only_cannot_create_core_recurrence") is not True:
        fail("support-only must not create core recurrence")
    if motif_principles.get("dependency_family_counted_once_per_motif") is not True:
        fail("semantic recurrence must count each dependency family once")
    if motif_principles.get("relchart_is_one_dependency_family") is not True:
        fail("RELCHART must remain a single dependency family")
    for relation_set_name, relation_values in semantic_motif_policy.get("relation_sets", {}).items():
        if not isinstance(relation_values, list):
            fail(f"semantic motif relation set {relation_set_name} must be a list")
        if len(relation_values) != len(set(relation_values)):
            fail(f"semantic motif relation set {relation_set_name} contains duplicates")

    if recurrence_quality_policy.get("policy_id") != "ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1":
        fail("recurrence quality policy id changed")
    if recurrence_quality_policy.get("status") != "FROZEN_EXPERIMENTAL_DIAGNOSTIC":
        fail("recurrence quality policy must remain diagnostic")
    if recurrence_quality_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("recurrence quality policy must remain E_PROJECT_POLICY")
    recurrence_quality_principles = recurrence_quality_policy.get("principles", {})
    for key in (
        "case_fitting_forbidden",
        "descriptive_only",
        "px_ps_scores_unchanged",
        "iem_unchanged",
        "idd_unchanged",
        "irc_unchanged",
        "ontology_unchanged",
        "null_calibration_required_before_any_weighting",
        "draconic_dependency_must_be_exposed",
    ):
        if recurrence_quality_principles.get(key) is not True:
            fail(f"recurrence quality invariant failed: {key}")
    if recurrence_quality_principles.get("null_rarity_not_used_as_score") is not True:
        fail("recurrence quality diagnostics must keep null rarity out of scoring")
    family_classes = recurrence_quality_policy.get("family_classes", {})
    if family_classes.get("RELCHART") != "RELATIONSHIP_CHART":
        fail("recurrence quality must preserve RELCHART as one family class")
    if family_classes.get("NATAL_DRACONIC") != "DRACONIC_CROSS":
        fail("recurrence quality must expose natal-draconic dependency")

    if recurrence_null_calibration_policy.get("policy_id") != "ALMAS_RECURRENCE_NULL_CALIBRATION_V1":
        fail("recurrence null calibration policy id changed")
    if recurrence_null_calibration_policy.get("status") != "FROZEN_EXPERIMENTAL_DIAGNOSTIC":
        fail("recurrence null calibration policy must remain diagnostic")
    if recurrence_null_calibration_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("recurrence null calibration policy must remain E_PROJECT_POLICY")
    null_source = recurrence_null_calibration_policy.get("null_source", {})
    if null_source.get("required_null_model") != "WITHIN_YEAR":
        fail("S2 baseline calibration must remain WITHIN_YEAR")
    if null_source.get("generator_policy_id") != "ALMAS_NULL_WITHIN_YEAR_V1":
        fail("S2 must bind the frozen Q6 generator")
    calibration_principles = recurrence_null_calibration_policy.get("principles", {})
    for key in (
        "case_fitting_forbidden",
        "diagnostic_only",
        "px_ps_scores_unchanged",
        "iem_unchanged",
        "idd_unchanged",
        "irc_unchanged",
        "ontology_unchanged",
        "combined_p_value_forbidden",
        "external_nulls_required_before_weighting",
        "development_cases_cannot_define_thresholds",
    ):
        if calibration_principles.get(key) is not True:
            fail(f"recurrence null calibration invariant failed: {key}")
    if calibration_principles.get("metaphysical_probability") is not False:
        fail("S2 must forbid metaphysical probability")
    if calibration_principles.get("external_population_claim") is not False:
        fail("S2 self-contained null must not claim external population")

    if recurrence_synthetic_controls_policy.get("policy_id") != "ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1":
        fail("recurrence synthetic controls policy id changed")
    if recurrence_synthetic_controls_policy.get("status") != "FROZEN_EXPERIMENTAL_DIAGNOSTIC":
        fail("recurrence synthetic controls policy must remain diagnostic")
    if recurrence_synthetic_controls_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("recurrence synthetic controls policy must remain E_PROJECT_POLICY")
    synthetic_principles = recurrence_synthetic_controls_policy.get("principles", {})
    for key in (
        "case_fitting_forbidden",
        "diagnostic_only",
        "deterministic_no_rng",
        "preserve_root_count",
        "preserve_root_strengths",
        "preserve_dependency_families",
        "px_ps_scores_unchanged",
        "iem_unchanged",
        "idd_unchanged",
        "irc_unchanged",
        "ontology_unchanged",
        "external_nulls_required_before_weighting",
        "development_cases_cannot_define_thresholds",
    ):
        if synthetic_principles.get(key) is not True:
            fail(f"recurrence synthetic control invariant failed: {key}")
    for key in (
        "metaphysical_probability",
        "population_probability_claim",
        "p_value_claim",
    ):
        if synthetic_principles.get(key) is not False:
            fail(f"recurrence synthetic control field must remain false: {key}")
    control_ids = [
        item.get("id")
        for item in recurrence_synthetic_controls_policy.get("control_families", [])
        if isinstance(item, dict)
    ]
    if control_ids != [
        "SEMANTIC_SIGNATURE_ROTATION",
        "DECOUPLED_POINT_RELATION_ROTATION",
    ]:
        fail("S3 control family registry changed")

    if external_recurrence_cohort_policy.get("policy_id") != "ALMAS_EXTERNAL_RECURRENCE_COHORT_V1":
        fail("external recurrence cohort policy id changed")
    if external_recurrence_cohort_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("external recurrence cohort policy must remain protocol-only")
    if external_recurrence_cohort_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("external recurrence cohort policy must remain E_PROJECT_POLICY")
    external_principles = external_recurrence_cohort_policy.get("principles", {})
    for key in (
        "case_fitting_forbidden",
        "preregistration_required_for_external_candidate",
        "contamination_forbids_external_candidate",
        "development_only_never_validates_its_own_rule",
        "raw_private_case_storage_in_repo_forbidden",
        "public_output_must_be_aggregate_only",
        "sample_identifiers_not_exposed_in_public_summary",
        "sample_snapshots_not_exposed_in_public_summary",
        "label_narrative_outcome_leakage_forbidden",
        "structural_snapshot_required",
        "px_ps_scores_unchanged",
        "iem_unchanged",
        "idd_unchanged",
        "irc_unchanged",
        "ontology_unchanged",
    ):
        if external_principles.get(key) is not True:
            fail(f"S4 external cohort invariant failed: {key}")
    for key in (
        "metaphysical_probability",
        "weighting_enabled",
        "l3_validation_enabled",
    ):
        if external_principles.get(key) is not False:
            fail(f"S4 external cohort field must remain false: {key}")
    if external_recurrence_cohort_policy.get("allowed_null_models") != [
        "PAIR_SHUFFLE",
        "MATCHED_AGE",
        "MATCHED_AGE_CLOCK",
    ]:
        fail("S4 allowed external null model registry changed")

    if external_recurrence_calibration_policy.get("policy_id") != "ALMAS_EXTERNAL_RECURRENCE_CALIBRATION_V1":
        fail("external recurrence calibration policy id changed")
    if external_recurrence_calibration_policy.get("status") != "FROZEN_EXPERIMENTAL_DIAGNOSTIC":
        fail("external recurrence calibration policy must remain diagnostic")
    if external_recurrence_calibration_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("external recurrence calibration policy must remain E_PROJECT_POLICY")
    external_calibration_principles = external_recurrence_calibration_policy.get("principles", {})
    for key in (
        "case_fitting_forbidden",
        "diagnostic_only",
        "clean_external_candidates_only",
        "preregistered_only",
        "development_only_excluded",
        "contaminated_samples_excluded",
        "leakage_samples_excluded",
        "aggregate_public_output_only",
        "sample_identifiers_not_exposed",
        "sample_snapshots_not_exposed",
        "px_ps_scores_unchanged",
        "iem_unchanged",
        "idd_unchanged",
        "irc_unchanged",
        "ontology_unchanged",
        "combined_p_value_forbidden",
        "multiple_testing_correction_not_claimed",
    ):
        if external_calibration_principles.get(key) is not True:
            fail(f"S5 external calibration invariant failed: {key}")
    for key in (
        "weighting_enabled",
        "candidate_freeze_enabled",
        "l3_validation_enabled",
        "metaphysical_probability",
        "population_probability_claim",
    ):
        if external_calibration_principles.get(key) is not False:
            fail(f"S5 external calibration field must remain false: {key}")
    if external_recurrence_calibration_policy.get("allowed_null_models") != [
        "PAIR_SHUFFLE",
        "MATCHED_AGE",
        "MATCHED_AGE_CLOCK",
    ]:
        fail("S5 allowed external null model registry changed")

    if px_v3_candidate_freeze_policy.get("policy_id") != "ALMAS_PX_V3_CANDIDATE_FREEZE_V1":
        fail("PX v3 candidate freeze policy id changed")
    if px_v3_candidate_freeze_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("PX v3 candidate freeze policy must remain protocol-only")
    if px_v3_candidate_freeze_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("PX v3 candidate freeze policy must remain E_PROJECT_POLICY")
    px3_principles = px_v3_candidate_freeze_policy.get("principles", {})
    for key in (
        "case_fitting_forbidden",
        "development_cases_cannot_validate_candidate",
        "freeze_before_holdout",
        "runtime_registry_mutation_forbidden",
        "candidate_freeze_is_not_validation",
    ):
        if px3_principles.get(key) is not True:
            fail(f"S6 PX v3 freeze invariant failed: {key}")
    for key in (
        "scoring_enabled",
        "weighting_enabled",
        "ontology_enabled",
        "l3_validation_enabled",
        "metaphysical_probability",
    ):
        if px3_principles.get(key) is not False:
            fail(f"S6 PX v3 field must remain false: {key}")
    if px_v3_candidate_registry.get("registry_id") != "ALMAS_PX_V3_CANDIDATES":
        fail("PX v3 registry id changed")
    if px_v3_candidate_registry.get("policy_id") != "ALMAS_PX_V3_CANDIDATE_FREEZE_V1":
        fail("PX v3 registry/policy mismatch")
    if px_v3_candidate_registry.get("records") != []:
        fail("canonical PX v3 registry must remain empty before candidate preregistration")
    if px_v3_candidate_registry.get("validated_candidate_ids") != []:
        fail("S6 cannot contain validated PX v3 candidates")

    if px_v3_holdout_evaluation_policy.get("policy_id") != "ALMAS_PX_V3_HOLDOUT_EVALUATION_V1":
        fail("PX v3 holdout evaluation policy id changed")
    if px_v3_holdout_evaluation_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("PX v3 holdout evaluation policy must remain protocol-only")
    if px_v3_holdout_evaluation_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("PX v3 holdout evaluation policy must remain E_PROJECT_POLICY")
    s7_principles = px_v3_holdout_evaluation_policy.get("principles", {})
    for key in (
        "candidate_must_be_frozen_for_validation",
        "cohort_must_pass_s4_firewall",
        "clean_external_samples_only",
        "development_overlap_forbidden",
        "formula_ref_must_match_frozen_candidate",
        "complete_score_coverage_required",
        "aggregate_public_output_only",
        "sample_identifiers_not_exposed",
        "sample_values_not_exposed",
        "threshold_fitting_on_holdout_forbidden",
        "promotion_decision_forbidden",
    ):
        if s7_principles.get(key) is not True:
            fail(f"S7 holdout invariant failed: {key}")
    for key in (
        "scoring_enabled",
        "weighting_enabled",
        "ontology_enabled",
        "l3_validation_enabled",
        "metaphysical_probability",
        "population_probability_claim",
    ):
        if s7_principles.get(key) is not False:
            fail(f"S7 holdout field must remain false: {key}")

    if px_v3_promotion_gate_policy.get("policy_id") != "ALMAS_PX_V3_PROMOTION_GATE_V1":
        fail("PX v3 promotion gate policy id changed")
    if px_v3_promotion_gate_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("PX v3 promotion gate policy must remain protocol-only")
    if px_v3_promotion_gate_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("PX v3 promotion gate policy must remain E_PROJECT_POLICY")
    s8_principles = px_v3_promotion_gate_policy.get("principles", {})
    for key in (
        "candidate_must_be_frozen_for_validation",
        "holdout_formula_must_match",
        "holdout_evaluation_must_be_diagnostic_only",
        "all_preregistered_criteria_must_pass",
        "independent_replication_required",
        "negative_controls_required",
        "ablation_required",
        "leakage_audit_required",
        "post_holdout_rule_change_forbidden",
        "case_fitting_forbidden",
        "automatic_registry_mutation_forbidden",
        "manual_new_version_required_for_activation",
        "promotion_eligible_is_not_active",
    ):
        if s8_principles.get(key) is not True:
            fail(f"S8 promotion invariant failed: {key}")
    for key in (
        "scoring_enabled",
        "weighting_enabled",
        "ontology_enabled",
        "l3_validation_enabled",
        "metaphysical_probability",
    ):
        if s8_principles.get(key) is not False:
            fail(f"S8 promotion field must remain false: {key}")

    if px_v3_activation_firewall_policy.get("policy_id") != "ALMAS_PX_V3_ACTIVATION_FIREWALL_V1":
        fail("PX v3 activation firewall policy id changed")
    if px_v3_activation_firewall_policy.get("status") != "FROZEN_RELEASE_FIREWALL":
        fail("PX v3 activation firewall must remain release-locked")
    if px_v3_activation_firewall_policy.get("release_line") != "1.15":
        fail("PX v3 activation firewall must remain bound to 1.15")
    if px_v3_activation_firewall_policy.get("operational_px_engine") != "ALMAS_SEMANTIC_MOTIF_V2":
        fail("ALMAS 1.15 must retain PX v2 as operational engine")
    if px_v3_activation_firewall_policy.get("px_v3_operational_in_release") is not False:
        fail("PX v3 must remain non-operational in ALMAS 1.15")
    s9_principles = px_v3_activation_firewall_policy.get("principles", {})
    for key in (
        "same_release_activation_forbidden",
        "promotion_eligible_does_not_activate",
        "manual_registry_change_required",
        "new_semver_required",
        "new_release_audit_required",
        "new_public_contract_validation_required",
        "runtime_activation_forbidden",
        "automatic_registry_mutation_forbidden",
        "px_v2_remains_operational",
    ):
        if s9_principles.get(key) is not True:
            fail(f"S9 activation firewall invariant failed: {key}")
    for key in (
        "px_v3_scoring_enabled",
        "px_v3_weighting_enabled",
        "px_v3_ontology_enabled",
        "px_v3_l3_validation_enabled",
        "metaphysical_probability",
    ):
        if s9_principles.get(key) is not False:
            fail(f"S9 activation firewall field must remain false: {key}")

    if validation_preregistration_bundle_policy.get("policy_id") != "ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1":
        fail("1.16 preregistration bundle policy id changed")
    if validation_preregistration_bundle_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("1.16 preregistration bundle policy must remain frozen")
    if validation_preregistration_bundle_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("1.16 preregistration bundle must remain E_PROJECT_POLICY")
    v1_principles = validation_preregistration_bundle_policy.get("principles", {})
    for key in (
        "candidate_must_be_frozen_for_validation",
        "holdout_must_be_unopened",
        "formula_ref_must_be_frozen",
        "development_holdout_separation_required",
        "endpoints_frozen_before_holdout",
        "success_failure_criteria_frozen_before_holdout",
        "blinding_plan_required",
        "leakage_audit_plan_required",
        "negative_controls_required",
        "ablation_plan_required",
        "independent_replication_plan_required",
        "raw_holdout_samples_forbidden",
        "observed_holdout_results_forbidden",
        "private_case_material_forbidden",
        "bundle_fingerprint_required",
        "automatic_registry_mutation_forbidden",
    ):
        if v1_principles.get(key) is not True:
            fail(f"1.16 V1 preregistration invariant failed: {key}")
    for key in (
        "scoring_enabled",
        "weighting_enabled",
        "ontology_enabled",
        "l3_validation_enabled",
        "metaphysical_probability",
    ):
        if v1_principles.get(key) is not False:
            fail(f"1.16 V1 preregistration field must remain false: {key}")

    v1_schema_props = validation_preregistration_bundle_schema.get("properties", {})
    if v1_schema_props.get("policy_id", {}).get("const") != "ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1":
        fail("1.16 V1 schema policy id changed")
    for field in (
        "holdout_opened",
        "observed_results_present",
        "raw_samples_present",
        "automatic_registry_mutation",
        "scoring_enabled",
        "weighting_enabled",
        "ontology_enabled",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v1_schema_props.get(field, {}).get("const") is not False:
            fail(f"1.16 V1 schema must lock {field}=false")

    if holdout_open_gate_policy.get("policy_id") != "ALMAS_HOLDOUT_OPEN_GATE_V1":
        fail("1.16 V2 holdout open gate policy id changed")
    if holdout_open_gate_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("1.16 V2 holdout open gate must remain frozen")
    if holdout_open_gate_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("1.16 V2 holdout open gate must remain E_PROJECT_POLICY")
    v2_principles = holdout_open_gate_policy.get("principles", {})
    for key in (
        "preregistration_fingerprint_must_match",
        "runtime_version_must_match_frozen",
        "runtime_commit_must_match_frozen",
        "candidate_formula_must_match_frozen",
        "cohort_metadata_must_match_frozen",
        "minimum_sample_count_must_be_met",
        "observed_results_forbidden_at_open",
        "posthoc_changes_forbidden",
        "open_gate_does_not_evaluate_holdout",
        "open_gate_does_not_promote_candidate",
        "automatic_registry_mutation_forbidden",
        "scoring_activation_forbidden",
        "weighting_activation_forbidden",
        "ontology_activation_forbidden",
        "l3_validation_forbidden",
    ):
        if v2_principles.get(key) is not True:
            fail(f"1.16 V2 invariant failed: {key}")
    if v2_principles.get("metaphysical_probability") is not False:
        fail("1.16 V2 must forbid metaphysical probability")

    v2_schema_props = holdout_open_record_schema.get("properties", {})
    if v2_schema_props.get("policy_id", {}).get("const") != "ALMAS_HOLDOUT_OPEN_GATE_V1":
        fail("1.16 V2 schema policy id changed")
    for field in (
        "holdout_evaluated",
        "promotion_permitted",
        "automatic_registry_mutation",
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v2_schema_props.get(field, {}).get("const") is not False:
            fail(f"1.16 V2 schema must lock {field}=false")
    if v2_schema_props.get("holdout_opened", {}).get("const") is not True:
        fail("1.16 V2 schema must require holdout_opened=true")
    if v2_schema_props.get("holdout_evaluation_permitted", {}).get("const") is not True:
        fail("1.16 V2 schema must permit holdout evaluation after gate")

    if validation_execution_ledger_policy.get("policy_id") != "ALMAS_VALIDATION_EXECUTION_LEDGER_V1":
        fail("1.16 V3 ledger policy id changed")
    if validation_execution_ledger_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("1.16 V3 ledger policy must remain frozen")
    if validation_execution_ledger_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("1.16 V3 ledger must remain E_PROJECT_POLICY")
    if validation_execution_ledger_policy.get("event_order") != [
        "PREREGISTERED",
        "HOLDOUT_OPENED",
        "HOLDOUT_EVALUATED",
        "DOCUMENTARY_REVEALED",
        "VALIDATION_CLOSED",
    ]:
        fail("1.16 V3 ledger event order changed")
    v3_principles = validation_execution_ledger_policy.get("principles", {})
    for key in (
        "append_only",
        "strict_event_order",
        "hash_chain_required",
        "prior_entries_immutable",
        "opaque_references_only",
        "private_payloads_forbidden",
        "automatic_registry_mutation_forbidden",
        "ledger_does_not_promote_candidate",
        "ledger_does_not_activate_scoring",
        "ledger_does_not_validate_l3",
    ):
        if v3_principles.get(key) is not True:
            fail(f"1.16 V3 ledger invariant failed: {key}")
    if v3_principles.get("metaphysical_probability") is not False:
        fail("1.16 V3 must forbid metaphysical probability")

    v3_schema_props = validation_execution_ledger_schema.get("properties", {})
    if v3_schema_props.get("policy_id", {}).get("const") != "ALMAS_VALIDATION_EXECUTION_LEDGER_V1":
        fail("1.16 V3 schema policy id changed")
    if v3_schema_props.get("promotion_decision", {}).get("const") != "FORBIDDEN":
        fail("1.16 V3 ledger must forbid promotion decisions")
    for field in (
        "automatic_registry_mutation",
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v3_schema_props.get(field, {}).get("const") is not False:
            fail(f"1.16 V3 schema must lock {field}=false")
    if validation_continuity_gate_policy.get("policy_id") != "ALMAS_VALIDATION_CONTINUITY_GATE_V1":
        fail("1.16 V4 continuity gate policy id changed")
    if validation_continuity_gate_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("1.16 V4 continuity gate must remain frozen")
    if validation_continuity_gate_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("1.16 V4 continuity gate must remain E_PROJECT_POLICY")
    if validation_continuity_gate_policy.get("required_ledger_events") != [
        "PREREGISTERED",
        "HOLDOUT_OPENED",
        "HOLDOUT_EVALUATED",
    ]:
        fail("1.16 V4 required ledger events changed")
    v4_principles = validation_continuity_gate_policy.get("principles", {})
    for key in (
        "preregistration_hash_must_match",
        "opening_hash_must_match",
        "holdout_artifact_hash_must_match",
        "ledger_hash_chain_must_be_valid",
        "candidate_id_continuity_required",
        "formula_ref_continuity_required",
        "cohort_identity_continuity_required",
        "null_model_continuity_required",
        "runtime_version_commit_frozen",
        "promotion_bridge_requires_continuity",
        "distribution_fingerprint_required",
        "private_payloads_forbidden_in_certificate",
        "automatic_registry_mutation_forbidden",
        "continuity_does_not_promote_candidate",
        "continuity_does_not_activate_scoring",
    ):
        if v4_principles.get(key) is not True:
            fail(f"1.16 V4 continuity invariant failed: {key}")
    for key in (
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v4_principles.get(key) is not False:
            fail(f"1.16 V4 continuity field must remain false: {key}")

    v4_schema_props = validation_continuity_certificate_schema.get(
        "properties", {}
    )
    if v4_schema_props.get("policy_id", {}).get("const") != "ALMAS_VALIDATION_CONTINUITY_GATE_V1":
        fail("1.16 V4 certificate schema policy id changed")
    for field in (
        "required_ledger_events_verified",
        "continuity_verified",
        "promotion_bridge_permitted",
    ):
        if v4_schema_props.get(field, {}).get("const") is not True:
            fail(f"1.16 V4 certificate must require {field}=true")
    for field in (
        "private_payloads_exposed",
        "automatic_registry_mutation",
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v4_schema_props.get(field, {}).get("const") is not False:
            fail(f"1.16 V4 certificate must lock {field}=false")

    if validation_closure_release_audit_policy.get("policy_id") != "ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1":
        fail("1.16 V5 closure/release policy id changed")
    if validation_closure_release_audit_policy.get("status") != "FROZEN_EXPERIMENTAL_PROTOCOL":
        fail("1.16 V5 closure/release policy must remain frozen")
    if validation_closure_release_audit_policy.get("epistemic_class") != "E_PROJECT_POLICY":
        fail("1.16 V5 closure/release policy must remain E_PROJECT_POLICY")
    if validation_closure_release_audit_policy.get("required_ledger_boundary_before_reveal") != "HOLDOUT_EVALUATED":
        fail("1.16 V5 reveal boundary changed")
    if validation_closure_release_audit_policy.get("required_ledger_boundary_before_close") != "DOCUMENTARY_REVEALED":
        fail("1.16 V5 closure boundary changed")
    if validation_closure_release_audit_policy.get("final_ledger_event") != "VALIDATION_CLOSED":
        fail("1.16 V5 final ledger event changed")
    v5_principles = validation_closure_release_audit_policy.get("principles", {})
    for key in (
        "documentary_reveal_requires_continuity",
        "structural_output_invariance_required",
        "leakage_counts_must_be_zero",
        "unexpected_reveal_fields_fail_closed",
        "public_identity_requires_risk_refs",
        "s8_result_required_for_closure",
        "eligible_and_noneligible_cycles_may_close",
        "ledger_must_end_validation_closed",
        "release_audit_package_aggregate_only",
        "private_payloads_forbidden",
        "manual_release_review_required",
        "manual_new_version_required_for_activation",
        "same_release_activation_forbidden",
        "automatic_registry_mutation_forbidden",
    ):
        if v5_principles.get(key) is not True:
            fail(f"1.16 V5 closure invariant failed: {key}")
    for key in (
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v5_principles.get(key) is not False:
            fail(f"1.16 V5 closure field must remain false: {key}")

    v5_reveal_props = documentary_reveal_record_schema.get("properties", {})
    if v5_reveal_props.get("policy_id", {}).get("const") != "ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1":
        fail("1.16 V5 reveal schema policy id changed")
    for field in (
        "structural_output_invariant",
    ):
        if v5_reveal_props.get(field, {}).get("const") is not True:
            fail(f"1.16 V5 reveal schema must require {field}=true")
    for field in (
        "forbidden_field_hits",
        "label_leakage_count",
        "narrative_leakage_count",
        "case_fitting_count",
        "post_holdout_rule_change_count",
    ):
        if v5_reveal_props.get(field, {}).get("const") != 0:
            fail(f"1.16 V5 reveal schema must require {field}=0")
    if v5_reveal_props.get("promotion_decision", {}).get("const") != "FORBIDDEN":
        fail("1.16 V5 reveal must forbid promotion decisions")
    for field in (
        "private_payloads_exposed",
        "automatic_registry_mutation",
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v5_reveal_props.get(field, {}).get("const") is not False:
            fail(f"1.16 V5 reveal schema must lock {field}=false")

    v5_closure_props = validation_closure_record_schema.get("properties", {})
    if v5_closure_props.get("policy_id", {}).get("const") != "ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1":
        fail("1.16 V5 closure schema policy id changed")
    for field in (
        "confirmatory_cycle_closed",
        "manual_new_version_required_for_activation",
        "manual_release_review_required",
        "same_release_activation_forbidden",
    ):
        if v5_closure_props.get(field, {}).get("const") is not True:
            fail(f"1.16 V5 closure schema must require {field}=true")
    for field in (
        "automatic_registry_mutation",
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v5_closure_props.get(field, {}).get("const") is not False:
            fail(f"1.16 V5 closure schema must lock {field}=false")

    v5_release_props = validation_release_audit_package_schema.get(
        "properties", {}
    )
    if v5_release_props.get("policy_id", {}).get("const") != "ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1":
        fail("1.16 V5 release-audit schema policy id changed")
    if v5_release_props.get("closed_ledger_entry_count", {}).get("const") != 5:
        fail("1.16 V5 release-audit package must require five ledger events")
    for field in (
        "release_audit_ready",
        "manual_release_review_required",
        "manual_new_version_required_for_activation",
        "same_release_activation_forbidden",
    ):
        if v5_release_props.get(field, {}).get("const") is not True:
            fail(f"1.16 V5 release-audit schema must require {field}=true")
    for field in (
        "private_payloads_exposed",
        "automatic_registry_mutation",
        "scoring_activation",
        "weighting_activation",
        "ontology_activation",
        "l3_validation",
        "metaphysical_probability",
    ):
        if v5_release_props.get(field, {}).get("const") is not False:
            fail(f"1.16 V5 release-audit schema must lock {field}=false")

    s8_required = set(px_v3_promotion_evidence_schema.get("required", []))
    for field in (
        "candidate",
        "holdout_evaluations",
        "external_calibration_refs",
        "independent_replication_refs",
        "leakage_audit_refs",
        "criterion_results",
        "negative_control_failure_count",
        "ablation_failure_count",
        "case_fitting_count",
        "label_leakage_count",
        "narrative_leakage_count",
        "post_holdout_rule_change_count",
    ):
        if field not in s8_required:
            fail(f"S8 promotion evidence schema missing required field: {field}")
    for field in ("scoring_enabled", "weighting_enabled", "ontology_enabled"):
        if px_v3_candidate_registry.get(field) is not False:
            fail(f"PX v3 canonical registry must keep {field}=false")
    px3_schema_props = px_v3_candidate_registry_schema.get("properties", {})
    if px3_schema_props.get("registry_id", {}).get("const") != "ALMAS_PX_V3_CANDIDATES":
        fail("PX v3 candidate schema registry id changed")
    if px3_schema_props.get("policy_id", {}).get("const") != "ALMAS_PX_V3_CANDIDATE_FREEZE_V1":
        fail("PX v3 candidate schema policy id changed")
    if px3_schema_props.get("validated_candidate_ids", {}).get("maxItems") != 0:
        fail("S6 schema must prohibit validated PX v3 candidate ids")
    external_schema_props = external_recurrence_cohort_schema.get("properties", {})
    if set(external_schema_props.get("null_model", {}).get("enum", [])) != {
        "PAIR_SHUFFLE",
        "MATCHED_AGE",
        "MATCHED_AGE_CLOCK",
    }:
        fail("S4 schema null_model enum diverges from policy")
    sample_schema = (
        external_schema_props.get("samples", {})
        .get("items", {})
        .get("properties", {})
    )
    recurrence_snapshot_schema = sample_schema.get("recurrence_snapshot", {})
    if "pillar_attribution" not in recurrence_snapshot_schema.get("required", []):
        fail("S4 recurrence snapshot must require pillar_attribution")

    if model_attribution_policy.get("policy_id") != "ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V2":
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
    if model_attribution_policy.get("attribution_unit") != "CANONICAL_EVIDENCE_UNIT":
        fail("1.14 Shapley must operate on canonical evidence units")
    if model_attribution_policy.get("derived_motif_units_are_independent_evidence") is not False:
        fail("derived motif units must not be declared independent evidence")

    if birth_time_perturbation_policy.get("policy_id") != "ALMAS_BIRTH_TIME_SENSITIVITY_V2":
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
    q4_curve = birth_time_perturbation_policy.get("diagnostic_curve", {})
    if q4_curve.get("windows_minutes") != [5, 15, 30, 60, 120]:
        fail("1.14 birth-time diagnostic curve windows changed")
    if q4_principles.get("missing_time_reliability_allows_diagnostic_curve") is not True:
        fail("missing reliability must still allow diagnostic time curve")
    if q4_principles.get("missing_time_reliability_forbids_single_birth_time_component") is not True:
        fail("undocumented reliability must forbid a single BIRTH_TIME component")

    if analysis_profile_policy.get("policy_id") != "ALMAS_ANALYSIS_PROFILES_V1":
        fail("analysis profile policy id changed")
    profile_principles = analysis_profile_policy.get("principles", {})
    if profile_principles.get("ready_means_profile_complete_not_metaphysically_proven") is not True:
        fail("READY must mean profile completeness, not metaphysical proof")
    profiles = analysis_profile_policy.get("profiles", {})
    if "FULL_ASTROLOGY" not in profiles or "FULL_MULTIDISCIPLINARY" not in profiles:
        fail("1.14 analysis profiles missing")
    full_astro = profiles.get("FULL_ASTROLOGY", {})
    if not {"M26", "M27", "M28", "M29"}.issubset(set(full_astro.get("excluded_modules", []))):
        fail("FULL_ASTROLOGY must exclude temporal/doctrine/reality modules by default")

    if hellenistic_lots_policy.get("policy_id") != "ALMAS_HELLENISTIC_LOTS_V1":
        fail("default Hellenistic lots policy id changed")
    lot_ids = {
        item.get("id")
        for item in hellenistic_lots_policy.get("lots", [])
        if isinstance(item, dict)
    }
    if lot_ids != {"FORTUNE", "SPIRIT"}:
        fail("default historical lots must remain Fortune and Spirit only")
    if hellenistic_lots_policy.get("principles", {}).get("lot_result_is_not_ontological_discriminator") is not True:
        fail("historical lots must not become ontological discriminators")

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

    if canonical_assembly_policy.get("policy_id") != "ALMAS_CANONICAL_ASSEMBLY_V2":
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
    if canonical_assembly_policy.get("model_state", {}).get("supported_requires_birth_time_component_when_timed_architecture") is not True:
        fail("timed architecture must require BIRTH_TIME for SUPPORTED")
    if q7_principles.get("ready_is_profile_completeness_not_metaphysical_truth") is not True:
        fail("canonical READY semantics must remain profile-scoped")
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

    natal_context_required = set(natal_context_schema.get("required", []))
    if not {"subjects", "cross_house_placements"}.issubset(
        natal_context_required
    ):
        fail(
            "natal context schema must require subjects and cross-house placements"
        )

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
    if "field_context" not in relationship_chart_consonance_schema.get("required", []):
        fail("M09 must expose relationship field authoring context")
    field_context_schema = (
        relationship_chart_consonance_schema.get("properties", {})
        .get("field_context", {})
    )
    field_props = field_context_schema.get("properties", {})
    if field_props.get("authoring_only", {}).get("const") is not True:
        fail("M09 relationship field must remain authoring_only")
    if field_props.get("structural_evidence_used", {}).get("const") is not False:
        fail("M09 relationship field must not become structural evidence")
    if field_props.get("creates_independent_roots", {}).get("const") is not False:
        fail("M09 relationship field must not create independent roots")
    if (
        field_props.get("composite", {})
        .get("properties", {})
        .get("houses_calculated", {})
        .get("const")
        is not False
    ):
        fail("M07 composite houses must remain unavailable")
    composite_field = field_props.get("composite", {})
    davison_field = field_props.get("davison", {})
    for field_name, field_schema in (
        ("composite", composite_field),
        ("davison", davison_field),
    ):
        if "angle_contacts" not in set(field_schema.get("required", [])):
            fail(f"M09 {field_name} field must require position-angle contacts")
        if (
            field_schema.get("properties", {})
            .get("angle_contacts", {})
            .get("$ref")
            != "#/$defs/internal_contacts"
        ):
            fail(f"M09 {field_name} angle contacts must reuse internal contact contract")
    if "house_placements" not in set(davison_field.get("required", [])):
        fail("M09 relationship field must expose explicit Davison house placements")
    placement_schema = (
        davison_field.get("properties", {})
        .get("house_placements", {})
        .get("additionalProperties", {})
    )
    if placement_schema.get("minimum") != 1 or placement_schema.get("maximum") != 12:
        fail("Davison house placements must remain within houses 1..12")

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
    if evidence_graph_schema.get("properties", {}).get("technique_dependency_registry_id", {}).get("const") != "ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1":
        fail("evidence graph must expose the canonical technique/dependency registry id")
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
    if not {"preregistration_ref", "delta90", "preserved_fraction", "robustness_component", "robustness_component_eligible"}.issubset(
        set(time_sensitivity_schema.get("required", []))
    ):
        fail("time sensitivity schema lacks v2 robustness fields")
    for field in ("diagnostic_curve", "diagnostic_curve_labels", "time_reliability_state"):
        if field not in time_sensitivity_schema.get("properties", {}):
            fail(f"time sensitivity schema missing v2 field: {field}")

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
    calibration_schema = null_model_output_schema.get("properties", {}).get("recurrence_calibration", {})
    calibration_props = calibration_schema.get("properties", {})
    if calibration_props.get("policy_id", {}).get("const") != "ALMAS_RECURRENCE_NULL_CALIBRATION_V1":
        fail("M24 schema must bind the S2 recurrence calibration policy")
    for field in (
        "used_for_weighting",
        "used_in_px_score",
        "used_in_ps_score",
        "used_in_iem",
        "used_in_idd",
        "used_in_irc",
        "used_in_ontology",
        "metaphysical_probability",
        "external_population_claim",
    ):
        if calibration_props.get(field, {}).get("const") is not False:
            fail(f"M24 S2 calibration field must remain false: {field}")
    synthetic_schema = null_model_output_schema.get("properties", {}).get("synthetic_recurrence_controls", {})
    synthetic_props = synthetic_schema.get("properties", {})
    if synthetic_props.get("policy_id", {}).get("const") != "ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1":
        fail("M24 schema must bind the S3 synthetic control policy")
    for field in (
        "used_for_weighting",
        "used_in_px_score",
        "used_in_ps_score",
        "used_in_iem",
        "used_in_idd",
        "used_in_irc",
        "used_in_ontology",
        "metaphysical_probability",
        "population_probability_claim",
        "p_value_claim",
    ):
        if synthetic_props.get(field, {}).get("const") is not False:
            fail(f"M24 S3 synthetic control field must remain false: {field}")

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
    if report_gate_props.get("gate_version", {}).get("const") != "1.1.0":
        fail("M30 gate version must be 1.1.0 for profile-aware completeness")
    for field in ("analysis_profile", "profile_policy_id", "profile_assessment"):
        if field not in report_gate_schema.get("required", []):
            fail(f"M30 profile field missing: {field}")
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

    report_model_handler_text = (
        ROOT / "src/almas_tfa/report_model_handlers.py"
    ).read_text(encoding="utf-8")
    if report_model_handler_text.count('"natal_context"') < 4:
        fail("M31 must expose natal_context to core interpretive sections")
    if report_model_handler_text.count('"relationship_field"') < 4:
        fail("M31 must expose relationship_field to core interpretive sections")

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

    authored_props = authored_report_schema.get("properties", {})
    if authored_props.get("document_kind", {}).get("const") != "ALMAS_AUTHORED_REPORT":
        fail("authored report document kind changed")
    if authored_props.get("interpretive_center", {}).get("const") != "ASTROLOGY_AND_SOURCE_BASED_METAPHYSICAL_HERMENEUTICS":
        fail("authored report must keep astrology and source-based metaphysical hermeneutics as interpretive center")
    if authored_props.get("technical_role", {}).get("const") != "CALCULATION_TRACEABILITY_AND_QUALITY_CONTROL":
        fail("authored report technical role changed")
    for field in (
        "metaphysical_scientific_validation_claimed",
        "canonical_values_mutated",
        "new_calculations_performed",
        "new_scores_created",
    ):
        if authored_props.get(field, {}).get("const") is not False:
            fail(f"authored report field {field} must remain false")
    authored_sections = authored_props.get("sections", {})
    if authored_sections.get("minItems") != 11 or authored_sections.get("maxItems") != 11:
        fail("authored report must preserve the eleven-section M31 structure")
    if "bibliography" not in authored_report_schema.get("required", []):
        fail("authored report must require publication bibliography")

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

    support_ref_item = claim_props.get("source_support_refs", {}).get("items", {})
    if set(support_ref_item.get("required", [])) != {"source_id", "support_index", "resolved"}:
        fail("doctrinal source_support_ref must require resolution state")
    if support_ref_item.get("properties", {}).get("resolved", {}).get("type") != "boolean":
        fail("doctrinal source_support_ref resolved must be boolean")
    for field in (
        "contemporary_usage_promoted_to_ontology",
        "project_hypothesis_promoted_to_doctrine",
        "cross_tradition_identity_inferred",
        "doctrine_adds_structural_score",
    ):
        if claim_props.get(field, {}).get("const") is not False:
            fail(f"doctrinal claim firewall must lock {field}=false")


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

    required_natal_substrate_sources = {
        "astrodienst_zodiac_sign",
        "astrodienst_element",
        "astrodienst_quality",
        "astrodienst_sign_ruler",
        "astrodienst_house_ruler",
    }
    missing_natal_sources = required_natal_substrate_sources - source_ids
    if missing_natal_sources:
        fail(
            "natal-substrate hermeneutics missing registered sources: "
            + ", ".join(sorted(missing_natal_sources))
        )

    required_planetary_function_sources = {
        "astrodienst_personal_planet",
        "astrodienst_jupiter",
        "astrodienst_saturn",
        "astrodienst_uranus",
        "astrodienst_neptune",
        "astrodienst_pluto",
    }
    missing_planetary_sources = required_planetary_function_sources - source_ids
    if missing_planetary_sources:
        fail(
            "planetary-function hermeneutics missing registered sources: "
            + ", ".join(sorted(missing_planetary_sources))
        )

    required_aspect_geometry_sources = {
        "astrodienst_aspect",
        "astrodienst_conjunction",
        "astrodienst_opposition",
        "astrodienst_square",
        "astrodienst_trine",
        "astrodienst_sextile",
    }
    missing_aspect_sources = required_aspect_geometry_sources - source_ids
    if missing_aspect_sources:
        fail(
            "aspect-geometry hermeneutics missing registered sources: "
            + ", ".join(sorted(missing_aspect_sources))
        )

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

    expected_canonical_required = {
        "schema_version",
        "analysis_mode",
        "analysis_profile",
        "profile_policy_id",
        "astronomy_backend",
        "evidence",
        "models",
        "indices",
        "pairwise_idd",
        "coverage",
        "robustness",
        "counterevidence",
        "counterevidence_state",
        "ontology",
        "doctrine",
        "temporal",
        "limitations",
        "assembly",
    }
    if set(canonical_schema.get("required", [])) != expected_canonical_required:
        fail("canonical schema required root field set changed")
    if set(
        canonical_schema.get("properties", {})
        .get("analysis_mode", {})
        .get("enum", [])
    ) != {"FULL", "TEMPORAL"}:
        fail("canonical analysis_mode must match current analysis profile policy")
    ontology_schema = canonical_schema.get("properties", {}).get("ontology", {})
    if ontology_schema.get("maxProperties") != 0:
        fail("canonical ontology placeholder must remain empty in M30")
    if ontology_schema.get("additionalProperties") is not False:
        fail("canonical ontology placeholder must reject properties")

    canonical_props = canonical_schema.get("properties", {})
    expected_canonical_root_props = {
        "schema_version",
        "analysis_mode",
        "analysis_profile",
        "profile_policy_id",
        "astronomy_backend",
        "natal_context",
        "relationship_field",
        "evidence",
        "models",
        "indices",
        "pairwise_idd",
        "coverage",
        "robustness",
        "counterevidence",
        "counterevidence_state",
        "ontology",
        "doctrine",
        "temporal",
        "semantic_motifs",
        "time_sensitivity",
        "limitations",
        "ontological_discrimination",
        "null_models",
        "assembly",
    }
    if set(canonical_props) != expected_canonical_root_props:
        fail("canonical schema root surface diverges from M30 output contract")
    if canonical_schema.get("additionalProperties") is not False:
        fail("canonical schema root must reject undeclared namespaces")

    if canonical_props.get("natal_context", {}).get("$ref") != "natal-context-output.schema.json":
        fail("canonical natal_context must compose the existing M04 output schema")
    if "natal_context" in set(canonical_schema.get("required", [])):
        fail("canonical natal_context must remain optional for legacy/imported analyses")
    if (
        canonical_props.get("relationship_field", {}).get("$ref")
        != "relationship-chart-consonance.schema.json#/properties/field_context"
    ):
        fail("canonical relationship_field must compose M09 field_context")
    if "relationship_field" in set(canonical_schema.get("required", [])):
        fail("canonical relationship_field must remain optional")

    if canonical_props.get("null_models", {}).get("$ref") != "null-model-output.schema.json":
        fail("canonical null_models must compose the M24 output schema")
    if canonical_props.get("semantic_motifs", {}).get("$ref") != "semantic-motif-graph.schema.json":
        fail("canonical semantic_motifs must compose the semantic motif graph schema")
    if canonical_props.get("time_sensitivity", {}).get("$ref") != "time-sensitivity-output.schema.json":
        fail("canonical time_sensitivity must compose the M23 output schema")
    if canonical_props.get("doctrine", {}).get("items", {}).get("$ref") != "doctrinal-claim.schema.json":
        fail("canonical doctrine items must compose the doctrinal claim schema")

    temporal_schema = canonical_props.get("temporal", {})
    if temporal_schema.get("additionalProperties") is not False:
        fail("canonical temporal wrapper must reject undeclared fields")
    temporal_props = temporal_schema.get("properties", {})
    if set(temporal_props) != {"activation", "events"}:
        fail("canonical temporal wrapper must expose exactly activation/events")
    if temporal_props.get("activation", {}).get("$ref") != "temporal-activation-output.schema.json":
        fail("canonical temporal.activation must compose M26 output schema")
    if temporal_props.get("events", {}).get("$ref") != "documentary-event-output.schema.json":
        fail("canonical temporal.events must compose M27 output schema")

    pairwise_schema = canonical_props.get("pairwise_idd", {})
    pairwise_item = pairwise_schema.get("additionalProperties", {})
    if pairwise_item.get("additionalProperties") is not False:
        fail("canonical pairwise_idd entries must reject undeclared fields")
    if set(pairwise_item.get("required", [])) != {"idd", "band"}:
        fail("canonical pairwise_idd entries must require idd and band")

    astronomy_backend_schema = canonical_props.get("astronomy_backend", {})
    expected_astronomy_backend_fields = {
        "state",
        "backend_id",
        "backend_version",
        "provenance_state",
        "provenance",
    }
    if set(astronomy_backend_schema.get("properties", {})) != expected_astronomy_backend_fields:
        fail("canonical astronomy backend trace surface changed")
    if set(astronomy_backend_schema.get("required", [])) != expected_astronomy_backend_fields:
        fail("canonical astronomy backend trace must require all trace fields")
    if astronomy_backend_schema.get("additionalProperties") is not False:
        fail("canonical astronomy backend trace must reject undeclared fields")
    production_rule_found = False
    for rule in astronomy_backend_schema.get("allOf", []):
        condition = (
            rule.get("if", {})
            .get("properties", {})
            .get("backend_id", {})
            .get("const")
        )
        if condition != "MOIRA_JPL_SPK":
            continue
        production_rule_found = True
        then_props = rule.get("then", {}).get("properties", {})
        if then_props.get("backend_version", {}).get("const") != "6.8.2":
            fail("canonical production astronomy backend version changed")
        if then_props.get("provenance_state", {}).get("const") != "DECLARED":
            fail("canonical production astronomy backend must require declared provenance")
        if then_props.get("provenance", {}).get("$ref") != "astronomy-backend-provenance.schema.json":
            fail("canonical production astronomy provenance must compose the production provenance schema")
    if not production_rule_found:
        fail("canonical schema lacks production astronomy provenance conditional")

    evidence_schema = canonical_props.get("evidence", {})
    evidence_item = evidence_schema.get("items", {})
    expected_evidence_fields = {
        "evidence_id",
        "source_module",
        "root_id",
        "root_key",
        "strength",
        "strength_state",
        "core_eligible",
        "dependency_families",
        "independent_family_count",
        "point_ids",
        "relation_ids",
        "concrete_contacts",
        "max_exactness",
        "house_overlays",
    }
    if set(evidence_item.get("properties", {})) != expected_evidence_fields:
        fail("canonical evidence projection surface changed")
    if set(evidence_item.get("required", [])) != expected_evidence_fields:
        fail("canonical evidence projection must require root identity and interpretive context from M17")
    if evidence_item.get("additionalProperties") is not False:
        fail("canonical evidence projection must reject undeclared fields")
    concrete_ref = (
        evidence_item.get("properties", {})
        .get("concrete_contacts", {})
        .get("$ref")
    )
    if concrete_ref != "independent-roots.schema.json#/properties/roots/items/properties/concrete_contacts":
        fail("canonical evidence concrete_contacts must reuse the M17 root contract")
    root_item = (
        independent_roots_schema.get("properties", {})
        .get("roots", {})
        .get("items", {})
    )
    if "concrete_contacts" not in set(root_item.get("required", [])):
        fail("M17 independent roots must require concrete_contacts")
    concrete_item = (
        root_item.get("properties", {})
        .get("concrete_contacts", {})
        .get("items", {})
    )
    required_concrete_fields = {
        "evidence_id",
        "source_module",
        "dependency_family",
        "directional",
        "subject_a",
        "point_a",
        "subject_b",
        "point_b",
        "relation_id",
        "layer_a",
        "layer_b",
        "exactness",
    }
    if set(concrete_item.get("required", [])) != required_concrete_fields:
        fail("M17 concrete contact trace fields changed")
    if concrete_item.get("additionalProperties") is not False:
        fail("M17 concrete contacts must reject undeclared fields")

    if evidence_item.get("properties", {}).get("source_module", {}).get("const") != "M17":
        fail("canonical evidence must remain rooted in M17")

    counter_item = canonical_schema.get("$defs", {}).get("counterevidence_item", {})
    expected_counter_fields = {
        "id",
        "model",
        "kind",
        "contradiction_key",
        "dependency_family",
        "essential",
        "severity",
        "evidence_refs",
        "note",
    }
    if set(counter_item.get("properties", {})) != expected_counter_fields:
        fail("canonical counterevidence item surface changed")
    if set(counter_item.get("required", [])) != expected_counter_fields:
        fail("canonical counterevidence item must require all M20 projection fields")
    if counter_item.get("additionalProperties") is not False:
        fail("canonical counterevidence items must reject undeclared fields")
    if canonical_props.get("counterevidence", {}).get("items", {}).get("$ref") != "#/$defs/counterevidence_item":
        fail("canonical counterevidence must use the normalized M20 item contract")

    counter_state_schema = canonical_props.get("counterevidence_state", {})
    if counter_state_schema.get("additionalProperties") is not False:
        fail("canonical counterevidence_state must reject undeclared fields")
    if set(counter_state_schema.get("required", [])) != {
        "ice_evaluable",
        "ice_by_model",
        "essential_contradictions",
    }:
        fail("canonical counterevidence_state required fields changed")

    assembly_schema = canonical_props.get("assembly", {})
    if assembly_schema.get("additionalProperties") is not False:
        fail("canonical assembly metadata must reject undeclared fields")
    assembly_props = assembly_schema.get("properties", {})
    if assembly_props.get("policy_id", {}).get("const") != "ALMAS_CANONICAL_ASSEMBLY_V2":
        fail("canonical assembly policy id changed")
    if assembly_props.get("source", {}).get("const") != "M01_M29_CANONICAL_NAMESPACES":
        fail("canonical assembly source changed")
    for field in (
        "recalculated_astrology",
        "recalculated_roots",
        "recalculated_pillars",
    ):
        if assembly_props.get(field, {}).get("const") is not False:
            fail(f"canonical assembly must lock {field}=false")

    robustness_schema = canonical_props.get("robustness", {})
    expected_robustness_fields = {
        "IRC",
        "R_min",
        "component_count",
        "components",
        "null_model_rarity_used_as_robustness",
        "timed_architecture_present",
        "birth_time_component_present",
    }
    if set(robustness_schema.get("properties", {})) != expected_robustness_fields:
        fail("canonical robustness surface changed")
    if set(robustness_schema.get("required", [])) != expected_robustness_fields:
        fail("canonical robustness must require all M30 fields")
    if robustness_schema.get("additionalProperties") is not False:
        fail("canonical robustness must reject undeclared fields")
    component_ref = (
        robustness_schema.get("properties", {})
        .get("components", {})
        .get("items", {})
        .get("$ref")
    )
    if component_ref != "robustness-output.schema.json#/properties/components/items":
        fail("canonical robustness components must reuse M25 component contract")
    if (
        robustness_schema.get("properties", {})
        .get("null_model_rarity_used_as_robustness", {})
        .get("const")
        is not False
    ):
        fail("canonical robustness must forbid null rarity as robustness")

    if canonical_props.get("profile_policy_id", {}).get("const") != "ALMAS_ANALYSIS_PROFILES_V1":
        fail("canonical profile policy id changed")
    profile_schema = assembly_props.get("analysis_profile", {})
    expected_profile_fields = {
        "profile_id",
        "analysis_mode",
        "required_modules",
        "optional_modules",
        "excluded_modules",
        "policy_id",
        "policy_status",
        "epistemic_class",
    }
    if set(profile_schema.get("properties", {})) != expected_profile_fields:
        fail("canonical embedded analysis profile surface changed")
    if set(profile_schema.get("required", [])) != expected_profile_fields:
        fail("canonical embedded analysis profile must require all trace fields")
    if profile_schema.get("additionalProperties") is not False:
        fail("canonical embedded analysis profile must reject undeclared fields")
    profile_props = profile_schema.get("properties", {})
    if profile_props.get("policy_id", {}).get("const") != "ALMAS_ANALYSIS_PROFILES_V1":
        fail("canonical embedded analysis profile policy changed")
    if profile_props.get("policy_status", {}).get("const") != "FROZEN_EXPERIMENTAL_BASELINE":
        fail("canonical embedded analysis profile status changed")
    if profile_props.get("epistemic_class", {}).get("const") != "E_PROJECT_POLICY":
        fail("canonical embedded analysis profile epistemic class changed")

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

    model_result_schema = canonical_schema.get("$defs", {}).get("model_result", {})
    if model_result_schema.get("additionalProperties") is not False:
        fail("canonical model_result must reject undeclared fields")
    expected_model_fields = {
        "iem",
        "state",
        "core",
        "support",
        "iem_pre",
        "iem_final",
        "ice",
        "ice_state",
        "supported_gate",
        "birth_time_gate_required",
        "birth_time_gate_satisfied",
    }
    if set(model_result_schema.get("required", [])) != expected_model_fields:
        fail("canonical model_result required field set changed")
    if canonical_schema.get("properties", {}).get("models", {}).get("additionalProperties") is not False:
        fail("canonical models wrapper must reject unknown model ids")

    indices_schema = canonical_schema.get("properties", {}).get("indices", {})
    expected_indices = {"IDD", "IAT", "ICC", "IRC", "ICE"}
    if set(indices_schema.get("properties", {})) != expected_indices:
        fail("canonical indices surface changed")
    if set(indices_schema.get("required", [])) != expected_indices:
        fail("canonical indices must require IDD/IAT/ICC/IRC/ICE")
    if indices_schema.get("additionalProperties") is not False:
        fail("canonical indices must reject undeclared indices")

    coverage_schema = canonical_schema.get("properties", {}).get("coverage", {})
    if coverage_schema.get("additionalProperties") is not False:
        fail("canonical coverage must reject undeclared fields")
    if set(coverage_schema.get("required", [])) != {
        "ICC",
        "domains",
        "formula",
        "policy_id",
    }:
        fail("canonical coverage required fields changed")
    if coverage_schema.get("properties", {}).get("formula", {}).get("const") != "100*sum(q_domain)/7":
        fail("canonical coverage formula changed")
    if coverage_schema.get("properties", {}).get("policy_id", {}).get("const") != "ALMAS_CANONICAL_ASSEMBLY_V2":
        fail("canonical coverage policy id changed")
    coverage_domains_schema = coverage_schema.get("properties", {}).get("domains", {})
    expected_coverage_domains = {
        "BASE_NATAL",
        "SYNASTRY_NODES",
        "ANGLES_HOUSES",
        "SYMMETRIES",
        "RELATIONSHIP_CHARTS",
        "DRACONIC",
        "LOTS_SECONDARY",
    }
    if set(coverage_domains_schema.get("properties", {})) != expected_coverage_domains:
        fail("canonical coverage domain set changed")
    if set(coverage_domains_schema.get("required", [])) != expected_coverage_domains:
        fail("canonical coverage must require all seven domains")
    if coverage_domains_schema.get("additionalProperties") is not False:
        fail("canonical coverage domains must reject unknown domains")
    for domain_id, domain_schema in coverage_domains_schema.get("properties", {}).items():
        if domain_schema.get("additionalProperties") is not False:
            fail(f"canonical coverage domain must reject extra fields: {domain_id}")
        if domain_schema.get("required") != ["q"]:
            fail(f"canonical coverage domain must require q: {domain_id}")
        if set(domain_schema.get("properties", {}).get("q", {}).get("enum", [])) != {0, 0.5, 1}:
            fail(f"canonical coverage q contract changed: {domain_id}")

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
