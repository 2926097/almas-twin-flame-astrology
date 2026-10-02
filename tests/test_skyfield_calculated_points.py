from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from almas_tfa.skyfield_calculated_points import CalculatedPointInputConfig,SkyfieldCalculatedPointInputs


class SkyfieldCalculatedInputTests(unittest.TestCase):
    def test_config_requires_de440_and_explicit_sha256(self):
        for family,sha in (('DE441','0'*64),('DE440','unknown'),('DE440','X'*64)):
            with self.assertRaises(ValueError):CalculatedPointInputConfig('unused',sha,family)

    def test_unpinned_provider_version_rejected_before_file_or_network(self):
        with patch('almas_tfa.skyfield_calculated_points.metadata.version',return_value='9.9'):
            with self.assertRaises(RuntimeError):SkyfieldCalculatedPointInputs(CalculatedPointInputConfig('missing','0'*64))

    def test_missing_kernel_is_explicit_and_never_downloaded(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'absent.bsp'
            with patch('almas_tfa.skyfield_calculated_points.metadata.version',return_value='1.55'):
                with self.assertRaises(FileNotFoundError):SkyfieldCalculatedPointInputs(CalculatedPointInputConfig(str(path),'0'*64))
            self.assertFalse(path.exists())

    def test_checksum_mismatch_rejected_before_loading_astronomical_data(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'wrong.bsp';path.write_bytes(b'synthetic:invalid-kernel')
            with patch('almas_tfa.skyfield_calculated_points.metadata.version',return_value='1.55'):
                with self.assertRaisesRegex(ValueError,'KERNEL_SHA256_MISMATCH'):
                    SkyfieldCalculatedPointInputs(CalculatedPointInputConfig(str(path),'0'*64))
