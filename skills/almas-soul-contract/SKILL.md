---
name: almas-preincarnation-contract-module
description: Specialized internal ALMAS module for reconstructing possible preincarnational agreements from canonical astrological architecture, doctrine, chronology, counterevidence and documented facts.
version: 1.9.1
author: Proyecto ALMAS
metadata:
  public_release: true
  kind: internal_module
  parent_skill: almas-twin-flame-astrology
  independent_versioning: false
  engine_revision: 1.9.0
  paradigm: metaphysical_research
  depends_on:
    - almas-metaphysical-relationship-astrology
  tags: [soul-contract, preincarnation, metaphysics, astrology, hermeneutics, karma, dharma, relationships]
---

# ALMAS · Módulo de Contrato Preencarnatorio

## 0. Paradigma

Este módulo trabaja explícitamente dentro del marco metafísico ALMAS.

La astrología se utiliza como **método metafísico de averiguación**. El motor contractual no parte de una objeción externa a la metafísica, sino de una pregunta interna: dado un conjunto de evidencias astrológicas, doctrinales, temporales y documentales, ¿qué arquitectura preencarnatoria explica mejor el vínculo?

Los controles metodológicos sirven para evitar sobreconteo, dependencia, ajuste retrospectivo al caso y saltos ontológicos apoyados en evidencia aislada. No constituyen una negación del paradigma metafísico.

## 0.1. Estatus arquitectónico

Este archivo se conserva en `skills/almas-soul-contract/SKILL.md` por compatibilidad histórica y como punto de entrada especializado.

**No constituye una segunda skill pública.** Hereda la versión raíz de ALMAS y su lógica forma parte de la arquitectura modular definida en `docs/MODULE_ARCHITECTURE.md`.

La revisión histórica del motor contractual `1.9.0` se conserva como `engine_revision`, no como SemVer público independiente.

## 1. Función del módulo

Reconstruir, cuando la evidencia lo permita, un posible **contrato, pacto o acuerdo preencarnatorio** entre dos almas.

La salida no es una quinta categoría junto a AF, KA, AG o LG. El contrato es una arquitectura transversal que puede coexistir con distintos modelos relacionales.

Preguntas nucleares:

- ¿qué finalidad metafísica parece organizar el encuentro?;
- ¿qué activa A en B?;
- ¿qué activa B en A?;
- ¿qué surge únicamente en el campo común?;
- ¿qué aprendizaje, reparación, confrontación, integración o servicio articula el vínculo?;
- ¿qué elementos son compatibles con continuidad kármica, dhármica o de vidas anteriores?;
- ¿qué condiciones indicarían desarrollo, integración, transformación o cierre de una cláusula?;
- ¿qué alternativas explicativas compiten con la lectura contractual?

## 2. Entrada principal

La entrada preferente es `astrology_to_soul_contract.json`, generado por el motor astrológico de la misma skill ALMAS y conforme a:

`schemas/astrology-to-soul-contract.schema.json`

El motor contractual debe consumir, no recalcular silenciosamente:

- raíces estructurales independientes;
- dirección A→B, B→A o campo común;
- familias técnicas;
- fuerza y recurrencia;
- pilares asociados;
- ontología relacional;
- temporalidad anclada;
- robustez;
- cobertura;
- contraevidencia;
- referencias canónicas a la evidencia astrológica.

Puede añadir además:

- doctrina primaria o histórica;
- estudios académicos;
- uso contemporáneo documentado;
- cronología de hechos;
- eventos públicos o privados autorizados;
- otras técnicas metafísicas incorporadas mediante módulos definidos y trazables.

## 3. Separación epistemológica

Mantener siempre:

- `A_CALCULATED`: dato calculado o documental.
- `B_TECHNIQUE`: técnica empleada.
- `C_DOCTRINE`: doctrina explícita de una fuente.
- `D_CONTEMPORARY_USAGE`: uso contemporáneo.
- `E_PROJECT_HYPOTHESIS`: inferencia ALMAS.

Una hipótesis contractual específica puede ser plenamente metafísica y, a la vez, seguir marcada como `E_PROJECT_HYPOTHESIS`. Esa etiqueta identifica procedencia, no debilita el paradigma.

## 4. Estados

Usar:

- `SUPPORTED`
- `COMPATIBLE`
- `INSUFFICIENT`
- `CONTRADICTED`
- `NOT_EVALUABLE`

Los estados no son probabilidades metafísicas.

## 5. Direccionalidad

Separar obligatoriamente:

- `A_EN_B`: función de A sobre la arquitectura de B;
- `B_EN_A`: función de B sobre la arquitectura de A;
- `CAMPO_COMUN`: función emergente de la relación como unidad.

