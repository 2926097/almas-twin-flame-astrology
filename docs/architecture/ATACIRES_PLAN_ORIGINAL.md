# Atacires → ALMAS Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrar las capacidades útiles de `Atacires-mcp` en ALMAS como motor temporal modular, reproducible y desacoplado, preservando la autoridad canónica de ALMAS, sus invariantes metodológicas y la reversibilidad total del cambio.

**Architecture:** Se adopta un diseño híbrido: `atacires_core` se ejecuta in-process y consume datos canónicos de ALMAS; M26 recibe señales temporales normalizadas; MCP queda como fachada externa opcional y Swiss Ephemeris como backend opcional sometido a gate jurídico-técnico. La integración se realiza técnica por técnica, comenzando por ciclos uniformes, y nunca permite que temporalidad cree evidencia estructural u ontología.

**Tech Stack:** Python 3.10/3.12, pytest, typing/Protocol, Pydantic donde ya sea patrón del repositorio, Moira/JPL como backend astronómico primario, `pyswisseph` opcional, MCP 2.x opcional, GitHub Actions.

**Spec:** `docs/architecture/ATACIRES_ALMAS_DIRECTRICES.md`

## Global Constraints

- ALMAS conserva la autoridad canónica sobre natal, evidencia, scoring, ontología y reporting.
- Moira/JPL permanece como backend astronómico productivo por defecto.
- Swiss Ephemeris no será dependencia obligatoria y requiere gate jurídico-técnico.
- Atacires sólo produce directamente dato calculado y técnica; interpretación/doctrina/hipótesis pertenecen a capas superiores.
- Ninguna señal temporal puede crear una raíz estructural ni modificar índices productivos por sí sola.
- Todo cálculo nuevo debe registrar provenance, versión, parámetros, backend y fingerprints suficientes para reproducibilidad.
- No se admiten dialectos internos paralelos de schema; todo output Atacires se normaliza una vez al canonical ALMAS.
- La feature desactivada debe producir exactamente el comportamiento previo de ALMAS.
- Cada técnica se integra por TDD, golden cases, regresión, invariancia y rollback verificable.
- No se migra MCP, backend astronómico y semántica matemática en el mismo cambio.
- YAGNI: no incorporar todavía retornos, direcciones primarias, reporting Atacires ni geocodificación externa salvo que una tarea posterior lo justifique.

## Review Focus

- Hora natal incompleta o incierta: el sistema debe degradar a `NOT_EVALUABLE` o ejecutar robustez explícita, nunca asumir precisión.
- Diferencias de schema (`Sun`/`SUN`, `longitude_deg`/`longitude`): deben fallar en el adaptador, no propagarse silenciosamente.
- Doble backend astronómico: divergencias Moira/Swiss deben quedar documentadas y jamás resolverse mediante fallback implícito.
- Activaciones huérfanas: una señal temporal sin raíz estructural válida debe quedar como observación no vinculada y no afectar scoring.
- Feature flag desactivado: el canonical completo debe ser byte-equivalente o semánticamente idéntico al baseline acordado.

---

## File Structure

### Crear

- `docs/architecture/ATACIRES_ALMAS_DIRECTRICES.md` — contrato rector de integración.
- `src/almas_tfa/atacires/__init__.py` — API pública interna del subpaquete.
- `src/almas_tfa/atacires/models.py` — modelos tipados del core temporal.
- `src/almas_tfa/atacires/engine.py` — motor determinista migrado desde Atacires.
- `src/almas_tfa/atacires/provenance.py` — fingerprints y provenance técnico.
- `src/almas_tfa/atacires/adapters.py` — normalización canonical ALMAS ↔ Atacires.
- `src/almas_tfa/atacires/temporal_signal.py` — construcción de `TemporalSignal` canónico.
- `src/almas_tfa/atacires/providers.py` — `EphemerisProvider` y contratos opcionales.
- `src/almas_tfa/integrations/atacires_temporal.py` — integración con M26.
- `tests/atacires/test_engine.py` — regresión del motor puro.
- `tests/atacires/test_adapters.py` — contratos de schema.
- `tests/atacires/test_provenance.py` — reproducibilidad y fingerprints.
- `tests/atacires/test_temporal_signal.py` — semántica de la señal temporal.
- `tests/integration/test_m26_atacires.py` — integración M26.
- `tests/integration/test_atacires_structural_invariance.py` — firewall metodológico.
- `tests/golden/atacires/` — fixtures aprobados y hashes.

