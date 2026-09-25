---
name: almas-twin-flame-astrology
description: Reproducible multidisciplinary relationship-astrology research skill for soul-bond differential analysis, twin-flame models, karmic and soulmate models, structural/temporal validation, doctrinal comparison, hermeneutics and canonical reports.
version: 1.8.4
author: Proyecto ALMAS
metadata:
  public_release: true
  tags: [astrology, relationships, esotericism, metaphysics, hermeneutics, research, validation]
---

# ALMAS · Astrología Metafísica Relacional v1.8.4

## 0. Public release status

This is the public `1.8.4` release of the ALMAS metaphysical relationship-astrology engine. The GitHub distribution prioritizes generalized rules, reusable implementation contracts, public-source provenance and synthetic examples. Real cases may appear only when their underlying data are already public and independently verifiable, with provenance recorded.

### Metaphysical research stance

ALMAS uses astrology as a **metaphysical method of inquiry** into soul architecture, relational origin/history/function, karmic or dharmic continuity, polarity, activation, integration and other defined metaphysical dimensions. The methodological controls in this skill are quality controls inside that paradigm: they prevent dependency inflation, case-fitting and unsupported ontological jumps; they are not a rejection of metaphysical inquiry.

The skill follows a **calculation → evidence → validation → metaphysical ontology → differential diagnosis → hermeneutics → report** protocol. It is not a single-label detector.

## 1. Objective

Study a relationship through a reproducible multi-layer architecture combining astronomy/astrology, structural validation, temporal activation, comparative doctrine and hermeneutic synthesis.

The core operational comparison may score four recurrent models:
- `AF`: almas afines / soul-affinity model.
- `KA`: vínculo kármico / karmic model.
- `AG`: almas gemelas / soulmate model.
- `LG`: llamas gemelas / twin-flame model.

These scores are structural compatibility indices, never metaphysical probabilities. Several models may be compatible simultaneously.

The broader ontology must not be reduced to those four labels. Analyse independent axes such as origin, history, function, polarity, modality, phase, viability and reciprocity. Categories such as monadic pair, split soul, twin ray, sacred partner, hieros gamos, mirror, catalytic, healing, teacher/student and mission/service may be examined where doctrinally relevant, but must not be treated as equivalent or forced into one final label.

## 2. Mandatory epistemic separation

Every material claim must preserve one class:
- `A_CALCULATED`: astronomical, geometric or documentary datum.
- `B_TECHNIQUE`: defined astrological/statistical technique.
- `C_DOCTRINE`: explicit claim from an identified source or tradition.
- `D_CONTEMPORARY_USAGE`: current emic/New-Age/community usage.
- `E_PROJECT_HYPOTHESIS`: operational synthesis created by this project.

Never present `E_PROJECT_HYPOTHESIS` as `C_DOCTRINE`.

Source hierarchy:
- `P1_PRIMARY`
- `P2_ACADEMIC`
- `P3_HISTORICAL_TECHNICAL`
- `P4_IDENTIFIED_METHOD`
- `P5_EMIC`
- `P6_WEAK_UNVERIFIED`

## 3. Non-negotiable rules

1. No single aspect, asteroid, atacir, synchronicity, subjective experience or event may create an ontological category.
2. Temporal techniques primarily indicate **when** a pre-existing architecture activates. Their direct contribution to structural model scoring is zero.
3. Intensity, suffering, obsession, destiny-feelings, sexual intensity or perceived telepathy do not automatically elevate a bond to a superior spiritual category.
4. Statistical rarity under an explicit null model is not metaphysical probability.
5. Do not infer another person's private thoughts, fidelity, sexuality, mental state, consent or future decisions from astrology or metaphysics.
6. Real-world facts, consent and boundaries prevail over symbolic interpretation.
7. Missing data are `NOT_EVALUABLE`, not negative evidence.
8. Mathematically dependent transformations do not count as independent confirmations.
9. Normalize ASC/DSC, MC/IC, Node/anti-Node and Vertex/Anti-Vertex when counting structures.
10. Exclude the draconic chart's own fixed nodal anchors from evidentiary recurrence.
11. Secondary asteroids are corroborative and cannot create a category absent from stronger structural layers.
12. Exploratory and confirmatory runs must remain distinguishable.
13. Counterevidence must be actively searched and applied once.
14. When two models yield the same observable signature and no validated discriminator exists, return `INSUFFICIENT` rather than forcing a choice.

## 4. States

