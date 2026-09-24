# Validation status

## Public v1.0.0

The repository validates only generalized rules and synthetic test fixtures. No result from an identifiable real relationship is part of the public validation corpus.

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
| Synthetic examples | Published |
| Case-specific analyses | Excluded by publication policy |

## Public automated tests

The public Python suite contains **14 deterministic unit tests** using synthetic values. It covers pillar aggregation, the one-root ceiling, non-simplex IEM behavior, ICE application, missing-essential handling, the SUPPORT gate, IDD overlap/disjoint behavior, robustness aggregation, precomputed-pillar analysis, evaluability handling and the public CLI/API contract.

A separate public-contract workflow verifies the repository structure and publication contract.

Public validation establishes implementation consistency with the declared rules. It does not validate astrology scientifically and does not convert model scores into metaphysical probabilities.
