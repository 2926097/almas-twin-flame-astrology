# ALMAS 1.21.0 · Informes astrológicos personales

## Objetivo

ALMAS 1.21 incorpora la capacidad de producir informes astrológicos personales sobre la arquitectura pública vigente, sin recuperar el diseño histórico acoplado de la antigua PR #6 y sin crear una segunda skill.

El trabajo se ejecutó en cinco bloques funcionales independientes (#62–#66) y un bloque de cierre SemVer separado.

## P1 · Canonical personal y perfiles

Se añade `personal_canonical_analysis` como superficie individual, minimizada y fingerprintable. No reutiliza el canonical relacional como contenedor genérico ni conserva datos natales brutos cuando no son necesarios.

Los perfiles publicados son:

- `EXECUTIVE_PERSONAL_REPORT`;
- `STANDARD_PERSONAL_REPORT`;
- `FULL_CRITICAL_REPORT`;
- `TECHNICAL_ATLAS`;
- `ESOTERIC_KABBALISTIC_REPORT`.

La calidad de hora natal degrada explícitamente la disponibilidad de capas sin inventar precisión.

## P2 · Autoría trazable

`ALMAS_PERSONAL_AUTHORED_REPORT` conserva fingerprint, perfil, estado y orden del modelo documental.

La autoría sólo puede utilizar rutas y clases epistemológicas autorizadas y no puede introducir bibliografía ausente del canonical o del router de fuentes.

## P3 · Publicación B5 compartida

Los informes personales reutilizan el renderer y preflight ya publicados:

- `ALMAS_B5_PERSONAL_BOOK_V1`;
- `ALMAS_B5_PERSONAL_PDF_V1`.

El dispatch se realiza por `document_kind`; no existe un segundo stack de publicación.

## P4 · Solicitud natal → canonical personal

La cadena autónoma es:

`personal_report_request → backend astronómico de producción → personal_canonical_analysis → personal_report_document_model`.

El backend se inyecta y conserva la procedencia `ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1 / ALMAS_MOIRA_JPL_SPK_V1`.

La minimización elimina metadata reconstruible como UTC/JD/coordenadas del canonical personal final.

## P5 · Router de fuentes

`ALMAS_PERSONAL_REFERENCE_ROUTER_V1` resuelve `reference_domains` contra las 76 fuentes del registro canónico.

Estados:

- `SUPPORTED`;
- `PARTIAL`;
- `SOURCE_GAP`.

`evolutionary` y `kabbalah` permanecen `PARTIAL` cuando faltan anclajes metodológicos suficientes. `fixed_stars` permanece `SOURCE_GAP` mientras no exista una fuente metodológica preregistrada. El sistema no inventa bibliografía para cerrar gaps.

## Invariantes

1. Una única skill ALMAS.
2. Un único backend astronómico de producción.
3. El reporting personal no modifica M00–M31.
4. No modifica scoring relacional, pesos, thresholds, discriminadores ni ontología.
5. Los datos privados no se incorporan como fixtures públicos.
6. DOCX/PDF personal reutiliza la infraestructura B5 existente.
7. Fuentes y doctrina permanecen separadas de técnica y cálculo.
8. `engine_revision` contractual permanece 1.9.0.

## Estado de validación previo al cierre

El último bloque funcional (#66) obtuvo:

- Núcleo Python: 574 tests en Python 3.12, PASS, 10 skipped por extras opcionales;
- Contrato público: PASS;
- Backend astronómico: PASS.

Los últimos runs aplicables de Publicación DOCX y Publicación PDF en `main` están en PASS. #66 no tocó rutas de publicación y, por los filtros de paths de los workflows, no generó nuevas ejecuciones DOCX/PDF.

El bloque de cierre SemVer debe ejecutar CI de nuevo sobre un único HEAD antes de fusionarse.