Use:
- `SUPPORTED`: predefined criteria are met.
- `COMPATIBLE`: evidence is coherent but insufficient for stronger support.
- `INSUFFICIENT`: competing hypotheses cannot be distinguished.
- `CONTRADICTED`: relevant evidence is materially incompatible.
- `NOT_EVALUABLE`: required data are unavailable or unusable.

These are methodological states, not probabilities.

## 5. Ontología relacional multiaxial

ALMAS no usa una etiqueta única como sustituto de la arquitectura completa.

Evaluar de forma independiente:

### ORIGIN
`INDEPENDENT_SOULS`, `SOUL_FAMILY_GROUP`, `RELATED_SOUL_ROOTS`, `SHARED_ORIGIN_UNDIFFERENTIATED`, `MONADIC_COMMON_SOURCE`, `SPLIT_SOUL`, `TWIN_SOUL`, `TWIN_FLAME_MODEL`, `INDETERMINATE`.

### PREINCARNATION_CONTRACT
`NONE_DETECTED`, `INDIVIDUAL_PREINCARNATIONAL_CHOICE`, `MISSION_PREINCARNATIONAL`, `BILATERAL_SOUL_CONTRACT`, `MULTIPARTY_SOUL_PLAN`, `INDETERMINATE`.

### HISTORY_CONTINUITY
`NEW_CONNECTION`, `FAMILIARITY`, `KARMIC_CONTINUITY`, `GILGUL_CONTINUITY`, `PAIRED_REINCARNATION`, `UNRESOLVED_CONTINUITY`, `INDETERMINATE`.

### FUNCTION
`COMPANIONSHIP`, `LEARNING`, `MIRROR`, `CATALYSIS`, `HEALING_REPAIR`, `INITIATION`, `EVOLUTION`, `INTEGRATION`, `MISSION_SERVICE`, `LIBERATION`, `CLOSURE_FUNCTION`.

### PHENOMENOLOGY
`RECOGNITION`, `FAMILIARITY_FEELING`, `SYNCHRONICITY`, `TRANSPERSONAL_MEANING`, `INTENSITY`, `ARCHETYPAL_EXPERIENCE`, `DREAM_OR_VISION`, `OTHER`.

### POLARITY
`SIMILARITY`, `COMPLEMENTARITY`, `MIRROR`, `EROTIC`, `ARCHETYPAL`, `MASCULINE_FEMININE_DOCTRINAL`, `MIXED`, `INDETERMINATE`.

### MODALITY
`MATERIAL_3D`, `TRANSITIONAL`, `MIXED_3D_TRANSPERSONAL`, `PREDOMINANTLY_TRANSPERSONAL`, `INDETERMINATE`.

### PHASE
`RECOGNITION`, `ACTIVATION`, `CRISIS_MIRROR`, `SEPARATION`, `SURRENDER`, `INTEGRATION`, `REUNION`, `SERVICE`, `CLOSURE`, `INDETERMINATE`.

### REAL_VIABILITY
`UNKNOWN`, `STABLE`, `UNSTABLE`, `SEPARATED`, `NON_ROMANTIC`, `NO_CONTACT`, `DEFINED_BY_FACTS`.

### RECIPROCITY
`BILATERAL`, `PARTIAL`, `ASYMMETRIC`, `NOT_EVALUABLE`.

Critical non-implications:

- origin does not imply contract;
- contract does not imply shared origin or romantic union;
- continuity does not imply twin flame;
- function does not imply origin;
- phenomenology does not imply ontology;
- mission does not imply shared origin;
- phase does not imply viability;
- astrological reciprocity does not substitute current interpersonal reciprocity.

Normative registry: `reference/ontology-registry.json`.
Output schema: `schemas/ontology-output.schema.json`.

## 6. Execution modes

- `FULL`: all applicable structural, cross-chart, temporal, robustness, doctrinal and reporting modules.
- `TARGETED`: selected techniques only; output must be marked partial.
- `TEMPORAL`: temporal activation of a prior structural analysis; otherwise `TEMPORAL_UNANCHORED`.
- `REPORT`: derives only from canonical analysis.

## 7. Mandatory module graph

