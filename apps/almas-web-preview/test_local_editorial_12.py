"""Synthetic-only 12-section local editorial publication contract tests."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
import json

sys.path.insert(0,str(Path(__file__).resolve().parent))
from local_editorial_12 import (SECTION_ORDER, FORMAT, EditorialGateError,
    digest, make_scaffold, validate_authored, verify_m31, render_docx,
    read_bundle, _read_json)

class EditorialTwelveTests(unittest.TestCase):
    def setUp(self):
        self.canonical={"models":{"AF":{"state":"INSUFFICIENT"}},"evidence":[]}
        fp=digest(self.canonical)
        self.gate={"state":"PARTIAL","reportable":True,"canonical_values_mutated":False,
                   "canonical_fingerprint":fp}
        self.model={"report_state":"PARTIAL","canonical_fingerprint":fp,
            "canonical_fingerprint_verified":True,"canonical_values_mutated":False,
            "canonical_values_embedded":False,"prose_generated":False,
            "sections":[{"section_id":sid,"order":i+1,"title":"Capítulo "+str(i+1),
                "section_state":"AVAILABLE","available_paths":["models","evidence"],
                "epistemic_classes_allowed":["A_CALCULATED","C_DOCTRINE"]}
                for i,sid in enumerate(SECTION_ORDER)]}
        self.authored=make_scaffold(self.canonical,self.gate,self.model)
    def fill(self):
        report=deepcopy(self.authored)
        for section in report["sections"]:
            section["narrative"]="Descripción sintética basada en el estado del modelo."
            section["canonical_paths_used"]=["models"]
            section["epistemic_classes_used"]=["A_CALCULATED"]
        return report
    def test_scaffold_has_twelve_empty_sections_and_never_claims_authored(self):
        self.assertEqual(self.authored["format"],FORMAT)
        self.assertEqual(len(self.authored["sections"]),12)
        self.assertEqual(self.authored["sections"][-1]["section_id"],"S12_PHASE_DYNAMICS")
        with self.assertRaisesRegex(EditorialGateError,"TEXT_AND_REFERENCES"):
            validate_authored(self.canonical,self.gate,self.model,self.authored)
    def test_manually_authored_all_twelve_is_valid_with_trace(self):
        doc=self.fill()
        validate_authored(self.canonical,self.gate,self.model,doc)
        self.assertEqual(verify_m31(self.canonical,self.gate,self.model),
                         doc["canonical_fingerprint"])
    def test_fingerprint_mutation_unavailable_data_and_bad_sources_fail(self):
        authored=self.fill()
        for mutate,code in [
            (lambda x:x.update(canonical_fingerprint="0"*64),"EDITORIAL_HEADER_INVALID"),
            (lambda x:x["sections"][1].update(canonical_paths_used=["raw_input"]),"EDITORIAL_SECTION_PROVENANCE_INVALID"),
            (lambda x:x["sections"][0].update(epistemic_classes_used=["C_DOCTRINE"]),"EDITORIAL_DOCTRINAL_SOURCE_REQUIRED"),
            (lambda x:x["sections"].pop(),"EDITORIAL_SECTIONS_INVALID"),
        ]:
            data=deepcopy(authored);mutate(data)
            with self.subTest(code=code),self.assertRaisesRegex(EditorialGateError,code):
                validate_authored(self.canonical,self.gate,self.model,data)
        mod=deepcopy(self.model)
        mod["sections"][0]["section_state"]="NOT_AVAILABLE"
        with self.assertRaisesRegex(EditorialGateError,"UNAVAILABLE_CANNOT"):
            validate_authored(self.canonical,self.gate,mod,authored)
        mod=deepcopy(self.model);mod["canonical_fingerprint"]="f"*64
        with self.assertRaisesRegex(EditorialGateError,"M30_M31_INTEGRITY_INVALID"):
            make_scaffold(self.canonical,self.gate,mod)
    def test_local_export_bundle_enters_same_twelve_section_gate(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"almas-local-results.json"
            package={"canonical_analysis":self.canonical,
                     "m30":self.gate,"m31":self.model,
                     "state":"PARTIAL","module_statuses":{},
                     "atlas":{"synthetic":True}}
            path.write_text(json.dumps(package),encoding="utf-8")
            canonical,gate,model=read_bundle(path)
            self.assertEqual(make_scaffold(canonical,gate,model),self.authored)
            self.assertEqual(verify_m31(canonical,gate,model),digest(self.canonical))

    def test_bundle_fail_closed_for_missing_mismatched_or_malformed_documents(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"almas-local-results.json"
            package={"canonical_analysis":self.canonical,"m30":self.gate,
                     "m31":self.model,"state":"PARTIAL"}
            cases=(
                ({**package,"m31":None},"LOCAL_BUNDLE_DOCUMENTS_MISSING"),
                ({**package,"state":"READY"},"LOCAL_BUNDLE_STATE_MISMATCH"),
                ({**package,"m30":{**self.gate,"canonical_fingerprint":"0"*64}},
                 "M30_M31_INTEGRITY_INVALID"),
            )
            for document,expected in cases:
                path.write_text(json.dumps(document),encoding="utf-8")
                with self.subTest(expected=expected),self.assertRaisesRegex(
                        EditorialGateError,expected):
                    canonical,gate,model=read_bundle(path)
                    make_scaffold(canonical,gate,model)

    def test_json_input_disallows_duplicate_keys_and_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"invalid.json"
            for raw,expected in (
                ('{"m30":{},"m30":{}}',"DUPLICATE_JSON_KEY"),
                ('{"m30":{"state":"READY","state":"PARTIAL"}}',
                 "DUPLICATE_JSON_KEY"),
                ('{"value":NaN}',"NONFINITE_JSON_NUMBER"),
                ('{"value":Infinity}',"NONFINITE_JSON_NUMBER"),
            ):
                path.write_text(raw,encoding="utf-8")
                with self.subTest(raw=raw),self.assertRaisesRegex(
                        EditorialGateError,expected):
                    _read_json(path)

    def test_pdf_is_preflighted_in_b5_and_keeps_fingerprint(self):
        from shutil import which
        from local_editorial_12 import render_pdf_from_docx
        if not which("soffice"):
            self.fail("LibreOffice is required for the PDF integration gate")
        authored=self.fill()
        validate_authored(self.canonical,self.gate,self.model,authored)
        with tempfile.TemporaryDirectory() as td:
            docx_path=Path(td)/"synthetic.docx"
            pdf_path=Path(td)/"synthetic.pdf"
            render_docx(authored,docx_path)
            receipt=render_pdf_from_docx(docx_path,pdf_path,
                fingerprint=authored["canonical_fingerprint"],
                section_titles=[x["title"] for x in authored["sections"]])
            self.assertTrue(receipt["preflight_passed"])
            self.assertEqual(len(receipt["pdf_sha256"]),64)
            self.assertGreater(receipt["pages"],0)
            self.assertGreater(pdf_path.stat().st_size,1000)

    def test_docx_is_written_locally_in_b5_without_original_canonical(self):
        try:
            from docx import Document
        except ImportError:
            self.skipTest("python-docx optional")
        authored=self.fill()
        validate_authored(self.canonical,self.gate,self.model,authored)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"synthetic.docx"
            out_sha=render_docx(authored,path)
            self.assertEqual(len(out_sha),64)
            self.assertTrue(path.stat().st_size>1000)
            result=Document(path)
            self.assertAlmostEqual(result.sections[0].page_width.mm,176,delta=1)
            self.assertAlmostEqual(result.sections[0].page_height.mm,250,delta=1)
            text=" ".join(p.text for p in result.paragraphs)
            self.assertIn("Capítulo 12",text)
            self.assertIn("No demuestra científicamente",text)

if __name__=="__main__":
    unittest.main()
