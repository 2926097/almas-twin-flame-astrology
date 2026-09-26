# Política de validez discriminante · Paso 14

## Finalidad

Este paso convierte la validación externa del discriminador ontológico en un gate cuantitativo reproducible.

La política canónica es:

`ALMAS_DISCRIMINANT_VALIDATION_V1`.

Su clasificación epistemológica es:

`E_PROJECT_POLICY`.

Los umbrales de esta política no se presentan como constantes científicas universales. Son criterios normativos del proyecto, congelados antes del holdout, diseñados para priorizar especificidad y preservación de `INSUFFICIENT`.

## Separación entre desarrollo y evaluación

Toda promoción L3 exige:

`development_evaluation_disjoint=true`.

Ningún caso utilizado para definir features, reglas, umbrales, pesos, orbes o discriminadores puede reutilizarse como evaluación confirmatoria de la misma versión.

## Métricas pairwise

Cada par incluido en `validated_pairs` debe disponer de una matriz binaria trazable:

- TP;
- TN;
- FP;
- FN.

A partir de estos conteos se calculan:

`sensibilidad = TP / (TP + FN)`

`especificidad = TN / (TN + FP)`

`balanced_accuracy = (sensibilidad + especificidad) / 2`

ALMAS calcula internamente intervalos Wilson al 95 %.

Para promoción L3:

- límite inferior CI95 de sensibilidad ≥ 0.60;
- límite inferior CI95 de especificidad ≥ 0.90;
- balanced accuracy ≥ 0.75.

La especificidad recibe un requisito más exigente porque un falso positivo ontológico puede producir falsa especificidad, mientras que un falso negativo puede conservar `INSUFFICIENT`.

## FALSE_SPECIFICITY_RATE

`FALSE_SPECIFICITY` ocurre cuando el sistema afirma una ontología más específica que la permitida por el techo inferencial o excluye un modelo sin discriminador validado suficiente.

La tasa se define como:

`FALSE_SPECIFICITY_RATE = errores_de_falsa_especificidad / casos_evaluables_para_falsa_especificidad`

No se usa sólo la estimación puntual.

La promoción exige:

`CI95_superior(FALSE_SPECIFICITY_RATE) <= 0.05`.

Esta regla hace que una muestra pequeña con cero errores no sea automáticamente confirmatoria.

Ejemplo normativo del gate Wilson actual:

- 0 errores en 72 controles: no supera el gate;
- 0 errores en 73 controles: supera exactamente el techo aproximado;
- cualquier diseño puede usar más controles.

El valor 0.05 es una política ALMAS versionada y puede cambiar únicamente mediante una nueva versión metodológica preregistrada.

## Controles sintéticos y adversariales

En controles sintéticos/adversariales la tolerancia es:

`FALSE_SPECIFICITY_RATE = 0`.

Un solo caso de sobreespecificación sintética bloquea la promoción.

Esta condición no sustituye la validación externa real.

## Cobertura de pares

`pairwise_results` debe cubrir exactamente todos los pares declarados en `validated_pairs`.

No está permitido:

- validar un solo par y extenderlo a otros;
- promediar pares para ocultar uno deficiente;
- reutilizar una matriz de confusión para un par distinto;
- declarar `ALL_TARGET_MODELS` sin resultados pairwise separados.

## Calibración

Las salidas categóricas que no expresan probabilidad usan:

`NOT_APPLICABLE_CATEGORICAL`.

No se fuerza una calibración probabilística artificial.

Si en el futuro un discriminador emite probabilidades o confianza probabilística:

`mode = PROBABILISTIC`

y debe existir:

- criterio de calibración preregistrado;
- referencias de evaluación;
- `passed=true`.

Una probabilidad no calibrada no puede autorizar L3.

## Incertidumbre

El método actual es:

`WILSON_SCORE`, confianza 95 %.

La incertidumbre forma parte del gate. No basta con que la tasa puntual de error sea pequeña.

La política evita imponer directamente un tamaño muestral fijo: el propio intervalo de confianza penaliza evaluaciones demasiado pequeñas.

## Relación con el registro de promoción

Cada registro `VALIDATED_DISCRIMINATOR` debe incluir:

`discriminant_validation`.

El runtime vuelve a calcular las métricas a partir de los conteos. Una ejecución no puede autorizarse simplemente escribiendo una tasa favorable en JSON.

El mismo registro continúa exigiendo:

- preregistro;
- replicación independiente;
- holdout externo;
- controles negativos;
- leakage audit;
- y, cuando proceda, el firewall de independencia astrológica.

## Límite epistemológico

Superar este gate significa que el clasificador operacional ha mostrado separación, especificidad y estabilidad suficientes dentro del observable y población registrados.

No demuestra:

- la existencia metafísica de soulmate, Mónada, split-soul o twin-flame;
- que una pareja concreta pertenezca metafísicamente a una categoría;
- que el resultado sea transferible a otros pares de modelos no validados.

## Siguiente paso

El Paso 15 formalizará blindaje, leakage y separación estricta entre información permitida y variables capaces de contaminar el clasificador.
