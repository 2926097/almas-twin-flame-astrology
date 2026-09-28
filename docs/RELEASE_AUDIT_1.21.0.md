# Auditoría de release · ALMAS 1.21.0

**Fecha:** 28 de septiembre de 2026  
**Rama de cierre:** `release/1.21.0-personal-reporting`  
**Base consolidada:** `0c8af741dfa08e20d25a08d5cedfbf8f6fba9eaf`  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** portar informes astrológicos personales a la arquitectura pública 1.20 y cerrar SemVer 1.21.0.

## Procedencia del cambio

La implementación se separó deliberadamente en bloques:

- PR #62: canonical personal, cinco perfiles y modelo documental;
- PR #63: autoría personal trazable;
- PR #64: publicación B5 DOCX/PDF compartida;
- PR #65: solicitud natal → backend → canonical personal;
- PR #66: router de fuentes personales contra el corpus canónico.

La antigua PR #6 se conserva únicamente como antecedente histórico de diseño y no se fusiona sobre la arquitectura vigente.

## Contratos incorporados

La release añade, entre otras superficies:

- `personal-report-request.schema.json`;
- `personal-canonical-analysis.schema.json`;
- `personal-report-document-model.schema.json`;
- `personal-authored-report.schema.json`;
- `personal-report-reference-router.schema.json`;
- `ALMAS_PERSONAL_REFERENCE_ROUTER_V1`;
- adaptadores B5 personales sobre el renderer/preflight compartido.

## Backend y minimización

La carta individual utiliza el backend astronómico de producción vigente. La solicitud no selecciona provider, kernel ni política astronómica.

El canonical personal aplica una lista blanca y no conserva metadata reconstruible innecesaria. La calidad de hora natal no se inventa y puede producir estados parciales.

## Fuentes

El router personal consume `reference/source-registry.json`, actualmente con 76 entradas, sin duplicarlo.

Las carencias se expresan mediante `PARTIAL` o `SOURCE_GAP`; no se fabrican referencias para obtener cobertura aparente.

## Publicación

DOCX y PDF personales reutilizan la infraestructura B5 existente. Los workflows de publicación continúan siendo independientes y se activan por paths relevantes.

## No regresión metodológica

1. No cambia scoring relacional.
2. No cambian pesos ni thresholds.
3. No se activa ningún discriminador nuevo.
4. No cambia la ontología.
5. No cambia `engine_revision=1.9.0` del módulo contractual.
6. No se incorporan datos personales reales al repositorio público.

## Evidencia previa al cierre

Sobre el último bloque funcional antes de esta rama:

- Núcleo Python 3.12: 574 tests, PASS, 10 skipped;
- Contrato público: PASS;
- Backend astronómico: PASS;
- últimos runs aplicables de Publicación DOCX: PASS;
- últimos runs aplicables de Publicación PDF: PASS.

## Gate de release

Este documento nace como auditoría de candidato. La release 1.21.0 sólo queda lista para fusión cuando el HEAD de esta rama cumpla:

- sincronía completa de `VERSION`, package, skill, manifests, schemas y fixtures versionados;
- Contrato público: PASS;
- Núcleo Python 3.10: PASS;
- Núcleo Python 3.12: PASS;
- Backend astronómico 3.10/3.12 y gates dorados: PASS;
- workflows DOCX/PDF: PASS cuando sean aplicables a las rutas modificadas;
- PR fusionable sin conflictos.

El cumplimiento del gate debe registrarse después de los checks del HEAD final, no anticiparse en este documento.
