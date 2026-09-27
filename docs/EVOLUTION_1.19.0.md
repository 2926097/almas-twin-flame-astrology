# ALMAS 1.19.0 · Autoría interpretativa y publicación B5

## Objetivo

ALMAS 1.19.0 desplaza el centro de desarrollo desde el endurecimiento de infraestructura hacia el producto sustantivo del proyecto: la lectura astrológica y la hermenéutica/metafísica basada en fuentes.

La astronomía reproducible, la robustez, los modelos nulos, los índices y los schemas permanecen como infraestructura de cálculo, trazabilidad y control de calidad. No se presentan como validación científica de los significados metafísicos ni sustituyen la interpretación.

La release no añade técnicas astrológicas, pesos, thresholds, scores, discriminadores ni reglas ontológicas.

## I1 · Puente M31 → interpretación

M31 expone a las síntesis S01 y S10, cuando están disponibles:

- `evidence`;
- `semantic_motifs`;
- `doctrine`;
- ontología y limitaciones ya autorizadas por el canonical.

La síntesis puede integrar cálculo, doctrina, uso contemporáneo e hipótesis del proyecto sin convertir esas clases en una única categoría epistemológica.

## I2 · Contrato de autoría

`schemas/authored-report.schema.json` y `src/almas_tfa/authored_report.py` introducen `ALMAS_AUTHORED_REPORT`.

El contrato fija:

- `interpretive_center=ASTROLOGY_AND_SOURCE_BASED_METAPHYSICAL_HERMENEUTICS`;
- `technical_role=CALCULATION_TRACEABILITY_AND_QUALITY_CONTROL`;
- mismo `canonical_fingerprint` que M30/M31;
- mismo `report_state`;
- once secciones en orden canónico;
- rutas y clases epistemológicas autorizadas por M31;
- referencias a evidencias, claims doctrinales y bibliografía;
- `canonical_values_mutated=false`;
- `new_calculations_performed=false`;
- `new_scores_created=false`.

La trazabilidad es por sección para no convertir cada párrafo en una auditoría.

## I3 · Primer informe interpretativo completo

`examples/authored-report.synthetic.json` demuestra las once secciones con una narrativa extensa y sintética.

El ejemplo integra reconocimiento nodal, transformación Venus–Plutón, consonancia Sol–Luna, astrología dracónica, doctrina moderna de llamas gemelas, misión preencarnatoria y contraevidencia.

La firma sintética permite sostener modelos de alma gemela y continuidad kármica/contractual, mientras la categoría llama gemela permanece compatible pero no se impone como explicación exclusiva.

El fixture no representa personas ni relaciones reales.

## I4 · Publicación DOCX B5

`ALMAS_B5_BOOK_V1` materializa `authored_report` como DOCX:

- ISO B5 vertical, 176 × 250 mm;
- márgenes de 18 mm;
- once secciones;
- narrativas copiadas sin reescritura;
- soporte de varios párrafos;
- límites interpretativos;
- trazabilidad visualmente subordinada;
- bibliografía;
- huella canónica y paginación.

`python-docx==1.2.0` permanece como dependencia opcional de publicación.

## I5 · Publicación PDF y preflight

`ALMAS_B5_PDF_V1` convierte el DOCX mediante LibreOffice y aplica preflight fail-closed.

Comprueba:

- MediaBox B5 en todas las páginas;
- CropBox B5;
- PDF no cifrado;
- ninguna página vacía;
- texto extraíble;
- fingerprint completo;
- los once títulos de sección;
- fuentes embebidas;
- SHA-256 del DOCX y del PDF.

`pypdf==6.19.0` se incorpora como dependencia opcional de publicación.

Este perfil no declara PDF/X ni certificación para una imprenta concreta.

## I6 · Validación material

Sobre el cierre funcional de 1.19:

- Núcleo Python 3.10: **498 tests**, PASS;
- Núcleo Python 3.12: **498 tests**, PASS;
- Contrato público: PASS;
- Publicación DOCX: PASS;
- Publicación PDF: **3 tests materiales**, PASS;
- Backend astronómico: PASS como regresión independiente.

La QA visual renderizó e inspeccionó las 13 páginas del fixture B5. No se observaron cortes, solapamientos ni desbordes; la bibliografía y sus URLs permanecen dentro de caja.

El PDF verificado contiene 13 páginas, tamaño 498,898 × 708,661 pt, no está cifrado y las fuentes detectadas están embebidas.

## Invariantes

1. La publicación no recalcula astrología.
2. La publicación no añade scores ni discriminadores.
3. La autoría no modifica `canonical_analysis`.
4. Las fuentes doctrinales aportan significado y procedencia, no peso automático.
5. La contraevidencia se conserva en la narrativa.
6. La temporalidad activa arquitectura previa; no crea por sí sola el vínculo.
7. La infraestructura científica/computacional controla el dato y la materialización; no reemplaza la hermenéutica.
8. La fase técnica se considera cerrada cuando cumple su criterio de aceptación y no se prolonga sin un defecto concreto.
