from __future__ import annotations

from math import isfinite
from numbers import Real
from typing import Any, Mapping


MODELS = ("AF", "KA", "AG", "LG")


def validate_ice_by_model(
    value: Any,
    *,
    field_name: str = "ice_by_model",
) -> dict[str, float] | None:
    """Valida ICE precomputado con semántica fail-closed.

    None significa que ICE no fue calculado. Si el mapa se declara, debe
    contener exactamente AF/KA/AG/LG, sin extras, con valores numéricos finitos
    en [0, 100]. La ausencia de un modelo nunca se convierte implícitamente en 0.
    """

    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} debe ser un objeto.")

    unknown = [key for key in value if key not in MODELS]
    if unknown:
        rendered = ", ".join(sorted((str(key) for key in unknown)))
        raise ValueError(
            f"{field_name} contiene modelos desconocidos: {rendered}."
        )

    missing = [model for model in MODELS if model not in value]
    if missing:
        raise ValueError(
            f"{field_name} incompleto; faltan modelos: {', '.join(missing)}."
        )

    output: dict[str, float] = {}
    for model in MODELS:
        raw = value[model]
        if isinstance(raw, bool) or not isinstance(raw, Real):
            raise ValueError(f"{field_name}.{model} debe ser numérico.")
        score = float(raw)
        if not isfinite(score) or not 0.0 <= score <= 100.0:
            raise ValueError(
                f"{field_name}.{model} debe estar en [0,100]."
            )
        output[model] = score

    return output
