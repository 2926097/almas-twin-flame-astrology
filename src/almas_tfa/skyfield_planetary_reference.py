from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata
from pathlib import Path
from typing import Any, Mapping

EXPECTED_SKYFIELD_VERSION = "1.55"
REFERENCE_METHOD_ID = "ALMAS_SKYFIELD_DE440_PLANETARY_REFERENCE_V1"

# Must match Moira's documented DE-series route endpoints.
TARGET_NAIF_IDS: Mapping[str, int] = {
    "SUN": 10,
    "MOON": 301,
    "MERCURY": 199,
    "VENUS": 299,
    "MARS": 4,
    "JUPITER": 5,
    "SATURN": 6,
    "URANUS": 7,
    "NEPTUNE": 8,
    "PLUTO": 9,
}
EARTH_NAIF_ID = 399


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class SkyfieldReferenceConfig:
    kernel_path: str
    kernel_sha256: str
    kernel_family: str = "DE440"
    expected_provider_version: str = EXPECTED_SKYFIELD_VERSION

    def __post_init__(self) -> None:
        if self.kernel_family != "DE440":
            raise ValueError("La referencia Skyfield V1 exige DE440.")
        if (
            len(self.kernel_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.kernel_sha256)
        ):
            raise ValueError("kernel_sha256 debe ser SHA-256 hexadecimal.")


class SkyfieldPlanetaryReference:
    """Referencia independiente para la etapa planetaria del gate dorado."""

    def __init__(
        self,
        config: SkyfieldReferenceConfig,
        *,
        ephemeris: Any | None = None,
        timescale: Any | None = None,
        ecliptic_frame: Any | None = None,
        equatorial_frame: Any | None = None,
        provider_version: str | None = None,
    ) -> None:
        self.config = config
        kernel_path = Path(config.kernel_path).expanduser().resolve()
        if not kernel_path.is_file():
            raise FileNotFoundError(f"Kernel JPL no encontrado: {kernel_path}")
        actual_sha = _file_sha256(kernel_path)
        if actual_sha != config.kernel_sha256:
            raise ValueError("KERNEL_SHA256_MISMATCH")
        self.kernel_path = kernel_path
        self.kernel_sha256 = actual_sha

        if ephemeris is None:
            installed = metadata.version("skyfield")
            if installed != config.expected_provider_version:
                raise RuntimeError(
                    "skyfield "
                    f"{config.expected_provider_version} requerido; "
                    f"instalado {installed}."
                )
            from skyfield.api import load, load_file
            from skyfield.framelib import (
                ecliptic_frame as sf_ecliptic_frame,
                true_equator_and_equinox_of_date,
            )

            ephemeris = load_file(str(kernel_path))
            timescale = load.timescale(builtin=True)
            ecliptic_frame = sf_ecliptic_frame
            equatorial_frame = true_equator_and_equinox_of_date
            provider_version = installed
        else:
            provider_version = (
                provider_version or config.expected_provider_version
            )
            if timescale is None:
                raise ValueError("timescale inyectado es obligatorio.")
            if ecliptic_frame is None or equatorial_frame is None:
                raise ValueError("frames de referencia inyectados obligatorios.")

        if provider_version != config.expected_provider_version:
            raise RuntimeError(
                f"Versión Skyfield no congelada: {provider_version}."
            )

        self._ephemeris = ephemeris
        self._timescale = timescale
        self._ecliptic_frame = ecliptic_frame
        self._equatorial_frame = equatorial_frame
        self.provider_version = provider_version

    @property
    def provenance(self) -> dict[str, Any]:
        return {
            "method_id": REFERENCE_METHOD_ID,
            "software": "skyfield",
            "software_version": self.provider_version,
            "ephemeris_family": self.config.kernel_family,
            "kernel_filename": self.kernel_path.name,
            "kernel_sha256": self.kernel_sha256,
            "coordinate_origin": "GEOCENTRIC",
            "reference_frame": "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
            "apparent_reduction": True,
            "time_alignment": "COMMON_TT_EPOCH_FROM_BACKEND_RECEIPT",
            "network_io_used": False,
        }

    def calculate_at_tt_jd(
        self,
        jd_tt: float,
    ) -> dict[str, dict[str, float]]:
        time = self._timescale.tt_jd(float(jd_tt))
        observer = self._ephemeris[EARTH_NAIF_ID].at(time)
        output: dict[str, dict[str, float]] = {}

        for point_id, target_id in TARGET_NAIF_IDS.items():
            apparent = observer.observe(
                self._ephemeris[target_id]
            ).apparent()
            latitude, longitude, _ = apparent.frame_latlon(
                self._ecliptic_frame
            )
            declination, _, _ = apparent.frame_latlon(
                self._equatorial_frame
            )
            output[point_id] = {
                "longitude": float(longitude.degrees) % 360.0,
                "latitude": float(latitude.degrees),
                "declination": float(declination.degrees),
            }

        return output
