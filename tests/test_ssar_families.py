import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import ValidationError
from almas_tfa.ssar import load_ssar_policy, run_ssar
from almas_tfa.ssar_s1 import load_s1_catalog, load_s1_policy
from almas_tfa.ssar_families import (
    build_families_request, load_families_catalog, load_families_policy,
    run_families, validate_families_result, validate_families_schema,
)

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    return json.loads((ROOT / "examples/ssar-families.synthetic.json").read_text(encoding="utf-8"))["request"]


def dyad(request=None):
    return run_families(fixture() if request is None else request)["dyads"][0]


def replace_points(request, first, second, name):
    for observation in request["observations"]:
        observation["point_id"] = first if observation["point_id"] == "EROS" else second
    for contact in request["cross_contacts"]:
        contact.update(point_a=first, point_b=second)
        contact["geometry"]["target_id"] = second
    request["dyads"][0]["id"] = name
    return request


class SSARFamiliesTests(unittest.TestCase):
    def test_positive_fixture_two_groups_four_scopes_and_no_global_score(self):
        request = fixture()
        output = run_families(request)
        result = output["dyads"][0]
        self.assertTrue(result["qualified_complex"])
        self.assertEqual(len(result["effective_group_refs"]), 2)
        self.assertEqual(result["assessments"]["structural_geometry"]["status"], "SUPPORTED")
        self.assertEqual(result["assessments"]["functional_interpretation"]["status"], "SUPPORTED")
        for key in ("temporal_activation", "documentary_correspondence"):
            self.assertEqual(result["assessments"][key]["status"], "NOT_EVALUABLE")
        self.assertEqual(result["documentary_scope"], "STRUCTURAL")
        self.assertIsNone(result["cluster_strength"])
        self.assertNotIn("global_state", result)
        self.assertNotIn("score", result)
        self.assertEqual(output["completion"], "PARTIAL")
        self.assertFalse(output["structural_scoring_modified"])
        validate_families_result(output, request=request)

    def test_demeter_persephone_has_actual_executable_positive_rule(self):
        request = replace_points(fixture(), "DEMETER", "PERSEPHONE",
                                 "DEMETER_PERSEPHONE_SEPARATION_RETURN_COMPLEX")
        result = dyad(request)
        self.assertTrue(result["qualified_complex"])
        self.assertIn("F4_HYMN", result["source_refs"])
        self.assertEqual(result["epistemic_class"], "E_PROJECT_HYPOTHESIS")

    def test_shiva_shakti_blockers_cannot_be_overridden_by_geometry(self):
        request = replace_points(fixture(), "SIVA", "SHAKTI", "SHIVA_SHAKTI_RELATIONAL_COMPLEX")
        result = dyad(request)
        self.assertFalse(result["qualified_complex"])
        self.assertIn("SHAKTI_IDENTITY_UNRESOLVED", result["blockers"])
        self.assertIn("SHIVA_SIVA_ALIAS_NOT_AUTHORIZED", result["blockers"])
        self.assertEqual(result["assessments"]["functional_interpretation"]["status"], "NOT_EVALUABLE")
        self.assertEqual(result["assessments"]["structural_geometry"]["status"], "NOT_EVALUABLE")

    def test_isis_geometry_is_evaluable_without_promoting_ambiguous_name(self):
        request = replace_points(fixture(), "ISIS", "OSIRIS", "ISIS_OSIRIS_RECOMPOSITION_COMPLEX")
        result = dyad(request)
        self.assertEqual(result["assessments"]["structural_geometry"]["status"], "SUPPORTED")
        self.assertEqual(result["assessments"]["functional_interpretation"]["status"], "NOT_EVALUABLE")
        self.assertFalse(result["qualified_complex"])
        self.assertIn("ISIS_NAME_ATTRIBUTION_AMBIGUOUS", result["blockers"])

    def test_single_direction_never_qualifies_and_missingness_is_not_counterevidence(self):
        request = fixture()
        request["dyads"][0]["cross_contact_refs"] = ["C1"]
        result = dyad(request)
        self.assertFalse(result["qualified_complex"])
        self.assertEqual(result["assessments"]["structural_geometry"]["status"], "NOT_EVALUABLE")
        self.assertEqual(result["assessments"]["structural_geometry"]["counterevidence_refs"], [])

    def test_search_incomplete_never_supported(self):
        request = fixture(); request["dyads"][0]["search_complete"] = False
        result = dyad(request)
        self.assertFalse(result["qualified_complex"])
        self.assertEqual(result["assessments"]["functional_interpretation"]["status"], "NOT_EVALUABLE")

    def test_complete_direction_without_contact_is_geometry_contradicted(self):
        request = fixture()
        contact = request["cross_contacts"][1]
        contact["endpoint_appearance_refs"] = []
        contact["geometry"]["longitude"] = 80
        result = dyad(request)
        self.assertFalse(result["qualified_complex"])
        self.assertEqual(result["assessments"]["structural_geometry"]["status"], "CONTRADICTED")
        self.assertEqual(result["assessments"]["structural_geometry"]["counterevidence_refs"], ["C2"])

    def test_cross_orb_inclusive_wraparound_and_opposition(self):
        for a, b in ((10, 11), (359.5, 0.5), (10, 190)):
            request = fixture()
            contact = request["cross_contacts"][0]
            contact["geometry"].update(longitude=a, target_longitude=b)
            for sample in contact["robustness"]["samples"]:
                sample.update(longitude=a, target_longitude=b)
            for index, longitude in ((0, a), (1, b)):
                obs = request["observations"][index]
                obs["geometry"].update(longitude=longitude, target_longitude=longitude + 1)
                for sample in obs["robustness"]["samples"]:
                    sample.update(longitude=longitude, target_longitude=longitude + 1)
            self.assertTrue(dyad(request)["qualified_complex"])

    def test_cross_robustness_missing_grid_unknown_precision_and_low_preservation(self):
        for change in ("missing", "grid", "precision", "weak"):
            request = fixture()
            contact = request["cross_contacts"][0]
            contact["endpoint_appearance_refs"] = []
            if change == "missing": contact["robustness"] = None
            if change == "grid": contact["robustness"]["samples"].pop()
            if change == "precision": contact["robustness"]["input_precision_sufficient"] = None
            if change == "weak":
                for sample in contact["robustness"]["samples"][:2]:
                    sample["longitude"] = 50
            self.assertFalse(dyad(request)["qualified_complex"])
            self.assertEqual(dyad(request)["assessments"]["structural_geometry"]["status"], "NOT_EVALUABLE")

    def test_cross_missing_geometry_remains_not_evaluable(self):
        request = fixture()
        request["cross_contacts"][0]["geometry"] = None
        request["cross_contacts"][0]["endpoint_appearance_refs"] = []
        self.assertEqual(dyad(request)["assessments"]["structural_geometry"]["status"], "NOT_EVALUABLE")

    def test_endpoint_subject_position_sample_and_technique_mismatch_rejected(self):
        for change in ("subject", "position", "sample", "technique", "ref", "selection"):
            request = fixture(); contact = request["cross_contacts"][0]
            if change == "subject": request["observations"][0]["subject_id"] = "B"
            if change == "position": contact["geometry"]["longitude"] = 10.1
            if change == "sample": contact["robustness"]["samples"][0]["longitude"] = 10.1
            if change == "technique": contact["endpoint_appearance_refs"] = ["A5"]
            if change == "ref": contact["endpoint_appearance_refs"] = ["MISSING"]
            if change == "selection": request["dyads"][0]["appearance_refs"].remove("A1")
            with self.assertRaises(ValueError): run_families(request)

    def test_two_directions_without_core_anchored_endpoints_cannot_form_complex(self):
        request = fixture()
        for contact in request["cross_contacts"]: contact["endpoint_appearance_refs"] = []
        result = dyad(request)
        self.assertEqual(result["assessments"]["structural_geometry"]["status"], "SUPPORTED")
        self.assertFalse(result["qualified_complex"])
        self.assertIn("BIDIRECTIONAL_ANCHORED_CONTACTS_NOT_MET", result["blockers"])

    def test_missing_core_and_qualified_significator_do_not_get_exception_override(self):
        request = fixture()
        for obs in request["observations"]: obs["core_root_refs"] = []
        result = dyad(request)
        self.assertFalse(result["qualified_complex"])
        self.assertIn("QUALIFIED_SIGNIFICATOR_MISSING", result["blockers"])
        self.assertIn("CORE_ANCHOR_MISSING", result["blockers"])

    def test_one_effective_group_only_compatible_not_qualified_complex(self):
        request = fixture()
        request["dyads"][0]["appearance_refs"].remove("A5")
        result = dyad(request)
        self.assertEqual(len(result["effective_group_refs"]), 1)
        self.assertFalse(result["qualified_complex"])
        self.assertEqual(result["assessments"]["functional_interpretation"]["status"], "COMPATIBLE")

    def test_composite_and_davison_share_one_group(self):
        request = fixture()
        extra = copy.deepcopy(request["observations"][-1])
        extra.update(id="A6", technique="DAVISON", evidence_key="DAVISON:OTHER")
        request["observations"].append(extra)
        request["dyads"][0]["appearance_refs"].append("A6")
        result = dyad(request)
        self.assertEqual(len(result["effective_group_refs"]), 2)

    def test_dependency_types_are_distinct_but_unknown_technical_statistical_collapse(self):
        for relation in ("UNKNOWN", "TECHNICAL_DEPENDENCY", "STATISTICAL_DEPENDENCY"):
            request = fixture()
            request["edges"] = [{"a": "U:A1", "b": "U:A5", "relation": relation,
                                 "rule_id": load_families_policy()["dependency_rules"][relation]}]
            output = run_families(request)
            self.assertEqual(len(output["dyads"][0]["effective_group_refs"]), 1)
            self.assertFalse(output["dyads"][0]["qualified_complex"])
            self.assertEqual(len(output["ssar"]["dependency_graph"]["equivalence_classes"]), 5)

    def test_semantic_overlap_does_not_claim_equivalence_or_independence(self):
        request = fixture()
        relation = "SEMANTIC_OVERLAP"
        request["edges"] = [{"a": "U:A1", "b": "U:A5", "relation": relation,
                             "rule_id": load_families_policy()["dependency_rules"][relation]}]
        output = run_families(request)
        self.assertTrue(output["dyads"][0]["qualified_complex"])
        self.assertFalse(output["ssar"]["dependency_graph"]["statistical_independence_established"])

    def test_equivalence_key_collapses_cross_technique_duplicate(self):
        request = fixture()
        request["observations"][-1]["evidence_key"] = request["observations"][0]["evidence_key"]
        output = run_families(request)
        self.assertFalse(output["dyads"][0]["qualified_complex"])
        self.assertEqual(len(output["ssar"]["dependency_graph"]["equivalence_classes"]), 4)

    def test_unknown_dependency_transitive_with_relationship_family(self):
        request = fixture()
        extra = copy.deepcopy(request["observations"][-1])
        extra.update(id="A6", technique="DAVISON", evidence_key="OTHER")
        request["observations"].append(extra)
        request["dyads"][0]["appearance_refs"].append("A6")
        request["edges"] = [{"a": "U:A1", "b": "U:A6", "relation": "UNKNOWN",
                             "rule_id": load_families_policy()["dependency_rules"]["UNKNOWN"]}]
        self.assertEqual(len(dyad(request)["effective_group_refs"]), 1)

    def test_family_partial_missing_components_not_zero_and_no_numeric_maximum(self):
        output = run_families(fixture())
        family = output["families"][0]
        self.assertEqual(family["coverage"], "PARTIAL")
        self.assertIsNone(family["cluster_strength"])
        self.assertEqual([c["coverage"] for c in family["components"]], ["SUPPLIED", "MISSING", "MISSING"])
        self.assertEqual(family["selection_policy"], "NO_RANKING_WITHOUT_FROZEN_COMMON_MAGNITUDE")
        self.assertNotIn("winner", family)

    def test_family_all_members_same_technique_remain_one_effective_group(self):
        request = fixture()
        request["observations"] = [request["observations"][0]]
        request["cross_contacts"] = []; request["dyads"] = []
        for point in ("AMOR", "CUPIDO"):
            obs = copy.deepcopy(request["observations"][0])
            obs.update(id=point, point_id=point, evidence_key=point)
            request["observations"].append(obs)
        family = run_families(request)["families"][0]
        self.assertEqual(family["coverage"], "SUPPLIED")
        self.assertEqual(len(family["effective_group_refs"]), 1)
        self.assertEqual(len(family["contact_refs"]), 3)
        self.assertIsNone(family["cluster_strength"])

    def test_equal_contacts_all_retained_without_undefined_strength_tiebreak(self):
        request = fixture(); request["cross_contacts"] = []; request["dyads"] = []
        request["observations"] = [request["observations"][0]]
        for point in ("AMOR", "CUPIDO"):
            obs = copy.deepcopy(request["observations"][0])
            obs.update(id=point, point_id=point, evidence_key=point)
            request["observations"].append(obs)
        self.assertEqual(run_families(request)["families"][0]["contact_refs"], ["A1", "AMOR", "CUPIDO"])

    def test_aphrodite_only_venus_overlay_no_independent_group(self):
        request = fixture()
        obs = copy.deepcopy(request["observations"][-1])
        obs.update(id="AP", point_id="APHRODITE", evidence_key="AP")
        obs["geometry"]["target_id"] = "VENUS"
        request["core_roots"][0]["point_ids"].append("VENUS")
        request["observations"].append(obs)
        output = run_families(request)
        self.assertEqual(output["overlays"][0]["contact_refs"], ["AP"])
        self.assertFalse(output["overlays"][0]["independent_function"])
        self.assertEqual(output["overlays"][0]["effective_group_refs"], [])
        self.assertEqual(len(output["dyads"][0]["effective_group_refs"]), 2)
        obs["geometry"]["target_id"] = "SUN"
        self.assertEqual(run_families(request)["overlays"][0]["components"][0]["coverage"], "BLOCKED")

    def test_shared_eros_family_and_dyad_do_not_create_units_or_roots(self):
        request = fixture(); output = run_families(request)
        self.assertEqual(len(output["ssar"]["dependency_graph"]["units"]), 5)
        self.assertEqual(output["dyads"][0]["core_root_refs"], ["R1"])
        self.assertEqual(len(output["shared_contacts"]), 3)
        self.assertTrue(all(not s["contributes_new_evidence"] for s in output["shared_contacts"]))

    def test_duplicate_appearance_contact_selection_and_wrong_order_rejected(self):
        for change in ("observation", "contact", "reverse", "selection", "order"):
            request = fixture()
            if change == "observation":
                extra = copy.deepcopy(request["observations"][0]); extra["id"] = "OTHER"
                request["observations"].append(extra)
            if change in ("contact", "reverse"):
                extra = copy.deepcopy(request["cross_contacts"][0]); extra["id"] = "OTHER"
                if change == "reverse":
                    extra["point_a"], extra["point_b"] = extra["point_b"], extra["point_a"]
                    extra["subject_a"], extra["subject_b"] = extra["subject_b"], extra["subject_a"]
                    g = extra["geometry"]
                    g["longitude"], g["target_longitude"] = g["target_longitude"], g["longitude"]
                    g["target_id"] = extra["point_b"]
                request["cross_contacts"].append(extra)
            if change == "selection": request["dyads"].append(copy.deepcopy(request["dyads"][0]))
            if change == "order": request["cross_contacts"][0]["point_a"] = "AMOR"
            with self.assertRaises(ValueError): run_families(request)

    def test_catalog_sources_cannot_be_removed_or_promoted_to_doctrine(self):
        for field in ("provenance", "semantic_basis", "method"):
            effective = build_families_request(replace_points(fixture(), "DEMETER", "PERSEPHONE",
                                                             "DEMETER_PERSEPHONE_SEPARATION_RETURN_COMPLEX"))
            effective["appearances"][0][field]["source_refs"] = []
            self.assertEqual(run_ssar(effective, policy=load_families_policy())["appearances"][0]["qualification"], "BLOCKED")

    def test_nonfinite_unknown_object_bad_subject_and_broken_dependency_rejected(self):
        for change in ("finite", "point", "subject", "edge"):
            request = fixture()
            if change == "finite": request["observations"][0]["geometry"]["longitude"] = float("nan")
            if change == "point": request["observations"][0]["point_id"] = "PARVATI"
            if change == "subject": request["observations"][0]["subject_id"] = "RELATIONSHIP"
            if change == "edge": request["edges"] = [{"a": "U:A1", "b": "ABSENT", "relation": "UNKNOWN",
                                                      "rule_id": load_families_policy()["dependency_rules"]["UNKNOWN"]}]
            with self.assertRaises((ValueError, ValidationError)): run_families(request)

    def test_result_tampering_in_each_scope_groups_sources_strength_and_effect_rejected(self):
        request = fixture()
        for key in ("structural_geometry", "functional_interpretation", "temporal_activation", "documentary_correspondence"):
            output = run_families(request)
            output["dyads"][0]["assessments"][key]["status"] = "CONTRADICTED"
            with self.assertRaises(ValueError): validate_families_result(output, request=request)
        for field, value in (("effective_group_refs", ["FAKE"]), ("source_refs", []), ("qualified_complex", False),
                             ("cluster_strength", 99), ("documentary_scope", "TEMPORAL")):
            output = run_families(request); output["dyads"][0][field] = value
            with self.assertRaises((ValueError, ValidationError)): validate_families_result(output, request=request)
        output = run_families(request); output["ontology_effect"] = "CHANGED"
        with self.assertRaises(ValidationError): validate_families_result(output, request=request)

    def test_opt_in_no_input_mutation_and_default_s1_catalogs_unchanged(self):
        request = fixture(); before = copy.deepcopy(request)
        s1_catalog, s1_policy = load_s1_catalog(), load_s1_policy()
        run_families(request)
        self.assertEqual(request, before)
        self.assertEqual(load_s1_catalog(), s1_catalog)
        self.assertEqual(load_s1_policy(), s1_policy)
        self.assertEqual(load_ssar_policy()["point_rules"], {})
        self.assertEqual(len(load_families_catalog()["dyads"]), 4)

    def test_disabled_without_schema_extra_and_empty_enabled_not_absence(self):
        output = run_families({"enabled": False, "history": "ignored"})
        self.assertEqual(output["dyads"], [])
        self.assertEqual(output["completion"], "NONE")
        code = "import sys;sys.path.insert(0,'src');from almas_tfa.ssar_families import run_families;assert run_families({'enabled':False})['completion']=='NONE'"
        subprocess.run([sys.executable, "-S", "-c", code], cwd=ROOT, check=True)
        output = run_families({"enabled": True})
        self.assertEqual(output["ssar"]["execution_status"], "not_run")
        self.assertEqual(output["completion"], "NONE")
        self.assertEqual(output["families"][0]["coverage"], "PARTIAL")


if __name__ == "__main__":
    unittest.main()
