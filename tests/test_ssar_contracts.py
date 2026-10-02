import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import Draft202012Validator, ValidationError

from almas_tfa.analysis import analyze_precomputed
from almas_tfa.ssar import (
    assess_ssar_claim, load_ssar_policy, run_ssar, ssar_dependency_groups,
    ssar_policy_hash, validate_ssar_result, validate_ssar_schema,
)

ROOT = Path(__file__).resolve().parents[1]


def fixture(kind="NAMED_SMALL_BODY"):
    policy = load_ssar_policy()
    point_id = "SYNTH_" + kind
    policy["policy_id"] = "SSAR_SYNTHETIC_DEVELOPMENT_V1"
    policy["point_rules"][point_id] = {
        "kind": kind, "function_id": "SYNTHETIC_FUNCTION", "allow_project_method": True,
        "rule_id": "SYNTHETIC_APPEARANCE_RULE_V1",
    }
    policy["type_rules"][kind]["aspect_policy"] = {
        "CONJUNCTION": {"angle": 0.0, "orb": 1.5},
        "OPPOSITION": {"angle": 180.0, "orb": 1.5},
    }
    policy["technique_groups"].update(SYNTH_A="SYNTH_A", SYNTH_B="SYNTH_B")
    sources = [
        {"id": "S0", "author": "Autor sintético", "work": "Identidad y definición sintéticas",
         "date": None, "locator": "Pasaje sintético 1", "priority": "P1", "epistemic_class": "A_DOCUMENTARY",
         "verification_status": "VERIFIED", "claim_scopes": ["IDENTITY", "NAME_ORIGIN", "TECHNICAL_DEFINITION"]},
        {"id": "S1", "author": "Autor sintético", "work": "Doctrina sintética",
         "date": None, "locator": "Pasaje sintético 2", "priority": "P1", "epistemic_class": "C_DOCTRINE",
         "verification_status": "VERIFIED", "claim_scopes": ["SEMANTIC_BASIS"]},
        {"id": "S2", "author": "Proyecto sintético", "work": "Método experimental sintético",
         "date": None, "locator": "Regla sintética 3", "priority": "P4", "epistemic_class": "E_PROJECT_HYPOTHESIS",
         "verification_status": "VERIFIED", "claim_scopes": ["ASTROLOGICAL_METHOD"]},
    ]
    appearance = {
        "id": "A1", "point_id": point_id, "kind": kind,
        "provenance": {"identity_status": "VERIFIED", "basis": "NAME" if kind == "NAMED_SMALL_BODY" else "TECHNICAL",
                       "verification_status": "VERIFIED", "name_class": "NP1_MYTHIC_DIRECT" if kind == "NAMED_SMALL_BODY" else None,
                       "source_refs": ["S0"], "algorithm": None if kind == "NAMED_SMALL_BODY" else "Algoritmo sintético explícito",
                       "conventions": None if kind == "NAMED_SMALL_BODY" else "Convenciones sintéticas explícitas",
                       "inputs": [] if kind == "NAMED_SMALL_BODY" else ["SYNTH_ASC", "SYNTH_SUN", "SYNTH_MOON"],
                       "variant": None if kind == "NAMED_SMALL_BODY" else "SYNTHETIC_VARIANT",
                       "sect": "DAY" if kind == "HELLENISTIC_LOT" else None},
        "semantic_basis": {"epistemic_class": "E_PROJECT_HYPOTHESIS", "source_refs": ["S1"],
                           "justification": "Hipótesis sintética; no es doctrina del autor.", "policy_ref": policy["policy_id"]},
        "method": {"epistemic_class": "E_PROJECT_HYPOTHESIS", "source_refs": ["S2"],
                   "justification": "Método sintético independiente del caso.", "policy_ref": policy["policy_id"]},
        "geometry": {"longitude": 10.0, "target_longitude": 11.0, "target_id": "SUN", "frame": "TROPICAL_ECLIPTIC"},
        "core_root_refs": ["R1"], "core_anchor_search_complete": True,
        "robustness": {"input_precision_sufficient": True,
                       "samples": [{"id": f"P{i}", "offset_minutes": offset, "longitude": 10.0 + offset / 1000,
                                    "target_longitude": 11.0} for i, offset in enumerate([-30, -15, 0, 15, 30])]},
    }
    request = {"enabled": True, "sources": sources,
               "core_roots": [{"root_id": "R1", "core_eligible": True, "core_evidence_ids": ["E-CORE-1"], "point_ids": ["SUN", "MOON"]}],
               "appearances": [appearance], "units": [], "edges": []}
    return request, policy


