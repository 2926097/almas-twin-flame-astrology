# Métricas

## IEM — Índice de Encaje del Modelo

Compatibilidad estructural con AF, KA, AG o LG. No es una probabilidad metafísica.

`IEM_pre` conserva la fórmula estructural histórica. `IEM_final` aplica ICE una sola vez:

`IEM_final = IEM_pre × (1 - 0.30 × ICE/100)`.

## IDD — Índice de Discriminación Diagnóstica

Separación distribucional entre arquitecturas de evidencia de modelos competidores. Alias histórico: IDE.

Desde ALMAS 1.22.0, la atribución Shapley usa exclusivamente raíces independientes como jugadores. PX/PS se recalculan dentro de cada coalición y actúan como interacciones derivadas; nunca reciben una segunda identidad de evidencia como jugador separado.

## IRC — Índice de Robustez de la Clasificación

Estabilidad frente a perturbación de hora natal, ablación, variación de parámetros y otras perturbaciones preregistradas.

Desde 1.22.0 los componentes correlacionados se agrupan antes de la agregación. Para cada grupo de dependencia:

`G_j = min(R_i del grupo j)`.

Después:

`IRC = 100 × geometric_mean(G_j)`.

`R_min = min(R_i)` sigue calculándose sobre todos los componentes individuales. El uso del mínimo intragrupo evita que medidas derivadas de una misma cadena de perturbación cuenten como réplicas independientes.

Grupos normativos actuales:
- `TIME_INPUT`: BIRTH_TIME.
- `STRUCTURAL_PERTURBATION`: ABLATION + PARAMETER_PERTURBATION.
- `DIAGNOSTIC_STABILITY`: IDD_STABILITY + VALIDATED_DISCRIMINATOR.

## IAT — Índice de Activación Temporal

Fuerza de activaciones temporales independientes ancladas a raíces estructurales preexistentes. IAT no altera IEM.

## ICC — Índice de Cobertura Canónica

Completitud de los dominios analíticos requeridos. Los datos ausentes reducen cobertura o evaluabilidad; no son contradicciones.

## ICE — Índice de Contraevidencia Estructural

Índice de contraevidencia estructural por modelo AF/KA/AG/LG. Puede proceder de un mapa precomputado completo o de M20.

En ALMAS 1.22.0 M20 puede derivar ICE autónomo sólo cuando se declara `counterevidence_complete=true`. Sin esa declaración, una lista parcial de contradicciones nunca se interpreta como exhaustiva y ICE permanece `NOT_CALCULATED`.

La deduplicación opera en dos niveles. Primero se conserva una sola contradicción por `modelo + dependency_family + contradiction_key`. Después, para el ICE autónomo, una misma `contradiction_key` presente en varias familias conserva únicamente su severidad máxima. Para las claves semánticamente distintas:

`ICE_model = 100 × (1 - Π_k (1 - s_k))`.

`s_k` es una severidad explícita en [0,1]. La expresión es un operador de saturación acotado definido por el proyecto, no una probabilidad. Las contradicciones esenciales conservan un gate categórico independiente.

La ausencia o incompletitud nunca se sustituye por cero. ICE=0 sólo es legítimo cuando existe un mapa precomputado que así lo declara o cuando una evaluación explícitamente completa no retiene contradicciones para el modelo.

Las fórmulas y gates normativos están definidos en `SKILL.md` y `manifests/quantitative-policy-manifest.json`.
