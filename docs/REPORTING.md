# Pipeline de informes y PDF

El objeto `canonical_analysis.json` es la única verdad analítica del informe.

Pipeline recomendado:

`canonical_analysis.json → M30 report_gate → M31 report_document_model.json → authored_report → DOCX → PDF/preflight → renderizado de todas las páginas → inspección → corrección → re-render/verificación`

Para informes largos se prefiere una fase de autoría DOCX antes de la conversión a PDF.

## Gate M30

No se redacta un informe analítico sin pasar por M30. En una ejecución configurada, si `canonical_analysis` no fue suministrado, el ensamblador canónico puede construirlo desde los namespaces M01–M29 antes de aplicar el gate. Desde 1.14.0, M30 resuelve además `analysis_profile`. Un canonical explícito nunca se sobrescribe.

Estados:

- **READY** — análisis íntegro para el `analysis_profile` seleccionado y sin degradaciones requeridas;
- **PARTIAL** — reportable con limitaciones explícitas;
- **BLOCKED** — no debe producirse informe analítico.

El informe debe conservar el `canonical_fingerprint` generado por M30 para identificar el objeto analítico exacto del que deriva.

M30 no puede modificar el canonical.

## Principio de narración

El informe no debe ser una tabla extensa de aspectos. Convierte los hallazgos técnicos en una explicación coherente de la arquitectura relacional manteniendo trazabilidad a la evidencia canónica.

Toda conclusión material debe indicar, cuando proceda:

- clase epistemológica A–E;
- fuente o técnica;
- estado `SUPPORTED / COMPATIBLE / INSUFFICIENT / CONTRADICTED / NOT_EVALUABLE`;
- modelos competidores;
- contraevidencia;
- incertidumbre;
- dependencia entre técnicas;
- carácter estructural, temporal o factual;
- límites inferenciales.

Un estado PARTIAL debe reflejar sus `degradation_reasons` en el documento. No se ocultan módulos requeridos no evaluables, datos ausentes ni limitaciones del análisis. Los módulos opcionales o excluidos por el perfil no degradan por sí mismos. El informe debe declarar el perfil usado y recordar que `READY` expresa completitud técnica del alcance, no validación metafísica. El ensamblador deriva ICC mediante siete dominios q=0/0.5/1 y conserva el IDD global como el mínimo de los IDD por pares evaluables.


## Recurrencia semántica en el informe

Cuando `canonical_analysis.semantic_motifs` existe, el informe debe distinguir explícitamente entre raíz geométrica y motivo semántico. `root_key` conserva identidad técnica; `motif_id` expresa una hipótesis operativa de recurrencia entre familias. PX/PS derivados de motivos no deben narrarse como nuevas raíces independientes ni como prueba de origen compartido.

Cuando M23 publica `time_sensitivity.diagnostic_curve`, deben mostrarse R5/R15/R30/R60/R120 aunque no exista un componente `BIRTH_TIME`. Si la fiabilidad horaria no está documentada, el informe debe indicar que la curva es diagnóstica y que no se agregó una robustez horaria única a IRC.

## Modelo documental M31

M31 no redacta el informe. Produce un modelo documental trazable que conserva el `canonical_fingerprint` aprobado por M30 y vuelve a verificarlo antes de construir la estructura.

Si el fingerprint ya no coincide, M31 rechaza la ejecución.

El modelo contiene exactamente once secciones. Cada una declara rutas obligatorias/opcionales, disponibilidad y clases epistemológicas permitidas. Sus estados posibles son `READY`, `PARTIAL` y `NOT_AVAILABLE`.

M31 fija `canonical_values_embedded=false`, `prose_generated=false`, `rendered_document_created=false`, `docx_created=false`, `pdf_created=false` y `publication_pipeline_required=true`.

Cuando `canonical_analysis.ontological_discrimination` existe, M31 conserva rutas hacia el diagnóstico ontológico en S01, S03, S06 y S10, y hacia `promotion_trace` en S08 y S11. No copia ni reinterpreta esos valores.

## Orden canónico

1. Síntesis ejecutiva.
2. Calidad de datos y método.
3. Ontología numérica.
4. Arquitectura estructural, raíces y motivos semánticos recurrentes.
5. Capas relacionales y cruzadas.
6. Diagnóstico diferencial y contraevidencia.
7. Activación temporal y eventos.
8. Robustez y validación.
9. Doctrina comparada y corpus.
10. Síntesis final.
11. Fuentes y anexos.

## Separaciones obligatorias

El informe debe mantener diferenciados:

- datos calculados/documentales;
- técnica;
- doctrina explícita;
- uso contemporáneo;
- hipótesis del proyecto;
- hechos reales de viabilidad/reciprocidad;
- interpretación temporal.

No se convierten rareza estadística, intensidad, sincronicidad, doctrina o activación temporal en probabilidad metafísica o predicción de hechos reales.

## Autoría interpretativa

Después de M31, `authored_report` convierte las rutas disponibles en prosa sin modificar el análisis. El centro del documento es la lectura astrológica y la hermenéutica/metafísica basada en fuentes; la capa técnica conserva la función de cálculo, trazabilidad y control de calidad.

La trazabilidad se exige por sección, no por frase. Cada sección registra rutas canónicas utilizadas, clases epistemológicas, claims doctrinales, evidencia estructural, fuentes y limitaciones. Esto permite una narrativa desarrollada sin reducirla a un formulario de auditoría.

`authored_report.bibliography` es editorial: permite construir citas, notas y anexos, pero no añade peso a modelos ni scores.

Contrato:

`schemas/authored-report.schema.json`

Validador semántico:

`src/almas_tfa/authored_report.py`

## Publicación DOCX

La primera materialización es `ALMAS_B5_BOOK_V1`: ISO B5 vertical (176 × 250 mm). El generador copia literalmente las narrativas de `authored_report`, conserva límites y bibliografía y relega evidencias/claims/fuentes a notas de trazabilidad secundarias.

Implementación:

`src/almas_tfa/docx_publication.py`

CLI:

`scripts/render_authored_report_docx.py`

Dependencia opcional:

`publication-docx = ["python-docx==1.2.0"]`

La publicación DOCX no recalcula astrología, no modifica el canonical, no crea scores y no reescribe la interpretación.

## Publicación PDF y preflight

El perfil `ALMAS_B5_PDF_V1` convierte el DOCX aprobado mediante LibreOffice y aplica un preflight fail-closed.

Comprueba todas las páginas B5, CropBox B5, ausencia de cifrado, fuentes embebidas, texto extraíble, ausencia de páginas vacías, fingerprint y once títulos de sección.

Implementación:

`src/almas_tfa/pdf_publication.py`

CLI:

`scripts/publish_authored_report_pdf.py`

Dependencia Python opcional:

`publication-pdf = ["pypdf==6.19.0"]`

LibreOffice sigue siendo una dependencia externa de materialización. Este perfil no declara todavía PDF/X ni certificación específica de imprenta.

## Publicación

M31 cierra el pipeline analítico M00–M31. La autoría narrativa, selección de formato, maquetación, DOCX, PDF y preflight comienzan únicamente después de M31.

La secuencia de publicación debe respetar:

`canonical_analysis → report_document_model → authored_report → DOCX → PDF/preflight → render completo → inspección → corrección → verificación final`.
