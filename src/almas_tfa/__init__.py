"""Public ALMAS relational-astrology scoring core."""

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
]
