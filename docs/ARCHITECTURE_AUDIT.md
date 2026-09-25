# Auditoría de arquitectura del repositorio ALMAS

**Fecha:** 25 de septiembre de 2026  
**Repositorio:** `2926097/almas-twin-flame-astrology`  
**Rama base:** `main`  
**Commit auditado:** `8bdd478b69628cc669616de084c11f6226310328`  
**Versión pública:** `1.10.1`  
**Objeto de esta fase:** inventariar la arquitectura real, distinguir especificación de implementación, detectar redundancias y fijar la secuencia de modularización sin alterar fórmulas, pesos, umbrales, ontología ni discriminadores.

## 1. Conclusión ejecutiva

El repositorio ya dispone de una arquitectura modular formal y coherente a nivel normativo. La decisión vigente es **una única skill pública con módulos internos especializados**, no un conjunto de skills públicas versionadas de manera independiente.

Esta decisión está expresamente recogida en `README.md`, `docs/ARCHITECTURE.md`, `docs/MODULE_ARCHITECTURE.md` y `manifests/almas-module-manifest.json`. El módulo de contrato preencarnatorio conservado en `skills/almas-soul-contract/` es un punto de entrada especializado por compatibilidad histórica, pero hereda la versión pública de ALMAS y no constituye una segunda skill pública.

La principal brecha no es de diseño conceptual, sino de **grado de ejecución**. El repositorio contiene una especificación extensa, manifiestos, schemas, fixtures sintéticos, registros doctrinales y controles de invariantes, mientras que el núcleo Python ejecutable se limita actualmente a scoring determinista sobre pilares ya precomputados. No existe todavía un orquestador Python que ejecute materialmente el pipeline M00–M31 ni un motor astronómico que derive por sí mismo posiciones, aspectos, cartas relacionales, raíces, temporalidad y demás capas desde datos natales brutos.

Por tanto, la siguiente fase no debe consistir en fragmentar ALMAS en varias skills públicas. Debe consistir en **hacer ejecutable la modularidad ya definida**, conservando `VERSION` como único SemVer público.

## 2. Inventario del repositorio

El árbol auditado contiene **175 archivos** distribuidos en **15 directorios**.

| Área | Archivos |
|---|---:|
| `docs/` | 22 |
| `reference/` | 37 |
| `schemas/` | 30 |
| `manifests/` | 17 |
| `examples/` | 19 |
| `tests/` | 32 |
| `src/` | 4 |
| `skills/` | 3 |
| `.github/` | 2 |
| `scripts/` | 1 |
| `public_cases/` | 1 |

Por formato existen 87 archivos Markdown, 74 JSON, 7 Python, 2 workflows YAML, 1 TOML y otros archivos auxiliares.

El repositorio dispone de dos workflows activos: `Public contract` y `Python core`. Ambos concluyen correctamente sobre el commit auditado. Los fallos existentes en commits inmediatamente anteriores quedaron corregidos por la depuración integrada en `1.10.1`.

## 3. Arquitectura normativa vigente

`manifests/almas-module-manifest.json` declara nueve unidades arquitectónicas:

| ID | Módulo | Estado |
|---|---|---|
| M_ASTROLOGY | Astrología metafísica relacional | CORE |
| M_ONTOLOGY | Ontología relacional comparada | CORE |
| M_DOCTRINE | Doctrina, genealogía y fuentes | CORE |
| M_SOUL_CONTRACT | Contrato álmico preencarnatorio | CORE |
| M_ROLES | Roles preencarnatorios | SUBMODULE |
| M_CAUSALITY | Causa contractual | SUBMODULE |
| M_TEMPORAL | Temporalidad y cumplimiento | CORE |
| M_VALIDATION | Dependencia, ablación, robustez y contraevidencia | CORE |
| M_REPORTING | Informe canónico y hermenéutica | CORE |

El pipeline FULL está declarado por separado en `manifests/analysis-pipeline-manifest.json` y comprende **32 etapas, M00–M31**, desde manifest y calidad de datos hasta reporting. Esta separación es correcta: el manifiesto arquitectónico define responsabilidades; el manifiesto de pipeline define secuencia de ejecución.

