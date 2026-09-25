import unittest

from almas_tfa.astrology_backend import NatalRequest
from almas_tfa.astrology_handlers import make_m02_natal
from almas_tfa.module_contract import ExecutionStatus
from almas_tfa.orchestrator import Orchestrator


def full_manifest():
    return {
        "mode": "FULL",
        "manifest_version": "1.0.0",
        "modules": [
            {"id": f"M{i:02d}", "name": f"module_{i:02d}"}
            for i in range(32)
        ],
    }


class FakeBackend:
    backend_id = "FAKE_TEST_BACKEND"
    backend_version = "0"

    def calculate_natal(self, request: NatalRequest):
        result = {
            "subject_id": request.subject_id,
            "timed": request.timed,
            "positions": {
                "SUN": {"longitude": 123.0},
                "MOON": {"longitude": 45.0},
            },
        }
        if request.timed:
            result["angles"] = {"ASC": 10.0, "MC": 100.0}
            result["houses"] = {"1": 10.0, "10": 100.0}
        return result


class TestAstrologyBackendContract(unittest.TestCase):
    def test_m02_accepts_injected_backend(self):
        subjects = [
            {
                "id": "A",
                "birth_date": "1977-03-20",
                "birth_time": "17:37",
                "timezone": "Europe/Madrid",
                "place": "Zaragoza, España",
                "time_reliability": "A",
            },
            {
                "id": "B",
                "birth_date": "1980-01-01",
                "birth_time": None,
                "timezone": "America/Santo_Domingo",
                "place": "Santo Domingo, República Dominicana",
                "time_reliability": "D",
            },
        ]

        orchestrator = Orchestrator(
            {"M02": make_m02_natal(FakeBackend())}
        )
        run = orchestrator.run(
            {"mode": "FULL", "subjects": subjects},
            full_manifest(),
        )

        self.assertEqual(run.results["M02"].status, ExecutionStatus.COMPLETED)
        self.assertTrue(run.canonical["natal"]["charts"]["A"]["timed"])
        self.assertFalse(run.canonical["natal"]["charts"]["B"]["timed"])
        self.assertIn("angles", run.canonical["natal"]["charts"]["A"])
        self.assertNotIn("angles", run.canonical["natal"]["charts"]["B"])
        self.assertTrue(run.results["M02"].limitations)


if __name__ == "__main__":
    unittest.main()
