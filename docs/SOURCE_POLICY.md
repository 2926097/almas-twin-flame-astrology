# Política de fuentes y doctrina

ALMAS separa la procedencia histórica/documental de la interpretación del proyecto.

## Clases epistemológicas

- **A_CALCULATED** — dato astronómico, geométrico o documental calculado/verificado.
- **B_TECHNIQUE** — procedimiento astrológico, estadístico o técnico definido de forma explícita.
- **C_DOCTRINE** — afirmación demostrablemente presente en una fuente o escuela identificada.
- **D_CONTEMPORARY_USAGE** — vocabulario o uso emic/New Age/comunitario contemporáneo.
- **E_PROJECT_HYPOTHESIS** — síntesis u operacionalización propia de ALMAS.

E nunca puede presentarse como C.

## Prioridad de fuentes

- **P1_PRIMARY** — texto primario, corpus oficial o fuente doctrinal directa.
- **P2_ACADEMIC** — investigación académica especializada, historia de las religiones o estudios del esoterismo.
- **P3_HISTORICAL_TECHNICAL** — fuente histórica o técnica astrológica/esotérica.
- **P4_IDENTIFIED_METHOD** — autor contemporáneo identificado con método explícito.
- **P5_EMIC** — fuente útil para documentar uso vivo de una comunidad.
- **P6_WEAK_UNVERIFIED** — material anónimo, SEO, no atribuido o débil/no verificado.

Prioridad y función son variables distintas. Una fuente puede ser P1 y, aun así, ser literaria en lugar de doctrinal.

## Roles de fuente

- **DOCTRINAL_PRIMARY** — texto primario de una enseñanza religiosa, mística o esotérica.
- **ACADEMIC_ANALYSIS** — estudio académico o histórico especializado.
- **ACADEMIC_CONTEXT** — contextualización académica.
- **HISTORICAL_TECHNICAL** — material técnico histórico.
- **IDENTIFIED_METHOD** — autor/escuela moderna con procedimiento explícito.
- **EMIC_USAGE** — fuente que documenta uso vivo de una comunidad.
- **LITERARY_ESOTERIC_PRIMARY** — obra literaria que desarrolla explícitamente motivos esotéricos/metafísicos.
- **LITERARY_PRIMARY** — obra literaria útil para genealogía simbólica o lexical.
- **LITERARY_CRITICISM** — investigación sobre transmisión y recepción literaria.
- **HISTORICAL_RECEPTION** — reseña, prensa o recepción histórica.
- **LEXICAL_HISTORY** — fuente útil para historia de términos y vocabulario.
- **WEAK_UNVERIFIED** — fuente débil o no verificada.

## Regla de no equivalencia

Motivos parecidos entre tradiciones no establecen identidad doctrinal.

Ejemplos:

- El mito de Aristófanes en Platón puede compararse con imágenes modernas de división/reunión, pero no es por sí mismo una doctrina moderna de llamas gemelas.
- La terminología de Mónada teosófica no demuestra una doctrina romántica de pareja monádica.
- La arquitectura mónada–alma–personalidad de Alice Bailey no debe reescribirse como taxonomía de llamas gemelas sin base textual explícita.
- El corpus de Summit Lighthouse/Elizabeth Clare Prophet sí contiene una doctrina moderna explícita de twin flames y debe tratarse de forma distinta a antecedentes o analogías anteriores.
- Los comparanda hindúes, budistas, cabalísticos, cristianos o sufíes conservan su contexto doctrinal propio.

M28 no puede inferir identidad entre dos conceptos sólo porque existan semejanzas funcionales, fenomenológicas o terminológicas. Cuando se afirma identidad doctrinal debe declararse el par mediante `concept_id` + `identity_target_concept_id` y no puede existir una relación genealógica explícita de no equivalencia.

## Trazabilidad mínima

Para cada afirmación doctrinal material se registrará, cuando sea posible:

- autor o fuente atribuida;
- obra/título;
- fecha;
- pasaje, página o sección;
- prioridad P1–P6;
- rol de la fuente;
- localizador bibliográfico/URL;
- qué sostiene explícitamente;
- qué no sostiene;
- estado de verificación;
- tipo y alcance del ancla.

El registro canónico está en `reference/source-registry.json`.

## Gate de doctrina directa

Una afirmación `C_DOCTRINE + DIRECT_DOCTRINE` marcada `SUPPORTED` requiere:

1. `source_registry` con metadatos completos;
2. al menos una fuente `P1_PRIMARY`;
3. `source_role=DOCTRINAL_PRIMARY`;
4. `verification_status=VERIFIED_PRIMARY`;
5. `evidence_scope=DOCTRINAL_CLAIM`;
6. ancla verificable registrada y citada por el claim;
7. `source_support_refs` que apunte al índice concreto de `supports[]`;
8. `does_not_support_checked=true`.

`source_support_refs` aporta trazabilidad reproducible hacia el alcance declarado de la fuente. No sustituye la revisión filológica o histórica del pasaje.

## Descripción académica

`ACADEMIC_DESCRIPTION` no se convierte en doctrina primaria. Requiere al menos una fuente P2 académica con ancla y alcance adecuados. Puede sostener una descripción histórica, sociológica o fenomenológica, no validar ontología.

## Uso contemporáneo

`D_CONTEMPORARY_USAGE` documenta cómo una comunidad, autor o corriente usa un término. Puede apoyarse en fuentes académicas, emic o métodos contemporáneos identificados. La salida mantiene siempre:

`contemporary_usage_promoted_to_ontology=false`.

## Hipótesis ALMAS

Una `E_PROJECT_HYPOTHESIS`:

- se declara como construcción del proyecto;
- conserva fuentes y alternativas;
- no puede usar `DIRECT_DOCTRINE`;
- no puede atribuir a una fuente la operacionalización astrológica creada por ALMAS;
- mantiene `project_hypothesis_promoted_to_doctrine=false`.

## Regla de no acumulación

El número de fuentes no se convierte en puntuación estructural.

`N_FUENTES ≠ FUERZA_ASTROLOGICA`

La redundancia documental puede aumentar la confianza en una atribución histórica o doctrinal, pero no en la presencia del fenómeno en un caso particular.

## Regla del corpus literario

La literatura puede usarse para:

- genealogía de términos y motivos;
- transmisión de imaginarios metafísicos;
- comparación de reconocimiento, división/reunión, destino, afinidad espiritual, reencarnación y planificación preencarnatoria;
- puentes históricos entre doctrina y espiritualidad popular.

No puede usarse automáticamente para:

- establecer doctrina;
- crear reglas astrológicas;
- validar categorías ontológicas;
- demostrar continuidad histórica entre tradiciones distintas.

El corpus literario curado se conserva separadamente en `reference/literary-corpus.json`.
