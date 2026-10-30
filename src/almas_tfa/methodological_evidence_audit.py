"""Auditoría descriptiva y fail-closed de M21–M24; no modifica el estado canónico.

Esta capa SHADOW no recalcula puntuaciones, no estima valores p y no promueve
ninguna afirmación relacional o metafísica. Sólo contrasta invariantes de los
recibos producidos por los módulos existentes.
"""
from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import Any

from .ablation_handlers import ABLATION_RUNS

AUDIT_POLICY = "ALMAS_METHOD_EVIDENCE_AUDIT_V1"


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label}: se esperaba un objeto.")
    return value


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label}: se esperaba un número finito.")
    return float(value)


def _ids(raw: Any, label: str) -> set[str]:
    if not isinstance(raw, list) or any(not isinstance(x, str) or not x for x in raw):
        raise ValueError(f"{label}: se esperaba una lista de identificadores.")
    if len(set(raw)) != len(raw):
        raise ValueError(f"{label}: identificadores duplicados.")
    return set(raw)


def _null_audit(value: Any) -> dict[str, Any]:
    if value is None:
        return {"status": "NOT_EVALUABLE", "reason": "M24_ABSENT"}
    data = _mapping(value, "M24")
    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("M24: faltan corridas nulas.")
    if data.get("metaphysical_probability") is not False:
        raise ValueError("M24: promoción a probabilidad metafísica no permitida.")
    names: set[str] = set()
    for item in runs:
        run = _mapping(item, "M24.run")
        name = run.get("id")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("M24: ID de corrida nula ausente o duplicado.")
        names.add(name)
        n = run.get("n")
        count = run.get("extreme_count")
        if (type(n) is not int or n <= 0 or type(count) is not int
                or not 0 <= count <= n):
            raise ValueError(f"M24.{name}: conteos inválidos.")
        freq = _finite(run.get("structural_frequency"), f"M24.{name}.structural_frequency")
        if abs(freq - count / n) > 1e-12:
            raise ValueError(f"M24.{name}: frecuencia inconsistente.")
        for frozen in ("preregistration_ref", "feature_set_ref", "orb_policy_ref",
                       "event_set_ref", "generator_ref", "statistic_id"):
            if not isinstance(run.get(frozen), str) or not run[frozen]:
                raise ValueError(f"M24.{name}: falta {frozen}.")
    return {"status": "DESCRIPTIVE_CHECKED", "run_count": len(runs),
            "p_value": None, "exchangeability": "NOT_VERIFIED",
            "empirical_validation": False}


def _ablation_audit(value: Any) -> dict[str, Any]:
    if value is None:
        return {"status": "NOT_EVALUABLE", "reason": "M22_ABSENT"}
    data = _mapping(value, "M22")
    if data.get("structural_only") is not True or data.get("dependency_classes_assigned") is not False:
        raise ValueError("M22: no se permiten promociones estructurales.")
    runs = data.get("runs")
    if not isinstance(runs, list) or len(runs) != len(ABLATION_RUNS):
        raise ValueError("M22: batería AB0–AB8 incompleta.")
    by_name: dict[str, Mapping[str, Any]] = {}
    for item in runs:
        run = _mapping(item, "M22.run")
        name = run.get("run")
        if name in by_name or name not in ABLATION_RUNS:
            raise ValueError("M22: corrida repetida o ajena a AB0–AB8.")
        by_name[name] = run
    if set(by_name) != set(ABLATION_RUNS):
        raise ValueError("M22: faltan corridas AB0–AB8.")
    baseline = _ids(by_name["AB0_FULL"].get("surviving_root_ids"), "AB0.roots")
    for name, run in by_name.items():
        kept = _ids(run.get("surviving_root_ids"), f"{name}.roots")
        lost = _ids(run.get("lost_root_ids"), f"{name}.lost_roots")
        if kept & lost or kept | lost != baseline:
            raise ValueError(f"{name}: partición de raíces inconsistente.")
        fraction = run.get("survival_fraction")
        expected = len(kept) / len(baseline) if baseline else None
        if (expected is None and fraction is not None) or (expected is not None and
            abs(_finite(fraction, f"{name}.survival_fraction") - expected) > 1e-12):
            raise ValueError(f"{name}: fracción de supervivencia inconsistente.")
    return {"status": "STRUCTURAL_CHECKED", "runs": list(ABLATION_RUNS),
            "baseline_root_count": len(baseline), "predictive_value": "NOT_MEASURED",
            "ontological_discrimination": False}


