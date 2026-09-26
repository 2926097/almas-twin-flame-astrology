# Baseline congelado · Discriminador ontológico v1

## Objeto

Este documento fija el baseline técnico y metodológico previo a la implantación del discriminador ontológico destinado a estudiar la separabilidad entre los modelos:

- SOULMATE;
- MONADIC_ORIGIN;
- SPLIT_SOUL;
- TWIN_FLAME.

La finalidad de este baseline es impedir que el desarrollo posterior modifique retrospectivamente las condiciones de partida o confunda mejoras del discriminador con cambios previos del sistema.

## Baseline de versión

- Repositorio: `2926097/almas-twin-flame-astrology`
- Rama base: `main`
- Versión pública congelada: `1.11.0`
- Tag: `v1.11.0`
- Commit auditado: `3fd60b834e83ebf5fa984f81d377fb61fb95170b`
- Tree SHA: `a5b3172d452b7d2c7a3231b476ccc436e7fd7aa2`
- Rama de desarrollo: `feature/discriminador-ontologico-v1`

El tag anotado `v1.11.0` resuelve al commit auditado indicado.

## Estado de release y CI

La release pública `ALMAS 1.11.0` está publicada sobre `v1.11.0`.

Para el commit congelado de baseline constan dos workflows completados con éxito:

- `Contrato público` · `.github/workflows/public-contract.yml` · SUCCESS.
- `Núcleo Python` · `.github/workflows/python-tests.yml` · SUCCESS.

La release declara 133 tests deterministas y pipeline FULL sintético M00–M31 validado de extremo a extremo.

## Arquitectura congelada

Se conserva como baseline:

- una única skill pública ALMAS;
- pipeline modular M00–M31;
- separación epistemológica A/B/C/D/E;
- ontología multiaxial;
- grafo de evidencia y deduplicación;
- raíces independientes;
- contraevidencia;
- ablación estructural;
- sensibilidad horaria;
- modelos nulos;
- robustez;
- temporalidad;
- gate doctrinal;
- viabilidad y reciprocidad basadas en hechos documentados.

## Invariantes de desarrollo

Durante la implantación inicial del discriminador ontológico v1 no se modifican silenciosamente:

- fórmulas de IEM, IDD, IRC, IAT, ICC o ICE;
- pesos estructurales existentes;
- thresholds vigentes de `SUPPORTED`;
- reglas de independencia;
- firewall de contraevidencia;
- significado de rareza bajo modelos nulos;
- regla de que la temporalidad no crea arquitectura estructural;
- regla de que una fuente doctrinal no añade puntos por su mera existencia;
- ontología multiaxial salvo mediante cambios explícitos, versionados y testeados.

## Principio de no-identificabilidad

El objetivo del nuevo discriminador no será forzar una etiqueta única.

Si dos o más modelos producen la misma firma observable y no existe un discriminador independiente validado capaz de separarlos, la salida correcta deberá preservar la indeterminación.

En particular, el sistema deberá poder devolver:

`SHARED_ORIGIN_UNDIFFERENTIATED / INSUFFICIENT`

cuando monadic origin, split-soul, twin-flame u otros modelos de origen compartido no puedan distinguirse de forma reproducible con la evidencia disponible.

## Regla de promoción

Ninguna señal nueva podrá convertirse directamente en regla confirmatoria.

Toda señal nueva deberá seguir:

`fuente/problema → definición operacional → observable → hipótesis competidoras → falsador → control negativo → independencia → test sintético → replicación → validación fuera de muestra → promoción`.

## Protección frente a circularidad

No constituyen por sí mismas verdad de referencia ontológica:

- autoetiqueta soulmate/twin-flame;
- intensidad;
- sufrimiento;
- obsesión;
- runner/chaser;
- sensación de destino;
- sincronías;
- reconocimiento inmediato;
- separación/reunión;
- matrimonio o ruptura;
- rareza astrológica;
- una sola técnica;
- un asteroide aislado;
- una sincronía temporal aislada.

## Regla de regresión

Todo cambio posterior deberá conservar los tests y contratos válidos de 1.11.0 o documentar expresamente la ruptura.

El desarrollo del discriminador se considerará regresivo si una señal no validada puede elevar por sí misma una categoría ontológica más específica de lo permitido por el baseline.

## Estado de este documento

Este archivo congela únicamente el punto de partida.

No introduce todavía:

- nuevas fórmulas;
- nuevos pesos;
- nuevos thresholds;
- discriminadores confirmatorios;
- cambios de versión pública;
- cambios en M21;
- cambios en M25;
- cambios de schema canónico.

El siguiente paso será definir formalmente el problema de identificabilidad y las condiciones de separabilidad entre modelos antes de implementar lógica nueva.
