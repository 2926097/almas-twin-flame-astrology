from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence


DEFAULT_MODELS = (
    "SOULMATE_MODEL",
    "MONADIC_ORIGIN",
    "SPLIT_SOUL",
    "TWIN_FLAME_MODEL",
)

SHARED_ORIGIN_MODELS = frozenset(
    {
        "MONADIC_ORIGIN",
        "SPLIT_SOUL",
        "TWIN_FLAME_MODEL",
    }
)

VALIDATION_LEVELS = {
    "L1_DOCTRINAL": 1,
    "L2_EXPERIMENTAL": 2,
    "L3_VALIDATED": 3,
}

OBSERVATION_RESULTS = {
    "SEPARATES",
    "NO_SEPARATION",
    "NOT_EVALUABLE",
}

MODES = {
    "CONFIRMATORY",
    "EXPLORATORY",
}

PAIR_STATUSES = {
    "SEPARABLE_VALIDATED",
    "SEPARABLE_EXPERIMENTAL",
    "OBSERVATIONALLY_EQUIVALENT",
    "INSUFFICIENT_EVIDENCE",
    "NOT_EVALUABLE",
    "CONFLICTING_EVIDENCE",
}


@dataclass(frozen=True)
class PairObservation:
    discriminator_id: str
    pair: tuple[str, str]
    validation_level: str
    result: str
    excluded_model: str | None = None
    root_key: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class _ReducedRoot:
    pair: tuple[str, str]
    root_key: str
    validation_level: str
    result: str
    excluded_model: str | None
    discriminator_ids: tuple[str, ...]
    conflict: bool


