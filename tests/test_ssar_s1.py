import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import ValidationError

from almas_tfa.ssar import run_ssar, load_ssar_policy, validate_ssar_result
from almas_tfa.ssar_s1 import (
    load_s1_catalog, load_s1_policy, build_s1_request, run_s1, validate_s1_result,
)

POINTS = ["CERES", "PALLAS", "JUNO", "VESTA", "CHIRON", "PSYCHE", "EROS"]
ROOT = Path(__file__).resolve().parents[1]


def fixture(point="CERES"):
    return {"enabled": True, "core_roots": [
        {"root_id": "R1", "core_eligible": True, "core_evidence_ids": ["CORE1"], "point_ids": ["SUN", "MOON"]}],
        "observations": [{"id": "A1", "point_id": point,
                          "geometry": {"longitude": 10.0, "target_longitude": 11.0, "target_id": "SUN", "frame": "TROPICAL_ECLIPTIC"},
                          "core_root_refs": ["R1"], "core_anchor_search_complete": True,
                          "robustness": {"input_precision_sufficient": True, "samples": [
                              {"id": f"P{i}", "offset_minutes": offset, "longitude": 10 + offset / 1000,
                               "target_longitude": 11.0} for i, offset in enumerate([-30, -15, 0, 15, 30])]} }],
        "units": [{"id": "U1", "appearance_ref": "A1", "technique": "SYNASTRY", "equivalence_key": "CONTACT1"}],
        "edges": [], "existing_contacts": []}


