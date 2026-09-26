# ALMAS 1.14.0 · Semantic Recurrence & Analysis Profiles

## Estado inicial verificado

Base auditada: ALMAS 1.13.0, commit `6256ecc1915102eb306b31404d6fc652a719b100`.

La release 1.13.0 tiene Q1–Q7 integrados, 317 tests deterministas y el
pipeline FULL M00–M31 ejecutable. La auditoría de 1.14 parte de dos limitaciones
de diseño generales, no de un caso privado:

1. `PX` depende en 1.13 de que una misma `root_key` acumule al menos dos
   familias independientes. Técnicas diferentes pueden describir el mismo
   motivo semántico sin compartir una root_key literal, por lo que la
   recurrencia semántica puede quedar infradetectada.
2. M30 degrada por cualquier módulo previo `NOT_EVALUABLE`/`SKIPPED`, aunque
   el análisis solicitado sea deliberadamente sólo astrológico y algunos
   módulos doctrinales, temporales o de realidad no pertenezcan a su alcance.

No se usan casos privados como fixtures, fuentes de pesos ni criterios de
promoción. Toda regla nueva debe probarse con fixtures sintéticos.

## Paso 1 · Auditoría y congelación del problema

Completado en esta rama.

Se preservan:

- fuerza de raíces Q1;
- deduplicación por dependencia;
- un único pilar semántico primario por raíz;
- `PU=NOT_EVALUABLE` sin discriminador validado;
- IDD separado de ontología;
- rareza nula fuera de IRC;
- temporalidad fuera de la creación de raíces;
- thresholds públicos de `SUPPORTED`.

## Paso 2 · Semantic Motif Graph + perfiles

**Completado en la rama de evolución.**

Implementación:

`evidencia → root_key → raíz independiente → semantic_motif → recurrencia`.

La recurrencia V2 se evalúa entre raíces distintas que comparten un motivo y
proceden de familias de dependencia independientes. La fuerza conservadora de
un motivo recurrente será la segunda mayor fuerza familiar: una sola familia no
puede crear PX y una tercera familia no duplica automáticamente la evidencia.

`PS` se derivará también a nivel de motivo recurrente de misión/servicio,
evitando exigir que una misma root_key contenga toda la recurrencia.

Se introduce `analysis_profile` como dimensión ortogonal a
`analysis_mode`. Como mínimo:

- `FULL_MULTIDISCIPLINARY`: comportamiento exhaustivo;
- `FULL_ASTROLOGY`: exige el núcleo astrológico/estructural y permite que
  módulos doctrinales, temporales o de realidad queden fuera del alcance sin
  degradar M30 por ese motivo.

## Paso 3 · Validación y release

**En ejecución.**

Antes de fusionar 1.14.0:

- tests sintéticos de recurrencia inter-familias;
- test que impida que compuesta+Davison se dupliquen como familias
  independientes cuando ambas pertenecen a `RELCHART`;
- test que impida a support-only crear PX;
- tests de perfiles M30;
- prueba FULL sintética;
- sincronización SemVer, manifests, schemas y documentación;
- SUCCESS de `Contrato público` y `Núcleo Python` 3.10/3.12 sobre el mismo
  HEAD.

La release no declarará validación empírica externa ni promoverá
discriminadores L3.
