# Protocolo ciego de identidad diádica · ALMAS

## Estado

Política canónica experimental: `ALMAS_PAIR_IDENTITY_VALIDATION_V1`.

Clase epistemológica: `E_PROJECT_POLICY`.

Estado empírico: `INFRASTRUCTURE_ONLY_NO_EMPIRICAL_HOLDOUT`.

Esta capa no altera IEM, IDD, IRC, ICC, ICE, PX, PS, PU ni la ontología de caso. Tampoco crea un discriminador L3.

## Problema que resuelve

ALMAS debe separar dos preguntas distintas:

1. **TF-PHENOTYPE**: una persona o relación presenta rasgos que, dentro del corpus estudiado, son compatibles con procesos descritos como twin-flame-like.
2. **TF-PAIR-IDENTITY**: dos individuos concretos son la díada declarada correspondiente entre un conjunto de candidatos.

La desigualdad `TF-PHENOTYPE != TF-PAIR-IDENTITY` es una **hipótesis operacional del proyecto**, no doctrina histórica ni verdad metafísica.

La validación de pair identity utiliza como referencia `DECLARED_MATCHED_DYAD`: una etiqueta documental/emic congelada antes del análisis. No se interpreta como prueba de una contraparte metafísica real.

## Matriz adversarial

Para díadas documentadas `D_i=(DF_i,DM_i)`:

- positivo: `DF_i-DM_i` → `DECLARED_MATCHED_DYAD`;
- hard negative primario: `DF_i-DM_j, i!=j` → `CROSS_DYAD_OPPOSITE_POLARITY`;
- controles secundarios: `DF_i-DF_j` y `DM_i-DM_j`;
- control externo: pares ordinarios independientes.

El hard negative DF-DM incorrecto es el principal porque mantiene la polaridad declarada. Un clasificador que sólo aprenda “DF frente a DM” debe fallar aquí.

DF/DM se registran como roles **declarados**. Esta política prohíbe inferirlos desde astrología.

## Cegamiento

La función `build_blinded_pair_identity_matrix` pertenece al custodio documental. Recibe referencias internas y un secreto de cegamiento y produce:

- `blinded_pairs`: sólo identificadores HMAC opacos y pares de sujetos;
- `sealed_truth`: estrato, correspondencia declarada y metadatos necesarios para el reveal.

`sealed_truth` no entra en M00-M31 ni en ninguna selección de features, fórmula o threshold. El output estructural debe congelarse antes del revelado y satisfacer `ALMAS_BLINDING_LEAKAGE_V1`.

## Separación desarrollo/evaluación

Las personas se separan por díada **antes** de construir cross-pairs. Ningún sujeto puede aparecer simultáneamente en desarrollo, holdout o replicación.

Los casos conocidos, interpretados previamente o usados para proponer reglas son `DEVELOPMENT_ONLY`. Nunca pueden convertirse después en holdout confirmatorio de esas mismas reglas.

Objetivos operativos de programa:

- 40 díadas: desarrollo;
- 120 díadas: primer holdout externo;
- 120 díadas: replicación independiente.

Son objetivos de diseño, no mínimos científicos universales. El gate real utiliza incertidumbre Wilson; con cero falsos positivos hacen falta al menos 73 negativos para que el límite superior 95 % sea <=0,05.

## Evaluación

`evaluate_pair_identity_holdout` recibe únicamente, después del reveal:

- `pair_id`;
- score continuo producido por una fórmula ya congelada;
- truth sellado;
- threshold congelado.

La comparación confirmatoria es `DECLARED_MATCHED_DYAD` frente a `CROSS_DYAD_OPPOSITE_POLARITY`.

Se calculan:

- sensibilidad y CI95 Wilson;
- especificidad y CI95 Wilson;
- balanced accuracy;
- FALSE_SPECIFICITY_RATE y su CI95 superior;
- ROC-AUC diagnóstica;
- concordancia pareada true-vs-cross para cada DF consultado.

El gate reutiliza los mínimos de `ALMAS_DISCRIMINANT_VALIDATION_V1`:

- CI95 inferior de sensibilidad >= 0,60;
- CI95 inferior de especificidad >= 0,90;
- balanced accuracy >= 0,75;
- CI95 superior de falsa especificidad <= 0,05.

ROC-AUC se informa, pero no constituye por sí sola un gate de promoción.

## Nulls, ablación y hora natal

Una evaluación futura debe ejecutar además:

- null de correspondencia por permutación de contrapartes;
- `ALMAS_NULL_WITHIN_YEAR_V1`;
- AB0-AB8;
- R5/R15/R30/R60/R120;
- auditoría de dependencia y pseudo-replicación.

Estos controles responden preguntas diferentes. Una baja frecuencia WITHIN_YEAR sigue siendo rareza estructural bajo ese null, no probabilidad de pair identity ni probabilidad metafísica.

## Criterio de éxito

`PASS_OPERATIONAL_GATE` significa únicamente que una fórmula congelada discriminó la **díada declarada** frente al hard negative DF-DM incorrecto bajo el conjunto evaluado.

El resultado conserva siempre:

- `l3_promotion_authorized=false`;
- `ontology_activation=false`;
- `declared_match_is_metaphysical_ground_truth=false`;
- `metaphysical_probability=false`.

Para una futura promoción L3 seguirían siendo obligatorios holdout externo, replicación independiente, controles negativos, cegamiento/leakage, auditoría de independencia astrológica, ablaciones y sensibilidad horaria.

## Privacidad

Los datos reales de holdout, identidades, fechas/horas/lugares natales y truth sellado permanecen fuera del repositorio público. GitHub sólo puede contener protocolo, schemas, código, fixtures sintéticos y métricas agregadas no identificables.