### Modificar

- `pyproject.toml` — empaquetado y extras opcionales, si la estructura vigente lo requiere.
- módulo/registro real de handlers M26 — registrar capacidad Atacires detrás de flag.
- esquema canónico temporal vigente — añadir campos mínimos sólo si faltan.
- workflow CI vigente — añadir shard/gate Atacires.
- documentación de arquitectura y validation status — reflejar capacidad experimental/canónica.

### No modificar en la primera iteración

- scoring productivo;
- pesos de índices;
- ontología productiva;
- backend Moira/JPL por defecto;
- reporting canónico fuera de los campos temporales aditivos;
- MCP externo actual, salvo preparación documental para fase posterior.

---

### Task 1: Congelar baseline y contrato de integración

**Files:**
- Create: `docs/architecture/ATACIRES_ALMAS_DIRECTRICES.md`
- Create: `docs/architecture/ATACIRES_ALMAS_BASELINE.md`
- Test: `tests/integration/test_atacires_feature_off_baseline.py`

**Interfaces:**
- Consumes: estado actual de ALMAS y snapshot aprobado de Atacires-mcp.
- Produces: SHAs congelados, comandos de regresión, hashes/golden baseline y contrato de feature-off.

- [ ] **Step 1: Escribir el test de baseline con Atacires desactivado**

Crear `test_atacires_feature_off_preserves_canonical_baseline()` y comparar los campos canónicos estructurales contra el fixture baseline acordado.

- [ ] **Step 2: Ejecutar el test y verificar que falla por falta del fixture/flag**

Run: `pytest tests/integration/test_atacires_feature_off_baseline.py -v`
Expected: FAIL por fixture o flag aún no definidos.

- [ ] **Step 3: Documentar snapshot y baseline**

Registrar SHA de ALMAS, SHA de Atacires, versión Python, comandos de suite, número de tests, fingerprints de fixtures y variables de entorno relevantes.

- [ ] **Step 4: Añadir configuración neutral del feature flag**

Definir `ALMAS_TEMPORAL_ATACIRES_ENABLED=false` con default falso sin alterar ejecución existente.

- [ ] **Step 5: Ejecutar regresión histórica completa**

Run: comando oficial de regresión ALMAS.
Expected: PASS completo y canonical baseline preservado.

- [ ] **Step 6: Commit**

```bash
git add docs/architecture tests/integration

git commit -m "chore: freeze atacires integration baseline"
```

### Task 2: Extraer el motor determinista Atacires como paquete interno

**Files:**
- Create: `src/almas_tfa/atacires/__init__.py`
- Create: `src/almas_tfa/atacires/models.py`
- Create: `src/almas_tfa/atacires/engine.py`
- Test: `tests/atacires/test_engine.py`

**Interfaces:**
- Consumes: algoritmos deterministas de `Atacires-mcp` que no requieren Swiss/MCP/HTTP.
- Produces: `calculate_uniform_cycle(request: UniformCycleRequest) -> UniformCycleResult`.

- [ ] **Step 1: Portar primero los tests del motor original**

Preservar casos de normalización angular, wrap 0/360, aspectos, dirección directa/conversa, DST/fold, límites y máximo de eventos.

- [ ] **Step 2: Ejecutar tests y verificar fallo por módulo inexistente**

Run: `pytest tests/atacires/test_engine.py -v`
Expected: FAIL por imports inexistentes.

- [ ] **Step 3: Crear modelos tipados mínimos**

Definir `UniformCycleRequest`, `TemporalEvent` y `UniformCycleResult` sin dependencias de Swiss ni MCP.

- [ ] **Step 4: Migrar algoritmo sin cambiar semántica**

Implementar `calculate_uniform_cycle(...)` preservando resultados del snapshot Atacires congelado.

