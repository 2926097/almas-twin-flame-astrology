# Evolución ALMAS 1.22.0 · cierre matemático posterior a 1.21

**Fecha:** 28 de septiembre de 2026  
**Baseline congelada:** ALMAS 1.21.0 · commit `88623bbec1bcb9e8d7fd621235e6c7ee6996094b`  
**Clase epistemológica:** E · política/hipótesis cuantitativa del proyecto.

## 1. Objeto

ALMAS 1.22.0 resuelve las tres líneas matemáticas que quedaron deliberadamente fuera del saneamiento 1.21.0:

1. dependencia entre raíces independientes y motivos derivados PX/PS;
2. dependencia entre componentes de IRC;
3. ausencia de una fórmula autónoma de ICE.

La release no presenta estas reglas como doctrina metafísica ni como validación científica de las ontologías. Tampoco activa PX v3: el registro de candidatos y el holdout externo real siguen gobernados por los firewalls S6–S9 y V1–V5.

## 2. PX/PS y Shapley V3

### Problema

En 1.21, M18 declaraba correctamente que un motivo semántico era una feature derivada y no una raíz independiente, pero M21 podía introducir simultáneamente raíces y motivos como jugadores Shapley. Esa representación era semánticamente inconsistente: una interacción generada por raíces adquiría una segunda identidad de atribución.

### Resolución

`ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V3` define como único jugador una `INDEPENDENT_ROOT`.

Para cada coalición S de raíces:

1. se reconstruyen los pilares directos PA/PK/PE/PR/PT;
2. se vuelve a derivar el grafo de motivos sólo con las raíces de S;
3. PX/PS aparecen únicamente cuando la coalición satisface sus reglas de recurrencia;
4. se calcula `IEM_pre(S)`;
5. Shapley distribuye el valor marginal de las interacciones entre las raíces que las hacen posibles.

No se han inventado nuevos pesos PX/PS. El motivo conserva su función como interacción de orden superior, pero `motif_player_count=0`.

## 3. IRC por grupos de dependencia

### Problema

La media geométrica histórica trataba cada componente como una réplica independiente aunque algunas medidas procedieran de la misma cadena de perturbación.

### Resolución

Se define una capa de grupos de dependencia:

- `TIME_INPUT`: BIRTH_TIME;
- `STRUCTURAL_PERTURBATION`: ABLATION y PARAMETER_PERTURBATION;
- `DIAGNOSTIC_STABILITY`: IDD_STABILITY y VALIDATED_DISCRIMINATOR.

Para cada grupo j:

`G_j = min(R_i del grupo j)`.

Después:

`IRC = 100 × geometric_mean(G_j)`.

`R_min = min(R_i)` permanece sobre todos los componentes individuales.

La regla es conservadora: añadir otra métrica correlacionada no aumenta por sí mismo el número efectivo de votos.

## 4. ICE autónomo

### Problema

1.21 había endurecido el contrato fail-closed pero M20 todavía dependía de un ICE precomputado.

### Resolución

M20 mantiene compatibilidad con `PRECOMPUTED` y añade `AUTONOMOUS`.

ICE autónomo sólo puede calcularse cuando:

- `counterevidence_complete=true`;
- la lista evaluada puede estar vacía, pero su exhaustividad está declarada;
- toda contradicción retenida tiene `severity` finita en [0,1].

La dependencia se controla en dos niveles:

1. deduplicación por modelo + familia de dependencia + `contradiction_key`;
2. para la agregación, una misma `contradiction_key` presente en varias familias conserva sólo la severidad máxima.

Para claves semánticamente distintas:

`ICE_model = 100 × (1 - Π_k(1-s_k))`.

La fórmula es un operador de saturación acotado del proyecto, no una probabilidad. La contradicción esencial conserva un gate categórico separado.

ICE=0 sólo puede aparecer por declaración precomputada explícita o por evaluación completa sin contradicciones retenidas. La missingness continúa sin transformarse en cero.

## 5. Trazabilidad

Se añade `ALMAS_QUANTITATIVE_POLICY_MANIFEST_V2`. El canonical puede exponer:

- grupos y mínimos efectivos de IRC;
- procedencia `PRECOMPUTED/AUTONOMOUS/NOT_CALCULATED` de ICE;
- declaración de completitud;
- fórmula y detalle de derivación de ICE.

## 6. Compatibilidad y ruptura

1.22.0 es una evolución matemática pública y por ello no se introdujo silenciosamente en 1.21.0. El baseline 1.21 permanece históricamente reproducible.

Cambios deliberados:
- las atribuciones Shapley pueden cambiar;
- IDD puede cambiar porque cambian sus distribuciones de atribución;
- IRC puede cambiar cuando antes existían varios componentes correlacionados;
- IEM_final puede pasar a ser evaluable sin ICE precomputado si M20 dispone de una evaluación completa.

No cambian:
- fórmulas directas de PA/PK/PE/PR/PT;
- definición semántica PX/PS v2;
- fórmula estructural de IEM_pre;
- penalización IEM_final por ICE;
- thresholds del gate SUPPORTED;
- exclusión de rareza nula como probabilidad metafísica;
- firewalls de temporalidad, doctrina, viabilidad y consentimiento;
- exigencia de validación externa para PX v3 y L3.

## 7. Criterio de cierre

La release sólo puede fusionarse cuando la suite completa, el contrato público y el backend astronómico pasen sobre el mismo commit final de la PR. El resultado final se registra en `docs/RELEASE_AUDIT_1.22.0.md`.
