# Registro canónico de promoción de discriminadores

## Finalidad

ALMAS distingue entre que una señal esté definida, sea reproducible, esté lista para replicación, sea elegible para confirmación y haya alcanzado realmente un estado validado.

El estado `L3_VALIDATED` no puede ser declarado libremente en una entrada de análisis.

La única autoridad ejecutable es:

`src/almas_tfa/data/discriminator-promotion-registry.json`

El archivo se distribuye dentro del paquete y se carga mediante:

`src/almas_tfa/discriminator_promotion_registry.py`

Su schema es:

`schemas/discriminator-promotion-registry.schema.json`.

## Ciclo de promoción

Los estados admitidos son:

`EXPLORATORY → REPRODUCIBLE → REPLICATION_READY → CONFIRMATORY_ELIGIBLE → VALIDATED_DISCRIMINATOR`

y los estados de salida:

`BLOCKED`

`RETIRED`.

No todos los candidatos deben recorrer toda la cadena.

Un candidato puede permanecer bloqueado indefinidamente si no existe observable independiente o si su estructura produce no-identificabilidad.

## Máquina de estados ejecutable

Desde el Paso 16, el ciclo de promoción está regulado por:

`ALMAS_PROMOTION_STATE_MACHINE_V1`.

La implementación canónica es:

`src/almas_tfa/promotion_state_machine.py`

y la política empaquetada:

`src/almas_tfa/data/promotion-state-machine-policy.json`.

Las promociones ascendentes sólo pueden recorrer un nivel:

`EXPLORATORY → REPRODUCIBLE → REPLICATION_READY → CONFIRMATORY_ELIGIBLE → VALIDATED_DISCRIMINATOR`.

No se permiten saltos. Los requisitos de etapa se almacenan en `promotion_evidence` y son acumulativos.

Cada discriminador conserva además `state_history`, con un `transition_id` único y fingerprints SHA-256 antes/después de cada transición aplicada.

`BLOCKED` conserva `last_active_status` y sólo puede volver a ese estado tras documentar `block_resolution_refs`.

`RETIRED` es terminal.

`VALIDATED_DISCRIMINATOR` no puede degradarse mediante rollback. Si pierde validez, debe pasar a `RETIRED` y pierde `l3_authorized`.

La máquina no redefine el gate L3: el último salto reutiliza exactamente la validación discriminante, el cegamiento/leakage, la independencia astrológica cuando proceda y el resto de requisitos ya empleados por M21/M25.

## Requisitos para autoridad L3

Un registro sólo puede autorizar `L3_VALIDATED` cuando cumple simultáneamente:

- `current_status=VALIDATED_DISCRIMINATOR`;
- `l3_authorized=true`;
- `promotion_ref` no nulo;
- fecha `promoted_at`;
- versión ALMAS congelada;
- commit SHA congelado;
- referencia de regla congelada;
- schemas congelados;
- preregistro documentado;
- replicación independiente;
- holdout externo;
- controles negativos;
- auditoría de leakage;
- pares de modelos explícitamente validados;
- familia `root_key_prefix` declarada.

La ausencia de cualquiera de estas piezas invalida la autoridad L3 en tiempo de ejecución.

## Gate cuantitativo de validez discriminante

Todo registro L3 debe incluir `discriminant_validation` y superar `ALMAS_DISCRIMINANT_VALIDATION_V1`.

El runtime recalcula desde conteos:

- sensibilidad;
- especificidad;
- balanced accuracy;
- intervalo Wilson 95 %;
- `FALSE_SPECIFICITY_RATE`;
- límite superior CI95 de falsa especificidad.

Los mínimos canónicos son CI95 sensibilidad ≥ 0.60, CI95 especificidad ≥ 0.90, balanced accuracy ≥ 0.75 y CI95 superior de falsa especificidad ≤ 0.05. Los controles sintéticos/adversariales admiten cero errores de falsa especificidad.

Si el discriminador produce probabilidades, la calibración debe estar preregistrada y aprobada.

Los umbrales pertenecen a `E_PROJECT_POLICY`; no son evidencia doctrinal ni probabilidad metafísica.

## Gate de cegamiento y leakage

Todo registro L3 debe incluir `blinding_audit` y superar `ALMAS_BLINDING_LEAKAGE_V1`.

La promoción exige:

- ejecución estructural previa sin etiquetas, narrativa, resultado esperado ni outcome del holdout;
- separación estricta desarrollo/evaluación;
- fingerprints SHA-256 de entrada y salida;
- revelado documental posterior;
- identidad del fingerprint estructural antes y después del revelado;
- `LABEL_LEAKAGE=0`;
- `NARRATIVE_LEAKAGE=0`;
- `CASE_FITTING=0`;
- cero cambios de regla posteriores a la apertura del holdout.

M21 aplica además un firewall fail-closed a `ontological_discriminator_input`. Un campo narrativo prohibido no se ignora: la ejecución falla explícitamente.

Este gate es acumulativo con `ALMAS_DISCRIMINANT_VALIDATION_V1`. Un buen rendimiento estadístico no compensa contaminación del holdout, y un protocolo ciego no compensa mala discriminación.

## Requisito adicional cuando uses_astrology=true

Todo registro declara explícitamente `uses_astrology`.

