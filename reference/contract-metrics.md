# ALMAS · Métricas del contrato preencarnatorio

## 1. Principio

Las métricas describen **fuerza, coherencia, especificidad y robustez de la arquitectura contractual**.

No son probabilidades metafísicas.

Un valor 85/100 significa alto encaje con los criterios operativos definidos, no “85% de probabilidad de contrato”.

## 2. Componentes normalizados

Todos los componentes internos se expresan en [0,1].

### ITP · Índice de Tarea Previa

Se calcula por persona.

Componentes:

- `preexistence_strength`: fuerza de la tarea en la arquitectura individual;
- `root_independence`: independencia de las raíces que la sostienen;
- `individual_ablation_survival`: supervivencia con pareja retirada y capas auxiliares;
- `birth_time_robustness`: estabilidad frente a incertidumbre horaria.

`ITP = 100 × GM(preexistence_strength, root_independence, individual_ablation_survival, birth_time_robustness)`

Si la hora no afecta materialmente, el componente se omite.

### IAA · Índice de Adecuación del Activador

Direccional: A_EN_B y B_EN_A.

Componentes:

- `configuration_specificity`;
- `semantic_fit`;
- `independent_recurrence`;
- `ablation_survival`;
- `robustness`.

`IAA = 100 × GM(componentes evaluables)`

C0_GENERIC impone techo 49.
C1_TARGETED impone techo 69.
C2/C3 pueden superar 70 si los gates pasan.

### IRCo · Índice de Reciprocidad Contractual

No mide sentimientos ni reciprocidad interpersonal.

Mide si las dos direcciones contractuales tienen arquitectura evaluable y complementaria.

`IRCo = 100 × GM(direction_A_to_B, direction_B_to_A, bilateral_alignment)`

Una relación puede tener IRCo alto y reciprocidad real actual parcial o no evaluable.

### ICCo · Índice de Coherencia del Campo Común

Componentes:

- `relchart_emergence`;
- `bilateral_root_consonance`;
- `common_task_specificity`;
- `semantic_alignment`.

Compuesta y Davison cuentan como una familia RELCHART.

### IVC · Índice de Coherencia Vertical Contractual

Mide trazabilidad C1→C8.

Para cada cláusula:

- C1 tarea previa;
- C2 motivo/causa;
- C3 rol;
- C4 activación;
- C5 prueba;
- C6 integración;
- C7 cumplimiento;
- C8 cierre/alternativa.

Cada eslabón: 1 completo, 0.5 degradado, 0 ausente/no trazado.

`IVC = 100 × sum(link_quality × link_weight) / sum(link_weight)`

Pesos por defecto:

- C1 1.5
- C2 1.5
- C3 1.0
- C4 1.0
- C5 1.0
- C6 1.0
- C7 1.0
- C8 0.5

C7/C8 pueden ser NOT_EVALUABLE en vínculos aún abiertos; eso reduce cobertura, no se convierte automáticamente en contradicción.

### IRCT · Índice de Robustez Contractual

Componentes:

- `ablation_stability`;
- `birth_time_stability`;
- `parameter_stability`;
- `dependency_control`;
- `causal_state_stability`.

`IRCT = 100 × GM(componentes evaluables)`

### ICE-C · Índice de Contraevidencia Contractual

Mide contradicciones explícitas.

No penaliza datos ausentes.

Ejemplos:

- tarea previa inexistente con buena cobertura;
- activador genérico incompatible con causa fuerte;
- cláusula que sólo aparece temporalmente;
- contradicción entre dirección y campo común;
- alternativa más simple con mejor explicación;
- fallo de ablación nuclear.

## 3. Cobertura contractual

`ICC-C` · Índice de Cobertura Contractual.

Dominios:

1. tareas previas;
2. causas direccionales;
3. roles;
4. tarea común;
5. cláusulas;
6. ablación;
7. robustez;
8. contraevidencia;
9. hechos para cumplimiento cuando proceda.

Calidad de dominio:
- 1 completa;
- 0.5 degradada;
- 0 no evaluable.

Los dominios futuros que todavía no pueden observarse se reportan por separado para no castigar un vínculo abierto como si contradijera el contrato.

## 4. IAP · Índice de Arquitectura Preencarnatoria

IAP resume la **arquitectura contractual funcional**.

No decide origen y no demuestra acuerdo bilateral literal.

Primero:

- `ITP_pair = GM(ITP_A, ITP_B)`
- `IAA_pair = GM(IAA_A_EN_B, IAA_B_EN_A)`

Luego:

`IAP_raw = WGM(ITP_pair=.20, IAA_pair=.20, IRCo=.15, ICCo=.15, IVC=.15, IRCT=.15)`

Ajustes:

`coverage_factor = 0.85 + 0.15 × ICC-C/100`

`counter_factor = 1 - 0.30 × ICE-C/100`

`IAP = clamp(IAP_raw × coverage_factor × counter_factor, 0, 100)`

## 5. Gates

### SUPPORTED · arquitectura contractual funcional

Requiere, como mínimo:

- IAP >= 80;
- ITP_A e ITP_B >= 60 cuando el modelo es bilateral;
- IAA_A_EN_B e IAA_B_EN_A >= 60 cuando se afirma bilateralidad;
- IVC >= 75;
- IRCT >= 70;
- ICC-C >= 75;
- al menos C2_MULTIROOT en una dirección y C1_TARGETED o superior en la otra;
- ninguna causa nuclear TEMPORAL_ONLY o SUPPORT_LAYER_DEPENDENT;
- no contradicción crítica.

Este SUPPORTED pertenece a **arquitectura contractual funcional R2**.

No eleva automáticamente R3_BILATERAL_AGREEMENT_MODEL a SUPPORTED.

### COMPATIBLE

IAP >= 60 y cadena contractual coherente, pero falta robustez, bilateralidad, cobertura o independencia suficiente.

### INSUFFICIENT

- IAP 40–59; o
- discriminadores competidores no resueltos; o
- cadena vertical incompleta; o
- dependencia excesiva de capas auxiliares.

### CONTRADICTED

Sólo con cobertura suficiente y contradicción material.

## 6. Regla de R3

Aunque IAP sea alto, `R3_BILATERAL_AGREEMENT_MODEL` no puede alcanzar SUPPORTED mientras el discriminador X_R2_FUNCTION_VS_R3_BILATERAL_AGREEMENT permanezca NOT_VALIDATED.

## 7. Presentación

En informes humanos expandir siempre el acrónimo:

- ITP — Índice de Tarea Previa;
- IAA — Índice de Adecuación del Activador;
- IRCo — Índice de Reciprocidad Contractual;
- ICCo — Índice de Coherencia del Campo Común;
- IVC — Índice de Coherencia Vertical Contractual;
- IRCT — Índice de Robustez Contractual;
- ICE-C — Índice de Contraevidencia Contractual;
- ICC-C — Índice de Cobertura Contractual;
- IAP — Índice de Arquitectura Preencarnatoria.
