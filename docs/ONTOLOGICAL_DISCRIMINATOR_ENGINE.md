# Motor lógico autónomo del discriminador ontológico

## Finalidad

Este componente implementa la lógica de identificabilidad definida para ALMAS y dispone ya de un adaptador interno opcional dentro de M21.

Su responsabilidad es limitada:

- recibir modelos candidatos;
- recibir observaciones discriminantes ya evaluadas;
- construir una matriz par a par;
- separar evidencia L2 de L3;
- eliminar modelos sólo con discriminadores L3 validados;
- conservar clases no resueltas;
- impedir falsa especificidad;
- devolver una vista exploratoria separada cuando se solicita.

No calcula astrología, no interpreta doctrina, no asigna scores y no convierte rareza en probabilidad metafísica.

## Archivo ejecutable

`src/almas_tfa/ontological_discriminator.py`

Función pública inicial:

`discriminate_ontology(...)`

El motor permanece como componente autónomo. M21 lo invoca únicamente a través de `src/almas_tfa/m21_ontology_adapter.py` cuando existe `ontological_discriminator_input`; sin esa entrada, el comportamiento histórico de M21 permanece intacto.

## Modelos por defecto

El motor opera inicialmente sobre:

- `SOULMATE_MODEL`;
- `MONADIC_ORIGIN`;
- `SPLIT_SOUL`;
- `TWIN_FLAME_MODEL`.

La lista puede sustituirse explícitamente para tests o futuras ampliaciones.

## Entrada elemental

Cada observación debe especificar:

- `discriminator_id`;
- `pair`;
- `validation_level`;
- `result`;
- `excluded_model` si `result=SEPARATES`;
- `root_key`;
- nota opcional.

Niveles admitidos:

- `L1_DOCTRINAL`;
- `L2_EXPERIMENTAL`;
- `L3_VALIDATED`.

Resultados admitidos:

- `SEPARATES`;
- `NO_SEPARATION`;
- `NOT_EVALUABLE`.

## Deduplicación por raíz

El motor agrupa observaciones por:

`(pair, root_key)`

y conserva el nivel de validación más alto disponible dentro de la misma raíz.

Esto evita que una misma señal gane peso por estar repetida como:

- varias técnicas derivadas;
- varias formulaciones textuales;
- varias versiones del mismo discriminador;
- capas experimental y validada de la misma raíz.

Una discrepancia dentro de la misma raíz al mismo nivel máximo se registra como conflicto y no produce exclusión.

## Matriz par a par

Para cada par se generan dos estados independientes:

`confirmatory_status`

y

`exploratory_status`.

El primero sólo puede usar L3 para excluir.

El segundo puede mostrar una separación L2 como:

`SEPARABLE_EXPERIMENTAL`.

La matriz confirmatoria admite:

- `SEPARABLE_VALIDATED`;
- `OBSERVATIONALLY_EQUIVALENT`;
- `INSUFFICIENT_EVIDENCE`;
- `NOT_EVALUABLE`;
- `CONFLICTING_EVIDENCE`.

## Regla canónica L2/L3

La invariante central del motor es:

`L2_EXPERIMENTAL !-> CONFIRMATORY_EXCLUSION`

Una señal L2 puede aparecer en la vista exploratoria, pero no se añade a `confirmed_exclusions`.

Por tanto, el modo `EXPLORATORY` nunca reescribe la decisión canónica.

## Eliminación confirmatoria

Un modelo sólo puede entrar en `confirmed_exclusions` cuando un par dispone de separación L3 consistente.

Si discriminadores L3 independientes del mismo par excluyen modelos opuestos, el par pasa a:

`CONFLICTING_EVIDENCE`

y ninguno se elimina.

Si un ciclo global de exclusiones eliminase todos los candidatos, el motor revoca esas exclusiones y registra:

`GLOBAL_ELIMINATION_CYCLE`.

## Estados de identificabilidad

`IDENTIFIABLE`

Queda un único modelo después de exclusiones L3 consistentes.

El motor fija como máximo:

`epistemic_state = COMPATIBLE`.

No produce `SUPPORTED`; ese estado requiere gates posteriores.

`PARTIALLY_IDENTIFIABLE`

Se ha excluido al menos un modelo, pero sobreviven dos o más.

`NON_IDENTIFIABLE`

No existe separación L3 suficiente o existen conflictos.

`NOT_EVALUABLE`

Los datos mínimos no permiten evaluar el problema.

## Clasificación conservadora

Si sobrevive un único modelo, la clasificación operacional puede nombrarlo.

Si sobreviven exclusivamente dos o más de:

- `MONADIC_ORIGIN`;
- `SPLIT_SOUL`;
- `TWIN_FLAME_MODEL`;

la salida es:

`SHARED_ORIGIN_UNDIFFERENTIATED`.

Si sobreviven combinaciones más amplias, se devuelve:

`INDETERMINATE`.

## Equivalencia

La salida `equivalence_classes` representa el conjunto de modelos que el nivel confirmatorio actual no ha podido separar.

