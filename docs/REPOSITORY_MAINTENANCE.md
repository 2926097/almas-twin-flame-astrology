# Mantenimiento del repositorio

## Objetivo

Mantener una única fuente normativa por responsabilidad y evitar que instantáneas históricas, nombres heredados o versiones internas compitan con el estado vigente.

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
| Auditoría del corpus | `reference/source-normalization-audit.json` |
| Ontología | `reference/ontology-registry.json` |
| Doctrina→astrología | `reference/doctrine-to-astrology-map.json` |
| Discriminadores transversales | `manifests/cross-model-discriminator-registry.json` |
| Estado de validación | `VALIDATION_STATUS.md` |

## Reglas de higiene

1. `VERSION` es el único SemVer público.
2. Un esquema puede tener versión propia, pero sus datos de prueba deben coincidir con ella.
3. Un manifiesto que declare `almas_version` debe coincidir con `VERSION`.
4. Las instantáneas históricas no permanecen en rutas activas cuando existe un reemplazo canónico.
5. Los documentos de fase ya completada se archivan en `docs/history/`.
6. No mantener dos archivos con nombres que sugieran la misma responsabilidad.
7. Las rutas renombradas se actualizan en SKILL, README, CI y documentación viva.
8. Los datos de prueba de `examples/` son sintéticos salvo declaración explícita en contrario.
9. Los casos privados nunca se copian a datos de prueba, ejemplos o documentación pública.
10. Una release no se integra en `main` mientras `Contrato público` o `Núcleo Python` estén en rojo.
11. Todo texto destinado a lectura humana se redacta en español. Se exceptúan identificadores de máquina, claves de esquemas, rutas, nombres canónicos, comandos y términos de estándar cuya traducción rompería compatibilidad o trazabilidad.

## Política de depuración

Una limpieza de repositorio puede:

- corregir rutas;
- retirar instantáneas obsoletas;
- archivar documentos históricos;
- eliminar comprobaciones duplicadas;
- hacer dinámicas las comprobaciones esquema↔datos de prueba;
- aclarar nombres;
- normalizar al español la prosa destinada a lectura humana sin renombrar contratos de máquina.

No puede, bajo una release PATCH, alterar silenciosamente:

- fórmulas;
- pesos;
- umbrales;
- ontología;
- reglas de independencia;
- discriminadores;
- estados epistemológicos.

Esos cambios requieren la categoría SemVer correspondiente y una entrada metodológica explícita en el changelog.
