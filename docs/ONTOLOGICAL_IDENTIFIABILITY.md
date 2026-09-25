# Identificabilidad ontológica y separabilidad de modelos · ALMAS

## Objeto

Este documento formaliza, antes de crear discriminadores concretos, cuándo ALMAS puede distinguir entre cuatro hipótesis operativas:

- `SOULMATE_MODEL` · alma gemela en sentido soulmate;
- `MONADIC_ORIGIN` · origen monádico común;
- `SPLIT_SOUL` · alma/entidad originaria dividida;
- `TWIN_FLAME_MODEL` · modelo contemporáneo twin flame.

Son hipótesis del proyecto, no equivalencias históricas entre tradiciones. `TWIN_SOUL` permanece separado hasta que el registro doctrinal determine su relación con los demás términos.

## Separación epistemológica

Toda evidencia conserva A/B/C/D/E:

- A · dato calculado o documental;
- B · técnica;
- C · doctrina explícita;
- D · uso contemporáneo;
- E · hipótesis del proyecto.

Validar un discriminador operacional no equivale a demostrar la ontología metafísica que describe.

## Notación

Sea:

`H = {S, M, P, T}`

con `S=SOULMATE_MODEL`, `M=MONADIC_ORIGIN`, `P=SPLIT_SOUL` y `T=TWIN_FLAME_MODEL`.

Sea `O* = {o1,...,on}` el conjunto de observables realmente evaluables en un caso.

Cada observable deberá declarar definición operacional, procedencia, tipo A/B/C/D/E, método, calidad, dependencia, regla de ausencia, hipótesis alternativas y falsador.

La firma observable de un modelo es:

`Signature(H_i | O*) = {Pred(H_i,o) : o ∈ O*}`.

Las predicciones pueden ser condiciones necesarias, incompatibilidades, patrones esperados, rangos, secuencias, condiciones documentales o restricciones doctrinales.

## Equivalencia observacional

Dos modelos son observacionalmente equivalentes respecto de `O*` cuando ningún discriminador validado disponible permite separarlos:

`H_i ~[O*] H_j`.

Esto no significa equivalencia doctrinal ni identidad metafísica.

La relación induce clases de equivalencia. Por ejemplo:

`{{S}, {M,P,T}}`

significa que soulmate es separable, pero monádico, split-soul y twin-flame siguen indistinguibles. En ese caso ALMAS no debe escoger M, P o T por puntuación y deberá conservar, cuando corresponda:

`SHARED_ORIGIN_UNDIFFERENTIATED / INSUFFICIENT`.

## Estados de identificabilidad

`IDENTIFIABLE`: los discriminadores admisibles reducen los modelos supervivientes a una única hipótesis operacional. No implica demostración metafísica.

`PARTIALLY_IDENTIFIABLE`: se excluye al menos un modelo, pero sobreviven dos o más modelos no separados. Las categorías específicas permanecen `INSUFFICIENT`.

`NON_IDENTIFIABLE`: los modelos relevantes producen la misma firma operacional o no existe un discriminador validado que los separe.

`NOT_EVALUABLE`: faltan datos, calidad, técnica o medición suficientes para evaluar la separabilidad.

## Separabilidad par a par

Un par `(H_i,H_j)` sólo es separable de forma confirmatoria si existe al menos un discriminador que:

1. produzca predicciones distintas para ambos modelos;
2. haya sido definido antes de observar el caso;
3. sea medible de forma reproducible;
4. no dependa de la autoetiqueta;
5. no duplique otra raíz;
6. tenga regla de falsación o incompatibilidad;
7. registre hipótesis alternativas;
8. alcance el nivel de validación exigido;
9. no dependa sólo de capas `support_only`;
10. supere controles de leakage aplicables.

Estados de cada par:

- `SEPARABLE_VALIDATED`;
- `SEPARABLE_EXPERIMENTAL`;
- `OBSERVATIONALLY_EQUIVALENT`;
- `INSUFFICIENT_EVIDENCE`;
- `NOT_EVALUABLE`.

Sólo `SEPARABLE_VALIDATED` puede excluir un modelo en una ejecución confirmatoria.

## Tipos de regla

`NECESSARY`: si una condición doctrinalmente necesaria está válidamente ausente, puede generar contraevidencia.

`SUFFICIENT_OPERATIONAL`: suficiente sólo dentro del modelo operacional preregistrado; no implica suficiencia metafísica.

`EXCLUSIONARY`: una observación es incompatible con un modelo según regla previa.

`SUPPORTIVE_NON_DISCRIMINATING`: compatible con un modelo y al menos un competidor; nunca separa por sí sola.

## Regla de monotonía epistemológica

Añadir evidencia no discriminante no puede convertir una clase no identificable en identificable.

Si una nueva evidencia tiene la misma compatibilidad con todos los modelos de una clase, la partición de equivalencia no cambia.

Por tanto, acumular intensidad, reconocimiento, sincronicidad o cualquier otra señal compartida no separa modelos que ya eran equivalentes.

## Prohibición de sustitución por puntuación

Si `H_i ~[O*] H_j`, entonces:

`Score(H_i) > Score(H_j)`

no permite concluir `H_i`.

Un score puede describir densidad, ajuste, intensidad o robustez. Sólo puede romper una equivalencia si ese score fue validado previamente como discriminador independiente entre esos modelos.

## Independencia

