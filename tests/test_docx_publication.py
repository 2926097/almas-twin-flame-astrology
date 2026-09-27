from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from almas_tfa.docx_publication import (
    DocxPublicationError,
    PROFILE_ID,
    build_authored_report_docx,
)


ROOT = Path(__file__).resolve().parents[1]
DOCX_AVAILABLE = importlib.util.find_spec("docx") is not None


@unittest.skipUnless(DOCX_AVAILABLE, "publication-docx extra not installed")
class DocxPublicationTests(unittest.TestCase):
    def authored(self):
        return json.loads(
            (ROOT / "examples/authored-report.synthetic.json").read_text(
                encoding="utf-8"
            )
        )

    def test_b5_docx_preserves_all_authored_narratives_and_bibliography(self):
        from docx import Document
        from docx.shared import Mm

        authored = self.authored()
        with TemporaryDirectory() as temp:
            output = Path(temp) / "report.docx"
            receipt = build_authored_report_docx(authored, output)

            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 0)
            self.assertEqual(receipt.profile_id, PROFILE_ID)
            self.assertEqual(receipt.section_count, 11)
            self.assertEqual(
                receipt.bibliography_count,
                len(authored["bibliography"]),
            )
            self.assertEqual(
                receipt.canonical_fingerprint,
                authored["canonical_fingerprint"],
            )
            self.assertEqual(len(receipt.docx_sha256), 64)

            document = Document(str(output))
            section = document.sections[0]
            self.assertEqual(section.page_width, Mm(176))
            self.assertEqual(section.page_height, Mm(250))

            paragraph_texts = [p.text for p in document.paragraphs]
            for authored_section in authored["sections"]:
                self.assertIn(authored_section["title"], paragraph_texts)
                self.assertIn(authored_section["narrative"], paragraph_texts)

            for entry in authored["bibliography"]:
                self.assertTrue(
                    any(
                        entry["citation_label"] in text
                        for text in paragraph_texts
                    )
                )

            self.assertIn(
                authored["canonical_fingerprint"],
                document.core_properties.comments,
            )
            footer_text = document.sections[0].footer.paragraphs[0].text
            self.assertIn(
                authored["canonical_fingerprint"][:12],
                footer_text,
            )

    def test_docx_publication_does_not_mutate_authored_report(self):
        authored = self.authored()
        snapshot = json.dumps(
            authored,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        with TemporaryDirectory() as temp:
            build_authored_report_docx(
                authored,
                Path(temp) / "report.docx",
            )
        self.assertEqual(
            json.dumps(
                authored,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            snapshot,
        )

    def test_invalid_document_kind_is_rejected_before_materialization(self):
        authored = self.authored()
        authored["document_kind"] = "OTHER"
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(
                DocxPublicationError,
                "document_kind",
            ):
                build_authored_report_docx(
                    authored,
                    Path(temp) / "report.docx",
                )


if __name__ == "__main__":
    unittest.main()
