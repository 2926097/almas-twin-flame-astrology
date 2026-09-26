# Integración del discriminador ontológico en M21

## Estado

M21 conserva su función histórica de discriminación diagnóstica por IDD entre los modelos estructurales AF, KA, AG y LG.

A partir de la fase experimental del discriminador ontológico, M21 puede ejecutar además una subcapa independiente para:

- SOULMATE_MODEL;
- MONADIC_ORIGIN;
- SPLIT_SOUL;
- TWIN_FLAME_MODEL.

La integración no sustituye IDD y no convierte IDD en evidencia ontológica.

## Dos espacios de modelos

M21 trabaja ahora con dos espacios que no deben confundirse.

### Espacio estructural histórico

`AF / KA / AG / LG`

Salida:

`pairwise_idd`

Su función es medir la separación entre atribuciones estructurales de raíces mediante el IDD existente.

### Espacio ontológico diferencial

`SOULMATE_MODEL / MONADIC_ORIGIN / SPLIT_SOUL / TWIN_FLAME_MODEL`

Salida:

`ontological_discrimination`

Su función es mantener modelos supervivientes, equivalencias observacionales y estados de identificabilidad mediante discriminadores preregistrados.

No existe conversión automática:

`IDD alto -> ontología específica`.

## Entrada opcional

La subcapa se activa sólo si la entrada contiene:

`ontological_discriminator_input`

Schema:

`schemas/m21-ontological-discriminator-input.schema.json`

Campos admitidos:

- `observations`;
- `models`, opcional;
- `mode`, `CONFIRMATORY` o `EXPLORATORY`;
- `minimum_data_evaluable`;
- `pair_coverage`.

Si la clave no existe, M21 conserva el comportamiento histórico.

## Compatibilidad

Una ejecución antigua que sólo entregue `attributions` sigue produciendo:

`canonical_updates["pairwise_idd"]`

sin añadir `ontological_discrimination`.

También se conserva la forma histórica del `payload` cuando no se solicita la subcapa ontológica.

## Independencia operacional

El adaptador interno está en:

`src/almas_tfa/m21_ontology_adapter.py`

Este adaptador sólo normaliza la configuración y llama a:

`discriminate_ontology(...)`

No recibe como argumentos:

- IEM;
- IDD;
- IRC;
- ICE;
- score de intensidad;
- rareza de modelo nulo.

Por diseño, modificar el IDD manteniendo constantes las observaciones ontológicas no puede modificar la salida ontológica.

## Ejecución parcial

Las dos subcapas pueden evaluarse de manera independiente.

Si existen atribuciones IDD pero no entrada ontológica, M21 calcula sólo IDD.

Si existe entrada ontológica pero no atribuciones IDD, M21 puede completar la subcapa ontológica sin inventar `pairwise_idd`.

M21 sólo devuelve `NOT_EVALUABLE` cuando ninguna de las dos subcapas es evaluable.

## Autoridad registral de L3

M21 no acepta ya `L3_VALIDATED` como una etiqueta libre.

Antes de ejecutar el motor ontológico, consulta el registro canónico empaquetado mediante `validate_l3_observations(...)`.

Toda observación L3 debe aportar `promotion_ref`, y ese registro debe estar promovido a `VALIDATED_DISCRIMINATOR`, tener evidencia de validación completa, incluir el par solicitado en `validated_pairs` y aceptar la familia de `root_key` observada.

El registro productivo actual no contiene ninguna promoción L3, por lo que cualquier intento real de declarar L3 sin promoción previa es rechazado.

## L2 y L3

La integración conserva el firewall del motor autónomo:

`L2_EXPERIMENTAL !-> CONFIRMATORY_EXCLUSION`

Un resultado L2 puede aparecer en la vista exploratoria, pero un IDD elevado no puede promocionarlo.

Sólo un discriminador `L3_VALIDATED` puede participar en una exclusión confirmatoria.

Incluso entonces, M21 no eleva automáticamente el resultado a `SUPPORTED`.

## Namespaces canónicos

M21 puede reclamar dos namespaces independientes:

`pairwise_idd`

y

`ontological_discrimination`.

El segundo cumple:

`schemas/ontological-discriminator-output.schema.json`.

No se sobrescribe ningún namespace producido por M15-M20.

## Invariante de no interferencia

Debe cumplirse:

`ontology(O, IDD=0) = ontology(O, IDD=100)`

si las observaciones ontológicas `O` no cambian.

De forma recíproca, activar la subcapa ontológica no debe alterar el valor de `pairwise_idd`.

## Falsa especificidad

Si sobreviven:

`MONADIC_ORIGIN + SPLIT_SOUL + TWIN_FLAME_MODEL`

M21 conserva:

`SHARED_ORIGIN_UNDIFFERENTIATED / INSUFFICIENT`.

No usa AF/KA/AG/LG, ni un IDD alto entre AG y LG, para escoger entre esos modelos.

## Pruebas

`tests/test_m21_ontological_integration.py`

verifica:

- compatibilidad del M21 histórico;
- IDD=100 sin promoción de L2;
- ejecución ontológica sin IDD;
- invariancia de la ontología ante cambios IDD 0↔100;
- rechazo explícito de configuración inválida.

## Límite de esta fase

La integración en M21 hace ejecutable la separación metodológica, pero no crea ningún discriminador L3 nuevo.

El siguiente trabajo deberá conectar la robustez de discriminadores realmente validados con M25 sin permitir que señales L2 entren en el IRC como `VALIDATED_DISCRIMINATOR`.
