from __future__ import annotations

from typing import Any, Mapping


SIGNS = (
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
)


def normalize_longitude(value: float) -> float:
    """Normaliza una longitud eclíptica al intervalo [0, 360)."""

    return float(value) % 360.0


def angular_distance(a: float, b: float) -> float:
    """Distancia angular mínima entre dos longitudes, en [0, 180]."""

    delta = abs(normalize_longitude(a) - normalize_longitude(b))
    return min(delta, 360.0 - delta)


def zodiac_sign(longitude: float) -> dict[str, Any]:
    """Devuelve signo, índice y grado dentro del signo."""

    lon = normalize_longitude(longitude)
    index = int(lon // 30.0)
    return {
        "sign": SIGNS[index],
        "sign_index": index,
        "degree_in_sign": lon - index * 30.0,
    }


def match_declared_aspect(
    a: float,
    b: float,
    aspect_policy: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any] | None:
    """Encuentra el aspecto declarado más exacto dentro de su orbe.

    No existen orbes por defecto. Cada aspecto debe declarar angle y orb.
    En caso de solapamiento se selecciona el menor orb absoluto y, después,
    el nombre lexicográficamente para mantener determinismo.
    """

    distance = angular_distance(a, b)
    candidates: list[dict[str, Any]] = []

    for name, spec in aspect_policy.items():
        if not isinstance(spec, Mapping):
            raise ValueError(f"{name}: la política de aspecto debe ser un objeto.")

        angle = float(spec["angle"])
        orb_limit = float(spec["orb"])
        if not 0.0 <= angle <= 180.0:
            raise ValueError(f"{name}: angle debe estar en [0, 180].")
        if orb_limit < 0.0:
            raise ValueError(f"{name}: orb no puede ser negativo.")

        orb = abs(distance - angle)
        if orb <= orb_limit:
            candidates.append(
                {
                    "aspect": str(name),
                    "angle": angle,
                    "distance": distance,
                    "orb": orb,
                    "orb_limit": orb_limit,
                    "exactness": (
                        1.0
                        if orb_limit == 0.0 and orb == 0.0
                        else (
                            max(0.0, 1.0 - (orb / orb_limit) ** 2)
                            if orb_limit > 0.0
                            else 0.0
                        )
                    ),
                }
            )

    if not candidates:
        return None

    candidates.sort(key=lambda x: (x["orb"], x["aspect"]))
    return candidates[0]


def house_for_longitude(
    longitude: float,
    cusps: Mapping[str, float],
) -> int | None:
    """Sitúa una longitud en una casa usando doce cúspides declaradas.

    No presupone sistema de casas; utiliza exclusivamente las cúspides que
    entregue el backend.
    """

    normalized = {}
    for i in range(1, 13):
        key = str(i)
        if key not in cusps:
            return None
        normalized[i] = normalize_longitude(float(cusps[key]))

    lon = normalize_longitude(longitude)
    for i in range(1, 13):
        start = normalized[i]
        end = normalized[1 if i == 12 else i + 1]
        span = (end - start) % 360.0
        offset = (lon - start) % 360.0
        if offset < span or (span == 0.0 and offset == 0.0):
            return i

    return None
