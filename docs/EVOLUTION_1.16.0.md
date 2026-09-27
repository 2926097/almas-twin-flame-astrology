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

## Próximas fases

V3 añadirá un ledger append-only de ejecución para registrar apertura,
evaluación, revelado documental y cierre sin reescribir etapas anteriores.

V4 conectará ese ledger con S7/S8 para exigir continuidad criptográfica entre
preregistro, apertura, holdout y promoción.
