# Contrato común de ejecución modular ALMAS

## Objeto

Este documento define el contrato operativo común para convertir la arquitectura M00–M31 en módulos ejecutables sin alterar la regla de **una única skill pública modular**.

La existencia de una etapa en el manifiesto no equivale a que exista ya un motor Python completo. El registro `manifests/execution-registry.json` separa explícitamente especificación, lógica reutilizable e implementación ejecutable.

## Entrada común

Todo handler recibe un `ModuleContext` con:

- `module_id`;
- `module_name`;
- `mode`;
- `raw_input`;
- `canonical_snapshot`;
- `prior_results`.

El snapshot canónico debe tratarse como inmutable. El módulo devuelve cambios; no modifica el estado compartido directamente.

## Salida común

Todo handler devuelve `ModuleResult` con:

- `module_id`;
- `status`;
- `payload`;
- `canonical_updates`;
- `evidence_refs`;
- `limitations`;
- `diagnostics`.

Los estados de ejecución son:

- `COMPLETED`: el módulo se ejecutó y puede producir actualizaciones canónicas;
- `SKIPPED`: la etapa fue omitida por una regla explícita de ejecución;
- `NOT_APPLICABLE`: la etapa no corresponde al caso o modo;
- `NOT_EVALUABLE`: faltan datos, cálculo o implementación suficiente;
- `FAILED`: se produjo un error operativo.

Estos estados son **estados de ejecución** y no sustituyen los estados epistemológicos `SUPPORTED`, `COMPATIBLE`, `INSUFFICIENT`, `CONTRADICTED` y `NOT_EVALUABLE` utilizados en ontología y diagnóstico diferencial.

## Propiedad del estado canónico

Cada actualización canónica reclama un namespace de primer nivel. Una vez que un módulo lo ha escrito, otro módulo no puede sobrescribirlo silenciosamente.

Esta regla implementa el invariante:

> un módulo no recalcula ni sustituye de forma silenciosa valores canónicos producidos por otro.

Las transformaciones legítimas deben escribir un nuevo namespace derivado o introducirse mediante una regla explícita futura con genealogía de procedencia.

## Orquestador

`src/almas_tfa/orchestrator.py` valida que el manifiesto FULL contenga exactamente M00–M31 en orden.

El orquestador:

1. recorre la secuencia declarada;
2. construye un contexto inmutable para cada etapa;
3. ejecuta únicamente handlers registrados;
4. marca como `NOT_EVALUABLE` las etapas todavía sin implementación;
5. acumula resultados y estado canónico;
6. registra la propiedad de cada namespace;
7. bloquea sobrescrituras intermodulares;
8. puede detenerse ante el primer fallo cuando `stop_on_failure=True`.

Por diseño, el primer esqueleto no finge que las 32 etapas están implementadas.

## Relación con canonical_analysis.json

El orquestador es infraestructura de ejecución. No sustituye `schemas/canonical-analysis.schema.json`.

Cuando estén implementados los handlers suficientes, determinados módulos publicarán namespaces canónicos que podrán ensamblarse y validarse contra `canonical-analysis.schema.json`.

Hasta entonces debe distinguirse:

`orchestration run != canonical_analysis completo`.

## Política de implementación

La secuencia recomendada es:

`contrato común → orquestador → adaptadores de lógica existente → cálculo/evidencia → ontología → contrato → temporalidad → reporting`.

No se modifican en este paso fórmulas, pesos, umbrales, modelos ontológicos ni discriminadores.

## Adaptadores ejecutables iniciales

La primera integración conecta al pipeline lógica ya existente sin cambiar sus fórmulas:

- `M18` — pilares: acepta pilares precomputados o deriva el valor de un pilar desde intensidades de raíces mediante `pillar_score`;
- `M19` — índices estructurales: reutiliza `score_model` y `supported_gate`;
- `M21` — discriminación diferencial: reutiliza `diagnostic_discrimination` e `idd_band`;
- `M25` — robustez: reutiliza `robustness_index` sobre componentes preregistrados.

Estos adaptadores viven en `src/almas_tfa/handlers.py`. Las etapas restantes continúan explícitamente como no implementadas hasta disponer de un motor reproducible.
