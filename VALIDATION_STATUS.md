# Validation status

## Public v1.0.0

The public repository contains the normative specification, public schemas, module/discriminator manifests, source provenance, a regression checklist, a public contract validator, an executable deterministic scoring core and a precomputed-pillar CLI.

The historical internal ALMAS v3.12 validation artifact preserved in `validation/validation-results-v3.12.json` reports:

- critical tests: **20 passed / 0 failed**;
- non-critical tests: **25 passed / 0 failed**;
- total recorded checks: **45 passed / 0 failed**.

That artifact is evidence about the internal v3.12 build from which public v1.0.0 descends. It is **not** represented as a fresh execution of the public repository, because the complete historical v3.12 script/manifests bundle has not yet been imported file-for-file into this repository.

## Public reproducibility status

| Layer | Status |
|---|---|
| Normative methodology | Published |
| Public raw/canonical schemas | Published |
| Precomputed scoring input/output schemas | Published |
| Module manifest | Published |
| Differential-discriminator registry | Published |
| Source-provenance policy and registry | Published |
| Historical v3.12 validation result | Published |
| Public static contract validator | Published; CI passing |
| Deterministic pillar/IEM/IDD/IRC scoring core | Published; unit-tested |
| Precomputed-pillar CLI | Published; unit-tested |
| Full astronomical calculation engine | Pending verified import |
| Evidence extraction/root construction engine | Pending verified import |
| Monte Carlo/ablation engine | Pending verified import |
| Full historical automated suite | Pending verified import |
| End-to-end canonical report renderer | Pending verified import |

No missing executable component should be silently reconstructed and presented as the historical implementation. When the original source is recovered, it should be imported with provenance and regression-tested against the preserved validation results.

## Public automated tests

The current public Python suite contains **14 deterministic unit tests**. It covers pillar aggregation, the one-root ceiling, non-simplex IEM behavior, ICE application, missing-essential handling, the SUPPORT gate, IDD overlap/disjoint behavior, robustness aggregation, precomputed-pillar analysis, evaluability handling and the public CLI/API contract.

The repository also runs a separate public-contract workflow. At the current `main` verification point, both **Public contract** and **Python core** complete successfully.
