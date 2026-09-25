# Modelo documental de informe · M31

## 1. Finalidad

M31 transforma un análisis autorizado por M30 en un `report_document_model` declarativo.

No redacta conclusiones, no copia valores analíticos y no renderiza documentos.

Cadena:

`canonical_analysis → M30 report_gate → M31 report_document_model → autoría/publicación`

## 2. Condiciones de entrada

M31 exige:

- `report_gate.reportable=true`;
- `report_gate.state` igual a `READY` o `PARTIAL`;
- `canonical_analysis` presente;
- `canonical_fingerprint` procedente de M30.

M31 recalcula el SHA-256 determinista del canonical y lo compara con el fingerprint de M30.

Si no coincide, la ejecución se rechaza. Esto impide que un canonical modificado después del gate llegue al informe.

## 3. Fuente analítica única

El modelo declara:

`canonical_source=canonical_analysis`

y:

`canonical_values_embedded=false`.

Las secciones contienen rutas, no copias de los valores analíticos.

El modelo documental nunca se convierte en una segunda verdad analítica.

## 4. Estados del documento

`report_state` hereda M30:

- `READY`;
- `PARTIAL`.

Si es `PARTIAL`:

- `partial_disclosure_required=true`;
- se conservan exactamente las `degradation_reasons` de M30.

Un modelo parcial no puede ocultar limitaciones para producir una narrativa aparentemente completa.

## 5. Secciones

M31 define exactamente once secciones y un orden fijo:

1. S01_SYNTHESIS — Síntesis ejecutiva.
2. S02_DATA_METHOD — Calidad de datos y método.
3. S03_NUMERIC_ONTOLOGY — Ontología numérica.
4. S04_STRUCTURE — Arquitectura estructural.
5. S05_RELATIONAL — Capas relacionales y cruzadas.
6. S06_DIFFERENTIAL — Diagnóstico diferencial y contraevidencia.
7. S07_TEMPORAL — Activación temporal y eventos.
8. S08_ROBUSTNESS — Robustez y validación.
9. S09_DOCTRINE — Doctrina comparada y corpus.
10. S10_FINAL_SYNTHESIS — Síntesis final.
11. S11_SOURCES_APPENDICES — Fuentes y anexos.

Cada sección declara:

- rutas obligatorias;
- rutas opcionales;
- rutas disponibles;
- rutas obligatorias ausentes;
- rutas opcionales ausentes;
- clases epistemológicas permitidas;
- estado de sección.

## 6. Estados de sección

- `READY` — todas las rutas obligatorias están disponibles;
- `PARTIAL` — sólo parte de las rutas obligatorias está disponible;
- `NOT_AVAILABLE` — ninguna ruta obligatoria está disponible.

La ausencia de una sección no autoriza a inventar su contenido.

## 7. Firewalls

M31 fija:

- `canonical_fingerprint_verified=true`;
- `section_order_fixed=true`;
- `canonical_values_embedded=false`;
- `canonical_values_mutated=false`;
- `prose_generated=false`;
- `render_profile_selected=false`;
- `rendered_document_created=false`;
- `docx_created=false`;
- `pdf_created=false`;
- `pdf_preflight_performed=false`;
- `publication_pipeline_required=true`.

## 8. Separación entre análisis y autoría

M31 no decide:

- extensión del informe;
- estilo narrativo;
- formato A4/B5;
- tipografía;
- portada;
- maquetación;
- DOCX;
- PDF;
- imprenta.

Estas decisiones pertenecen al pipeline de publicación y pueden variar sin modificar el análisis.

## 9. Contrato

Salida canónica:

`schemas/report-document-model.schema.json`

M31 es la última etapa del pipeline analítico M00–M31. La producción material del documento empieza después.