`M00 manifest → M01 data quality → M02 natal → M03 synastry → M04 nodes/angles/houses/regencies → M05 declinations → M06 antiscia/contra-antiscia → M07 composite → M08 Davison → M09 relationship-chart consonance → M10 individual draconics → M11 natal↔draconic → M12 draconic↔draconic → M13 lots → M14 secondary symbolic layer → M15 evidence extraction → M16 dependency/deduplication → M17 independent roots → M18 pillars → M19 structural model indices → M20 counterevidence → M21 differential attribution/discrimination → M22 ablation → M23 time sensitivity → M24 null models → M25 robustness → M26 temporal activation → M27 dated events → M28 doctrine/hermeneutics → M29 viability/reciprocity → M30 report gate → M31 report`.

A calculable required module omitted in `FULL` blocks a full result. A genuinely impossible module is `NOT_EVALUABLE` and must not be replaced by zero.

## 8. Astrological scope

Include, where data allow:
- tropical natal charts;
- complete synastry;
- signs, houses, cusps and rulerships;
- lunar nodes and angles;
- declinations/parallels/contra-parallels;
- antiscia and contra-antiscia;
- midpoint composite;
- Davison relationship chart;
- individual draconic charts;
- natal↔draconic in both directions;
- draconic↔draconic as corroborative layer;
- Hellenistic lots with formula and source;
- secondary asteroids as support-only;
- progressions;
- solar arc;
- C360 and exploratory atacires;
- transits/eclipses;
- event charts;
- recurrent-degree roots;
- Monte Carlo/null models;
- ablation;
- birth-time robustness.

Dependency rules:
- Composite and Davison belong to one `RELCHART` family for independence accounting.
- Draconic↔draconic is corroborative, not independently core-eligible by default.
- Secondary asteroids are `support_only=true`.
- Houses and signs contextualize roots; they do not create ontological roots alone.

## 9. Evidence strength

For a contact within a declared orb:

`F = max(0, 1 - (distance/orb_limit)^2)`

`S = F × technique_reliability × birth_time_factor × aspect_coefficient`

Raw pillar loadings satisfy `sum(loadings) <= 1`.
For scoring, normalize within each evidence item:

`L*_p = L_p / max(L)`

`contribution_p = S × L*_p`.

## 10. Pillars

- `PA`: Afinidad estructural.
- `PK`: Continuidad kármica.
- `PE`: Espejo y complementariedad.
- `PR`: Coherencia relacional.
- `PX`: Recurrencia independiente.
- `PT`: Transformación e integración.
- `PS`: Misión/servicio.
- `PU`: Singularidad diádica, experimental.

For each pillar, use the three strongest independent roots `r1 >= r2 >= r3`:

`P = 100 × (r1 + 0.5r2 + (1/3)r3) / (1 + 0.5 + 1/3)`.

## 11. Core model compatibility index — IEM

`IEM` = **Índice de Encaje del Modelo**.

Core pillars:
- AF: PA, PR.
- KA: PK, PT.
- AG: PA, PE, PR, PX.
- LG: PA, PE, PR, PX, PT.

Support pillars:
- AF: PE, PX.
- KA: PX, PR, PE.
- AG: PK, PT, PS.
- LG: PK, PS, PU.

`CORE` = geometric mean of evaluable essential pillars in [0,1].

`SUPPORT` = arithmetic mean of evaluable support pillars.

`IEM_pre = 100 × CORE × (0.90 + 0.10 × SUPPORT)`

`IEM_final = IEM_pre × (1 - 0.30 × ICE/100)`

IEMs are independent and do not sum to 100.

## 12. Differential discrimination — IDD

`IDD` = **Índice de Discriminación Diagnóstica**. `IDE` may appear as a legacy alias for `IDD`.

Use Shapley attribution over `IEM_pre` to estimate which independent roots distinguish models. Exact attribution is preferred for small root sets; deterministic permutation approximation may be used for larger sets with convergence checks.

Normalize primary root contributions by model and compare distributions with Jensen-Shannon divergence. A practical 0–100 form is:

`IDD(m,n) = 100 × sqrt(JSD_base2(p_m, p_n))`.

Interpretive bands:
- `<15`: substantial overlap;
- `15–29`: transitional distinction;
- `30–49`: material distinction;
- `>=50`: very marked distinction.

IDD measures separation of evidence architecture, not metaphysical truth.

## 13. Robustness — IRC

`IRC` = **Índice de Robustez de la Clasificación**.

Applicable components may include birth-time robustness, layer ablation, parameter perturbation, IDD stability and validated discriminators where available.

For perturbation family X:

`R_X = exp(-delta90/20) × sqrt(G)`

where `G` is the fraction preserving preregistered interpretive bands.

