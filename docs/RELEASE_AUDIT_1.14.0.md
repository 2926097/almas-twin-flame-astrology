# Auditoría final de release · ALMAS 1.14.0

**Fecha:** 26 de septiembre de 2026  
**Rama auditada:** `evolution/1.14.0-semantic-recurrence-profiles`  
**Base:** ALMAS 1.13.0 · `6256ecc1915102eb306b31404d6fc652a719b100`  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** recurrencia semántica multitécnica, perfiles de análisis, sensibilidad horaria v2 y lotes históricos mínimos.

## 1. Problema de diseño corregido

ALMAS 1.13.0 conservaba correctamente la independencia geométrica de las raíces,
pero PX dependía demasiado de la identidad literal de `root_key`. Dos técnicas
podían expresar el mismo tema relacional sin producir una raíz multifamilia y,
por tanto, sin generar recurrencia formal.

1.14.0 separa dos identidades:

- `root_key`: identidad geométrica y unidad de deduplicación;
- `motif_id`: identidad semántica derivada para estudiar recurrencia.

La nueva capa no fusiona raíces ni altera M16/M17.

## 2. Semantic Motif Graph

`ALMAS_SEMANTIC_MOTIF_V2` crea motivos semánticos primarios sobre raíces core.

Motivos vigentes:

- KARMIC_CONTINUITY;
- WOUND_REPAIR;
- IDENTITY_TRANSFORMATION;
- TRANSFORMATION_POWER;
- TRANSPERSONAL_FIELD;
- EROTIC_POLARITY;
- MIRROR_COMPLEMENTARITY;
- RELATIONAL_COHERENCE;
- STRUCTURAL_AFFINITY.

Cada raíz recibe como máximo un motivo primario. La recurrencia exige al menos
dos familias de dependencia independientes y, normalmente, dos raíces
distintas. Una sola raíz puede bastar únicamente cuando M16/M17 ya demuestran
que esa raíz contiene varias familias independientes.

Dentro de un motivo, cada familia cuenta una sola vez y conserva su máxima
fuerza core. Las capas support-only no pueden crear recurrencia core.

## 3. PX v2

PX ya no depende de identidad literal de root_key.

El cálculo sigue esta secuencia:

`raíces core → motivo semántico → máximo por familia → fuerza de motivo → PX`.

La fuerza del motivo se obtiene mediante `pillar_score` sobre los máximos por
familia. PX agrega posteriormente los motivos primarios recurrentes.

Se publican componentes diagnósticos:

- PX_G_EXACT_ROOT_RECURRENCE;
- PX_S_SEMANTIC_RECURRENCE;
- PX_R_RELCHART_CROSS_FAMILY;
- PX_D_NATAL_DRACONIC_CROSS_FAMILY.

Ninguno es probabilidad ontológica.

## 4. PS v2

PS se deriva mediante motivos de misión:

- MISSION_SOLAR;
- MISSION_JOVIAN;
- MISSION_SATURNIAN;
- MISSION_NODAL.

La firma exige eje meridiano y el ancla correspondiente y sólo entra en PS si
se vuelve recurrente entre familias independientes.

PS describe recurrencia estructural de un motivo de misión; no demuestra una
misión compartida factual ni un acuerdo preencarnatorio literal.

## 5. M18 y M21

M18 utiliza `ALMAS_ROOT_PILLAR_ATTRIBUTION_V2`. PA, PK, PE, PR y PT siguen
procediendo de raíces canónicas. PX y PS proceden del grafo semántico.

M21 utiliza `ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V2` y trabaja sobre
`CANONICAL_EVIDENCE_UNIT`. Una unidad puede ser raíz o feature derivada de
motivo para PX/PS. Las features derivadas no se declaran raíces independientes
ni aumentan el conteo estructural M17.

IDD continúa midiendo separación entre arquitecturas de evidencia y no actúa
como discriminador ontológico.

## 6. Perfiles de análisis

`ALMAS_ANALYSIS_PROFILES_V1` separa completitud del alcance solicitado.

Perfiles públicos:

- FULL_MULTIDISCIPLINARY;
- FULL_ASTROLOGY;
- TEMPORAL;
- SOUL_CONTRACT.

M30 sólo degrada por módulos requeridos por el perfil. Los módulos opcionales o
excluidos pueden permanecer NOT_EVALUABLE/SKIPPED sin convertir automáticamente
el informe en PARTIAL.

`READY` significa completitud técnica del perfil, no verdad metafísica.

## 7. Sensibilidad horaria v2

`ALMAS_BIRTH_TIME_SENSITIVITY_V2` separa:

1. curva diagnóstica R5/R15/R30/R60/R120;
2. componente agregado BIRTH_TIME.

