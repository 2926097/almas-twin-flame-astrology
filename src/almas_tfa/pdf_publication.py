from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence

from .docx_publication import (
    build_authored_report_docx,
    build_personal_authored_report_docx,
)


PROFILE_ID = "ALMAS_B5_PDF_V1"
PERSONAL_PROFILE_ID = "ALMAS_B5_PERSONAL_PDF_V1"
B5_WIDTH_PT = 176.0 / 25.4 * 72.0
B5_HEIGHT_PT = 250.0 / 25.4 * 72.0
PAGE_TOLERANCE_PT = 1.0


class PdfPublicationError(ValueError):
    pass


@dataclass(frozen=True)
class PdfPreflightResult:
    page_count: int
    all_pages_b5: bool
    all_cropboxes_b5: bool
    all_fonts_embedded: bool
    font_names: tuple[str, ...]
    empty_pages: tuple[int, ...]
    text_complete: bool
    required_text_missing: tuple[str, ...]
    encrypted: bool
    preflight_passed: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PdfPublicationReceipt:
    profile_id: str
    output_path: str
    canonical_fingerprint: str
    source_docx_sha256: str
    pdf_sha256: str
    page_count: int
    all_pages_b5: bool
    all_cropboxes_b5: bool
    all_fonts_embedded: bool
    font_names: tuple[str, ...]
    empty_pages: tuple[int, ...]
    text_complete: bool
    preflight_passed: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _require_pypdf():
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "La publicación PDF requiere el extra opcional "
            "'publication-pdf' (pypdf==6.19.0)."
        ) from exc
    return PdfReader


def _resolve_soffice(explicit: str | Path | None = None) -> str:
    if explicit is not None:
        candidate = str(explicit)
        if Path(candidate).is_file():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
        raise PdfPublicationError(f"No se encuentra LibreOffice/soffice: {candidate}")

    for name in ("soffice", "libreoffice"):
        resolved = shutil.which(name)
        if resolved:
            return resolved
    raise PdfPublicationError(
        "No se encuentra LibreOffice. Instale soffice/libreoffice para convertir DOCX a PDF."
    )


def convert_docx_to_pdf(
    docx_path: str | Path,
    output_pdf: str | Path,
    *,
    soffice_path: str | Path | None = None,
) -> Path:
    """Convierte un DOCX aprobado a PDF sin modificar su contenido."""

    source = Path(docx_path)
    if not source.is_file():
        raise PdfPublicationError(f"DOCX inexistente: {source}")

    output = Path(output_pdf)
    output.parent.mkdir(parents=True, exist_ok=True)
    soffice = _resolve_soffice(soffice_path)

    with TemporaryDirectory(prefix="almas-lo-") as temp:
        temp_root = Path(temp)
        converted_dir = temp_root / "out"
        converted_dir.mkdir()
        home = temp_root / "home"
        profile = temp_root / "profile"
        home.mkdir()
        profile.mkdir()

        env = os.environ.copy()
        env["HOME"] = str(home)
        env["SAL_USE_VCLPLUGIN"] = "svp"

        cmd = [
            soffice,
            "--headless",
            "--nologo",
            "--nolockcheck",
            f"-env:UserInstallation={profile.resolve().as_uri()}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(converted_dir),
            str(source.resolve()),
        ]
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

        produced = converted_dir / f"{source.stem}.pdf"
        if not produced.is_file() or produced.stat().st_size == 0:
            matches = list(converted_dir.glob("*.pdf"))
            if len(matches) == 1:
                produced = matches[0]

        if not produced.is_file() or produced.stat().st_size == 0:
            raise PdfPublicationError(
                "LibreOffice no produjo un PDF válido. "
                f"exit={proc.returncode}; stdout={proc.stdout!r}; stderr={proc.stderr!r}"
            )

        shutil.copy2(produced, output)

    return output


