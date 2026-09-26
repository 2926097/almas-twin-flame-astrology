from __future__ import annotations

from itertools import combinations
from math import comb
import json
from importlib import resources
import random
from typing import Any, Mapping, Sequence

from .core import MODEL_PILLARS, pillar_score, score_model


POLICY_RESOURCE = "model-attribution-policy.json"
POLICY_PACKAGE = "almas_tfa"
MODELS = ("AF", "KA", "AG", "LG")
PILLARS = ("PA", "PK", "PE", "PR", "PX", "PT", "PS", "PU")


def load_model_attribution_policy() -> dict[str, Any]:
    """Carga la política congelada de atribución Shapley para M21."""

    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V1":
        raise ValueError("Política de atribución de modelos desconocida.")
    return policy


def _eligible_roots(
    pillar_attribution: Mapping[str, Any],
) -> list[dict[str, Any]]:
    raw = pillar_attribution.get("root_attributions")
    if not isinstance(raw, list):
        raise ValueError("pillar_attribution.root_attributions debe ser una lista.")

    roots: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, Mapping) or not item.get("eligible"):
            continue
        root_id = str(item.get("root_id") or "")
        if not root_id:
            raise ValueError("Toda atribución elegible requiere root_id.")
        if root_id in seen:
            raise ValueError(f"root_id duplicado en atribución: {root_id}.")
        seen.add(root_id)

        contributions = item.get("contributions")
        if not isinstance(contributions, Mapping) or not contributions:
            continue

        clean: dict[str, float] = {}
        for pillar, value in contributions.items():
            pillar = str(pillar)
            if pillar not in PILLARS or pillar == "PU":
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"{root_id}:{pillar}: contribution debe ser numérica."
                )
            value = float(value)
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{root_id}:{pillar}: contribution debe estar en [0,1]."
                )
            if value > 0:
                clean[pillar] = value

        if clean:
            roots.append(
                {
                    "root_id": root_id,
                    "contributions": clean,
                }
            )

    roots.sort(key=lambda item: item["root_id"])
    return roots


def _coalition_pillars(
    roots_by_id: Mapping[str, Mapping[str, float]],
    selected: set[str],
) -> dict[str, float | None]:
    strengths: dict[str, list[float]] = {
        pillar: [] for pillar in PILLARS if pillar != "PU"
    }

    for root_id in selected:
        contributions = roots_by_id[root_id]
        for pillar, value in contributions.items():
            if pillar != "PU":
                strengths[pillar].append(float(value))

    pillars: dict[str, float | None] = {}
    for pillar in PILLARS:
        if pillar == "PU":
            pillars[pillar] = None
        else:
            values = strengths[pillar]
            pillars[pillar] = pillar_score(values) if values else 0.0
    return pillars


def _value(
    model: str,
    roots_by_id: Mapping[str, Mapping[str, float]],
    selected: set[str],
) -> float:
    pillars = _coalition_pillars(roots_by_id, selected)
    return score_model(model, pillars, ice=0.0).iem_pre


def _exact_shapley(
    model: str,
    root_ids: Sequence[str],
    roots_by_id: Mapping[str, Mapping[str, float]],
) -> dict[str, float]:
    n = len(root_ids)
    output = {root_id: 0.0 for root_id in root_ids}
    if n == 0:
        return output

    for root_id in root_ids:
        others = [item for item in root_ids if item != root_id]
        for size in range(n):
            weight = 1.0 / n / comb(n - 1, size)
            for subset in combinations(others, size):
                base = set(subset)
                before = _value(model, roots_by_id, base)
                after = _value(model, roots_by_id, base | {root_id})
                marginal = after - before
                if marginal < -1e-9:
                    raise ValueError(
                        f"{model}:{root_id}: marginal Shapley negativo {marginal}."
                    )
                output[root_id] += weight * max(0.0, marginal)

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
    roots_by_id: Mapping[str, Mapping[str, float]],
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
            for model in MODELS:
                selected: set[str] = set()
                before = _value(model, roots_by_id, selected)
                for root_id in permutation:
                    selected.add(root_id)
                    after = _value(model, roots_by_id, selected)
                    marginal = after - before
                    if marginal < -1e-9:
                        raise ValueError(
                            f"{model}:{root_id}: marginal negativo en permutación."
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
    """Deriva atribuciones Shapley por raíz para AF/KA/AG/LG.

    La función de valor es IEM_pre. ICE, IEM_final, temporalidad y rareza nula
    quedan fuera por diseño para que IDD mida arquitectura de evidencia.
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

    roots = _eligible_roots(pillar_attribution)
    if not roots:
        return {
            "policy_id": policy["policy_id"],
            "state": "NOT_EVALUABLE",
            "reason": "NO_ELIGIBLE_ROOTS",
            "attributions": {},
            "method": None,
        }

    root_ids = [item["root_id"] for item in roots]
    roots_by_id = {
        item["root_id"]: dict(item["contributions"])
        for item in roots
    }

    exact_max = int(policy["exact_method"]["max_roots"])
    if len(root_ids) <= exact_max:
        attributions = {
            model: _exact_shapley(model, root_ids, roots_by_id)
            for model in MODELS
        }
        method = {
            "method": policy["exact_method"]["name"],
            "root_count": len(root_ids),
            "convergence_state": "EXACT",
            "permutations_used": None,
        }
    else:
        attributions, method = _approximate_all_models(
            root_ids,
            roots_by_id,
            policy,
        )
        method["root_count"] = len(root_ids)

    totals = {
        model: sum(values.values())
        for model, values in attributions.items()
    }
    grand_values = {
        model: _value(model, roots_by_id, set(root_ids))
        for model in MODELS
    }

    efficiency_error = {
        model: abs(totals[model] - grand_values[model])
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

    return {
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "state": "EVALUABLE",
        "value_function": policy["value_function"],
        "root_count": len(root_ids),
        "root_ids": root_ids,
        "attributions": positive,
        "model_iem_pre_from_roots": grand_values,
        "shapley_efficiency_error": efficiency_error,
        "method": method,
        "idd_is_ontological_discriminator": False,
    }
