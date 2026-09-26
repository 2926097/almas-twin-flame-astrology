---
name: almas-twin-flame-astrology
description: Skill multidisciplinar reproducible de astrología relacional para análisis diferencial de vínculos del alma, modelos de llamas gemelas, vínculos kármicos y almas gemelas, validación estructural/temporal, comparación doctrinal, hermenéutica e informes canónicos.
version: 1.12.0
author: Proyecto ALMAS
metadata:
  public_release: true
  tags: [astrology, relationships, esotericism, metaphysics, hermeneutics, research, validation]
---

# ALMAS · Astrología Metafísica Relacional v1.12.0

## 0. Estado de la release pública

Ésta es la release pública `1.12.0` del motor ALMAS de astrología metafísica relacional. La distribución en GitHub prioriza reglas generalizadas, contratos de implementación reutilizables, procedencia de fuentes públicas y ejemplos sintéticos. Los casos reales sólo pueden incorporarse cuando sus datos subyacentes ya son públicos e independientemente verificables y la procedencia queda registrada.

### Enfoque de investigación metafísica

ALMAS utiliza la astrología como **método metafísico de investigación** de la arquitectura del alma, el origen, historia y función relacional, la continuidad kármica o dhármica, la polaridad, la activación, la integración y otras dimensiones metafísicas definidas. Los controles metodológicos de esta skill son controles de calidad internos al paradigma: evitan inflación por dependencia, ajuste retrospectivo al caso y saltos ontológicos no sustentados; no constituyen una negación de la investigación metafísica.

La skill sigue el protocolo **cálculo → evidencia → validación → ontología metafísica → diagnóstico diferencial → hermenéutica → informe**. No es un detector de etiqueta única.

## 1. Objetivo

Estudiar una relación mediante una arquitectura multicapa reproducible que combine astronomía/astrología, validación estructural, activación temporal, doctrina comparada y síntesis hermenéutica.

La comparación operativa central puede puntuar cuatro modelos recurrentes:
- `AF`: almas afines.
- `KA`: vínculo kármico.
- `AG`: almas gemelas / soulmate.
- `LG`: llamas gemelas / twin flame.

Estas puntuaciones son índices de compatibilidad estructural, nunca probabilidades metafísicas. Varios modelos pueden ser compatibles simultáneamente.

La ontología más amplia no debe reducirse a esas cuatro etiquetas. Deben analizarse ejes independientes como origen, historia, función, polaridad, modalidad, fase, viabilidad y reciprocidad. Categorías como pareja monádica, split soul, twin ray, sacred partner, hieros gamos, espejo, catalítica, sanadora, maestro/alumno y misión/servicio pueden examinarse cuando sean doctrinalmente relevantes, pero no deben tratarse como equivalentes ni forzarse en una única etiqueta final.

## 2. Separación epistemológica obligatoria

Toda afirmación material debe conservar una clase:
- `A_CALCULATED`: dato astronómico, geométrico o documental.
- `B_TECHNIQUE`: técnica astrológica o estadística definida.
- `C_DOCTRINE`: afirmación explícita de una fuente o tradición identificada.
- `D_CONTEMPORARY_USAGE`: uso emic, New Age o comunitario contemporáneo.
- `E_PROJECT_HYPOTHESIS`: síntesis operativa creada por este proyecto.

Nunca presentar `E_PROJECT_HYPOTHESIS` como `C_DOCTRINE`.

Jerarquía de fuentes:
- `P1_PRIMARY`
- `P2_ACADEMIC`
- `P3_HISTORICAL_TECHNICAL`
- `P4_IDENTIFIED_METHOD`
- `P5_EMIC`
- `P6_WEAK_UNVERIFIED`

## 3. Reglas no negociables

