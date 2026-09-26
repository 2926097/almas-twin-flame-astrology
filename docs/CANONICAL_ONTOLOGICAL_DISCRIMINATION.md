# Discriminación ontológica en canonical_analysis

## Finalidad

`canonical_analysis` puede transportar ahora, de forma opcional, la salida de M21:

`ontological_discrimination`.

La extensión es aditiva y mantiene `schema_version=1.0.0` porque los análisis anteriores siguen siendo válidos cuando el campo no existe.

## Contrato

`schemas/canonical-analysis.schema.json` referencia:

`schemas/ontological-discriminator-output.schema.json`.

El namespace conserva modelos candidatos, exclusiones confirmatorias, modelos supervivientes, matriz par a par, clases de equivalencia, identificabilidad, estado epistemológico, clasificación conservadora, conflictos, guardarraíl de falsa especificidad, reglas L2/L3, vista exploratoria cuando corresponda y `promotion_trace`.

## promotion_trace

Para cada observación L3 registrada conserva:

- `discriminator_id`;
- `promotion_ref`;
- `root_key`;
- par de modelos.

M21 valida la promoción antes de ejecutar el motor. El motor preserva esa referencia para que M30, M31 y la publicación puedan auditarla sin reconstruirla desde datos externos. Una señal L2 no crea `promotion_trace`.

## Gate M30

Si `ontological_discrimination` está presente, M30 valida semánticamente versión, unicidad y consistencia de modelos, partición supervivientes/exclusiones, identificabilidad, clasificación, guardarraíl de falsa especificidad y estructura de `promotion_trace`.

M30 bloquea, por ejemplo, un canonical que conserve varios modelos supervivientes pero nombre una categoría específica incompatible con esa partición. La ausencia del namespace no bloquea análisis históricos.

## Reporting M31

M31 sigue sin copiar valores analíticos. Sólo expone rutas hacia la verdad canónica:

- S01: `ontological_discrimination`;
- S03: `ontological_discrimination`;
- S06: `ontological_discrimination`;
- S08: `ontological_discrimination.promotion_trace`;
- S10: `ontological_discrimination`;
- S11: `ontological_discrimination.promotion_trace`.

Así, supervivientes, ambigüedad, identificabilidad y promociones permanecen disponibles para autoría posterior sin crear una segunda fuente analítica.

## Invariante

`M21 → canonical_analysis.ontological_discrimination → M30 → M31 routes`

debe conservar identidad y fingerprint.

M31 mantiene `canonical_values_embedded=false` y `canonical_values_mutated=false`.
