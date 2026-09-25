# Gate de reportabilidad · M30

## 1. Finalidad

M30 decide si un `canonical_analysis` puede convertirse en informe sin corregir, completar ni reinterpretar sus valores.

La secuencia es:

`canonical_analysis → validación M30 → report_gate → M31`

M30 no es una etapa analítica. Es un firewall de integridad, trazabilidad y suficiencia formal.

## 2. Estados

### READY

El análisis es reportable como FULL sin degradaciones detectadas.

Requiere:

- `canonical_analysis` presente;
- campos canónicos obligatorios;
- `schema_version=1.0.0`;
- `analysis_mode` válido;
- coherencia interna de modelos;
- ninguna incidencia bloqueante;
- traza de ejecución disponible;
- ningún módulo previo `FAILED`, `NOT_EVALUABLE` o `SKIPPED`.

### PARTIAL

El análisis sigue siendo reportable, pero el informe debe declarar el alcance parcial.

Causas típicas:

- `analysis_mode=TARGETED`;
- `analysis_mode=TEMPORAL`;
- traza de ejecución no disponible;
- módulos previos `NOT_EVALUABLE`;
- módulos previos `SKIPPED`;
- métricas FULL como ICC/IRC/indices no declaradas.

PARTIAL no autoriza rellenar datos ausentes.

### BLOCKED

No debe generarse informe analítico.

Causas:

- ausencia de `canonical_analysis`;
- campos obligatorios ausentes;
- schema o modo inválidos;
- módulo previo `FAILED`;
- conflicto entre canonical raw y canonical snapshot;
- incoherencia interna de modelos;
- una afirmación positiva de modelo sin evidencia canónica.

## 3. Fuente del canonical

M30 distingue:

- `RAW_INPUT`;
- `CANONICAL_SNAPSHOT`;
- `CONFLICT`.

Si raw y snapshot existen y son distintos, M30 no elige uno: bloquea.

Si el canonical sólo llega por raw input, M30 realiza una copia profunda al namespace canónico, sin mutarlo.

## 4. Fingerprint

Todo canonical válido para el gate recibe un SHA-256 determinista sobre JSON ordenado:

`canonical_fingerprint`

El fingerprint permite que M31 y futuras fases de publicación indiquen exactamente qué objeto analítico alimentó el documento.

El fingerprint no certifica autoría ni firma digital.

## 5. Coherencia de modelos

En modo FULL deben existir:

- AF;
- KA;
- AG;
- LG.

Cada modelo declara:

- `iem`;
- `state`.

Reglas:

- `iem` debe estar entre 0 y 100 cuando es numérico;
- `NOT_EVALUABLE` exige `iem=null`;
- un estado evaluado distinto de `NOT_EVALUABLE` no puede tener `iem=null`;
- si existe al menos un modelo `SUPPORTED` o `COMPATIBLE`, la evidencia canónica no puede estar vacía.

M30 no comprueba si el modelo metafísico es verdadero. Comprueba que el objeto canónico sea internamente coherente.

## 6. Cobertura y robustez FULL

En modo FULL, la ausencia de:

- `coverage.ICC`;
- `robustness.IRC`;
- `indices`;

no bloquea necesariamente el informe, pero degrada el gate a PARTIAL.

Valores ICC/IRC fuera de 0–100 sí son bloqueantes.

## 7. Traza de ejecución

Cuando existen resultados M00–M29:

- `FAILED` → BLOCKED;
- `NOT_EVALUABLE` → PARTIAL;
- `SKIPPED` → PARTIAL;
- `NOT_APPLICABLE` → no degrada por sí mismo;
- `COMPLETED` → válido.

Si no existe traza, un canonical importado coherente puede ser reportable, pero sólo como PARTIAL.

## 8. No mutación

M30 fija:

`canonical_values_mutated=false`.

No:

- recalcula IEM;
- inventa ICC/IRC;
- rellena evidencia;
- cambia estados;
- elimina contraevidencia;
- añade doctrina;
- modifica ontología.

## 9. Contratos

Entrada:

`schemas/canonical-analysis.schema.json`

Salida:

`schemas/report-gate-output.schema.json`
