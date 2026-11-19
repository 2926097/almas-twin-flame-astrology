"""Offline regression tests; synthetic fixtures are not astronomical evidence."""
import json
from datetime import timedelta
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import horizons_positions as h


def fixture(number=2847, name='Parvati', center='Earth (399)', site='GEOCENTRIC'):
    at = h.utc('2026-10-31T09:00:00Z')
    lines = []
    for hours, lon in [(-25, 358.99), (-24, 359), (-23, 359.01), (-1, 359.99), (0, 0), (1, 0.01)]:
        stamp = (at + timedelta(hours=hours)).strftime('%Y-%b-%d %H:%M:%S')
        lines.append(f'{stamp}, , , {lon}, 1.0,')
    text = (f'Target body name: {number} {name} (fixture)\nCenter body name: {center}\n'
            f'Center-site name: {site}\nAtmos refraction: NO (AIRLESS)\nDate__(UT)__HR:MN:SS, , , ObsEcLon, ObsEcLat,\n'
            '$$SOE\n' + '\n'.join(lines) + '\n$$EOE')
    return json.dumps({'result': text, 'signature': {'version': 'fixture'}}).encode()


class RecoveryTests(unittest.TestCase):
    def test_parse(self):
        rows, target, _ = h.parse(fixture(), 2847, 'Parvati')
        self.assertEqual(len(rows), 6)
        self.assertIn('Parvati', target)

    def test_html_200_rejected(self):
        with self.assertRaises(ValueError):
            h.parse(b'<html>HTTP 200 login</html>', 2847)

    def test_ambiguous_response_rejected(self):
        with self.assertRaises(ValueError):
            h.parse(json.dumps({'result': 'Multiple matches found'}), 2847)

    def test_wrong_identity_rejected(self):
        with self.assertRaises(ValueError):
            h.parse(fixture(number=2060), 2847)
        with self.assertRaises(ValueError):
            h.parse(fixture(name='Other'), 2847, 'Parvati')

    def test_wrong_center_rejected(self):
        for data in [fixture(center='Sun (10)'), fixture(site='Observatory')]:
            with self.assertRaises(ValueError):
                h.parse(data, 2847)

    def test_wrap_and_cache(self):
        at = h.utc('2026-10-31T09:00:00Z')
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            url = h.API + '?' + h.urllib.parse.urlencode(h.query(2847, at))
            key = h.hashlib.sha256(url.encode()).hexdigest()
            (cache / (key + '.json')).write_bytes(fixture())
            with patch.object(h.urllib.request, 'urlopen', side_effect=AssertionError('network')):
                result = h.fetch(2847, at, cache, 1)
            self.assertAlmostEqual(result['speed_deg_per_day'], .24)
            self.assertAlmostEqual(result['yesterday_speed_deg_per_day'], .24)
            with self.assertRaisesRegex(ValueError, 'epochs missing'):
                # This fixture was deliberately stored for another requested hour.
                at2 = at + timedelta(minutes=1)
                url2 = h.API + '?' + h.urllib.parse.urlencode(h.query(2847, at2))
                key2 = h.hashlib.sha256(url2.encode()).hexdigest()
                (cache / (key2 + '.json')).write_bytes(fixture())
                with patch.object(h.urllib.request, 'urlopen') as network:
                    network.return_value.__enter__.return_value.read.return_value = fixture()
                    h.fetch(2847, at2, cache, 1)

    def test_no_offset_rejected(self):
        with self.assertRaises(ValueError):
            h.utc('2026-10-31T09:00:00')

    def test_reject_nan(self):
        with self.assertRaises(ValueError):
            h.parse(fixture().replace(b'359,', b'NaN,'), 2847)


if __name__ == '__main__':
    unittest.main()