- [ ] **Step 5: Ejecutar tests del motor**

Run: `pytest tests/atacires/test_engine.py -v`
Expected: PASS completo.

- [ ] **Step 6: Comparar contra golden del repositorio Atacires**

Generar salida con el snapshot antiguo y el nuevo core para los mismos casos.
Expected: equivalencia exacta o diferencias justificadas y documentadas.

- [ ] **Step 7: Commit**

```bash
git add src/almas_tfa/atacires tests/atacires

git commit -m "feat: add deterministic atacires core"
```

### Task 3: Implementar provenance y fingerprints reproducibles

**Files:**
- Create: `src/almas_tfa/atacires/provenance.py`
- Test: `tests/atacires/test_provenance.py`

**Interfaces:**
- Consumes: request normalizado, versión del engine, source chart fingerprint.
- Produces: `build_atacires_provenance(...) -> AtaciresProvenance` y `fingerprint_payload(...) -> str`.

- [ ] **Step 1: Escribir tests de determinismo de fingerprint**

Afirmar que reordenar claves JSON no cambia el fingerprint y que cambiar un parámetro matemático sí lo cambia.

- [ ] **Step 2: Ejecutar y verificar fallo**

Run: `pytest tests/atacires/test_provenance.py -v`
Expected: FAIL por funciones inexistentes.

- [ ] **Step 3: Implementar canonical serialization + SHA-256**

Definir firma exacta `fingerprint_payload(payload: Mapping[str, Any]) -> str`.

- [ ] **Step 4: Implementar `AtaciresProvenance`**

Campos mínimos: `technique_id`, `technique_version`, `engine_revision`, `parameters`, `source_fingerprint`, `input_fingerprint`, `output_fingerprint`, `executed_at`, `warnings`.

- [ ] **Step 5: Ejecutar tests**

Run: `pytest tests/atacires/test_provenance.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/almas_tfa/atacires/provenance.py tests/atacires/test_provenance.py

git commit -m "feat: add atacires provenance fingerprints"
```

### Task 4: Crear adaptador único desde el canonical ALMAS

**Files:**
- Create: `src/almas_tfa/atacires/adapters.py`
- Test: `tests/atacires/test_adapters.py`

**Interfaces:**
- Consumes: carta natal canónica ALMAS.
- Produces: `extract_canonical_longitudes(chart: Mapping) -> dict[str, float]` y `build_uniform_cycle_request(...) -> UniformCycleRequest`.

- [ ] **Step 1: Escribir tests de mapping de cuerpos y ángulos**

Cubrir `SUN`, `MOON`, nodos y ángulos; rechazar longitudes NaN/infinito y claves ambiguas.

- [ ] **Step 2: Añadir test de source fingerprint obligatorio**

La construcción de request debe fallar si el chart no aporta provenance/fingerprint suficiente.

- [ ] **Step 3: Ejecutar tests y verificar fallo**

Run: `pytest tests/atacires/test_adapters.py -v`
Expected: FAIL por adaptador inexistente.

- [ ] **Step 4: Implementar adaptador explícito**

No introducir aliases globales; toda traducción queda localizada en este archivo.

- [ ] **Step 5: Ejecutar tests**

Run: `pytest tests/atacires/test_adapters.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/almas_tfa/atacires/adapters.py tests/atacires/test_adapters.py

git commit -m "feat: add canonical atacires adapter"
```

### Task 5: Definir `TemporalSignal` canónico para atacires

**Files:**
- Create: `src/almas_tfa/atacires/temporal_signal.py`
- Modify: schema temporal canónico existente sólo si faltan campos imprescindibles.
- Test: `tests/atacires/test_temporal_signal.py`

**Interfaces:**
- Consumes: `UniformCycleResult` + provenance + root/dependency metadata.
- Produces: `to_temporal_signals(...) -> list[TemporalSignal]`.

- [ ] **Step 1: Escribir test de señal vinculada**

La señal debe contener `root_id`, `dependency_group_id`, `technique_family`, `activation_time`, `orb/separation`, `provenance` y `status`.

- [ ] **Step 2: Escribir test de señal huérfana**