No implica identidad doctrinal ni identidad metafísica.

## Vista exploratoria

Sólo aparece cuando:

`mode=EXPLORATORY`.

Incluye:

- exclusiones L2 hipotéticas;
- modelos que sobrevivirían experimentalmente;
- clasificación experimental;
- lista de exclusiones exclusivamente experimentales;
- advertencia explícita de no promoción.

La propiedad:

`canonical_decision_unchanged=true`

es obligatoria.

## Guardarraíl de falsa especificidad

`false_specificity_guard` debe permanecer verdadero cuando:

- queda un único modelo; o
- sobreviven varios y la salida conserva `SHARED_ORIGIN_UNDIFFERENTIATED` o `INDETERMINATE`.

Una implementación futura que devuelva una categoría específica con múltiples modelos confirmatoriamente supervivientes deberá fallar tests.

## Prohibiciones

El motor no acepta como mecanismo de decisión:

- diferencias de score sin validación discriminante;
- suma de sincronías;
- intensidad;
- sufrimiento;
- rareza astrológica;
- número bruto de técnicas;
- autoetiqueta;
- narrativa retrospectiva.

La salida incluye expresamente:

- `l2_can_confirm=false`;
- `scores_can_break_equivalence=false`;
- `absence_is_counterevidence_by_default=false`.

## Contrato de salida

Schema:

`schemas/ontological-discriminator-output.schema.json`

Tests:

`tests/test_ontological_discriminator.py`

Los tests cubren:

- L2 no excluye en confirmatorio;
- vista exploratoria no modifica la decisión canónica;
- salida `SHARED_ORIGIN_UNDIFFERENTIATED`;
- identificabilidad con un único superviviente sin promoción automática a SUPPORTED;
- conflicto L3;
- deduplicación por raíz;
- equivalencia observacional con cobertura completa;
- NOT_EVALUABLE por falta de datos mínimos;
- guardarraíl de falsa especificidad.

## Batería adversarial sintética

El Paso 11 añade:

`tests/test_ontological_discriminator_adversarial.py`

y los invariantes:

`tests/ONTOLOGICAL_DISCRIMINATOR_ADVERSARIAL_INVARIANTS.md`.

La batería intenta forzar falsa especificidad mediante:

- inundación L1/L2;
- repetición de una misma raíz;
- conflicto interno L3;
- ciclos globales de eliminación;
- ruido NOT_EVALUABLE;
- contaminación narrativa;
- autoetiqueta, runner/chaser, sincronicidad e intensidad;
- rareza astrológica y afirmaciones temporales;
- reutilización fraudulenta de `promotion_ref`;
- pares y familias de raíz no autorizados;
- registros de validación incompletos.

Superar esta batería sólo demuestra resistencia del clasificador a ataques sintéticos conocidos. No promociona candidatos ni constituye validación externa.

## Suite metamórfica formal

El Paso 12 añade:

`tests/test_ontological_discriminator_metamorphic.py`

y los invariantes:

`tests/ONTOLOGICAL_DISCRIMINATOR_METAMORPHIC_INVARIANTS.md`.

Se distinguen dos oráculos:

- `FULL_OUTPUT_IDENTITY`: la salida completa debe ser idéntica;
- `SEMANTIC_DECISION_IDENTITY`: pueden cambiar orden o metadatos no decisorios, pero no exclusiones confirmatorias, supervivientes, identificabilidad, estado epistemológico, clasificación ni falsa especificidad.

La suite cubre MR01–MR15: permutación de observaciones, inversión de pares, idempotencia, cambio de notas, normalización de modo, ruido L1/L2/NOT_EVALUABLE, orden de modelos, representación Mapping/dataclass, alias de discriminador, multiplicidad de raíces concordantes y determinismo repetido.

Durante esta fase se detectó y corrigió una dependencia indebida de `pair_coverage` respecto de la orientación textual del par. Ahora `A_vs_B` y `B_vs_A` son equivalentes; si ambas orientaciones aparecen con valores incompatibles, la entrada se rechaza.

Superar estas relaciones prueba invariancia lógica del software. No constituye validación externa ni promoción ontológica.

## Integración vigente con M21

M21 conserva el IDD sobre atribuciones estructurales AF/KA/AG/LG y añade, de forma opcional, una subcapa ontológica independiente.

La arquitectura adoptada es:

`M21 IDD histórico -> pairwise_idd`

y, cuando existe entrada explícita:

`M21 -> m21_ontology_adapter -> discriminate_ontology -> ontological_discrimination`.

El IDD no se transmite al motor ontológico como observable ni como score.

La integración está documentada en:

`docs/M21_ONTOLOGICAL_INTEGRATION.md`.

## Próximo paso

El Paso 13 formalizó la independencia de la astrología como posible fuente de observables discriminantes. Ninguna firma astrológica podrá adquirir función ontológica confirmatoria sin validación discriminante independiente, controles negativos, deduplicación de raíces y prueba fuera de muestra.
