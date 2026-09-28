# Máquina de estados de promoción de discriminadores · Paso 16

## Finalidad

El Paso 16 convierte el ciclo de promoción metodológica de ALMAS en una máquina de estados ejecutable.

La política canónica es:

`ALMAS_PROMOTION_STATE_MACHINE_V1`.

Su naturaleza epistemológica es:

`E_PROJECT_POLICY`.

La máquina no prueba que una ontología metafísica sea verdadera. Regula cuándo un discriminador puede avanzar metodológicamente y qué evidencia debe existir antes de hacerlo.

## Línea principal

La única secuencia ascendente permitida es:

`EXPLORATORY → REPRODUCIBLE → REPLICATION_READY → CONFIRMATORY_ELIGIBLE → VALIDATED_DISCRIMINATOR`.

No se permiten saltos.

Por tanto:

`EXPLORATORY → REPLICATION_READY`

es inválido aunque el registro contenga documentos suficientes para estados posteriores.

La evidencia debe incorporarse y auditarse etapa por etapa.

## Estados especiales

### BLOCKED

Puede alcanzarse desde cualquier estado activo anterior a L3.

Al bloquearse se conserva:

`last_active_status`.

Un desbloqueo sólo puede regresar exactamente a ese estado y debe aportar:

`block_resolution_refs`.

Los registros OD05 y OD06, que ya estaban bloqueados antes del Paso 16, se migran conservadoramente con:

`last_active_status = EXPLORATORY`.

Esto no afirma que hubiesen alcanzado previamente un grado superior; únicamente define el nivel mínimo al que podrían volver si el bloqueo fuese resuelto.

### RETIRED

Es terminal.

Un discriminador retirado no puede reactivarse mediante una transición ordinaria.

Si en el futuro fuera necesario reutilizar una idea retirada, debe crearse una nueva versión/identidad de discriminador con nueva genealogía metodológica.

## Rollback

Se permite rollback de un único nivel:

`REPRODUCIBLE → EXPLORATORY`

`REPLICATION_READY → REPRODUCIBLE`

`CONFIRMATORY_ELIGIBLE → REPLICATION_READY`.

No se permite:

`VALIDATED_DISCRIMINATOR → CONFIRMATORY_ELIGIBLE`.

Si un L3 pierde validez, su destino es:

`RETIRED`.

Esto evita que una validación histórica quede silenciosamente degradada mientras conserva trazas de autoridad L3.

## Evidencia acumulativa

Cada registro incorpora:

`promotion_evidence`.

### REPRODUCIBLE

Exige:

- `implementation_refs`;
- `reproducibility_refs`;
- `synthetic_test_refs`.

### REPLICATION_READY

Conserva todo lo anterior y añade:

- `preregistration_refs`;
- `counterevidence_refs`;
- `negative_control_plan_refs`;
- `leakage_plan_refs`.

### CONFIRMATORY_ELIGIBLE

Conserva todo lo anterior y añade:

- `independent_replication_refs`;
- `negative_control_result_refs`;
- `doctrine_gate_refs`;
- `discriminator_evaluation_refs`;
- `holdout_protocol_refs`;
- `support_only_exclusion_refs`.

Los requisitos son acumulativos. Un estado superior no sustituye los requisitos de estados previos.

## Gate VALIDATED_DISCRIMINATOR

El último salto no se satisface sólo con `promotion_evidence`.

La máquina reutiliza todos los gates canónicos ya implantados:

- snapshot congelado;
- `promotion_ref`;
- `promoted_at`;
- `validated_pairs`;
- evidencia de validación;
- `ALMAS_DISCRIMINANT_VALIDATION_V1`;
- `ALMAS_BLINDING_LEAKAGE_V1`;
- independencia astrológica cuando `uses_astrology=true`.

Así, el Paso 16 no crea una segunda definición de L3.

Usa la definición única ya empleada por M21 y M25.

## Transiciones auditables

Cada transición requiere:

- `transition_id` único;
- estado origen;
- estado destino;
- modo;
- fecha;
- actor/referencia responsable;
- motivo;
- referencias de evidencia;
- cambios permitidos en el registro.

La máquina rechaza cambios de identidad como:

- `discriminator_id`;
- `root_key_prefix`;
- `uses_astrology`.

Una transición puede actualizar únicamente evidencia y campos de promoción autorizados.

## state_history

Cada registro contiene:

`state_history`.

Las nuevas transiciones añaden:

- `record_fingerprint_before`;
- `record_fingerprint_after`.

Los fingerprints se calculan con JSON canónico y SHA-256 sobre el estado del registro, excluyendo el propio historial para evitar circularidad.

Un `transition_id` nunca puede reutilizarse.

## Migración de los estados existentes

El Paso 16 no promueve ningún candidato.

Los estados importados siguen siendo:

- OD01: `EXPLORATORY`;
- OD02: `EXPLORATORY`;
- OD03: `EXPLORATORY`;
- OD04: `EXPLORATORY`;
- OD05: `BLOCKED`;
- OD06: `BLOCKED`;
- OD07: `RETIRED`.

`validated_discriminator_ids` continúa vacío.

Las entradas iniciales de `state_history` usan modo `IMPORT` para dejar constancia de que esos estados preexistían a la máquina de estados.

## Invariantes

1. No se permiten saltos hacia delante.
2. Los requisitos de etapa son acumulativos.
3. Un estado no-L3 no puede mantener `l3_authorized=true`.
4. L3 reutiliza exactamente los gates de validación ya existentes.
5. Un L3 invalidado se retira; no se degrada silenciosamente.
6. RETIRED es terminal.
7. BLOCKED sólo vuelve al último estado activo documentado.
8. Cada transición deja una huella SHA-256.
9. La identidad del discriminador no puede mutar mediante una transición.
10. La máquina de estados valida promoción metodológica, no verdad metafísica.

## Siguiente paso

El Paso 17 actualizará el reporting para exponer de forma explícita:

- estado actual de promoción;
- requisitos satisfechos;
- requisitos pendientes;
- historial de promoción;
- razón de bloqueo/retiro;
- alcance L3 cuando exista;

sin convertir el estado metodológico en una conclusión ontológica.
