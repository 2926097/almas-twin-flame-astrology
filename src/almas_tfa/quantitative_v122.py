from __future__ import annotations

from dataclasses import dataclass
from math import prod
from numbers import Real
from typing import Any, Mapping, Sequence

from .core import MODEL_PILLARS, diagnostic_discrimination, geometric_mean
from .quantitative_contracts import MODELS


@dataclass(frozen=True)
class DependencyAwareModelScore:
    model: str
    core: float
    support: float | None
    iem_pre: float
    ice: float
    iem_final: float
    essential_evaluable: bool
    core_weights: Mapping[str, float]
    support_weights: Mapping[str, float]


def _percent(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} debe ser numérico.")
    value = float(value)
    if not 0.0 <= value <= 100.0:
        raise ValueError(f"{name} debe estar en [0,100].")
    return value


def _unit(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} debe ser numérico.")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} debe estar en [0,1].")
    return value


def source_overlap(left: Sequence[str], right: Sequence[str]) -> float:
    """Coeficiente de solapamiento de procedencia entre dos dimensiones.

    Usa |A∩B|/min(|A|,|B|). Si alguna procedencia está vacía, no se presume
    dependencia. La ausencia de procedencia para un pilar positivo se bloquea
    antes de llegar a esta función.
    """

    a = {str(value) for value in left if str(value)}
    b = {str(value) for value in right if str(value)}
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def derive_pillar_source_roots(
    attribution_units: Sequence[Mapping[str, Any]],
) -> dict[str, list[str]]:
    """Reconstruye procedencia raíz→pilar sin convertir motivos en raíces nuevas."""

    output: dict[str, set[str]] = {
        pillar: set() for pillar in ("PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU")
    }
    for item in attribution_units:
        if not isinstance(item, Mapping) or not item.get("eligible"):
            continue
        contributions = item.get("contributions")
        if not isinstance(contributions, Mapping):
            continue

        unit_type = str(item.get("unit_type") or "ROOT")
        if unit_type == "SEMANTIC_MOTIF":
            raw_sources = item.get("source_root_ids")
            sources = (
                {str(value) for value in raw_sources if str(value)}
                if isinstance(raw_sources, list)
                else set()
            )
        else:
            root_id = str(item.get("root_id") or item.get("unit_id") or "")
            sources = {root_id} if root_id else set()

        for pillar, raw_value in contributions.items():
            pillar = str(pillar)
            if pillar not in output:
                continue
            if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
                continue
            if float(raw_value) > 0.0:
                output[pillar].update(sources)

    return {pillar: sorted(values) for pillar, values in output.items()}


def _validate_lineage(
    pillar_scores: Mapping[str, float | None],
    pillar_sources: Mapping[str, Sequence[str]],
    pillars: Sequence[str],
) -> None:
    for pillar in pillars:
        value = pillar_scores.get(pillar)
        if value is None:
            continue
        numeric = _percent(value, pillar)
        sources = pillar_sources.get(pillar, ())
        if numeric > 0.0 and not any(str(source) for source in sources):
            raise ValueError(
                f"{pillar}: pilar positivo sin procedencia de raíces; "
                "la corrección de dependencia 1.22 no es evaluable."
            )


def _dependency_weights(
    pillars: Sequence[str],
    pillar_sources: Mapping[str, Sequence[str]],
) -> dict[str, float]:
    output: dict[str, float] = {}
    for pillar in pillars:
        redundancy = sum(
            source_overlap(
                pillar_sources.get(pillar, ()),
                pillar_sources.get(other, ()),
            )
            for other in pillars
            if other != pillar
        )
        output[pillar] = 1.0 / (1.0 + redundancy)
    return output


def _weighted_geometric(
    values: Mapping[str, float],
    weights: Mapping[str, float],
) -> float:
    active = [(values[key], weights[key]) for key in values if weights.get(key, 0.0) > 0.0]
    if not active:
        raise ValueError("No existen dimensiones activas para la media geométrica.")
    if any(value == 0.0 for value, _ in active):
        return 0.0
    total_weight = sum(weight for _, weight in active)
    return prod(value ** weight for value, weight in active) ** (1.0 / total_weight)