Sin `root_id` válido, la señal se conserva como observación temporal y no obtiene capacidad de scoring.

- [ ] **Step 3: Ejecutar tests y verificar fallo**

Run: `pytest tests/atacires/test_temporal_signal.py -v`
Expected: FAIL.

- [ ] **Step 4: Implementar conversión**

No modificar todavía ningún índice ni pilar productivo.

- [ ] **Step 5: Ejecutar tests**

Run: `pytest tests/atacires/test_temporal_signal.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/almas_tfa/atacires/temporal_signal.py tests/atacires/test_temporal_signal.py

git commit -m "feat: model atacires temporal signals"
```

### Task 6: Integrar Atacires en M26 detrás de feature flag

**Files:**
- Create: `src/almas_tfa/integrations/atacires_temporal.py`
- Modify: registro/handler M26 real.
- Test: `tests/integration/test_m26_atacires.py`

**Interfaces:**
- Consumes: canonical natal, roots estructurales preexistentes y configuración temporal.
- Produces: señales temporales aditivas dentro de M26.

- [ ] **Step 1: Escribir test con flag desactivado**

Afirmar que M26 produce exactamente la salida anterior.

- [ ] **Step 2: Escribir test con flag activado**

Afirmar que sólo se añade la sección/señales Atacires esperadas.

- [ ] **Step 3: Escribir test `NOT_EVALUABLE`**

Cuando falten datos esenciales, M26 debe registrar estado no evaluable sin fallback implícito.

- [ ] **Step 4: Ejecutar tests y verificar fallo**

Run: `pytest tests/integration/test_m26_atacires.py -v`
Expected: FAIL.

- [ ] **Step 5: Implementar `AtaciresTemporalAdapter`**

Firma propuesta: `run_atacires_temporal(context: AnalysisContext, config: AtaciresConfig) -> AtaciresTemporalResult`.

- [ ] **Step 6: Registrar handler en M26 sólo bajo flag**

No tocar M03–M25 ni scoring.

- [ ] **Step 7: Ejecutar tests de integración**

Run: `pytest tests/integration/test_m26_atacires.py -v`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add src/almas_tfa/integrations tests/integration/test_m26_atacires.py

git commit -m "feat: integrate atacires into M26 behind flag"
```

### Task 7: Blindar la invariancia estructural y ontológica

**Files:**
- Create: `tests/integration/test_atacires_structural_invariance.py`

**Interfaces:**
- Consumes: pipeline completo con feature OFF y ON.
- Produces: gate automático contra contaminación estructural.

- [ ] **Step 1: Escribir test de igualdad de evidencia estructural**

Comparar grafo/raíces antes y después.

- [ ] **Step 2: Escribir test de igualdad de índices productivos**

Comparar IEM, IDD, IRC, IAT, ICC, ICE y pilares productivos definidos en la versión vigente.

- [ ] **Step 3: Escribir test de igualdad ontológica**

Comparar categorías y estados ontológicos.

- [ ] **Step 4: Ejecutar el test antes de cualquier wiring adicional**

Run: `pytest tests/integration/test_atacires_structural_invariance.py -v`
Expected: PASS una vez finalizada Task 6; cualquier cambio estructural = blocker.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_atacires_structural_invariance.py

git commit -m "test: enforce atacires structural invariance"
```

### Task 8: Importar golden cases y crear validación diferencial

**Files:**
- Create: `tests/golden/atacires/`
- Create: `tests/atacires/test_golden_atacires.py`
- Create: `tests/atacires/test_differential_atacires.py`

**Interfaces:**
- Consumes: fixtures Atacires originales y resultados del nuevo core.
- Produces: evidencia de equivalencia matemática y registro de divergencias.

- [ ] **Step 1: Copiar fixtures no sensibles con provenance de origen**

Cada fixture debe identificar SHA fuente y técnica.

- [ ] **Step 2: Escribir golden tests exactos para `UNIFORM_CYCLE`**

Comparar fechas, aspectos, separaciones y ordering.

- [ ] **Step 3: Escribir differential tests contra snapshot Atacires original**

Registrar toda divergencia; ninguna debe quedar como tolerancia implícita.