1. Ningún aspecto, asteroide, atacir, sincronía, experiencia subjetiva o evento aislado puede crear una categoría ontológica.
2. Las técnicas temporales indican principalmente **cuándo** se activa una arquitectura preexistente. Su contribución directa a la puntuación estructural es cero.
3. Intensidad, sufrimiento, obsesión, sensación de destino, intensidad sexual o telepatía percibida no elevan automáticamente un vínculo a una categoría espiritual superior.
4. La rareza estadística bajo un modelo nulo explícito no es probabilidad metafísica.
5. No inferir pensamientos privados, fidelidad, sexualidad, estado mental, consentimiento o decisiones futuras de otra persona desde astrología o metafísica.
6. Los hechos reales, el consentimiento y los límites prevalecen sobre la interpretación simbólica.
7. Los datos ausentes son `NOT_EVALUABLE`, no evidencia negativa.
8. Las transformaciones matemáticamente dependientes no cuentan como confirmaciones independientes.
9. Normalizar ASC/DSC, MC/IC, Nodo/anti-Nodo y Vertex/Anti-Vertex al contar estructuras.
10. Excluir de la recurrencia probatoria los anclajes nodales fijos propios de la carta dracónica.
11. Los asteroides secundarios son corroborativos y no pueden crear una categoría ausente en capas estructurales más fuertes.
12. Las ejecuciones exploratorias y confirmatorias deben permanecer diferenciadas.
13. La contraevidencia debe buscarse activamente y aplicarse una sola vez.
14. Cuando dos modelos produzcan la misma firma observable y no exista un discriminador validado, devolver `INSUFFICIENT` en vez de forzar una elección.

## 4. Estados

Usar:
- `SUPPORTED`: se cumplen los criterios predefinidos.
- `COMPATIBLE`: la evidencia es coherente pero insuficiente para un soporte más fuerte.
- `INSUFFICIENT`: las hipótesis competidoras no pueden distinguirse.
- `CONTRADICTED`: existe evidencia relevante materialmente incompatible.
- `NOT_EVALUABLE`: los datos requeridos no están disponibles o no son utilizables.

Son estados metodológicos, no probabilidades.

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

No implicaciones críticas:

- origen no implica contrato;
- contrato no implica origen compartido ni unión romántica;
- continuidad no implica llama gemela;
- función no implica origen;
- fenomenología no implica ontología;
- misión no implica origen compartido;
- fase no implica viabilidad;
- reciprocidad astrológica no sustituye reciprocidad interpersonal actual.

Registro normativo: `reference/ontology-registry.json`.
Schema de salida: `schemas/ontology-output.schema.json`.

## 6. Modos de ejecución

- `FULL`: todos los módulos estructurales, cruzados, temporales, de robustez, doctrinales y de reporting aplicables.
- `TARGETED`: sólo técnicas seleccionadas; la salida debe marcarse como parcial.
- `TEMPORAL`: activación temporal de un análisis estructural previo; en otro caso `TEMPORAL_UNANCHORED`.
- `REPORT`: deriva únicamente del análisis canónico.

## 7. Grafo obligatorio de módulos

`M00 manifiesto → M01 calidad de datos → M02 natal → M03 sinastría → M04 nodos/ángulos/casas/regencias → M05 declinaciones → M06 antiscios/contra-antiscios → M07 compuesta → M08 Davison → M09 consonancia de cartas relacionales → M10 dracónicas individuales → M11 natal↔dracónica → M12 dracónica↔dracónica → M13 lotes → M14 capa simbólica secundaria → M15 extracción de evidencia → M16 dependencia/deduplicación → M17 raíces independientes → M18 pilares → M19 índices de modelos estructurales → M20 contraevidencia → M21 atribución/discriminación diferencial → M22 ablación → M23 sensibilidad horaria → M24 modelos nulos → M25 robustez → M26 activación temporal → M27 eventos fechados → M28 doctrina/hermenéutica → M29 viabilidad/reciprocidad → M30 gate de informe → M31 modelo documental`.

La omisión de un módulo calculable requerido en `FULL` bloquea un resultado completo. Un módulo genuinamente imposible es `NOT_EVALUABLE` y no debe sustituirse por cero.

## 8. Alcance astrológico

