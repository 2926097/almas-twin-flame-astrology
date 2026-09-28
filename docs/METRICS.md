# Métricas

## IEM — Índice de Encaje del Modelo
Compatibilidad estructural con AF, KA, AG o LG. No es una probabilidad metafísica.

## IDD — Índice de Discriminación Diagnóstica
Separación distribucional entre arquitecturas de evidencia de modelos competidores. Alias histórico: IDE.

## IRC — Índice de Robustez de la Clasificación
Estabilidad frente a perturbación de hora natal, ablación, variación de parámetros y otras perturbaciones preregistradas.

## IAT — Índice de Activación Temporal
Fuerza de activaciones temporales independientes ancladas a raíces estructurales preexistentes. IAT no altera IEM.

## ICC — Índice de Cobertura Canónica
Completitud de los dominios analíticos requeridos. Los datos ausentes reducen cobertura o evaluabilidad; no son contradicciones.

## ICE — Índice de Contraevidencia Estructural
Índice de contraevidencia estructural aplicado a cada modelo AF/KA/AG/LG. Puede proceder de un mapa precomputado completo o de `ALMAS_ICE_AUTONOMOUS_V1` cuando la evaluación se declara completa. La ruta autónoma deduplica primero, conserva la severidad máxima dentro de cada familia de dependencia y agrega familias independientes con una función saturante. Una evaluación completa y vacía produce cero; missingness no. ICE es severidad estructural del modelo, no probabilidad metafísica.

Las fórmulas y gates normativos están definidos en `SKILL.md`.


## IEM 1.22 · corrección de dependencia

Cuando existe trazabilidad `pillar_source_roots`, CORE usa una media geométrica ponderada por independencia de procedencia. El peso de un pilar decrece con el solapamiento de sus raíces respecto a otros pilares del núcleo. SUPPORT cuenta únicamente la fracción de procedencia novedosa respecto al núcleo. PX/PS mantienen su significado, pero su condición derivada no añade una segunda raíz.

## IDD 1.22 · Shapley firmado

La función de valor es `IEM_PRE_DEPENDENCY_AWARE`. Las contribuciones Shapley negativas se conservan cuando representan redundancia o reducción marginal. Para Jensen–Shannon se transforman en canales `unidad::POS` y `unidad::NEG` por magnitud.

## IRC 1.22 · familias de dependencia

IRC se calcula sobre scores de familias de dependencia, no sobre una lista plana de componentes. Dentro de cada familia se usa media geométrica; después se agrega entre familias. `R_min` sigue usando todos los componentes individuales.
