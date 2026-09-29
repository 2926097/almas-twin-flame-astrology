"""Contenedor canónico de fases, sin motor de inferencia (Paso 2)."""

from __future__ import annotations

from typing import Any


def empty_dynamic_phase_state() -> dict[str, Any]:
    """Inicializa tres ámbitos independientes sin atribuir fase alguna.

    La taxonomía y los criterios de atribución se definirán en pasos posteriores.
    Ningún índice, tránsito ni etiqueta doctrinal se usa aquí como evidencia.
    """
    return {
        "model_id": "ALMAS_DYNAMIC_PHASE_STATE_V1",
        "relational_phase": {"phase": None, "status": "NOT_EVALUABLE"},
        "actor_a_phase": {"phase": None, "status": "NOT_EVALUABLE"},
        "actor_b_phase": {"phase": None, "status": "NOT_EVALUABLE"},
    }