La reconstrucción preencarnatoria posee además su propio pipeline especializado. No debe fusionarse con los otros dos manifiestos porque responde a una función diferente.

## 4. Clasificación funcional de los componentes

### CORE_EXECUTABLE

La implementación Python actualmente activa se concentra en:

- `src/almas_tfa/core.py`
- `src/almas_tfa/analysis.py`
- `src/almas_tfa/cli.py`
- `src/almas_tfa/__init__.py`

El núcleo implementa agregación de raíces en pilares, IEM, aplicación de ICE, gate de `SUPPORTED`, IDD mediante Jensen–Shannon y componentes básicos de IRC.

`analysis.py` consume pilares ya calculados y produce scoring AF/KA/AG/LG. La propia API declara expresamente que no calcula astronomía, aspectos, raíces, modelos nulos ni temporalidad.

### CORE_NORMATIVE

Se consideran normativos, pero no motores Python autónomos:

- `SKILL.md`
- `docs/ARCHITECTURE.md`
- `docs/MODULE_ARCHITECTURE.md`
- `docs/ONTOLOGY.md`
- `docs/METRICS.md`
- `docs/REPORTING.md`
- manifiestos de `manifests/`

Estos archivos describen reglas, responsabilidades, secuencias, límites inferenciales y contratos metodológicos.

### SPECIALIZED_INTERNAL_MODULE

`skills/almas-soul-contract/` constituye un módulo interno especializado. Su `SKILL.md` declara correctamente:

- `kind: internal_module`;
- `parent_skill: almas-twin-flame-astrology`;
- `independent_versioning: false`;
- `engine_revision: 1.9.0`.

Su archivo `VERSION` coincide actualmente con la raíz: `1.10.1`.

### SCHEMA_LAYER

`schemas/` contiene 30 contratos JSON. Esta capa ya cubre análisis canónico, ontología, contrato, temporalidad, libre albedrío, cláusulas, genealogía doctrinal, eventos documentales, validación y reconstrucción preencarnatoria.

### REFERENCE_AND_DOCTRINE

`reference/` contiene 37 archivos entre registros canónicos, matrices doctrinales, genealogías, motores diferenciales y documentación metodológica.

### VALIDATION

La validación está distribuida entre:

- 30 documentos de invariantes;
- 2 archivos Python de pruebas unitarias;
- `scripts/validate_public_contract.py`;
- 2 workflows GitHub Actions;
- fixtures sintéticos en `examples/`.

Según `VALIDATION_STATUS.md`, la suite ejecutable comprende 14 tests deterministas y el contrato público verifica adicionalmente coherencia de versiones, rutas, manifiestos, schemas, fuentes, genealogía, discriminadores, pipeline y reglas de publicación.

### REPORTING

La arquitectura de reporting está especificada documentalmente, pero no existe todavía un paquete Python equivalente a `report-engine`. El pipeline `canonical_analysis.json → report_document_model.json → documento → PDF` es normativo, no una implementación completa dentro de `src/`.

### LEGACY/HISTORY

Los documentos históricos están correctamente aislados en `docs/history/`. No se ha detectado en esta auditoría un componente activo que deba marcarse inmediatamente como `DEPRECATED`.

## 5. Brechas entre especificación e implementación

La brecha principal es que **M00–M31 está declarado, pero no existe todavía como grafo ejecutable de módulos Python**. El usuario puede seguir el protocolo mediante la skill y sus reglas, pero el paquete `almas_tfa` no orquesta cada etapa de forma autónoma.

No existe en el núcleo Python un motor astronómico que reciba fecha, hora y lugar y genere posiciones natales, casas, aspectos, declinaciones, antiscios, compuesta, Davison o dracónica. La CLI `almas-score` consume pilares precomputados.

Tampoco existe todavía un grafo de evidencia ejecutable que derive contactos, dependencia técnica, raíces independientes y deduplicación a partir de observaciones brutas. El scoring presupone que esta fase se ha resuelto aguas arriba.

