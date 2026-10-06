"""Oráculo congelado exclusivo de tests: mismas matemáticas, sin tolerancias ocultas."""
from copy import deepcopy
import hashlib
import importlib.machinery
import importlib.util
from pathlib import Path
import random
import unittest
from almas_tfa.atacires import engine
from almas_tfa.atacires.providers import EphemerisProvider
from test_atacires_upstream import request
from test_atacires_integration import ctx, settings
from almas_tfa.integrations.atacires_temporal import make_atacires_temporal_handler
from almas_tfa.temporal_handlers import m26_temporal_activation

FIXTURE=Path(__file__).parent/'fixtures/atacires/upstream_engine.py.txt'
loader=importlib.machinery.SourceFileLoader('atacires_frozen_oracle',str(FIXTURE))
spec=importlib.util.spec_from_loader(loader.name,loader)
oracle=importlib.util.module_from_spec(spec);loader.exec_module(oracle)

class DifferentialTests(unittest.TestCase):
    def test_frozen_oracle_matches_imported_bytes(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest())
    def test_one_hundred_seeded_uniform_cases_exact(self):
        rng=random.Random(20261006)
        for index in range(100):
            data=request(natal_points={'P':rng.random()*360,'S':rng.random()*360},
                         cycle_years=rng.choice([.5,1,5,12,60,360]),direction=rng.choice(['direct','converse']),
                         aspects_deg=rng.sample([0,30,60,90,120,150,180],rng.randint(1,7)),orb_deg=rng.random()*2)
            with self.subTest(index=index):self.assertEqual(engine.calculate(deepcopy(data)),oracle.calculate(deepcopy(data)))
    def test_synthetic_provider_matches_protocol_without_swiss(self):
        class FakeProvider:
            backend_id='FAKE';backend_version='1';provenance={'fixture':True}
            def calculate_transit_positions(self,instant_utc):return {'positions':{'SUN':{'longitude':10}}}
        self.assertIsInstance(FakeProvider(),EphemerisProvider)
        self.assertFalse(isinstance(object(),EphemerisProvider))
    def test_multiple_aspects_pass_numbers_per_contact_not_global(self):
        context=ctx({'atacires_requests':[{'subject_id':'A','settings':settings(aspects_deg=[0,90])}]})
        signals=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']['signals']
        first={}
        for s in signals:first.setdefault((s['source_point'],s['target_point'],s['oriented_aspect_deg']),s['pass_number'])
        self.assertTrue(all(n==1 for n in first.values()))
    def test_dependency_cluster_uses_existing_policy(self):
        from almas_tfa.temporal_dependency import FAMILY_CLUSTERS
        signal=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(ctx()).canonical_updates['atacires_shadow']['signals'][0]
        self.assertEqual(signal['dependency_cluster'],FAMILY_CLUSTERS['TATACIR'])