Reciprocidad:

- `BILATERAL`
- `PARCIAL`
- `ASIMETRICA`
- `NO_EVALUABLE`

Bilateral no significa simétrico.

## 6. Ocho cláusulas base

La taxonomía inicial utiliza ocho familias funcionales:

1. **Encuentro y reconocimiento**.
2. **Vínculo amoroso**.
3. **Herida y reparación**.
4. **Libertad y autonomía**.
5. **Comunicación y verdad**.
6. **Transformación y poder**.
7. **Integración y encarnación**.
8. **Liberación y cierre**.

Cada cláusula debe registrar:

- raíces estructurales;
- dirección;
- técnicas;
- dependencia;
- significado metafísico;
- acción simbólica;
- aprendizaje;
- sombra;
- requisito de integración;
- firma de cumplimiento;
- temporalidad;
- contraevidencia;
- alternativas;
- robustez.

Una cláusula nueva sólo puede añadirse después de definir procedencia, discriminadores, evidencia necesaria, contraevidencia y tests.

## 7. Roles preencarnatorios

Los roles son funcionales por cláusula, no identidades esenciales.

Roles iniciales:

- ACTIVADOR
- CATALIZADOR
- ESPEJO
- MEMORIA
- ESTRUCTURADOR
- LIBERADOR
- CONFRONTADOR
- PORTADOR_DE_VULNERABILIDAD
- INTEGRADOR
- MEDIADOR
- TESTIGO
- COMPANERO_DE_APRENDIZAJE

Cadena mínima:

`ARQUITECTURA_RECEPTORA → FACTOR_DEL_OTRO → RAIZ_ACTIVADA → FUNCION_METAFISICA → CLAUSULA`

Intensidad:

- `PRIMARIO`
- `SECUNDARIO`
- `CORROBORATIVO`
- `INSUFICIENTE`
- `NO_EVALUABLE`

## 8.1. Causa contractual

La **causa contractual** pregunta por qué una persona encaja metafísicamente como activador de una tarea que la otra ya trae antes del encuentro.

Cadena mínima:

`TAREA_PREVIA_RECEPTOR → FACTOR_ACTIVADOR_DEL_OTRO → ENCAJE_GEOMETRICO → RECURRENCIA → FUNCION_CONTRACTUAL → CAMPO_COMUN`

La tarea previa se identifica primero desde la arquitectura individual del receptor. Después se evalúa el encaje del otro. Este orden evita construir retrospectivamente la tarea sólo porque existe un aspecto sinástrico.

Tipos iniciales:

- CAUSA_DE_RECONOCIMIENTO
- CAUSA_DE_CATALISIS
- CAUSA_DE_CONFRONTACION
- CAUSA_DE_ENCARNACION
- CAUSA_DE_RECIPROCIDAD
- CAUSA_DE_VERDAD
- CAUSA_DE_INTEGRACION
- CAUSA_DE_LIBERACION

Referencia normativa: `reference/causa-contractual.md`.

## 8. Preexistencia y origen

El contrato puede investigar, sin forzar equivalencias doctrinales:

- origen independiente;
- familia o grupo de almas;
- origen compartido;
- continuidad kármica;
- continuidad dhármica;
- vínculo de vidas anteriores;
- modelos monádicos;
- split-soul;
- twin-soul / twin-flame / twin-ray;
- maestro/alumno;
- sacred partner / hieros gamos;
- misión o servicio compartido.

Cuando dos modelos produzcan la misma firma observable y no exista discriminador validado, usar una categoría no resuelta o `INSUFFICIENT`.

## 9. Historia preencarnatoria hipotética

La reconstrucción puede organizarse en:

`ORIGEN → ACUERDO → DESCENSO/ENCARNACION → ENCUENTRO → ACTIVACION → DESARROLLO → INTEGRACION/TRANSFORMACION/CIERRE`

No todas las fases deben estar presentes ni en ese orden.

Cada tramo debe enlazar con evidencia y fuente doctrinal cuando exista.

## 10. Temporalidad contractual

Distinguir:

### Tiempo 1 · Activación inicial
Qué raíces preexistentes pone en movimiento el encuentro.

### Tiempo 2 · Desarrollo
Qué cláusulas reaparecen mediante activaciones o hechos independientes.

### Tiempo 3 · Integración, transformación o cierre
Qué indicios muestran que la función cambia de modalidad, se integra o deja de organizar el vínculo.

Estados temporales:

