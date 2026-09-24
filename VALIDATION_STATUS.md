# Validation status

## Public v1.0.0

The public repository currently contains the normative specification, public schemas, module/discriminator manifests, a regression checklist and a lightweight public contract validator.

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
| Module manifest | Published |
| Differential-discriminator registry | Published |
| Historical v3.12 validation result | Published |
| Public static contract validator | Published |
| Full astronomical calculation engine | Pending verified import |
| Monte Carlo/ablation engine | Pending verified import |
| Full historical automated suite | Pending verified import |
| End-to-end canonical report renderer | Pending verified import |

No missing executable component should be silently reconstructed and presented as the historical implementation. When the original source is recovered, it should be imported with provenance and regression-tested against the preserved validation results.
