# Contrato de autoría interpretativa · ALMAS 1.19

## Finalidad

La autoría comienza después de M31. Su función es convertir un análisis ya cerrado en una lectura extensa, comprensible y argumentada.

Cadena:

`canonical_analysis → M30 → M31 report_document_model → authored_report → DOCX/PDF`

El `authored_report` no es una nueva capa analítica. No recalcula cartas, no modifica índices y no crea scores.

## Centro interpretativo

El contrato fija:

`interpretive_center=ASTROLOGY_AND_SOURCE_BASED_METAPHYSICAL_HERMENEUTICS`

y:

`technical_role=CALCULATION_TRACEABILITY_AND_QUALITY_CONTROL`.

Esto expresa la jerarquía metodológica de ALMAS: la astronomía reproducible y los controles cuantitativos sirven para estabilizar el dato; la lectura astrológica y la interpretación metafísica basada en fuentes constituyen el contenido sustantivo del informe.

No se afirma validación científica de los significados metafísicos. Se exige, en cambio, que el cálculo del que parte la lectura sea reproducible y que la procedencia de las afirmaciones sea visible.

## Trazabilidad sin convertir el informe en una auditoría

La trazabilidad se registra por sección, no frase por frase.

Cada una de las once secciones conserva:

- narrativa redactada;
- rutas canónicas utilizadas;
- clases epistemológicas utilizadas;
- referencias a claims doctrinales;
- referencias a evidencias estructurales;
- referencias bibliográficas;
- limitaciones relevantes.

Esto permite una prosa literaria, evolutiva y esotérica sin perder el vínculo con el análisis.

## Síntesis vertical por motivo

La profundidad del informe no procede de dedicar un apartado aislado a cada técnica. Cuando varias rutas están disponibles, la unidad narrativa preferente es el **motivo** o problema interpretativo.

Secuencia recomendada:

`sustrato individual → activación/interacción → campo relacional → reencuadre dracónico → contexto histórico auxiliar → raíz/motivo → comparandum metafísico → límite inferencial`.

Por tanto:

- `natal_context` explica qué existe antes del vínculo;
- `evidence` identifica las raíces estructurales que realmente sostienen el análisis;
- `relationship_field` muestra cómo esas funciones se organizan como campo compuesto/Davison;
- `draconic_context` puede reencuadrar o corroborar el mismo tema desde el eje nodal;
- `lots_context` sólo añade contexto histórico selectivo y nunca desplaza la arquitectura principal;
- `semantic_motifs` organiza la síntesis entre capas;
- `doctrine` entra después como comparandum documentado, no como sustituto de la explicación astrológica.

El fixture `examples/authored-report.synthetic.json` demuestra esta secuencia. Es una regresión editorial de integración, no una plantilla textual obligatoria ni un evaluador automático de calidad.

## Fuentes

`bibliography[]` es una superficie editorial. No añade peso analítico.

Cada fuente utilizada en `source_refs` debe tener una entrada bibliográfica con un `citation_label` reutilizable por DOCX/PDF. Puede contener autor, obra, tradición, localizador, URL y ancla de verificación.

Los `doctrinal_claim_refs` deben resolver contra `canonical_analysis.doctrine`. Los `evidence_refs` deben resolver contra `canonical_analysis.evidence`.

## Relación con M31

La autoría debe conservar:

- el mismo `canonical_fingerprint`;
- el mismo `report_state`;
- el orden exacto de las once secciones;
- sólo rutas que M31 haya declarado disponibles;
- sólo clases epistemológicas permitidas por cada sección.

Una sección `NOT_AVAILABLE` en M31 debe quedar `OMITTED_NOT_AVAILABLE`; no puede rellenarse imaginativamente.

## Alcance del paso

Este contrato no decide todavía tipografía, B5/A4, portada, DOCX, PDF o preflight. Esos aspectos pertenecen a la capa material posterior.

El objetivo de este paso es que ALMAS pueda redactar una interpretación rica y basada en fuentes antes de entrar en maquetación.
