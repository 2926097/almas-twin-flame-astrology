# ALMAS Twin-Flame Astrology Skill

**Public release:** 1.0.0  
**Internal lineage:** Twin-Flame Astrology / ALMAS v3.12.1  
**Status:** research specification / reproducible interpretive framework

ALMAS is a multidisciplinary framework for studying relationship astrology and soul-bond models without reducing a relationship to a single label. It combines synastry, composite and Davison charts, draconic layers, traditional mirror techniques, temporal activation, null-model rarity, ablation, birth-time robustness, comparative doctrine and hermeneutic reporting.

The framework can compare four recurrent operational models — **AF** (almas afines), **KA** (karmic), **AG** (almas gemelas/soulmate), and **LG** (llamas gemelas/twin flame) — while simultaneously analysing independent axes of origin, history, function, polarity, modality, phase, viability and reciprocity.

## What v1.0.0 means

`1.0.0` is the first **public GitHub version**. It is not the first internal version. The public release derives from the ALMAS v3.12.1 line and consolidates its calculation, validation, differential-diagnosis, hermeneutic and reporting rules into a publication-oriented specification.

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
docs/PROVENANCE.md          Public/internal version lineage
schemas/                    Minimal canonical JSON contracts
tests/INVARIANTS.md         Release invariants and regression checklist
CHANGELOG.md                Public changelog
VERSION                     Public version
```

## Use

Start with `SKILL.md`. A FULL run should produce a canonical analytical object first, then derive any report from that canonical object. The report layer may format and explain findings, but it must not recalculate or alter analytical values.

## License

No open-source license has been selected for v1.0.0. Publication on GitHub does not itself grant reuse rights beyond those provided by applicable law and GitHub's platform terms. Add a license only when the project owner has chosen one deliberately.
