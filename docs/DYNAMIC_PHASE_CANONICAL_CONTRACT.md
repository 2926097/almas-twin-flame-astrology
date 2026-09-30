# Contrato canónico de fases dinámicas — ALMAS 1.22.0

`canonical_analysis` conserva ahora una superficie estable para describir fases y transiciones sin modificar los índices heredados. El ensamblaje inicial deja las fases y las cuatro capas temporales como `NOT_EVALUABLE`, las colecciones de transición y secuencia vacías, y la causalidad como `UNESTABLISHED`. Una colección vacía significa que no se ha incorporado evidencia; no significa que se haya observado ausencia de cambio.

| Campo canónico | Contenido y límite |
| --- | --- |
| `dynamic_phases` | Fase relacional y fases de cada actor, con estado explícito. |
| `actor_states` | Estado separado de A y B; no copia automáticamente la fase relacional. |
| `phase_transitions` | Transiciones justificadas por evidencia, sin inferencia automática. |
| `doctrinal_sequences` | Correspondencias con modelos doctrinales, separadas de los hechos. |
| `temporal_sequence_graph` | Relaciones explícitas EVENT → ACTIVATION → ROOT → PHASE, sólo con referencias de evidencia; no rellena nodos intermedios. |
| `temporal_layers` | Referencias separadas a `IAT_REL`, `IAT_A`, `IAT_B` e `IAT_CROSS`; no introduce nuevas fórmulas ni reemplaza el IAT heredado. |
| `root_recurrence` | Unidades de recurrencia por raíz; el campo declara que no crea score. |
| `angular_robustness` | Diagnóstico de retención de raíces angulares ante offsets preregistrados; no altera scores ni estados de fase. |
| `causal_firewall` | Causalidad no establecida y prohibición de que astrología cause o determine conducta. |
| `preregistered_predictions` | Referencias a registros prospectivos; no predicciones de decisiones o desenlaces. |

`counterevidence` mantiene su contrato previo y se presenta como ruta de evidencia para valorar fases. Los cambios son aditivos dentro de la versión 1.22.0: no recalculan cartas, raíces, pilares, IEM, IDD, IAT, ICC, IRC o ICE.
