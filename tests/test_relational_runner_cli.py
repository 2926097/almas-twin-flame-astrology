import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_relational_work_request as runner


class RelationalRunnerCliTests(unittest.TestCase):
    def test_reused_output_dir_does_not_keep_stale_canonical(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            request_path = root / "request.json"
            manifest_path = root / "manifest.json"
            output_dir = root / "output"
            output_dir.mkdir()
            canonical_path = output_dir / "canonical_analysis.json"
            canonical_path.write_text(
                json.dumps({"request": "previous"}),
                encoding="utf-8",
            )
            request_path.write_text("{}", encoding="utf-8")
            manifest_path.write_text("{}", encoding="utf-8")
            receipt = {"failed_modules": []}
            result = {
                "raw_input": {},
                "orchestration_run": {},
                "execution_receipt": receipt,
                "canonical_analysis": None,
            }
            argv = [
                "run_relational_work_request.py",
                str(request_path),
                "--output-dir", str(output_dir),
                "--manifest", str(manifest_path),
                "--kernel-path", str(root / "kernel.bsp"),
                "--kernel-sha256", "0" * 64,
                "--kernel-family", "DE440",
                "--house-system", "P",
            ]
            with (
                patch("sys.argv", argv),
                patch.object(
                    runner,
                    "assess_relational_work_request",
                    return_value={"ready_for_raw_input": True},
                ),
                patch.object(
                    runner,
                    "execute_relational_work_request",
                    return_value=result,
                ),
                patch.object(runner, "MoiraProductionBackend"),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                exit_code = runner.main()

            self.assertEqual(exit_code, 4)
            self.assertFalse(canonical_path.exists())

    def test_runner_guide_has_real_markdown_structure_and_private_contract(self):
        guide = (
            Path(__file__).resolve().parents[1]
            / "reference"
            / "private-relational-runner.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn(r"\n", guide)
        self.assertGreaterEqual(guide.count("\n## "), 4)
        self.assertIn("canonical_analysis.json", guide)
        self.assertIn("canonical_reconstructed_outside_pipeline=false", guide)
        self.assertIn("case_published_by_runner=false", guide)
        self.assertIn("Si M30 no lo produce", guide)


if __name__ == "__main__":
    unittest.main()
