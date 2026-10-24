"""Offline readiness verification never opens a natal or downloads ephemerides."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest
from importlib import metadata

WEB = Path(__file__).resolve().parent
sys.path.insert(0,str(WEB))
from local_astronomy_preflight import assess_local_astronomy_runtime, LocalAstronomyNotReady

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.kernel=Path(self.directory.name)/"synthetic-not-an-actual-ephemeris.bsp"
        self.kernel.write_bytes(b"SYNTHETIC_FOR_HASH_TESTS_ONLY")
        self.digest=sha256(self.kernel.read_bytes()).hexdigest()
    def tearDown(self):
        self.directory.cleanup()
    def check(self, **overrides):
        args=dict(kernel_path=self.kernel,kernel_sha256=self.digest,
                  kernel_family="DE440",house_system="PLACIDUS",
                  provider_version=lambda name: "6.8.2")
        args.update(overrides)
        return assess_local_astronomy_runtime(**args)
    def test_checksum_and_provider_contract_pass_with_synthetic_bytes(self):
        # This test checks only the preflight control, NEVER astronomical validity.
        receipt=self.check()
        self.assertEqual(receipt["state"],"LOCAL_RUNTIME_READY")
        self.assertEqual(receipt["external_golden_gate"],"NOT_VERIFIED_BY_THIS_PREFLIGHT")
        self.assertNotIn("kernel_path",receipt)
        self.assertNotIn("birth_date",receipt)
    def test_missing_bad_digest_and_invalid_policy_refused(self):
        for overrides, code in [
          (dict(kernel_path=Path(self.directory.name)/"absent"),"KERNEL_FILE_NOT_FOUND"),
          (dict(kernel_sha256="0"*64),"KERNEL_SHA256_MISMATCH"),
          (dict(kernel_sha256="invalid"),"KERNEL_SHA256_INVALID"),
          (dict(kernel_family="DE999"),"UNSUPPORTED_KERNEL_FAMILY"),
          (dict(house_system="KOCH"),"HOUSE_SYSTEM_NOT_CERTIFIED_BY_GOLDEN_GATE"),
          (dict(provider_version=lambda name:"6.8.1"),"MOIRA_VERSION_MISMATCH"),
        ]:
          with self.subTest(code=code),self.assertRaisesRegex(LocalAstronomyNotReady,code):
            self.check(**overrides)
    def test_missing_dependency_fails_closed(self):
        def unavailable(_name):
            raise metadata.PackageNotFoundError("moira-astro")
        with self.assertRaisesRegex(LocalAstronomyNotReady,"MOIRA_MISSING"):
            self.check(provider_version=unavailable)
