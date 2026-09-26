# Auditoría final de release · ALMAS 1.15.0

**Fecha:** 27 de septiembre de 2026  
**Rama auditada:** `evolution/1.15.0-recurrence-specificity`  
**Base:** ALMAS 1.14.0 · `48baeff6581f36185cf01c246d8224daaa3d2dcd`  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** calibración de especificidad de la recurrencia semántica y ciclo metodológico PX v3 no operativo.

## 1. Motivo de la release

ALMAS 1.14.0 corrigió el falso negativo operacional de PX 1.13 mediante
recurrencia semántica multitécnica. La primera ejecución de estrés mostró el
problema complementario: un PX elevado puede saturarse en controles nulos y
depender de familias técnicas concretas.

1.15.0 no corrige esa observación ajustando pesos al caso. En su lugar construye
una infraestructura preregistrable S1–S9 para medir especificidad, recibir
controles externos y probar futuras reglas fuera de muestra.

## 2. S1 · calidad de recurrencia

`ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1` describe, por motivo:

- número de familias y clases técnicas;
- entropía normalizada de fuerza;
- número efectivo de familias;
- dominancia de la familia principal;
- recurrencia sin NATAL_DRACONIC;
- supervivencia leave-one-family-out;
- supervivencia leave-one-class-out.

S1 es estrictamente descriptiva y no modifica PX/PS, IEM, IDD, IRC u ontología.

## 3. S2 · calibración nula

`ALMAS_RECURRENCE_NULL_CALIBRATION_V1` reutiliza el universo
`ALMAS_NULL_WITHIN_YEAR_V1` para medir presencia, fuerza y calidad de cada
motivo, así como PX/PS y número de motivos recurrentes.

Se publican frecuencias incondicionales y condicionadas a presencia del motivo
con intervalos de Wilson. No existe p-value combinado ni interpretación
metafísica de la frecuencia.

## 4. S3 · controles sintéticos

`ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1` incorpora dos familias
deterministas:

- SEMANTIC_SIGNATURE_ROTATION;
- DECOUPLED_POINT_RELATION_ROTATION.

No se usa RNG. Las frecuencias describen una familia finita de controles
deterministas y no una población.

## 5. S4 · firewall de cohortes externas

`ALMAS_EXTERNAL_RECURRENCE_COHORT_V1` define la entrada privada de
`PAIR_SHUFFLE`, `MATCHED_AGE` y `MATCHED_AGE_CLOCK`.

Exige preregistro, versión/commit congelados, reglas de inclusión/emparejamiento,
estado de validación, cegamiento, contaminación, leakage y snapshot estructural.

La salida pública es agregada. Identificadores y snapshots individuales no se
serializan.

## 6. S5 · calibración externa

`ALMAS_EXTERNAL_RECURRENCE_CALIBRATION_V1` conecta únicamente controles
externos limpios y preregistrados con el mismo núcleo matemático de S2.

DEVELOPMENT_ONLY, post-hoc, contaminación, leakage y case fitting quedan
excluidos. La salida sigue siendo diagnóstica y no habilita weighting.

## 7. S6 · candidatos PX v3

`ALMAS_PX_V3_CANDIDATE_FREEZE_V1` introduce un gate para congelar reglas
antes del holdout.

El registro canónico `ALMAS_PX_V3_CANDIDATES` permanece deliberadamente
vacío:

`records=[]`

`validated_candidate_ids=[]`

Ninguna fórmula PX v3 real forma parte de 1.15.0.

## 8. S7 · runner holdout

`ALMAS_PX_V3_HOLDOUT_EVALUATION_V1` sólo acepta candidatos previamente
congelados, cohorte S4 limpia, fórmula idéntica y cobertura completa.

Produce estadísticos agregados y un fingerprint SHA-256. No publica sample refs
ni valores individuales y fija `promotion_decision=FORBIDDEN`.

## 9. S8 · promoción metodológica

`ALMAS_PX_V3_PROMOTION_GATE_V1` puede declarar `PROMOTION_ELIGIBLE` sólo
con holdout válido, calibración externa, replicación independiente, controles
negativos, ablación, auditoría de leakage, criterios preregistrados y cero
case fitting/cambios post-holdout.

`PROMOTION_ELIGIBLE` no activa la regla, no muta el registro y no constituye
validación metafísica.

## 10. S9 · firewall de activación

`ALMAS_PX_V3_ACTIVATION_FIREWALL_V1` vincula la release 1.15 a PX v2:

`operational_px_engine=ALMAS_SEMANTIC_MOTIF_V2`.

Dentro de 1.15 se bloquea cualquier registro activo, validated candidate,
scoring, weighting u ontología PX v3.

Una activación futura requiere una nueva línea SemVer, cambio canónico manual,
nueva auditoría y nuevo contrato público.

## 11. Invariantes preservados

1. PX v2 continúa siendo el único PX operativo.
2. S1–S9 no modifican PX, PS, IEM, IDD, IRC ni ontología de producción.
3. Rareza o frecuencia bajo null/control no es probabilidad metafísica.
4. Un caso de desarrollo no puede validar la regla que ayudó a crear.
5. Holdout y desarrollo no pueden solaparse.
6. La fórmula se congela antes del holdout.
7. Ningún proceso runtime puede mutar el registro canónico.
8. `PROMOTION_ELIGIBLE` no equivale a activación.
9. `validated_discriminator_ids=[]` permanece sin discriminadores L3 reales.
10. `ALMAS_PX_V3_CANDIDATES.records=[]` permanece vacío.
11. Compuesta/Davison siguen una sola familia RELCHART.
12. Support-only no crea recurrencia core.
13. Temporalidad no crea raíces estructurales.
14. Los datos privados no se incorporan al repositorio público.

## 12. Compatibilidad

1.15.0 conserva los contratos M00–M31 y los scores de producción de 1.14.0.
Los nuevos componentes son diagnósticos, protocolos, schemas y gates
metodológicos.

No se cambian los thresholds públicos de SUPPORTED, las fórmulas IEM/IDD/IRC,
el motor PX v2 ni los discriminadores ontológicos vigentes.

## 13. Procedencia y privacidad

La línea S4–S8 está subordinada a `ALMAS_PUBLIC_DATA_ISOLATION_V1`,
`ALMAS_BLINDING_LEAKAGE_V1` y al protocolo de validación externa.

Los holdouts privados permanecen fuera del repositorio. Sólo se permiten
agregados públicos no identificables.

## 14. Validación automatizada

La release incorpora tests específicos para S1–S9, además de la suite previa
M00–M31, firewalls metodológicos, schemas y contrato público.

La fusión requiere que el mismo HEAD final 1.15.0 concluya SUCCESS en:

- Contrato público;
- Núcleo Python 3.10;
- Núcleo Python 3.12.

El HEAD de release ejecuta **394 tests deterministas**. El mismo recuento se
registra en `VALIDATION_STATUS.md`.

## 15. Límites que permanecen

No se ha ejecutado un holdout externo real preregistrado.

No existe una fórmula PX v3 real congelada, evaluada o promovida.

No existe ningún discriminador ontológico L3 validado.

La infraestructura de calibración no valida científicamente la astrología ni
demuestra categorías metafísicas.

## 16. Decisión de release

ALMAS 1.15.0 se considera cerrable como release minor porque añade un ciclo
metodológico completo para calibrar y validar futuras reglas de especificidad
sin alterar retrospectivamente el scoring de 1.14.

No debe inventarse un candidato PX v3 para completar la release. La ausencia
de candidatos activos es un resultado metodológico correcto y está protegida
por S9.
