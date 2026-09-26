# ALMAS 1.15.0 · Specificity Calibration

## Objetivo

ALMAS 1.14.0 corrigió la infradetección de recurrencia semántica de 1.13.0.
La siguiente evolución no debe reducir o aumentar PX mirando un caso concreto.
Primero debe medir **qué tipo de recurrencia está produciendo PX** y cuánto
depende de una familia técnica concreta.

La fase S1 introduce una capa diagnóstica que no cambia ningún score.

## S1 · Recurrence Quality Diagnostics

Política: `ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1`.

Se mantienen separadas:

- identidad geométrica: `root_key`;
- identidad semántica: `motif_id`;
- calidad de recurrencia: diagnóstico descriptivo.

Cada motivo recurrente publica:

- número de familias de dependencia;
- clases técnicas distintas;
- entropía normalizada de fuerza entre familias;
- número efectivo de familias;
- participación de la familia dominante;
- recurrencia después de retirar `NATAL_DRACONIC`;
- supervivencia leave-one-family-out;
- supervivencia leave-one-class-out.

Clases técnicas iniciales:

- SYN → TROPICAL_RELATIONAL;
- DECLINATION/ANTISCIA → SYMMETRY;
- RELCHART → RELATIONSHIP_CHART;
- NATAL_DRACONIC → DRACONIC_CROSS;
- DRACONIC_DD/SECONDARY → SUPPORT_ONLY.

Las familias desconocidas core se conservan como clase propia para no ocultar
nuevas técnicas.

## Invariante central

S1 **no modifica** PX, PS, IEM, IDD, IRC ni la clasificación ontológica.

La observación de que un motivo dependa de dracónica o sobreviva a múltiples
ablaciones se registra, pero todavía no se transforma en peso. Hacerlo antes de
calibración externa produciría una nueva forma de case fitting.

## S2 · Recurrence Null Calibration Battery

S2 queda implementada con la política
`ALMAS_RECURRENCE_NULL_CALIBRATION_V1`.

La primera batería utiliza el universo nulo autocontenido
`ALMAS_NULL_WITHIN_YEAR_V1`. No crea todavía una población externa y no se
usa para weighting.

Para cada motivo recurrente observado se calculan:

- frecuencia de recurrencia del mismo `motif_id` en el null;
- frecuencia de fuerza de motivo >= observada;
- frecuencia de igual o mayor número de clases técnicas;
- recurrencia cross-class;
- recurrencia después de retirar `NATAL_DRACONIC`;
- entropía de fuerza entre familias;
- número efectivo de familias;
- dominancia de la familia principal;
- supervivencia leave-one-family-out;
- supervivencia leave-one-class-out.

Las frecuencias numéricas se publican tanto de forma incondicional sobre todas
las muestras como condicionadas a que el motivo exista en la muestra nula.
Esto evita confundir «el motivo aparece a menudo» con «cuando aparece, alcanza
una fuerza elevada».

Se construye además un catálogo de motivos nulos, incluidos motivos que no
aparecen en el baseline observado, y se recalibran los agregados
`PX_SCORE`, `PS_SCORE` y el número de motivos recurrentes.

Cada frecuencia incorpora intervalo de Wilson. No se calcula un p-value
combinado, no se afirma corrección por comparaciones múltiples y
`metaphysical_probability=false`.

M24 expone el bloque `recurrence_calibration`, pero:

- `used_for_weighting=false`;
- `used_in_px_score=false`;
- `used_in_ps_score=false`;
- `used_in_iem=false`;
- `used_in_idd=false`;
- `used_in_irc=false`;
- `used_in_ontology=false`.

Si una ejecución antigua o un fixture no contiene el grafo semántico y los
diagnósticos S1, S2 falla cerrado como `NOT_EVALUABLE` sin bloquear el
universo nulo Q6.

## S3 · Deterministic Synthetic Recurrence Controls

S3 queda implementada mediante
`ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1`.

La finalidad es responder a una pregunta distinta de S2: cuánto PX/PS puede
emerger por la amplitud del clasificador semántico cuando se rompen
deliberadamente asociaciones internas del caso conservando sus distribuciones
marginales principales.

Se generan dos familias de controles deterministas:

**SEMANTIC_SIGNATURE_ROTATION.** Rota conjuntamente `point_ids` y
`relation_ids` entre raíces core. Conserva el multiconjunto de firmas
semánticas, el número de raíces, sus fuerzas y sus familias técnicas, pero
rompe la asociación firma↔familia/fuerza.

**DECOUPLED_POINT_RELATION_ROTATION.** Rota puntos y relaciones con
desplazamientos diferentes. Conserva por separado los marginales de puntos y
relaciones, pero rompe además su asociación mutua.

No se usa RNG. Para cada familia se generan como máximo 32 desplazamientos
distintos, limitados por el número de raíces core disponibles.

Los controles recalculan exclusivamente el Semantic Motif Graph y los
diagnósticos S1. No recalculan astronomía ni se interpretan como cartas reales.

S3 compara:

- PX y PS observados;
- número de motivos recurrentes;
- presencia de cada motivo;
- fuerza del motivo;
- recurrencia cross-class;
- recurrencia no dracónica.

Las frecuencias publicadas se etiquetan explícitamente como
`FINITE_DETERMINISTIC_CONTROL_FAMILY_FREQUENCY`. No son p-values, no
representan una población y no tienen interpretación probabilística metafísica.

M24 expone `synthetic_recurrence_controls`, siempre con:

- `used_for_weighting=false`;
- `used_in_px_score=false`;
- `used_in_ps_score=false`;
- `used_in_iem=false`;
- `used_in_idd=false`;
- `used_in_irc=false`;
- `used_in_ontology=false`;
- `metaphysical_probability=false`;
- `population_probability_claim=false`;
- `p_value_claim=false`.

## Siguientes fases

S4 preparará la capa de controles externos (`PAIR_SHUFFLE`,
`MATCHED_AGE_CLOCK`) y el protocolo para congelar candidatos PX v3. Ninguna
regla de weighting podrá promocionarse usando los casos que sirvieron para
descubrir el problema de saturación.

S4 podrá modificar PX/PS sólo después de preregistro, controles negativos,
ablación por familia y validación fuera de muestra.

Los casos usados para descubrir estos problemas permanecen DEVELOPMENT_ONLY
para cualquier regla derivada de esta línea metodológica.
