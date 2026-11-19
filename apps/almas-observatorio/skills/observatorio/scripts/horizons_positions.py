"""Fetch apparent geocentric ecliptic-of-date positions; Python standard library only."""
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import urllib.parse
import urllib.request

API = 'https://ssd.jpl.nasa.gov/api/horizons.api'
CORE = {2060: 'Chiron', 2847: 'Parvati', 1170: 'Siva', 4227: 'Kaali',
        3811: 'Karma', 3: 'Juno', 16: 'Psyche', 433: 'Eros'}


def angle_delta(a, b):
    return (a - b + 180) % 360 - 180


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('An explicit UTC offset is required')
    return result.astimezone(timezone.utc)


def query(number, at):
    # One-day sampling at one-hour steps includes yesterday, today and t +/- 1 h.
    start = at - timedelta(hours=25)
    return {'format': 'json', 'COMMAND': f"'{number};'", 'OBJ_DATA': "'YES'",
            'MAKE_EPHEM': "'YES'", 'EPHEM_TYPE': "'OBSERVER'", 'CENTER': "'500@399'",
            'START_TIME': "'" + start.strftime('%Y-%m-%d %H:%M:%S') + "'",
            'STOP_TIME': "'" + (at + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S') + "'",
            'STEP_SIZE': "'1 h'", 'QUANTITIES': "'31'", 'CSV_FORMAT': "'YES'",
            'EXTRA_PREC': "'YES'", 'TIME_DIGITS': "'SECONDS'", 'CAL_FORMAT': "'CAL'",
            'TIME_TYPE': "'UT'", 'APPARENT': "'AIRLESS'"}


def parse(payload, number, name=None):
    doc = json.loads(payload)
    if doc.get('error'):
        raise ValueError('Horizons: ' + str(doc['error'])[:400])
    result = doc.get('result', '')
    target = re.search(r'Target body name:\s*([^\r\n]+)', result)
    if not target or not re.match(rf'{number}\s+\S', target.group(1)):
        raise ValueError('Target number not confirmed in response')
    if name and not re.search(rf'\b{re.escape(name)}\b', target.group(1), re.I):
        raise ValueError('Target name mismatch')
    if not re.search(r'Center body name:\s*Earth\s*\(399\)', result):
        raise ValueError('Earth center not confirmed')
    if not re.search(r'Center-site name:\s*(?:GEOCENTRIC|BODY CENTER)\s*(?:\r?\n|$)', result):
        raise ValueError('Geocentric site not confirmed')
    if not re.search(r'Atmos refraction:\s*NO \(AIRLESS\)', result):
        raise ValueError('Airless apparent convention not confirmed')
    if '$$SOE' not in result or '$$EOE' not in result:
        raise ValueError('Ephemeris delimiters missing')
    head, rest = result.split('$$SOE', 1)
    header = next((line for line in reversed(head.splitlines())
                   if 'ObsEcLon' in line and 'ObsEcLat' in line), None)
    if not header or 'Date__(UT)' not in header:
        raise ValueError('UT ecliptic columns not confirmed')
    columns = [c.strip() for c in next(csv.reader([header]))]
    lon_i, lat_i = columns.index('ObsEcLon'), columns.index('ObsEcLat')
    rows = {}
    for row in csv.reader(io.StringIO(rest.split('$$EOE', 1)[0])):
        if not row or not row[0].strip():
            continue
        stamp = row[0].strip().removeprefix('A.D. ')
        dt = datetime.strptime(stamp, '%Y-%b-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        lon, lat = float(row[lon_i]), float(row[lat_i])
        if not math.isfinite(lon) or not math.isfinite(lat) or not 0 <= lon < 360 or abs(lat) > 90:
            raise ValueError('Invalid coordinates')
        if dt in rows:
            raise ValueError('Duplicate epoch')
        rows[dt] = (lon, lat)
    return rows, target.group(1).strip(), doc.get('signature', {})


def validate_samples(payload, number, at):
    parsed = parse(payload, number, CORE.get(number))
    if any(at + timedelta(hours=h) not in parsed[0] for h in (-25, -24, -23, -1, 0, 1)):
        raise ValueError('Requested epochs missing; do not substitute another hour')
    return parsed


def fetch(number, at, cache, timeout):
    params = query(number, at)
    url = API + '?' + urllib.parse.urlencode(params)
    key = hashlib.sha256(url.encode()).hexdigest()
    raw_path = cache / (key + '.json')
    errors = []
    raw = None
    if raw_path.exists():
        try:
            candidate = raw_path.read_bytes()
            validate_samples(candidate, number, at)
            raw = candidate
        except (ValueError, KeyError, IndexError) as exc:
            errors.append('Rejected cache: ' + str(exc))
    if raw is None:
        # One bounded attempt; orchestrator must change route after failure.
        with urllib.request.urlopen(url, timeout=timeout) as response:
            raw = response.read(4_000_001)
            if len(raw) > 4_000_000:
                raise ValueError('Response exceeds limit')
        validate_samples(raw, number, at)
        raw_path.write_bytes(raw)
    rows, target, signature = validate_samples(raw, number, at)
    required = [at - timedelta(days=1), at - timedelta(hours=1), at, at + timedelta(hours=1)]
    if any(t not in rows for t in required):
        raise ValueError('Requested epochs missing; do not substitute another hour')
    speed = angle_delta(rows[required[3]][0], rows[required[1]][0]) * 12
    return {'number': number, 'target': target, 'status': 'VERIFIED',
            'at_utc': at.isoformat(), 'longitude_deg': rows[at][0],
            'latitude_deg': rows[at][1], 'yesterday_longitude_deg': rows[required[0]][0],
            'speed_deg_per_day': speed,
            'yesterday_speed_deg_per_day': angle_delta(rows[at - timedelta(hours=23)][0], rows[at - timedelta(hours=25)][0]) * 12, 'speed_method': 'central difference +/- 1 hour',
            'frame': 'geocentric apparent IAU76/80 ecliptic of date, airless, quantity 31',
            'precision_note': 'Printed precision is not accuracy; validate cross-provider differences.',
            'source': url, 'signature': signature, 'raw_file': str(raw_path),
            'sha256': hashlib.sha256(raw).hexdigest(), 'incidents': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--at', required=True)
    parser.add_argument('--bodies', default=','.join(map(str, CORE)))
    parser.add_argument('--cache', required=True, type=Path)
    parser.add_argument('--timeout', type=float, default=15)
    args = parser.parse_args()
    at = utc(args.at)
    if at.microsecond:
        parser.error('Use whole seconds')
    numbers = list(dict.fromkeys(int(n.strip()) for n in args.bodies.split(',')))
    if not numbers or any(n <= 0 for n in numbers):
        parser.error('Use positive numbered small bodies')
    args.cache.mkdir(parents=True, exist_ok=True)
    results = []
    for number in numbers:
        try:
            results.append(fetch(number, at, args.cache, args.timeout))
        except Exception as exc:
            results.append({'number': number, 'status': 'UNAVAILABLE',
                            'at_utc': at.isoformat(),
                            'source': API + '?' + urllib.parse.urlencode(query(number, at)),
                            'requested_system': 'Earth geocenter, apparent ecliptic of date, airless',
                            'error': type(exc).__name__ + ': ' + str(exc)[:500]})
    count = sum(r['status'] == 'VERIFIED' for r in results)
    print(json.dumps({'at_utc': at.isoformat(), 'coverage': f'{count}/{len(results)}',
                      'complete': count == len(results), 'bodies': results}, ensure_ascii=False, indent=2))
    return 0 if count == len(results) else 2


if __name__ == '__main__':
    raise SystemExit(main())
