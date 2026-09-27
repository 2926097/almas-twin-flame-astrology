from __future__ import annotations

from importlib import metadata
from math import asin, atan2, cos, degrees, radians, sin, sqrt, tan
from typing import Any, Callable, Mapping, Sequence

EXPECTED_SKYFIELD_VERSION = "1.55"
REFERENCE_METHOD_ID = "ALMAS_SKYFIELD_PLACIDUS_REFERENCE_V1"


def _signed_delta_deg(a: float, b: float) -> float:
    return (float(a) - float(b) + 180.0) % 360.0 - 180.0


def _transpose(matrix: Any) -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(float(matrix[j][i]) for j in range(3))
        for i in range(3)
    )


def _matmul(a: Any, b: Any) -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(
            sum(float(a[i][k]) * float(b[k][j]) for k in range(3))
            for j in range(3)
        )
        for i in range(3)
    )


def true_obliquity_from_frames_deg(
    equatorial_rotation: Any,
    ecliptic_rotation: Any,
) -> float:
    """Recover true obliquity from two independently supplied date frames."""
    relative = _matmul(ecliptic_rotation, _transpose(equatorial_rotation))
    epsilon = abs(degrees(atan2(float(relative[1][2]), float(relative[1][1]))))
    if not 20.0 < epsilon < 26.0:
        raise ValueError(
            f"Oblicuidad verdadera fuera de rango físico esperado: {epsilon}."
        )
    return epsilon


def _ra_to_ecliptic_longitude(ra_deg: float, epsilon_deg: float) -> float:
    ra = radians(float(ra_deg))
    eps = radians(float(epsilon_deg))
    return degrees(
        atan2(sin(ra), cos(ra) * cos(eps))
    ) % 360.0


def _ascendant_longitude(
    armc_deg: float,
    latitude_deg: float,
    epsilon_deg: float,
) -> float:
    theta = radians(float(armc_deg))
    phi = radians(float(latitude_deg))
    eps = radians(float(epsilon_deg))
    denominator = -(
        sin(theta) * cos(eps)
        + tan(phi) * sin(eps)
    )
    return degrees(atan2(cos(theta), denominator)) % 360.0


def _placidus_intermediate_ra(
    armc_deg: float,
    latitude_deg: float,
    epsilon_deg: float,
    *,
    offset_deg: float,
    ad_fraction: float,
    convergence_threshold_deg: float = 1e-7,
    max_iterations: int = 100,
) -> float:
    phi = radians(float(latitude_deg))
    eps = radians(float(epsilon_deg))
    ra = (float(armc_deg) + float(offset_deg)) % 360.0

    for _ in range(int(max_iterations)):
        argument = tan(phi) * sin(radians(ra)) * tan(eps)
        if argument < -1.0 or argument > 1.0:
            raise ValueError(
                "Placidus indefinido para esta latitud/declinación."
            )
        ad_deg = degrees(asin(max(-1.0, min(1.0, argument))))
        new_ra = (
            float(armc_deg)
            + float(offset_deg)
            + float(ad_fraction) * ad_deg
        ) % 360.0
        if abs(_signed_delta_deg(new_ra, ra)) <= convergence_threshold_deg:
            return new_ra
        ra = new_ra

    raise RuntimeError("Placidus no convergió dentro del máximo de iteraciones.")


def placidus_from_armc(
    armc_deg: float,
    latitude_deg: float,
    epsilon_deg: float,
    *,
    convergence_threshold_deg: float = 1e-7,
    max_iterations: int = 100,
) -> dict[str, Any]:
    if abs(float(latitude_deg)) >= 90.0 - float(epsilon_deg):
        raise ValueError(
            "Placidus geométricamente indefinido dentro del círculo polar."
        )

    armc = float(armc_deg) % 360.0
    epsilon = float(epsilon_deg)
    latitude = float(latitude_deg)

    mc = _ra_to_ecliptic_longitude(armc, epsilon)
    asc = _ascendant_longitude(armc, latitude, epsilon)

    definitions = {
        11: (30.0, 1.0 / 3.0),
        12: (60.0, 2.0 / 3.0),
        2: (120.0, 2.0 / 3.0),
        3: (150.0, 1.0 / 3.0),
    }

    cusps: dict[int, float] = {
        1: asc,
        4: (mc + 180.0) % 360.0,
        7: (asc + 180.0) % 360.0,
        10: mc,
    }

    for house, (offset, fraction) in definitions.items():
        ra = _placidus_intermediate_ra(
            armc,
            latitude,
            epsilon,
            offset_deg=offset,
            ad_fraction=fraction,
            convergence_threshold_deg=convergence_threshold_deg,
            max_iterations=max_iterations,
        )
        cusps[house] = _ra_to_ecliptic_longitude(ra, epsilon)

    cusps[5] = (cusps[11] + 180.0) % 360.0
    cusps[6] = (cusps[12] + 180.0) % 360.0
    cusps[8] = (cusps[2] + 180.0) % 360.0
    cusps[9] = (cusps[3] + 180.0) % 360.0

    ordered = {f"H{i}": cusps[i] for i in range(1, 13)}
    return {
        "armc": armc,
        "obliquity": epsilon,
        "houses": ordered,
        "angles": {
            "ASC": asc,
            "DSC": (asc + 180.0) % 360.0,
            "MC": mc,
            "IC": (mc + 180.0) % 360.0,
        },
    }


