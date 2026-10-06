# Directrices rectoras para integrar Atacires-mcp en ALMAS

## Propósito

Estas directrices constituyen el contrato arquitectónico y metodológico previo a cualquier integración de `2926097/Atacires-mcp` en `2926097/almas-twin-flame-astrology`. Su finalidad es preservar la reproducibilidad, trazabilidad, separación de responsabilidades y firewall ontológico de ALMAS mientras se incorporan capacidades temporales y geométricas de Atacires.

## Directriz 1 — Integración por capacidades, no fusión plana

Atacires no se incorporará como un bloque monolítico. El objetivo es absorber capacidades bien delimitadas dentro de ALMAS conservando fronteras explícitas entre motor temporal, backend astronómico, transporte MCP, geocodificación y reporting.

La integración inicial se limitará al núcleo determinista de atacires y a los adaptadores necesarios para consumir datos canónicos de ALMAS. MCP, HTTP, Render y Swiss Ephemeris no formarán parte obligatoria del núcleo productivo.

## Directriz 2 — ALMAS conserva la autoridad canónica

ALMAS seguirá siendo la autoridad única sobre:

- datos natales normalizados;
- esquema canónico de posiciones, ángulos, casas y nodos;
- grafo de evidencia;
- índices y pilares productivos;
- ontología relacional;
- estados `SUPPORTED`, `COMPATIBLE`, `INSUFFICIENT`, `CONTRADICTED` y `NOT_EVALUABLE`;
- ensamblado canónico y reporting.

Atacires será un proveedor de resultados técnicos temporales, no una segunda fuente de verdad estructural.

## Directriz 3 — Moira/JPL permanece como backend astronómico primario

La incorporación de Atacires no sustituirá automáticamente el backend astronómico vigente de ALMAS. Swiss Ephemeris quedará fuera de la dependencia obligatoria y sólo podrá habilitarse mediante extra/adaptador opcional después de resolver explícitamente licencia, compatibilidad y validación diferencial.

No se permitirá fallback silencioso entre backends astronómicos.

## Directriz 4 — Separación entre cálculo y significado

Todo resultado de Atacires deberá circular por capas diferenciadas:

A) `CALCULATED_DATA`: dato calculado y reproducible.
B) `TECHNIQUE`: técnica concreta, parámetros y versión.
C) `DOCTRINE`: doctrina explícita de una fuente, si existe.
D) `CONTEMPORARY_USE`: uso contemporáneo documentado.
E) `PROJECT_HYPOTHESIS`: hipótesis ALMAS.

El motor Atacires sólo podrá producir directamente A y B. C, D y E pertenecen a capas interpretativas/documentales posteriores.

## Directriz 5 — La temporalidad no crea ontología

Atacires se integrará como activación temporal de arquitectura ya existente. Ningún atacir, progresión, arco, retorno, dirección, estación o coincidencia temporal aislada podrá:

- crear una raíz estructural nueva;
- elevar un estado ontológico;
- modificar por sí solo IEM, IDD, IRC, IAT, ICC, ICE;
- crear o promover PA/PK/PE/PR/PX/PT/PS/PU;
- convertir rareza en probabilidad metafísica.

Toda señal temporal deberá enlazarse a una raíz o entidad estructural preexistente o quedar marcada como observación temporal no vinculada.

## Directriz 6 — Contrato canónico único

No coexistirán dialectos de datos internos. Los nombres y campos de Atacires deberán normalizarse una sola vez en un adaptador explícito hacia el canonical ALMAS.

Ejemplos de normalización:

- `Sun` → `SUN`
- `longitude_deg` → `longitude`
- `latitude_deg` → `latitude`
- `longitude_speed_deg_per_day` → `speed`
- nodos con `node_variant` y `nodal_axis_id`

No se admitirán aliases implícitos repartidos por distintos módulos.

## Directriz 7 — Provenance obligatorio y reproducible

Todo cálculo Atacires integrado deberá registrar, como mínimo:

- `technique_id`;
- `technique_version`;
- `engine_revision`;
- parámetros efectivos;
- backend astronómico y versión cuando aplique;
- efemérides/kernel/fingerprint cuando aplique;
- sistema zodiacal;
- sistema de casas cuando aplique;
- time scale/model;
- timezone IANA;
- coordenadas y procedencia de coordenadas;
- input fingerprint;
- output fingerprint;
- timestamp de ejecución;
- advertencias y degradaciones;
- incertidumbre natal relevante.

Mismo input + mismos fingerprints + misma versión debe producir el mismo resultado serializable, salvo técnicas expresamente no deterministas, que deberán declararlo.

## Directriz 8 — Control explícito de incertidumbre natal

Las técnicas sensibles a hora natal deberán declarar esa sensibilidad. Cuando proceda, la integración deberá permitir:

- hora exacta;
- rango horario;
- Monte Carlo sobre incertidumbre;
- estabilidad por perturbación;
- clasificación de resultados como robustos, sensibles o no evaluables.

La hora incierta no se resolverá mediante una falsa precisión.

## Directriz 9 — Independencia estadística y deduplicación

Las salidas de Atacires no se contarán automáticamente como evidencia independiente cuando deriven de la misma raíz astronómica o de la misma transformación matemática.

Cada señal deberá incluir `dependency_group_id`, `root_id` y `technique_family`, permitiendo deduplicación, recurrencia, ablación y análisis de robustez.

## Directriz 10 — Migración por técnica

Las técnicas se incorporarán individualmente, con su propio contrato, tests y criterios de aceptación. Orden recomendado:

1. `UNIFORM_CYCLE` / atacires deterministas;
2. búsqueda de contactos temporales;
3. progresiones secundarias;
4. arco solar;
5. retornos sólo tras reconciliación con RRA existente;
6. direcciones primarias únicamente si su definición matemática y alcance quedan formalmente cerrados.

