#!/usr/bin/env python3
"""Calculate public asteroid ephemerides; never publish private birth/chart data.

Source: Swiss Ephemeris short asteroid files (1500–2100), tropical geocentric
apparent longitudes at 09:00 UTC for requested civil day and previous day.
Includes mandatory Chiron (2060) from seas_18.se1. No Moshier fallback is\naccepted, and partial results are never published.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

import swisseph as swe

ASTEROIDS = {
    2847: "Parvati", 1170: "Siva", 4227: "Kaali", 3811: "Karma",
    3: "Juno", 16: "Psyche", 433: "Eros", 42: "Isis",
    1923: "Osiris", 1221: "Amor", 1585: "Union",
    447: "Valentine", 763: "Cupido", 399: "Persephone",
    6583: "Destinn",
}
PRIORITY = (2847, 1170, 4227, 3811, 3, 16, 433)
MIRRORS = ("https://ephe.scryr.io/ephe", "https://www.astro.com/ftp/swisseph/ephe")
STANDARD = ("sepl_18.se1", "semo_18.se1", "seas_18.se1")


def asteroid_file(number: int) -> str:
    return f"ast{number // 1000}/se{number:05d}s.se1"


def obtain(relative: str, cache: Path) -> dict:
    target = cache / relative
    if target.is_file() and target.stat().st_size > 1024:
        raw = target.read_bytes()
        return {"path": relative, "source": "local_cache", "sha256": hashlib.sha256(raw).hexdigest()}
    problems = []
    for base in MIRRORS:
        url = f"{base}/{relative}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "ALMAS-public-ephemerides/1.0"}), timeout=35) as response:
                raw = response.read(5_000_000)
            if len(raw) <= 1024 or raw[:500].lstrip().lower().startswith((b"<!doctype", b"<html")):
                raise ValueError("response is not a valid ephemeris binary")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            return {"path": relative, "source": url, "sha256": hashlib.sha256(raw).hexdigest()}
        except Exception as exc:
            problems.append(f"{url}: {type(exc).__name__} {exc}")
    raise RuntimeError(f"Failed {relative}: " + " | ".join(problems))


def position(number: int, day: date) -> dict:
    jd_ut = swe.julday(day.year, day.month, day.day, 9.0, swe.GREG_CAL)
    body = swe.JUNO if number == 3 else swe.AST_OFFSET + number
    requested = swe.FLG_SWIEPH | swe.FLG_SPEED
    xx, returned = swe.calc_ut(jd_ut, body, requested)
    if not (returned & swe.FLG_SWIEPH):
        raise RuntimeError(f"Object {number}: Swiss calculation unavailable, flags={returned}")
    longitude, latitude, distance, speed = xx[:4]
    if not (0 <= longitude < 360 and -90 <= latitude <= 90):
        raise ValueError(f"Object {number}: invalid longitude/latitude")
    return {
        "longitude_deg": round(longitude, 8),
        "latitude_deg": round(latitude, 8),
        "distance_au": round(distance, 10),
        "speed_deg_per_day": round(speed, 8),
        "motion": "R" if speed < -1e-7 else "D" if speed > 1e-7 else "STATIONARY_SPEED_THRESHOLD",
        "flags_requested": requested,
        "flags_returned": returned,
    }


def chiron_position(day: date) -> dict:
    """Chiron is a built-in Swiss Ephemeris body (2060), not a generic asteroid ID.

    The bundled seas_18.se1 contains its orbital data for the 2026 reference.
    Reject fallback to Moshier exactly as for the numbered asteroids.
    """
    jd_ut = swe.julday(day.year, day.month, day.day, 9.0, swe.GREG_CAL)
    requested = swe.FLG_SWIEPH | swe.FLG_SPEED
    xx, returned = swe.calc_ut(jd_ut, swe.CHIRON, requested)
    if not (returned & swe.FLG_SWIEPH):
        raise RuntimeError(f"Chiron 2060: Swiss calculation unavailable, flags={returned}")
    longitude, latitude, distance, speed = xx[:4]
    if not (0 <= longitude < 360 and -90 <= latitude <= 90):
        raise ValueError("Chiron 2060: invalid longitude/latitude")
    return {
        "longitude_deg": round(longitude, 8),
        "latitude_deg": round(latitude, 8),
        "distance_au": round(distance, 10),
        "speed_deg_per_day": round(speed, 8),
        "motion": "R" if speed < -1e-7 else "D" if speed > 1e-7 else "STATIONARY_SPEED_THRESHOLD",
        "flags_requested": requested,
        "flags_returned": returned,
    }


def calculate(day: date, cache: Path) -> dict:
    files = {}
    missing = {}
    required = list(STANDARD) + [asteroid_file(n) for n in ASTEROIDS if n != 3]
    for name in required:
        try:
            files[name] = obtain(name, cache)
        except Exception as exc:
            missing[name] = str(exc)
    if missing:
        raise RuntimeError("NO_PUBLICATION missing sources: " + json.dumps(missing, ensure_ascii=False))
    swe.set_ephe_path(str(cache.resolve()))
    dates = (day - timedelta(days=1), day)
    bodies = {}
    for number, name in ASTEROIDS.items():
        try:
            bodies[str(number)] = {
                "name": name,
                "positions": {d.isoformat(): position(number, d) for d in dates},
            }
        except Exception as exc:
            missing[str(number)] = str(exc)
    chiron = None
    try:
        chiron = {
            "number": 2060,
            "name": "Chiron",
            "source_file": "seas_18.se1",
            "positions": {d.isoformat(): chiron_position(d) for d in dates},
        }
    except Exception as exc:
        missing["chiron_2060"] = str(exc)
    if missing or chiron is None or not all(str(n) in bodies for n in PRIORITY):
        raise RuntimeError("NO_PUBLICATION calculation errors: " + json.dumps(missing, ensure_ascii=False))
    return {
        "schema_version": "1.1",
        "reference_day_utc": day.isoformat(),
        "reference_time_utc": "09:00:00",
        "checked_days": [d.isoformat() for d in dates],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "engine": f"pyswisseph {swe.version}",
        "frame": "tropical geocentric apparent ecliptic of date (not topocentric)",
        "primary_ids": list(PRIORITY),
        "verified_complete": True,
        "files": files,
        "asteroids": bodies,
        "chiron": chiron,
        "privacy": "Public ephemerides only: no natal data, charts or relational interpretation",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--cache", default=".ephemeris-files")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    day = date.fromisoformat(args.date)
    result = calculate(day, Path(args.cache))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(f"VERIFIED {day.isoformat()} ({len(ASTEROIDS)} asteroids + Chiron) -> {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ALMAS ASTEROID EPHEMERIS ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