`IRC = 100 × geometric_mean(applicable R_i)`

`R_min = min(applicable R_i)`.

## 14. Temporal activation — IAT

`IAT` = **Índice de Activación Temporal**.

A temporal signal contributes only when anchored to a pre-existing structural root.

Classes:
- direct repetition: K=1.00;
- relational root activation: K=0.90;
- endpoint activation: K=0.70;
- unanchored: K=0.

Primary temporal families:
- `TPROG`: secondary progressions;
- `TDIR`: solar arc and related directed family;
- `TTRANSIT`: transits;
- `TECLIPSE`: eclipses under declared rules;
- `TREL`: progressed/directed composite or Davison.

Within one root/family keep the strongest signal. Aggregate independent temporal families and roots using preregistered weights. IAT never modifies IEM.

## 15. Coverage — ICC

`ICC` = **Índice de Cobertura Canónica**.

Dependency-aware domains:
1. natal foundation;
2. synastry/nodes;
3. angles/houses/rulership;
4. symmetries;
5. relationship charts;
6. draconic layers;
7. lots/secondary symbolic.

Each domain quality q may be 1 complete, 0.5 degraded, 0 not evaluable.

`ICC = 100 × sum(q) / 7`.

Temporal and documentary coverage may be reported separately as `ICC_T` and `ICC_D`.

## 16. Counterevidence — ICE

`ICE` = **Índice de Contraevidencia Estructural**.

ICE measures explicit contradictions or structural incompatibilities. It is not a penalty for missing data and must not double-count the same contradiction through dependent layers.

## 17. Structural support gate

A model may be marked `SUPPORTED` only when all preregistered minimums are met, including adequate IEM, core strength, coverage, robustness, minimum perturbation resilience, evaluability of essential pillars and absence of essential contradiction.

The public default for v1.0.0 is:
- `IEM_final >= 75`;
- `CORE >= 0.65`;
- `ICC >= 80`;
- `IRC >= 70`;
- `R_min >= 0.50`;
- no essential contradiction;
- essential pillars evaluable.

This is structural support within the model, not metaphysical proof.

## 18. Discriminator registry

A binary discriminator may only be used when preregistered and validated. If two candidate ontologies remain observationally equivalent under the available evidence, return `INSUFFICIENT`.

Do not turn transformation, mission, mirroring, draconic recurrence, asteroids or a higher LG IEM into an ontological discriminator unless a validated rule exists.

## 19. Null models and rarity

Freeze the feature set, orb policy, event set and null model before confirmatory inspection.

Acceptable null models may include matched-age, within-year, matched-age-clock, ephemeris-date, pair-shuffle, event-date-shift or technique-specific cycle nulls.

Use Monte Carlo/Wilson intervals where appropriate. Report rarity only as structural frequency under the declared null.

## 20. Doctrine and comparative hermeneutics

Do not collapse traditions into equivalence.

For every doctrinal comparison identify:
1. provenance;
2. primary source or best available authority;
3. historical meaning;
4. contemporary usage;
5. what the source does **not** establish;
6. whether the correspondence is doctrine or project hypothesis.

Relevant corpora may include Platonism/Neoplatonism, Kabbalah, Christian mysticism, Sufism, Hindu/Vedantic/Tantric traditions, Buddhism where appropriate, Spiritism, Theosophy, Alice Bailey, I AM Activity, Summit Lighthouse, New Age and academic studies of esotericism.

Examples of non-equivalence:
- Aristophanes' speech in Plato's *Symposium* is an antecedent, not identical to modern twin-flame doctrine.
- Plotinus does not by itself establish one unique split counterpart.
- Kabbalistic zivug/gilgul/tikkun are comparanda, not automatically modern twin flames.
- Christian mystical marriage is primarily soul–God language.
- Sufi lover/Beloved language must not be automatically retrofitted into modern dyadic soul models.
- Buddhist anatta/anātman prevents casually importing an enduring split-soul ontology.

Doctrine interprets evidence; doctrine never adds IEM points.

## 21. Hermeneutic synthesis

A complete report must explain:
- what was found;
- source and technique;
- symbolic meaning;
- compatible models;
- competing alternatives;
- contrary evidence;
- uncertainty and missingness;
- dependency among techniques;
- structural versus temporal components;
- why each final state is adopted.

Do not write the report as a table of aspects. Convert technical findings into a coherent account of relational architecture while preserving traceability to canonical evidence.

## 22. Canonical/report contract

