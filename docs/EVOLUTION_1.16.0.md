# ALMAS 1.16.0 · Validation Operations

## Objetivo

ALMAS 1.15.0 cerró S1–S9 y dejó correctamente sin ejecutar la parte que exige
datos externos reales: candidatos congelados, cohortes holdout, replicación y
promoción fuera de muestra.

1.16.0 no debe inventar esos datos. Su objetivo es operacionalizar el proceso
para que una validación real pueda abrirse, congelarse, auditarse y cerrarse
sin que los resultados observados entren antes de tiempo en la metodología.

## V1 · Validation Preregistration Bundle

V1 introduce
`ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1`.

El paquete se construye únicamente a partir de un candidato PX v3 ya
`FROZEN_FOR_VALIDATION` y un plan de cohorte todavía no abierto.

Congela:

- versión ALMAS y commit SHA;
- candidate_id, formula_ref, descriptores y dirección esperada;
- null model externo;
- feature/orb policy refs;
- reglas de inclusión y emparejamiento;
- tamaño mínimo planificado;
- plan de cegamiento;
- plan de auditoría de leakage;
- replicaciones independientes previstas;
- controles negativos;
- ablaciones;
- endpoints;
- criterios explícitos de éxito y fallo.

El bundle rechaza datos que pertenezcan al holdout observado: muestras,
snapshots, candidate scores, distribuciones observadas, labels y outcomes.

También rechaza solapamiento entre `development_case_refs` y
`planned_holdout_refs`.

La salida recibe un SHA-256 determinista sobre el contenido congelado.

V1 no:

- abre el holdout;
- evalúa resultados;
- modifica el registro PX v3;
- habilita scoring o weighting;
- valida L3;
- convierte rendimiento en probabilidad metafísica.

## Estado de la fase

La infraestructura puede quedar lista aunque el registro canónico PX v3 siga
vacío. En ese estado, una ejecución real de V1 sobre el registro empaquetado
debe permanecer `NOT_EVALUABLE`: no se crea un candidato artificial para
hacer pasar el protocolo.

## V2 · HOLDOUT_OPEN Gate

V2 queda implementada mediante `ALMAS_HOLDOUT_OPEN_GATE_V1`.

Antes de permitir cualquier evaluación, el gate verifica:

- fingerprint SHA-256 exacto del bundle V1;
- versión runtime = versión congelada;
- commit runtime = commit congelado;
- candidate_id y formula_ref idénticos;
- cohort_id, null model, feature/orb policy y reglas de inclusión/emparejamiento
  idénticos al preregistro;
- tamaño de cohorte >= mínimo preregistrado;
- ausencia de resultados, scores, labels, outcomes o snapshots observados.

Si alguna condición falla, la salida es `BLOCKED_HOLDOUT_OPEN`.

Una apertura válida genera un `opening_record` y un SHA-256 determinista.
Ese registro fija:

`holdout_opened=true`

`holdout_evaluation_permitted=true`

pero mantiene:

`holdout_evaluated=false`

`promotion_permitted=false`

`scoring_activation=false`

`weighting_activation=false`

`ontology_activation=false`

`l3_validation=false`.

Por tanto V2 autoriza comenzar la evaluación congelada, no interpreta ningún
resultado ni cambia el modelo de producción.

## V3 · Append-only Validation Ledger

V3 queda implementada mediante
`ALMAS_VALIDATION_EXECUTION_LEDGER_V1`.

El ledger registra una cadena estrictamente ordenada:

1. `PREREGISTERED`;
2. `HOLDOUT_OPENED`;
3. `HOLDOUT_EVALUATED`;
4. `DOCUMENTARY_REVEALED`;
5. `VALIDATION_CLOSED`.

Cada entrada contiene únicamente:

- número de secuencia;
- tipo de evento;
- referencia opaca al artefacto;
- SHA-256 del artefacto;
- SHA-256 de la entrada anterior;
- SHA-256 propio.

La cadena es append-only. Cualquier modificación retroactiva de una entrada,
del enlace previo, del contador, del evento actual o del chain head invalida el
ledger.

El ledger no almacena datos privados, snapshots, scores ni resultados del
holdout. Sólo conserva referencias y fingerprints de artefactos externos.

V3 tampoco decide promoción ni activa scoring, weighting, ontología o L3.

## V4 · Validation Continuity Gate

V4 queda implementada mediante
`ALMAS_VALIDATION_CONTINUITY_GATE_V1`.

La finalidad es impedir que una evaluación S7 llegue al gate S8 si no puede
demostrarse que pertenece exactamente al mismo ciclo congelado V1/V2/V3.

V4 verifica:

- SHA-256 del bundle V1;
- SHA-256 del opening record V2;
- enlace V2→V1 mediante `preregistration_sha256`;
- continuidad de `validation_id`;
- continuidad de `candidate_id` y `formula_ref`;
- versión y commit runtime iguales a los congelados;
- identidad de cohorte, null model y políticas de features/orbes;
- fingerprint de distribución S7 válido;
- número de muestras limpias compatible con la cohorte abierta;
- ausencia de flags ilegales de activación/promoción en S7;
- integridad completa del ledger V3;
- presencia ordenada de PREREGISTERED → HOLDOUT_OPENED → HOLDOUT_EVALUATED;
- coincidencia exacta entre los tres hashes de artefactos y las tres primeras
  entradas del ledger.

Cuando todo coincide, V4 genera un
`Validation Continuity Certificate` y su fingerprint SHA-256.

El certificado contiene exclusivamente metadatos, referencias y fingerprints.
No contiene muestras, scores individuales, cartas, narrativas ni datos
privados.

La ruta normativa 1.16 hacia S8 es
`evaluate_px_v3_promotion_with_continuity`. Esta ruta rechaza cualquier
evidencia de promoción que no incluya un certificado V4 válido o cuyo
fingerprint holdout no sea el mismo que S8 pretende evaluar.

Superar V4 sólo permite **presentar** la evidencia al gate S8. No equivale a
`PROMOTION_ELIGIBLE`, no activa PX v3 y mantiene:

- `automatic_registry_mutation=false`;
- `scoring_activation=false`;
- `weighting_activation=false`;
- `ontology_activation=false`;
- `l3_validation=false`;
- `metaphysical_probability=false`.

## Próximas fases

V5 formalizará el cierre confirmatorio, el revelado documental y el paquete
de auditoría de release sin activar automáticamente PX v3.