Dos observaciones no constituyen dos discriminadores si derivan de la misma raíz causal, geométrica, doctrinal, narrativa o de medición.

El futuro registro deberá conservar al menos:

- `dependency_family`;
- `root_key`;
- `source_root`;
- `measurement_root`.

La repetición de una misma estructura en varias técnicas no aumenta automáticamente la capacidad de separación.

## Niveles de separabilidad

`L1_DOCTRINAL`: dos modelos realizan afirmaciones distintas en fuentes.

`L2_OPERATIONAL`: la diferencia doctrinal puede convertirse en observable reproducible y falsable.

`L3_VALIDATED`: la regla y la medición fueron preregistradas, replicadas y probadas fuera del conjunto de desarrollo con controles negativos y de leakage.

Sólo L3 puede actuar como discriminador confirmatorio.

Ningún nivel equivale a validación ontológica de la metafísica subyacente.

## Validez exigible

Cada candidato deberá distinguir:

- `SOURCE_VALIDITY`;
- `CONSTRUCT_VALIDITY`;
- `MEASUREMENT_RELIABILITY`;
- `DISCRIMINANT_VALIDITY`;
- `CONVERGENT_VALIDITY`;
- `OUT_OF_SAMPLE_STABILITY`;
- `NEGATIVE_CONTROL_SPECIFICITY`;
- `LEAKAGE_RESISTANCE`.

## Función de decisión

La futura función puede expresarse como:

`δ(x,H,D_valid) → (Survivors,Partition,IdentifiabilityState,EpistemicState)`.

Reglas mínimas:

1. datos indispensables ausentes → `NOT_EVALUABLE`;
2. ningún discriminador validado separa supervivientes → `NON_IDENTIFIABLE` o `PARTIALLY_IDENTIFIABLE`;
3. sobrevive una clase con más de un modelo → categoría específica `INSUFFICIENT`;
4. sobrevive un solo modelo por discriminadores validados → `IDENTIFIABLE`, sujeto a los demás gates;
5. una señal experimental no elimina modelos en modo confirmatorio;
6. ausencia de evidencia no equivale a contraevidencia salvo que una condición necesaria fuese válidamente observable.

## Correspondencia con la ontología vigente

`reference/ontology-registry.json` ya contiene:

- `SHARED_ORIGIN_UNDIFFERENTIATED`;
- `MONADIC_COMMON_SOURCE`;
- `SPLIT_SOUL`;
- `TWIN_SOUL`;
- `TWIN_FLAME_MODEL`;
- `INDETERMINATE`.

La nueva lógica no sustituye esas categorías. Determina cuándo existe base para pasar de una categoría amplia a una específica.

## Terminología «alma gemela»

El término español es ambiguo y puede traducir soulmate, twin soul o incluso twin flame.

Para el discriminador inicial se utilizará `SOULMATE_MODEL` para «alma gemela» en sentido soulmate. Las equivalencias históricas deberán resolverse en el registro doctrinal posterior, nunca por semejanza léxica.

## Astrología

Una señal astrológica sólo puede participar como observable técnico B si es reproducible, tiene parámetros explícitos, ha sido deduplicada por dependencia, posee raíz identificada y responde a una hipótesis diferencial previa.

Rareza bajo un modelo nulo no es probabilidad metafísica.

Las técnicas temporales pueden activar una arquitectura ya existente, pero no crear una categoría ontológica.

## Fenomenología

Reconocimiento, intensidad, familiaridad, sueños, sincronicidad, destino, runner/chaser o experiencias transpersonales se consideran por defecto:

`SUPPORTIVE_NON_DISCRIMINATING`

hasta que exista evidencia independiente de capacidad diferencial reproducible.

La autoetiqueta se registra como D y no forma parte de la verdad de referencia.

## Falsa especificidad

Se produce `FALSE_SPECIFICITY` cuando la salida es más específica que la partición permitida por los discriminadores validados.

Ejemplo:

Partición válida: `{{S},{M,P,T}}`.

Salida incorrecta: `TWIN_FLAME_MODEL / SUPPORTED`.

Esto deberá ser un error crítico de los tests futuros.

## Invariantes derivados

La implementación futura deberá demostrar que:

- duplicar evidencia no discriminante no cambia la partición;
- eliminar una autoetiqueta no cambia el análisis estructural;
- una señal experimental no elimina modelos en modo confirmatorio;
- si M y P tienen la misma firma, el sistema no escoge entre ellos;
- si M, P y T son equivalentes, la categoría específica queda `INSUFFICIENT`;
- un discriminador sólo afecta los pares para los que fue validado;
- la ausencia de un dato opcional no crea contraevidencia;
- una técnica temporal no crea distinción ontológica;
- una puntuación mayor no rompe equivalencia;
- una misma raíz repetida no se convierte en varios discriminadores.

## Límite ontológico

ALMAS puede validar consistencia, calidad de fuentes, reproducibilidad, discriminación operacional, estabilidad, especificidad, resistencia a leakage y comportamiento fuera de desarrollo.

Eso no demuestra por sí solo la existencia objetiva de una ontología metafísica.

## Próximo paso

El siguiente paso será construir el registro doctrinal comparado de los cuatro modelos y documentar, fuente por fuente, qué afirmaciones son realmente diferenciales y cuáles son compartidas. Ese trabajo producirá candidatos a discriminador, no reglas confirmatorias.
