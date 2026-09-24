# ALMAS · Astrología Metafísica Relacional

**Versión pública:** 1.3.1  
**Status:** research specification / reproducible interpretive framework

ALMAS is a multidisciplinary framework for studying relationship astrology and soul-bond models without reducing a relationship to a single label. It combines synastry, composite and Davison charts, draconic layers, traditional mirror techniques, temporal activation, null-model rarity, ablation, birth-time robustness, comparative doctrine and hermeneutic reporting.

The framework can compare four recurrent operational models — **AF** (almas afines), **KA** (karmic), **AG** (almas gemelas/soulmate), and **LG** (llamas gemelas/twin flame) — while simultaneously analysing independent axes of origin, history, function, polarity, modality, phase, viability and reciprocity.

## Arquitectura pública

El repositorio contiene el motor de **astrología metafísica relacional** y, como segunda skill interoperable, el motor de **contrato álmico preencarnatorio**. Ambos pertenecen a ALMAS, pero mantienen funciones y versionado propios. GitHub contiene metodología generalizada, código reutilizable, fuentes públicas y ejemplos sintéticos; los casos reales sólo pueden incorporarse cuando sus datos ya son públicos y verificables.

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


## Dos skills interoperables

**1. ALMAS · Astrología Metafísica Relacional** — esta raíz del repositorio. Calcula y organiza la arquitectura metafísica observable mediante astrología: cartas, sinastría, nodos, ejes, declinaciones, antiscios, compuesta, Davison, dracónica, lotes, temporalidad, recurrencia, rareza estructural, ablación y robustez.

**2. ALMAS · Contrato Álmico v1.2.0** — `skills/almas-soul-contract/SKILL.md`. Reconstruye el posible acuerdo preencarnatorio a partir de la arquitectura astrológica ya calculada, doctrina documentada, cronología y contraevidencia. Su reconstrucción FULL sigue ocho etapas: origen → motivo → roles → condiciones de encuentro → tareas individuales → tarea común → cláusulas → mecanismos de cumplimiento. La etapa de origen incorpora un **motor diferencial del origen de las almas** que compara modelos competidores y conserva `SHARED_ORIGIN_UNDIFFERENTIATED` cuando faltan discriminadores validados.

Las dos skills se conectan mediante `schemas/astrology-to-soul-contract.schema.json`. La astrología funciona aquí como método metafísico de investigación; los controles metodológicos evitan sobreconteo, dependencia y ajuste al caso, no desautorizan el paradigma metafísico.

Consulta también `docs/DUAL_ENGINE_ARCHITECTURE.md`.
