# Architecture · ALMAS v1.4.0

ALMAS is a **single public skill with internal specialized modules**.

The normative module manifest is `manifests/almas-module-manifest.json`.

## Layers

1. **Data and calculation** — birth/event data, ephemerides, chart positions and geometric relations.
2. **Technique** — synastry, declinations, antiscia, composite, Davison, draconic, lots, timing and statistics.
3. **Evidence graph** — dependency-aware contacts, independent roots and pillar loading.
4. **Validation** — null models, Monte Carlo/Wilson intervals, ablation, parameter perturbation and birth-time robustness.
5. **Ontology** — AF/KA/AG/LG compatibility plus multidimensional relational axes.
6. **Doctrine and genealogy** — primary sources, academic analysis, historical reception, contemporary usage and explicit non-equivalence links.
7. **Preincarnation reconstruction** — origin, agreement motive, roles, encounter conditions, individual tasks, common task, clauses and fulfillment mechanisms.
8. **Temporal/lifecycle layer** — activation, development, integration, transformation and closure, always anchored to pre-existing structure.
9. **Reporting** — canonical analysis → canonical soul contract → report document model → publication output.

## Independence rules

- ASC/DSC, MC/IC, NN/SN and Vertex/Anti-Vertex are axis pairs and must not inflate root counts.
- Composite and Davison belong to one relationship-chart family for independence accounting.
- Draconic↔draconic is corroborative by default.
- Secondary asteroids are corroborative/support-only.
- Signs/houses contextualize a root but do not create one alone.
- Temporal activation never adds direct structural IEM points.
- Doctrine never adds structural points merely because a concept exists in a source.

## Versioning

`VERSION` is the only public ALMAS SemVer.

Internal modules may expose `engine_revision`, `schema_version` or `manifest_version` for compatibility, but not an independent public skill version.

## Core flow

`sources + data → calculation → evidence → validation → ontology → preincarnation reconstruction → lifecycle → report`

See `SKILL.md`, `docs/MODULE_ARCHITECTURE.md` and `manifests/almas-module-manifest.json`.