class SkyfieldPlacidusReference:
    """Independent Placidus reference; no Moira house routines are called."""

    def __init__(
        self,
        *,
        provider_version: str | None = None,
        timescale_factory: Callable[[float], Any] | None = None,
        equatorial_frame: Any | None = None,
        ecliptic_frame: Any | None = None,
    ) -> None:
        if provider_version is None:
            provider_version = metadata.version("skyfield")
        if provider_version != EXPECTED_SKYFIELD_VERSION:
            raise RuntimeError(
                f"skyfield {EXPECTED_SKYFIELD_VERSION} requerido; "
                f"instalado {provider_version}."
            )

        if timescale_factory is None:
            from skyfield.api import load

            def timescale_factory(delta_t_seconds: float) -> Any:
                return load.timescale(
                    delta_t=float(delta_t_seconds),
                    builtin=True,
                )

        if equatorial_frame is None or ecliptic_frame is None:
            from skyfield.framelib import (
                ecliptic_frame as sf_ecliptic_frame,
                true_equator_and_equinox_of_date,
            )
            equatorial_frame = true_equator_and_equinox_of_date
            ecliptic_frame = sf_ecliptic_frame

        self.provider_version = provider_version
        self._timescale_factory = timescale_factory
        self._equatorial_frame = equatorial_frame
        self._ecliptic_frame = ecliptic_frame

    @property
    def provenance(self) -> dict[str, Any]:
        return {
            "method_id": REFERENCE_METHOD_ID,
            "software": "skyfield",
            "software_version": self.provider_version,
            "ephemeris_family": "N/A_HOUSE_GEOMETRY",
            "house_system": "PLACIDUS",
            "house_code": "P",
            "armc": (
                "GREENWICH_APPARENT_SIDEREAL_TIME_PLUS_"
                "GEOGRAPHIC_LONGITUDE"
            ),
            "time_alignment": "BACKEND_JD_UT_PLUS_BACKEND_DELTA_T",
            "obliquity": (
                "TRUE_OBLIQUITY_FROM_SKYFIELD_TRUE_EQUATOR_"
                "AND_TRUE_ECLIPTIC_FRAMES"
            ),
            "intermediate_cusps": "CLASSIC_ITERATIVE_SEMI_ARC_TRISECTION",
            "network_io_used": False,
        }

    def calculate(
        self,
        *,
        jd_ut: float,
        delta_t_seconds: float,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        timescale = self._timescale_factory(float(delta_t_seconds))
        time = timescale.ut1_jd(float(jd_ut))

        # The supplied ΔT must reproduce the same TT epoch as the backend.
        expected_tt = float(jd_ut) + float(delta_t_seconds) / 86400.0
        if abs(float(time.tt) - expected_tt) > 5e-10:
            raise RuntimeError("Skyfield no respetó el ΔT suministrado.")

        armc = (float(time.gast) * 15.0 + float(longitude)) % 360.0

        equatorial_rotation = self._equatorial_frame.rotation_at(time)
        ecliptic_rotation = self._ecliptic_frame.rotation_at(time)
        epsilon = true_obliquity_from_frames_deg(
            equatorial_rotation,
            ecliptic_rotation,
        )

        result = placidus_from_armc(
            armc,
            float(latitude),
            epsilon,
        )
        result["jd_ut"] = float(jd_ut)
        result["jd_tt"] = expected_tt
        result["delta_t_seconds"] = float(delta_t_seconds)
        return result