- [ ] **Step 4: Ejecutar suite golden/differential**

Run: `pytest tests/atacires/test_golden_atacires.py tests/atacires/test_differential_atacires.py -v`
Expected: PASS o divergencias explícitamente documentadas y aprobadas.

- [ ] **Step 5: Commit**

```bash
git add tests/golden/atacires tests/atacires

git commit -m "test: add atacires golden and differential validation"
```

### Task 9: Incorporar robustez por incertidumbre natal

**Files:**
- Create: `src/almas_tfa/atacires/robustness.py`
- Test: `tests/atacires/test_robustness.py`

**Interfaces:**
- Consumes: rango de hora natal o muestras Monte Carlo y función de cálculo temporal.
- Produces: `AtaciresRobustnessResult` con estabilidad, dispersión y estado evaluable.

- [ ] **Step 1: Escribir test de hora exacta**

Una hora exacta debe producir robustez trivial sin Monte Carlo innecesario.

- [ ] **Step 2: Escribir test de rango horario**

Perturbaciones que mueven significativamente la activación deben marcar el resultado como sensible.

- [ ] **Step 3: Escribir test de resultado estable**

Si la señal se mantiene dentro del criterio preregistrado, marcar `robust` sin traducirlo a probabilidad metafísica.

- [ ] **Step 4: Ejecutar tests y verificar fallo**

Run: `pytest tests/atacires/test_robustness.py -v`
Expected: FAIL.

- [ ] **Step 5: Implementar API de robustez reutilizando infraestructura Monte Carlo existente de ALMAS cuando exista**

No crear un segundo framework Monte Carlo si ALMAS ya dispone de uno canónico.

- [ ] **Step 6: Ejecutar tests**

Run: `pytest tests/atacires/test_robustness.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/almas_tfa/atacires/robustness.py tests/atacires/test_robustness.py

git commit -m "feat: add natal uncertainty robustness for atacires"
```

### Task 10: Añadir benchmarks y límites operativos

**Files:**
- Create: `benchmarks/atacires_benchmark.py`
- Create: `docs/validation/ATACIRES_PERFORMANCE.md`
- Test: `tests/atacires/test_limits.py`

**Interfaces:**
- Consumes: core temporal y fixtures pequeños/medios/máximos.
- Produces: p50/p95/p99, memoria y límites documentados.

- [ ] **Step 1: Escribir tests de límites duros**

Cubrir máximo de eventos, ventana temporal extrema, parámetros no finitos y inputs excesivos.

- [ ] **Step 2: Ejecutar tests**

Run: `pytest tests/atacires/test_limits.py -v`
Expected: PASS con rechazo fail-closed.

- [ ] **Step 3: Ejecutar benchmark baseline**

Medir core puro separado de cualquier backend astronómico.

- [ ] **Step 4: Documentar presupuesto de rendimiento**

El camino ALMAS preexistente no podrá degradar p95 >20 % por la mera presencia de Atacires desactivado.

- [ ] **Step 5: Commit**

```bash
git add benchmarks docs/validation tests/atacires/test_limits.py

git commit -m "perf: baseline atacires runtime limits"
```

### Task 11: Añadir gate de CI y supply-chain

**Files:**
- Modify: workflow CI vigente.
- Modify: `pyproject.toml` si procede.
- Create: `docs/validation/ATACIRES_VALIDATION_STATUS.md`

**Interfaces:**
- Consumes: suites anteriores.
- Produces: gate reproducible requerido para merge/release.

- [ ] **Step 1: Añadir shard `atacires-core`**

Ejecutar unit, contract, golden e invariance.

- [ ] **Step 2: Añadir matriz Python vigente de ALMAS**

El core debe pasar en las versiones soportadas por ALMAS; no reducir soporte a 3.12 por comodidad.

- [ ] **Step 3: Añadir comprobación de artefactos/licencias aplicable**

Swiss debe estar ausente del conjunto obligatorio salvo decisión posterior.

- [ ] **Step 4: Ejecutar CI local/equivalente y workflow remoto**

Expected: todos los required checks PASS.

- [ ] **Step 5: Commit**