def _object(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def _font_is_embedded(font: Any) -> bool:
    font = _object(font)
    descriptor = font.get("/FontDescriptor") if hasattr(font, "get") else None
    if descriptor is not None:
        descriptor = _object(descriptor)
        if any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")):
            return True

    descendants = font.get("/DescendantFonts") if hasattr(font, "get") else None
    if descendants is not None:
        descendants = _object(descendants)
        for descendant in descendants:
            descendant = _object(descendant)
            descriptor = descendant.get("/FontDescriptor")
            if descriptor is None:
                continue
            descriptor = _object(descriptor)
            if any(
                key in descriptor
                for key in ("/FontFile", "/FontFile2", "/FontFile3")
            ):
                return True
    return False


def _font_inventory(reader: Any) -> dict[str, bool]:
    fonts: dict[str, bool] = {}
    for page in reader.pages:
        resources = page.get("/Resources")
        if resources is None:
            continue
        resources = _object(resources)
        page_fonts = resources.get("/Font")
        if page_fonts is None:
            continue
        page_fonts = _object(page_fonts)
        for _name, ref in page_fonts.items():
            font = _object(ref)
            base_font = str(font.get("/BaseFont") or _name)
            fonts[base_font] = fonts.get(base_font, False) or _font_is_embedded(font)
    return fonts


def _box_is_b5(box: Any) -> bool:
    width = float(box.width)
    height = float(box.height)
    return (
        abs(width - B5_WIDTH_PT) <= PAGE_TOLERANCE_PT
        and abs(height - B5_HEIGHT_PT) <= PAGE_TOLERANCE_PT
    )


def preflight_pdf(
    pdf_path: str | Path,
    *,
    required_text: Sequence[str] = (),
) -> PdfPreflightResult:
    """Comprueba la materialización PDF; no evalúa contenido interpretativo."""

    PdfReader = _require_pypdf()
    path = Path(pdf_path)
    if not path.is_file() or path.stat().st_size == 0:
        raise PdfPublicationError(f"PDF inexistente o vacío: {path}")

    reader = PdfReader(str(path))
    encrypted = bool(reader.is_encrypted)
    if encrypted:
        return PdfPreflightResult(
            page_count=len(reader.pages),
            all_pages_b5=False,
            all_cropboxes_b5=False,
            all_fonts_embedded=False,
            font_names=(),
            empty_pages=(),
            text_complete=False,
            required_text_missing=tuple(required_text),
            encrypted=True,
            preflight_passed=False,
        )

    page_count = len(reader.pages)
    all_pages_b5 = page_count > 0 and all(
        _box_is_b5(page.mediabox) for page in reader.pages
    )
    all_cropboxes_b5 = page_count > 0 and all(
        _box_is_b5(page.cropbox) for page in reader.pages
    )

    page_texts = [(page.extract_text() or "").strip() for page in reader.pages]
    empty_pages = tuple(
        index
        for index, text in enumerate(page_texts, start=1)
        if not text
    )
    joined_text = "\n".join(page_texts)
    missing = tuple(text for text in required_text if text not in joined_text)
    text_complete = not missing

    fonts = _font_inventory(reader)
    all_fonts_embedded = bool(fonts) and all(fonts.values())

    passed = (
        page_count > 0
        and all_pages_b5
        and all_cropboxes_b5
        and all_fonts_embedded
        and not empty_pages
        and text_complete
        and not encrypted
    )
    return PdfPreflightResult(
        page_count=page_count,
        all_pages_b5=all_pages_b5,
        all_cropboxes_b5=all_cropboxes_b5,
        all_fonts_embedded=all_fonts_embedded,
        font_names=tuple(sorted(fonts)),
        empty_pages=empty_pages,
        text_complete=text_complete,
        required_text_missing=missing,
        encrypted=encrypted,
        preflight_passed=passed,
    )


def _publish_report_pdf(
    authored_report: Mapping[str, Any],
    output_pdf: str | Path,
    *,
    build_docx: Any,
    profile_id: str,
    output_docx: str | Path | None,
    title: str,
    subtitle: str,
    soffice_path: str | Path | None,
) -> PdfPublicationReceipt:
    output_pdf_path = Path(output_pdf)
    fingerprint = authored_report.get("canonical_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise PdfPublicationError("canonical_fingerprint inválido.")

    titles = [
        str(section.get("title"))
        for section in authored_report.get("sections", [])
        if isinstance(section, Mapping) and section.get("title")
    ]
    required_text = [fingerprint, *titles]

    with TemporaryDirectory(prefix="almas-pdf-") as temp:
        temp_root = Path(temp)
        docx_path = (
            Path(output_docx)
            if output_docx is not None
            else temp_root / "authored-report.docx"
        )
        build_docx(
            authored_report,
            docx_path,
            title=title,
            subtitle=subtitle,
        )
        source_docx_sha256 = _sha256_file(docx_path)

        convert_docx_to_pdf(
            docx_path,
            output_pdf_path,
            soffice_path=soffice_path,
        )

    result = preflight_pdf(
        output_pdf_path,
        required_text=required_text,
    )
    if not result.preflight_passed:
        raise PdfPublicationError(
            "Preflight PDF no superado: "
            f"B5={result.all_pages_b5}; crop={result.all_cropboxes_b5}; "
            f"fonts={result.all_fonts_embedded}; empty={result.empty_pages}; "
            f"missing={result.required_text_missing}; "
            f"encrypted={result.encrypted}"
        )

    return PdfPublicationReceipt(
        profile_id=profile_id,
        output_path=str(output_pdf_path),
        canonical_fingerprint=fingerprint,
        source_docx_sha256=source_docx_sha256,
        pdf_sha256=_sha256_file(output_pdf_path),
        page_count=result.page_count,
        all_pages_b5=result.all_pages_b5,
        all_cropboxes_b5=result.all_cropboxes_b5,
        all_fonts_embedded=result.all_fonts_embedded,
        font_names=result.font_names,
        empty_pages=result.empty_pages,
        text_complete=result.text_complete,
        preflight_passed=result.preflight_passed,
    )


def publish_authored_report_pdf(
    authored_report: Mapping[str, Any],
    output_pdf: str | Path,
    *,
    output_docx: str | Path | None = None,
    title: str = "ALMAS · Informe interpretativo",
    subtitle: str = (
        "Astrología relacional y hermenéutica metafísica basada en fuentes"
    ),
    soffice_path: str | Path | None = None,
) -> PdfPublicationReceipt:
    """Publica el authored_report relacional como PDF B5."""

    return _publish_report_pdf(
        authored_report,
        output_pdf,
        build_docx=build_authored_report_docx,
        profile_id=PROFILE_ID,
        output_docx=output_docx,
        title=title,
        subtitle=subtitle,
        soffice_path=soffice_path,
    )


def publish_personal_authored_report_pdf(
    authored_report: Mapping[str, Any],
    output_pdf: str | Path,
    *,
    output_docx: str | Path | None = None,
    title: str = "ALMAS · Informe astrológico personal",
    subtitle: str = "Astrología natal y hermenéutica basada en fuentes",
    soffice_path: str | Path | None = None,
) -> PdfPublicationReceipt:
    """Publica el authored_report personal con el mismo preflight B5."""

    return _publish_report_pdf(
        authored_report,
        output_pdf,
        build_docx=build_personal_authored_report_docx,
        profile_id=PERSONAL_PROFILE_ID,
        output_docx=output_docx,
        title=title,
        subtitle=subtitle,
        soffice_path=soffice_path,
    )


def publish_report_pdf(
    authored_report: Mapping[str, Any],
    output_pdf: str | Path,
    *,
    output_docx: str | Path | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    soffice_path: str | Path | None = None,
) -> PdfPublicationReceipt:
    """Dispatch de publicación PDF según document_kind."""

    kind = authored_report.get("document_kind")
    if kind == "ALMAS_AUTHORED_REPORT":
        return publish_authored_report_pdf(
            authored_report,
            output_pdf,
            output_docx=output_docx,
            title=title or "ALMAS · Informe interpretativo",
            subtitle=subtitle
            or "Astrología relacional y hermenéutica metafísica basada en fuentes",
            soffice_path=soffice_path,
        )
    if kind == "ALMAS_PERSONAL_AUTHORED_REPORT":
        return publish_personal_authored_report_pdf(
            authored_report,
            output_pdf,
            output_docx=output_docx,
            title=title or "ALMAS · Informe astrológico personal",
            subtitle=subtitle
            or "Astrología natal y hermenéutica basada en fuentes",
            soffice_path=soffice_path,
        )
    raise PdfPublicationError(
        f"document_kind no publicable: {kind}"
    )