Incluir, cuando los datos lo permitan:
- cartas natales tropicales;
- sinastría completa;
- signos, casas, cúspides y regencias;
- nodos lunares y ángulos;
- declinaciones/paralelos/contra-paralelos;
- antiscios y contra-antiscios;
- compuesta de puntos medios;
- carta relacional Davison;
- cartas dracónicas individuales;
- natal↔dracónica en ambas direcciones;
- dracónica↔dracónica como capa corroborativa;
- lotes helenísticos con fórmula y fuente;
- asteroides secundarios como `support_only`;
- progresiones;
- arco solar;
- C360 y atacires exploratorios;
- tránsitos/eclipses;
- cartas de eventos;
- raíces de grados recurrentes;
- Monte Carlo/modelos nulos;
- ablación;
- robustez frente a hora natal.

Reglas de dependencia:
- Compuesta y Davison pertenecen a una única familia `RELCHART` para el cómputo de independencia.
- Dracónica↔dracónica es corroborativa y no es elegible por defecto como núcleo independiente.
- Los asteroides secundarios son `support_only=true`.
- Casas y signos contextualizan raíces; no crean por sí solos raíces ontológicas.

## 9. Fuerza de evidencia

Para un contacto dentro de un orbe declarado:

`F = max(0, 1 - (distance/orb_limit)^2)`

`S = F × technique_reliability × birth_time_factor × aspect_coefficient`

Las cargas brutas de pilares cumplen `sum(loadings) <= 1`.
Para puntuar, normalizar dentro de cada elemento de evidencia:

`L*_p = L_p / max(L)`

`contribution_p = S × L*_p`.

## 10. Pilares

- `PA`: Afinidad estructural.
- `PK`: Continuidad kármica.
- `PE`: Espejo y complementariedad.
- `PR`: Coherencia relacional.
- `PX`: Recurrencia independiente.
- `PT`: Transformación e integración.
- `PS`: Misión/servicio.
- `PU`: Singularidad diádica, experimental.

Para cada pilar, usar las tres raíces independientes más fuertes `r1 >= r2 >= r3`:

`P = 100 × (r1 + 0.5r2 + (1/3)r3) / (1 + 0.5 + 1/3)`.

## 11. Índice de Encaje del Modelo — IEM

`IEM` = **Índice de Encaje del Modelo**.

Pilares esenciales:
- AF: PA, PR.
- KA: PK, PT.
- AG: PA, PE, PR, PX.
- LG: PA, PE, PR, PX, PT.

Pilares de apoyo:
- AF: PE, PX.
- KA: PX, PR, PE.
- AG: PK, PT, PS.
- LG: PK, PS, PU.

`CORE` = media geométrica de pilares esenciales evaluables en [0,1].

`SUPPORT` = media aritmética de pilares de apoyo evaluables.

`IEM_pre = 100 × CORE × (0.90 + 0.10 × SUPPORT)`

`IEM_final = IEM_pre × (1 - 0.30 × ICE/100)`

Los IEM son independientes y no suman 100.

## 12. Discriminación diferencial — IDD

`IDD` = **Índice de Discriminación Diagnóstica**. `IDE` puede aparecer como alias histórico de `IDD`.

Usar atribución Shapley sobre `IEM_pre` para estimar qué raíces independientes distinguen modelos. Se prefiere la atribución exacta para conjuntos pequeños de raíces; para conjuntos mayores puede usarse una aproximación determinista por permutaciones con control de convergencia.

Normalizar las contribuciones primarias por modelo y comparar distribuciones mediante divergencia Jensen–Shannon. Una forma práctica 0–100 es:

`IDD(m,n) = 100 × sqrt(JSD_base2(p_m, p_n))`.

Bandas interpretativas:
- `<15`: solapamiento sustancial;
- `15–29`: distinción transicional;
- `30–49`: distinción material;
- `>=50`: distinción muy marcada.

IDD mide separación de arquitecturas de evidencia, no verdad metafísica.

## 13. Robustez — IRC

`IRC` = **Índice de Robustez de la Clasificación**.

Los componentes aplicables pueden incluir robustez frente a hora natal, ablación de capas, perturbación de parámetros, estabilidad de IDD y discriminadores validados cuando existan.

Para la familia de perturbación X:

`R_X = exp(-delta90/20) × sqrt(G)`

donde `G` es la fracción que preserva las bandas interpretativas preregistradas.

`IRC = 100 × geometric_mean(applicable R_i)`

`R_min = min(applicable R_i)`.

## 14. Activación temporal — IAT

