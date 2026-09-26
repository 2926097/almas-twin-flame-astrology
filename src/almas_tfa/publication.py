from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Protocol

from .capabilities import route_capabilities


class CanonicalFingerprintError(ValueError):
    pass


@dataclass(frozen=True)
class ReportProfile:
    profile_id: str
    page_width_mm: float
    page_height_mm: float
    margin_inside_mm: float
    margin_outside_mm: float
    margin_top_mm: float
    margin_bottom_mm: float
    body_font: str
    sans_font: str
    body_size_pt: float
    caption_size_pt: float
    line_spacing_multiple: float
    mirrored_headers: bool
    part_openings_recto: bool
    image_min_ppi: int


REPORT_PROFILES = {
    "B5_BOOK": ReportProfile(
        "B5_BOOK", 176.0, 250.0, 22.0, 18.0, 18.0, 20.0,
        "Noto Serif", "Nimbus Sans", 10.5, 8.6, 1.17, True, True, 270
    ),
    "A4_PROFESSIONAL": ReportProfile(
        "A4_PROFESSIONAL", 210.0, 297.0, 22.0, 18.0, 20.0, 20.0,
        "Noto Serif", "Nimbus Sans", 10.5, 8.8, 1.18, True, False, 240
    ),
}


class PublicationBackend(Protocol):
    backend_id: str
    backend_version: str

    def render(
        self,
        plan: Mapping[str, Any],
        canonical: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        ...


def _fingerprint(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _report_kind(report_model: Mapping[str, Any]) -> str:
    if report_model.get("document_kind") == "ALMAS_ANALYTICAL_REPORT_MODEL":
        return "RELATIONAL_RESEARCH"
    if report_model.get("document_kind") == "ALMAS_PERSONAL_REPORT_MODEL":
        return str(report_model.get("report_mode"))
    raise ValueError("document_kind no reconocido para publicación.")


def build_publication_plan(
    canonical: Mapping[str, Any],
    report_model: Mapping[str, Any],
    *,
    profile_id: str = "B5_BOOK",
    output_format: str = "PDF",
    available_capabilities: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    if profile_id not in REPORT_PROFILES:
        raise ValueError(f"Perfil editorial no reconocido: {profile_id}")

    expected = report_model.get("canonical_fingerprint")
    actual = _fingerprint(canonical)
    if expected != actual:
        raise CanonicalFingerprintError(
            "El report model no corresponde al objeto canónico suministrado."
        )
    if report_model.get("canonical_fingerprint_verified") is not True:
        raise CanonicalFingerprintError("El report model no declara fingerprint verificado.")

    report_kind = _report_kind(report_model)
    route = route_capabilities(
        report_kind,
        available_capabilities,
        output_format=output_format,
    )
    profile = REPORT_PROFILES[profile_id]

    return {
        "plan_version": "1.0.0",
        "pipeline": "P00-P05",
        "report_kind": report_kind,
        "output_format": output_format.upper(),
        "canonical_fingerprint": actual,
        "canonical_values_mutated": False,
        "report_model_source": report_model.get("document_kind"),
        "profile": asdict(profile),
        "sections": [
            {
                "section_id": section.get("section_id"),
                "order": section.get("order"),
                "title": section.get("title"),
                "source_paths": section.get("source_paths")
                or section.get("available_paths", []),
                "state": section.get("section_state"),
            }
            for section in report_model.get("sections", [])
        ],
        "capability_route": route,
        "authoring_contract": {
            "language": "es",
            "source_of_truth": report_model.get("canonical_source"),
            "no_silent_recalculation": True,
            "no_silent_missing_data_fill": True,
            "reader_facing_labels": ["DATO", "LECTURA", "HIPÓTESIS"],
        },
        "qa_requirements": {
            "preflight_required": output_format.upper() == "PDF",
            "render_every_page": output_format.upper() == "PDF",
            "inspect_every_page": output_format.upper() == "PDF",
            "fonts_embedded": output_format.upper() == "PDF",
            "minimum_image_ppi": profile.image_min_ppi,
            "no_clipped_text": True,
            "no_broken_glyphs": True,
            "bookmarks_required": output_format.upper() == "PDF",
            "page_size_mm": [profile.page_width_mm, profile.page_height_mm],
        },
        "publication_backend_required": output_format.upper() in {"DOCX", "PDF"},
    }


def render_with_backend(
    plan: Mapping[str, Any],
    canonical: Mapping[str, Any],
    backend: PublicationBackend,
) -> dict[str, Any]:
    result = dict(backend.render(plan, canonical))
    return {
        "backend": {"id": backend.backend_id, "version": backend.backend_version},
        "canonical_fingerprint": plan["canonical_fingerprint"],
        "result": result,
    }


def evaluate_publication_qa(
    plan: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    qa = plan["qa_requirements"]
    failures: list[str] = []

    expected_size = tuple(float(x) for x in qa["page_size_mm"])
    actual_size = tuple(float(x) for x in metrics.get("page_size_mm", ()))
    if actual_size != expected_size:
        failures.append("PAGE_SIZE_MISMATCH")

    page_count = int(metrics.get("page_count", 0))
    rendered_pages = int(metrics.get("rendered_pages", 0))
    if qa["render_every_page"] and rendered_pages != page_count:
        failures.append("NOT_ALL_PAGES_RENDERED")
    if qa["fonts_embedded"] and not metrics.get("fonts_embedded", False):
        failures.append("FONTS_NOT_EMBEDDED")
    if float(metrics.get("minimum_image_ppi", 0)) < float(qa["minimum_image_ppi"]):
        failures.append("IMAGE_RESOLUTION_BELOW_PROFILE")
    if int(metrics.get("clipping_errors", 0)):
        failures.append("CLIPPING_DETECTED")
    if int(metrics.get("broken_glyphs", 0)):
        failures.append("BROKEN_GLYPHS")
    if qa["bookmarks_required"] and not metrics.get("bookmarks_present", False):
        failures.append("BOOKMARKS_MISSING")

    return {
        "qa_version": "1.0.0",
        "state": "PASS" if not failures else "FAIL",
        "failures": failures,
        "page_count": page_count,
        "rendered_pages": rendered_pages,
    }