`canonical_analysis.json` is the single analytical truth.

`report_document_model.json` may select, order and display canonical values but cannot alter them.

Recommended report sequence:
1. synthesis;
2. data quality and method;
3. numeric ontology and index definitions;
4. structural architecture;
5. relational/cross-chart layers;
6. differential diagnosis and counterevidence;
7. temporal activation/events;
8. robustness/validation;
9. comparative doctrine/corpus;
10. final synthesis;
11. sources and appendices.

Expand acronyms on first appearance. Use quantified bars as presentation aids, never as metaphysical probability meters.

## 23. PDF/report pipeline

Preferred pipeline:

`canonical_analysis.json → report_document_model.json → structured document → PDF → preflight → render every page → inspect → correct → re-render/verify`.

For long reports, DOCX authoring followed by controlled PDF conversion is preferred. Use vertical page orientation unless the target publication format requires otherwise.

## 24. Validation invariants

A release-grade run must verify at minimum:
- no omitted calculable FULL module;
- no metaphysical probability;
- no max-IEM classifier;
- no temporal or phenomenological contribution to structural IEM;
- no asteroid-created ontology;
- dependency/root deduplication;
- composite/Davison dependency control;
- missing != zero;
- ambiguity preserved when discriminators are absent;
- IDD != validated discriminator;
- real-world consent/facts prevail;
- doctrine != project hypothesis;
- report values equal canonical values.

## 25. New-category rule

When a new category or technique is proposed:
1. identify provenance;
2. compare it with existing categories;
3. define evidence requirements;
4. state what cannot be concluded;
5. integrate it into the ontology;
6. create reproducible rules;
7. add tests;
8. avoid fitting criteria to the case under study;
9. validate before promoting it to a confirmatory rule.

## 26. Output standard

Every full analysis should clearly distinguish:
- data/documentation;
- technique;
- doctrine;
- contemporary usage;
- project hypothesis;
- structural evidence;
- temporal activation;
- counterevidence;
- uncertainty;
- real-world viability and reciprocity when observable.

The objective is not to confirm a prior belief, but to build the broadest, most documented, reproducible and discriminating model possible for studying soul-bond narratives and astrological relationship structures.


## 32. Interoperabilidad con ALMAS Contrato Álmico

La reconstrucción de un posible **acuerdo preencarnatorio** se ejecuta en el **módulo interno de Contrato Preencarnatorio** de la misma skill ALMAS.

El motor astrológico produce la arquitectura trazable que el módulo contractual consume como evidencia de entrada.

Salida de intercambio recomendada:

`cálculo astrológico → raíces independientes → pilares/ontología → temporalidad → robustez/contraevidencia → astrology_to_soul_contract.json`

La interfaz normativa se define en `schemas/astrology-to-soul-contract.schema.json`.

El punto de entrada especializado del módulo contractual se conserva en `skills/almas-soul-contract/SKILL.md` por compatibilidad histórica.

Reglas de interoperabilidad:

1. El motor contractual consume raíces y evidencias ya normalizadas; no recalcula silenciosamente la astrología.
2. Una cláusula contractual debe apuntar a una o más raíces del motor astrológico.
3. La temporalidad contractual sólo puede referirse a activaciones ancladas a arquitectura estructural.
4. La contraevidencia y la robustez viajan con la evidencia; no se eliminan al pasar al motor contractual.
5. Los motores internos pueden evolucionar mediante `engine_revision` o `schema_version`, pero heredan una única versión pública desde `VERSION`.

## 33. Convención lingüística pública

La documentación destinada a lectura humana utiliza **terminología española** como forma principal.

Los identificadores de máquina en inglés pueden conservarse cuando sean necesarios para compatibilidad con código o esquemas, acompañados de su denominación española cuando sea útil.

Ejemplos:

- `soul contract` → **contrato álmico**;
- `preincarnational agreement` → **acuerdo preencarnatorio**;
- `relationship chart` → **carta relacional**;
- `root` → **raíz semántica**;
- `counterevidence` → **contraevidencia**;
- `closure` → **cierre**;
- `embodiment` → **encarnación**;
- `reciprocity` → **reciprocidad**.

Esta convención no obliga a renombrar claves internas de software si ello rompe compatibilidad.


## 36. Causa contractual

La causa contractual pertenece al **módulo interno de Contrato Preencarnatorio**. El motor astrológico aporta la tarea previa del receptor, el activador, la geometría, la recurrencia y la robustez necesarias para que el módulo contractual evalúe la causa preencarnatoria.