def score_model_dependency_aware(
    model: str,
    pillar_scores: Mapping[str, float | None],
    pillar_sources: Mapping[str, Sequence[str]],
    *,
    ice: float = 0.0,
) -> DependencyAwareModelScore:
    """IEM 1.22: corrige dependencia entre pilares mediante procedencia raíz.

    Los pilares siguen siendo los mismos. Lo que cambia es su agregación:
    dimensiones que reutilizan las mismas raíces reciben menor masa efectiva.
    PX/PS conservan significado estructural, pero no cuentan como evidencia
    independiente adicional cuando proceden de las mismas raíces.
    """

    model = model.upper()
    if model not in MODEL_PILLARS:
        raise ValueError(f"modelo desconocido: {model}")

    spec = MODEL_PILLARS[model]
    core_pillars = tuple(spec["core"])
    support_pillars = tuple(spec["support"])
    _validate_lineage(
        pillar_scores,
        pillar_sources,
        tuple(dict.fromkeys(core_pillars + support_pillars)),
    )

    essential_evaluable = all(
        pillar_scores.get(pillar) is not None for pillar in core_pillars
    )
    ice_value = _percent(ice, "ICE")

    if not essential_evaluable:
        available = {
            pillar: _percent(pillar_scores[pillar], pillar) / 100.0
            for pillar in core_pillars
            if pillar_scores.get(pillar) is not None
        }
        core_weights = _dependency_weights(tuple(available), pillar_sources)
        core = (
            _weighted_geometric(available, core_weights)
            if available
            else 0.0
        )
        return DependencyAwareModelScore(
            model=model,
            core=core,
            support=None,
            iem_pre=0.0,
            ice=ice_value,
            iem_final=0.0,
            essential_evaluable=False,
            core_weights=core_weights,
            support_weights={},
        )

    core_values = {
        pillar: _percent(pillar_scores[pillar], pillar) / 100.0
        for pillar in core_pillars
    }
    core_weights = _dependency_weights(core_pillars, pillar_sources)
    core = _weighted_geometric(core_values, core_weights)

    support_values = {
        pillar: _percent(pillar_scores[pillar], pillar) / 100.0
        for pillar in support_pillars
        if pillar_scores.get(pillar) is not None
    }
    support_weights: dict[str, float] = {}
    for pillar in support_values:
        internal_redundancy = sum(
            source_overlap(
                pillar_sources.get(pillar, ()),
                pillar_sources.get(other, ()),
            )
            for other in support_values
            if other != pillar
        )
        core_overlap = max(
            (
                source_overlap(
                    pillar_sources.get(pillar, ()),
                    pillar_sources.get(core_pillar, ()),
                )
                for core_pillar in core_pillars
            ),
            default=0.0,
        )
        support_weights[pillar] = (
            (1.0 - core_overlap) / (1.0 + internal_redundancy)
        )

    active_support = {
        pillar: value
        for pillar, value in support_values.items()
        if support_weights.get(pillar, 0.0) > 0.0
    }
    if active_support:
        denominator = sum(support_weights[pillar] for pillar in active_support)
        support = sum(
            active_support[pillar] * support_weights[pillar]
            for pillar in active_support
        ) / denominator
        multiplier = 0.90 + 0.10 * support
    else:
        support = None
        multiplier = 1.0

    iem_pre = 100.0 * core * multiplier
    iem_final = iem_pre * (1.0 - 0.30 * ice_value / 100.0)

    return DependencyAwareModelScore(
        model=model,
        core=core,
        support=support,
        iem_pre=iem_pre,
        ice=ice_value,
        iem_final=iem_final,
        essential_evaluable=True,
        core_weights=core_weights,
        support_weights=support_weights,
    )


def robustness_dependency_family(component: Mapping[str, Any]) -> str:
    explicit = component.get("dependency_family")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()

    kind = str(component.get("kind") or "")
    if kind == "BIRTH_TIME":
        return "BIRTH_TIME"
    if kind == "ABLATION":
        return "ABLATION"
    if kind in {"PARAMETER_PERTURBATION", "IDD_STABILITY"}:
        return "PARAMETER_ENSEMBLE"
    if kind == "VALIDATED_DISCRIMINATOR":
        return "VALIDATED_DISCRIMINATOR:" + str(component.get("id") or "UNKNOWN")
    return "UNCLASSIFIED:" + kind


