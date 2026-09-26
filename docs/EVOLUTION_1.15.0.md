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

## S4 · External Recurrence Cohort Firewall

S4 queda implementada mediante
`ALMAS_EXTERNAL_RECURRENCE_COHORT_V1` y el schema
`external-recurrence-control-cohort.schema.json`.

La finalidad no es todavía recalibrar PX, sino permitir que ALMAS reciba en
runtime cohortes externas `PAIR_SHUFFLE`, `MATCHED_AGE` o
`MATCHED_AGE_CLOCK` sin contaminar el repositorio ni convertir una cohorte
mal seleccionada en evidencia de validación.

Cada cohorte debe congelar antes de la ejecución:

- `preregistration_ref`;
- versión ALMAS y commit SHA;
- `feature_set_ref`;
- `orb_policy_ref`;
- regla de emparejamiento;
- regla de inclusión;
- muestras y estado de validación.

Cada muestra declara además:

- `validation_status`;
- `selection_status`;
- nivel de cegamiento;
- contaminación;
- forbidden-field hits;
- label leakage;
- narrative leakage;
- case fitting;
- snapshot estructural de recurrencia.

Los estados externos sólo se consideran candidatos limpios cuando son
`EXTERNAL_HOLDOUT` o `FROZEN_CONFIRMATORY`, fueron seleccionados mediante
`PREREGISTERED`, no presentan contaminación/leakage y contienen el snapshot
estructural requerido.

Una muestra `DEVELOPMENT_ONLY` puede mantenerse como material de desarrollo,
pero nunca se convierte en validación externa de la regla que ayudó a crear.

La salida pública de S4 es deliberadamente agregada. No publica:

- `sample_ref`;
- snapshots individuales;
- datos natales;
- identidades privadas.

El acceso a snapshots sólo existe en memoria mediante una función runtime
separada después de superar el firewall.

S4 fija expresamente:

- `candidate_weighting_enabled=false`;
- `l3_validation=false`;
- `metaphysical_probability=false`.

Por tanto, disponer de una cohorte externa limpia no modifica todavía PX/PS ni
promociona ningún discriminador.

## S5 · External Recurrence Calibration

S5 queda implementada mediante
`ALMAS_EXTERNAL_RECURRENCE_CALIBRATION_V1`.

La capa toma una cohorte que ya ha superado S4 y extrae únicamente muestras que
cumplen simultáneamente:

- `EXTERNAL_HOLDOUT` o `FROZEN_CONFIRMATORY`;
- selección `PREREGISTERED`;
- `contamination=false`;
- cero forbidden-field hits;
- cero label leakage;
- cero narrative leakage;
- cero case fitting;
- snapshot estructural de recurrencia evaluable.

Las muestras `DEVELOPMENT_ONLY`, post-hoc, contaminadas o con leakage quedan
fuera de la calibración externa aunque permanezcan documentadas en el resumen
de cohorte.

S5 reutiliza el mismo núcleo matemático de S2 para evitar dos definiciones de
calibración. Compara, sobre los controles externos limpios:

- presencia de motivo;
- fuerza del motivo;
- diversidad de clases;
- recurrencia cross-class;
- recurrencia no dracónica;
- entropía;
- número efectivo de familias;
- dominancia;
- supervivencia leave-one-family-out;
- supervivencia leave-one-class-out;
- PX/PS agregados y número de motivos recurrentes.

La salida pública sólo conserva agregados y metadatos de procedencia. No
serializa `sample_ref` ni snapshots individuales.

S5 continúa siendo `DIAGNOSTIC_ONLY`:

- `used_for_weighting=false`;
- `candidate_freeze_enabled=false`;
- `l3_validation=false`;
- `metaphysical_probability=false`;
- `population_probability_claim=false`.

Por tanto, una señal que sea rara en S5 todavía no modifica PX v2. S5 aporta
evidencia externa de especificidad metodológica, no una probabilidad de
ontología.

## S6 · PX v3 Candidate Freeze Gate

S6 queda implementada mediante
`ALMAS_PX_V3_CANDIDATE_FREEZE_V1`, el registro canónico
`ALMAS_PX_V3_CANDIDATES` y el schema
`px-v3-candidate-registry.schema.json`.

S6 no introduce todavía ninguna fórmula PX v3 real. El registro canónico nace
vacío y bloquea por contrato:

- `scoring_enabled=true`;
- `weighting_enabled=true`;
- `ontology_enabled=true`;
- cualquier `validated_candidate_ids`.

Un candidato hipotético sólo puede alcanzar
`FROZEN_FOR_VALIDATION` antes del holdout si declara:

- descriptores S1 permitidos;
- `formula_ref` congelada;
- dirección esperada;
- referencias de casos de desarrollo;
- referencias S2 y S3;
- ablaciones requeridas;
- controles negativos;
- criterios explícitos de falsación;
- `holdout_refs=[]`;
- `formula_frozen_before_holdout=true`;
- `holdout_fitted_thresholds=false`.

Si el holdout ya fue observado, si la fórmula se ajustó después del holdout o
si se intenta habilitar scoring/ontología, el gate rechaza la congelación.

La congelación sólo significa que la regla está suficientemente especificada
para ser **probada**. No significa que sea correcta, útil, validada o que pueda
entrar en PX.

El registro público permanece actualmente:

`records=[]`

`validated_candidate_ids=[]`

Por tanto ALMAS 1.15 no incorpora aún ningún candidato PX v3 real y PX v2 sigue
siendo el único score operativo.

## Siguientes fases

S7 definirá el runner de evaluación holdout para candidatos congelados. El
runner deberá consumir una cohorte S4/S5 distinta de los casos de desarrollo y
producir únicamente métricas de validación, sin modificar el registro ni el
scoring.

S8 podrá promover un candidato sólo después de preregistro, evaluación
holdout, replicación independiente, controles negativos, ablación por familia
y auditoría de leakage. Una promoción de PX v3 seguirá siendo una decisión
metodológica del proyecto, no una validación de ontología metafísica.
