"""Compatibilidad histórica para las etapas finales M28-M31.

Las implementaciones canónicas viven en módulos especializados:
- M28: doctrine_handlers.py
- M29: reality_handlers.py
- M30: report_gate_handlers.py
- M31: report_model_handlers.py
"""

from .doctrine_handlers import m28_doctrine_hermeneutics
from .reality_handlers import m29_viability_reciprocity
from .report_gate_handlers import m30_report_gate, make_m30_report_gate_auto
from .report_model_handlers import m31_report

__all__ = [
    "m28_doctrine_hermeneutics",
    "m29_viability_reciprocity",
    "m30_report_gate",
    "make_m30_report_gate_auto",
    "m31_report",
]
