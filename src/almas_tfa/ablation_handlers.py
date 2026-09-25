from __future__ import annotations

from typing import Any, Callable, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


ABLATION_RUNS = (
    "AB0_FULL",
    "AB1_NO_ASTEROIDS",
    "AB2_NO_TEMPORALITY",
    "AB3_NO_DRACONIC",
    "AB4_NO_RELCHART",
    "AB5_NO_HOUSES_ANGLES",
    "AB6_NO_NODES",
    "AB7_TROPICAL_PLANETARY_CORE",
    "AB8_INDIVIDUAL_ONLY",
)


def _root_key(item: Mapping[str, Any]) -> str:
    return str(item.get("root_key", ""))


def _technique(item: Mapping[str, Any]) -> str:
    return str(item.get("technique_family", ""))


def _dependency(item: Mapping[str, Any]) -> str:
    return str(item.get("dependency_family", ""))


def _contact(item: Mapping[str, Any]) -> Mapping[str, Any]:
    value = item.get("contact")
    return value if isinstance(value, Mapping) else {}


def _is_angular(item: Mapping[str, Any]) -> bool:
    key = _root_key(item)
    return any(
        token in key
        for token in ("AXIS_HORIZON", "AXIS_MERIDIAN", "AXIS_VERTEX")
    )


def _is_nodal(item: Mapping[str, Any]) -> bool:
    key = _root_key(item)
    if "AXIS_NODES" in key:
        return True
    contact = _contact(item)
    points = {
        str(contact.get("point_a", "")).upper(),
        str(contact.get("point_b", "")).upper(),
    }
    return bool(points & {"NORTH_NODE", "SOUTH_NODE", "NN", "SN"})


def _is_temporal(item: Mapping[str, Any]) -> bool:
    technique = _technique(item)
    module = str(item.get("source_module", ""))
    return technique.startswith("TEMPORAL") or module in {"M26", "M27"}


def _is_draconic(item: Mapping[str, Any]) -> bool:
    return _technique(item) in {"NATAL_DRACONIC", "DRACONIC_DD"}


def _is_relchart(item: Mapping[str, Any]) -> bool:
    return _technique(item) == "RELCHART" or _dependency(item) == "RELCHART"


def _is_secondary(item: Mapping[str, Any]) -> bool:
    return _technique(item) == "SECONDARY" or str(
        item.get("canonical_source", "")
    ) == "secondary_symbolic"


def _is_tropical_planetary_core(item: Mapping[str, Any]) -> bool:
    if _technique(item) != "SYN":
        return False

    contact = _contact(item)
    allowed = {"LUMINARY", "PLANET"}
    return (
        contact.get("point_a_type") in allowed
        and contact.get("point_b_type") in allowed
    )


def _is_individual_only(item: Mapping[str, Any]) -> bool:
    contact = _contact(item)
    a = contact.get("subject_a")
    b = contact.get("subject_b")
    return a is not None and b is not None and a == b


def _predicate(run_id: str) -> Callable[[Mapping[str, Any]], bool]:
    if run_id == "AB0_FULL":
        return lambda item: True
    if run_id == "AB1_NO_ASTEROIDS":
        return lambda item: not _is_secondary(item)
    if run_id == "AB2_NO_TEMPORALITY":
        return lambda item: not _is_temporal(item)
    if run_id == "AB3_NO_DRACONIC":
        return lambda item: not _is_draconic(item)
    if run_id == "AB4_NO_RELCHART":
        return lambda item: not _is_relchart(item)
    if run_id == "AB5_NO_HOUSES_ANGLES":
        return lambda item: not _is_angular(item)
    if run_id == "AB6_NO_NODES":
        return lambda item: not _is_nodal(item)
    if run_id == "AB7_TROPICAL_PLANETARY_CORE":
        return _is_tropical_planetary_core
    if run_id == "AB8_INDIVIDUAL_ONLY":
        return _is_individual_only
    raise ValueError(f"Ablación desconocida: {run_id}")


def m22_ablation(context: ModuleContext) -> ModuleResult:
    """M22: matriz de supervivencia de evidencia y raíces AB0–AB8."""

    dedup = context.canonical_snapshot.get("deduplicated_evidence")
    roots_obj = context.canonical_snapshot.get("independent_roots")
    if not isinstance(dedup, Mapping) or not isinstance(roots_obj, Mapping):
        return not_evaluable_result(
            "M22",
            "M22 requiere salidas canónicas de M16 y M17.",
        )

    evidence = dedup.get("retained")
    roots = roots_obj.get("roots")
    if not isinstance(evidence, list) or not isinstance(roots, list):
        return not_evaluable_result(
            "M22",
            "Las salidas de evidencia o raíces no son evaluables.",
        )

    full_evidence_ids = {
        str(item.get("evidence_id"))
        for item in evidence
        if isinstance(item, Mapping)
    }
    root_membership = {
        str(root.get("root_id")): {
            str(eid) for eid in root.get("evidence_ids", [])
        }
        for root in roots
        if isinstance(root, Mapping)
    }
    full_root_ids = set(root_membership)

    runs_output = []
    for run_id in ABLATION_RUNS:
        keep = _predicate(run_id)
        surviving_evidence = {
            str(item.get("evidence_id"))
            for item in evidence
            if isinstance(item, Mapping) and keep(item)
        }
        surviving_roots = {
            root_id
            for root_id, members in root_membership.items()
            if members & surviving_evidence
        }

        runs_output.append(
            {
                "run": run_id,
                "surviving_evidence_ids": sorted(surviving_evidence),
                "lost_evidence_ids": sorted(full_evidence_ids - surviving_evidence),
                "surviving_root_ids": sorted(surviving_roots),
                "lost_root_ids": sorted(full_root_ids - surviving_roots),
                "survival_fraction": (
                    len(surviving_roots) / len(full_root_ids)
                    if full_root_ids
                    else None
                ),
            }
        )

    root_survival = []
    by_run = {run["run"]: set(run["surviving_root_ids"]) for run in runs_output}
    for root_id in sorted(full_root_ids):
        root_survival.append(
            {
                "root_id": root_id,
                "survives": {
                    run_id: root_id in by_run[run_id]
                    for run_id in ABLATION_RUNS
                },
            }
        )

    output = {
        "runs": runs_output,
        "root_survival": root_survival,
        "structural_only": True,
        "dependency_classes_assigned": False,
    }

    return ModuleResult(
        module_id="M22",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"ablation": output},
        limitations=(
            "M22 mide supervivencia estructural; no asigna automáticamente clases contractuales ni estados metafísicos.",
        ),
    )