class SSARContractsTests(unittest.TestCase):
    def test_default_policy_has_no_enabled_points_or_implicit_orbs(self):
        policy = load_ssar_policy()
        validate_ssar_schema(policy, "Policy")
        self.assertEqual(policy["point_rules"], {})
        self.assertTrue(all(rule["aspect_policy"] is None for rule in policy["type_rules"].values()))
        self.assertEqual(policy["policy_status"], "DEVELOPMENT")

    def test_qualified_synthetic_appearance_for_each_kind(self):
        for kind in ("NAMED_SMALL_BODY", "CALCULATED_POINT", "HELLENISTIC_LOT"):
            with self.subTest(kind=kind):
                request, policy = fixture(kind)
                result = run_ssar(request, policy=policy)
                self.assertEqual(result["qualified_significators"], ["A1"])
                self.assertEqual(result["appearances"][0]["assessment"]["status"], "SUPPORTED")
                self.assertEqual(result["appearances"][0]["epistemic_class"], "E_PROJECT_HYPOTHESIS")
                self.assertTrue(result["appearances"][0]["project_method"])
                self.assertEqual(result["completion"], "PARTIAL")
                self.assertEqual(result["complexes"], [])
                validate_ssar_result(result, policy=policy, request=request)

    def test_default_policy_blocks_synthetic_candidate(self):
        request, _ = fixture()
        result = run_ssar(request)
        self.assertEqual(result["appearances"][0]["qualification"], "BLOCKED")
        self.assertIn("POINT_NOT_ENABLED_BY_POLICY", result["appearances"][0]["gate_reasons"])

    def test_pending_disputed_unresolved_nominal_provenance_is_blocked(self):
        for status in ("PENDING", "DISPUTED", "UNRESOLVED"):
            request, policy = fixture()
            request["appearances"][0]["provenance"]["verification_status"] = status
            self.assertEqual(run_ssar(request, policy=policy)["appearances"][0]["qualification"], "BLOCKED")

    def test_person_place_and_ambiguous_names_cannot_qualify_by_name(self):
        for name_class in ("NP3_PERSON_OR_PLACE", "NP4_AMBIGUOUS", None):
            request, policy = fixture()
            request["appearances"][0]["provenance"]["name_class"] = name_class
            result = run_ssar(request, policy=policy)["appearances"][0]
            self.assertEqual(result["qualification"], "BLOCKED")
            self.assertIn("NOMINAL_SEMANTIC_ASSOCIATION_FORBIDDEN", result["gate_reasons"])

    def test_independent_method_can_be_exploratory_without_restoring_nominal_equivalence(self):
        request, policy = fixture()
        prov = request["appearances"][0]["provenance"]
        prov.update(basis="INDEPENDENT_OF_NAME", verification_status="PENDING", name_class=None)
        result = run_ssar(request, policy=policy)
        self.assertEqual(result["qualified_significators"], ["A1"])
        self.assertEqual(result["analysis_scope"], "EXPLORATORY")

    def test_missing_essential_fields_are_not_positive_support(self):
        for field in ("provenance", "semantic_basis", "method", "geometry", "robustness"):
            request, policy = fixture()
            request["appearances"][0][field] = None
            result = run_ssar(request, policy=policy)["appearances"][0]
            self.assertEqual(result["qualification"], "BLOCKED")
            self.assertEqual(result["assessment"]["status"], "NOT_EVALUABLE")

    def test_calculated_method_needs_algorithm_conventions_and_verification(self):
        for field in ("algorithm", "conventions", "inputs", "variant"):
            for kind in ("CALCULATED_POINT", "HELLENISTIC_LOT"):
                request, policy = fixture(kind)
                request["appearances"][0]["provenance"][field] = [] if field == "inputs" else None
                self.assertEqual(run_ssar(request, policy=policy)["qualified_significators"], [])

    def test_unknown_required_sect_blocks_lot_interpretation(self):
        request, policy = fixture("HELLENISTIC_LOT")
        request["appearances"][0]["provenance"]["sect"] = None
        result = run_ssar(request, policy=policy)["appearances"][0]
        self.assertEqual(result["qualification"], "BLOCKED")
        self.assertIn("REQUIRED_SECT_UNRESOLVED", result["gate_reasons"])

    def test_source_pending_or_wrong_claim_scope_blocks_support(self):
        for field, value in (("verification_status", "PENDING"), ("claim_scopes", ["IDENTITY"])):
            request, policy = fixture()
            request["sources"][1][field] = value
            self.assertEqual(run_ssar(request, policy=policy)["appearances"][0]["qualification"], "BLOCKED")

    def test_project_method_needs_justification_and_explicit_authorization(self):
        request, policy = fixture()
        request["appearances"][0]["method"]["justification"] = None
        self.assertEqual(run_ssar(request, policy=policy)["qualified_significators"], [])
        request, policy = fixture()
        policy["point_rules"][request["appearances"][0]["point_id"]]["allow_project_method"] = False
        self.assertEqual(run_ssar(request, policy=policy)["qualified_significators"], [])

    def test_doctrine_cannot_borrow_project_method_classification(self):
        request, policy = fixture()
        request["appearances"][0]["semantic_basis"]["epistemic_class"] = "C_DOCTRINE"
        request["sources"][1]["epistemic_class"] = "E_PROJECT_HYPOTHESIS"
        self.assertEqual(run_ssar(request, policy=policy)["qualified_significators"], [])

    def test_weak_source_remains_secondary_support(self):
        request, policy = fixture()
        request["sources"][1]["priority"] = "P5"
        result = run_ssar(request, policy=policy)
        self.assertEqual(result["secondary_support"], ["A1"])
        self.assertEqual(result["appearances"][0]["assessment"]["status"], "COMPATIBLE")

    def test_complete_search_without_core_anchor_is_secondary_support(self):
        request, policy = fixture()
        request["appearances"][0]["core_root_refs"] = []
        self.assertEqual(run_ssar(request, policy=policy)["secondary_support"], ["A1"])

    def test_incomplete_anchor_search_is_blocked(self):
        request, policy = fixture()
        request["appearances"][0]["core_anchor_search_complete"] = False
        self.assertEqual(run_ssar(request, policy=policy)["appearances"][0]["qualification"], "BLOCKED")

    def test_exact_orb_boundary_is_inclusive(self):
        request, policy = fixture()
        a = request["appearances"][0]
        a["geometry"]["target_longitude"] = 11.5
        for sample in a["robustness"]["samples"]:
            sample.update(longitude=10.0, target_longitude=11.5)
        self.assertEqual(run_ssar(request, policy=policy)["qualified_significators"], ["A1"])

    def test_complete_geometry_outside_orb_is_no_contact_in_geometric_scope(self):
        request, policy = fixture()
        request["appearances"][0]["geometry"]["target_longitude"] = 11.5000001
        result = run_ssar(request, policy=policy)["appearances"][0]
        self.assertEqual(result["qualification"], "NO_CONTACT")
        self.assertEqual(result["assessment"]["scope"], "STRUCTURAL_GEOMETRY")
        self.assertEqual(result["assessment"]["status"], "CONTRADICTED")

    def test_robustness_at_criterion_qualifies_below_it_is_secondary(self):
        request, policy = fixture()
        samples = request["appearances"][0]["robustness"]["samples"]
        samples[0]["target_longitude"] = 30.0
        self.assertEqual(run_ssar(request, policy=policy)["qualified_significators"], ["A1"])
        samples[1]["target_longitude"] = 30.0
        self.assertEqual(run_ssar(request, policy=policy)["secondary_support"], ["A1"])

    def test_perturbation_cannot_change_aspect_to_preserve_contact(self):
        request, policy = fixture()
        for sample in request["appearances"][0]["robustness"]["samples"]:
            sample["target_longitude"] = sample["longitude"] + 180.0
        result = run_ssar(request, policy=policy)["appearances"][0]
        self.assertEqual(result["robustness"]["preserved_count"], 0)
        self.assertEqual(result["qualification"], "SECONDARY_SUPPORT")

    def test_missing_wrong_grid_and_precision_block_qualification(self):
        for change in ("short", "wrong_grid", "unknown_precision", "false_precision"):
            request, policy = fixture()
            robust = request["appearances"][0]["robustness"]
            if change == "short": robust["samples"].pop()
            if change == "wrong_grid": robust["samples"][0]["offset_minutes"] = -40
            if change == "unknown_precision": robust["input_precision_sufficient"] = None
            if change == "false_precision": robust["input_precision_sufficient"] = False
            self.assertEqual(run_ssar(request, policy=policy)["qualified_significators"], [])
            self.assertEqual(run_ssar(request, policy=policy)["secondary_support"], [])

    def test_duplicate_perturbation_offsets_are_invalid(self):
        request, policy = fixture()
        request["appearances"][0]["robustness"]["samples"][1]["offset_minutes"] = -30
        with self.assertRaises(ValueError): run_ssar(request, policy=policy)

    def test_broken_references_and_duplicate_ids_are_rejected(self):
        for change in ("source", "root", "appearance", "source_duplicate", "root_duplicate", "sample_duplicate"):
            request, policy = fixture()
            if change == "source": request["appearances"][0]["method"]["source_refs"] = ["ABSENT"]
            if change == "root": request["appearances"][0]["core_root_refs"] = ["ABSENT"]
            if change == "appearance": request["units"] = [{"id": "U1", "appearance_ref": "ABSENT", "technique": "SYNTH_A", "equivalence_key": "K1"}]
            if change == "source_duplicate": request["sources"].append(copy.deepcopy(request["sources"][0]))
            if change == "root_duplicate": request["core_roots"].append(copy.deepcopy(request["core_roots"][0]))
            if change == "sample_duplicate": request["appearances"][0]["robustness"]["samples"][1]["id"] = "P0"
            with self.assertRaises(ValueError): run_ssar(request, policy=policy)

    def test_support_root_empty_core_proof_or_wrong_target_cannot_anchor(self):
        for change in ("support", "empty_proof", "target"):
            request, policy = fixture()
            if change == "support": request["core_roots"][0]["core_eligible"] = False
            if change == "empty_proof": request["core_roots"][0]["core_evidence_ids"] = []
            if change == "target": request["appearances"][0]["geometry"]["target_id"] = "JUPITER"
            with self.assertRaises(ValueError): run_ssar(request, policy=policy)

    def test_invalid_numeric_or_boolean_values_are_rejected(self):
        for value in (math.nan, math.inf, -math.inf, True):
            request, policy = fixture()
            request["appearances"][0]["geometry"]["longitude"] = value
            with self.assertRaises((ValueError, ValidationError)): run_ssar(request, policy=policy)

    def test_no_run_disabled_or_empty_never_means_no_findings(self):
        policy = load_ssar_policy()
        for request in ({"enabled": False}, {"enabled": True}):
            result = run_ssar(request)
            self.assertEqual(result["execution_status"], "not_run")
            self.assertEqual(result["completion"], "NONE")
            validate_ssar_result(result, policy=policy, request=request)

    def test_disabled_path_does_not_load_policy_or_need_extras(self):
        from unittest.mock import patch
        with patch("almas_tfa.ssar.load_ssar_policy", side_effect=AssertionError):
            self.assertFalse(run_ssar({"enabled": False})["enabled"])
        code = "import sys;sys.path.insert(0,'src');from almas_tfa.ssar import run_ssar;assert run_ssar({'enabled':False})['execution_status']=='not_run'"
        subprocess.run([sys.executable, "-S", "-c", code], cwd=ROOT, check=True)

    def test_policy_hash_is_deterministic_key_order_invariant_and_sensitive(self):
        policy = load_ssar_policy()
        reordered = dict(reversed(list(policy.items())))
        self.assertEqual(ssar_policy_hash(policy), ssar_policy_hash(reordered))
        changed = copy.deepcopy(policy)
        changed["type_rules"]["NAMED_SMALL_BODY"]["minimum_preserved_fraction"] = 0.9
        self.assertNotEqual(ssar_policy_hash(policy), ssar_policy_hash(changed))

    def test_policy_cannot_freeze_claim_confirmation_or_modify_core(self):
        request, policy = fixture()
        for field, value in (("policy_status", "FROZEN"), ("structural_scoring_modified", True), ("ontology_effect", "CONFIRM"), ("discriminator_effect", "PROMOTE")):
            changed = copy.deepcopy(policy); changed[field] = value
            with self.assertRaises(ValidationError): run_ssar(request, policy=changed)
        result = run_ssar(request, policy=policy)
        for field, value in (("analysis_scope", "CONFIRMATORY"), ("completion", "COMPLETE"), ("structural_scoring_modified", True)):
            changed = copy.deepcopy(result); changed[field] = value
            with self.assertRaises(ValidationError): validate_ssar_result(changed, policy=policy)

    def test_call_does_not_mutate_request_policy_or_core_outputs(self):
        request, policy = fixture()
        request_copy, policy_copy = copy.deepcopy(request), copy.deepcopy(policy)
        payload = json.loads((ROOT / "examples/precomputed-pillars.json").read_text())
        before = analyze_precomputed(payload)
        run_ssar(request, policy=policy)
        self.assertEqual(before, analyze_precomputed(payload))
        self.assertEqual(request, request_copy)
        self.assertEqual(policy, policy_copy)

    def test_scoped_state_precedence_and_counterevidence_with_partial_coverage(self):
        base = dict(scope="DOCUMENTARY_CORRESPONDENCE", policy_ref="P", rule_ref="R", coverage_sufficient=True)
        for kwargs, expected in [({}, "INSUFFICIENT"), ({"compatible": True}, "COMPATIBLE"),
                                ({"positive_complete": True}, "SUPPORTED"),
                                ({"mixed_or_underdetermined": True, "compatible": True}, "INSUFFICIENT"),
                                ({"coverage_sufficient": False}, "NOT_EVALUABLE"),
                                ({"rule_ref": None, "positive_complete": True}, "NOT_EVALUABLE"),
                                ({"coverage_sufficient": False, "excluding_counterevidence_refs": ["CE1"], "counterevidence_evaluable": True}, "CONTRADICTED"),
                                ({"excluding_counterevidence_refs": ["CE1"]}, "NOT_EVALUABLE")]:
            values = dict(base); values.update(kwargs)
            self.assertEqual(assess_ssar_claim(**values)["status"], expected)
        with self.assertRaises(ValueError): assess_ssar_claim(**dict(base, positive_complete=1))

    def test_supported_geometry_does_not_promote_unknown_or_contradicted_manifestation(self):
        common = dict(policy_ref="P", rule_ref="R")
        geometry = assess_ssar_claim(scope="STRUCTURAL_GEOMETRY", coverage_sufficient=True, positive_complete=True, **common)
        unknown = assess_ssar_claim(scope="DOCUMENTARY_CORRESPONDENCE", coverage_sufficient=False, **common)
        contradicted = assess_ssar_claim(scope="DOCUMENTARY_CORRESPONDENCE", coverage_sufficient=True, excluding_counterevidence_refs=["CE1"], counterevidence_evaluable=True, **common)
        self.assertEqual(geometry["status"], "SUPPORTED")
        self.assertEqual(unknown["status"], "NOT_EVALUABLE")
        self.assertEqual(contradicted["status"], "CONTRADICTED")
        self.assertNotIn("global_status", geometry)

    def test_output_references_hash_coverage_and_states_are_verified(self):
        request, policy = fixture(); result = run_ssar(request, policy=policy)
        for change in ("hash", "ref", "status", "coverage", "root", "hidden_pending"):
            out = copy.deepcopy(result)
            if change == "hash": out["policy_hash"] = "0" * 64
            if change == "ref": out["qualified_significators"] = ["ABSENT"]
            if change == "status": out["appearances"][0]["assessment"]["status"] = "COMPATIBLE"
            if change == "coverage": out["coverage"][0]["assessed_refs"] = []
            if change == "root": out["appearances"][0]["core_root_refs"] = []
            if change == "hidden_pending": out["coverage"][2]["status"] = "not_applicable"
            with self.assertRaises(ValueError): validate_ssar_result(out, policy=policy, request=request)

    def test_output_replay_detects_fabricated_geometry_or_robustness(self):
        request, policy = fixture(); result = run_ssar(request, policy=policy)
        result["appearances"][0]["matched_aspect"]["orb"] = 0
        with self.assertRaises(ValueError): validate_ssar_result(result, policy=policy, request=request)

    def test_effective_output_requires_input_context_for_reference_validation(self):
        request, policy = fixture()
        result = run_ssar(request, policy=policy)
        with self.assertRaisesRegex(ValueError, "entrada y política"):
            validate_ssar_result(result, policy=policy)
        result["appearances"][0]["core_root_refs"] = ["ABSENT"]
        with self.assertRaisesRegex(ValueError, "no reproduce"):
            validate_ssar_result(result, policy=policy, request=request)

    def test_public_synthetic_fixture_is_reproducible(self):
        artifact = json.loads((ROOT / "examples/ssar-contracts.synthetic.json").read_text())
        self.assertTrue(artifact["synthetic"])
        self.assertEqual(run_ssar(artifact["request"], policy=artifact["policy"]), artifact["result"])
        validate_ssar_result(artifact["result"], policy=artifact["policy"], request=artifact["request"])

    def test_output_rejects_fabricated_counts_or_thresholds_without_request(self):
        request, policy = fixture()
        for change in ("count", "fraction", "threshold", "orb", "function"):
            result = run_ssar(request, policy=policy)
            out = result["appearances"][0]
            if change == "count": out["robustness"]["preserved_count"] = 6
            if change == "fraction": out["robustness"]["preserved_fraction"] = 0.5
            if change == "threshold": out["robustness"]["required_fraction"] = 0.1
            if change == "orb": out["matched_aspect"]["orb_limit"] = 2
            if change == "function": out["function_id"] = "OTHER"
            messages = {"count": "aritméticamente", "fraction": "aritméticamente", "threshold": "regla publicada", "orb": "Exactitud geométrica", "function": "función o regla"}
            with self.assertRaisesRegex(ValueError, messages[change]):
                validate_ssar_result(result, policy=policy)

    def test_schemas_are_packaged_and_repository_wrappers_reference_same_contract(self):
        definitions = json.loads((ROOT / "src/almas_tfa/data/ssar-contract-definitions.json").read_text())
        Draft202012Validator.check_schema(definitions)
        for path in (ROOT / "schemas").glob("ssar-*.schema.json"):
            wrapper = json.loads(path.read_text())
            Draft202012Validator.check_schema(wrapper)
            target, fragment = wrapper["$ref"].split("#")
            self.assertEqual((path.parent / target).resolve(), ROOT / "src/almas_tfa/data/ssar-contract-definitions.json")
            self.assertIn(fragment.rsplit("/", 1)[1], definitions["$defs"])


