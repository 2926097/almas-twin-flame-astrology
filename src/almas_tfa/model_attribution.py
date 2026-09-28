from __future__ import annotations

from itertools import combinations
from math import comb
import json
from importlib import resources
import random
from typing import Any, Mapping, Sequence

from .core import pillar_score, score_model
from .pillar_attribution import classify_root, load_root_pillar_policy
from .semantic_motifs import (
    load_semantic_motif_policy,
    semantic_root_signature,
)


POLICY_RESOURCE = "model-attribution-policy.json"
POLICY_PACKAGE = "almas_tfa"
MODELS = ("AF", "KA", "AG", "LG")


def load_model_attribution_policy() -> dict[str, Any]:
    """Carga la política congelada de atribución Shapley para M21."""

    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V3":
        raise ValueError("Política de atribución de modelos desconocida.")
    return policy


def _eligible_root_players(
    pillar_attribution: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Devuelve exclusivamente raíces independientes como jugadores Shapley.

    Los motivos PX/PS son funciones derivadas de coaliciones de raíces. No
    pueden entrar como jugadores separados porque eso contaría la misma
    arquitectura una segunda vez.
    """

    raw = pillar_attribution.get("source_roots")
    if not isinstance(raw, list):
        return []

    roots: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        if not bool(item.get("core_eligible")):
            continue
        if item.get("strength_state") != "CALCULATED_CORE":
            continue

        root_id = str(item.get("root_id") or "")
        if not root_id:
            raise ValueError("Toda raíz Shapley elegible requiere root_id.")
        if root_id in seen:
            raise ValueError(f"root_id duplicado en raíces fuente: {root_id}.")

        strength = item.get("strength")
        if (
            isinstance(strength, bool)
            or not isinstance(strength, (int, float))
        ):
            raise ValueError(f"{root_id}: strength debe ser numérico.")
        strength = float(strength)
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"{root_id}: strength debe estar en [0,1].")

        seen.add(root_id)
        roots.append(dict(item))

    roots.sort(key=lambda item: str(item["root_id"]))
    return roots


class _CoalitionValueEngine:
    """Función de valor IEM_pre con PX/PS recalculados por coalición.

    Las firmas invariantes por raíz se precalculan una sola vez. La evaluación
    de cada coalición reproduce exactamente las reglas de M18/PXv2 sin releer
    políticas ni reclasificar geometría miles de veces.
    """

    _DIRECT_PILLARS = ("PA", "PK", "PE", "PR", "PT")

    def __init__(self, roots: Sequence[Mapping[str, Any]]) -> None:
        self._roots_by_id = {
            str(root["root_id"]): dict(root)
            for root in roots
        }
        self._pillar_policy = load_root_pillar_policy()
        self._motif_policy = load_semantic_motif_policy()
        self._direct = {
            root_id: classify_root(
                root,
                policy=self._pillar_policy,
            )
            for root_id, root in self._roots_by_id.items()
        }
        self._semantic = {
            root_id: semantic_root_signature(
                root,
                policy=self._motif_policy,
            )
            for root_id, root in self._roots_by_id.items()
        }
        limits = self._motif_policy["minimum_recurrence"]
        self._min_families = int(limits["distinct_dependency_families"])
        self._min_roots = int(limits["distinct_roots"])
        self._allow_exact_multifamily = bool(
            limits["allow_single_exact_root_when_multifamily"]
        )
        self._cache: dict[tuple[str, ...], dict[str, float]] = {}

    def _motif_pillar(
        self,
        selected: set[str],
        *,
        mission: bool,
    ) -> float:
        groups: dict[str, list[dict[str, Any]]] = {}

        for root_id in selected:
            signature = self._semantic[root_id]
            motif_ids = (
                list(signature["mission_motifs"])
                if mission
                else (
                    [str(signature["primary_motif"])]
                    if signature["primary_motif"] is not None
                    else []
                )
            )
            for motif_id in motif_ids:
                groups.setdefault(motif_id, []).append(signature)

        motif_strengths: list[float] = []
        for signatures in groups.values():
            family_maxima: dict[str, float] = {}
            root_ids: set[str] = set()
            exact_multifamily = False

            for signature in signatures:
                root_id = str(signature["root_id"])
                if root_id:
                    root_ids.add(root_id)
                exact_multifamily = (
                    exact_multifamily
                    or bool(signature["exact_multifamily"])
                )
                for family, raw_value in signature["family_strengths"].items():
                    value = float(raw_value)
                    family_maxima[family] = max(
                        family_maxima.get(family, 0.0),
                        value,
                    )

            recurrent = (
                len(family_maxima) >= self._min_families
                and (
                    len(root_ids) >= self._min_roots
                    or (
                        self._allow_exact_multifamily
                        and exact_multifamily
                    )
                )
            )
            if recurrent and family_maxima:
                motif_strengths.append(
                    pillar_score(list(family_maxima.values())) / 100.0
                )

        return pillar_score(motif_strengths) if motif_strengths else 0.0

    def _pillars(self, selected: set[str]) -> dict[str, float | None]:
        strengths: dict[str, list[float]] = {
            pillar: [] for pillar in self._DIRECT_PILLARS
        }

        for root_id in selected:
            item = self._direct[root_id]
            if not item.get("eligible"):
                continue
            contributions = item.get("contributions")
            if not isinstance(contributions, Mapping):
                continue
            for pillar, raw_value in contributions.items():
                if pillar in strengths:
                    strengths[str(pillar)].append(float(raw_value))

        pillars: dict[str, float | None] = {
            pillar: (
                pillar_score(values)
                if values
                else 0.0
            )
            for pillar, values in strengths.items()
        }
        pillars["PX"] = self._motif_pillar(selected, mission=False)
        pillars["PS"] = self._motif_pillar(selected, mission=True)
        pillars["PU"] = None
        return pillars

    def values(self, selected: set[str]) -> dict[str, float]:
        key = tuple(sorted(selected))
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        pillars = self._pillars(selected)
        values = {
            model: float(score_model(model, pillars, ice=0.0).iem_pre)
            for model in MODELS
        }
        self._cache[key] = values
        return values


def _exact_shapley(
    root_ids: Sequence[str],
    engine: _CoalitionValueEngine,
) -> dict[str, dict[str, float]]:
    n = len(root_ids)
    output = {
        model: {root_id: 0.0 for root_id in root_ids}
        for model in MODELS
    }
    if n == 0:
        return output

    for root_id in root_ids:
        others = [item for item in root_ids if item != root_id]
        for size in range(n):
            weight = 1.0 / n / comb(n - 1, size)
            for subset in combinations(others, size):
                base = set(subset)
                before = engine.values(base)
                after = engine.values(base | {root_id})
                for model in MODELS:
                    marginal = after[model] - before[model]
                    if marginal < -1e-9:
                        raise ValueError(
                            f"{model}:{root_id}: marginal Shapley negativo "
                            f"{marginal}."
                        )
                    output[model][root_id] += weight * max(0.0, marginal)

    return output


def _permutation_batch(
    rng: random.Random,
    root_ids: Sequence[str],
    count: int,
    *,
    antithetic: bool,
) -> list[tuple[str, ...]]:
    permutations: list[tuple[str, ...]] = []
    while len(permutations) < count:
        values = list(root_ids)
        rng.shuffle(values)
        permutation = tuple(values)
        permutations.append(permutation)
        if antithetic and len(permutations) < count:
            permutations.append(tuple(reversed(permutation)))
    return permutations[:count]


def _approximate_all_models(
    root_ids: Sequence[str],
    engine: _CoalitionValueEngine,
    policy: Mapping[str, Any],
) -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    spec = policy["approximation_method"]
    seed = int(spec["seed"])
    minimum = int(spec["minimum_permutations"])
    maximum = int(spec["maximum_permutations"])
    batch_size = int(spec["batch_size"])
    tolerance = float(spec["convergence_tolerance_iem_points"])
    stable_required = int(spec["consecutive_stable_checks"])
    antithetic = bool(spec["use_reverse_permutation"])

    if minimum <= 0 or maximum < minimum or batch_size <= 0:
        raise ValueError("Política de permutaciones inválida.")

    rng = random.Random(seed)
    sums = {
        model: {root_id: 0.0 for root_id in root_ids}
        for model in MODELS
    }
    previous: dict[str, dict[str, float]] | None = None
    stable_checks = 0
    used = 0
    max_delta = None

    while used < maximum:
        count = min(batch_size, maximum - used)
        permutations = _permutation_batch(
            rng,
            root_ids,
            count,
            antithetic=antithetic,
        )

        for permutation in permutations:
            selected: set[str] = set()
            before = engine.values(selected)
            for root_id in permutation:
                selected.add(root_id)
                after = engine.values(selected)
                for model in MODELS:
                    marginal = after[model] - before[model]
                    if marginal < -1e-9:
                        raise ValueError(
                            f"{model}:{root_id}: marginal negativo "
                            "en permutación."
                        )
                    sums[model][root_id] += max(0.0, marginal)
                before = after

        used += len(permutations)
        current = {
            model: {
                root_id: sums[model][root_id] / used
                for root_id in root_ids
            }
            for model in MODELS
        }

        if used >= minimum and previous is not None:
            deltas = [
                abs(
                    current[model][root_id]
                    - previous[model][root_id]
                )
                for model in MODELS
                for root_id in root_ids
            ]
            max_delta = max(deltas) if deltas else 0.0
            if max_delta <= tolerance:
                stable_checks += 1
            else:
                stable_checks = 0
            if stable_checks >= stable_required:
                return current, {
                    "method": spec["name"],
                    "permutations_used": used,
                    "convergence_state": "CONVERGED",
                    "max_delta_iem_points": max_delta,
                    "seed": seed,
                    "antithetic": antithetic,
                }

        previous = current

    final = {
        model: {
            root_id: sums[model][root_id] / used
            for root_id in root_ids
        }
        for model in MODELS
    }
    return final, {
        "method": spec["name"],
        "permutations_used": used,
        "convergence_state": "MAX_REACHED",
        "max_delta_iem_points": max_delta,
        "seed": seed,
        "antithetic": antithetic,
    }


def derive_model_attributions(
    pillar_attribution: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Atribuye IEM_pre a raíces independientes con Shapley de interacciones.

    PX y PS se recalculan dentro de cada coalición de raíces. Por tanto, los
    motivos semánticos conservan su efecto sobre IEM pero nunca se convierten
    en jugadores independientes ni reciben una segunda cuota de evidencia.
    """

    if policy is None:
        policy = load_model_attribution_policy()

    if policy.get("structural_coverage_required") is True:
        if pillar_attribution.get("structural_absence_is_zero") is not True:
            return {
                "policy_id": policy["policy_id"],
                "state": "NOT_EVALUABLE",
                "reason": "INCOMPLETE_STRUCTURAL_COVERAGE",
                "attributions": {},
                "method": None,
            }

    roots = _eligible_root_players(pillar_attribution)
    if not roots:
        return {
            "policy_id": policy["policy_id"],
            "state": "NOT_EVALUABLE",
            "reason": "SOURCE_ROOTS_REQUIRED_FOR_DEPENDENCY_SAFE_SHAPLEY",
            "attributions": {},
            "method": None,
        }

    root_ids = [str(item["root_id"]) for item in roots]
    engine = _CoalitionValueEngine(roots)

    exact_max = int(
        policy["exact_method"].get(
            "max_roots",
            policy["exact_method"].get("max_units", 10),
        )
    )
    if len(root_ids) <= exact_max:
        attributions = _exact_shapley(root_ids, engine)
        method = {
            "method": policy["exact_method"]["name"],
            "root_count": len(root_ids),
            "convergence_state": "EXACT",
            "permutations_used": None,
        }
    else:
        attributions, method = _approximate_all_models(
            root_ids,
            engine,
            policy,
        )
        method["root_count"] = len(root_ids)

    totals = {
        model: sum(values.values())
        for model, values in attributions.items()
    }
    grand_values = engine.values(set(root_ids))
    empty_values = engine.values(set())

    efficiency_error = {
        model: abs(
            totals[model] - (grand_values[model] - empty_values[model])
        )
        for model in MODELS
    }

    positive = {
        model: {
            root_id: value
            for root_id, value in values.items()
            if value > 1e-12
        }
        for model, values in attributions.items()
    }

    motif_records = pillar_attribution.get("motif_attributions")
    motif_count = len(motif_records) if isinstance(motif_records, list) else 0

    return {
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "state": "EVALUABLE",
        "value_function": policy["value_function"],
        "player_unit": "INDEPENDENT_ROOT",
        "unit_count": len(root_ids),
        "unit_ids": root_ids,
        "root_count": len(root_ids),
        "motif_unit_count": motif_count,
        "motif_player_count": 0,
        "motifs_recomputed_inside_coalitions": True,
        "interaction_allocation": "SHAPLEY_TO_SOURCE_ROOTS",
        "attributions": positive,
        "model_iem_pre_from_roots": grand_values,
        "empty_coalition_iem_pre": empty_values,
        "shapley_efficiency_error": efficiency_error,
        "method": method,
        "idd_is_ontological_discriminator": False,
    }
