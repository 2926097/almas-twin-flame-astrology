# ALMAS 1.14.0 · Recurrencia semántica, perfiles y sensibilidad horaria

## 1. Objetivo

ALMAS 1.14.0 corrige una limitación observada en 1.13.0: una arquitectura
multitécnica podía repetir el mismo tema relacional en sinastría, declinación,
RELCHART o natal↔dracónica sin que las evidencias compartieran un
`root_key` literal. El resultado era un PX artificialmente bajo o cero.

La solución no fusiona raíces geométricas distintas. Introduce una capa
semántica superior:

`evidencia → root_key → raíz independiente → motif_id → recurrencia → PX/PS`.

La capa es `E_PROJECT_HYPOTHESIS`; no es doctrina ni validación empírica.

## 2. Dos identidades distintas

### 2.1 Root identity

`root_key` sigue describiendo la identidad geométrica de una raíz y conserva
las reglas de deduplicación de M16/M17. 1.14.0 no modifica ni relaja esa
identidad.

### 2.2 Motif identity

`motif_id` agrupa raíces diferentes que expresan un mismo patrón semántico.
El agrupamiento no convierte las raíces en independientes entre sí: cada
familia de dependencia cuenta una sola vez dentro de un motivo.

Motivos primarios congelados en `ALMAS_SEMANTIC_MOTIF_V2`:

- `KARMIC_CONTINUITY`
- `WOUND_REPAIR`
- `IDENTITY_TRANSFORMATION`
- `TRANSFORMATION_POWER`
- `TRANSPERSONAL_FIELD`
- `EROTIC_POLARITY`
- `MIRROR_COMPLEMENTARITY`
- `RELATIONAL_COHERENCE`
- `STRUCTURAL_AFFINITY`

Cada raíz core recibe como máximo un motivo primario.

## 3. Recurrencia PX v2

Un motivo es recurrente cuando aparece en al menos dos familias de dependencia
y al menos dos raíces distintas. Se admite una sola raíz cuando M16 ya ha
demostrado que contiene al menos dos familias independientes.

Las capas `support_only` no pueden crear recurrencia core. Compuesta y
Davison siguen perteneciendo a una sola familia `RELCHART`.
Dracónica↔dracónica y asteroides secundarios continúan como soporte.

Para cada motivo:

1. se toma el máximo de fuerza core por familia;
2. las familias se agregan mediante la función pública `pillar_score`;
3. los motivos recurrentes se agregan de nuevo para producir PX.

El resultado publica además componentes diagnósticos:

- `PX_G_EXACT_ROOT_RECURRENCE`
- `PX_S_SEMANTIC_RECURRENCE`
- `PX_R_RELCHART_CROSS_FAMILY`
- `PX_D_NATAL_DRACONIC_CROSS_FAMILY`

Ningún componente es probabilidad ontológica.

## 4. PS v2 · misión/servicio emergente

PS deja de exigir que una única raíz contenga simultáneamente toda la firma de
misión. Se crean motivos de misión cuando el eje meridiano aparece con:

- Sol → `MISSION_SOLAR`
- Júpiter → `MISSION_JOVIAN`
- Saturno → `MISSION_SATURNIAN`
- eje nodal → `MISSION_NODAL`

El mismo criterio de recurrencia por familias independientes debe cumplirse
antes de alimentar PS.

PS describe recurrencia astrológica de un motivo de misión; no demuestra una
misión compartida factual ni un contrato preencarnatorio literal.

## 5. Shapley e IDD

M21 opera ahora sobre `CANONICAL_EVIDENCE_UNIT`. Una unidad puede ser:

- una raíz independiente;
- un motivo semántico derivado que materializa PX o PS.

Las unidades de motivo son features derivadas, no nuevas raíces
independientes. Shapley distribuye su contribución a IEM_pre sin cambiar esta
clasificación epistemológica.

## 6. Perfiles de análisis

`ALMAS_ANALYSIS_PROFILES_V1` separa completitud técnica de alcance solicitado.

### FULL_MULTIDISCIPLINARY

Perfil estricto por defecto. Requiere las capas estructurales, temporales,
doctrinales y de realidad aplicables.

### FULL_ASTROLOGY

Informe completo limitado a cartas. M26–M29 quedan fuera del alcance por
defecto; M12–M14 y M20 son opcionales. Un módulo fuera del perfil no degrada
M30.

### TEMPORAL

Exige arquitectura estructural y M26; las capas no pertinentes pueden ser
opcionales o excluidas.

### SOUL_CONTRACT

Exige estructura, robustez y doctrina contractual; hechos/temporalidad
adicionales siguen condicionados por disponibilidad.

`M30=READY` significa “completo para el perfil seleccionado”, no “verdad
metafísica demostrada”.

## 7. Sensibilidad horaria v2

`ALMAS_BIRTH_TIME_SENSITIVITY_V2` separa dos productos.

### Curva diagnóstica

Siempre que exista hora, zona y localización calculables, M23 prueba:

`R5, R15, R30, R60, R120`

mediante endpoints cartesianos ±ventana para ambos sujetos. Esta curva puede
calcularse aunque no exista una categoría documental A/B/C/D.

### Componente BIRTH_TIME

Sólo se agrega a IRC cuando ambos sujetos tienen una categoría de fiabilidad
horaria admitida. Una hora escrita en una carta no recibe automáticamente una
Rodden Rating.

Si falta fiabilidad documentada:

- M23 puede quedar `COMPLETED`;
- la curva diagnóstica se publica;
- `robustness_component=null`;
- M25 no inventa BIRTH_TIME;
- una arquitectura dependiente de hora no puede alcanzar `SUPPORTED` por el
  gate canónico v2.

## 8. Lotes históricos por defecto

M13 incorpora `ALMAS_HELLENISTIC_LOTS_V1` cuando no se suministra una
`lot_policy` explícita.

La baseline calcula únicamente Fortuna y Espíritu, con inversión diurna/nocturna
y fuentes históricas registradas. La secta se resuelve preferentemente desde
entrada explícita y, como fallback operativo, desde la posición por casa del
Sol respecto del horizonte.

No se añaden Eros, Necesidad u otros lotes por defecto porque sus variantes
históricas requieren decisiones doctrinales adicionales.

## 9. Robustez y ablación

Las ablaciones de 1.14.0 recalculan el grafo de motivos después de retirar
raíces. No reutilizan PX/PS congelados del baseline. Por tanto, retirar una
familia independiente puede destruir legítimamente la recurrencia semántica y
reducir PX/PS.

## 10. Invariantes

1. `root_key` no se reescribe para fabricar recurrencia.
2. Una familia de dependencia cuenta una vez por motivo.
3. `support_only` no crea PX/PS core.
4. RELCHART continúa siendo una única familia.
5. PX/PS no crean PU.
6. PU sigue `NOT_EVALUABLE` sin discriminador L3 validado.
7. IDD no se convierte en discriminador ontológico.
8. Rareza nula sigue fuera de IRC y no es probabilidad metafísica.
9. Un perfil cambia completitud, nunca puntuaciones ni evidencia.
10. READY es completitud del perfil, no validación metafísica.
