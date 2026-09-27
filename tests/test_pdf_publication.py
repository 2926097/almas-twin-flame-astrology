from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from almas_tfa.pdf_publication import (
    PROFILE_ID,
    preflight_pdf,
    publish_authored_report_pdf,
)


ROOT = Path(__file__).resolve().parents[1]
PYPDF_AVAILABLE = importlib.util.find_spec("pypdf") is not None
DOCX_AVAILABLE = importlib.util.find_spec("docx") is not None
SOFFICE_AVAILABLE = shutil.which("soffice") is not None or shutil.which("libreoffice") is not None


@unittest.skipUnless(
    PYPDF_AVAILABLE and DOCX_AVAILABLE and SOFFICE_AVAILABLE,
    "publication-docx/publication-pdf extras or LibreOffice not installed",
)
class PdfPublicationTests(unittest.TestCase):
    def authored(self):
        return json.loads(
            (ROOT / "examples/authored-report.synthetic.json").read_text(
                encoding="utf-8"
            )
        )

    def test_end_to_end_pdf_publication_passes_b5_preflight(self):
        from pypdf import PdfReader

        authored = self.authored()
        with TemporaryDirectory() as temp:
            root = Path(temp)
            pdf = root / "report.pdf"
            docx = root / "report.docx"
            receipt = publish_authored_report_pdf(
                authored,
                pdf,
                output_docx=docx,
            )

            self.assertTrue(pdf.is_file())
            self.assertTrue(docx.is_file())
            self.assertGreaterEqual(receipt.page_count, 13)
            self.assertEqual(receipt.profile_id, PROFILE_ID)
            self.assertTrue(receipt.all_pages_b5)
            self.assertTrue(receipt.all_cropboxes_b5)
            self.assertTrue(receipt.all_fonts_embedded)
            self.assertEqual(receipt.empty_pages, ())
            self.assertTrue(receipt.text_complete)
            self.assertTrue(receipt.preflight_passed)
            self.assertEqual(len(receipt.pdf_sha256), 64)
            self.assertEqual(len(receipt.source_docx_sha256), 64)

            reader = PdfReader(str(pdf))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            self.assertIn(authored["canonical_fingerprint"], text)
            for section in authored["sections"]:
                self.assertIn(section["title"], text)

    def test_pdf_publication_does_not_mutate_authored_report(self):
        authored = self.authored()
        snapshot = json.dumps(
            authored,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        with TemporaryDirectory() as temp:
            publish_authored_report_pdf(
                authored,
                Path(temp) / "report.pdf",
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

    def test_preflight_rejects_non_b5_pdf(self):
        from pypdf import PdfWriter

        with TemporaryDirectory() as temp:
            pdf = Path(temp) / "a4.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=595.0, height=842.0)
            with pdf.open("wb") as handle:
                writer.write(handle)

            result = preflight_pdf(pdf)
            self.assertFalse(result.all_pages_b5)
            self.assertFalse(result.preflight_passed)


if __name__ == "__main__":
    unittest.main()
