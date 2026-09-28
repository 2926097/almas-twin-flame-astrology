# Arquitectura de ALMAS

ALMAS es una **única skill pública con módulos internos especializados**.

## Manifiestos normativos

- `manifests/almas-module-manifest.json`: declara los módulos arquitectónicos de la skill.
- `manifests/analysis-pipeline-manifest.json`: declara la secuencia ejecutable M00–M31 para un análisis FULL.
- `manifests/preincarnation-pipeline-manifest.json`: declara las ocho etapas de reconstrucción preencarnatoria.

Estos manifiestos cumplen funciones distintas y no deben fusionarse ni duplicarse.

## Capas

1. **Datos y cálculo** — datos natales/eventos, posiciones y geometría.
2. **Técnica** — sinastría, declinaciones, antiscios, compuesta, Davison, dracónica, lotes y temporalidad.
3. **Grafo de evidencia** — contactos, dependencias y raíces independientes.
4. **Validación** — modelos nulos, ablación, sensibilidad, robustez y contraevidencia.
5. **Ontología** — AF/KA/AG/LG y ejes relacionales independientes.
6. **Doctrina y genealogía** — fuentes primarias, academia, historia, uso contemporáneo y no-equivalencias.
7. **Reconstrucción preencarnatoria** — origen, motivo, roles, condiciones, tareas, cláusulas y cumplimiento.
8. **Ciclo temporal/documental** — activación, recurrencia, integración, transformación y cierre.
9. **Reporting** — canonical → modelo de documento → salida publicada.

## Reglas de independencia

- ASC/DSC, MC/IC, NN/SN y Vertex/Anti-Vertex son pares de eje.
- Compuesta y Davison pertenecen a una misma familia relacional para independencia.
- Dracónica↔dracónica es corroborativa por defecto.
- Asteroides secundarios son `support_only`.
- Casas y signos contextualizan; no crean una raíz ontológica por sí solos.
- Temporalidad no añade puntos estructurales directos.
- Doctrina no añade puntuación por su mera existencia.

## Versionado

`VERSION` es el único SemVer público.

Los componentes internos pueden usar `schema_version`, `manifest_version` o `engine_revision` para compatibilidad técnica.

## Flujo

`fuentes + datos → cálculo → evidencia → validación → ontología → reconstrucción preencarnatoria → ciclo temporal → informe`

Véanse `SKILL.md`, `docs/MODULE_ARCHITECTURE.md` y los manifiestos de `manifests/`.