def _time_audit(value: Any) -> dict[str, Any]:
    if value is None:
        return {"status": "NOT_EVALUABLE", "reason": "M23_ABSENT"}
    data = _mapping(value, "M23")
    eligible = data.get("robustness_component_eligible")
    if type(eligible) is not bool:
        raise ValueError("M23: elegibilidad desconocida.")
    component = data.get("robustness_component")
    if eligible != (component is not None):
        raise ValueError("M23: componente incompatible con elegibilidad.")
    if eligible and not 0 <= _finite(component, "M23.component") <= 1:
        raise ValueError("M23: componente fuera de [0,1].")
    if not isinstance(data.get("preregistration_ref"), str) or not data["preregistration_ref"]:
        raise ValueError("M23: falta preregistro.")
    return {"status": "COMPONENT_DESCRIPTIVE" if eligible else "DIAGNOSTIC_ONLY",
            "input_reliability_proven_by_audit": False,
            "predictive_validity": "NOT_EVALUABLE"}


def _shapley_audit(value: Any) -> dict[str, Any]:
    if value is None:
        return {"status": "NOT_EVALUABLE", "reason": "M21_ATTRIBUTION_ABSENT"}
    data = _mapping(value, "M21.model_attributions")
    if data.get("state") != "EVALUABLE":
        return {"status": "NOT_EVALUABLE", "reason": str(data.get("reason", "M21_NOT_EVALUABLE"))}
    ids = _ids(data.get("unit_ids"), "M21.unit_ids")
    if (data.get("player_unit") != "INDEPENDENT_ROOT"
            or data.get("motif_player_count") != 0
            or data.get("motifs_recomputed_inside_coalitions") is not True):
        raise ValueError("M21: unidad Shapley o deduplicación incompatibles.")
    attributions = _mapping(data.get("attributions"), "M21.attributions")
    for model, values in attributions.items():
        terms = _mapping(values, f"M21.{model}")
        if not set(terms).issubset(ids):
            raise ValueError(f"M21.{model}: jugador derivado no autorizado.")
        for key, v in terms.items():
            _finite(v, f"M21.{model}.{key}")
    errors = _mapping(data.get("shapley_efficiency_error"), "M21.efficiency")
    residuals = {str(k): _finite(v, f"M21.efficiency.{k}") for k, v in errors.items()}
    if not residuals or any(x < 0 for x in residuals.values()):
        raise ValueError("M21: residuos incompletos o negativos.")
    return {"status": "ATTRIBUTION_CHECKED", "independent_players": len(ids),
            "maximum_efficiency_residual": max(residuals.values()),
            "causality": "NOT_ESTABLISHED", "ontological_discrimination": False}


def audit_methodological_evidence(canonical: Mapping[str, Any]) -> dict[str, Any]:
    """Inspecciona salidas existentes. Nunca las modifica ni genera índices nuevos.

    La validez empírica exige cohorte, protocolo y evaluación externa de forma
    independiente; su mera declaración en el JSON no autoriza promoción.
    """
    source = _mapping(canonical, "canonical")
    return {
        "policy_id": AUDIT_POLICY,
        "mode": "SHADOW_READ_ONLY",
        "computational_verification": {"status": "CI_SHA_RECEIPT_REQUIRED"},
        "null_models": _null_audit(source.get("null_models")),
        "ablations": _ablation_audit(source.get("ablation")),
        "birth_time": _time_audit(source.get("time_sensitivity")),
        "shapley": _shapley_audit(source.get("model_attributions")),
        "empirical_validation": {"status": "NOT_VERIFIED_BY_THIS_AUDIT",
                                 "independent_holdout_required": True},
        "metaphysical_hypotheses": {"status": "NOT_EVALUABLE",
                                    "metaphysical_probability": None},
        "production_indices_modified": False,
        "promotes_ontology": False,
    }
