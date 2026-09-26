# Pipeline de informes y PDF

El objeto `canonical_analysis.json` es la única verdad analítica del informe.

Pipeline recomendado:

`canonical_analysis.json → M30 report_gate → M31 report_document_model.json → documento estructurado → PDF → preflight → renderizado de todas las páginas → inspección → corrección → re-render/verificación`

Para informes largos se prefiere una fase de autoría DOCX antes de la conversión a PDF.

## Gate M30

No se redacta un informe analítico sin pasar por M30.

Estados:

- **READY** — análisis FULL íntegro y sin degradaciones detectadas;
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

Un estado PARTIAL debe reflejar sus `degradation_reasons` en el documento. No se ocultan módulos no evaluables, datos ausentes ni limitaciones del análisis.

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
4. Arquitectura estructural.
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

## Publicación

M31 cierra el pipeline analítico M00–M31. La autoría narrativa, selección de formato, maquetación, DOCX, PDF y preflight comienzan únicamente después de M31.

La secuencia de publicación debe respetar:

`canonical_analysis → report_document_model → documento → PDF → preflight → render completo → inspección → corrección → verificación final`.
