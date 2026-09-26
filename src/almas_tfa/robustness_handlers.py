"""Compatibilidad histórica para imports de robustez ALMAS.

Las implementaciones canónicas viven en módulos especializados:
- M23: time_sensitivity_handlers.py
- M24: null_model_handlers.py
- M25: robustness_index_handlers.py
"""

from .null_model_handlers import m24_null_models, make_m24_null_models, wilson_interval
from .robustness_index_handlers import m25_robustness, make_m25_robustness
from .time_sensitivity_handlers import m23_time_sensitivity

__all__ = [
    "m23_time_sensitivity",
    "m24_null_models",
    "make_m24_null_models",
    "m25_robustness",
    "make_m25_robustness",
    "wilson_interval",
]
