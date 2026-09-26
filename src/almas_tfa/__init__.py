"""Núcleo público de scoring y orquestación modular de ALMAS."""

from .analysis import analyze_precomputed
from .astrology_backend import AstrologyBackend, NatalRequest, natal_request_from_subject
from .astrology_handlers import make_m02_natal
from .astrology_geometry import angular_distance, house_for_longitude, match_declared_aspect, normalize_longitude, zodiac_sign
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
from .lot_handlers import m13_lots
from .secondary_handlers import m14_secondary_symbolic
from .evidence_handlers import m15_evidence_extraction, m16_dependency_deduplication, m17_independent_roots
from .root_strengths import derive_root_strength, evidence_strength, load_root_strength_policy
from .counterevidence_handlers import m20_counterevidence
from .ablation_handlers import ABLATION_RUNS, m22_ablation
from .time_sensitivity_handlers import m23_time_sensitivity
from .null_model_handlers import ALLOWED_NULL_MODELS, m24_null_models, wilson_interval
from .robustness_index_handlers import m25_robustness
from .temporal_handlers import m26_temporal_activation, m27_dated_events
from .doctrine_handlers import m28_doctrine_hermeneutics
from .reality_handlers import m29_viability_reciprocity
from .report_gate_handlers import m30_report_gate
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
    "m14_secondary_symbolic",
    "m15_evidence_extraction",
    "m16_dependency_deduplication",
    "m17_independent_roots",
    "load_root_strength_policy",
    "evidence_strength",
    "derive_root_strength",
    "m20_counterevidence",
    "ABLATION_RUNS",
    "m22_ablation",
    "m23_time_sensitivity",
    "ALLOWED_NULL_MODELS",
    "m24_null_models",
    "wilson_interval",
    "m25_robustness",
    "m26_temporal_activation",
    "m27_dated_events",
    "m28_doctrine_hermeneutics",
    "m29_viability_reciprocity",
    "m30_report_gate",
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