class SSARDependencyTests(unittest.TestCase):
    def setUp(self):
        _, self.policy = fixture()
        self.units = [{"id": "U1", "appearance_ref": "A1", "technique": "SYNTH_A", "equivalence_key": "K1"},
                      {"id": "U2", "appearance_ref": "A2", "technique": "SYNTH_B", "equivalence_key": "K2"}]

    def request_with_units(self):
        request, policy = fixture()
        second = copy.deepcopy(request["appearances"][0])
        second["id"] = "A2"
        request["appearances"].append(second)
        request["units"] = copy.deepcopy(self.units)
        return request, policy

    def edge(self, relation):
        return {"a": "U1", "b": "U2", "relation": relation, "rule_id": self.policy["dependency_rules"][relation]}

    def test_two_groups_are_operational_not_independence_certification(self):
        graph = ssar_dependency_groups(self.units, [], self.policy)
        self.assertEqual(len(graph["effective_groups"]), 2)
        self.assertFalse(graph["statistical_independence_established"])

    def test_unknown_technical_statistical_edges_merge_without_equivalence(self):
        for relation in ("UNKNOWN", "TECHNICAL_DEPENDENCY", "STATISTICAL_DEPENDENCY"):
            graph = ssar_dependency_groups(self.units, [self.edge(relation)], self.policy)
            self.assertEqual(len(graph["effective_groups"]), 1)
            self.assertEqual(len(graph["equivalence_classes"]), 2)

    def test_unknown_dependency_is_transitive_and_order_deterministic(self):
        self.policy["technique_groups"]["SYNTH_C"] = "SYNTH_C"
        self.units.append({"id": "U3", "appearance_ref": "A3", "technique": "SYNTH_C", "equivalence_key": "K3"})
        edges = [self.edge("UNKNOWN"), {"a": "U2", "b": "U3", "relation": "TECHNICAL_DEPENDENCY", "rule_id": self.policy["dependency_rules"]["TECHNICAL_DEPENDENCY"]}]
        graph = ssar_dependency_groups(self.units, edges, self.policy)
        reversed_graph = ssar_dependency_groups(list(reversed(self.units)), edges, self.policy)
        self.assertEqual(graph, reversed_graph)
        self.assertEqual(graph["effective_groups"][0]["unit_refs"], ["U1", "U2", "U3"])
        self.assertEqual(len(graph["equivalence_classes"]), 3)

    def test_semantic_overlap_is_recorded_without_imposed_equivalence(self):
        graph = ssar_dependency_groups(self.units, [self.edge("SEMANTIC_OVERLAP")], self.policy)
        self.assertEqual(len(graph["effective_groups"]), 2)
        self.assertEqual(len(graph["equivalence_classes"]), 2)
        self.assertEqual(len(graph["edges"]), 1)

    def test_same_equivalence_key_is_deduplicated_without_missing_edge_loophole(self):
        self.units[1]["equivalence_key"] = "K1"
        graph = ssar_dependency_groups(self.units, [], self.policy)
        self.assertEqual(len(graph["equivalence_classes"]), 1)
        self.assertEqual(len(graph["effective_groups"]), 1)

    def test_same_appearance_cannot_count_twice_under_distinct_keys_or_techniques(self):
        self.units[1]["appearance_ref"] = "A1"
        graph = ssar_dependency_groups(self.units, [], self.policy)
        self.assertEqual(len(graph["equivalence_classes"]), 1)
        self.assertEqual(len(graph["effective_groups"]), 1)

    def test_relationship_chart_and_calculated_variants_share_published_groups(self):
        for a, b in (("COMPOSITE", "DAVISON"), ("BLACK_MOON_MEAN", "BLACK_MOON_OSCULATING"), ("VERTEX", "ANTI_VERTEX")):
            self.units[0]["technique"], self.units[1]["technique"] = a, b
            graph = ssar_dependency_groups(self.units, [], self.policy)
            self.assertEqual(len(graph["effective_groups"]), 1)
            self.assertEqual(len(graph["equivalence_classes"]), 2)

    def test_broken_edge_unknown_technique_and_rule_mismatch_are_invalid(self):
        for change in ("edge", "technique", "rule", "equivalence"):
            units, edge = copy.deepcopy(self.units), self.edge("UNKNOWN")
            if change == "edge": edge["b"] = "ABSENT"
            if change == "technique": units[0]["technique"] = "UNDECLARED"
            if change == "rule": edge["rule_id"] = "ABSENT"
            if change == "equivalence": edge = self.edge("EQUIVALENT")
            with self.assertRaises(ValueError): ssar_dependency_groups(units, [edge], self.policy)

    def test_blocked_units_do_not_enter_effective_groups(self):
        request, policy = self.request_with_units()
        for appearance in request["appearances"]:
            appearance["provenance"]["verification_status"] = "PENDING"
        graph = run_ssar(request, policy=policy)["dependency_graph"]
        self.assertEqual(graph["effective_groups"], [])
        self.assertEqual(graph["excluded_unit_refs"], ["U1", "U2"])

    def test_partition_tampering_and_double_membership_are_rejected(self):
        request, policy = self.request_with_units()
        request["edges"] = [self.edge("UNKNOWN")]
        result = run_ssar(request, policy=policy)
        graph = result["dependency_graph"]
        graph["effective_groups"] = [{"id": "GR:U1", "unit_refs": ["U1"]}, {"id": "GR:U2", "unit_refs": ["U2"]}]
        with self.assertRaises(ValueError): validate_ssar_result(result, policy=policy, request=request)
        result = run_ssar(request, policy=policy)
        result["dependency_graph"]["effective_groups"].append({"id": "OTHER", "unit_refs": ["U1"]})
        with self.assertRaises(ValueError): validate_ssar_result(result, policy=policy, request=request)


if __name__ == "__main__":
    unittest.main()
