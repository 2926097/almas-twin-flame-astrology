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
Índice precomputado de contraevidencia estructural aplicado a cada modelo AF/KA/AG/LG mediante la fórmula congelada de IEM_final. M20 normaliza y deduplica contradicciones explícitas, pero no deriva una fórmula autónoma de ICE. Si se declara `ice_by_model`, el mapa debe contener los cuatro modelos completos con valores en [0,100]; si no se declara, ICE permanece `NOT_CALCULATED`/`NOT_EVALUABLE`. La ausencia o incompletitud nunca se sustituye por cero.

Las fórmulas y gates normativos están definidos en `SKILL.md`.
