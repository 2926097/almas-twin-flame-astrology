from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from almas_tfa.publication_authoring import (
    SECTION_IDS,
    build_publication_manuscript,
    canonical_fingerprint,
)
from almas_tfa.publication_docx import render_publication_docx


def canonical():
    return {
        "analysis_mode": "FULL",
        "models": {"AF": {"state": "SUPPORTED"}},
        "evidence": {"roots": []},
        "doctrine": {"claims": []},
    }


def report_model(c):
    fp = canonical_fingerprint(c)
    return {
        "canonical_fingerprint": fp,
        "canonical_fingerprint_verified": True,
        "sections": [
            {
                "section_id": section_id,
                "title": section_id,
                "section_state": "READY",
            }
            for section_id in SECTION_IDS
        ],
    }


def narrative_sections():
    sections = []
    for section_id in SECTION_IDS:
        sections.append(
            {
                "section_id": section_id,
                "title": section_id,
                "blocks": [
                    {
                        "block_id": f"{section_id}:B1",
                        "role": "ASTROLOGICAL_READING",
                        "epistemic_class": "B_TECHNIQUE",
                        "text": "Lectura astrológica sintética.",
                        "canonical_paths": ["models"],
                        "source_ids": [],
                    }
                ],
            }
        )
    return sections


class PublicationAuthoringTests(unittest.TestCase):
    def test_astrological_reading_requires_canonical_path(self):
        c = canonical()
        sections = narrative_sections()
        sections[0]["blocks"][0]["canonical_paths"] = []
        with self.assertRaisesRegex(ValueError, "ruta canónica"):
            build_publication_manuscript(
                report_document_model=report_model(c),
                canonical_analysis=c,
                title="Informe",
                subtitle=None,
                narrative_sections=sections,
            )

    def test_metaphysical_hermeneutics_requires_source_and_astrology(self):
        c = canonical()
        sections = narrative_sections()
        sections[0]["blocks"][0] = {
            "block_id": "S01_SYNTHESIS:M1",
            "role": "METAPHYSICAL_HERMENEUTICS",
            "epistemic_class": "E_PROJECT_HYPOTHESIS",
            "text": "Hermenéutica.",
            "canonical_paths": ["models"],
            "source_ids": [],
        }
        with self.assertRaisesRegex(ValueError, "al menos una fuente"):
            build_publication_manuscript(
                report_document_model=report_model(c),
                canonical_analysis=c,
                title="Informe",
                subtitle=None,
                narrative_sections=sections,
            )

    def test_fingerprint_mismatch_is_rejected(self):
        c = canonical()
        model = report_model(c)
        model["canonical_fingerprint"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            build_publication_manuscript(
                report_document_model=model,
                canonical_analysis=c,
                title="Informe",
                subtitle=None,
                narrative_sections=narrative_sections(),
            )

    def test_builds_exactly_eleven_sections(self):
        c = canonical()
        manuscript = build_publication_manuscript(
            report_document_model=report_model(c),
            canonical_analysis=c,
            title="Informe",
            subtitle="Lectura",
            narrative_sections=narrative_sections(),
        )
        self.assertEqual(
            [s["section_id"] for s in manuscript["sections"]],
            list(SECTION_IDS),
        )
        self.assertEqual(
            manuscript["authoring_principle"],
            "INTERPRETATION_PRIMARY_METHOD_SUPPORT",
        )

    def test_renders_b5_docx(self):
        try:
            from docx import Document
        except ImportError:
            self.skipTest("python-docx no instalado")
        c = canonical()
        manuscript = build_publication_manuscript(
            report_document_model=report_model(c),
            canonical_analysis=c,
            title="Informe ALMAS",
            subtitle="Lectura astrológica y metafísica",
            narrative_sections=narrative_sections(),
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            render_publication_docx(manuscript, path, profile="B5_BOOK")
            self.assertTrue(path.is_file())
            document = Document(path)
            section = document.sections[0]
            self.assertAlmostEqual(section.page_width.mm, 176.0, places=1)
            self.assertAlmostEqual(section.page_height.mm, 250.0, places=1)
            text = "\n".join(p.text for p in document.paragraphs)
            self.assertIn("Informe ALMAS", text)
            self.assertIn("Lectura astrológica sintética.", text)


if __name__ == "__main__":
    unittest.main()