def _normalize_models(models: Sequence[str] | None) -> tuple[str, ...]:
    normalized = tuple(models or DEFAULT_MODELS)
    if len(normalized) < 2:
        raise ValueError("Se requieren al menos dos modelos candidatos.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("Los modelos candidatos deben ser únicos.")
    return normalized


def _canonical_pair(pair: Sequence[str], order: Mapping[str, int]) -> tuple[str, str]:
    if len(pair) != 2:
        raise ValueError("Cada observación debe contener exactamente dos modelos.")
    a, b = pair
    if a == b:
        raise ValueError("Una observación no puede comparar un modelo consigo mismo.")
    if a not in order or b not in order:
        raise ValueError(f"Par fuera del conjunto candidato: {a!r}, {b!r}.")
    return tuple(sorted((a, b), key=order.__getitem__))  # type: ignore[return-value]


def _normalize_observation(
    raw: PairObservation | Mapping[str, Any],
    order: Mapping[str, int],
) -> PairObservation:
    if isinstance(raw, PairObservation):
        obs = raw
    elif isinstance(raw, Mapping):
        pair_raw = raw.get("pair")
        if not isinstance(pair_raw, (list, tuple)):
            raise ValueError("pair debe ser una lista o tupla de dos modelos.")
        obs = PairObservation(
            discriminator_id=str(raw.get("discriminator_id") or "").strip(),
            pair=(str(pair_raw[0]), str(pair_raw[1])) if len(pair_raw) == 2 else tuple(pair_raw),  # type: ignore[arg-type]
            validation_level=str(raw.get("validation_level") or "").strip(),
            result=str(raw.get("result") or "").strip(),
            excluded_model=(
                str(raw.get("excluded_model"))
                if raw.get("excluded_model") is not None
                else None
            ),
            root_key=(
                str(raw.get("root_key"))
                if raw.get("root_key") is not None
                else None
            ),
            note=str(raw.get("note")) if raw.get("note") is not None else None,
        )
    else:
        raise TypeError("Cada observación debe ser PairObservation o Mapping.")

    if not obs.discriminator_id:
        raise ValueError("discriminator_id es obligatorio.")
    if obs.validation_level not in VALIDATION_LEVELS:
        raise ValueError(
            f"validation_level no reconocido: {obs.validation_level!r}."
        )
    if obs.result not in OBSERVATION_RESULTS:
        raise ValueError(f"result no reconocido: {obs.result!r}.")

    pair = _canonical_pair(obs.pair, order)

    excluded = obs.excluded_model
    if obs.result == "SEPARATES":
        if excluded is None:
            raise ValueError("SEPARATES requiere excluded_model.")
        if excluded not in pair:
            raise ValueError("excluded_model debe pertenecer al par comparado.")
    elif excluded is not None:
        raise ValueError(
            "excluded_model sólo puede declararse cuando result=SEPARATES."
        )

    return PairObservation(
        discriminator_id=obs.discriminator_id,
        pair=pair,
        validation_level=obs.validation_level,
        result=obs.result,
        excluded_model=excluded,
        root_key=obs.root_key or obs.discriminator_id,
        note=obs.note,
    )


def _reduce_root(observations: Sequence[PairObservation]) -> _ReducedRoot:
    if not observations:
        raise ValueError("No se puede reducir una raíz vacía.")

    max_rank = max(VALIDATION_LEVELS[o.validation_level] for o in observations)
    top = [
        o
        for o in observations
        if VALIDATION_LEVELS[o.validation_level] == max_rank
    ]
    level = top[0].validation_level
    pair = top[0].pair
    root_key = top[0].root_key or top[0].discriminator_id

    separating = [o for o in top if o.result == "SEPARATES"]
    non_separating = [o for o in top if o.result == "NO_SEPARATION"]

    excluded = {o.excluded_model for o in separating}
    conflict = len(excluded) > 1 or (bool(separating) and bool(non_separating))

    if conflict:
        result = "NOT_EVALUABLE"
        excluded_model = None
    elif separating:
        result = "SEPARATES"
        excluded_model = separating[0].excluded_model
    elif non_separating:
        result = "NO_SEPARATION"
        excluded_model = None
    else:
        result = "NOT_EVALUABLE"
        excluded_model = None

    return _ReducedRoot(
        pair=pair,
        root_key=root_key,
        validation_level=level,
        result=result,
        excluded_model=excluded_model,
        discriminator_ids=tuple(sorted({o.discriminator_id for o in top})),
        conflict=conflict,
    )


def _coverage_for_pair(
    pair: tuple[str, str],
    pair_coverage: Mapping[str, str] | None,
) -> str:
    if not pair_coverage:
        return "PARTIAL"
    key = f"{pair[0]}_vs_{pair[1]}"
    value = str(pair_coverage.get(key, "PARTIAL")).upper()
    if value not in {"COMPLETE", "PARTIAL", "NONE"}:
        raise ValueError(f"Cobertura no reconocida para {key}: {value!r}.")
    return value


def _pair_assessment(
    pair: tuple[str, str],
    roots: Sequence[_ReducedRoot],
    coverage: str,
) -> dict[str, Any]:
    conflicts = [
        {
            "root_key": root.root_key,
            "validation_level": root.validation_level,
            "discriminator_ids": list(root.discriminator_ids),
        }
        for root in roots
        if root.conflict
    ]

    l3 = [
        root
        for root in roots
        if root.validation_level == "L3_VALIDATED" and not root.conflict
    ]
    l2 = [
        root
        for root in roots
        if root.validation_level == "L2_EXPERIMENTAL" and not root.conflict
    ]

    l3_sep = [root for root in l3 if root.result == "SEPARATES"]
    l2_sep = [root for root in l2 if root.result == "SEPARATES"]

    l3_excluded = {root.excluded_model for root in l3_sep}
    l2_excluded = {root.excluded_model for root in l2_sep}

    if len(l3_excluded) > 1:
        confirmatory_status = "CONFLICTING_EVIDENCE"
        confirmed_excluded = None
        conflicts.append(
            {
                "root_key": "PAIR_LEVEL_L3",
                "validation_level": "L3_VALIDATED",
                "discriminator_ids": sorted(
                    d for root in l3_sep for d in root.discriminator_ids
                ),
            }
        )
    elif l3_sep:
        confirmatory_status = "SEPARABLE_VALIDATED"
        confirmed_excluded = next(iter(l3_excluded))
    elif coverage == "COMPLETE" and any(
        root.result == "NO_SEPARATION" for root in l3
    ):
        confirmatory_status = "OBSERVATIONALLY_EQUIVALENT"
        confirmed_excluded = None
    elif coverage == "NONE" and not roots:
        confirmatory_status = "NOT_EVALUABLE"
        confirmed_excluded = None
    else:
        confirmatory_status = "INSUFFICIENT_EVIDENCE"
        confirmed_excluded = None

    if confirmatory_status == "SEPARABLE_VALIDATED":
        exploratory_status = confirmatory_status
        exploratory_excluded = confirmed_excluded
    elif len(l2_excluded) > 1:
        exploratory_status = "CONFLICTING_EVIDENCE"
        exploratory_excluded = None
        conflicts.append(
            {
                "root_key": "PAIR_LEVEL_L2",
                "validation_level": "L2_EXPERIMENTAL",
                "discriminator_ids": sorted(
                    d for root in l2_sep for d in root.discriminator_ids
                ),
            }
        )
    elif l2_sep:
        exploratory_status = "SEPARABLE_EXPERIMENTAL"
        exploratory_excluded = next(iter(l2_excluded))
    elif confirmatory_status == "OBSERVATIONALLY_EQUIVALENT":
        exploratory_status = "OBSERVATIONALLY_EQUIVALENT"
        exploratory_excluded = None
    elif coverage == "NONE" and not roots:
        exploratory_status = "NOT_EVALUABLE"
        exploratory_excluded = None
    else:
        exploratory_status = "INSUFFICIENT_EVIDENCE"
        exploratory_excluded = None

    return {
        "pair": list(pair),
        "coverage": coverage,
        "confirmatory_status": confirmatory_status,
        "exploratory_status": exploratory_status,
        "confirmed_excluded_model": confirmed_excluded,
        "exploratory_excluded_model": exploratory_excluded,
        "validated_roots": [
            root.root_key
            for root in l3
            if root.result != "NOT_EVALUABLE"
        ],
        "experimental_roots": [
            root.root_key
            for root in l2
            if root.result != "NOT_EVALUABLE"
        ],
        "conflicts": conflicts,
    }


def _classification_for_survivors(survivors: Sequence[str]) -> str:
    if len(survivors) == 1:
        return survivors[0]
    survivor_set = set(survivors)
    if survivor_set and survivor_set.issubset(SHARED_ORIGIN_MODELS):
        return "SHARED_ORIGIN_UNDIFFERENTIATED"
    return "INDETERMINATE"


def _state_for_survivors(
    *,
    candidate_count: int,
    survivors: Sequence[str],
    minimum_data_evaluable: bool,
    conflicts: Sequence[Mapping[str, Any]],
) -> tuple[str, str]:
    if not minimum_data_evaluable:
        return "NOT_EVALUABLE", "NOT_EVALUABLE"
    if conflicts:
        return "NON_IDENTIFIABLE", "INSUFFICIENT"
    if len(survivors) == 1:
        return "IDENTIFIABLE", "COMPATIBLE"
    if len(survivors) < candidate_count:
        return "PARTIALLY_IDENTIFIABLE", "INSUFFICIENT"
    return "NON_IDENTIFIABLE", "INSUFFICIENT"


def discriminate_ontology(
    observations: Iterable[PairObservation | Mapping[str, Any]],
    *,
    models: Sequence[str] | None = None,
    mode: str = "CONFIRMATORY",
    minimum_data_evaluable: bool = True,
    pair_coverage: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Evalúa separabilidad de modelos sin convertir scores en ontología.

    La salida canónica siempre se basa únicamente en discriminadores L3_VALIDATED.
    En modo EXPLORATORY se añade una proyección separada que permite inspeccionar
    qué exclusiones sugerirían señales L2_EXPERIMENTAL sin promoverlas a decisión
    confirmatoria.
    """

    mode = mode.upper()
    if mode not in MODES:
        raise ValueError(f"Modo no reconocido: {mode!r}.")

    candidates = _normalize_models(models)
    order = {model: index for index, model in enumerate(candidates)}

    normalized = [
        _normalize_observation(raw, order)
        for raw in observations
    ]

    by_pair_root: dict[tuple[str, str], dict[str, list[PairObservation]]] = {}
    for obs in normalized:
        pair_bucket = by_pair_root.setdefault(obs.pair, {})
        pair_bucket.setdefault(obs.root_key or obs.discriminator_id, []).append(obs)

    reduced_by_pair: dict[tuple[str, str], list[_ReducedRoot]] = {}
    for pair, roots in by_pair_root.items():
        reduced_by_pair[pair] = [
            _reduce_root(group)
            for _, group in sorted(roots.items())
        ]

    pairwise_matrix: dict[str, dict[str, Any]] = {}
    global_conflicts: list[dict[str, Any]] = []

    for pair in combinations(candidates, 2):
        canonical = _canonical_pair(pair, order)
        assessment = _pair_assessment(
            canonical,
            reduced_by_pair.get(canonical, []),
            _coverage_for_pair(canonical, pair_coverage),
        )
        key = f"{canonical[0]}_vs_{canonical[1]}"
        pairwise_matrix[key] = assessment
        for conflict in assessment["conflicts"]:
            global_conflicts.append(
                {
                    "pair": list(canonical),
                    **conflict,
                }
            )

    confirmed_exclusions = {
        assessment["confirmed_excluded_model"]
        for assessment in pairwise_matrix.values()
        if assessment["confirmatory_status"] == "SEPARABLE_VALIDATED"
        and assessment["confirmed_excluded_model"] is not None
    }

    if confirmed_exclusions == set(candidates):
        global_conflicts.append(
            {
                "pair": [],
                "root_key": "GLOBAL_ELIMINATION_CYCLE",
                "validation_level": "L3_VALIDATED",
                "discriminator_ids": [],
            }
        )
        confirmed_exclusions = set()

    if not minimum_data_evaluable:
        confirmed_exclusions = set()

    surviving_models = [
        model for model in candidates if model not in confirmed_exclusions
    ]

    active_conflicts = [
        conflict
        for conflict in global_conflicts
        if not conflict.get("pair")
        or all(model in surviving_models for model in conflict["pair"])
    ]

    identifiability_state, epistemic_state = _state_for_survivors(
        candidate_count=len(candidates),
        survivors=surviving_models,
        minimum_data_evaluable=minimum_data_evaluable,
        conflicts=active_conflicts,
    )

    if not minimum_data_evaluable:
        classification = "INDETERMINATE"
        equivalence_classes: list[list[str]] = []
    else:
        classification = _classification_for_survivors(surviving_models)
        equivalence_classes = [list(surviving_models)] if surviving_models else []

    output: dict[str, Any] = {
        "schema_version": "1.0.0",
        "mode": mode,
        "candidate_models": list(candidates),
        "confirmed_exclusions": sorted(
            confirmed_exclusions,
            key=order.__getitem__,
        ),
        "surviving_models": surviving_models,
        "pairwise_matrix": pairwise_matrix,
        "equivalence_classes": equivalence_classes,
        "identifiability_state": identifiability_state,
        "epistemic_state": epistemic_state,
        "classification": classification,
        "conflicts": global_conflicts,
        "false_specificity_guard": (
            len(surviving_models) <= 1
            or classification in {
                "SHARED_ORIGIN_UNDIFFERENTIATED",
                "INDETERMINATE",
            }
        ),
        "rules": {
            "l2_can_confirm": False,
            "scores_can_break_equivalence": False,
            "absence_is_counterevidence_by_default": False,
        },
    }

    if mode == "EXPLORATORY":
        exploratory_exclusions = set(confirmed_exclusions)

        if minimum_data_evaluable:
            for assessment in pairwise_matrix.values():
                if (
                    assessment["exploratory_status"] == "SEPARABLE_EXPERIMENTAL"
                    and assessment["exploratory_excluded_model"] is not None
                ):
                    exploratory_exclusions.add(
                        assessment["exploratory_excluded_model"]
                    )

        if exploratory_exclusions == set(candidates):
            exploratory_survivors = list(surviving_models)
            exploratory_conflict = True
        else:
            exploratory_survivors = [
                model
                for model in candidates
                if model not in exploratory_exclusions
            ]
            exploratory_conflict = False

        output["exploratory_view"] = {
            "excluded_models": sorted(
                exploratory_exclusions,
                key=order.__getitem__,
            ),
            "surviving_models": exploratory_survivors,
            "classification": _classification_for_survivors(
                exploratory_survivors
            ),
            "experimental_only_exclusions": sorted(
                exploratory_exclusions - confirmed_exclusions,
                key=order.__getitem__,
            ),
            "conflict": exploratory_conflict,
            "canonical_decision_unchanged": True,
            "warning": (
                "La vista exploratoria no puede promoverse a clasificación "
                "confirmatoria sin discriminadores L3_VALIDATED."
            ),
        }

    return output
