# Mantenimiento del repositorio

## Objetivo

Mantener una única fuente normativa por responsabilidad y evitar que snapshots históricos, nombres heredados o versiones internas compitan con el estado vigente.

## Fuentes canónicas por dominio

| Dominio | Fuente canónica |
|---|---|
| Versión pública | `VERSION` |
| Especificación principal | `SKILL.md` |
| Arquitectura de módulos | `manifests/almas-module-manifest.json` |
| Pipeline FULL M00–M31 | `manifests/analysis-pipeline-manifest.json` |
| Pipeline preencarnatorio | `manifests/preincarnation-pipeline-manifest.json` |
| Fuentes | `reference/source-registry.json` |
| Conceptos | `reference/concept-registry.json` |
| Genealogía doctrinal | `reference/doctrinal-genealogy.json` |
| Audit del corpus | `reference/source-normalization-audit.json` |
| Ontología | `reference/ontology-registry.json` |
| Doctrina→astrología | `reference/doctrine-to-astrology-map.json` |
| Discriminadores transversales | `manifests/cross-model-discriminator-registry.json` |
| Estado de validación | `VALIDATION_STATUS.md` |

## Reglas de higiene

1. `VERSION` es el único SemVer público.
2. Un schema puede tener versión propia, pero su fixture debe coincidir con ella.
3. Un manifiesto que declare `almas_version` debe coincidir con `VERSION`.
4. Los snapshots históricos no permanecen en rutas activas cuando existe un reemplazo canónico.
5. Los documentos de fase ya completada se archivan en `docs/history/`.
6. No mantener dos archivos con nombres que sugieran la misma responsabilidad.
7. Las rutas renombradas se actualizan en SKILL, README, CI y documentación viva.
8. Los fixtures de `examples/` son sintéticos salvo declaración explícita en contrario.
9. Los casos privados nunca se copian a fixtures, ejemplos o documentación pública.
10. Una release no se integra en `main` mientras `Public contract` o `Python core` estén en rojo.

## Política de depuración

Una limpieza de repositorio puede:

- corregir rutas;
- retirar snapshots obsoletos;
- archivar documentos históricos;
- eliminar comprobaciones duplicadas;
- hacer dinámicas las comprobaciones schema↔fixture;
- aclarar nombres.

No puede, bajo una release PATCH, alterar silenciosamente:

- fórmulas;
- pesos;
- umbrales;
- ontología;
- reglas de independencia;
- discriminadores;
- estados epistemológicos.

Esos cambios requieren la categoría SemVer correspondiente y una entrada metodológica explícita en el changelog.
