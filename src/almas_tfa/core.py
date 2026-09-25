from __future__ import annotations

from dataclasses import dataclass
from math import exp, log2, prod, sqrt
from typing import Iterable, Mapping, Sequence

MODEL_PILLARS = {
    "AF": {"core": ("PA", "PR"), "support": ("PE", "PX")},
    "KA": {"core": ("PK", "PT"), "support": ("PX", "PR", "PE")},
    "AG": {"core": ("PA", "PE", "PR", "PX"), "support": ("PK", "PT", "PS")},
    "LG": {"core": ("PA", "PE", "PR", "PX", "PT"), "support": ("PK", "PS", "PU")},
}

SUPPORTED_THRESHOLDS = {
    "iem_final": 75.0,
    "core": 0.65,
    "icc": 80.0,
    "irc": 70.0,
    "r_min": 0.50,
}


def _check_unit(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} debe estar en [0, 1]; valor recibido: {value}")
    return value


def _check_percent(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 100.0:
        raise ValueError(f"{name} debe estar en [0, 100]; valor recibido: {value}")
    return value


def geometric_mean(values: Iterable[float]) -> float:
    vals = [float(v) for v in values]
    if not vals:
        raise ValueError("geometric_mean requiere al menos un valor")
    if any(v < 0 for v in vals):
        raise ValueError("geometric_mean no admite valores negativos")
    if any(v == 0 for v in vals):
        return 0.0
    return prod(vals) ** (1.0 / len(vals))


def pillar_score(root_strengths: Sequence[float]) -> float:
    """Devuelve una puntuación de pilar 0–100 usando hasta las tres raíces independientes más fuertes."""
    roots = sorted(
        (_check_unit(v, "fuerza de raíz") for v in root_strengths),
        reverse=True,
    )[:3]
    if not roots:
        return 0.0
    weights = (1.0, 0.5, 1.0 / 3.0)
    numerator = sum(v * weights[i] for i, v in enumerate(roots))
    denominator = sum(weights)
    return 100.0 * numerator / denominator


@dataclass(frozen=True)
class ModelScore:
    model: str
    core: float
    support: float | None
    iem_pre: float
    ice: float
    iem_final: float
    essential_evaluable: bool


def score_model(
    model: str,
    pillar_scores: Mapping[str, float | None],
    *,
    ice: float = 0.0,
) -> ModelScore:
    """Calcula IEM a partir de puntuaciones de pilares ya derivadas.

    Las entradas de pilares son porcentajes en [0,100]. None significa NOT_EVALUABLE.
    Los pilares esenciales ausentes nunca se convierten en evidencia cero.
    """
    model = model.upper()
    if model not in MODEL_PILLARS:
        raise ValueError(f"modelo desconocido: {model}")

    spec = MODEL_PILLARS[model]
    essential_values = []
    essential_evaluable = True

    for pillar in spec["core"]:
        value = pillar_scores.get(pillar)
        if value is None:
            essential_evaluable = False
            continue
        essential_values.append(_check_percent(value, pillar) / 100.0)

    if not essential_evaluable or len(essential_values) != len(spec["core"]):
        core = 0.0 if not essential_values else geometric_mean(essential_values)
        return ModelScore(
            model=model,
            core=core,
            support=None,
            iem_pre=0.0,
            ice=_check_percent(ice, "ICE"),
            iem_final=0.0,
            essential_evaluable=False,
        )

    core = geometric_mean(essential_values)

    support_values = []
    for pillar in spec["support"]:
        value = pillar_scores.get(pillar)
        if value is not None:
            support_values.append(_check_percent(value, pillar) / 100.0)

    if support_values:
        support = sum(support_values) / len(support_values)
        multiplier = 0.90 + 0.10 * support
    else:
        support = None
        # Regla pública v1.0.0: sin apoyo evaluable se usa un multiplicador neutro.
        # La ausencia de datos se representa aparte mediante cobertura/evaluabilidad.
        multiplier = 1.0

    iem_pre = 100.0 * core * multiplier
    ice_value = _check_percent(ice, "ICE")
    iem_final = iem_pre * (1.0 - 0.30 * ice_value / 100.0)

    return ModelScore(
        model=model,
        core=core,
        support=support,
        iem_pre=iem_pre,
        ice=ice_value,
        iem_final=iem_final,
        essential_evaluable=True,
    )


def supported_gate(
    score: ModelScore,
    *,
    icc: float,
    irc: float,
    r_min: float,
    essential_contradiction: bool = False,
) -> bool:
    """Devuelve si se satisface el gate público congelado SUPPORT."""
    if not score.essential_evaluable or essential_contradiction:
        return False

    return (
        score.iem_final >= SUPPORTED_THRESHOLDS["iem_final"]
        and score.core >= SUPPORTED_THRESHOLDS["core"]
        and _check_percent(icc, "ICC") >= SUPPORTED_THRESHOLDS["icc"]
        and _check_percent(irc, "IRC") >= SUPPORTED_THRESHOLDS["irc"]
        and _check_unit(r_min, "R_min") >= SUPPORTED_THRESHOLDS["r_min"]
    )


def normalize_contributions(values: Mapping[str, float]) -> dict[str, float]:
    cleaned: dict[str, float] = {}
    for key, value in values.items():
        value = float(value)
        if value < 0:
            raise ValueError("las contribuciones deben ser no negativas")
        if value > 0:
            cleaned[str(key)] = value

    total = sum(cleaned.values())
    if total <= 0:
        return {}

    return {k: v / total for k, v in cleaned.items()}


def _kl_base2(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    total = 0.0
    for key, pv in p.items():
        if pv <= 0:
            continue
        qv = q.get(key, 0.0)
        if qv <= 0:
            raise ValueError("la distribución de referencia KL tiene soporte cero")
        total += pv * log2(pv / qv)
    return total


def diagnostic_discrimination(
    model_a: Mapping[str, float],
    model_b: Mapping[str, float],
) -> float | None:
    """Calcula IDD = 100 * sqrt(JSD_base2) sobre atribuciones normalizadas de raíces."""
    p = normalize_contributions(model_a)
    q = normalize_contributions(model_b)

    if not p or not q:
        return None

    keys = set(p) | set(q)
    m = {
        key: 0.5 * p.get(key, 0.0) + 0.5 * q.get(key, 0.0)
        for key in keys
    }
    jsd = 0.5 * _kl_base2(p, m) + 0.5 * _kl_base2(q, m)
    jsd = min(1.0, max(0.0, jsd))
    return 100.0 * sqrt(jsd)


def idd_band(idd: float | None) -> str:
    if idd is None:
        return "NOT_EVALUABLE"

    value = _check_percent(idd, "IDD")
    if value < 15:
        return "OVERLAP"
    if value < 30:
        return "TRANSITION"
    if value < 50:
        return "MATERIAL"
    return "VERY_MARKED"


def robustness_component(delta90: float, preserved_fraction: float) -> float:
    """Calcula un componente de robustez R_X en el intervalo 0–1."""
    delta90 = float(delta90)
    if delta90 < 0:
        raise ValueError("delta90 debe ser no negativo")

    g = _check_unit(preserved_fraction, "fracción preservada")
    return exp(-delta90 / 20.0) * sqrt(g)


def robustness_index(components: Sequence[float]) -> tuple[float, float]:
    """Devuelve (IRC porcentual, R_min) a partir de componentes 0–1 aplicables."""
    vals = [_check_unit(v, "componente de robustez") for v in components]
    if not vals:
        raise ValueError("se requiere al menos un componente de robustez")

    return 100.0 * geometric_mean(vals), min(vals)