`IAT` = **Índice de Activación Temporal**.

Una señal temporal contribuye sólo cuando está anclada a una raíz estructural preexistente.

Clases:
- repetición directa: K=1.00;
- activación de raíz relacional: K=0.90;
- activación de endpoint: K=0.70;
- no anclada: K=0.

Familias temporales primarias:
- `TPROG`: progresiones secundarias;
- `TDIR`: arco solar y familia dirigida relacionada;
- `TTRANSIT`: tránsitos;
- `TECLIPSE`: eclipses bajo reglas declaradas;
- `TREL`: compuesta o Davison progresada/dirigida.

Dentro de una raíz/familia conservar la señal más fuerte. Agregar familias temporales y raíces independientes mediante pesos preregistrados. IAT nunca modifica IEM.

## 15. Cobertura — ICC

`ICC` = **Índice de Cobertura Canónica**.

Dominios conscientes de dependencia:
1. base natal;
2. sinastría/nodos;
3. ángulos/casas/regencias;
4. simetrías;
5. cartas relacionales;
6. capas dracónicas;
7. lotes/capa simbólica secundaria.

La calidad q de cada dominio puede ser 1 completa, 0.5 degradada, 0 no evaluable.

`ICC = 100 × sum(q) / 7`.

La cobertura temporal y documental puede informarse separadamente como `ICC_T` e `ICC_D`.

## 16. Contraevidencia — ICE

`ICE` = **Índice de Contraevidencia Estructural**.

ICE mide contradicciones explícitas o incompatibilidades estructurales. No penaliza datos ausentes y no debe contar dos veces la misma contradicción a través de capas dependientes.

## 17. Gate de soporte estructural

Un modelo sólo puede marcarse `SUPPORTED` cuando se cumplen todos los mínimos preregistrados, incluidos IEM suficiente, fuerza de núcleo, cobertura, robustez, resiliencia mínima a perturbaciones, evaluabilidad de pilares esenciales y ausencia de contradicción esencial.

Los umbrales públicos vigentes, heredados desde v1.0.0, son:
- `IEM_final >= 75`;
- `CORE >= 0.65`;
- `ICC >= 80`;
- `IRC >= 70`;
- `R_min >= 0.50`;
- ausencia de contradicción esencial;
- pilares esenciales evaluables.

Es soporte estructural dentro del modelo, no prueba metafísica.

## 18. Registro de discriminadores

Un discriminador binario sólo puede utilizarse cuando está preregistrado y validado. Si dos ontologías candidatas siguen siendo observacionalmente equivalentes con la evidencia disponible, devolver `INSUFFICIENT`.

No convertir transformación, misión, espejo, recurrencia dracónica, asteroides o un IEM LG superior en discriminadores ontológicos salvo que exista una regla validada.

## 19. Modelos nulos y rareza

Congelar el conjunto de características, política de orbes, conjunto de eventos y modelo nulo antes de la inspección confirmatoria.

Los modelos nulos aceptables pueden incluir `matched-age`, `within-year`, `matched-age-clock`, `ephemeris-date`, `pair-shuffle`, `event-date-shift` o nulos específicos de ciclo/técnica.

Usar Monte Carlo e intervalos de Wilson cuando proceda. Informar la rareza sólo como frecuencia estructural bajo el nulo declarado.

## 20. Doctrina y hermenéutica comparada

No fusionar tradiciones como si fueran equivalentes.

Para cada comparación doctrinal identificar:
1. procedencia;
2. fuente primaria o mejor autoridad disponible;
3. significado histórico;
4. uso contemporáneo;
5. qué **no** establece la fuente;
6. si la correspondencia es doctrina o hipótesis del proyecto.

Los corpus relevantes pueden incluir Platonismo/Neoplatonismo, Cábala, misticismo cristiano, sufismo, tradiciones hindúes/Vedanta/Tantra, budismo cuando proceda, espiritismo, Teosofía, Alice Bailey, I AM Activity, Summit Lighthouse, New Age y estudios académicos del esoterismo.