- `LATENTE`
- `ACTIVADA`
- `EN_DESARROLLO`
- `INTEGRADA`
- `TRANSFORMADA`
- `CERRADA`
- `NO_EVALUABLE`

La temporalidad debe permanecer anclada a raíces estructurales.

## 11. Gramática contractual

Formato recomendado:

`ACTOR_O_CAMPO → FUNCION → OBJETIVO_ALMICO → SOMBRA → REQUISITO_DE_INTEGRACION → FIRMA_DE_CUMPLIMIENTO`

Ejemplo sintético:

`A_EN_B → activar autonomía → hacer visible la tensión vínculo/libertad → huida o control → sostener cercanía sin apropiación → la relación deja de necesitar crisis para preservar individualidad`.

## 12. Doctrina comparada

Investigar sin equiparar automáticamente:

- Platonismo/Neoplatonismo;
- Cábala;
- misticismo cristiano;
- sufismo;
- hinduismo, Vedanta y Tantra;
- budismo cuando proceda;
- espiritismo;
- Teosofía;
- Alice Bailey;
- I AM Activity;
- Summit Lighthouse;
- New Age;
- estudios académicos del esoterismo.

Para cada fuente indicar qué sostiene, qué no sostiene y cómo se relaciona con la hipótesis ALMAS.

## 13. Controles metodológicos internos

1. Una evidencia aislada no crea una cláusula ontológica.
2. Técnicas dependientes no cuentan como confirmaciones independientes.
3. La temporalidad activa arquitectura; no sustituye estructura.
4. La rareza estadística no se convierte en probabilidad metafísica.
5. No ajustar pesos, cláusulas o umbrales para obtener el resultado deseado en un caso.
6. Buscar contraevidencia activamente.
7. Diferenciar ausencia evaluada de `NOT_EVALUABLE`.
8. Una función metafísica no implica obligación conductual de otra persona.
9. Viabilidad y reciprocidad observables se registran como hechos del plano encarnado y no se sustituyen por inferencia simbólica.

## 14. Salida canónica

La salida recomendada es:

`canonical_soul_contract.json`

conforme a `schemas/contrato-almico.schema.json`.

El relato final se genera después de cerrar:

`evidencia → raíces → cláusulas → roles → temporalidad → doctrina → contraevidencia → síntesis`

Nunca al revés.

## 15. Publicación

GitHub publica reglas generalizadas, fuentes públicas, tests sintéticos y casos reales únicamente cuando los datos subyacentes ya son públicos y verificables.

El material privado no se convierte en público por haber sido usado en investigación interna.


## 16. Reconstrucción preencarnatoria en ocho etapas

En modo FULL, Soul Contract debe intentar reconstruir la secuencia:

`ORIGEN → MOTIVO_DEL_ACUERDO → SELECCION_DE_ROLES → CONDICIONES_DE_ENCUENTRO → TAREAS_INDIVIDUALES → TAREA_COMUN → CLAUSULAS → MECANISMOS_DE_CUMPLIMIENTO`

Cada etapa conserva estado epistemológico, hipótesis competidoras, raíces astrológicas, fuentes doctrinales, alternativas, contraevidencia, dependencias y robustez.

La reconstrucción no presupone que todas las tradiciones describan literalmente estas ocho fases. Es una ontología operativa ALMAS que compara doctrinas y métodos sin fusionarlos.

Reglas centrales:

1. El origen se evalúa antes de usar las cláusulas como confirmación.
2. El motivo del acuerdo debe enlazar con tareas previas o funciones identificables.
3. Los roles se calculan por A_EN_B, B_EN_A y CAMPO_COMUN.
4. Las condiciones de encuentro requieren raíces estructurales más activación; la sincronía aislada no basta.
5. TAREA_A_PREVIA y TAREA_B_PREVIA se identifican desde las cartas individuales antes de mirar la activación del otro.
6. La TAREA_COMUN pertenece al campo relacional y no es la suma de A+B.
7. Cada cláusula debe poder rastrearse hacia atrás hasta motivo, roles, tareas y raíces.
8. Los mecanismos de cumplimiento son vías funcionales, no desenlaces obligatorios.

Mecanismos admitidos inicialmente:

- ACTIVACION
- REPETICION
- RECIPROCIDAD
- CATALISIS
- ENCARNACION
- TIKKUN_REPARACION
- SERVICIO
- LIBERACION
- TRANSFORMACION_DE_MODALIDAD
- CIERRE
- RUTA_ALTERNATIVA
- APLAZAMIENTO

En modo FULL, la salida `canonical_soul_contract.json` debe incluir `reconstruccion_preencarnatoria`. Si una etapa no puede resolverse, se conserva como `INSUFFICIENT` o `NOT_EVALUABLE`; no se rellena narrativamente.

