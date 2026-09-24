# ALMAS · Nota de compatibilidad arquitectónica

> **Estado:** documento legado. La arquitectura normativa vigente está en `docs/MODULE_ARCHITECTURE.md`.

Las versiones intermedias de ALMAS describieron la astrología metafísica relacional y el contrato álmico como dos skills o motores con versionado independiente.

Desde **ALMAS v1.4.0**, esa separación deja de ser normativa.

ALMAS se publica como **una única skill modular**. Se conservan dos motores funcionales porque realizan tareas diferentes:

1. **Motor astrológico-relacional** — calcula cartas, raíces, pilares, modelos, temporalidad, robustez y contraevidencia.
2. **Módulo de contrato preencarnatorio** — consume la arquitectura ya calculada y reconstruye origen, motivo, roles, tareas, cláusulas y mecanismos de cumplimiento.

La separación es computacional y metodológica, no una división en dos productos o skills.

El bridge `schemas/astrology-to-soul-contract.schema.json` se conserva porque impide que el módulo contractual recalcule o duplique evidencia astrológica.

## Flujo vigente

```text
DATOS
  ↓
MOTOR ASTROLÓGICO
  ↓
canonical_analysis.json
  ↓
bridge contractual
  ↓
MÓDULO DE CONTRATO PREENCARNATORIO
  ↓
canonical_soul_contract.json
  ↓
VALIDACIÓN + INFORME
```

## Versionado

La única versión pública es la contenida en `VERSION`.

Los motores internos pueden mantener `schema_version`, `engine_revision` o `manifest_version` para compatibilidad técnica, pero no SemVer público independiente.

Véase `docs/MODULE_ARCHITECTURE.md`.