```bash
git add .github pyproject.toml docs/validation

git commit -m "ci: gate atacires integration"
```

### Task 12: Preparar `EphemerisProvider` sin activar Swiss

**Files:**
- Create: `src/almas_tfa/atacires/providers.py`
- Test: `tests/atacires/test_providers.py`

**Interfaces:**
- Consumes: técnicas futuras que necesitan efemérides.
- Produces: `EphemerisProvider` protocol desacoplado de librería concreta.

- [ ] **Step 1: Escribir contract test con fake provider**

La técnica dependiente debe funcionar contra un fake determinista sin importar Swiss.

- [ ] **Step 2: Escribir test de provider ausente**

Debe producir error tipado/`NOT_EVALUABLE`, nunca fallback.

- [ ] **Step 3: Ejecutar tests y verificar fallo**

Run: `pytest tests/atacires/test_providers.py -v`
Expected: FAIL.

- [ ] **Step 4: Definir `EphemerisProvider` protocol**

Incluir identificador, versión y método(s) mínimos requeridos por técnicas futuras.

- [ ] **Step 5: Ejecutar tests**

Run: `pytest tests/atacires/test_providers.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/almas_tfa/atacires/providers.py tests/atacires/test_providers.py

git commit -m "refactor: define ephemeris provider boundary"
```

### Task 13: Reconciliar técnicas existentes antes de ampliar Atacires

**Files:**
- Create: `docs/architecture/ATACIRES_TECHNIQUE_MATRIX.md`
- Test: none, documentación/gate de diseño.

**Interfaces:**
- Consumes: catálogo de técnicas ALMAS y Atacires.
- Produces: decisión `AUTHORITATIVE`, `DIFFERENTIAL_ONLY`, `NEW_CAPABILITY`, `DEFERRED` por técnica.

- [ ] **Step 1: Inventariar técnicas solapadas**

Como mínimo: retornos, progresiones secundarias, arco solar, direcciones primarias y búsquedas de contactos.

- [ ] **Step 2: Clasificar equivalencia matemática**

No asumir equivalencia por nombre.

- [ ] **Step 3: Designar autoridad por técnica**

Los retornos no se migran hasta reconciliarlos con RRA.

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/ATACIRES_TECHNIQUE_MATRIX.md