La ontología multiaxial, los motores doctrinales, la reconstrucción preencarnatoria, el diferencial de origen, roles, tareas y cláusulas están muy desarrollados como especificación, schemas, registros e invariantes, pero gran parte de ellos no dispone todavía de un motor Python autónomo equivalente al núcleo IEM/IDD/IRC.

La capa de reporting tampoco dispone de implementación ejecutable propia.

## 6. Redundancias y solapamientos

No se recomienda eliminar `docs/ARCHITECTURE.md` ni `docs/MODULE_ARCHITECTURE.md` en esta fase. Existe solapamiento semántico, pero el manifiesto de mantenimiento establece que la fuente canónica arquitectónica es `manifests/almas-module-manifest.json`; los documentos deben permanecer como explicaciones derivadas, no como fuentes normativas competidoras.

El `VERSION` de `skills/almas-soul-contract/` es redundante desde una perspectiva estricta, pero actualmente tiene utilidad de compatibilidad. Debe mantenerse sincronizado automáticamente o mediante el validador y nunca adquirir SemVer independiente.

Se recomienda revisar semánticamente la declaración de `M_TEMPORAL`, cuyo `entrypoint` actual apunta a `manifests/preincarnation-pipeline-manifest.json`. Temporalidad y reconstrucción preencarnatoria están relacionadas, pero no son responsabilidades equivalentes. La referencia puede ser intencional; en cualquier caso merece una revisión antes de convertir el manifiesto en orquestación ejecutable.

No se han detectado duplicados manifiestos que justifiquen borrar archivos activos sin una revisión de dependencias.

## 7. Inconsistencia lingüística

El proyecto ha establecido que sus textos deben mantenerse en español. Sin embargo, persisten fragmentos sustanciales en inglés dentro de archivos vivos.

Ejemplos verificados:

- el front matter y varias secciones iniciales de `SKILL.md`;
- `docs/REPORTING.md`;
- `docs/METRICS.md`;
- descripciones y docstrings del paquete Python;
- mensajes de limitaciones producidos por `analysis.py`;
- descripción de la CLI.

Esto no afecta al cálculo, pero sí constituye una inconsistencia editorial y contractual del repositorio. Debe corregirse en una fase específica, preservando identificadores técnicos, nombres de clases, claves JSON y términos cuyo cambio rompería compatibilidad.

## 8. Estado de validación

Sobre el commit auditado:

- `Public contract`: **SUCCESS**.
- `Python core`: **SUCCESS**.
- el repositorio declara validación externa: **PREREGISTRATION READY**;
- holdout externo real: **NOT YET EXECUTED**.

Debe mantenerse la distinción entre coherencia interna de implementación y validación empírica externa. El sistema actual valida que las reglas publicadas sean consistentes con la implementación y los contratos, no la verdad empírica de las ontologías metafísicas.

## 9. Decisión arquitectónica resultante

La auditoría **no recomienda dividir ALMAS en múltiples skills públicas**.

La arquitectura objetivo debe conservar:

```text
ALMAS 1.x
│
├── SKILL.md                       ← skill pública única
├── manifests/                     ← arquitectura y pipelines
├── schemas/                       ← contratos de datos
├── reference/                     ← doctrina, fuentes y reglas
├── skills/
│   └── almas-soul-contract/       ← entrada interna especializada
├── src/almas_tfa/
│   ├── core.py                    ← scoring actual
│   ├── analysis.py
│   ├── cli.py
│   └── [módulos ejecutables futuros]
├── tests/
└── docs/
```

La modularización futura debe producir **módulos internos ejecutables**, no SemVer públicos separados.

## 10. Secuencia de implementación recomendada tras la auditoría

La siguiente fase debe transformar el diseño normativo en una arquitectura de ejecución. El orden recomendado es:

1. definir un contrato Python común para módulos y resultados;
2. crear un `orchestrator` que lea el manifiesto M00–M31;
3. separar dentro de `src/almas_tfa/` los dominios de datos, astrología, evidencia, ontología, contrato, temporalidad, validación y reporting;
4. implementar primero aquellas etapas que ya disponen de reglas deterministas y fixtures;
5. mantener `canonical_analysis.json` como única verdad analítica;
6. hacer que contrato, hermenéutica y reporting consuman la salida canónica sin recalcular evidencia;
7. convertir progresivamente invariantes documentales en tests ejecutables cuando exista una regla determinista equivalente;
8. normalizar el idioma vivo del repositorio al español;
9. sólo después reorganizar físicamente schemas o referencias si el orquestador demuestra que existe una frontera de dominio estable.

## 11. Resultado del Paso 1

**Paso 1 — Auditoría del repositorio: COMPLETADO.**

Clasificación general:

- arquitectura normativa: **MADURA**;
- modularidad conceptual: **IMPLEMENTADA**;
- schemas y contratos: **AMPLIOS**;
- scoring numérico: **EJECUTABLE**;
- pipeline M00–M31: **DECLARADO, NO ORQUESTADO EN PYTHON**;
- cálculo astrológico integral: **NO IMPLEMENTADO EN EL NÚCLEO PYTHON**;
- ontología/contrato diferencial: **ESPECIFICACIÓN AVANZADA, EJECUCIÓN PARCIAL**;
- reporting automatizado: **ESPECIFICADO, NO IMPLEMENTADO COMO MOTOR PYTHON**;
- CI actual: **VERDE**;
- validación externa real: **PENDIENTE**;
- idioma del repositorio: **PARCIALMENTE INCONSISTENTE CON LA POLÍTICA ESPAÑOLA**.

La próxima actuación debe ser el **Paso 2: contrato común de módulos + diseño del orquestador interno**, manteniendo intacta la release pública `1.10.1` hasta que exista una modificación funcional que justifique un cambio SemVer.

## 12. Actualización post-auditoría — ALMAS 1.11.0

Las secciones 1–11 anteriores son una fotografía deliberadamente histórica del commit base `8bdd478b69628cc669616de084c11f6226310328` / ALMAS 1.10.1. Las brechas allí descritas motivaron la implementación posterior y no deben leerse como estado actual de 1.11.0.

Estado posterior a la implementación:

- contrato común de módulos: **IMPLEMENTADO**;
- orquestador M00–M31: **IMPLEMENTADO**;
- M00: **ORCHESTRATOR_NATIVE**;
- M01 y M03–M31: **EXECUTABLE_HANDLER**;
- M02 natal y M08 Davison: **BACKEND_REQUIRED**, con contratos inyectables ya implementados;
- geometría relacional, simetrías, compuesta, dracónicas, lotes y capa secundaria: **EJECUTABLES**;
- grafo de evidencia, deduplicación y raíces independientes: **EJECUTABLES**;
- contraevidencia y ablación AB0–AB8: **EJECUTABLES**;
- sensibilidad horaria, modelos nulos, Wilson y robustez: **EJECUTABLES**;
- temporalidad anclada y eventos documentales: **EJECUTABLES**;
- doctrina/hermenéutica, viabilidad/reciprocidad y gate/modelo de reporting: **EJECUTABLES**;
- prueba sintética FULL M00–M31: **SUCCESS**;
- suite Python: **75 tests deterministas, SUCCESS**;
- contrato público CI: **SUCCESS**.

Persisten deliberadamente límites metodológicos: no existe todavía backend astronómico de producción seleccionado; la fuerza final de raíces no se calcula sin una política preregistrada para fiabilidad/factor horario/coeficiente/cargas; M20 no inventa una fórmula de agregación ICE; M26 no inventa pesos de agregación IAT; y la validación externa holdout continúa pendiente. Estas ausencias se representan como `NOT_CALCULATED`, `NOT_EVALUABLE` o fronteras explícitas, nunca mediante valores simulados.

El objetivo de la fase siguiente deja de ser “hacer ejecutable M00–M31” y pasa a ser **cerrar las políticas cuantitativas aún no preregistradas, seleccionar/validar backend astronómico de producción, normalizar el idioma vivo del repositorio y ejecutar validación externa congelada**.