Referencia normativa: `reference/preincarnation-reconstruction.md`.
Esquema: `schemas/preincarnation-reconstruction.schema.json`.
Mapa de fuentes: `reference/preincarnation-source-map.json`.
Invariantes: `tests/PREINCARNATION_RECONSTRUCTION_INVARIANTS.md`.


## 17. Motor diferencial del origen

La etapa ORIGEN debe ejecutarse mediante el motor definido en:

- `reference/origin-differential.md`
- `manifests/origin-model-registry.json`
- `schemas/origin-differential.schema.json`
- `tests/ORIGIN_DIFFERENTIAL_INVARIANTS.md`

Modelos iniciales:

- INDEPENDENT_SOULS
- SOUL_FAMILY_GROUP
- RELATED_SOUL_ROOTS
- ZIVUG_TRUE_PAIR
- SHARED_ORIGIN_UNDIFFERENTIATED
- MONADIC_COMMON_SOURCE
- SPLIT_SOUL
- TWIN_SOUL
- TWIN_FLAME_MODEL

La salida FULL de reconstrucción preencarnatoria debe incluir `origin_differential`.

Regla de techo:

Un subtipo de origen no puede alcanzar `SUPPORTED` sin un discriminador astrológico `VALIDATED` que lo separe de sus rivales principales.

Cuando varias ontologías sigan explicando la misma firma observable, usar:

`SHARED_ORIGIN_UNDIFFERENTIATED + INSUFFICIENT`

y enumerar los modelos compatibles y los discriminadores faltantes.

La finalidad del motor es discriminar mejor, no forzar una identidad ontológica.


## 18. Motor diferencial del motivo del acuerdo

La etapa MOTIVO_DEL_ACUERDO debe ejecutarse mediante:

- reference/agreement-motive-differential.md
- manifests/agreement-motive-registry.json
- schemas/agreement-motive-differential.schema.json
- tests/AGREEMENT_MOTIVE_INVARIANTS.md

La salida FULL debe incluir agreement_motive_differential.

La evaluación distingue:
1. motivo funcional;
2. dirección/alcance;
3. mecanismo preencarnatorio.

No se permite inferir que un acuerdo fue elegido, solicitado, mutuamente pactado o providencialmente asignado sólo porque el motivo funcional sea fuerte.

Un motivo puede ser PRIMARY, SECONDARY o CORROBORATIVE.

Mecanismos M3 como ACORDADA_MUTUAMENTE o PROVIDENCIALMENTE_ASIGNADA requieren fuente doctrinal o método identificado y no se universalizan entre tradiciones.


## 19. Motor diferencial de selección de roles

La etapa SELECCION_DE_ROLES debe ejecutarse mediante:

- reference/role-selection-differential.md
- manifests/role-selection-registry.json
- schemas/role-selection-differential.schema.json
- tests/ROLE_SELECTION_INVARIANTS.md

La salida FULL debe incluir role_selection_differential.

El motor separa:
- rol funcional;
- dirección;
- intensidad;
- mecanismo preencarnatorio;
- posible cambio de fase.

Un rol funcional fuerte no eleva automáticamente a SUPPORTED el mecanismo por el que ese rol fue asumido antes de encarnar.

RSD5_REQUESTED_VS_MUTUAL, RSD6_KARMIC_VS_VOLUNTARY y RSD8_UNIQUE_ROLE permanecen NOT_VALIDATED.


## 20. Motor diferencial de condiciones de encuentro

La etapa CONDICIONES_DE_ENCUENTRO debe ejecutarse mediante:

- reference/encounter-conditions-differential.md
- manifests/encounter-conditions-registry.json
- schemas/encounter-conditions-differential.schema.json
- tests/ENCOUNTER_CONDITIONS_INVARIANTS.md

La salida FULL debe incluir encounter_conditions_differential.

Una condición sólo es contractual cuando enlaza una raíz estructural previa con una activación y un contexto trazables.

Una coincidencia temporal, geográfica o subjetiva sin anclaje estructural no crea condición de encuentro.

ECD4_REQUIRED_CONTEXT_VS_INCIDENTAL, ECD6_UNIQUE_EVENT_VS_ALTERNATIVE_PATH, ECD7_GEOGRAPHIC_NECESSITY y ECD8_FREE_WILL_BRANCH permanecen NOT_VALIDATED.


## 21. Motor diferencial de tareas individuales

La etapa TAREAS_INDIVIDUALES debe ejecutarse mediante:

- reference/individual-tasks-differential.md
- manifests/individual-tasks-registry.json
- schemas/individual-tasks-differential.schema.json
- tests/INDIVIDUAL_TASKS_INVARIANTS.md

La salida FULL debe incluir individual_tasks_differential.

Las tareas de A y B se fijan antes de introducir la carta del otro. ITF8_INDEPENDENCIA_DEL_OTRO es obligatoria para considerar una tarea como previa.

La activación sinástrica puede explicar cómo se moviliza una tarea, pero no puede fabricarla retrospectivamente.


## 22. Motor diferencial de tarea común

La etapa TAREA_COMUN debe ejecutarse mediante:

- reference/common-task-differential.md
- manifests/common-task-registry.json
- schemas/common-task-differential.schema.json
- tests/COMMON_TASK_INVARIANTS.md

La salida FULL debe incluir common_task_differential.

La tarea común sólo existe cuando supera CTD1_SUM_VS_EMERGENCE: debe aparecer una función del campo relacional que no quede explicada por la suma de TAREA_A_PREVIA y TAREA_B_PREVIA.

Compuesta y Davison forman una única familia RELCHART a efectos de independencia.


## 23. Motor de ensamblaje de cláusulas

La etapa CLAUSULAS debe ejecutarse mediante:

- reference/clause-assembly.md
- manifests/clause-registry.json
- schemas/clause-assembly.schema.json
- tests/CLAUSE_ASSEMBLY_INVARIANTS.md

La salida FULL debe incluir clause_assembly.

Las ocho cláusulas son objetos derivados. Cada una debe conservar genealogía vertical hacia motivo, roles, tareas y raíces. Una cláusula sin genealogía suficiente queda INSUFFICIENT.

El motor controla solapamiento para evitar que una misma raíz se multiplique artificialmente bajo varios nombres de cláusula.

## 24. Motor de mecanismos de cumplimiento

La etapa MECANISMOS_DE_CUMPLIMIENTO debe ejecutarse mediante:

- reference/fulfillment-mechanisms.md
- manifests/fulfillment-mechanisms-registry.json
- schemas/fulfillment-mechanisms.schema.json
- tests/FULFILLMENT_MECHANISMS_INVARIANTS.md

La salida FULL debe incluir fulfillment_mechanisms_differential.

Regla principal:

ACTIVACION ≠ CUMPLIMIENTO

INTEGRADA, TRANSFORMADA y CERRADA requieren hechos documentados posteriores a la activación y comparación con una firma de cumplimiento preregistrada.

FM_RUTA_ALTERNATIVA y FM_APLAZAMIENTO son hipótesis condicionadas por las fuentes que admiten contingencia o choice points; no implican predicción de reencuentro, obligación de continuidad ni futura encarnación.

Con estos dos motores, la reconstrucción FULL queda cerrada en ocho etapas diferenciales:
ORIGEN → MOTIVO → ROLES → CONDICIONES → TAREAS_INDIVIDUALES → TAREA_COMUN → CLAUSULAS → CUMPLIMIENTO.


## 26. Cadena causal contractual v2

Además de las ocho etapas diferenciales históricas, una ejecución FULL debe ensamblar la cadena causal:

`TAREA_PREVIA → MOTIVO_DE_ELECCION_DEL_OTRO → ROL_ASUMIDO → CLAUSULA_DE_ACTIVACION → PRUEBA_PACTADA → INTEGRACION_ESPERADA → CONDICION_DE_CUMPLIMIENTO → CIERRE_O_ALTERNATIVA`.

La cadena reutiliza los motores existentes; no vuelve a contar evidencia.

`ORIGIN` permanece como contexto ontológico independiente.

La salida debe ajustarse a `schemas/preincarnation-contract-chain.schema.json`.

El contenido literal de supuestas promesas, frases, fechas o desenlaces pre-natales permanece `NOT_EVALUABLE` desde astrología.


## 25. Validación externa del módulo contractual

Las cláusulas, causas, roles y modelos de origen derivados durante desarrollo no se consideran externamente validados hasta superar un holdout preregistrado.

Reglas:

1. un caso usado para construir una cláusula es `DEVELOPMENT_ONLY` para esa cláusula;
2. un IAP alto no constituye ground truth;
3. una autoetiqueta twin-flame/soulmate no valida el modelo;
4. AB0–AB8 se ejecuta en holdout sin reajustar criterios;
5. discriminadores `NOT_VALIDATED` no pueden elevar una ontología fuerte a `SUPPORTED`;
6. toda promoción de regla exige replicación independiente.

Referencia: `docs/EXTERNAL_VALIDATION_PROTOCOL.md`.