class SSARS1Tests(unittest.TestCase):
    def test_seven_functions_are_opt_in_and_default_policy_remains_empty(self):
        catalog, policy = load_s1_catalog(), load_s1_policy()
        self.assertEqual(set(policy["point_rules"]), set(POINTS))
        self.assertEqual(len({entry["function_id"] for entry in catalog["entries"]}), 7)
        self.assertFalse(load_ssar_policy()["point_rules"])
        self.assertTrue(all(entry["epistemic_class"] == "E_PROJECT_HYPOTHESIS" for entry in catalog["entries"]))

    def test_all_seven_positive_functions_have_limits_and_no_documentary_promotion(self):
        for point in POINTS:
            with self.subTest(point=point):
                request = fixture(point)
                output = run_s1(request)
                self.assertEqual(output["ssar"]["qualified_significators"], ["A1"])
                self.assertEqual(output["functional_notes"][0]["documentary_status"], "NOT_EVALUABLE")
                self.assertIsNotNone(output["functional_notes"][0]["interpretation"])
                self.assertTrue(output["functional_notes"][0]["inferential_limit"])
                self.assertFalse(output["ssar"]["structural_scoring_modified"])
                self.assertEqual(output["ssar"]["ontology_effect"], "NONE")
                self.assertEqual(output["ssar"]["complexes"], [])
                validate_s1_result(output, request=request)

    def test_all_seven_negative_geometry_suppresses_interpretation(self):
        for point in POINTS:
            with self.subTest(point=point):
                request = fixture(point)
                request["observations"][0]["geometry"]["longitude"] = 25.0
                output = run_s1(request)
                self.assertEqual(output["ssar"]["appearances"][0]["qualification"], "NO_CONTACT")
                self.assertEqual(output["ssar"]["appearances"][0]["assessment"]["scope"], "STRUCTURAL_GEOMETRY")
                self.assertIsNone(output["functional_notes"][0]["interpretation"])

    def test_all_seven_missing_essential_geometry_and_robustness_block(self):
        for point in POINTS:
            for field in ("geometry", "robustness"):
                with self.subTest(point=point, field=field):
                    request = fixture(point)
                    request["observations"][0][field] = None
                    output = run_s1(request)
                    self.assertEqual(output["ssar"]["appearances"][0]["qualification"], "BLOCKED")
                    self.assertIsNone(output["functional_notes"][0]["interpretation"])

    def test_all_seven_without_core_anchor_are_only_exploratory_support(self):
        for point in POINTS:
            with self.subTest(point=point):
                request = fixture(point)
                request["observations"][0]["core_root_refs"] = []
                output = run_s1(request)
                self.assertEqual(output["ssar"]["secondary_support"], ["A1"])
                self.assertEqual(output["ssar"]["appearances"][0]["assessment"]["status"], "COMPATIBLE")

    def test_all_seven_incomplete_core_search_block(self):
        for point in POINTS:
            request = fixture(point)
            request["observations"][0]["core_anchor_search_complete"] = False
            self.assertEqual(run_s1(request)["ssar"]["qualified_significators"], [])

    def test_all_seven_weak_robustness_is_secondary_and_unknown_precision_blocks(self):
        for point in POINTS:
            request = fixture(point)
            robust = request["observations"][0]["robustness"]
            for sample in robust["samples"][0:2]:
                sample["longitude"] = 25.0
            self.assertEqual(run_s1(request)["ssar"]["secondary_support"], ["A1"])
            robust["input_precision_sufficient"] = False
            self.assertEqual(run_s1(request)["ssar"]["appearances"][0]["qualification"], "BLOCKED")

    def test_all_seven_pending_identity_or_semantic_source_blocks(self):
        for point in POINTS:
            for field in ("identity", "source"):
                with self.subTest(point=point, field=field):
                    request = build_s1_request(fixture(point))
                    if field == "identity":
                        request["appearances"][0]["provenance"]["identity_status"] = "PENDING"
                    else:
                        next(source for source in request["sources"] if source["id"] == "S1_PROJECT")["verification_status"] = "PENDING"
                    self.assertEqual(run_ssar(request, policy=load_s1_policy())["qualified_significators"], [])

    def test_four_verified_names_block_if_nominal_verification_is_lost(self):
        for point in ("CERES", "VESTA", "PSYCHE", "EROS"):
            request = build_s1_request(fixture(point))
            request["appearances"][0]["provenance"]["verification_status"] = "PENDING"
            self.assertEqual(run_ssar(request, policy=load_s1_policy())["appearances"][0]["qualification"], "BLOCKED")

    def test_three_pending_names_only_allow_declared_independent_method(self):
        for point in ("PALLAS", "JUNO", "CHIRON"):
            request = build_s1_request(fixture(point))
            prov = request["appearances"][0]["provenance"]
            self.assertEqual(prov["verification_status"], "PENDING")
            self.assertEqual(run_ssar(request, policy=load_s1_policy())["qualified_significators"], ["A1"])
            prov.update(basis="NAME", name_class="NP1_MYTHIC_DIRECT", verification_status="VERIFIED")
            self.assertEqual(run_ssar(request, policy=load_s1_policy())["qualified_significators"], [])

    def test_cannot_label_project_rule_as_doctrine_or_remove_catalog_sources(self):
        for point in POINTS:
            for field in ("semantic_basis", "method"):
                for mutation in ("epistemic_class", "source_refs"):
                    request = build_s1_request(fixture(point))
                    request["appearances"][0][field][mutation] = "C_DOCTRINE" if mutation == "epistemic_class" else []
                    if field == "method" and mutation == "epistemic_class":
                        with self.assertRaises(ValidationError):
                            run_ssar(request, policy=load_s1_policy())
                    else:
                        self.assertEqual(run_ssar(request, policy=load_s1_policy())["qualified_significators"], [])

    def test_outer_planet_or_secondary_cannot_be_used_as_s1_target(self):
        for target in ("JUPITER", "SATURN", "CHIRON", "JUNO", "PLUTO"):
            request = fixture()
            request["observations"][0]["geometry"]["target_id"] = target
            request["core_roots"][0]["point_ids"].append(target)
            self.assertIn("TARGET_NOT_AUTHORIZED_BY_POINT_POLICY", run_s1(request)["ssar"]["appearances"][0]["gate_reasons"])

    def test_every_published_anchor_is_usable_and_missing_root_is_error(self):
        for target in load_s1_policy()["point_rules"]["CERES"]["allowed_target_ids"]:
            request = fixture()
            request["observations"][0]["geometry"]["target_id"] = target
            request["core_roots"][0]["point_ids"] = [target]
            self.assertEqual(run_s1(request)["ssar"]["qualified_significators"], ["A1"])
        request["core_roots"] = []
        with self.assertRaises(ValueError):
            run_s1(request)

    def test_inclusive_orb_boundary_and_wraparound(self):
        for longitude, target in ((10, 11.5), (359.5, 0.5), (10, 190)):
            request = fixture()
            observation = request["observations"][0]
            observation["geometry"].update(longitude=longitude, target_longitude=target)
            for sample in observation["robustness"]["samples"]:
                sample.update(longitude=longitude, target_longitude=target)
            self.assertEqual(run_s1(request)["ssar"]["qualified_significators"], ["A1"])

    def test_reused_chiron_and_vesta_contacts_add_no_units_or_roots(self):
        for point, layers in (("CHIRON", ["CHIRON_PROCESS", "WOUND_REPAIR"]), ("VESTA", ["SURRENDER_VESTAL"])):
            request = fixture(point)
            original = run_s1(request)
            observation = request["observations"][0]
            request["existing_contacts"] = [dict(layer=layer, evidence_id="OLD_CONTACT", artifact_ref="synthetic:"+layer,
                appearance_ref="A1", point_id=point, geometry=copy.deepcopy(observation["geometry"]), core_root_refs=["R1"]) for layer in layers]
            result = run_s1(request)
            self.assertEqual(result["ssar"], original["ssar"])
            self.assertTrue(all(not link["contributes_new_evidence"] for link in result["reused_contacts"]))
            validate_s1_result(result, request=request)

    def test_invalid_reuse_scope_geometry_root_or_reference_rejected(self):
        for field, value in (("layer", "SURRENDER_VESTAL"), ("point_id", "VESTA"), ("appearance_ref", "MISSING"), ("core_root_refs", []),
                             ("geometry", {"longitude": 11.0, "target_longitude": 11.0, "target_id": "SUN", "frame": "TROPICAL_ECLIPTIC"})):
            request = fixture("CHIRON")
            record = dict(layer="CHIRON_PROCESS", evidence_id="OLD", artifact_ref="synthetic:old", appearance_ref="A1", point_id="CHIRON", geometry=copy.deepcopy(request["observations"][0]["geometry"]), core_root_refs=["R1"])
            record[field] = value
            request["existing_contacts"] = [record]
            with self.assertRaises(ValueError):
                run_s1(request)

    def test_duplicate_reuse_or_duplicate_observation_rejected(self):
        request = fixture("CHIRON")
        record = dict(layer="CHIRON_PROCESS", evidence_id="OLD", artifact_ref="synthetic:old", appearance_ref="A1", point_id="CHIRON", geometry=copy.deepcopy(request["observations"][0]["geometry"]), core_root_refs=["R1"])
        request["existing_contacts"] = [record, copy.deepcopy(record)]
        with self.assertRaises(ValueError):
            run_s1(request)
        request = fixture("CHIRON")
        other = copy.deepcopy(request["observations"][0]); other["id"] = "A2"
        request["observations"].append(other)
        with self.assertRaises(ValueError):
            run_s1(request)

    def test_empty_search_is_not_absence_and_disabled_discards_history_without_extras(self):
        output = run_s1({"enabled": True})
        self.assertEqual(output["ssar"]["execution_status"], "not_run")
        self.assertEqual(output["ssar"]["completion"], "NONE")
        request = fixture()
        request["enabled"] = False
        output = run_s1(request)
        self.assertEqual(output["functional_notes"], [])
        code = "import sys; sys.path.insert(0,'src'); from almas_tfa.ssar_s1 import run_s1; assert run_s1({'enabled':False,'history':'ignored'})['ssar']['execution_status']=='not_run'"
        subprocess.run([sys.executable, "-S", "-c", code], cwd=ROOT, check=True)

    def test_unknown_object_or_prohibited_result_effect_rejected(self):
        request = fixture(); request["observations"][0]["point_id"] = "ALMA"
        with self.assertRaises(ValidationError):
            run_s1(request)
        for technique in ("NATAL_DRACONIC", "ANTISCIA", "VERTEX", "BLACK_MOON_MEAN"):
            request = fixture()
            request["units"][0]["technique"] = technique
            with self.assertRaises(ValueError):
                run_s1(request)
        request = fixture()
        result = run_s1(request)
        result["ssar"]["structural_scoring_modified"] = True
        with self.assertRaises(ValidationError):
            validate_s1_result(result, request=request)

    def test_modified_notes_links_hash_or_refs_cannot_be_validated(self):
        request = fixture("VESTA")
        for field, value in (("interpretation", "Se confirma celibato"), ("documentary_status", "SUPPORTED"), ("appearance_ref", "MISSING"), ("inferential_limit", "Sin límites")):
            output = run_s1(request); output["functional_notes"][0][field] = value
            with self.assertRaises((ValueError, ValidationError)):
                validate_s1_result(output, request=request)
        output = run_s1(request); output["catalog_hash"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_s1_result(output, request=request)

    def test_request_and_catalog_are_not_mutated(self):
        request, catalog = fixture(), load_s1_catalog()
        before = copy.deepcopy(request)
        output = run_s1(request)
        self.assertEqual(request, before)
        self.assertEqual(load_s1_catalog(), catalog)
        validate_ssar_result(output["ssar"], policy=load_s1_policy(), request=build_s1_request(request))


if __name__ == "__main__":
    unittest.main()