git commit -m "docs: reconcile atacires technique ownership"
```

### Task 14: Migrar segunda técnica sólo después del gate del core

**Files:**
- Determinar a partir de `ATACIRES_TECHNIQUE_MATRIX.md`.
- Test: suite específica de la técnica elegida.

**Interfaces:**
- Consumes: `EphemerisProvider`, canonical ALMAS, provenance y `TemporalSignal`.
- Produces: nueva técnica temporal sin duplicar infraestructura.

- [ ] **Step 1: Elegir una sola técnica con estado `NEW_CAPABILITY` o autoridad aprobada**

Prioridad recomendada: búsqueda de contactos temporales, después progresiones secundarias y arco solar.

- [ ] **Step 2: Escribir golden/contract/invariance tests antes de portar código**

- [ ] **Step 3: Implementar la técnica contra interfaces existentes**

- [ ] **Step 4: Ejecutar regresión y robustness aplicable**

- [ ] **Step 5: Commit independiente**

Mensaje: `feat: add <technique> temporal capability`.

### Task 15: Mantener MCP como fachada opcional y migrarlo sólo después

**Files:**
- Create/Modify: ubicación MCP que siga el patrón vigente del repositorio.
- Test: contract tests MCP.

**Interfaces:**
- Consumes: el mismo `almas_tfa.atacires` core.
- Produces: tools MCP sin duplicar cálculo.

- [ ] **Step 1: Congelar contrato MCP actual**

Documentar tools y schemas actuales antes de migrar.

- [ ] **Step 2: Crear contract tests contra el core integrado**

- [ ] **Step 3: Migrar MCP a 2.x en PR/commit separado**

No cambiar matemáticas en esta tarea.

- [ ] **Step 4: Verificar auth/host/origin y stateless behavior**

- [ ] **Step 5: Commit**

Mensaje: `feat: expose integrated atacires core over MCP v2`.

### Task 16: Evaluar Swiss como extra opcional, no como requisito

**Files:**
- Modify: `pyproject.toml` extras.
- Create: `src/almas_tfa/integrations/atacires_swiss.py` sólo si el gate jurídico se aprueba.
- Test: `tests/atacires/test_swiss_optional.py`.

**Interfaces:**
- Consumes: `EphemerisProvider`.
- Produces: provider Swiss opcional.

- [ ] **Step 1: Registrar decisión de licencia**

Sin aprobación expresa, marcar la tarea `DEFERRED` y no añadir dependencia.

- [ ] **Step 2: Si se aprueba, escribir contract tests del provider**

- [ ] **Step 3: Implementar provider opcional**

- [ ] **Step 4: Ejecutar differential tests Moira/JPL ↔ Swiss**

- [ ] **Step 5: Confirmar que Moira/JPL sigue siendo default**

- [ ] **Step 6: Commit separado**

Mensaje: `feat: add optional swiss ephemeris provider`.

### Task 17: Validación final, shadow mode y release candidate

**Files:**
- Modify: `docs/validation/ATACIRES_VALIDATION_STATUS.md`
- Modify: release/validation docs vigentes.

**Interfaces:**
- Consumes: todas las tareas anteriores.
- Produces: decisión GO/NO-GO verificable.

- [ ] **Step 1: Ejecutar regresión histórica completa**

Expected: 100 % PASS.

- [ ] **Step 2: Ejecutar suite Atacires completa**

Expected: 100 % PASS.

- [ ] **Step 3: Ejecutar golden + differential + invariance + robustness**

Expected: sin blockers.

- [ ] **Step 4: Ejecutar shadow mode sobre casos representativos**

Comparar resultados sin hacerlos productivos.

- [ ] **Step 5: Verificar rollback**

Desactivar flag y demostrar vuelta al baseline sin migraciones destructivas.

- [ ] **Step 6: Emitir acta de aceptación**

Debe evaluar literalmente:

```text
historical_regression_pass
atacires_golden_pass
canonical_contract_pass
provenance_complete
structural_invariance_pass
license_gate_pass
security_gate_pass
rollback_verified
```

- [ ] **Step 7: Commit**

```bash
git add docs/validation

git commit -m "docs: certify atacires integration release gate"
```

---

## Roadmap por prioridad

**P0 — obligatoria antes de integración visible:** Tasks 1–8 y 11.

**P1 — robustez y extensibilidad:** Tasks 9, 10, 12 y 13.

**P2 — ampliación funcional:** Task 14 técnica por técnica.

**P3 — interfaces externas y backend alternativo:** Tasks 15 y 16.

**Release:** Task 17.

## Criterios de rollback

Rollback inmediato si ocurre cualquiera de los siguientes eventos:

- regresión de la suite histórica;
- cambio no explicado en índices/ontología;
- divergencia golden no aprobada;
- provenance incompleta;
- licencia Swiss no resuelta y Swiss aparece en dependencia obligatoria;
- degradación de rendimiento preexistente >20 % p95 atribuible a la integración;
- imposibilidad de desactivar la feature sin migración destructiva.

## Qué no hacer durante la ejecución

- No copiar `scripts/` completo dentro de ALMAS y arreglar imports después.
- No introducir llamadas HTTP/MCP para cálculos internos.
- No cambiar backend astronómico por defecto.
- No mezclar migración MCP con cambios matemáticos.
- No usar Atacires como evidencia ontológica independiente.
- No tocar pesos, thresholds o índices productivos.
- No integrar retornos antes de reconciliar RRA.
- No asumir que dos técnicas con el mismo nombre son matemáticamente equivalentes.
- No hacer geocodificación pública automática con datos natales completos.

## Resultado esperado al finalizar

ALMAS dispondrá de un motor Atacires interno, reproducible y desacoplado, inicialmente centrado en ciclos uniformes y activaciones temporales, integrado en M26 y blindado contra contaminación estructural. MCP seguirá siendo una interfaz opcional, Swiss un backend opcional y la ampliación a nuevas técnicas se hará una por una mediante los mismos contratos, tests y gates.