La curva puede calcularse cuando existen hora, zona y localización aunque no
exista una categoría documental A/B/C/D.

El componente BIRTH_TIME sólo entra en IRC cuando la fiabilidad horaria exigida
está documentada. La mera impresión de una hora en una carta no se transforma
en Rodden Rating.

Cuando la arquitectura utiliza puntos dependientes de hora y BIRTH_TIME no es
evaluable, el ensamblaje canónico impide elevar un modelo a SUPPORTED.

## 8. M13 · lotes históricos mínimos

`ALMAS_HELLENISTIC_LOTS_V1` proporciona una baseline histórica para:

- Fortuna;
- Espíritu.

La política registra inversión diurna/nocturna y fuentes. La secta explícita
tiene prioridad; el fallback por posición del Sol respecto del horizonte se
declara como regla operacional.

No se añaden Eros, Necesidad u otros lotes por defecto porque existen variantes
históricas que exigirían decisiones adicionales.

Los lotes no funcionan como discriminadores ontológicos.

## 9. Robustez y ablación

Q5 conserva sus fórmulas públicas, pero las ablaciones de 1.14.0 vuelven a
derivar los pilares desde las raíces supervivientes. Por tanto PX y PS se
recalculan después de retirar familias, en vez de reutilizar la recurrencia del
baseline.

Esto permite que una ablación destruya correctamente un motivo recurrente si
desaparece una de sus familias independientes.

## 10. Invariantes preservados

1. root_key no se modifica para fabricar recurrencia.
2. Compuesta y Davison continúan en una única familia RELCHART.
3. Dracónica↔dracónica continúa support-only.
4. Asteroides secundarios continúan support-only.
5. support-only no crea PX ni PS core.
6. PX y PS no crean PU.
7. PU permanece NOT_EVALUABLE sin discriminador L3 validado.
8. IDD no equivale a ontología.
9. Rareza nula permanece fuera de IRC.
10. Temporalidad no crea raíces estructurales.
11. Los perfiles no cambian scores ni evidencia.
12. Los thresholds públicos de SUPPORTED permanecen sin cambios.
13. `validated_discriminator_ids=[]` permanece sin discriminadores reales.

## 11. Corpus y procedencia

La release amplía el corpus a 40 fuentes y 97 conceptos para documentar la
baseline de Fortuna/Espíritu, secta y Daimon.

La incorporación documental no añade puntuación por sí sola. Las fórmulas
históricas son doctrina/técnica operacionalizada; su uso como variable ALMAS
sigue sometido a los techos inferenciales del proyecto.

## 12. Compatibilidad

La release conserva:

- contratos M00–M31;
- canonical_analysis schema 1.0.0;
- adaptadores precomputados;
- thresholds IEM/ICC/IRC/R_min;
- discriminación ontológica separada;
- gates de promoción L3;
- aislamiento de casos privados.

Los cambios de M18/M21/M23/M30 son compatibles a nivel de pipeline, pero
modifican legítimamente resultados cuantitativos porque corrigen la definición
operacional de recurrencia y completitud.

## 13. Validación automatizada

En el HEAD auditado antes de esta auditoría:

- Contrato público: SUCCESS;
- Núcleo Python 3.10: SUCCESS;
- Núcleo Python 3.12: SUCCESS;
- 327 tests deterministas: OK.

La suite contiene pruebas de:

- recurrencia semántica entre root_keys distintas;
- no duplicación por familia RELCHART;
- incapacidad de support-only para crear PX;
- misión recurrente PS v2;
- unidades derivadas de motivo en Shapley;
- perfiles M30;
- curva horaria sin rating;
- Fortuna/Espíritu;
- ablación con recálculo de PX/PS.

Tras cualquier cambio posterior a esta auditoría debe repetirse CI sobre el
nuevo HEAD antes de fusionar.

## 14. Límites que permanecen

La release no ejecuta un holdout externo real preregistrado.

No existe ningún discriminador ontológico L3 validado.

La recurrencia semántica es una hipótesis operacional del proyecto y todavía
debe someterse a falsos positivos, controles sintéticos y cohortes externas.

Los perfiles resuelven completitud técnica; no resuelven por sí mismos la
incertidumbre ontológica.

La reproducibilidad del software no valida científicamente la astrología ni
convierte PX, PS, IEM, IDD, IRC o modelos nulos en probabilidades metafísicas.

## 15. Decisión de release

ALMAS 1.14.0 cumple el objetivo de corregir la infradetección de recurrencia sin
romper la independencia geométrica de raíces y añade perfiles explícitos para
evitar que un análisis deliberadamente limitado quede degradado por módulos
fuera de alcance.

La release puede fusionarse sólo cuando el HEAD final, incluida esta auditoría,
obtenga SUCCESS en Contrato público y Núcleo Python 3.10/3.12.
