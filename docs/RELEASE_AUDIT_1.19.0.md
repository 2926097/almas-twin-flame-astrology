# Auditoría final de release · ALMAS 1.19.0

**Fecha:** 27 de septiembre de 2026  
**Rama auditada:** `release/1.19.0`  
**Base:** ALMAS 1.18.0  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** autoría interpretativa trazable y publicación B5 DOCX/PDF.

## Alcance

1.19.0 no reabre el núcleo cuantitativo ni el backend astronómico. La release construye la capa que faltaba entre `canonical_analysis` y el documento final.

Cadena material cerrada:

`canonical_analysis → M30 → M31 report_document_model → authored_report → DOCX B5 → PDF B5 → preflight → render visual`

La lectura astrológica y metafísica basada en fuentes constituye el contenido sustantivo. Los controles computacionales permanecen como soporte de precisión, procedencia y consistencia.

## Secuencia de implementación

- PR #15: puente M31 hacia evidencia, motivos semánticos y doctrina;
- PR #16: contrato de `authored_report`;
- PR #20: fixture interpretativo completo de once secciones;
- PR #21: publicación DOCX B5;
- PR #22: publicación PDF B5 y preflight.

Cada bloque se cerró antes de iniciar el siguiente para evitar convertir el endurecimiento técnico en un fin autónomo.

## Autoría

El `authored_report` conserva fingerprint, estado M31, orden de secciones, clases epistemológicas, referencias a evidencia y fuentes.

No crea una segunda verdad analítica y declara explícitamente:

- `canonical_values_mutated=false`;
- `new_calculations_performed=false`;
- `new_scores_created=false`;
- `metaphysical_scientific_validation_claimed=false`.

## DOCX

`ALMAS_B5_BOOK_V1` utiliza ISO B5 176 × 250 mm y copia la narrativa sin resumen ni reinterpretación.

La QA material verificó trece páginas completas, incluidos párrafos múltiples, límites interpretativos, bibliografía, URLs, footer y fingerprint.

## PDF

`ALMAS_B5_PDF_V1` convierte mediante LibreOffice con perfil temporal aislado.

El preflight comprueba geometría B5, CropBox, cifrado, páginas vacías, extracción de texto, fingerprint, títulos y embedding de fuentes.

La inspección local del artefacto de referencia registró:

- 13 páginas;
- 498,898 × 708,661 pt;
- PDF 1.7;
- no cifrado;
- fuentes detectadas embebidas;
- sin cortes, solapamientos ni desbordes.

La release no afirma PDF/X ni cumplimiento de requisitos de una imprenta concreta.

## CI final

En el head funcional previo al cierre:

- `Núcleo Python` 3.10: SUCCESS, 498 tests;
- `Núcleo Python` 3.12: SUCCESS, 498 tests;
- `Contrato público`: SUCCESS;
- `Backend astronómico`: SUCCESS;
- `Publicación DOCX`: SUCCESS;
- `Publicación PDF`: SUCCESS, 3 tests materiales.

## Estado epistemológico

La release mejora la capacidad de convertir datos astrológicos reproducibles y fuentes verificadas en una obra interpretativa trazable.

No constituye validación científica de la astrología ni de las ontologías metafísicas. No se ha ejecutado un holdout externo real y no existe ningún discriminador L3 real promovido.

La separación operativa queda fijada:

`cálculo reproducible → interpretación astrológica → hermenéutica basada en fuentes → publicación`

El cálculo es medio de control; el significado pertenece a la capa interpretativa.
