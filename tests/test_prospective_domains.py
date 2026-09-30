"""Paso 15: fecha y dominios fijados antes de observación, sin predicción."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
RECORD=json.loads((ROOT/"reference/prospective-domains-2027-03-29.json").read_text())
SCHEMA=json.loads((ROOT/"schemas/prospective-domains.schema.json").read_text())

class ProspectiveDomainsTests(unittest.TestCase):
    def test_domains_and_phase_mappings_are_preregistered_as_not_evaluable(self):
        Draft202012Validator(SCHEMA,format_checker=Draft202012Validator.FORMAT_CHECKER).validate(RECORD)
        self.assertEqual(RECORD["observation_date"],"2027-03-29")
        self.assertEqual(len(RECORD["domains_to_observe"]),4)
        self.assertEqual({x["phase_id"] for x in RECORD["phase_mappings"]},{"awakening_candidate","surrender_candidate"})
        self.assertTrue(all(x["status"]=="NOT_EVALUABLE" for x in RECORD["phase_mappings"]))

    def test_no_reunion_or_decisions_or_identity_link_are_predicted(self):
        self.assertFalse(RECORD["identity_linked_in_public_record"])
        self.assertEqual(RECORD["evidence_predeclared"],[])
        self.assertFalse(RECORD["meeting_or_reunion_predeclared"])
        self.assertFalse(RECORD["future_decisions_predicted"])
        self.assertEqual(RECORD["ontology_status"],"INSUFFICIENT")

if __name__=="__main__":
    unittest.main()