Ejemplos de no equivalencia:
- El discurso de Aristófanes en el *Banquete* de Platón es un antecedente, no idéntico a la doctrina moderna de llamas gemelas.
- Plotino no establece por sí solo una contraparte única escindida.
- Zivug/gilgul/tikkun cabalísticos son comparanda, no llamas gemelas modernas por defecto.
- El matrimonio místico cristiano se formula principalmente en lenguaje alma–Dios.
- El lenguaje sufí amante/Amado no debe reinterpretarse automáticamente como modelo diádico moderno del alma.
- Anatta/anātman budista impide importar sin más una ontología persistente de alma escindida.

La doctrina interpreta evidencia; nunca añade puntos IEM.

## 21. Síntesis hermenéutica

Un informe completo debe explicar:
- qué se encontró;
- fuente y técnica;
- significado simbólico;
- modelos compatibles;
- alternativas competidoras;
- evidencia contraria;
- incertidumbre y datos ausentes;
- dependencia entre técnicas;
- componentes estructurales frente a temporales;
- por qué se adopta cada estado final.

No redactar el informe como una tabla de aspectos. Convertir los hallazgos técnicos en una exposición coherente de la arquitectura relacional, conservando trazabilidad hacia la evidencia canónica.

## 22. Contrato canónico y de informe

`canonical_analysis.json` es la única verdad analítica.

M30 genera el gate de reportabilidad y el fingerprint canónico. M31 construye `report_document_model.json` exclusivamente como estructura de secciones y rutas hacia la verdad canónica; no incrusta ni modifica valores analíticos.

Secuencia canónica de informe:
1. síntesis ejecutiva;
2. calidad de datos y método;
3. ontología numérica y definiciones de índices;
4. arquitectura estructural;
5. capas relacionales/cruzadas;
6. diagnóstico diferencial y contraevidencia;
7. activación temporal/eventos;
8. robustez/validación;
9. doctrina comparada/corpus;
10. síntesis final;
11. fuentes y anexos.

Expandir las siglas en su primera aparición. Las barras cuantificadas son ayudas de presentación, nunca medidores de probabilidad metafísica.

## 23. Pipeline de informe/PDF

Pipeline preferente:

`canonical_analysis.json → M30 report_gate → M31 report_document_model.json → documento estructurado → PDF → preflight → renderizar todas las páginas → inspeccionar → corregir → re-renderizar/verificar`.

Para informes largos se prefiere la autoría en DOCX seguida de conversión controlada a PDF. Usar orientación vertical salvo que el formato de publicación objetivo requiera otra disposición.

## 24. Invariantes de validación

Una ejecución de calidad release debe verificar como mínimo:
- ningún módulo calculable FULL omitido;
- ninguna probabilidad metafísica;
- ningún clasificador por IEM máximo;
- ninguna contribución temporal o fenomenológica al IEM estructural;
- ninguna ontología creada por asteroides;
- deduplicación por dependencia/raíz;
- control de dependencia compuesta/Davison;
- ausente != cero;
- ambigüedad preservada cuando faltan discriminadores;
- IDD != discriminador validado;
- prevalencia de consentimiento/hechos reales;
- doctrina != hipótesis del proyecto;
- valores del informe iguales a los canónicos o, en M31, referencias a rutas sin mutación.

## 25. Regla para categorías nuevas

Cuando se proponga una categoría o técnica nueva:
1. identificar procedencia;
2. compararla con categorías existentes;
3. definir requisitos de evidencia;
4. declarar qué no puede concluirse;
5. integrarla en la ontología;
6. crear reglas reproducibles;
7. añadir tests;
8. evitar ajustar criterios al caso estudiado;
9. validar antes de promoverla a regla confirmatoria.

## 26. Estándar de salida

Todo análisis FULL debe distinguir claramente:
- datos/documentación;
- técnica;
- doctrina;
- uso contemporáneo;
- hipótesis del proyecto;
- evidencia estructural;
- activación temporal;
- contraevidencia;
- incertidumbre;
- viabilidad y reciprocidad reales cuando sean observables.

El objetivo no es confirmar una creencia previa, sino construir el modelo más amplio, documentado, reproducible y discriminante posible para estudiar narrativas de vínculos del alma y estructuras astrológicas relacionales.

## 27. Interoperabilidad con ALMAS Contrato Álmico

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