def grouped_robustness_index(
    components: Sequence[Mapping[str, Any]],
) -> tuple[float, float, list[dict[str, Any]]]:
    """IRC 1.22: agrupa componentes correlacionados antes de agregarlos."""

    if not components:
        raise ValueError("se requiere al menos un componente de robustez")

    grouped: dict[str, list[tuple[str, float]]] = {}
    raw_values: list[float] = []
    for index, component in enumerate(components, start=1):
        if not isinstance(component, Mapping):
            raise ValueError(f"componente {index}: debe ser un objeto")
        value = _unit(component.get("value"), f"componente {index}.value")
        raw_values.append(value)
        family = robustness_dependency_family(component)
        grouped.setdefault(family, []).append(
            (str(component.get("id") or f"C{index}"), value)
        )

    families: list[dict[str, Any]] = []
    family_scores: list[float] = []
    for family in sorted(grouped):
        members = grouped[family]
        score = geometric_mean([value for _, value in members])
        family_scores.append(score)
        families.append(
            {
                "dependency_family": family,
                "member_ids": [member_id for member_id, _ in members],
                "member_count": len(members),
                "family_score": score,
            }
        )

    return (
        100.0 * geometric_mean(family_scores),
        min(raw_values),
        families,
    )


def derive_autonomous_ice(
    retained_by_model: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[dict[str, float], dict[str, list[dict[str, Any]]]]:
    """ICE 1.22 desde contraevidencia explícita ya deduplicada.

    Dentro de una familia de dependencia conserva la severidad máxima. Entre
    familias declaradas independientes usa suma probabilística saturante:
    1 - Π(1-s_f). Es una agregación de severidad, no una probabilidad metafísica.
    """

    ice_by_model: dict[str, float] = {}
    diagnostics: dict[str, list[dict[str, Any]]] = {}

    for model in MODELS:
        items = retained_by_model.get(model, ())
        families: dict[str, float] = {}
        for index, item in enumerate(items, start=1):
            if not isinstance(item, Mapping):
                raise ValueError(f"{model}: contraevidencia {index} inválida.")
            family = item.get("dependency_family")
            if not isinstance(family, str) or not family:
                raise ValueError(
                    f"{model}: contraevidencia {index} sin dependency_family."
                )
            severity = item.get("severity")
            if severity is None:
                raise ValueError(
                    f"{model}: contraevidencia {index} sin severity; "
                    "ICE autónomo no es evaluable."
                )
            value = _unit(severity, f"{model}.counterevidence[{index}].severity")
            families[family] = max(families.get(family, 0.0), value)

        family_rows = [
            {"dependency_family": family, "severity": families[family]}
            for family in sorted(families)
        ]
        combined = 1.0 - prod(
            1.0 - row["severity"] for row in family_rows
        )
        ice_by_model[model] = 100.0 * combined
        diagnostics[model] = family_rows

    return ice_by_model, diagnostics


def signed_contribution_channels(
    values: Mapping[str, float],
) -> dict[str, float]:
    """Convierte una atribución Shapley firmada en masa no negativa para IDD."""

    channels: dict[str, float] = {}
    for raw_key, raw_value in values.items():
        if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
            raise ValueError("Las atribuciones firmadas deben ser numéricas.")
        value = float(raw_value)
        if value > 0.0:
            channels[f"{raw_key}::POS"] = value
        elif value < 0.0:
            channels[f"{raw_key}::NEG"] = -value
    return channels


def diagnostic_discrimination_signed(
    model_a: Mapping[str, float],
    model_b: Mapping[str, float],
) -> float | None:
    """IDD 1.22 sobre canales de magnitud y signo de Shapley.

    La transformación POS/NEG conserva la dirección del efecto sin introducir
    probabilidades ni truncar a cero las contribuciones negativas.
    """

    return diagnostic_discrimination(
        signed_contribution_channels(model_a),
        signed_contribution_channels(model_b),
    )
