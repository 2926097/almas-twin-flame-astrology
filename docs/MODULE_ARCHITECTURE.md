# ALMAS · Arquitectura modular única

## Decisión

ALMAS se publica y versiona como **una única skill**.

Astrología relacional, ontología, doctrina, contrato preencarnatorio, roles, causalidad, temporalidad, validación y reporting son módulos internos.

`skills/almas-soul-contract/SKILL.md` se conserva como punto de entrada especializado por compatibilidad, pero no constituye una segunda skill pública.

## Registros y manifiestos, funciones diferenciadas

- `manifests/almas-module-manifest.json`: arquitectura de alto nivel.
- `manifests/analysis-pipeline-manifest.json`: módulos ejecutables M00–M31 de un análisis FULL.
- `manifests/preincarnation-pipeline-manifest.json`: ocho etapas de reconstrucción preencarnatoria.
- `manifests/execution-registry.json`: grado de implementación ejecutable de M00–M31.

No son duplicados. El contrato operativo común está documentado en `docs/MODULE_EXECUTION_CONTRACT.md` y materializado en `src/almas_tfa/module_contract.py` y `src/almas_tfa/orchestrator.py`.

La antigua arquitectura dual se conserva sólo como historia en `docs/history/DUAL_ENGINE_ARCHITECTURE.md`.

## Flujo canónico

```text
FUENTES + DATOS
      ↓
CÁLCULO ASTROLÓGICO
      ↓
canonical_analysis.json
      ↓
EVIDENCIA + VALIDACIÓN
      ↓
ONTOLOGÍA MULTIAXIAL
      ↓
RECONSTRUCCIÓN PREENCARNATORIA
      ↓
canonical_soul_contract.json
      ↓
TEMPORALIDAD / HECHOS / VIABILIDAD
      ↓
INFORME
```

El módulo contractual consume evidencia canónica; no recalcula silenciosamente la capa astrológica.

## Versionado

`VERSION` es el único SemVer público.

Los módulos internos pueden usar:

- `schema_version`;
- `engine_revision`;
- `manifest_version`.

## Separación epistemológica

Cada afirmación conserva:

- A · dato calculado/documental;
- B · técnica;
- C · doctrina explícita;
- D · uso contemporáneo;
- E · hipótesis del proyecto.

Las fuentes definen conceptos y límites. La astrología evalúa operacionalizaciones. Una fuente nunca aporta puntos por existir.

## Desarrollo

Toda función nueva sigue:

`problema/fuente → definición → evidencia necesaria → límites → regla reproducible → fixture/test sintético → validación → incorporación`.

Un caso privado puede revelar un problema metodológico, pero sus datos no se publican ni se convierten directamente en regla.