## 28. Convención lingüística pública

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


## 29. Causa contractual

La causa contractual pertenece al **módulo interno de Contrato Preencarnatorio**. El motor astrológico aporta la tarea previa del receptor, el activador, la geometría, la recurrencia y la robustez necesarias para que el módulo contractual evalúe la causa preencarnatoria.

La causa contractual intenta explicar por qué un factor de A encaja como activador de una tarea que B ya trae antes del encuentro.

Cadena obligatoria:

`TAREA_PREVIA_RECEPTOR → FACTOR_ACTIVADOR_DEL_OTRO → ENCAJE_GEOMETRICO → RECURRENCIA → FUNCION_CONTRACTUAL → CAMPO_COMUN`.

La tarea previa debe identificarse sin usar primero la sinastría. Si sólo aparece después de ver el contacto con la otra persona, la inferencia es circular y se marca `INSUFFICIENT`.

Tipos de causa: reconocimiento, catálisis, confrontación, encarnación, reciprocidad, verdad, integración y liberación.

Referencia: `reference/causa-contractual.md`.


## 30. Integración doctrinal basada en fuentes

ALMAS mantiene una capa formal de genealogía doctrinal separada de la puntuación astrológica.

Archivos normativos:

- `schemas/source-registry.schema.json`;
- `reference/source-registry.json`;
- `reference/concept-registry.json`;
- `reference/doctrinal-genealogy.json`;
- `reference/source-normalization-audit.json`;
- `docs/SOURCE_POLICY.md`;
- `docs/SOURCE_ANCHOR_POLICY.md`;
- `docs/SOURCE_RESEARCH_BACKLOG.md`.

El plan histórico de integración inicial se conserva en `docs/history/SOURCE_INTEGRATION_PLAN_PHASE1.md`.

Reglas:

1. Una fuente define, contextualiza o limita conceptos; no añade puntuación astrológica por existir.
2. Todo concepto doctrinal debe distinguir antecedentes, doctrina explícita, uso contemporáneo e hipótesis ALMAS.
3. Relaciones entre conceptos usan vínculos explícitos como `NON_EQUIVALENT`, `PARTIAL_OVERLAP`, `COMPARATIVE_ANTECEDENT_ONLY` o `PROJECT_OPERATIONALIZATION`.
4. Una operacionalización astrológica creada por ALMAS permanece `E_PROJECT_HYPOTHESIS`, aunque dialogue con una doctrina P1.
5. Los huecos documentales permanecen `INSUFFICIENT` o `NOT_EVALUABLE`; no se rellenan por semejanza intuitiva.


## 31. Cadena causal del contrato preencarnatorio

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


## 32. Traducción doctrina → astrología

Toda correspondencia doctrinal se procesa en tres pasos:

`FUENTE → VARIABLE_METAFISICA → OPERACIONALIZACION_ASTROLOGICA`.

La fuente define el concepto y sus límites. La variable metafísica permite compararlo dentro de ALMAS. La operacionalización astrológica pertenece normalmente a `E_PROJECT_HYPOTHESIS`.

Ejemplo:

`Kardec 258–259 → PREBIRTH_THEME_OR_TRIAL → tareas individuales + nodos/regentes + estructura saturnina + recurrencia`.

Kardec no es fuente de esa técnica astrológica; sólo de la doctrina de elección del género de prueba.

Registro normativo: `reference/doctrine-to-astrology-map.json`.
Documentación: `docs/DOCTRINE_TO_ASTROLOGY.md`.


## 33. Motor de causalidad preencarnatoria

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


## 34. Discriminación transversal

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


## 35. Ablación contractual

Una ejecución FULL del contrato debe ejecutar la batería:

`AB0_FULL`, `AB1_NO_ASTEROIDS`, `AB2_NO_TEMPORALITY`, `AB3_NO_DRACONIC`, `AB4_NO_RELCHART`, `AB5_NO_HOUSES_ANGLES`, `AB6_NO_NODES`, `AB7_TROPICAL_PLANETARY_CORE`, `AB8_INDIVIDUAL_ONLY`.

Objetivos:

- comprobar que tareas previas existen sin la pareja;
- comprobar que causas/cláusulas sobreviven sin asteroides y temporalidad;
- medir dependencia de dracónica, cartas relacionales y ángulos;
- separar núcleo estructural de soporte auxiliar.

Clases: `CORE_STABLE`, `MULTILAYER_STABLE`, `DRACONIC_SENSITIVE`, `DRACONIC_DEPENDENT`, `RELCHART_SENSITIVE`, `RELCHART_DEPENDENT`, `ANGULAR_SENSITIVE`, `SUPPORT_LAYER_DEPENDENT`, `TEMPORAL_ONLY`, `NOT_EVALUABLE`.

Referencia: `reference/contract-ablation.md`.


## 36. Métricas contractuales

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


## 37. Libre albedrío contractual

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


## 38. Temporalidad contractual v2

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


## 39. Hechos y biografía documental

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


## 40. Gate doctrinal

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

## 41. Separaciones doctrinales obligatorias v1.4

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


## 42. Validación externa y preregistro

ALMAS distingue estrictamente `DEVELOPMENT_ONLY`, `INTERNAL_REPLICATION`, `EXTERNAL_HOLDOUT`, `FROZEN_CONFIRMATORY`, `RETIRED` y `NOT_EVALUABLE`.

Un caso que haya intervenido en descubrir, ajustar o seleccionar una regla no puede validar externamente esa misma regla en la versión correspondiente.

Flujo preferente:

`BLIND_STRUCTURAL → DOCUMENTARY_OPENING → FINAL_AUDIT`.

Las autoetiquetas soulmate/twin-flame pertenecen a `D_CONTEMPORARY_USAGE` y nunca constituyen ground truth ontológico.

Endpoints primarios:

- `EV1_REPRODUCIBILITY`
- `EV2_FALSE_SPECIFICITY`
- `EV3_AMBIGUITY_PRESERVATION`
- `EV4_CORE_SURVIVAL`
- `EV5_CONTRACT_SPECIFICITY`
- `EV6_LABEL_INDEPENDENCE`
- `EV7_DOCTRINAL_ATTRIBUTION`
- `EV8_TEMPORAL_ANCHORING`

Errores metodológicos explícitos:

`FALSE_SPECIFICITY`, `DEPENDENCY_INFLATION`, `NARRATIVE_LEAKAGE`, `DOCTRINAL_OVERREACH`, `TEMPORAL_CREATION`, `LABEL_LEAKAGE`, `CASE_FITTING`, `PRIVACY_BREACH`.

`CASE_FITTING` invalida el estatus confirmatorio de la ejecución.

La validación externa evalúa generalización, reproducibilidad y especificidad metodológica. No se presenta como demostración experimental de una ontología metafísica.

Referencia: `docs/EXTERNAL_VALIDATION_PROTOCOL.md`.


## 43. Cláusula contractual C4–C8

Desde ALMAS 1.10.0, toda cláusula contractual debe separar explícitamente:

`CONTENIDO_RECONSTRUIDO → MECANISMO_DE_ACTIVACION → PRUEBA_CONTRACTUAL → INTEGRACION → CUMPLIMIENTO`.

Campos normativos:

- `resolution_level` — R0–R4;
- `reconstructed_contract_content`;
- `activation_mechanism`;
- `contract_test`;
- `integration_requirement`;
- `fulfillment_signature`;
- `claim_refs`;
- `allowed_conclusion`;
- `inferential_ceiling`.

Reglas:

1. El contenido reconstruido es siempre una formulación hermenéutica, no una transcripción literal pre-natal.
2. El mecanismo debe remontarse a tarea previa + activador + raíces; un evento posterior no puede crear la cláusula.
3. La prueba contractual se define antes de evaluar hechos de integración.
4. Las frases del informe se subordinan a Claim Contract v2.
5. Por defecto, una cláusula astrológicamente reconstruida no supera `R2_RELATIONAL_PREINCARNATIONAL_FUNCTION`.
6. R3 exige discriminador independiente validado.
7. R4 no alcanza `SUPPORTED` desde astrología.

Schema: `schemas/clause-assembly.schema.json` v1.1.0.  
Reconstrucción: `schemas/preincarnation-reconstruction.schema.json` v1.9.0.
