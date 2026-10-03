"""Núcleo público de scoring y orquestación modular de ALMAS."""

from .analysis import analyze_precomputed
from .astrology_backend import AstronomyBackendNotEvaluableError, AstrologyBackend, NatalRequest, natal_request_from_subject
from .astrology_handlers import make_m02_natal
from .astrology_geometry import angular_distance, house_for_longitude, match_declared_aspect, normalize_longitude, zodiac_sign
from .production_astronomy import MoiraBackendConfig, MoiraProductionBackend, load_production_astronomy_backend_policy
from .core import (
    MODEL_PILLARS,
    SUPPORTED_THRESHOLDS,
    ModelScore,
    diagnostic_discrimination,
    geometric_mean,
    idd_band,
    normalize_contributions,
    pillar_score,
    robustness_component,
    robustness_index,
    score_model,
    supported_gate,
)
from .handlers import configured_handlers, default_handlers
from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleHandler,
    ModuleResult,
)
from .relational_handlers import m03_synastry, m04_nodes_angles_houses_regencies
from .symmetry_handlers import antiscion_longitude, contra_antiscion_longitude, m05_declinations, m06_antiscia
from .relationship_chart_handlers import DavisonBackend, DavisonRequest, circular_midpoint, m07_composite, make_m08_davison
from .relationship_consonance import m09_relationship_chart_consonance
from .draconic_handlers import m10_individual_draconics, m11_natal_draconic_cross, m12_draconic_draconic
from .lot_handlers import m13_lots, load_default_lot_policy
from .secondary_handlers import m14_secondary_symbolic
from .evidence_handlers import m15_evidence_extraction, m16_dependency_deduplication, m17_independent_roots
from .root_strengths import derive_root_strength, evidence_strength, load_root_strength_policy
from .structural_policies import load_declared_orb_contract_policy, load_relational_orb_baseline_policy, load_structural_loading_policy, load_technique_dependency_registry, validate_declared_aspect_policy
from .pillar_attribution import classify_root, derive_pillars_from_roots, load_root_pillar_policy
from .semantic_motifs import classify_primary_motif, derive_semantic_motif_graph, load_semantic_motif_policy, mission_motifs
from .recurrence_quality import derive_recurrence_quality_diagnostics, load_recurrence_quality_policy
from .model_attribution import derive_model_attributions, load_model_attribution_policy
from .counterevidence_handlers import m20_counterevidence
from .ablation_handlers import ABLATION_RUNS, m22_ablation
from .time_sensitivity_handlers import m23_time_sensitivity, make_m23_time_sensitivity
from .time_perturbation import generate_birth_time_sensitivity, load_birth_time_perturbation_policy
from .null_model_handlers import ALLOWED_NULL_MODELS, m24_null_models, make_m24_null_models, wilson_interval
from .null_generation import generate_within_year_null_runs, load_null_generation_policy
from .null_calibration import derive_recurrence_null_calibration, load_recurrence_null_calibration_policy
from .synthetic_controls import derive_recurrence_synthetic_controls, load_recurrence_synthetic_controls_policy
from .external_control_cohorts import extract_clean_external_candidate_snapshots, extract_validated_external_snapshots, load_external_recurrence_cohort_policy, validate_external_recurrence_cohort
from .external_recurrence_calibration import derive_external_recurrence_calibration, load_external_recurrence_calibration_policy
from .px_v3_candidates import evaluate_px_v3_candidate, evaluate_px_v3_candidate_registry, load_px_v3_candidate_freeze_policy, load_px_v3_candidate_registry
from .px_v3_holdout import evaluate_px_v3_holdout, load_px_v3_holdout_evaluation_policy
from .px_v3_promotion import evaluate_px_v3_promotion, load_px_v3_promotion_gate_policy
from .px_v3_activation import evaluate_px_v3_activation_firewall, load_px_v3_activation_firewall_policy
from .validation_preregistration import build_validation_preregistration_bundle, load_validation_preregistration_bundle_policy
from .holdout_open import evaluate_holdout_open, load_holdout_open_gate_policy
from .validation_ledger import append_validation_event, audit_validation_ledger, initialize_validation_ledger, load_validation_execution_ledger_policy
from .validation_continuity import evaluate_px_v3_promotion_with_continuity, evaluate_validation_continuity, load_validation_continuity_gate_policy
from .validation_closure import build_documentary_reveal_record, close_validation_cycle, load_validation_closure_release_audit_policy, record_documentary_reveal
from .robustness_index_handlers import m25_robustness, make_m25_robustness
from .robustness_quantification import derive_q5_robustness_components, load_q5_robustness_policy
from .temporal_handlers import m26_temporal_activation, m27_dated_events
from .temporal_sequence_graph import build_temporal_sequence_graph
from .angular_robustness import evaluate_angular_robustness
from .doctrine_handlers import m28_doctrine_hermeneutics
from .reality_handlers import m29_viability_reciprocity
from .report_gate_handlers import m30_report_gate, make_m30_report_gate_auto
from .canonical_assembly import assemble_canonical_analysis, derive_canonical_coverage, load_canonical_assembly_policy
from .analysis_profiles import load_analysis_profile_policy, profile_trace_assessment, resolve_analysis_profile
from .report_model_handlers import m31_report
from .orchestrator import (
    CanonicalOverwriteError,
    OrchestrationRun,
    Orchestrator,
    PipelineDefinitionError,
    validate_pipeline_manifest,
)

