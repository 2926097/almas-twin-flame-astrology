import unittest
from unittest.mock import patch

from almas_tfa.module_contract import ExecutionStatus, ModuleResult
from almas_tfa.orchestrator import OrchestrationRun
from almas_tfa.relational_execution import (
    RelationalExecutionError,
    execute_relational_work_request,
)


def manifest():
    return {
        "mode": "FULL",
        "manifest_version": "1.0.0",
        "modules": [
            {"id": f"M{i:02d}", "name": f"module_{i:02d}"}
            for i in range(32)
        ],
    }


def request():
    return {
        "request": {
            "format": "ALMAS_WORK_REQUEST",
            "public_version": "1.25.0",
            "type": "RELATIONAL",
            "analysis_profile": "FULL_ASTROLOGY",
            "analysis_policy_profile": (
                "ALMAS_RELATIONAL_STRICT_RESEARCH_V1"
            ),
            "subjects": [
                {
                    "id": "A",
                    "birth_date": "1977-03-20",
                    "birth_time": "17:45",
                    "timezone": "Europe/Madrid",
                    "latitude": 41.65606,
                    "longitude": -0.87734,
                    "time_reliability": "D",
                },
                {
                    "id": "B",
                    "birth_date": "1991-05-23",
                    "birth_time": "04:15",
                    "timezone": "America/Santo_Domingo",
                    "latitude": 18.4539,
                    "longitude": -69.30864,
                    "time_reliability": "B",
                },
            ],
            "events": [],
            "execution_state": "REQUEST_ONLY",
        }
    }


class Backend:
    backend_id = "TEST_BACKEND"
    backend_version = "1"
    provenance = {
        "backend_id": "TEST_BACKEND",
        "backend_version": "1",
        "kernel_sha256": "0" * 64,
    }


class RelationalExecutionTests(unittest.TestCase):
    def test_backend_is_required(self):
        with self.assertRaisesRegex(
            RelationalExecutionError,
            "astrology_backend",
        ):
            execute_relational_work_request(
                request(),
                manifest(),
                astrology_backend=None,
            )

    @patch("almas_tfa.relational_execution.Orchestrator.run")
    @patch("almas_tfa.relational_execution.configured_handlers")
    def test_canonical_is_returned_only_from_orchestrator(
        self,
        handlers_mock,
        run_mock,
    ):
        handlers_mock.return_value = {}
        canonical = {
            "schema_version": "1.0.0",
            "analysis_mode": "FULL",
        }
        run_mock.return_value = OrchestrationRun(
            mode="FULL",
            canonical={
                "canonical_analysis": canonical,
                "report_gate": {
                    "state": "PARTIAL",
                    "canonical_fingerprint": "abc",
                },
            },
            results={
                "M00": ModuleResult(
                    module_id="M00",
                    status=ExecutionStatus.COMPLETED,
                ),
                "M02": ModuleResult(
                    module_id="M02",
                    status=ExecutionStatus.NOT_EVALUABLE,
                ),
            },
            ownership={},
        )

        result = execute_relational_work_request(
            request(),
            manifest(),
            astrology_backend=Backend(),
        )

        self.assertEqual(result["canonical_analysis"], canonical)
        self.assertTrue(
            result["execution_receipt"]["canonical_analysis_available"]
        )
        self.assertFalse(
            result["execution_receipt"][
                "canonical_reconstructed_outside_pipeline"
            ]
        )
        self.assertEqual(
            result["execution_receipt"]["not_evaluable_modules"],
            ["M02"],
        )
        self.assertEqual(
            len(result["execution_receipt"]["analysis_policy_fingerprint"]),
            64,
        )
        self.assertEqual(
            result["raw_input"]["aspect_policy"]["CONJUNCTION"]["orb"],
            3.5,
        )

    @patch("almas_tfa.relational_execution.Orchestrator.run")
    @patch("almas_tfa.relational_execution.configured_handlers")
    def test_missing_pipeline_canonical_stays_missing(
        self,
        handlers_mock,
        run_mock,
    ):
        handlers_mock.return_value = {}
        run_mock.return_value = OrchestrationRun(
            mode="FULL",
            canonical={
                "report_gate": {"state": "BLOCKED"},
            },
            results={
                "M30": ModuleResult(
                    module_id="M30",
                    status=ExecutionStatus.COMPLETED,
                )
            },
            ownership={},
        )

        result = execute_relational_work_request(
            request(),
            manifest(),
            astrology_backend=Backend(),
        )
        self.assertIsNone(result["canonical_analysis"])
        self.assertFalse(
            result["execution_receipt"]["canonical_analysis_available"]
        )


if __name__ == "__main__":
    unittest.main()
