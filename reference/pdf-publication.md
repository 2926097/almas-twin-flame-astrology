# Publicación PDF · ALMAS B5

## Posición en el pipeline

El PDF se genera únicamente después de cerrar la autoría y el DOCX:

`canonical_analysis → M30 → M31 → authored_report → DOCX → PDF → preflight → render visual`

No existe una segunda redacción en PDF. La conversión materializa el DOCX aprobado.

## Perfil ALMAS_B5_PDF_V1

El primer perfil PDF exige:

- formato B5 vertical en todas las páginas;
- CropBox también B5;
- PDF no cifrado;
- ninguna página vacía;
- texto extraíble;
- presencia de la huella canónica completa;
- presencia de los once títulos de sección;
- todas las fuentes utilizadas embebidas;
- SHA-256 del DOCX fuente y del PDF final.

El perfil no declara PDF/X, sangrado ni certificación específica de imprenta. Es una base reproducible para lectura y producción digital; los requisitos de una imprenta concreta se añaden sólo cuando estén documentados.

## Conversión

`src/almas_tfa/pdf_publication.py` utiliza LibreOffice/soffice en modo headless con un perfil temporal aislado.

La dependencia Python es opcional:

`publication-pdf = ["pypdf==6.19.0"]`

LibreOffice es una dependencia externa de materialización, no del núcleo analítico.

## Preflight

`preflight_pdf()` verifica geometría, fuentes, extracción de texto, páginas vacías y cifrado.

`publish_authored_report_pdf()` opera fail-closed: si el preflight no pasa, no devuelve un receipt de publicación válida.

El receipt contiene:

- `profile_id`;
- `canonical_fingerprint`;
- SHA-256 del DOCX;
- SHA-256 del PDF;
- número de páginas;
- estados B5/CropBox;
- inventario de fuentes;
- estado de fuentes embebidas;
- páginas vacías;
- estado de completitud textual;
- `preflight_passed`.

## Inspección visual

El preflight estructural no reemplaza la inspección visual.

Antes de cerrar una release material se renderizan todas las páginas del PDF y se comprueba:

- ausencia de cortes y solapamientos;
- márgenes correctos;
- glifos legibles;
- bibliografía contenida en caja;
- paginación y pies correctos.

## Límite epistemológico

La publicación PDF no cambia ninguna conclusión. No modifica modelos, índices, doctrina, contraevidencia ni interpretación. La ciencia/computación permanece como control del dato y de la materialización; el contenido sustantivo sigue siendo la lectura astrológica y metafísica basada en fuentes.
