import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleResult
from almas_tfa.orchestrator import (
    CanonicalOverwriteError,
    Orchestrator,
    PipelineDefinitionError,
    validate_pipeline_manifest,
)


def full_manifest():
    return {
        "mode": "FULL",
        "modules": [
            {"id": f"M{i:02d}", "name": f"module_{i:02d}"}
            for i in range(32)
        ],
    }


class TestPipelineManifest(unittest.TestCase):
    def test_accepts_exact_m00_m31(self):
        modules = validate_pipeline_manifest(full_manifest())
        self.assertEqual(len(modules), 32)
        self.assertEqual(modules[0]["id"], "M00")
        self.assertEqual(modules[-1]["id"], "M31")

    def test_rejects_missing_stage(self):
        manifest = full_manifest()
        manifest["modules"].pop(7)
        with self.assertRaises(PipelineDefinitionError):
            validate_pipeline_manifest(manifest)


class TestOrchestrator(unittest.TestCase):
    def test_unregistered_modules_are_not_evaluable(self):
        run = Orchestrator().run({"mode": "FULL"}, full_manifest())
        self.assertEqual(
            run.results["M02"].status,
            ExecutionStatus.NOT_EVALUABLE,
        )

    def test_registered_handlers_run_in_manifest_order(self):
        observed = []

        def make_handler(module_id):
            def handler(context):
                observed.append(context.module_id)
                return ModuleResult(
                    module_id=module_id,
                    status=ExecutionStatus.COMPLETED,
                    canonical_updates={module_id.lower(): {"ok": True}},
                )
            return handler

        orchestrator = Orchestrator(
            {
                "M00": make_handler("M00"),
                "M03": make_handler("M03"),
                "M31": make_handler("M31"),
            }
        )
        run = orchestrator.run({"mode": "FULL"}, full_manifest())

        self.assertEqual(observed, ["M00", "M03", "M31"])
        self.assertEqual(run.ownership["m00"], "M00")
        self.assertEqual(run.ownership["m31"], "M31")

    def test_canonical_overwrite_is_blocked(self):
        def first(_context):
            return ModuleResult(
                module_id="M00",
                status=ExecutionStatus.COMPLETED,
                canonical_updates={"shared": {"value": 1}},
            )

        def second(_context):
            return ModuleResult(
                module_id="M01",
                status=ExecutionStatus.COMPLETED,
                canonical_updates={"shared": {"value": 2}},
            )

        orchestrator = Orchestrator({"M00": first, "M01": second})
        with self.assertRaises(CanonicalOverwriteError):
            orchestrator.run(
                {"mode": "FULL"},
                full_manifest(),
                stop_on_failure=True,
            )

    def test_failure_is_explicit_when_not_strict(self):
        def broken(_context):
            raise RuntimeError("fallo sintético")

        run = Orchestrator({"M00": broken}).run(
            {"mode": "FULL"},
            full_manifest(),
        )
        self.assertEqual(run.results["M00"].status, ExecutionStatus.FAILED)
        self.assertIn("RuntimeError", run.results["M00"].diagnostics[0])


if __name__ == "__main__":
    unittest.main()
