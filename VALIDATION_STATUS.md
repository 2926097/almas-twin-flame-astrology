# Validation status

## Public v1.3.1

The repository validates generalized rules with synthetic test fixtures. Real public case studies, if added, are documentary/illustrative material and are not used as hidden validation fixtures or as a basis for case-fitted rules.

Current public layers:

| Layer | Status |
|---|---|
| Normative methodology | Published |
| Public raw/canonical schemas | Published |
| Precomputed scoring input/output schemas | Published |
| Module manifest | Published |
| Differential-discriminator registry | Published |
| Source-provenance policy and registry | Published |
| Public static contract validator | Published; CI enabled |
| Deterministic pillar/IEM/IDD/IRC scoring core | Published; unit-tested |
| Precomputed-pillar CLI | Published; unit-tested |
| ALMAS Soul Contract skill | Published; independent v1.2.0 |
| Astrology→Soul Contract bridge | Published; contract v1.0.0 |
| Preincarnation reconstruction | Published; eight-stage schema v1.1.0 |
| Soul-origin differential engine | Published; model registry/schema v1.0.0 |
| Synthetic examples | Published |
| Private/non-public case analyses | Excluded |
| Public sourced case studies | Permitted outside the synthetic validation corpus |

## Public automated tests

The public Python suite contains **14 deterministic unit tests** using synthetic values. It covers pillar aggregation, the one-root ceiling, non-simplex IEM behavior, ICE application, missing-essential handling, the SUPPORT gate, IDD overlap/disjoint behavior, robustness aggregation, precomputed-pillar analysis, evaluability handling and the public CLI/API contract.

A separate public-contract workflow verifies the repository structure and publication contract.

Public validation establishes implementation consistency with the declared rules. It does not validate astrology scientifically and does not convert model scores into metaphysical probabilities.
