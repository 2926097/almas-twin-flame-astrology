"""Entradas astronómicas optativas para SSAR, sin modificar el backend core."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata
from math import degrees
from pathlib import Path

from .calculated_points import EARTH_MOON_GM_DE440, MAX_JD_TT, MIN_JD_TT, _numbers
from .skyfield_placidus_reference import true_obliquity_from_frames_deg

EXPECTED_SKYFIELD_VERSION = '1.55'
OFFSETS_MINUTES = (-30, -15, 0, 15, 30)


@dataclass(frozen=True)
class CalculatedPointInputConfig:
    kernel_path: str
    kernel_sha256: str
    kernel_family: str = 'DE440'

    def __post_init__(self):
        if self.kernel_family != 'DE440' or len(self.kernel_sha256) != 64 or any(
            c not in '0123456789abcdef' for c in self.kernel_sha256):
            raise ValueError('El proveedor de fase 6 exige DE440 y SHA-256 explícito.')


class SkyfieldCalculatedPointInputs:
    def __init__(self, config: CalculatedPointInputConfig):
        if metadata.version('skyfield') != EXPECTED_SKYFIELD_VERSION:
            raise RuntimeError('El proveedor requiere skyfield==1.55.')
        path = Path(config.kernel_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError('Kernel DE440 ausente; no se descarga automáticamente.')
        digest = sha256(path.read_bytes()).hexdigest()
        if digest != config.kernel_sha256:
            raise ValueError('KERNEL_SHA256_MISMATCH')
        from skyfield.api import load, load_file
        from skyfield.framelib import ecliptic_frame
        self._ephemeris = load_file(str(path))
        self._timescale = load.timescale(builtin=True)
        self._frame = ecliptic_frame
        self._provenance = dict(provider='SKYFIELD_CALCULATED_POINT_INPUTS', software_version=EXPECTED_SKYFIELD_VERSION,
            epoch_scale='TT', armc_scale='GAST_UT1', coordinate_origin='GEOCENTRIC', state_frame='ICRF_INERTIAL',
            reference_frame='TRUE_ECLIPTIC_EQUINOX_OF_DATE', ephemeris_id='DE440', ephemeris_sha256=digest,
            source_refs=['JPL_DE440', 'SKYFIELD_1_55'], network_io_used=False,
            time_conversion='SKYFIELD_BUILTIN_TT_UT1_DELTA_T', frame_model='SKYFIELD_IAU2000A_DATE_FRAMES')

    @property
    def provenance(self):
        return deepcopy(self._provenance)

    def samples(self, jd_tt: float, latitude_deg: float, longitude_deg: float) -> list[dict]:
        jd, latitude, longitude = _numbers((jd_tt, latitude_deg, longitude_deg))
        if not -90 < latitude < 90 or not -180 <= longitude <= 180:
            raise ValueError('Coordenadas geográficas fuera de alcance.')
        if not MIN_JD_TT <= jd - 30/1440 <= jd + 30/1440 <= MAX_JD_TT:
            raise ValueError('La malla completa requiere épocas TT dentro de 1900–2100.')
        output = []
        for offset in OFFSETS_MINUTES:
            epoch = jd + offset/1440
            time = self._timescale.tt_jd(epoch)
            geocentric = self._ephemeris[301].at(time) - self._ephemeris[399].at(time)
            rotation = self._frame.rotation_at(time)
            epsilon = true_obliquity_from_frames_deg(time.M, rotation)
            # API interna de Skyfield 1.55 fijada e inspeccionada; sin EOP descargado.
            dpsi, _ = time._nutation_angles_radians
            output.append(dict(offset_minutes=offset, jd_tt=epoch, armc_deg=(float(time.gast)*15 + longitude) % 360,
                latitude_deg=latitude, true_obliquity_deg=epsilon, nutation_longitude_deg=degrees(float(dpsi)),
                moon_state=dict(epoch_jd_tt=epoch, position_icrf_km=[float(v) for v in geocentric.xyz.km],
                    velocity_icrf_km_s=[float(v) for v in geocentric.velocity.km_per_s],
                    rotation_icrf_to_true_ecliptic=[[float(v) for v in row] for row in rotation],
                    mu_km3_s2=EARTH_MOON_GM_DE440, frame='ICRF_INERTIAL', coordinate_origin='GEOCENTRIC',
                    position_units='KM', velocity_units='KM_PER_SECOND')))
        return output