__all__ = [
    "analyze_precomputed",
    "AstrologyBackend",
    "AstronomyBackendNotEvaluableError",
    "MoiraBackendConfig",
    "MoiraProductionBackend",
    "load_production_astronomy_backend_policy",
    "NatalRequest",
    "natal_request_from_subject",
    "make_m02_natal",
    "normalize_longitude",
    "angular_distance",
    "zodiac_sign",
    "match_declared_aspect",
    "house_for_longitude",
    "m03_synastry",
    "m04_nodes_angles_houses_regencies",
    "m05_declinations",
    "m06_antiscia",
    "antiscion_longitude",
    "contra_antiscion_longitude",
    "circular_midpoint",
    "m07_composite",
    "DavisonRequest",
    "DavisonBackend",
    "make_m08_davison",
    "m09_relationship_chart_consonance",
    "m10_individual_draconics",
    "m11_natal_draconic_cross",
    "m12_draconic_draconic",
    "m13_lots",
    "load_default_lot_policy",
    "m14_secondary_symbolic",
    "m15_evidence_extraction",
    "m16_dependency_deduplication",
    "m17_independent_roots",
    "load_root_strength_policy",
    "evidence_strength",
    "derive_root_strength",
    "load_technique_dependency_registry",
    "load_declared_orb_contract_policy",
    "load_relational_orb_baseline_policy",
    "load_structural_loading_policy",
    "validate_declared_aspect_policy",
    "load_root_pillar_policy",
    "classify_root",
    "derive_pillars_from_roots",
    "load_semantic_motif_policy",
    "classify_primary_motif",
    "mission_motifs",
    "derive_semantic_motif_graph",
    "load_recurrence_quality_policy",
    "derive_recurrence_quality_diagnostics",
    "load_model_attribution_policy",
    "derive_model_attributions",
    "m20_counterevidence",
    "ABLATION_RUNS",
    "m22_ablation",
    "m23_time_sensitivity",
    "make_m23_time_sensitivity",
    "load_birth_time_perturbation_policy",
    "generate_birth_time_sensitivity",
    "ALLOWED_NULL_MODELS",
    "m24_null_models",
    "make_m24_null_models",
    "load_null_generation_policy",
    "generate_within_year_null_runs",
    "load_recurrence_null_calibration_policy",
    "derive_recurrence_null_calibration",
    "load_recurrence_synthetic_controls_policy",
    "derive_recurrence_synthetic_controls",
    "load_external_recurrence_cohort_policy",
    "validate_external_recurrence_cohort",
    "extract_validated_external_snapshots",
    "extract_clean_external_candidate_snapshots",
    "load_external_recurrence_calibration_policy",
    "derive_external_recurrence_calibration",
    "load_px_v3_candidate_freeze_policy",
    "load_px_v3_candidate_registry",
    "evaluate_px_v3_candidate",
    "evaluate_px_v3_candidate_registry",
    "load_px_v3_holdout_evaluation_policy",
    "evaluate_px_v3_holdout",
    "load_px_v3_promotion_gate_policy",
    "evaluate_px_v3_promotion",
    "load_px_v3_activation_firewall_policy",
    "evaluate_px_v3_activation_firewall",
    "load_validation_preregistration_bundle_policy",
    "build_validation_preregistration_bundle",
    "load_holdout_open_gate_policy",
    "evaluate_holdout_open",
    "load_validation_execution_ledger_policy",
    "initialize_validation_ledger",
    "append_validation_event",
    "audit_validation_ledger",
    "load_validation_continuity_gate_policy",
    "evaluate_validation_continuity",
    "evaluate_px_v3_promotion_with_continuity",
    "load_validation_closure_release_audit_policy",
    "build_documentary_reveal_record",
    "record_documentary_reveal",
    "close_validation_cycle",
    "wilson_interval",
    "m25_robustness",
    "make_m25_robustness",
    "load_q5_robustness_policy",
    "derive_q5_robustness_components",
    "m26_temporal_activation",
    "m27_dated_events",
    "build_temporal_sequence_graph",
    "evaluate_angular_robustness",
    "m28_doctrine_hermeneutics",
    "m29_viability_reciprocity",
    "m30_report_gate",
    "make_m30_report_gate_auto",
    "load_canonical_assembly_policy",
    "derive_canonical_coverage",
    "assemble_canonical_analysis",
    "load_analysis_profile_policy",
    "resolve_analysis_profile",
    "profile_trace_assessment",
    "m31_report",
    "MODEL_PILLARS",
    "SUPPORTED_THRESHOLDS",
    "ModelScore",
    "diagnostic_discrimination",
    "geometric_mean",
    "idd_band",
    "normalize_contributions",
    "pillar_score",
    "robustness_component",
    "robustness_index",
    "score_model",
    "supported_gate",
    "default_handlers",
    "configured_handlers",
    "ExecutionStatus",
    "ModuleContext",
    "ModuleHandler",
    "ModuleResult",
    "CanonicalOverwriteError",
    "OrchestrationRun",
    "Orchestrator",
    "PipelineDefinitionError",
    "validate_pipeline_manifest",
]


from .work_request import (
    WorkRequestError,
    assess_work_request,
    build_raw_input_from_work_request,
)

__all__.extend([
    "WorkRequestError",
    "assess_work_request",
    "build_raw_input_from_work_request",
])
