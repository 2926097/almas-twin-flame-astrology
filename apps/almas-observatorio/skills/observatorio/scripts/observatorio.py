"""Procesa el producto público ALMAS y opcionalmente una sola carta de vínculo privada."""
import argparse
import hashlib
import itertools
import json
import math
import re
from datetime import date, timedelta
from pathlib import Path

PLANETS = "sun moon mercury venus mars jupiter saturn uranus neptune pluto true_node".split()
ASTEROIDS = {"2847":"Parvati","1170":"Siva","4227":"Kaali","3811":"Karma","3":"Juno","16":"Psyche","433":"Eros"}
ASPECTS = {0:"conjunción",60:"sextil",90:"cuadratura",120:"trígono",180:"oposición"}
LABELS = dict(zip(PLANETS, "Sol Luna Mercurio Venus Marte Júpiter Saturno Urano Neptuno Plutón Nodo".split()))
FRAME = "tropical geocentric apparent ecliptic of date (not topocentric)"


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate(doc, day):
    days = [(day - timedelta(days=1)).isoformat(), day.isoformat()]
    version = tuple(map(int, str(doc["schema_version"]).split(".")))
    if (version < (1, 2) or doc["verified_complete"] is not True or doc["checked_days"] != days
            or doc["reference_time_utc"] != "09:00:00" or doc["reference_day_utc"] != days[1]
            or doc["frame"] != FRAME or not doc["engine"].startswith("pyswisseph ")):
        raise ValueError("Cabecera, marco o fechas incompatibles")
    chiron = doc["chiron"]
    if chiron["number"] != 2060 or chiron["source_file"] != "seas_18.se1":
        raise ValueError("Identidad o archivo de Quirón")
    sources = {LABELS[key]: doc["planets"][key] for key in PLANETS}
    sources["Quirón"] = chiron["positions"]
    files = ["sepl_18.se1","semo_18.se1","seas_18.se1"]
    for key, name in ASTEROIDS.items():
        entry = doc["asteroids"][key]
        if entry["name"] != name:
            raise ValueError(f"Identidad de {key}")
        sources[name] = entry["positions"]
        if key != "3":
            files.append(f"ast{int(key)//1000}/se{int(key):05d}s.se1")
    for path in files:
        if not re.fullmatch("[a-fA-F0-9]{64}", doc["files"][path]["sha256"]):
            raise ValueError(f"Huella de procedencia ausente en {path}")
    for body, samples in sources.items():
        for d in days:
            p = samples[d]
            lon = p["longitude_deg"]
            if (not number(lon) or not 0 <= lon < 360 or not number(p["speed_deg_per_day"])
                    or p["flags_returned"] != 258):
                raise ValueError(f"{body} {d}: posición, velocidad o flags incompatibles")
    return {d: {body: samples[d] for body, samples in sources.items()} for d in days}


def separation(a, b):
    return abs((a-b+180) % 360 - 180)


def contacts(samples, previous, profile=None):
    pairs = ((a, b, "Tránsito", samples[b], previous[b]) for a,b in itertools.combinations(samples, 2))
    if profile:
        fixed = ((a,b,chart,{"longitude_deg":lon},{"longitude_deg":lon})
                 for a in samples for chart, points in profile["cartas"].items() for b,lon in points.items())
        pairs = itertools.chain(pairs, fixed)
    result = []
    for a,b,chart,target,prior in pairs:
        lon = samples[a]["longitude_deg"]
        dest = target["longitude_deg"]
        dist = separation(lon, dest)
        angle = min(ASPECTS, key=lambda x:abs(dist-x))
        orb = abs(dist-angle)
        limit = 0.5 if a in ASTEROIDS.values() or b in ASTEROIDS.values() else 1
        if orb <= limit:
            result.append(dict(transito=a, receptor=b, carta=chart, longitud=lon, destino=dest,
                               aspecto=ASPECTS[angle], angulo=angle, orbe=round(orb,8),
                               orbe_ayer=round(abs(separation(previous[a]["longitude_deg"],prior["longitude_deg"])-angle),8)))
    return sorted(result,key=lambda row:row["orbe"])


def run(folder, today, profile=None):
    if profile:
        if (not profile.get("vinculo") or not profile.get("version") or not profile.get("cartas")
                or set(profile["cartas"]) - {"Natal A","Natal B","Compuesta","Davison"}):
            raise ValueError("Perfil incompleto o tipo de carta desconocido")
        for points in profile["cartas"].values():
            if not isinstance(points,dict) or not points or not all(number(v) and 0 <= v < 360 for v in points.values()):
                raise ValueError("Longitudes natales inválidas")
    samples, hashes, issues = {}, {}, {}
    for offset in [0,-1,1,-2,2,-3,3,-4,4,-5,5]:
        day = today + timedelta(days=offset)
        path = folder / f"{day}.json"
        try:
            raw = path.read_bytes()
            loaded = validate(json.loads(raw), day)
            for key, positions in loaded.items():
                if key in samples and samples[key] != positions:
                    raise ValueError(f"Discrepancia entre productos en {key}")
        except (OSError, ValueError, KeyError, AttributeError, TypeError) as exc:
            issues[str(day)] = str(exc)
            if not offset:
                return {"estado":"PENDIENTE","incidencias":issues}
            continue
        samples.update(loaded)
        hashes[path.name] = hashlib.sha256(raw).hexdigest()
    window = [str(today+timedelta(days=i)) for i in range(-5,6)]
    yesterday = str(today-timedelta(days=1))
    return dict(estado="VALIDADO_HOY_AYER", fecha=str(today), referencia="09:00 UTC",
                vinculo=profile["vinculo"] if profile else None, version=profile["version"] if profile else None,
                cobertura={d:d in samples for d in window}, archivos_sha256=hashes, incidencias=issues,
                posiciones={d:samples[d] for d in window if d in samples},
                contactos=contacts(samples[str(today)],samples[yesterday],profile))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carpeta", type=Path)
    parser.add_argument("fecha", type=date.fromisoformat)
    parser.add_argument("--perfil", type=Path)
    args = parser.parse_args()
    profile = json.loads(args.perfil.read_text()) if args.perfil else None
    result = run(args.carpeta, args.fecha, profile)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    raise SystemExit(0 if result["estado"] == "VALIDADO_HOY_AYER" else 2)
