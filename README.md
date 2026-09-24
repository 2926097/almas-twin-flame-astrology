# ALMAS · Astrología Metafísica Relacional

**Versión pública:** 1.5.0  
**Status:** research specification / reproducible interpretive framework

ALMAS is a multidisciplinary framework for studying relationship astrology and soul-bond models without reducing a relationship to a single label. It combines synastry, composite and Davison charts, draconic layers, traditional mirror techniques, temporal activation, null-model rarity, ablation, birth-time robustness, comparative doctrine and hermeneutic reporting.

The framework can compare four recurrent operational models — **AF** (almas afines), **KA** (karmic), **AG** (almas gemelas/soulmate), and **LG** (llamas gemelas/twin flame) — while simultaneously analysing independent axes of origin, history, function, polarity, modality, phase, viability and reciprocity.

## Arquitectura pública

El repositorio publica **una única skill ALMAS** organizada en módulos internos: astrología metafísica relacional, ontología, doctrina y fuentes, contrato preencarnatorio, roles, causalidad, temporalidad, validación e informes. GitHub contiene metodología generalizada, código reutilizable, fuentes públicas y ejemplos sintéticos; los casos reales sólo pueden incorporarse cuando sus datos ya son públicos y verificables.

## Core principles

- Calculated data, technique, doctrine, contemporary usage and project hypothesis remain separate.
- A rare pattern is not a metaphysical probability.
- Temporal techniques activate pre-existing structure; they do not create it.
- No single aspect, asteroid, event or synchronicity defines an ontological category.
- Competing models are not forced apart when no validated discriminator exists.
- Counterevidence, missing data and technique dependency are explicit parts of the analysis.
- Consent, boundaries and observable facts override symbolic interpretation.

## Main indices

- **IEM — Índice de Encaje del Modelo**: structural compatibility with a defined model.
- **IDD — Índice de Discriminación Diagnóstica**: how strongly the evidence architecture separates competing models. Older internal documents may use `IDE`.
- **IRC — Índice de Robustez de la Clasificación**: stability under perturbation, ablation and birth-time uncertainty.
- **IAT — Índice de Activación Temporal**: activation of pre-existing structural roots by independent temporal families.
- **ICC — Índice de Cobertura Canónica**: completeness of the required analytical domains.
- **ICE — Índice de Contraevidencia Estructural**: explicit contradictory evidence.

## Repository layout

```text
SKILL.md                    Main executable/research specification
docs/ARCHITECTURE.md        Layering, module graph and independence rules
docs/ONTOLOGY.md            Relational ontology and states
docs/METRICS.md             IEM, IDD, IRC, IAT, ICC, ICE
docs/REPORTING.md           Canonical report and PDF pipeline
docs/PROVENANCE.md          Public versioning and provenance policy
docs/PUBLICATION_POLICY.md  Rules for public/private/synthetic material
schemas/                    Minimal canonical JSON contracts
tests/INVARIANTS.md         Release invariants and regression checklist
CHANGELOG.md                Public changelog
VERSION                     Public version
```

## Use

Start with `SKILL.md`. A FULL run should produce a canonical analytical object first, then derive any report from that canonical object. The report layer may format and explain findings, but it must not recalculate or alter analytical values.


## Validation and reproducibility

![Public contract](https://github.com/2926097/almas-twin-flame-astrology/actions/workflows/public-contract.yml/badge.svg)
![Python core](https://github.com/2926097/almas-twin-flame-astrology/actions/workflows/python-tests.yml/badge.svg)

The public contract validator runs on every push and pull request. It currently verifies the public version contract, required files, the M00–M31 module manifest, AF/KA/AG/LG canonical model slots, evidential states, raw-input cardinality and discriminator-registration rules.


## Source provenance

Doctrine and contemporary usage are not treated as interchangeable. The source policy is documented in [docs/SOURCE_POLICY.md](docs/SOURCE_POLICY.md), with a machine-readable starter registry in [reference/source-registry.json](reference/source-registry.json).

The registry currently distinguishes classical antecedents, Theosophical and Bailey material, explicit Summit Lighthouse/Elizabeth Clare Prophet twin-flame doctrine, and academic context. Project hypotheses do not become doctrinal claims merely because analogous imagery exists in an older tradition.

## Executable scoring core

The repository now includes a dependency-free Python core in `src/almas_tfa/core.py`. It implements the frozen public formulas for:

- pillar aggregation from the three strongest independent roots;
- AF/KA/AG/LG IEM calculation;
- single ICE application;
- the structural `SUPPORTED` gate;
- IDD/Jensen–Shannon diagnostic separation;
- IRC robustness components and aggregation.

Install locally with `python -m pip install -e .` and run the deterministic regression suite with `python -m unittest discover -s tests -p "test_*.py" -v`.

For precomputed pillar data, the installed command is:

```bash
almas-score examples/precomputed-pillars.json
```

The input/output contracts are `schemas/precomputed-pillars.schema.json` and `schemas/precomputed-result.schema.json`. See `docs/CLI.md` for the full interface.

## Current public implementation status

The repository is a validated **generalized method specification plus executable scoring core**, with schemas, manifests, source provenance, synthetic examples, regression invariants and CI. Case-specific analyses and private research artifacts are intentionally excluded.

## License

No open-source license has been selected for the current public release. Publication on GitHub does not itself grant reuse rights beyond those provided by applicable law and GitHub's platform terms. Add a license only when the project owner has chosen one deliberately.


## Arquitectura modular

**ALMAS es una única skill pública.** El motor astrológico calcula la arquitectura relacional y el módulo de contrato preencarnatorio consume esa salida sin recalcularla.

El punto de entrada especializado del contrato se conserva en `skills/almas-soul-contract/SKILL.md` por compatibilidad histórica, pero hereda la versión raíz y no constituye una segunda skill.

La arquitectura normativa está en `docs/MODULE_ARCHITECTURE.md`. El orden ejecutable de las ocho etapas preencarnatorias se publica en `manifests/preincarnation-pipeline-manifest.json`.

## Fase 1 · Fuentes y genealogía doctrinal

ALMAS v1.4.0 inicia la normalización del corpus documental mediante `schemas/source-registry.schema.json` y `docs/SOURCE_INTEGRATION_PLAN.md`. Las fuentes definen procedencia, significado y límites doctrinales; nunca añaden puntuación astrológica por su mera existencia.
