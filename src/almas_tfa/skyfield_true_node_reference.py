from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata
from math import atan2, degrees, sqrt
from pathlib import Path
from typing import Any, Sequence

EXPECTED_SKYFIELD_VERSION = "1.55"
REFERENCE_METHOD_ID = "ALMAS_SKYFIELD_DE440_TRUE_NODE_REFERENCE_V1"
EARTH_NAIF_ID = 399
MOON_NAIF_ID = 301


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    )


def _matvec(matrix: Any, vector: Sequence[float]) -> tuple[float, float, float]:
    return tuple(
        sum(float(matrix[i][j]) * float(vector[j]) for j in range(3))
        for i in range(3)
    )


def ascending_node_longitude_from_state(
    position_icrf: Sequence[float],
    velocity_icrf: Sequence[float],
    rotation_icrf_to_true_ecliptic: Any,
) -> float:
    """Instantaneous geocentric osculating ascending-node longitude.

    The orbital normal is built in the inertial ICRF frame and only then
    rotated to the true ecliptic/equinox of date.  This avoids contaminating
    the osculating plane with the angular velocity of the date-dependent frame.
    """

    h_icrf = _cross(position_icrf, velocity_icrf)
    h_ecliptic = _matvec(rotation_icrf_to_true_ecliptic, h_icrf)
    hx, hy, _ = h_ecliptic

    # n = k x h = (-hy, hx, 0), oriented toward the ascending node.
    nx = -hy
    ny = hx
    norm = sqrt(nx * nx + ny * ny)
    if norm <= 1e-18:
        raise ValueError("Plano lunar degenerado: nodo ascendente indefinido.")

    return degrees(atan2(ny, nx)) % 360.0


@dataclass(frozen=True)
class SkyfieldTrueNodeReferenceConfig:
    kernel_path: str
    kernel_sha256: str
    kernel_family: str = "DE440"
    expected_provider_version: str = EXPECTED_SKYFIELD_VERSION

    def __post_init__(self) -> None:
        if self.kernel_family != "DE440":
            raise ValueError("La referencia True Node V1 exige DE440.")
        if (
            len(self.kernel_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.kernel_sha256)
        ):
            raise ValueError("kernel_sha256 debe ser SHA-256 hexadecimal.")


class SkyfieldTrueNodeReference:
    """Referencia independiente del True Node mediante geometría osculadora."""

    def __init__(
        self,
        config: SkyfieldTrueNodeReferenceConfig,
        *,
        ephemeris: Any | None = None,
        timescale: Any | None = None,
        ecliptic_frame: Any | None = None,
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
                    f"skyfield {config.expected_provider_version} requerido; "
                    f"instalado {installed}."
                )
            from skyfield.api import load, load_file
            from skyfield.framelib import ecliptic_frame as sf_ecliptic_frame

            ephemeris = load_file(str(kernel_path))
            timescale = load.timescale(builtin=True)
            ecliptic_frame = sf_ecliptic_frame
            provider_version = installed
        else:
            provider_version = provider_version or config.expected_provider_version
            if timescale is None or ecliptic_frame is None:
                raise ValueError("timescale/frame inyectados obligatorios.")

        if provider_version != config.expected_provider_version:
            raise RuntimeError(
                f"Versión Skyfield no congelada: {provider_version}."
            )

        self._ephemeris = ephemeris
        self._timescale = timescale
        self._ecliptic_frame = ecliptic_frame
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
            "definition": (
                "INSTANTANEOUS_GEOCENTRIC_OSCULATING_LUNAR_PLANE_"
                "INTERSECTION_WITH_TRUE_ECLIPTIC_OF_DATE"
            ),
            "state_vectors": "SIMULTANEOUS_MOON_MINUS_EARTH",
            "network_io_used": False,
        }

    def calculate_at_tt_jd(self, jd_tt: float) -> float:
        time = self._timescale.tt_jd(float(jd_tt))
        moon = self._ephemeris[MOON_NAIF_ID].at(time)
        earth = self._ephemeris[EARTH_NAIF_ID].at(time)
        geocentric = moon - earth

        position = geocentric.xyz.au
        velocity = geocentric.velocity.au_per_d
        rotation = self._ecliptic_frame.rotation_at(time)
        return ascending_node_longitude_from_state(
            position,
            velocity,
            rotation,
        )