La causa contractual intenta explicar por qué un factor de A encaja como activador de una tarea que B ya trae antes del encuentro.

Cadena obligatoria:

`TAREA_PREVIA_RECEPTOR → FACTOR_ACTIVADOR_DEL_OTRO → ENCAJE_GEOMETRICO → RECURRENCIA → FUNCION_CONTRACTUAL → CAMPO_COMUN`.

La tarea previa debe identificarse sin usar primero la sinastría. Si sólo aparece después de ver el contacto con la otra persona, la inferencia es circular y se marca `INSUFFICIENT`.

Tipos de causa: reconocimiento, catálisis, confrontación, encarnación, reciprocidad, verdad, integración y liberación.

Referencia: `reference/causa-contractual.md`.


## 37. Integración doctrinal basada en fuentes

ALMAS v1.4.0 inicia una capa formal de genealogía doctrinal.

Archivos normativos:

- `schemas/source-registry.schema.json`;
- `reference/source-registry.json`;
- `reference/concept-registry.json`;
- `reference/doctrinal-genealogy.json`;
- `docs/SOURCE_INTEGRATION_PLAN.md`;
- `docs/SOURCE_GAPS.md`.

Reglas:

1. Una fuente define, contextualiza o limita conceptos; no añade puntuación astrológica por existir.
2. Todo concepto doctrinal debe distinguir antecedentes, doctrina explícita, uso contemporáneo e hipótesis ALMAS.
3. Relaciones entre conceptos usan vínculos explícitos como `NON_EQUIVALENT`, `PARTIAL_OVERLAP`, `COMPARATIVE_ANTECEDENT_ONLY` o `PROJECT_OPERATIONALIZATION`.
4. Una operacionalización astrológica creada por ALMAS permanece `E_PROJECT_HYPOTHESIS`, aunque dialogue con una doctrina P1.
5. Los huecos documentales permanecen `INSUFFICIENT` o `NOT_EVALUABLE`; no se rellenan por semejanza intuitiva.


## 38. Cadena causal del contrato preencarnatorio

En modo FULL, el módulo contractual debe producir una cadena causal adicional:

`TAREA_PREVIA → MOTIVO_DE_ELECCION_DEL_OTRO → ROL_ASUMIDO → CLAUSULA_DE_ACTIVACION → PRUEBA_PACTADA → INTEGRACION_ESPERADA → CONDICION_DE_CUMPLIMIENTO → FORMAS_DE_CIERRE_O_ALTERNATIVA`.

Niveles de resolución:

- `R0_NOT_EVALUABLE`;
- `R1_PREINCARNATIONAL_THEME`;
- `R2_RELATIONAL_PREINCARNATIONAL_FUNCTION`;
- `R3_BILATERAL_AGREEMENT_MODEL`;
- `R4_LITERAL_CONTENT`.

`R4_LITERAL_CONTENT` no puede alcanzar `SUPPORTED` desde astrología.

Granularidad contractual:

`THEME → FUNCTION → ROLE → CONDITION → EVENT → DETAIL`.

La fuerza inferencial disminuye hacia EVENT/DETAIL. La temporalidad puede documentar activación de un evento, pero no convertirlo retrospectivamente en detalle pactado.

Referencia: `reference/contract-causal-architecture-v2.md`.
Esquema: `schemas/preincarnation-contract-chain.schema.json`.


## 39. Traducción doctrina → astrología

Toda correspondencia doctrinal se procesa en tres pasos:

`FUENTE → VARIABLE_METAFISICA → OPERACIONALIZACION_ASTROLOGICA`.

La fuente define el concepto y sus límites. La variable metafísica permite compararlo dentro de ALMAS. La operacionalización astrológica pertenece normalmente a `E_PROJECT_HYPOTHESIS`.

Ejemplo:

`Kardec 258–259 → PREBIRTH_THEME_OR_TRIAL → tareas individuales + nodos/regentes + estructura saturnina + recurrencia`.

Kardec no es fuente de esa técnica astrológica; sólo de la doctrina de elección del género de prueba.

Registro normativo: `reference/doctrine-to-astrology-map.json`.
Documentación: `docs/DOCTRINE_TO_ASTROLOGY.md`.


## 40. Motor de causalidad preencarnatoria

El motor causal evalúa si una persona activa de forma específica una tarea que la otra ya trae.

Cadena:

