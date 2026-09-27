# Auditoría final de release · ALMAS 1.16.0

**Fecha:** 27 de septiembre de 2026  
**Rama auditada:** `evolution/1.16.0-validation-operations`  
**Base:** ALMAS 1.15.0  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** operacionalización V1–V5 del ciclo de validación externa, sin activación automática de PX v3.

## Alcance

ALMAS 1.16.0 incorpora infraestructura para preregistrar, abrir, ejecutar, encadenar, revelar documentalmente y cerrar una validación externa sin permitir que los resultados observados modifiquen retrospectivamente la metodología congelada.

La release no incorpora un candidato PX v3 real al registro canónico, no ejecuta por sí misma un holdout externo real y no promueve ningún discriminador a L3.

## Cadena operacional

V1, `ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1`, congela candidato, fórmula, versión/commit, cohorte, cegamiento, auditoría de leakage, replicación, controles, ablaciones, endpoints y criterios de éxito/fallo antes de observar el holdout.

V2, `ALMAS_HOLDOUT_OPEN_GATE_V1`, verifica ese preregistro y produce un registro de apertura. La apertura autoriza ejecutar el holdout congelado, pero no constituye evaluación, promoción ni activación.

V3, `ALMAS_VALIDATION_EXECUTION_LEDGER_V1`, conserva una cadena SHA-256 append-only: `PREREGISTERED → HOLDOUT_OPENED → HOLDOUT_EVALUATED → DOCUMENTARY_REVEALED → VALIDATION_CLOSED`.

V4, `ALMAS_VALIDATION_CONTINUITY_GATE_V1`, exige continuidad entre V1, V2, S7 y las tres primeras entradas del ledger. El certificado resultante sólo permite presentar la evidencia a S8.

V5, `ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1`, exige revelado documental tardío sin mutación del fingerprint estructural, cero leakage/case fitting y un resultado S8 enlazado al mismo certificado V4. El cierre produce un artefacto confirmatorio y un paquete agregado de auditoría de release.

## Firewalls de cierre

Un resultado `PROMOTION_ELIGIBLE` queda registrado únicamente como `PROMOTION_ELIGIBLE_AWAITING_VERSIONED_ACTIVATION`. La misma release no puede activar el candidato.

Los artefactos V1–V5 mantienen:

- `automatic_registry_mutation=false`;
- `same_release_activation_forbidden=true`;
- `manual_new_version_required_for_activation=true`;
- `scoring_activation=false`;
- `weighting_activation=false`;
- `ontology_activation=false`;
- `l3_validation=false`;
- `metaphysical_probability=false`.

El registro canónico PX v3 permanece vacío y PX v2 continúa siendo la capa operativa.

## Privacidad y datos

Los artefactos públicos de validación sólo contienen metadatos, referencias opacas, agregados y fingerprints. No se publican muestras holdout privadas, scores individuales, cartas, narrativa relacional privada ni identificadores de casos privados.

El revelado documental V5 no acepta narrativa cruda como payload. Una identidad pública inevitable exige referencias explícitas del riesgo de cegamiento y no relaja las prohibiciones de leakage.

## Validación automatizada

El contrato público incluye políticas, schemas, módulos y tests específicos para V1–V5. La suite se ejecuta en Python 3.10 y 3.12 y el validador público comprueba las invariantes de freeze, continuidad, ledger, revelado tardío, cierre y no activación.

El número definitivo de tests de esta release se fija por el workflow `Núcleo Python`. La documentación de estado se sincroniza con el resultado del runner antes del merge final.

## Estado empírico

**Holdout externo real:** NO EJECUTADO.  
**Candidato PX v3 real promovido:** NINGUNO.  
**Discriminadores L3 reales:** NINGUNO.  
**Registro PX v3 activo:** VACÍO.

Por tanto, la release demuestra coherencia e integridad del procedimiento implementado; no demuestra validez científica de la astrología ni verdad ontológica de categorías metafísicas.
