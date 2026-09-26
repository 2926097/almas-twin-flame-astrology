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

## S7 · PX v3 Holdout Evaluation Runner

S7 queda implementada mediante
`ALMAS_PX_V3_HOLDOUT_EVALUATION_V1`.

El runner sólo acepta candidatos que ya estén
`FROZEN_FOR_VALIDATION` según S6 y cohortes que superen el firewall S4.

Antes de evaluar comprueba:

- que no exista solapamiento entre `development_case_refs` y holdout;
- que `formula_ref` coincida exactamente con la fórmula congelada;
- que todos los controles externos limpios tengan un valor de candidato;
- que no se incorporen muestras contaminadas, post-hoc o con leakage.

La ejecución produce únicamente una distribución agregada de los valores
holdout:

- N;
- media;
- mediana;
- mínimo;
- máximo;
- P10 nearest-rank;
- P90 nearest-rank.

También genera un fingerprint SHA-256 determinista de la distribución ordenada.
El fingerprint permite congelar el resultado sin publicar los identificadores
ni los valores individuales.

S7 no decide si el candidato «pasa» o «falla». La salida fija:

- `promotion_decision=FORBIDDEN`;
- `candidate_validated=false`;
- `scoring_enabled=false`;
- `weighting_enabled=false`;
- `ontology_enabled=false`;
- `l3_validation=false`;
- `metaphysical_probability=false`.

La finalidad es impedir que el análisis del holdout modifique retrospectivamente
la fórmula o el threshold. S7 registra la distribución; no promueve la regla.

## S8 · PX v3 Promotion Eligibility Gate

S8 queda implementada mediante
`ALMAS_PX_V3_PROMOTION_GATE_V1` y el schema
`px-v3-promotion-evidence.schema.json`.

El gate consume un candidato S6 ya congelado y exige evidencia independiente
de que la regla fue probada sin modificarla retrospectivamente. Como mínimo
requiere:

- al menos una evaluación holdout S7 válida;
- referencias de calibración externa S5;
- al menos una replicación independiente;
- auditoría de leakage;
- criterios preregistrados con resultado explícito;
- cero fallos en controles negativos;
- cero fallos de ablación;
- cero case fitting;
- cero label leakage;
- cero narrative leakage;
- cero cambios de regla después de observar el holdout.

Cada salida S7 debe conservar el mismo `candidate_id` y `formula_ref`,
permanecer `HOLDOUT_EVALUATED_DIAGNOSTIC_ONLY`, incluir fingerprint y no
haber intentado promover el candidato durante la evaluación.

Si se cumplen todos los requisitos, S8 puede devolver:

`PROMOTION_ELIGIBLE`

Este estado **no activa** el candidato. La salida mantiene:

- `automatic_registry_mutation=false`;
- `manual_new_version_required_for_activation=true`;
- `active_in_scoring=false`;
- `scoring_enabled=false`;
- `weighting_enabled=false`;
- `ontology_enabled=false`;
- `l3_validation=false`;
- `metaphysical_probability=false`.

`PROMOTION_ELIGIBLE` significa únicamente que la evidencia metodológica
declarada supera el gate de promoción. No significa ontología demostrada ni
autoriza a alterar el registro canónico dentro de la misma ejecución.

El registro canónico PX v3 continúa vacío en 1.15:

`records=[]`

`validated_candidate_ids=[]`

## S9 · PX v3 Versioned Activation Firewall

S9 queda implementada mediante
`ALMAS_PX_V3_ACTIVATION_FIREWALL_V1`.

El firewall se vincula explícitamente a la línea `1.15.x` y declara como motor
PX operativo:

`ALMAS_SEMANTIC_MOTIF_V2`

Es decir, **PX v2 continúa siendo el único score operativo en ALMAS 1.15**.

Incluso si una ejecución externa suministrara un resultado S8
`PROMOTION_ELIGIBLE`, S9 fija:

- `promotion_eligible_causes_activation=false`;
- `px_v3_active=false`;
- `activation_permitted=false`;
- `runtime_activation=false`;
- `automatic_registry_mutation=false`.

Cualquier intento de introducir dentro de 1.15:

- registros PX v3 activos;
- `validated_candidate_ids`;
- `scoring_enabled=true`;
- `weighting_enabled=true`;
- `ontology_enabled=true`;

produce `BLOCKED_RELEASE_FIREWALL`.

La activación futura exige simultáneamente:

1. nueva versión SemVer fuera de la línea 1.15;
2. cambio manual del registro canónico;
3. auditoría de release nueva;
4. nueva validación del contrato público;
5. trazabilidad a un candidato S8 elegible.

Con el registro canónico actual vacío, la salida normativa es:

`NO_ACTIVE_PX_V3_CANDIDATE`.

## Cierre metodológico de 1.15

S1–S9 completan la infraestructura de calibración de especificidad sin alterar
los scores de producción de 1.14.

La release 1.15 puede publicar:

- diagnósticos de calidad de recurrencia;
- calibración WITHIN_YEAR;
- controles sintéticos;
- firewall de cohortes externas;
- calibración externa;
- registro/gate de candidatos;
- runner holdout;
- gate de promoción;
- firewall de activación.

Pero no publica una fórmula PX v3 real, no modifica PX/PS, no incorpora
candidatos validados y no eleva ninguna ontología.

El siguiente trabajo ya pertenece a una futura versión: poblar cohortes externas
preregistradas y probar reglas previamente congeladas. No debe prolongarse
1.15 inventando un candidato sólo para completar el ciclo.