`TAREA_PREVIA_RECEPTOR → ACTIVADOR_DEL_OTRO → ENCAJE → RECURRENCIA → DIRECCION → CAMPO_COMUN → FUNCION → CLAUSULA`.

Niveles de especificidad:

- `C0_GENERIC`;
- `C1_TARGETED`;
- `C2_MULTIROOT`;
- `C3_PAIR_SPECIFIC_EMERGENT`.

`C0_GENERIC` no puede alcanzar `SUPPORTED`.  
`C1_TARGETED` no puede alcanzar `SUPPORTED` sin una segunda raíz independiente o corroboración independiente equivalente.

La temporalidad no crea causalidad.

Referencia: `reference/preincarnation-causality-engine.md`.
Registro: `manifests/causal-type-registry.json`.
Esquema: `schemas/preincarnation-causality.schema.json`.


## 41. Discriminación transversal

ALMAS distingue entre:

- discriminadores funcionales/epistémicos;
- discriminadores ontológicos.

Puede distinguirse operacionalmente:

- continuidad frente a conexión nueva;
- arquitectura contractual frente a karma genérico;
- contrato funcional frente a catálisis sin cadena contractual;
- misión/servicio frente a origen compartido;
- fenomenología frente a ontología.

Permanecen `NOT_VALIDATED` como discriminadores ontológicos:

- R2 función contractual vs R3 acuerdo bilateral literal;
- raíz relacionada vs zivug;
- zivug vs twin flame;
- split-soul vs twin flame;
- monádico vs raíz relacionada;
- twin-soul vs twin-flame;
- AG vs LG.

Registro: `manifests/cross-model-discriminator-registry.json`.


## 42. Ablación contractual

Una ejecución FULL del contrato debe ejecutar la batería:

`AB0_FULL`, `AB1_NO_ASTEROIDS`, `AB2_NO_TEMPORALITY`, `AB3_NO_DRACONIC`, `AB4_NO_RELCHART`, `AB5_NO_HOUSES_ANGLES`, `AB6_NO_NODES`, `AB7_TROPICAL_PLANETARY_CORE`, `AB8_INDIVIDUAL_ONLY`.

Objetivos:

- comprobar que tareas previas existen sin la pareja;
- comprobar que causas/cláusulas sobreviven sin asteroides y temporalidad;
- medir dependencia de dracónica, cartas relacionales y ángulos;
- separar núcleo estructural de soporte auxiliar.

Clases: `CORE_STABLE`, `MULTILAYER_STABLE`, `DRACONIC_SENSITIVE`, `DRACONIC_DEPENDENT`, `RELCHART_SENSITIVE`, `RELCHART_DEPENDENT`, `ANGULAR_SENSITIVE`, `SUPPORT_LAYER_DEPENDENT`, `TEMPORAL_ONLY`, `NOT_EVALUABLE`.

Referencia: `reference/contract-ablation.md`.


## 43. Métricas contractuales

El módulo contractual puede cuantificar arquitectura sin convertirla en probabilidad metafísica.

Índices:

- `ITP` — Índice de Tarea Previa;
- `IAA` — Índice de Adecuación del Activador;
- `IRCo` — Índice de Reciprocidad Contractual;
- `ICCo` — Índice de Coherencia del Campo Común;
- `IVC` — Índice de Coherencia Vertical Contractual;
- `IRCT` — Índice de Robustez Contractual;
- `ICE-C` — Índice de Contraevidencia Contractual;
- `ICC-C` — Índice de Cobertura Contractual;
- `IAP` — Índice de Arquitectura Preencarnatoria.

`IAP` resume arquitectura funcional R2. No decide ORIGIN ni eleva automáticamente R3_BILATERAL_AGREEMENT_MODEL a SUPPORTED.

Referencia: `reference/contract-metrics.md`.


## 44. Libre albedrío contractual

Cada cláusula contractual debe distinguir:

- `ESTRUCTURA_PREVIA`;
- `ELECCION_ENCARNADA`;
- `FORMA_RELACIONAL`;
- `RUTA_ALTERNATIVA`.

Niveles de determinación:

- `FD0_NOT_EVALUABLE`;
- `FD1_THEME_FIXED_FORM_OPEN`;
- `FD2_ROLE_TENDENCY_FORM_OPEN`;
- `FD3_CONDITIONAL_ROUTE`;
- `FD4_FIXED_EVENT_CLAIM`.

`FD4_FIXED_EVENT_CLAIM` no puede alcanzar `SUPPORTED` desde astrología.

