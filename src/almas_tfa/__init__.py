"""Núcleo público de scoring y orquestación modular de ALMAS."""

from .analysis import analyze_precomputed
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
from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleHandler,
    ModuleResult,
)
from .orchestrator import (
    CanonicalOverwriteError,
    OrchestrationRun,
    Orchestrator,
    PipelineDefinitionError,
    validate_pipeline_manifest,
)

__all__ = [
    "analyze_precomputed",
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
