# ALMAS · Paso 16: dependencia C360 y arco solar

C360 (`TATACIR`) y arco solar (`TDIR`) conservan sus señales y nombres técnicos propios, pero el registro las sitúa en `SLOW_SYMBOLIC_DIRECTIONS`. `summarize_temporal_dependencies` agrupa ambas como una unidad de recurrencia cuando apuntan a la misma raíz; señales sin raíz no se agrupan entre sí.

El paso no crea puntuación ni cambia pesos, umbrales o el IAT vigente. El resultado explicita `score_created: false` y `legacy_iat_modified: false`; la agregación numérica queda para su bloque cuantitativo, con política preregistrada.
