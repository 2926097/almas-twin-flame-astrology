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
from .handlers import default_handlers
from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleHandler,
    ModuleResult,
)
from .relational_handlers import m03_synastry, m04_nodes_angles_houses_regencies
from .symmetry_handlers import antiscion_longitude, contra_antiscion_longitude, m05_declinations, m06_antiscia
from .relationship_chart_handlers import DavisonBackend, DavisonRequest, circular_midpoint, m07_composite, make_m08_davison
from .draconic_handlers import m10_individual_draconics, m11_natal_draconic_cross, m12_draconic_draconic
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
    "m10_individual_draconics",
    "m11_natal_draconic_cross",
    "m12_draconic_draconic",
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
