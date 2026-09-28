# Auditoría final de release · ALMAS 1.13.0

**Fecha:** 26 de septiembre de 2026  
**Rama auditada:** `evolution/1.13.0-quantitative-closure`  
**Base:** ALMAS 1.12.0  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** cierre cuantitativo reproducible del modo FULL.

## 1. Problema resuelto

ALMAS 1.12.0 disponía de fórmulas y handlers para IEM, IDD, IRC, sensibilidad,
ablación y modelos nulos, pero varias etapas todavía consumían insumos
precomputados. Eso permitía ejecutar el pipeline, aunque un análisis real podía
quedar en M30=PARTIAL si las fuerzas de raíz, atribuciones, perturbaciones o
resúmenes de robustez no habían sido generados externamente.

1.13.0 cierra esas entradas sin calibrarlas sobre un caso real concreto.

## 2. Q1 · fuerza de raíces

`ALMAS_ROOT_STRENGTH_BASELINE_V1` transforma la exactitud geométrica ya
normalizada en fuerza de raíz mediante la fórmula pública
`S=F×reliability×birth_time_factor×aspect_coefficient`.

La baseline congela coeficientes neutros mientras no exista calibración externa
preregistrada. Las capas support-only conservan fuerza diagnóstica pero no
crean raíz core.

## 3. Q2 · raíz → pilar

`ALMAS_ROOT_PILLAR_ATTRIBUTION_V1` elimina la entrada manual de M18.
Cada raíz core recibe como máximo un pilar semántico primario. PX se trata como
metapilar ortogonal de recurrencia y PU permanece NOT_EVALUABLE sin un
discriminador validado.

La atribución es E_PROJECT_HYPOTHESIS y no doctrina.

## 4. Q3 · atribución por modelo e IDD

`ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V1` deriva la contribución de cada raíz a
AF, KA, AG y LG sobre IEM_pre. Para conjuntos pequeños usa Shapley exacto y
para conjuntos mayores una aproximación determinista con control de
convergencia.

IDD sigue midiendo separación de arquitecturas de evidencia y no funciona como
discriminador ontológico.

## 5. Q4 · sensibilidad horaria

`ALMAS_BIRTH_TIME_PERTURBATION_V1` genera parrillas simétricas según
time_reliability, recalcula la arquitectura estructural y obtiene delta90 y G.

`R_birth_time=exp(-delta90/20)×sqrt(G)`.

La política es experimental del proyecto; no constituye una validación externa
de las categorías A/B/C/D de fiabilidad horaria.

## 6. Q5 · robustez

`ALMAS_ROBUSTNESS_Q5_V1` deriva automáticamente:

- ABLATION;
- PARAMETER_PERTURBATION;
- IDD_STABILITY.

Los componentes automáticos sustituyen al legacy del mismo kind y no se
cuentan dos veces. M24 continúa excluido de IRC.

## 7. Q6 · modelos nulos

`ALMAS_NULL_WITHIN_YEAR_V1` genera un null autocontenido reproducible mediante
32 fechas estratificadas por sujeto dentro de su propio año, manteniendo hora,
zona y localización.

Las estadísticas CORE_ROOT_COUNT, MAX_IEM_PRE y PX_PILLAR_SCORE se reportan
por separado con intervalos de Wilson.

El sistema fija `metaphysical_probability=false`,
`external_population_claim=false` y prohíbe un p-value combinado.
PAIR_SHUFFLE, MATCHED_AGE y MATCHED_AGE_CLOCK continúan requiriendo un pool
externo apropiado.

## 8. Q7 · canonical y M30

`ALMAS_CANONICAL_ASSEMBLY_V1` ensambla `canonical_analysis` desde los
namespaces M01–M29 ya calculados. No recalcula astrología, raíces ni pilares.

ICC se deriva de siete dominios q=0/0.5/1. El IDD global de presentación es el
mínimo de los IDD por pares evaluables, preservando todos los pares en el
canonical.

SUPPORTED sólo puede cerrarse con ICE evaluable y el gate público completo.
Un canonical explícito nunca se sobrescribe.

## 9. Compatibilidad

Se conservan adaptadores legacy para:

- root_strengths/pillars precomputados;
- mapas IDD precomputados;
- time_sensitivity_summary;
- null_model_runs externos;
- robustness_component_summaries;
- canonical_analysis explícito.

Cuando una ruta automática Q1–Q7 es evaluable, tiene prioridad sobre el shim
equivalente para evitar doble contabilización.

## 10. Invariantes preservados

1. Rareza nula no es probabilidad metafísica.
2. Temporalidad no crea raíces ni modifica IEM.
3. PU no se genera automáticamente.
4. IDD no sustituye discriminación ontológica.
5. Un L2 no se autopromociona a L3.
6. No existe actualmente ningún VALIDATED_DISCRIMINATOR real.
7. Ausencia de datos no es contraevidencia.
8. Compuesta y Davison continúan dentro de RELCHART.
9. Support-only no crea categoría ontológica.
10. Los thresholds públicos de SUPPORTED permanecen sin cambios.

## 11. Validación automatizada

La release incorpora una ejecución FULL sintética M00–M31 sin shims
cuantitativos Q1–Q7 y tests unitarios específicos para cada política.

El cierre requiere SUCCESS sobre el mismo HEAD en:

- `Contrato público`;
- `Núcleo Python` Python 3.10;
- `Núcleo Python` Python 3.12.

## 12. Límites que permanecen

El backend astronómico de producción sigue siendo una dependencia inyectable;
la release no selecciona por sí sola una efeméride de producción.

No se ha ejecutado un holdout externo real preregistrado y
`validated_discriminator_ids=[]`.

La reproducibilidad del software no valida científicamente la astrología ni una
ontología metafísica. 1.13.0 elimina entradas cuantitativas ad hoc; no convierte
los índices en probabilidades de alma gemela o llama gemela.

## 13. Decisión de release

ALMAS 1.13.0 es una release minor porque amplía de forma sustancial la
automatización del modo FULL manteniendo contratos, thresholds y firewalls
epistemológicos compatibles. La fusión sólo procede si los workflows finales
del HEAD 1.13.0 concluyen SUCCESS y el contrato público confirma sincronía de
versiones, schemas, policies y manifests.
