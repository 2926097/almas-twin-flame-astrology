# Auditoría de release ALMAS 1.22.0

**Fecha:** 28 de septiembre de 2026  
**PR:** #72  
**Baseline congelada:** ALMAS 1.21.0 · `88623bbec1bcb9e8d7fd621235e6c7ee6996094b`  
**Implementación cuantitativa validada:** `5c71949a7a476d8285d843d6c4e13ee6047c9936`  
**Estado:** **PASS · APTA PARA CIERRE DE RELEASE**.

## Alcance auditado

ALMAS 1.22.0 versiona las tres evoluciones matemáticas que quedaron deliberadamente fuera del saneamiento 1.21.0:

1. dependencia raíces↔motivos en PX/PS;
2. dependencia entre componentes de IRC;
3. fórmula autónoma de ICE.

La release no activa PX v3, no declara discriminadores L3, no convierte rareza o índices en probabilidades metafísicas y no altera los firewalls de temporalidad, doctrina, realidad, consentimiento o privacidad.

## Resultado matemático

### Shapley V3 · PX/PS

`ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V3` usa exclusivamente raíces independientes como jugadores. PX y PS se recalculan dentro de cada coalición y permanecen interacciones derivadas. Un motivo semántico no puede recibir una segunda cuota de evidencia como jugador separado.

La implementación precalcula firmas semánticas invariantes por raíz para evitar recomputación patológica. Esta optimización no cambia la función de valor ni las reglas de recurrencia.

### IRC agrupado

M25 agrupa componentes por dependencia antes de la media geométrica:

- `TIME_INPUT`;
- `STRUCTURAL_PERTURBATION`;
- `DIAGNOSTIC_STABILITY`.

Cada grupo aporta `G_j = min(R_i)` y después se calcula:

`IRC = 100 × geometric_mean(G_j)`.

`R_min` continúa siendo el mínimo de todos los componentes individuales.

### ICE autónomo

M20 conserva `PRECOMPUTED` y añade `AUTONOMOUS` sólo con `counterevidence_complete=true`. La deduplicación opera por familia y por `contradiction_key`; una misma contradicción observada en varias familias conserva su severidad máxima. Las contradicciones semánticamente distintas se agregan mediante:

`ICE_model = 100 × (1 - Π_k(1-s_k))`.

La fórmula es un operador de saturación acotado de clase E del proyecto, no una probabilidad. Sin declaración explícita de completitud, ICE permanece `NOT_CALCULATED`.

## Gate CI de la implementación

Sobre `5c71949a7a476d8285d843d6c4e13ee6047c9936`:

- **Python 3.10:** 596 tests en 88.677 s · PASS · 10 skipped.
- **Python 3.12:** 596 tests en 86.210 s · PASS · 10 skipped.
- **Contrato público:** PASS dentro de ambos jobs del núcleo y workflow independiente PASS.
- **Backend astronómico:** PASS.
- **Publicación DOCX:** PASS.
- **Publicación PDF:** PASS.

Runs de evidencia:

- Núcleo Python: `36412434923`;
- Contrato público: `36412434977`;
- Backend astronómico: `36412434854`;
- Publicación DOCX: `36412434849`;
- Publicación PDF: `36412435044`.

## Invariantes verificadas

- missingness no se convierte en ICE=0;
- un mapa ICE precomputado parcial se rechaza;
- ICE autónomo exige evaluación completa y severidades finitas;
- una contradicción semántica no se multiplica por aparecer en varias familias;
- las contradicciones esenciales conservan un gate categórico separado;
- motivos PX/PS no son jugadores Shapley;
- componentes correlacionados de IRC no reciben votos independientes;
- rareza nula permanece fuera de IRC;
- PX v3 sigue bloqueado sin validación externa;
- no existe ningún discriminador L3 real activado.

## Limitaciones que permanecen deliberadamente abiertas

La release valida coherencia matemática, implementación, contratos y regresiones internas. **No** constituye validación científica de la astrología ni de ontologías metafísicas. El holdout externo real continúa sin ejecutarse; por tanto PX v3 y cualquier promoción L3 permanecen inactivos.

## Conclusión

Las tres líneas matemáticas abiertas tras 1.21.0 quedan **implementadas, versionadas y cerradas en 1.22.0**. La sincronización documental posterior a este gate no modifica código cuantitativo y debe mantener todos los workflows verdes antes del merge de la PR #72.
