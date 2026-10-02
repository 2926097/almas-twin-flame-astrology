"""Geometría de puntos calculados; ninguna función decide interpretación."""
from __future__ import annotations

from math import atan2, cos, degrees, fsum, isfinite, radians, sin, sqrt
from typing import Sequence

MIN_JD_TT = 2415020.5  # 1900-01-01: alcance aprobado del subperfil, no límite IERS.
MAX_JD_TT = 2488069.5  # 2100-01-01.
EARTH_MOON_GM_DE440 = 398600.43550702266 + 4902.800118457549


def _numbers(values: Sequence[float]) -> tuple[float, ...]:
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) for v in values):
        raise ValueError('El cálculo exige números finitos, sin booleanos.')
    return tuple(float(v) for v in values)


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _norm(v):
    # fsum fija la acumulación entre Python 3.10/3.12; sum cambió en 3.12.
    return sqrt(fsum(x*x for x in v))


def _rotation(matrix: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], ...]:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError('La transformación requiere matriz 3×3.')
    rows = tuple(_numbers(row) for row in matrix)
    if any(abs(fsum(rows[i][k]*rows[j][k] for k in range(3)) - (1 if i == j else 0)) > 1e-10
           for i in range(3) for j in range(3)):
        raise ValueError('La transformación no es ortonormal.')
    det = fsum(rows[0][i]*_cross(rows[1], rows[2])[i] for i in range(3))
    if abs(det - 1) > 1e-10:
        raise ValueError('La transformación no conserva orientación.')
    return rows


def vertex_axis(armc_deg: float, latitude_deg: float, obliquity_deg: float) -> dict:
    """Intersección eclíptica/vertical primario, con polo occidental explícito."""
    armc, latitude, obliquity = _numbers((armc_deg, latitude_deg, obliquity_deg))
    if not -90 < latitude < 90 or not 20 < obliquity < 26:
        raise ValueError('Latitud polar u oblicuidad fuera del alcance aprobado.')
    theta, phi, eps = map(radians, (armc % 360, latitude, obliquity))
    # r(λ)·norte = A cos(λ) + B sin(λ); sin dividir por sin(latitud).
    a = -sin(phi)*cos(theta)
    b = -sin(phi)*sin(theta)*cos(eps) + cos(phi)*sin(eps)
    if sqrt(a*a+b*b) <= 1e-12:
        raise ValueError('Planos coincidentes: eje Vertex indefinido.')
    longitude = atan2(-a, b)
    east_component = -sin(theta)*cos(longitude) + cos(theta)*sin(longitude)*cos(eps)
    if abs(east_component) <= 1e-12:
        raise ValueError('Intersección sin orientación este/oeste resoluble.')
    vertex = degrees(longitude) % 360
    if east_component > 0:
        vertex = (vertex + 180) % 360
    return dict(vertex=vertex, anti_vertex=(vertex + 180) % 360, axis_longitude=vertex % 180)


def mean_apogee(jd_tt: float, nutation_longitude_deg: float) -> float:
    """Modelo escalar IERS 2003 F+Ω−l+180°, más Δψ suministrado.

    No es la proyección de órbita media Moshier/Swiss; esta variante se
    identifica expresamente para evitar intercambiarlas por su nombre.
    """
    jd, dpsi = _numbers((jd_tt, nutation_longitude_deg))
    if not MIN_JD_TT <= jd <= MAX_JD_TT or abs(dpsi) > 1:
        raise ValueError('Época o nutación fuera del alcance aprobado.')
    t = (jd - 2451545.0) / 36525.0
    polynomials = (
        (485868.249036, 1717915923.2178, 31.8792, 0.051635, -0.00024470),
        (335779.526232, 1739527262.8478, -12.7512, -0.001037, 0.00000417),
        (450160.398036, -6962890.5431, 7.4722, 0.007702, -0.00005939),
    )
    lunar_anomaly, latitude_argument, node = (
        fsum(coefficient * t**power for power, coefficient in enumerate(poly)) / 3600
        for poly in polynomials)
    return (latitude_argument + node - lunar_anomaly + 180 + dpsi) % 360


def osculating_apogee(position_icrf_km: Sequence[float], velocity_icrf_km_s: Sequence[float],
                      rotation_icrf_to_true_ecliptic: Sequence[Sequence[float]],
                      mu_km3_s2: float = EARTH_MOON_GM_DE440) -> dict:
    """Apogeo de la elipse osculante geocéntrica, formado en marco inercial.

    La rotación de fecha se aplica a la dirección final; nunca a una
    velocidad respecto de un marco rotante. No se usa luz-tiempo.
    """
    if len(position_icrf_km) != 3 or len(velocity_icrf_km_s) != 3:
        raise ValueError('El estado requiere dos vectores de tres componentes.')
    r, v = _numbers(position_icrf_km), _numbers(velocity_icrf_km_s)
    mu = _numbers((mu_km3_s2,))[0]
    rotation = _rotation(rotation_icrf_to_true_ecliptic)
    radius, speed = _norm(r), _norm(v)
    if mu <= 0 or radius <= 0 or speed <= 0:
        raise ValueError('Estado o parámetro gravitacional degenerado.')
    h = _cross(r, v)
    if _norm(h) / (radius * speed) <= 1e-12:
        raise ValueError('Momento angular degenerado.')
    vh = _cross(v, h)
    eccentricity_vector = tuple(vh[i]/mu - r[i]/radius for i in range(3))
    eccentricity = _norm(eccentricity_vector)
    if not 1e-10 < eccentricity < 1 - 1e-10:
        raise ValueError('Órbita circular o no elíptica: apogeo no admitido.')
    apogee = tuple(-fsum(rotation[i][j]*eccentricity_vector[j] for j in range(3)) for i in range(3))
    if sqrt(apogee[0]**2 + apogee[1]**2) <= 1e-12 * eccentricity:
        raise ValueError('Longitud eclíptica del apogeo indefinida.')
    return dict(longitude=degrees(atan2(apogee[1], apogee[0])) % 360, eccentricity=eccentricity)


def axis_sample_longitude(longitude: float, central_axis_longitude: float) -> float:
    """Representante del eje próximo al central; conserva continuidad circular."""
    value, central = _numbers((longitude, central_axis_longitude))
    base = value % 180
    candidates = (base, base + 180)
    return min(candidates, key=lambda c: abs((c - central + 180) % 360 - 180))