No se habilitará una técnica sólo porque el código exista en Atacires.

## Directriz 11 — MCP es fachada, no dependencia interna

ALMAS no llamará al motor Atacires mediante red para su flujo interno ordinario. El motor se consumirá in-process mediante interfaces Python estables.

MCP podrá mantenerse como interfaz externa para agentes y clientes remotos, pero deberá consumir el mismo core interno que ALMAS. No existirán dos implementaciones del cálculo.

## Directriz 12 — Swiss Ephemeris es opcional y jurídicamente gated

`pyswisseph` no será dependencia obligatoria del paquete principal. Cualquier distribución o servicio que lo use deberá superar un gate jurídico-técnico previo relativo a su licencia.

Hasta entonces:

- Moira/JPL = autoridad primaria;
- Swiss = validación diferencial/compatibilidad opcional;
- ninguna funcionalidad productiva esencial dependerá exclusivamente de Swiss.

## Directriz 13 — Privacidad y geocodificación

La geocodificación externa no formará parte del cálculo canónico. Los datos natales completos no se enviarán a proveedores públicos de geocodificación.

La resolución de lugar deberá producir un objeto independiente con coordenadas, timezone, proveedor, versión/fuente y fingerprint. El cálculo consume ese objeto ya resuelto.

## Directriz 14 — Seguridad fail-closed

Ante datos insuficientes, inconsistentes o backend no disponible, la salida deberá ser `NOT_EVALUABLE` o error tipado; nunca se inferirán silenciosamente coordenadas, hora, timezone, backend o parámetros críticos.

## Directriz 15 — Feature flags y reversibilidad

La integración se desplegará de forma aditiva mediante feature flags independientes:

- `ALMAS_TEMPORAL_ATACIRES_ENABLED`
- `ALMAS_ATACIRES_MCP_ENABLED`
- `ALMAS_ASTRONOMY_BACKEND`

El rollback deberá poder desactivar Atacires sin migraciones destructivas ni pérdida de datos canónicos.

## Directriz 16 — TDD, regresión y golden cases antes de producción

Cada técnica nueva deberá entrar mediante TDD y disponer de:

- unit tests;
- contract tests;
- golden cases;
- regression tests;
- invariance tests;
- property/fuzz tests cuando proceda;
- benchmark reproducible;
- documentación de límites.

La suite histórica completa de ALMAS debe seguir pasando con Atacires desactivado.

## Directriz 17 — Pruebas de invariancia metodológica

Debe existir una prueba explícita que demuestre que activar Atacires altera únicamente la capa temporal y no cambia evidencia estructural, scoring ni ontología salvo que una futura especificación, separada y validada, lo autorice expresamente.

## Directriz 18 — Shadow mode antes de uso canónico

Toda técnica Atacires nueva entrará primero en `shadow mode`: se calcula, registra y compara, pero no afecta salidas productivas. Sólo tras superar golden, regresión, diferencial y robustez podrá promoverse a visible/canónica.

## Directriz 19 — Observabilidad sin datos sensibles

Las métricas operativas deben registrar latencia, errores, versión, backend, técnica y fingerprint, pero no fecha/hora/lugar natal completos ni información personal identificable.

## Directriz 20 — No duplicar capacidades existentes

Antes de integrar cualquier técnica deberá comprobarse si ALMAS ya posee una implementación equivalente. Si existe, se aplicará una de estas decisiones:

- mantener la implementación ALMAS como autoridad y usar Atacires como oracle diferencial;
- migrar de forma explícita a Atacires con golden equivalence;
- mantener ambas con nombres semánticos distintos cuando no sean matemáticamente equivalentes.

Nunca coexistirán dos implementaciones «canónicas» de la misma técnica sin una política de resolución.

## Directriz 21 — Versionado independiente de algoritmos

Las técnicas Atacires tendrán `engine_revision` o `technique_version` propia, separada del SemVer público de ALMAS. Cambios matemáticos deberán incrementar esa revisión y regenerar los golden fingerprints afectados.

## Directriz 22 — Criterio de aceptación global

La integración sólo podrá promoverse a comportamiento canónico si se cumple simultáneamente:

```text
ACCEPT =
  historical_regression_pass
  AND atacires_golden_pass
  AND canonical_contract_pass
  AND provenance_complete
  AND structural_invariance_pass
  AND license_gate_pass
  AND security_gate_pass
  AND rollback_verified
```

Si cualquiera de estas condiciones falla, la capacidad permanecerá experimental o desactivada.

## Directriz 23 — Lo que no debe implementarse todavía

Queda expresamente fuera del primer ciclo:

- reemplazo de Moira/JPL por Swiss;
- migración simultánea de MCP y semántica matemática;
- uso de atacires como evidencia ontológica independiente;
- modificación de índices productivos;
- unificación de retornos sin comparación contra RRA;
- geocodificación pública automática con datos personales;
- nuevas categorías metafísicas derivadas de temporalidad;
- optimizaciones prematuras antes de benchmarks;
- refactor global de ALMAS no necesario para esta integración.

## Decisión arquitectónica principal

La arquitectura objetivo será híbrida:

```text
ALMAS canonical natal (Moira/JPL)
        |
        v
Atacires Core in-process
        |
        v
TemporalSignal canonical
        |
        v
M26 temporal activation
        |
        v
M27 facts / M30 canonical / M31 reporting

MCP v2 (opcional) ---> mismo Atacires Core
Swiss (opcional) ---> EphemerisProvider alternativo
```

La integración inicial es, por tanto, una integración lógica y modular dentro del repositorio ALMAS, no una absorción indiscriminada del servicio Atacires-mcp.
