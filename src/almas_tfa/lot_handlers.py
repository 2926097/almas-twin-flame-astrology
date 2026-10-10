from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping

from .astrology_geometry import house_for_longitude, normalize_longitude, zodiac_sign
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .positional_hermeneutics import build_position_profile
from .relational_handlers import _chart_points


DEFAULT_POLICY_RESOURCE = "hellenistic-lots-policy.json"
DEFAULT_POLICY_PACKAGE = "almas_tfa"


def load_default_lot_policy() -> dict[str, Any]:
    resource = resources.files(DEFAULT_POLICY_PACKAGE).joinpath("data", DEFAULT_POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_HELLENISTIC_LOTS_V1":
        raise ValueError("Política histórica de lotes desconocida.")
    return policy


def _resolve_sect_from_context(
    subject_id: str,
    context: ModuleContext,
) -> str | None:
    natal_context = context.canonical_snapshot.get("natal_context")
    if not isinstance(natal_context, Mapping):
        return None
    subjects = natal_context.get("subjects")
    if not isinstance(subjects, Mapping):
        return None
    subject = subjects.get(subject_id)
    if not isinstance(subject, Mapping):
        return None
    placements = subject.get("house_placements")
    if not isinstance(placements, Mapping):
        return None
    sun = placements.get("SUN")
    if not isinstance(sun, Mapping):
        return None
    house = sun.get("house")
    if isinstance(house, bool) or not isinstance(house, (int, float)):
        return None
    house = int(house)
    if 7 <= house <= 12:
        return "DAY"
    if 1 <= house <= 6:
        return "NIGHT"
    return None


def _resolve_formula(
    lot_spec: Mapping[str, Any],
    *,
    subject_id: str,
    sect_by_subject: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    formula = lot_spec.get("formula")
    if isinstance(formula, Mapping):
        return formula

    variants = lot_spec.get("variants")
    if not isinstance(variants, Mapping):
        return None

    sect = sect_by_subject.get(subject_id)
    if sect not in {"DAY", "NIGHT"}:
        return None

    selected = variants.get(sect)
    return selected if isinstance(selected, Mapping) else None


def _formula_longitude(
    formula: Mapping[str, Any],
    points: Mapping[str, Mapping[str, Any]],
) -> float | None:
    base = formula.get("base")
    if not isinstance(base, str) or base not in points:
        return None

    value = float(points[base]["longitude"])

    add = formula.get("add", [])
    subtract = formula.get("subtract", [])
    if not isinstance(add, list) or not isinstance(subtract, list):
        raise ValueError("Los campos add y subtract de un lote deben ser listas.")

    for point_id in add:
        if not isinstance(point_id, str) or point_id not in points:
            return None
        value += float(points[point_id]["longitude"])

    for point_id in subtract:
        if not isinstance(point_id, str) or point_id not in points:
            return None
        value -= float(points[point_id]["longitude"])

    return normalize_longitude(value)


def m13_lots(context: ModuleContext) -> ModuleResult:
    """M13: evalúa lotes mediante fórmulas y fuentes expresamente declaradas."""

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result("M13", "No existe salida natal canónica.")

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M13", "M13 requiere exactamente dos cartas.")

    policy = context.raw_input.get("lot_policy")
    policy_source = "RAW_INPUT"
    if not isinstance(policy, Mapping):
        policy = load_default_lot_policy()
        policy_source = "ALMAS_HELLENISTIC_LOTS_V1"

    lot_specs = policy.get("lots")
    if not isinstance(lot_specs, list) or not lot_specs:
        return not_evaluable_result("M13", "lot_policy.lots está vacío.")

    declared_sect = policy.get("sect_by_subject") or {}
    if not isinstance(declared_sect, Mapping):
        raise ValueError("lot_policy.sect_by_subject debe ser un objeto.")

    sect_by_subject: dict[str, Any] = dict(declared_sect)
    for subject_id in charts:
        sid = str(subject_id)
        if sect_by_subject.get(sid) not in {"DAY", "NIGHT"}:
            resolved = _resolve_sect_from_context(sid, context)
            if resolved is not None:
                sect_by_subject[sid] = resolved

    for spec in lot_specs:
        if not isinstance(spec, Mapping):
            raise ValueError("Cada lote debe ser un objeto.")
        if not isinstance(spec.get("id"), str) or not spec.get("id"):
            raise ValueError("Cada lote debe declarar id.")
        if not isinstance(spec.get("source_ref"), str) or not spec.get("source_ref"):
            raise ValueError(
                f"{spec.get('id')}: cada lote debe declarar source_ref."
            )

    output: dict[str, Any] = {
        "policy": dict(policy),
        "policy_source": policy_source,
        "sect_by_subject": dict(sect_by_subject),
        "subjects": {},
    }
    limitations: list[str] = []

    for subject_id, chart in charts.items():
        if not isinstance(chart, Mapping):
            raise ValueError(f"{subject_id}: carta natal inválida.")

        points = _chart_points(chart)
        subject_lots: dict[str, Any] = {}

        for spec in lot_specs:
            lot_id = str(spec["id"])
            formula = _resolve_formula(
                spec,
                subject_id=str(subject_id),
                sect_by_subject=sect_by_subject,
            )

            if formula is None:
                subject_lots[lot_id] = {
                    "status": "NOT_EVALUABLE",
                    "longitude": None,
                    "sign": None,
                    "sign_index": None,
                    "degree_in_sign": None,
                    "house": None,
                    "source_ref": spec["source_ref"],
                    "corroborating_source_ref": spec.get(
                        "corroborating_source_ref"
                    ),
                    "reason": "FORMULA_OR_SECT_NOT_RESOLVED",
                }
                limitations.append(
                    f"{subject_id}/{lot_id}: fórmula o sect no resuelto."
                )
                continue

            longitude = _formula_longitude(formula, points)
            if longitude is None:
                subject_lots[lot_id] = {
                    "status": "NOT_EVALUABLE",
                    "longitude": None,
                    "sign": None,
                    "sign_index": None,
                    "degree_in_sign": None,
                    "house": None,
                    "source_ref": spec["source_ref"],
                    "corroborating_source_ref": spec.get(
                        "corroborating_source_ref"
                    ),
                    "formula": dict(formula),
                    "reason": "MISSING_FORMULA_POINT",
                }
                limitations.append(
                    f"{subject_id}/{lot_id}: falta un punto requerido por la fórmula."
                )
                continue

            houses = chart.get("houses")
            house = (
                house_for_longitude(longitude, houses)
                if isinstance(houses, Mapping)
                else None
            )
            subject_lots[lot_id] = {
                "status": "CALCULATED",
                "longitude": longitude,
                **zodiac_sign(longitude),
                "house": house,
                "source_ref": spec["source_ref"],
                "corroborating_source_ref": spec.get(
                    "corroborating_source_ref"
                ),
                "formula": dict(formula),
                "sect": sect_by_subject.get(subject_id),
            }

            # Los lotes calculados en M13 también son puntos virtuales con
            # posición. Añadimos el contexto editorial sólo bajo el mismo
            # interruptor de definición completa que usa M04.
            if context.raw_input.get("maximum_definition_context") is True:
                lot_positions = dict(points)
                lot_positions[lot_id] = {
                    "longitude": longitude,
                    "point_type": "LOT",
                    "calculation_method": "FORMULA",
                }
                provenance = chart.get("backend_provenance")
                house_system = (
                    provenance.get("house_system")
                    if isinstance(provenance, Mapping)
                    else chart.get("house_system")
                )
                profile = build_position_profile(
                    point_id=lot_id,
                    point_type="LOT",
                    longitude=longitude,
                    house=house,
                    positions=lot_positions,
                    house_system=house_system,
                    rulership_policy=context.raw_input.get("rulership_policy"),
                    rulership_policy_id=context.raw_input.get("rulership_policy_id"),
                    decan_rulership_policy=context.raw_input.get("decan_rulership_policy"),
                    calculation_method="FORMULA",
                    zodiac=chart.get("zodiac"),
                )
                flat_profile = {
                    **profile["position"],
                    **{key: value for key, value in profile.items() if key != "position"},
                }
                def pointer_token(value: str) -> str:
                    return value.replace("~", "~0").replace("/", "~1")

                for ruler_group in (flat_profile["decan"], flat_profile["sign_rulers"]):
                    ruler_group["ruler_profile_refs"] = [
                        "/natal_context/subjects/"
                        + pointer_token(str(subject_id))
                        + "/position_profiles/"
                        + pointer_token(ruler)
                        for ruler in ruler_group.get("rulers", [])
                        if ruler in points
                    ]
                subject_lots[lot_id]["position_profile"] = flat_profile

        output["subjects"][str(subject_id)] = subject_lots

    return ModuleResult(
        module_id="M13",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"lots": output},
        limitations=tuple(
            limitations
            + (
                [
                    "M13 usó la baseline histórica ALMAS_HELLENISTIC_LOTS_V1 para Fortuna/Espíritu; la fórmula histórica no es validación empírica ni discriminador ontológico."
                ]
                if policy_source == "ALMAS_HELLENISTIC_LOTS_V1"
                else []
            )
        ),
    )
