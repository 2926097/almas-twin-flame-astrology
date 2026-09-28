from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata
from pathlib import Path
from typing import Any, Mapping

EXPECTED_SKYFIELD_VERSION = "1.55"

TARGET_CANDIDATES: dict[str, tuple[str, ...]] = {
    "SUN": ("sun",),
    "MOON": ("moon",),
    "MERCURY": ("mercury barycenter", "mercury"),
    "VENUS": ("venus barycenter", "venus"),
    "MARS": ("mars barycenter", "mars"),
    "JUPITER": ("jupiter barycenter", "jupiter"),
    "SATURN": ("saturn barycenter", "saturn"),
    "URANUS": ("uranus barycenter", "uranus"),
    "NEPTUNE": ("neptune barycenter", "neptune"),
    "PLUTO": ("pluto barycenter", "pluto"),
}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def parse_utc_case(case: Mapping[str, Any]) -> datetime:
    if case.get("timezone") != "UTC":
        raise ValueError("Los casos dorados de referencia deben estar congelados en UTC.")
    value = datetime.fromisoformat(
        f'{case["birth_date"]}T{case["birth_time"]}'
    )
    return value.replace(tzinfo=timezone.utc)


def _target(kernel: Any, point_id: str) -> tuple[Any, str]:
    errors: list[str] = []
    for candidate in TARGET_CANDIDATES[point_id]:
        try:
            return kernel[candidate], candidate
        except Exception as exc:  # pragma: no cover - provider-specific exception
            errors.append(f"{candidate}: {exc}")
    raise KeyError(
        f"No se pudo resolver {point_id} en el kernel Skyfield: "
        + " | ".join(errors)
    )


def generate_skyfield_planetary_reference(
    *,
    kernel_path: str,
    expected_kernel_sha256: str,
    case: Mapping[str, Any],
    expected_version: str = EXPECTED_SKYFIELD_VERSION,
) -> dict[str, Any]:
    installed = metadata.version("skyfield")
    if installed != expected_version:
        raise RuntimeError(
            f"skyfield {expected_version} requerido; instalado {installed}."
        )

    path = Path(kernel_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Kernel JPL no encontrado: {path}")
    actual_sha = file_sha256(path)
    if actual_sha != expected_kernel_sha256:
        raise ValueError("REFERENCE_KERNEL_SHA256_MISMATCH")

    # Importación tardía: el núcleo ALMAS no depende de Skyfield.
    from skyfield.api import load, load_file
    from skyfield.framelib import (
        ecliptic_frame,
        true_equator_and_equinox_of_date,
    )

    kernel = load_file(str(path))
    ts = load.timescale()
    instant = parse_utc_case(case)
    t = ts.from_datetime(instant)
    earth = kernel["earth"]

    measurements: list[dict[str, Any]] = []
    resolved_targets: dict[str, str] = {}

    for point_id in TARGET_CANDIDATES:
        target, resolved_name = _target(kernel, point_id)
        resolved_targets[point_id] = resolved_name

        apparent = earth.at(t).observe(target).apparent()
        ecl_lat, ecl_lon, _ = apparent.frame_latlon(ecliptic_frame)
        dec, _, _ = apparent.frame_latlon(
            true_equator_and_equinox_of_date
        )

        measurements.extend(
            [
                {
                    "metric": "planetary_longitude",
                    "point_id": point_id,
                    "reference_deg": float(ecl_lon.degrees) % 360.0,
                },
                {
                    "metric": "ecliptic_latitude",
                    "point_id": point_id,
                    "reference_deg": float(ecl_lat.degrees),
                },
                {
                    "metric": "declination",
                    "point_id": point_id,
                    "reference_deg": float(dec.degrees),
                },
            ]
        )

    return {
        "schema_version": "1.0.0",
        "policy_id": "ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1",
        "case_set_id": "ALMAS_ASTRONOMY_GOLDEN_CASES_V1",
        "case_id": case["case_id"],
        "reference_provenance": {
            "method_id": "ALMAS_SKYFIELD_DE440_PLANETARY_REFERENCE_V1",
            "software": "skyfield",
            "software_version": installed,
            "ephemeris_family": "DE440",
            "kernel_filename": path.name,
            "kernel_sha256": actual_sha,
            "coordinate_origin": "GEOCENTRIC",
            "reference_frame": "TRUE_ECLIPTIC_AND_EQUINOX_OF_DATE",
            "apparent_reduction": True,
            "topocentric_positions": False,
            "network_io_used": False,
        },
        "resolved_kernel_targets": resolved_targets,
        "measurements": measurements,
    }
