"""Deterministic C-N geometry from supplied natal longitudes. Standard library only."""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.resources
import json
import math
from pathlib import Path
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, TZPATH

VERSION = "0.3.1"
UTC = timezone.utc
MAX_EVENTS = 10000

class InputError(ValueError):
    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code, self.details = code, details or {}

def number(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError("INVALID_NUMBER", f"{name}: se requiere número finito")
    value = float(value)
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise InputError("INVALID_NUMBER", f"{name}: fuera de rango [{minimum}, {maximum}]")
    return value

def norm360(value):
    return value % 360.0

def wrap180(value):
    return (value + 180.0) % 360.0 - 180.0

def zone(key):
    if not isinstance(key, str) or not key:
        raise InputError("INVALID_TIMEZONE", "Se requiere zona IANA")
    try:
        return ZoneInfo(key)
    except (ZoneInfoNotFoundError, ValueError):
        raise InputError("INVALID_TIMEZONE", f"Zona IANA desconocida: {key}") from None

def zone_provenance(key):
    # Follow the same ordered data search used by ZoneInfo; hash actual TZif bytes.
    for root in TZPATH:
        path = Path(root) / key
        if path.is_file():
            version = "unknown"
            manifest = Path(root) / "tzdata.zi"
            if manifest.is_file():
                with manifest.open(encoding="utf-8") as handle:
                    first = handle.readline().strip()
                if first.startswith("# version "):
                    version = first.removeprefix("# version ")
            return {"provider": "system_zoneinfo", "version": version,
                    "tzif_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    import tzdata
    resource = importlib.resources.files("tzdata.zoneinfo").joinpath(*key.split("/"))
    return {"provider": "python_tzdata", "version": tzdata.__version__,
            "tzif_sha256": hashlib.sha256(resource.read_bytes()).hexdigest()}

def parse_datetime(value, label):
    if not isinstance(value, str) or "T" not in value:
        raise InputError("INVALID_DATETIME", f"{label}: usar fecha y hora ISO 8601 completa")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise InputError("INVALID_DATETIME", f"{label}: fecha/hora no válida") from None

def utc_datetime(value, label):
    dt = parse_datetime(value, label)
    if dt.tzinfo is None:
        raise InputError("TIMEZONE_REQUIRED", f"{label}: incluir Z o desplazamiento UTC explícito")
    return dt.astimezone(UTC)

def local_to_utc(value, key, fold=None):
    dt = parse_datetime(value, "datetime_local")
    if dt.tzinfo is not None:
        raise InputError("OFFSET_NOT_ALLOWED", "datetime_local no debe incluir desplazamiento")
    if fold is not None and (type(fold) is not int or fold not in (0, 1)):
        raise InputError("INVALID_FOLD", "fold debe ser 0 o 1")
    tz = zone(key)
    candidates = {}
    for f in (0, 1):
        candidate = dt.replace(tzinfo=tz, fold=f).astimezone(UTC)
        if candidate.astimezone(tz).replace(tzinfo=None) == dt:
            candidates[f] = candidate
    unique = set(candidates.values())
    if not unique:
        raise InputError("NONEXISTENT_LOCAL_TIME", "La hora local no existió por cambio horario")
    if len(unique) > 1 and fold is None:
        raise InputError("AMBIGUOUS_LOCAL_TIME", "La hora local tiene dos instantes posibles",
                         {"candidates": [{"fold": f, "utc": iso(t)} for f, t in candidates.items()]})
    return candidates[fold if fold is not None else min(candidates)]

def iso(dt):
    return dt.isoformat(timespec="microseconds").replace("+00:00", "Z")

def rotate(points, years_elapsed, cycle_years, direction="direct"):
    if direction not in ("direct", "converse"):
        raise InputError("INVALID_DIRECTION", "direction debe ser direct o converse")
    sign = 1 if direction == "direct" else -1
    return {key: norm360(value + sign * 360.0 * years_elapsed / cycle_years)
            for key, value in points.items()}

def calculate(data):
    if not isinstance(data, dict):
        raise InputError("INVALID_INPUT", "La entrada debe ser un objeto JSON")
    allowed = {"schema_version", "technique", "datetime_local", "timezone_id", "fold",
               "start_utc", "end_utc", "output_timezone", "cycle_years", "year_days", "direction",
               "natal_points", "positions_source", "aspects_deg", "orb_deg", "promissors",
               "significators", "include_self"}
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise InputError("UNKNOWN_FIELDS", "Campos no admitidos; no se ignorarán", {"fields": unknown})
    if data.get("schema_version") != "1.0":
        raise InputError("UNSUPPORTED_SCHEMA", "schema_version debe ser 1.0")
    if data.get("technique") != "UNIFORM_CYCLE":
        raise InputError("UNSUPPORTED_TECHNIQUE", "Esta versión solo implementa UNIFORM_CYCLE")
    birth = local_to_utc(data.get("datetime_local"), data.get("timezone_id"), data.get("fold"))
    start = utc_datetime(data.get("start_utc"), "start_utc")
    end = utc_datetime(data.get("end_utc"), "end_utc")
    if start < birth or end < start:
        raise InputError("INVALID_INTERVAL", "Se requiere nacimiento <= inicio <= fin")
    n = number(data.get("cycle_years"), "cycle_years", 0.0001, 10000)
    y = number(data.get("year_days", 365.2422), "year_days", 360, 366)
    orb = number(data.get("orb_deg", 1), "orb_deg", 0, 179.999999)
    direction = data.get("direction", "direct")
    if direction not in ("direct", "converse"):
        raise InputError("INVALID_DIRECTION", "direction debe ser direct o converse")
    points = data.get("natal_points")
    if not isinstance(points, dict) or not 1 <= len(points) <= 100:
        raise InputError("INVALID_POINTS", "Se requieren entre 1 y 100 posiciones natales")
    if any(not isinstance(k, str) or not k.strip() for k in points):
        raise InputError("INVALID_POINTS", "Cada punto requiere un nombre no vacío")
    points = {k: number(v, k, 0, math.nextafter(360, 0)) for k, v in points.items()}
    source = data.get("positions_source")
    if not isinstance(source, str) or not source.strip():
        raise InputError("POSITIONS_SOURCE_REQUIRED", "Identificar origen de posiciones, por ejemplo PDF y página")
    aspects = data.get("aspects_deg", [0, 60, 90, 120, 180])
    if not isinstance(aspects, list) or not 1 <= len(aspects) <= 20:
        raise InputError("INVALID_ASPECTS", "aspects_deg debe ser lista no vacía, máximo 20")
    aspects = sorted(set(number(a, "aspect", 0, 180) for a in aspects))
    groups = []
    for name in ("promissors", "significators"):
        selected = data.get(name, list(points))
        if (not isinstance(selected, list) or not selected or
                any(not isinstance(k, str) or k not in points for k in selected)):
            raise InputError("INVALID_SELECTION", f"{name}: lista no vacía de puntos conocidos")
        groups.append(list(dict.fromkeys(selected)))
    include_self = data.get("include_self", False)
    if type(include_self) is not bool:
        raise InputError("INVALID_BOOLEAN", "include_self debe ser booleano")
    output_key = data.get("output_timezone", "Europe/Madrid")
    output_zone = zone(output_key)
    velocity = (1 if direction == "direct" else -1) * 360.0 / (n * y)
    age_start = (start - birth).total_seconds() / 86400
    age_end = (end - birth).total_seconds() / 86400
    half_window = orb / abs(velocity)
    hits = []
    for p in groups[0]:
        for s in groups[1]:
            if p == s and not include_self:
                continue
            for aspect in aspects:
                orientations = [aspect] if aspect in (0, 180) else [-aspect, aspect]
                for angle in orientations:
                    lo, hi = sorted((points[p] + velocity * age_start - points[s] - angle,
                                     points[p] + velocity * age_end - points[s] - angle))
                    k_start, k_end = math.ceil(lo / 360 - 1e-12), math.floor(hi / 360 + 1e-12)
                    if len(hits) + max(0, k_end-k_start+1) > MAX_EVENTS:
                        raise InputError("EVENT_LIMIT_EXCEEDED", "Acotar período, puntos, aspectos o ciclo")
                    for k in range(k_start, k_end + 1):
                        days = (points[s] + angle - points[p] + 360 * k) / velocity
                        exact = birth + timedelta(days=days)
                        if not start <= exact <= end:
                            # Round-off at analytical interval endpoints: at most 1 ms.
                            if abs((exact-start).total_seconds()) <= .001:
                                exact = start
                            elif abs((exact-end).total_seconds()) <= .001:
                                exact = end
                            else:
                                continue
                        residual = abs(wrap180(points[p] + velocity * days - points[s] - angle))
                        hits.append({"promissor": p, "significator": s, "aspect_deg": aspect,
                                     "oriented_aspect_deg": angle, "date_exact_utc": iso(exact),
                                     "date_exact_local": iso(exact.astimezone(output_zone)),
                                     "angular_residual_deg": residual,
                                     "window_start_utc": iso(exact-timedelta(days=half_window)),
                                     "window_end_utc": iso(exact+timedelta(days=half_window)),
                                     "window_half_days": half_window})
    hits.sort(key=lambda h: (h["date_exact_utc"], h["promissor"], h["significator"], h["aspect_deg"]))
    warnings = ["SUPPLIED_POSITIONS_NOT_ASTRONOMICALLY_VERIFIED", "NO_EPHEMERIS_USED_IN_SUPPLIED_POSITIONS_MODE",
                "POSIX_CIVIL_TIME_NO_LEAP_SECONDS", "ORB_WINDOWS_ARE_SYMBOLIC_NOT_EVENT_PROBABILITIES"]
    if min(birth.year, start.year, end.year) < 1970:
        warnings.append("HISTORICAL_TIME_REQUIRES_DOCUMENTARY_VERIFICATION")
    warnings.append("TIMEZONE_RULES_BOUND_TO_RECORDED_TZIF")
    provenance = {key: zone_provenance(key) for key in dict.fromkeys([data["timezone_id"], output_key])}
    return {"schema_version": "1.0", "engine_version": VERSION,
            "calculation": {"technique": "UNIFORM_CYCLE", "direction": direction,
                            "cycle_years": n, "year_days": y, "velocity_deg_per_day": velocity,
                            "orb_deg": orb, "aspects_deg": aspects, "include_self": include_self,
                            "solver": "analytical_all_turns", "timescale": "UTC-labelled_POSIX_civil",
                            "ephemeris": None, "timezone_provenance": provenance},
            "input": {"birth_utc": iso(birth), "timezone_id": data["timezone_id"],
                      "start_utc": iso(start), "end_utc": iso(end), "output_timezone": output_key,
                      "natal_points": points, "positions_source": source},
            "directed_positions_start": rotate(points, age_start/y, n, direction),
            "directed_positions_end": rotate(points, age_end/y, n, direction),
            "hits": hits, "warnings": warnings,
            "quality": {"positions": "supplied_not_verified", "interpretative_probability": None}}

def reject_nonfinite(text):
    raise InputError("INVALID_JSON_NUMBER", f"Número JSON no finito: {text}")

def reject_duplicate_keys(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise InputError("DUPLICATE_JSON_KEY", f"Clave JSON duplicada: {k}")
        result[k] = v
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON de entrada o - para stdin")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        data = json.loads(text, parse_constant=reject_nonfinite, object_pairs_hook=reject_duplicate_keys)
        result = calculate(data)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except InputError as err:
        print(json.dumps({"error": {"code": err.code, "message": str(err), "details": err.details}}, ensure_ascii=False))
        return 2
    except (OSError, json.JSONDecodeError, OverflowError) as err:
        print(json.dumps({"error": {"code": "INPUT_OR_RANGE_ERROR", "message": str(err)}}))
        return 2

if __name__ == "__main__":
    sys.exit(main())