Toda forma compartida requiere elección y hechos bilaterales. Reconocimiento, contrato u origen no sustituyen consentimiento.

Referencia: `reference/contract-free-will.md`.


## 45. Temporalidad contractual v2

Toda cláusula separa:

`ESTRUCTURA → ACTIVACION → DESARROLLO → INTEGRACION/TRANSFORMACION/CIERRE`.

Estados de ciclo:

- `LATENT`
- `TRIGGERED`
- `ACTIVE`
- `RECURRING`
- `INTEGRATING`
- `EMBODIED`
- `TRANSFORMED`
- `CLOSED`
- `NOT_EVALUABLE`

Estados de ventana:

- `RETROSPECTIVE_CONFIRMED`
- `RETROSPECTIVE_UNCONFIRMED`
- `CURRENT_ACTIVE`
- `PROSPECTIVE_ACTIVATION`
- `EXPLORATORY`
- `UNANCHORED`

Una ventana futura `PROSPECTIVE_ACTIVATION` no permite asignar `EMBODIED`, `TRANSFORMED` ni `CLOSED`.

IAT mide activación de raíces preexistentes y no modifica IAP.

Referencia: `reference/contract-temporality-v2.md`.


## 46. Hechos y biografía documental

Los hechos entran sólo después de congelar la estructura.

Secuencia:

`ESTRUCTURA_CONGELADA → EVENTO_DOCUMENTADO → FUNCIÓN_PROBATORIA`.

Un evento puede corroborar activación, aportar hechos de cumplimiento, contraevidencia, viabilidad, reciprocidad o fenomenología documentada. No puede crear raíces, cláusulas u origen retrospectivamente.

Calidad documental:

- `DQ1_PRIMARY_DOCUMENT`
- `DQ2_DIRECT_SELF_REPORT`
- `DQ3_CORROBORATED_REPORT`
- `DQ4_SECONDARY_REPORT`
- `DQ5_UNVERIFIED`

Clases públicas: `PUBLIC_VERIFIABLE` y `SYNTHETIC`. Los eventos privados no se publican.

Referencia: `reference/documentary-events.md`.
Esquema: `schemas/documentary-event-ledger.schema.json`.


## 38. Gate doctrinal

Antes de integrar una fuente en una conclusión metafísica, clasificar la relación entre la afirmación y la fuente:

- `DIRECT_DOCTRINE`
- `ACADEMIC_DESCRIPTION`
- `HISTORICAL_ANTECEDENT`
- `COMPARATIVE_ANALOGUE`
- `CONTEMPORARY_USAGE`
- `PROJECT_OPERATIONALIZATION`
- `PROJECT_SYNTHESIS`

Referencia normativa: `reference/doctrinal-gate.md`.

### Reglas

1. `C_DOCTRINE` exige fuente primaria pertinente y trazabilidad.
2. `D_CONTEMPORARY_USAGE` no confirma ontología.
3. `PROJECT_OPERATIONALIZATION` y `PROJECT_SYNTHESIS` permanecen `E_PROJECT_HYPOTHESIS`.
4. El gate doctrinal y el gate astrológico son independientes.
5. El número de fuentes nunca aumenta IEM, IAP ni la fuerza de una raíz astrológica.
6. Una categoría con doctrina bien definida pero sin discriminador astrológico suficiente permanece `INSUFFICIENT` en el caso.
7. Una firma astrológica sin correspondencia doctrinal inequívoca no autoriza a reescribir una tradición histórica.

Objeto recomendado: `schemas/doctrinal-claim.schema.json`.

## 39. Separaciones doctrinales obligatorias v1.4

ALMAS preserva, entre otras, las siguientes no-equivalencias:

- elección preencarnatoria ≠ prueba preencarnatoria ≠ misión ≠ plan del alma ≠ contrato bilateral;
- gilgul ≠ contrato álmico;
- zivug ≠ twin flame;
- bat zug ≠ split soul;
- raíz del alma luriana ≠ Mónada teosófica;
- tikkun ≠ reunión romántica;
- uso literario victoriano de Twin-Flame ≠ doctrina Summit Lighthouse;
- astrología esotérica de Bailey ≠ astrología contractual ALMAS;
- carta dracónica ≠ prueba de vidas pasadas;
- reconocimiento/sincronicidad/transformación reportados ≠ ontología.

Estas separaciones son parte del contrato de regresión de la metodología.
