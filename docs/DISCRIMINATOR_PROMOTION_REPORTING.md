# Reporting del ciclo de promoción de discriminadores · Paso 17

## Finalidad

El Paso 17 hace visible en los informes el estado metodológico del sistema de discriminación ontológica sin convertir ese estado en una conclusión sobre el caso estudiado.

La capa se denomina:

`promotion_reporting`.

Su naturaleza epistemológica es:

`METHODOLOGICAL_STATUS_ONLY`.

No es una nueva fuente de evidencia ontológica.

## Fuente

El snapshot se deriva exclusivamente de:

- `src/almas_tfa/data/discriminator-promotion-registry.json`;
- `ALMAS_PROMOTION_STATE_MACHINE_V1`.

No se deriva de autoetiquetas, narrativa del caso, puntuaciones IEM/IDD/IRC ni de la clasificación producida por M21.

## Qué expone

Para cada discriminador se informa:

- identificador;
- estado actual;
- último estado activo cuando está bloqueado;
- razón de bloqueo o retirada cuando exista;
- uso o no de astrología;
- autoridad L3;
- cumplimiento efectivo del gate L3;
- siguiente estado ordinario posible;
- requisitos de la etapa siguiente;
- requisitos cumplidos;
- requisitos pendientes;
- `promotion_ref`;
- fecha de promoción;
- pares realmente validados;
- historial de transiciones;
- condición terminal/bloqueada.

## Requisitos pendientes

El reporting reutiliza la misma política de requisitos acumulativos del Paso 16.

No crea una segunda lista de gates.

Por ejemplo, un discriminador `EXPLORATORY` puede mostrar que para alcanzar `REPRODUCIBLE` aún faltan:

- reproducibilidad;
- tests sintéticos;

mientras ya consta una referencia de implementación.

Mostrar esta situación no equivale a promoverlo.

## Historial

`history` conserva la traza metodológica:

- `transition_id`;
- origen y destino;
- modo;
- fecha;
- actor/referencia;
- razón;
- evidencia asociada;
- fingerprints antes/después cuando existan.

Esta traza permite distinguir entre:

- estado importado;
- promoción;
- rollback;
- bloqueo;
- desbloqueo;
- retirada.

## Firewalls

Cada snapshot fija:

`methodological_status_only=true`

`ontological_inference_allowed=false`

`case_classification_mutated=false`

`irc_mutated=false`.

Cada registro fija además:

`ontological_weight=0`

`can_change_case_classification=false`

`can_raise_irc=false`.

Por tanto, la madurez metodológica de un discriminador nunca se transforma en puntuación metafísica.

## Genealogía documental integrada

Desde el Paso 18, el snapshot incorpora:

`source_genealogy`.

La genealogía resuelve para cada OD su procedencia P1–P6, rol de fuente, tradición, autor/obra, ancla, conceptos, `supports`, `does_not_support`, relaciones genealógicas y equivalencias prohibidas.

Sus firewalls son:

- `methodological_provenance_only=true`;
- `ontological_inference_allowed=false`;
- `source_count_adds_weight=false`;
- `source_priority_adds_ontological_weight=false`;
- `cross_tradition_identity_allowed=false`.

Así, el reporting puede explicar por qué OD06 procede de doctrinas monádicas y al mismo tiempo conservar que Mónada–alma–personalidad no equivale a una díada twin-flame.

## Integración con M31

M31 incorpora el snapshot como:

`report_document_model.promotion_reporting`.

La sección S08 Robustez y validación y la sección S11 Fuentes y anexos quedan declaradas como superficies de reporting metodológico.

Esto no modifica el fingerprint de `canonical_analysis`: el snapshot se añade después de que M30 haya congelado y M31 haya verificado el canonical.

## Distinción respecto de promotion_trace

`ontological_discrimination.promotion_trace` responde a:

“¿Qué discriminadores L3 intervinieron realmente en esta ejecución?”

`promotion_reporting` responde a:

“¿Cuál es el estado metodológico del registro de discriminadores en el momento de producir el informe?”

Son objetos diferentes.

Si no existe ningún L3, `promotion_trace` puede estar vacío mientras `promotion_reporting` sigue describiendo candidatos exploratorios, bloqueados o retirados.

## Estado productivo actual

El Paso 17 no cambia estados.

El snapshot productivo continúa mostrando:

- OD01–OD04: `EXPLORATORY`;
- OD05–OD06: `BLOCKED`;
- OD07: `RETIRED`;
- cero `VALIDATED_DISCRIMINATOR`.

## Regla de interpretación

El informe puede decir:

“OD01 permanece en estado EXPLORATORY y aún no satisface los requisitos de REPRODUCIBLE.”

No puede convertirlo en:

“OD01 confirma un modelo ontológico.”

La primera frase describe metodología.

La segunda requeriría evidencia L3 aplicada al par concreto y todos los gates de M21/M25.

## Siguiente paso

El Paso 19 aislará los casos privados del repositorio público y formalizará qué datos pueden utilizarse en fixtures, holdouts y documentación.
