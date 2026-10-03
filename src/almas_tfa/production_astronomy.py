from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from contextlib import nullcontext
from enum import Enum
from hashlib import sha256
from importlib import metadata, resources
import json
from math import asin, atan2, cos, degrees, floor, isfinite, radians, sin, sqrt
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .astrology_backend import (
    AstronomyBackendNotEvaluableError,
    NatalRequest,
)
from .dual_nodes import mean_node_positions
from .relationship_chart_handlers import DavisonRequest


POLICY_RESOURCE = "production-astronomy-backend-policy.json"
FIXED_STAR_PARAN_POLICY_RESOURCE = "fixed-star-paran-policy.json"
POLICY_PACKAGE = "almas_tfa"
BACKEND_ID = "MOIRA_JPL_SPK"
PARAN_PLANET_BODIES = (
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
)


def load_production_astronomy_backend_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data", POLICY_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1":
        raise ValueError("Política de backend astronómico desconocida.")
    return policy


def load_fixed_star_paran_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data", FIXED_STAR_PARAN_POLICY_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_FIXED_STAR_PARAN_POLICY_V1":
        raise ValueError("Política de estrellas fijas/parans desconocida.")
    return policy


def _provider_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return _provider_jsonable(value.value)
    if isinstance(value, Mapping):
        return {
            str(key): _provider_jsonable(item)
            for key, item in value.items()
        }
    if isinstance(value, (set, frozenset)):
        converted = [_provider_jsonable(item) for item in value]
        return sorted(
            converted,
            key=lambda item: json.dumps(
                item, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ),
        )
    if isinstance(value, (list, tuple)):
        return [_provider_jsonable(item) for item in value]
    if is_dataclass(value):
        return {
            field.name: _provider_jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if hasattr(value, "__dict__"):
        return {
            str(key): _provider_jsonable(item)
            for key, item in vars(value).items()
            if not str(key).startswith("_")
        }
    return str(value)


def _canon_entry_payload(entry: Any) -> dict[str, Any]:
    name = _value(entry, "name")
    tiers = _value(entry, "tiers")
    default_enabled = _value(entry, "default_enabled", True)
    if not isinstance(name, str) or not name.strip():
        raise AstronomyBackendNotEvaluableError(
            "Canon de estrellas: entrada sin nombre válido."
        )
    if not isinstance(tiers, (list, tuple, set, frozenset)) or not tiers:
        raise AstronomyBackendNotEvaluableError(
            f"Canon de estrellas: {name} sin memberships."
        )
    if not isinstance(default_enabled, bool):
        raise AstronomyBackendNotEvaluableError(
            f"Canon de estrellas: {name} tiene default_enabled inválido."
        )
    normalized_tiers = sorted(
        str(_value(tier, "value", tier)).strip().lower()
        for tier in tiers
    )
    if any(not tier for tier in normalized_tiers):
        raise AstronomyBackendNotEvaluableError(
            f"Canon de estrellas: {name} tiene membership vacío."
        )
    return {
        "name": name.strip(),
        "tiers": normalized_tiers,
        "default_enabled": default_enabled,
    }


def _canon_fingerprint(entries: list[dict[str, Any]]) -> str:
    names = [item["name"].strip().casefold() for item in entries]
    if len(names) != len(set(names)):
        raise AstronomyBackendNotEvaluableError(
            "Canon de estrellas: nombres duplicados tras normalización."
        )
    normalized = sorted(
        (
            {
                "name": item["name"],
                "tiers": sorted(item["tiers"]),
                "default_enabled": bool(item["default_enabled"]),
            }
            for item in entries
        ),
        key=lambda item: item["name"],
    )
    encoded = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _canonical_json_fingerprint(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True)
class MoiraBackendConfig:
    kernel_path: str
    kernel_sha256: str
    kernel_family: str
    house_system: str
    expected_provider_version: str = "6.8.2"

    def __post_init__(self) -> None:
        if not self.kernel_path:
            raise ValueError("kernel_path es obligatorio.")
        if (
            not isinstance(self.kernel_sha256, str)
            or len(self.kernel_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.kernel_sha256)
        ):
            raise ValueError("kernel_sha256 debe ser SHA-256 hexadecimal.")
        if not self.kernel_family:
            raise ValueError("kernel_family es obligatorio.")
        if not self.house_system:
            raise ValueError("house_system es obligatorio.")


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _value(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _normalize_name(value: Any) -> str:
    return (
        str(value)
        .strip()
        .upper()
        .replace("-", "_")
        .replace(" ", "_")
    )


def _normalize_system(value: Any) -> str:
    raw = _value(value, "value")
    if raw is None:
        raw = _value(value, "name", value)
    return _normalize_name(raw)


def _strict_utc(request: NatalRequest) -> datetime:
    if not request.birth_time:
        raise AstronomyBackendNotEvaluableError(
            f"{request.subject_id}: el backend de producción no inventa hora natal."
        )
    if not request.timezone:
        raise AstronomyBackendNotEvaluableError(
            f"{request.subject_id}: timezone IANA obligatoria."
        )

    try:
        naive = datetime.fromisoformat(
            f"{request.birth_date}T{request.birth_time}"
        )
    except ValueError as exc:
        raise AstronomyBackendNotEvaluableError(
            f"{request.subject_id}: fecha/hora local inválida."
        ) from exc

    try:
        zone = ZoneInfo(request.timezone)
    except ZoneInfoNotFoundError as exc:
        raise AstronomyBackendNotEvaluableError(
            f"{request.subject_id}: timezone IANA desconocida: {request.timezone}."
        ) from exc

    valid: dict[datetime, datetime] = {}
    for fold in (0, 1):
        aware = naive.replace(tzinfo=zone, fold=fold)
        utc_value = aware.astimezone(timezone.utc)
        roundtrip = utc_value.astimezone(zone).replace(tzinfo=None)
        if roundtrip == naive:
            valid[utc_value] = aware

    if not valid:
        raise AstronomyBackendNotEvaluableError(
            f"{request.subject_id}: hora local inexistente por transición DST."
        )
    if len(valid) > 1:
        raise AstronomyBackendNotEvaluableError(
            f"{request.subject_id}: hora local ambigua por transición DST."
        )
    return next(iter(valid))


def _declination(longitude: float, latitude: float, obliquity: float) -> float:
    lon = radians(float(longitude))
    lat = radians(float(latitude))
    eps = radians(float(obliquity))
    value = sin(lat) * cos(eps) + cos(lat) * sin(eps) * sin(lon)
    value = max(-1.0, min(1.0, value))
    return degrees(asin(value))


def _spherical_midpoint(
    lat_a: float,
    lon_a: float,
    lat_b: float,
    lon_b: float,
) -> tuple[float, float]:
    lat1, lon1 = radians(lat_a), radians(lon_a)
    lat2, lon2 = radians(lat_b), radians(lon_b)

    x = cos(lat1) * cos(lon1) + cos(lat2) * cos(lon2)
    y = cos(lat1) * sin(lon1) + cos(lat2) * sin(lon2)
    z = sin(lat1) + sin(lat2)
    norm = sqrt(x * x + y * y + z * z)
    if norm <= 1e-15:
        raise AstronomyBackendNotEvaluableError(
            "Davison: puntos geográficos antipodales sin punto medio único."
        )

    x /= norm
    y /= norm
    z /= norm
    return degrees(asin(z)), degrees(atan2(y, x))


class MoiraProductionBackend:
    """Adaptador ALMAS para Moira/JPL con procedencia fail-closed.

    La dependencia es opcional. El cálculo exige un kernel local cuyo SHA-256
    coincida con el valor congelado. No descarga efemérides ni geocodifica.
    """

    backend_id = BACKEND_ID

    def __init__(
        self,
        config: MoiraBackendConfig,
        *,
        facade: Any | None = None,
        house_system_token: Any | None = None,
        provider_version: str | None = None,
        policy: Mapping[str, Any] | None = None,
        paran_api: Mapping[str, Any] | None = None,
        reader_override_factory: Any | None = None,
    ) -> None:
        self.config = config
        self.policy = dict(
            policy or load_production_astronomy_backend_policy()
        )

        provider = self.policy["provider"]
        expected = str(provider["pinned_version"])
        if config.expected_provider_version != expected:
            raise ValueError(
                "expected_provider_version diverge de la política congelada."
            )

        family = config.kernel_family.upper()
        if family not in set(self.policy["kernel"]["allowed_families"]):
            raise ValueError(f"Familia de kernel no permitida: {family}.")
        self.kernel_family = family

        kernel_path = Path(config.kernel_path).expanduser().resolve()
        if not kernel_path.is_file():
            raise FileNotFoundError(f"Kernel JPL no encontrado: {kernel_path}")
        actual_sha = _file_sha256(kernel_path)
        if actual_sha != config.kernel_sha256:
            raise ValueError("KERNEL_SHA256_MISMATCH")
        self.kernel_path = kernel_path
        self.kernel_sha256 = actual_sha

        if facade is None:
            installed = metadata.version(str(provider["package"]))
            if installed != expected:
                raise RuntimeError(
                    f"moira-astro {expected} requerido; instalado {installed}."
                )
            from moira import HouseSystem, Moira
            from moira.facade import (
                find_parans,
                jd_from_datetime,
                list_paran_stars,
                natal_angular_contacts,
                paran_policy_preset,
                utc_to_ut1,
            )
            from moira.spk_reader import use_reader_override

            facade = Moira(kernel_path=str(kernel_path))
            paran_api = {
                "find_parans": find_parans,
                "jd_from_datetime": jd_from_datetime,
                "list_paran_stars": list_paran_stars,
                "natal_angular_contacts": natal_angular_contacts,
                "paran_policy_preset": paran_policy_preset,
                "utc_to_ut1": utc_to_ut1,
            }
            reader_override_factory = use_reader_override
            try:
                house_system_token = getattr(
                    HouseSystem, config.house_system.upper()
                )
            except AttributeError as exc:
                raise ValueError(
                    f"Sistema de casas Moira desconocido: "
                    f"{config.house_system}."
                ) from exc
            provider_version = installed
        else:
            provider_version = provider_version or expected
            if house_system_token is None:
                house_system_token = config.house_system.upper()

        if provider_version != expected:
            raise RuntimeError(
                f"Versión del provider no congelada: {provider_version}."
            )

        self._facade = facade
        self._house_system_token = house_system_token
        self._paran_api = dict(paran_api or {})
        self._reader_override_factory = reader_override_factory
        self.backend_version = expected

    @property
    def provenance(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy["policy_id"],
            "adapter_id": self.policy["adapter_id"],
            "backend_id": self.backend_id,
            "backend_version": self.backend_version,
            "provider_package": self.policy["provider"]["package"],
            "provider_version": self.backend_version,
            "kernel_filename": self.kernel_path.name,
            "kernel_family": self.kernel_family,
            "kernel_sha256": self.kernel_sha256,
            "house_system": self.config.house_system.upper(),
            "node_mode": self.policy["natal"]["node_mode"],
            "node_variants": ["TRUE", "MEAN"],
            "zodiac": self.policy["natal"]["zodiac"],
            "coordinate_origin": self.policy["natal"]["coordinate_origin"],
            "reference_frame": self.policy["natal"]["reference_frame"],
            "apparent_reduction": self.policy["natal"]["apparent_reduction"],
            "topocentric_positions": self.policy["natal"]["topocentric_positions"],
            "network_io_used": False,
            "geocoding_used": False,
        }

    @property
    def capabilities(self) -> Mapping[str, bool]:
        capabilities = dict(self.policy["capabilities"])
        required = {
            "find_parans",
            "jd_from_datetime",
            "list_paran_stars",
            "natal_angular_contacts",
            "paran_policy_preset",
            "utc_to_ut1",
        }
        capabilities["fixed_star_parans"] = all(
            callable(self._paran_api.get(name)) for name in required
        )
        return capabilities

    def _chart_and_houses(
        self,
        instant: datetime,
        *,
        latitude: float,
        longitude: float,
    ) -> tuple[Any, Any]:
        chart = self._facade.chart(
            instant,
            include_nodes=True,
        )
        houses = self._facade.houses(
            instant,
            latitude=float(latitude),
            longitude=float(longitude),
            system=self._house_system_token,
        )

        if bool(_value(houses, "fallback", False)):
            raise AstronomyBackendNotEvaluableError(
                "El sistema de casas requirió fallback polar; ALMAS lo prohíbe."
            )
        effective = _value(houses, "effective_system")
        if effective is not None:
            requested = _normalize_system(self._house_system_token)
            if _normalize_system(effective) != requested:
                raise AstronomyBackendNotEvaluableError(
                    "El sistema de casas efectivo difiere del solicitado."
                )
        return chart, houses

    def _positions(self, chart: Any) -> dict[str, dict[str, Any]]:
        planets = _value(chart, "planets")
        if not isinstance(planets, Mapping):
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió un mapa de planetas."
            )

        obliquity = _value(chart, "obliquity")
        if isinstance(obliquity, bool) or not isinstance(
            obliquity, (int, float)
        ):
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió oblicuidad numérica."
            )

        allowed = {
            "SUN", "MOON", "MERCURY", "VENUS", "MARS",
            "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO",
        }
        output: dict[str, dict[str, Any]] = {}
        for raw_name, data in planets.items():
            point_id = _normalize_name(raw_name)
            if point_id not in allowed:
                continue
            longitude = _value(data, "longitude")
            latitude = _value(data, "latitude", 0.0)
            speed = _value(data, "speed")
            retrograde = _value(data, "retrograde")
            if not isinstance(longitude, (int, float)) or isinstance(
                longitude, bool
            ):
                continue
            if not isinstance(latitude, (int, float)) or isinstance(
                latitude, bool
            ):
                latitude = 0.0
            output[point_id] = {
                "longitude": float(longitude) % 360.0,
                "latitude": float(latitude),
                "declination": _declination(
                    float(longitude), float(latitude), float(obliquity)
                ),
                "speed": (
                    float(speed)
                    if isinstance(speed, (int, float))
                    and not isinstance(speed, bool)
                    else None
                ),
                "retrograde": (
                    bool(retrograde)
                    if isinstance(retrograde, bool)
                    else (
                        float(speed) < 0
                        if isinstance(speed, (int, float))
                        and not isinstance(speed, bool)
                        else None
                    )
                ),
                "point_type": (
                    "LUMINARY"
                    if point_id in {"SUN", "MOON"}
                    else "PLANET"
                ),
            }

        missing = sorted(
            set(self.policy["natal"]["required_points"])
            - {"NORTH_NODE", "SOUTH_NODE"}
            - set(output)
        )
        if missing:
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió puntos planetarios requeridos: "
                + ", ".join(missing)
            )

        nodes = _value(chart, "nodes")
        if not isinstance(nodes, Mapping):
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió nodos lunares."
            )
        north = None
        for raw_name, data in nodes.items():
            normalized = _normalize_name(raw_name)
            if (
                ("TRUE" in normalized and "NODE" in normalized)
                or normalized in {"NORTH_NODE", "TRUE_NODE"}
            ):
                north = data
                break
        if north is None:
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió True/North Node."
            )

        node_lon = _value(north, "longitude")
        if not isinstance(node_lon, (int, float)) or isinstance(
            node_lon, bool
        ):
            raise AstronomyBackendNotEvaluableError(
                "True Node sin longitud numérica."
            )
        node_speed = _value(north, "speed")
        north_lon = float(node_lon) % 360.0
        north_dec = _declination(north_lon, 0.0, float(obliquity))
        south_lon = (north_lon + 180.0) % 360.0
        south_dec = _declination(south_lon, 0.0, float(obliquity))

        output["NORTH_NODE"] = {
            "longitude": north_lon,
            "latitude": 0.0,
            "declination": north_dec,
            "speed": (
                float(node_speed)
                if isinstance(node_speed, (int, float))
                and not isinstance(node_speed, bool)
                else None
            ),
            "retrograde": (
                float(node_speed) < 0
                if isinstance(node_speed, (int, float))
                and not isinstance(node_speed, bool)
                else None
            ),
            "point_type": "NODE",
            "node_variant": "TRUE",
            "nodal_axis_id": "LUNAR_NODE_AXIS",
        }
        output["SOUTH_NODE"] = {
            "longitude": south_lon,
            "latitude": 0.0,
            "declination": south_dec,
            "speed": (
                float(node_speed)
                if isinstance(node_speed, (int, float))
                and not isinstance(node_speed, bool)
                else None
            ),
            "retrograde": (
                float(node_speed) < 0
                if isinstance(node_speed, (int, float))
                and not isinstance(node_speed, bool)
                else None
            ),
            "point_type": "NODE",
            "node_variant": "TRUE",
            "nodal_axis_id": "LUNAR_NODE_AXIS",
        }
        return output

    def _house_payload(self, houses: Any) -> tuple[dict[str, float], dict[str, float]]:
        raw_cusps = _value(houses, "cusps")
        if not isinstance(raw_cusps, (list, tuple)) or len(raw_cusps) != 12:
            raise AstronomyBackendNotEvaluableError(
                "Moira debe devolver exactamente doce cúspides."
            )
        cusps = {
            str(index): float(raw_cusps[index - 1]) % 360.0
            for index in range(1, 13)
        }
        asc = _value(houses, "asc")
        mc = _value(houses, "mc")
        if not isinstance(asc, (int, float)) or not isinstance(
            mc, (int, float)
        ):
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió ASC/MC numéricos."
            )
        angles = {
            "ASC": float(asc) % 360.0,
            "DSC": (float(asc) + 180.0) % 360.0,
            "MC": float(mc) % 360.0,
            "IC": (float(mc) + 180.0) % 360.0,
        }
        return cusps, angles

    def _calculate_at(
        self,
        instant: datetime,
        *,
        latitude: float,
        longitude: float,
        subject_id: str,
    ) -> dict[str, Any]:
        chart, house_data = self._chart_and_houses(
            instant,
            latitude=latitude,
            longitude=longitude,
        )
        houses, angles = self._house_payload(house_data)
        jd_ut = _value(chart, "jd_ut")
        delta_t = _value(chart, "delta_t")
        if (
            isinstance(jd_ut, bool)
            or not isinstance(jd_ut, (int, float))
            or isinstance(delta_t, bool)
            or not isinstance(delta_t, (int, float))
        ):
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió jd_ut/delta_t numéricos."
            )
        jd_ut = float(jd_ut)
        delta_t = float(delta_t)
        jd_tt = jd_ut + delta_t / 86400.0
        positions = self._positions(chart)
        positions.update(mean_node_positions(jd_tt=jd_tt))
        obliquity = float(_value(chart, "obliquity"))
        for point_id in ("MEAN_NORTH_NODE", "MEAN_SOUTH_NODE"):
            positions[point_id]["declination"] = _declination(
                positions[point_id]["longitude"], 0.0, obliquity
            )
        return {
            "subject_id": subject_id,
            "timed": True,
            "backend_id": self.backend_id,
            "backend_version": self.backend_version,
            "zodiac": "TROPICAL",
            "positions": positions,
            "angles": angles,
            "houses": houses,
            "backend_provenance": self.provenance,
            "metadata": {
                "utc_instant": instant.astimezone(timezone.utc).isoformat(),
                "jd_ut": jd_ut,
                "delta_t_seconds": delta_t,
                "jd_tt": jd_tt,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "house_system_requested": self.config.house_system.upper(),
                "house_fallback_used": False,
            },
        }

    def calculate_natal(self, request: NatalRequest) -> Mapping[str, Any]:
        if request.latitude is None or request.longitude is None:
            raise AstronomyBackendNotEvaluableError(
                f"{request.subject_id}: coordenadas numéricas obligatorias; "
                "no se permite geocodificación implícita."
            )
        instant = _strict_utc(request)
        return self._calculate_at(
            instant,
            latitude=request.latitude,
            longitude=request.longitude,
            subject_id=request.subject_id,
        )

    def calculate_transit_positions(
        self,
        instant_utc: datetime,
    ) -> Mapping[str, Any]:
        """Calcula posiciones geocéntricas para TTRANSIT sin casas."""

        if not isinstance(instant_utc, datetime) or instant_utc.tzinfo is None:
            raise AstronomyBackendNotEvaluableError(
                "TTRANSIT requiere un datetime timezone-aware."
            )
        instant = instant_utc.astimezone(timezone.utc)
        chart = self._facade.chart(
            instant,
            include_nodes=True,
        )
        positions = self._positions(chart)
        jd_ut = _value(chart, "jd_ut")
        delta_t = _value(chart, "delta_t")
        if (
            isinstance(jd_ut, bool)
            or not isinstance(jd_ut, (int, float))
            or isinstance(delta_t, bool)
            or not isinstance(delta_t, (int, float))
        ):
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió jd_ut/delta_t para Mean Node de tránsito."
            )
        positions.update(mean_node_positions(jd_tt=float(jd_ut) + float(delta_t) / 86400.0))
        obliquity = _value(chart, "obliquity")
        if isinstance(obliquity, bool) or not isinstance(obliquity, (int, float)):
            raise AstronomyBackendNotEvaluableError(
                "Moira no devolvió oblicuidad para Mean Node de tránsito."
            )
        for point_id in ("MEAN_NORTH_NODE", "MEAN_SOUTH_NODE"):
            positions[point_id]["declination"] = _declination(
                positions[point_id]["longitude"], 0.0, float(obliquity)
            )
        planet_ids = {
            "SUN", "MOON", "MERCURY", "VENUS", "MARS",
            "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO",
        }
        return {
            "instant_utc": instant.isoformat(),
            "positions": {
                point_id: dict(data)
                for point_id, data in positions.items()
            if point_id in planet_ids | {
                "NORTH_NODE", "SOUTH_NODE", "MEAN_NORTH_NODE", "MEAN_SOUTH_NODE"
            }
            },
            "backend_id": self.backend_id,
            "backend_version": self.backend_version,
            "backend_provenance": self.provenance,
        }

    def calculate_return_chart(self, instant_utc: datetime, *, latitude: float, longitude: float) -> Mapping[str, Any]:
        """Carta geocéntrica para un retorno exacto y ubicación explícita."""
        from math import isfinite
        if not isinstance(instant_utc, datetime) or instant_utc.tzinfo is None:
            raise AstronomyBackendNotEvaluableError("Carta de retorno requiere datetime con zona.")
        for value, bound in ((latitude, 90), (longitude, 180)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not -bound <= value <= bound:
                raise AstronomyBackendNotEvaluableError("Coordenadas de retorno inválidas.")
        return self._calculate_at(instant_utc.astimezone(timezone.utc), latitude=float(latitude),
                                  longitude=float(longitude), subject_id="RETURN_CHART")

    def _require_paran_api(self) -> Mapping[str, Any]:
        required = {
            "find_parans",
            "jd_from_datetime",
            "list_paran_stars",
            "natal_angular_contacts",
            "paran_policy_preset",
            "utc_to_ut1",
        }
        missing = sorted(
            name
            for name in required
            if not callable(self._paran_api.get(name))
        )
        if missing:
            raise AstronomyBackendNotEvaluableError(
                "Superficie Moira de estrellas/parans no disponible: "
                + ", ".join(missing)
            )
        return self._paran_api

    def _reader_scope(self):
        factory = self._reader_override_factory
        if factory is None:
            return nullcontext()
        return factory(getattr(self._facade, "_reader", None))

    def calculate_fixed_star_parans(
        self,
        request: NatalRequest,
    ) -> Mapping[str, Any]:
        """Capa secundaria support_only de estrellas fijas y parans."""

        if (
            isinstance(request.latitude, bool)
            or not isinstance(request.latitude, (int, float))
            or isinstance(request.longitude, bool)
            or not isinstance(request.longitude, (int, float))
            or not isfinite(float(request.latitude))
            or not isfinite(float(request.longitude))
            or not -90.0 <= float(request.latitude) <= 90.0
            or not -180.0 <= float(request.longitude) <= 180.0
        ):
            raise AstronomyBackendNotEvaluableError(
                f"{request.subject_id}: estrellas/parans requieren "
                "coordenadas numéricas válidas (latitud −90..90, "
                "longitud −180..180)."
            )
        instant = _strict_utc(request)
        layer_policy = load_fixed_star_paran_policy()
        policy_fingerprint = _canonical_json_fingerprint(layer_policy)
        api = self._require_paran_api()

        try:
            raw_entries = api["list_paran_stars"](
                tiers=None,
                available_only=True,
            )
        except Exception as exc:
            raise AstronomyBackendNotEvaluableError(
                "No se pudo resolver el canon de estrellas de Moira."
            ) from exc

        canon_entries = [
            _canon_entry_payload(entry)
            for entry in raw_entries
        ]
        if not canon_entries:
            raise AstronomyBackendNotEvaluableError(
                "El canon de estrellas disponible está vacío."
            )
        canon_names = [item["name"] for item in canon_entries]
        canon_fingerprint = _canon_fingerprint(canon_entries)

        fixed_stars: list[dict[str, Any]] = []
        for name in canon_names:
            try:
                star = self._facade.fixed_star(name, instant)
            except Exception as exc:
                raise AstronomyBackendNotEvaluableError(
                    f"No se pudo calcular la estrella fija {name}."
                ) from exc

            longitude = _value(star, "longitude")
            latitude = _value(star, "latitude")
            magnitude = _value(star, "magnitude")
            if (
                isinstance(longitude, bool)
                or not isinstance(longitude, (int, float))
                or isinstance(latitude, bool)
                or not isinstance(latitude, (int, float))
                or isinstance(magnitude, bool)
                or not isinstance(magnitude, (int, float))
            ):
                raise AstronomyBackendNotEvaluableError(
                    f"Estrella fija {name}: posición/magnitud inválida."
                )
            if not all(
                isfinite(float(value))
                for value in (longitude, latitude, magnitude)
            ):
                raise AstronomyBackendNotEvaluableError(
                    f"Estrella fija {name}: posición/magnitud no finita."
                )
            if not -90.0 <= float(latitude) <= 90.0:
                raise AstronomyBackendNotEvaluableError(
                    f"Estrella fija {name}: latitud eclíptica fuera de rango."
                )
            returned_name = str(_value(star, "name", name)).strip()
            if returned_name.casefold() != name.casefold():
                raise AstronomyBackendNotEvaluableError(
                    f"Estrella fija {name}: nombre devuelto no coincide."
                )
            source = _value(star, "source")
            is_topocentric = _value(star, "is_topocentric")
            computation_truth = _provider_jsonable(
                _value(star, "computation_truth")
            )
            nomenclature = _provider_jsonable(
                _value(star, "nomenclature")
            )
            if (
                not isinstance(source, str)
                or not source.strip()
                or not isinstance(is_topocentric, bool)
                or not isinstance(computation_truth, Mapping)
                or not computation_truth
                or nomenclature is None
            ):
                raise AstronomyBackendNotEvaluableError(
                    f"Estrella fija {name}: provenance incompleta."
                )

            fixed_stars.append(
                {
                    "name": returned_name,
                    "nomenclature": nomenclature,
                    "longitude": float(longitude) % 360.0,
                    "latitude": float(latitude),
                    "magnitude": float(magnitude),
                    "source": source.strip(),
                    "is_topocentric": is_topocentric,
                    "computation_truth": computation_truth,
                }
            )

        try:
            jd_utc = float(api["jd_from_datetime"](instant))
            jd_day_utc = floor(jd_utc - 0.5) + 0.5
            jd_day_ut1 = float(api["utc_to_ut1"](jd_day_utc))
            natal_jd_ut1 = float(api["utc_to_ut1"](jd_utc))
            provider_policy = api["paran_policy_preset"](
                layer_policy["parans"]["policy_preset"]
            )
        except Exception as exc:
            raise AstronomyBackendNotEvaluableError(
                "No se pudo preparar la escala temporal/política de parans."
            ) from exc

        bodies = [*PARAN_PLANET_BODIES, *canon_names]
        reader_scope = self._reader_scope()
        try:
            with reader_scope:
                raw_parans = api["find_parans"](
                    bodies,
                    jd_day_ut1,
                    float(request.latitude),
                    float(request.longitude),
                    orb_minutes=float(
                        layer_policy["parans"]["orb_minutes"]
                    ),
                    policy=provider_policy,
                )
                raw_contacts = api["natal_angular_contacts"](
                    canon_names,
                    natal_jd_ut1,
                    float(request.latitude),
                    float(request.longitude),
                    orb_minutes=float(
                        layer_policy["natal_angular_contacts"][
                            "orb_minutes"
                        ]
                    ),
                )
        except Exception as exc:
            raise AstronomyBackendNotEvaluableError(
                "Moira no pudo calcular parans/contactos angulares."
            ) from exc

        if not isinstance(raw_parans, (list, tuple)) or not isinstance(
            raw_contacts, (list, tuple)
        ):
            raise AstronomyBackendNotEvaluableError(
                "Moira devolvió colecciones de parans/contactos inválidas."
            )

        parans: list[dict[str, Any]] = []
        allowed_bodies = set(PARAN_PLANET_BODIES) | set(canon_names)
        circles = {
            "Rising", "Setting", "Culminating", "AntiCulminating"
        }
        for item in raw_parans:
            signature = _value(item, "signature")
            body_family = str(
                _value(signature, "body_family", "")
            )
            if body_family != "planet-star":
                raise AstronomyBackendNotEvaluableError(
                    "El preset star_planet_only devolvió un paran "
                    f"fuera de contrato: {body_family or 'UNKNOWN'}."
                )
            body1 = str(_value(item, "body1", ""))
            body2 = str(_value(item, "body2", ""))
            circle1 = str(_value(item, "circle1", ""))
            circle2 = str(_value(item, "circle2", ""))
            jd1 = _value(item, "jd1")
            jd2 = _value(item, "jd2")
            orb_min = _value(item, "orb_min")
            if (
                body1 not in allowed_bodies
                or body2 not in allowed_bodies
                or body1 == body2
                or not ({body1, body2} & set(canon_names))
                or not ({body1, body2} & set(PARAN_PLANET_BODIES))
                or circle1 not in circles
                or circle2 not in circles
                or any(
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not isfinite(float(value))
                    for value in (jd1, jd2, orb_min)
                )
                or float(orb_min) < 0.0
                or float(orb_min)
                > float(layer_policy["parans"]["orb_minutes"])
            ):
                raise AstronomyBackendNotEvaluableError(
                    "Moira devolvió un paran con campos fuera del contrato."
                )
            parans.append(
                {
                    "body1": body1,
                    "body2": body2,
                    "circle1": circle1,
                    "circle2": circle2,
                    "jd1": float(jd1),
                    "jd2": float(jd2),
                    "orb_min": float(orb_min),
                    "signature": _provider_jsonable(signature),
                }
            )

        contacts: list[dict[str, Any]] = []
        for item in raw_contacts:
            body = str(_value(item, "body", ""))
            body_family = str(_value(item, "body_family", ""))
            circle = str(_value(item, "circle", ""))
            crossing_jd = _value(item, "crossing_jd")
            contact_jd = _value(item, "natal_jd")
            delta_minutes = _value(item, "delta_minutes")
            absolute_delta = _value(item, "absolute_delta_minutes")
            if (
                body not in set(canon_names)
                or body_family != "star"
                or circle not in circles
                or any(
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not isfinite(float(value))
                    for value in (
                        crossing_jd,
                        contact_jd,
                        delta_minutes,
                        absolute_delta,
                    )
                )
                or abs(
                    abs(float(delta_minutes)) - float(absolute_delta)
                ) > 1e-6
                or float(absolute_delta)
                > float(layer_policy["natal_angular_contacts"]["orb_minutes"])
            ):
                raise AstronomyBackendNotEvaluableError(
                    "Moira devolvió un contacto angular fuera de contrato."
                )
            contacts.append(
                {
                    "body": body,
                    "body_family": body_family,
                    "circle": circle,
                    "crossing_jd": float(crossing_jd),
                    "natal_jd": float(contact_jd),
                    "delta_minutes": float(delta_minutes),
                    "absolute_delta_minutes": float(absolute_delta),
                }
            )

        return {
            "subject_id": request.subject_id,
            "layer_id": "FIXED_STARS_PARANS",
            "schema_version": "1.0.0",
            "status": "CALCULATED",
            "structural_role": "SUPPORT_ONLY",
            "policy_id": layer_policy["policy_id"],
            "policy_fingerprint_sha256": policy_fingerprint,
            "method_source_ids": list(layer_policy["method_source_ids"]),
            "backend_id": self.backend_id,
            "backend_version": self.backend_version,
            "backend_provenance": self.provenance,
            "canon": {
                "selection": layer_policy["star_canon"]["selection"],
                "returned_count": len(canon_entries),
                "fingerprint_sha256": canon_fingerprint,
                "entries": canon_entries,
            },
            "fixed_stars": fixed_stars,
            "parans": parans,
            "natal_angular_contacts": contacts,
            "metadata": {
                "utc_instant": instant.isoformat(),
                "jd_utc": jd_utc,
                "jd_day_ut1": jd_day_ut1,
                "natal_jd_ut1": natal_jd_ut1,
                "latitude": float(request.latitude),
                "longitude": float(request.longitude),
                "paran_policy_preset": layer_policy["parans"][
                    "policy_preset"
                ],
                "paran_orb_minutes": float(
                    layer_policy["parans"]["orb_minutes"]
                ),
                "angular_contact_orb_minutes": float(
                    layer_policy["natal_angular_contacts"][
                        "orb_minutes"
                    ]
                ),
                "network_io_used": False,
                "geocoding_used": False,
                "paran_day_basis": "UT_CALENDAR_DAY",
            },
        }

    def calculate_davison(self, request: DavisonRequest) -> Mapping[str, Any]:
        a = request.subject_a
        b = request.subject_b
        if (
            a.latitude is None
            or a.longitude is None
            or b.latitude is None
            or b.longitude is None
        ):
            raise AstronomyBackendNotEvaluableError(
                "Davison requiere coordenadas numéricas de ambos sujetos."
            )

        policy = request.policy
        if policy.get("time_midpoint") != "UTC_INSTANT":
            raise AstronomyBackendNotEvaluableError(
                "Davison v1 requiere time_midpoint=UTC_INSTANT."
            )
        geo_mode = policy.get("geographic_midpoint")
        if geo_mode not in {
            "BACKEND_DECLARED",
            "SPHERICAL_GREAT_CIRCLE",
        }:
            raise AstronomyBackendNotEvaluableError(
                "Davison v1 requiere geographic_midpoint "
                "BACKEND_DECLARED o SPHERICAL_GREAT_CIRCLE."
            )

        instant_a = _strict_utc(a)
        instant_b = _strict_utc(b)
        midpoint = instant_a + (instant_b - instant_a) / 2
        mid_lat, mid_lon = _spherical_midpoint(
            a.latitude,
            a.longitude,
            b.latitude,
            b.longitude,
        )
        result = self._calculate_at(
            midpoint,
            latitude=mid_lat,
            longitude=mid_lon,
            subject_id=f"DAVISON:{a.subject_id}:{b.subject_id}",
        )
        result["subject_ids"] = [a.subject_id, b.subject_id]
        result["davison"] = {
            "time_midpoint": "UTC_INSTANT",
            "geographic_midpoint": "SPHERICAL_GREAT_CIRCLE",
            "midpoint_utc": midpoint.isoformat(),
            "midpoint_latitude": mid_lat,
            "midpoint_longitude": mid_lon,
        }
        return result