Cuando es `true`, `astrology_validation` debe existir y contener referencias no vacías a:

- `non_astrological_criterion_refs`;
- `astrology_ablation_refs`;
- `matched_control_refs`;
- `dependency_audit_refs`;
- `out_of_sample_refs`;
- `astrology_specific_replication_refs`.

También debe fijar en `true`:

- `single_feature_prohibition_acknowledged`;
- `null_rarity_not_ontological`;
- `temporal_activation_not_origin_proof`.

Este gate se aplica tanto en la autorización M21 como en la revalidación de componentes `VALIDATED_DISCRIMINATOR` en M25.

En el registro productivo OD01, OD02 y OD04 declaran `uses_astrology=true`, pero mantienen `astrology_validation=null` y `l3_authorized=false`. Por tanto, no pueden actuar como L3.


## Alcance por pares

La validación no es global por defecto.

Un discriminador puede estar validado, por ejemplo, para:

`SOULMATE_MODEL ↔ TWIN_FLAME_MODEL`

sin estar validado para:

`MONADIC_ORIGIN ↔ SPLIT_SOUL`.

M21 compara el par solicitado con `validated_pairs`. Si queda fuera del alcance registrado, rechaza la observación.

## promotion_ref

Toda observación `L3_VALIDATED` debe aportar:

`promotion_ref`.

Ese valor debe coincidir exactamente con el registro canónico.

Por tanto, una entrada no puede convertir:

`L2_EXPERIMENTAL`

en:

`L3_VALIDATED`

cambiando simplemente una cadena de texto.

## Familia de raíces

Cada promoción declara:

`root_key_prefix`.

Una raíz de ejecución L3 sólo es admisible cuando pertenece a esa familia.

Ejemplo conceptual:

`OD01:...`

no puede hacerse pasar por una raíz validada de:

`OD04:...`.

Esto preserva genealogía del discriminador y evita que una raíz confirmatoria sea reutilizada bajo otra regla.

## Relación con M21

Antes de ejecutar `discriminate_ontology(...)`, el adaptador M21 llama a:

`validate_l3_observations(...)`.

Las observaciones L1 y L2 continúan permitidas sin promoción registral.

Las observaciones L3:

- deben existir en el registro;
- deben estar promovidas;
- deben coincidir con `promotion_ref`;
- deben respetar el par validado;
- deben respetar la familia de raíces.

Si no, M21 falla explícitamente.

## Relación con M25

M25 no se limita a confiar en que M21 produjo una raíz L3.

También exige en el componente `VALIDATED_DISCRIMINATOR`:

- `discriminator_id`;
- `promotion_ref`;
- `root_key`;
- `source_module=M21`;
- `validation_level=L3_VALIDATED`.

Después vuelve a consultar el registro canónico.

Esto crea doble verificación:

`registro → M21 → salida canónica → M25 → registro`.

## Estado actual

El registro productivo contiene actualmente:

`validated_discriminator_ids = []`.

Ningún candidato OD01–OD07 está promovido a L3.

Los estados vigentes son:

- OD01: `EXPLORATORY`;
- OD02: `EXPLORATORY`;
- OD03: `EXPLORATORY`;
- OD04: `EXPLORATORY`;
- OD05: `BLOCKED`;
- OD06: `BLOCKED`;
- OD07: `RETIRED`.

Por tanto, cualquier L3 real enviado hoy a M21 debe ser rechazado.

Los tests positivos de L3 utilizan un registro sintético inyectado mediante mock y nunca modifican el registro productivo.

## Qué valida una promoción

Una promoción a `VALIDATED_DISCRIMINATOR` validaría exclusivamente el alcance metodológico descrito en el registro.

No demostraría:

- que una ontología metafísica existe;
- que una pareja concreta sea una twin flame;
- que la rareza sea probabilidad metafísica;
- que el score estructural equivalga a verdad ontológica.

## Invariantes

1. Una ejecución no puede autopromover un discriminador.
2. Un `promotion_ref` inventado no autoriza L3.
3. Un discriminador promovido para un par no se extiende a otros pares.
4. Una raíz fuera de `root_key_prefix` no hereda la promoción.
5. Un registro incompleto no autoriza L3.
6. L2 nunca requiere promoción registral.
7. M25 no acepta un L3 que el registro no autorice.
8. El registro productivo actual contiene cero L3.
9. Un discriminador con `uses_astrology=true` no autoriza L3 sin `astrology_validation` completa.
10. Ningún feature astrológico aislado, rareza nula o activación temporal sustituye la validación discriminante independiente.
11. Un L3 no autoriza promoción sin `blinding_audit` completa.
12. `LABEL_LEAKAGE`, `NARRATIVE_LEAKAGE`, `CASE_FITTING` o cambios post-holdout bloquean L3.
13. El fingerprint estructural debe permanecer idéntico tras el revelado documental.
14. No se permiten saltos ascendentes de estados.
15. Los requisitos de promoción son acumulativos por etapa.
16. `transition_id` no puede reutilizarse.
17. `BLOCKED` sólo vuelve a `last_active_status`.
18. `RETIRED` es terminal.
19. Un L3 invalidado se retira y no retrocede silenciosamente.
20. La identidad del discriminador no puede mutar mediante una transición.
