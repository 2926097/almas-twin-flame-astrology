from __future__ import annotations

import json
from pathlib import Path
import unittest

from almas_tfa.personal_reference_router import load_personal_reference_router


ROOT = Path(__file__).resolve().parents[1]


class FixedStarSourcePreregistrationTests(unittest.TestCase):
    def test_sources_and_concept_are_registered_without_router_activation(self):
        sources = json.loads(
            (ROOT / "reference/source-registry.json").read_text(encoding="utf-8")
        )
        concepts = json.loads(
            (ROOT / "reference/concept-registry.json").read_text(encoding="utf-8")
        )
        source_ids = {item["id"] for item in sources["entries"]}
        self.assertIn("brady_book_fixed_stars_1998", source_ids)
        self.assertIn("ptolemy_tetrabiblos_1_9_fixed_stars", source_ids)

        concept = next(
            item
            for item in concepts["concepts"]
            if item["id"] == "FIXED_STAR_ASTROLOGY"
        )
        self.assertEqual(concept["concept_class"], "TECHNICAL_METHOD")
        self.assertIn(
            "brady_book_fixed_stars_1998",
            concept["method_sources"],
        )
        self.assertIn(
            "ptolemy_tetrabiblos_1_9_fixed_stars",
            concept["historical_sources"],
        )

        router = load_personal_reference_router()
        fixed = router["domains"]["fixed_stars"]
        self.assertEqual(fixed["status"], "SOURCE_GAP")
        self.assertEqual(fixed["source_ids"], [])

    def test_preregistered_sources_are_support_only_in_scope(self):
        sources = json.loads(
            (ROOT / "reference/source-registry.json").read_text(encoding="utf-8")
        )
        entries = {item["id"]: item for item in sources["entries"]}
        for source_id in (
            "brady_book_fixed_stars_1998",
            "ptolemy_tetrabiblos_1_9_fixed_stars",
        ):
            entry = entries[source_id]
            self.assertEqual(entry["evidence_scope"], "METHOD_DESCRIPTION")
            joined = " ".join(entry["does_not_support"]).lower()
            self.assertIn("ontolog", joined)


if __name__ == "__main__":
    unittest.main()
