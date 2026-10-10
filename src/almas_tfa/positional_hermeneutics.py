"""Trazable descriptores de posiciones para autoría, sin scoring ni prosa automática."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .astrology_geometry import SIGNS, zodiac_sign

_MOVING_TYPES = {"LUMINARY", "PLANET", "ASTEROID", "NODE"}
_MAX_DISPOSITOR_DEPTH = 16
_MAX_DISPOSITOR_BRANCHES = 512
_MAX_RULERS_PER_SIGN = 3


def _rulers_for_sign(policy: Mapping[str, Any] | None, sign: str) -> list[str]:
    if policy is None or sign not in policy:
        return []
    raw = policy[sign]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        if not raw or any(not isinstance(item, str) or not item.strip() for item in raw):
            raise ValueError(f"{sign}: la lista de regentes debe contener nombres no vacíos.")
        if len(raw) > _MAX_RULERS_PER_SIGN:
            raise ValueError(f"{sign}: demasiados regentes para una política reproducible.")
        return list(dict.fromkeys(item.strip() for item in raw))
    raise ValueError(f"{sign}: regencia debe ser string o lista de strings.")


def _validate_decan_policy(policy: Mapping[str, Any] | None) -> tuple[str | None, Mapping[str, Any] | None]:
    if policy is None:
        return None, None
    policy_id = policy.get("policy_id")
    rulers = policy.get("rulers_by_sign")
    if not isinstance(policy_id, str) or not policy_id.strip():
        raise ValueError("decan_rulership_policy.policy_id es obligatorio.")
    if not isinstance(rulers, Mapping):
        raise ValueError("decan_rulership_policy.rulers_by_sign debe ser un objeto.")
    unknown = set(rulers) - set(SIGNS)
    if unknown:
        raise ValueError("decan_rulership_policy contiene signos desconocidos.")
    for sign, values in rulers.items():
        if (
            not isinstance(values, list)
            or len(values) != 3
            or any(not isinstance(item, str) or not item.strip() for item in values)
        ):
            raise ValueError(f"{sign}: deben declararse tres regentes de decanato.")
    return policy_id.strip(), rulers


def _dispositor_chains(
    point_id: str,
    positions: Mapping[str, Any],
    rulership_policy: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    if not isinstance(rulership_policy, Mapping):
        return []

    initial = _rulers_for_sign(rulership_policy, zodiac_sign(float(positions[point_id]["longitude"]))["sign"])
    if not initial:
        return [{"path": [point_id], "state": "UNRESOLVED"}]

    finished: list[dict[str, Any]] = []

    def walk(current: str, path: list[str]) -> None:
        if len(finished) >= _MAX_DISPOSITOR_BRANCHES:
            return
        if len(path) >= _MAX_DISPOSITOR_DEPTH:
            finished.append({"path": path, "state": "MAX_DEPTH"})
            return
        current_data = positions.get(current)
        if not isinstance(current_data, Mapping) or current_data.get("longitude") is None:
            finished.append({"path": path, "state": "UNRESOLVED"})
            return
        current_sign = zodiac_sign(float(current_data["longitude"]))["sign"]
        next_rulers = _rulers_for_sign(rulership_policy, current_sign)
        if not next_rulers:
            finished.append({"path": path, "state": "UNRESOLVED"})
            return
        for ruler in next_rulers:
            if len(finished) >= _MAX_DISPOSITOR_BRANCHES:
                return
            if ruler == current:
                finished.append({"path": path, "state": "SELF_DISPOSITOR"})
            elif ruler in path:
                finished.append({"path": [*path, ruler], "state": "CYCLE"})
            else:
                walk(ruler, [*path, ruler])

    for ruler in initial:
        if len(finished) >= _MAX_DISPOSITOR_BRANCHES:
            finished.append({"path": [point_id], "state": "MAX_BRANCHES"})
            break
        if ruler == point_id:
            finished.append({"path": [point_id], "state": "SELF_DISPOSITOR"})
        elif ruler in positions:
            walk(ruler, [point_id, ruler])
        else:
            finished.append({"path": [point_id, ruler], "state": "UNRESOLVED"})
    return finished


def _motion_context(
    point_type: str | None,
    retrograde: Any,
    speed: Any,
    calculation_method: Any,
) -> dict[str, Any]:
    if retrograde is not None and not isinstance(retrograde, bool):
        raise ValueError("retrograde debe ser booleano o nulo.")
    if point_type == "ANGLE":
        if retrograde is True:
            raise ValueError("ANGLE no admite retrogradación.")
        state = "NOT_APPLICABLE"
    elif point_type in _MOVING_TYPES:
        state = "NOT_EVALUABLE" if retrograde is None else ("RETROGRADE" if retrograde else "DIRECT")
    elif point_type in {"LOT", "OTHER", None}:
        if not isinstance(calculation_method, str) or not calculation_method.strip():
            state = "NOT_EVALUABLE"
        else:
            state = "NOT_EVALUABLE" if retrograde is None else ("RETROGRADE" if retrograde else "DIRECT")
    else:
        state = "NOT_EVALUABLE"
    return {
        "state": state,
        "speed": speed,
        "station_state": "NOT_EVALUATED",
        "interpretation_state": "NOT_AUTHORED",
    }


def build_position_profile(
    *,
    point_id: str,
    point_type: str | None,
    longitude: float,
    house: int | None,
    positions: Mapping[str, Any],
    house_system: str | None = None,
    rulership_policy: Mapping[str, Any] | None = None,
    rulership_policy_id: str | None = None,
    decan_rulership_policy: Mapping[str, Any] | None = None,
    retrograde: bool | None = None,
    speed: float | None = None,
    calculation_method: str | None = None,
    zodiac: str | None = None,
) -> dict[str, Any]:
    """Describe posición y regencias explícitas; nunca asigna significado doctrinal.

    Decanos son tercios geométricos de diez grados. Su regente sólo se devuelve
    si el usuario declara una política con tres regentes por signo. La longitud
    se interpreta en el zodiaco que ya codifica el backend; este método no aplica
    ayanāṃśa ni transforma posiciones entre zodiacos.
    """
    if point_id not in positions or not isinstance(positions[point_id], Mapping):
        raise ValueError("point_id debe existir en positions.")
    if not isinstance(point_id, str) or not point_id.strip():
        raise ValueError("point_id debe ser no vacío.")
    lon = float(longitude)
    if not 0.0 <= lon < 360.0:
        lon %= 360.0
    pos = zodiac_sign(lon)
    decan_number = min(int(pos["degree_in_sign"] // 10.0) + 1, 3)
    decan_policy_id, decan_rulers_by_sign = _validate_decan_policy(decan_rulership_policy)
    declared_decan_rulers: list[str] = []
    if decan_rulers_by_sign is not None:
        sign_rulers = decan_rulers_by_sign.get(pos["sign"])
        if sign_rulers is not None:
            declared_decan_rulers = [sign_rulers[decan_number - 1]]

    sign_rulers = _rulers_for_sign(rulership_policy, pos["sign"])
    position_info = {
        **pos,
        "longitude": lon,
        "zodiac": zodiac or "UNSPECIFIED",
    }
    return {
        "point_id": point_id,
        "point_type": point_type,
        "position": position_info,
        "house": house,
        "house_system": house_system,
        "house_state": (
            "NOT_EVALUABLE" if house is None else
            ("AVAILABLE" if isinstance(house_system, str) and house_system.strip() else "SYSTEM_UNSPECIFIED")
        ),
        "decan": {
            "number": decan_number,
            "start_degree": float((decan_number - 1) * 10),
            "end_degree_exclusive": float(decan_number * 10),
            "system_id": "SIGN_TEN_DEGREE_SEGMENTS_V1",
            "rulers": declared_decan_rulers,
            "ruler_policy_id": decan_policy_id,
            "ruler_state": "DECLARED" if declared_decan_rulers else "NOT_DECLARED",
        },
        "sign_rulers": {
            "rulers": sign_rulers,
            "policy_id": rulership_policy_id,
            "state": "DECLARED" if sign_rulers else "NOT_DECLARED",
        },
        "dispositor_chains": _dispositor_chains(point_id, positions, rulership_policy),
        "motion": _motion_context(point_type, retrograde, speed, calculation_method),
    }
