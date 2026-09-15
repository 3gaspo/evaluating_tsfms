# Experiment catalog

## Runnable migrated families

### Foundation-model benchmark

Compares `chronos_bolt`, `chronos2`, `timesfm3`, `ts_icl`, and deterministic
`seasonal_naive` over the official TIME test tasks. It records actual target
mode, scaled MASE, finite/grid/total coverage, and inference seconds. Seasonal
Naive defines one reusable evaluation grid from finite ground-truth support,
finite Seasonal predictions, and finite Seasonal MASE. Every learned model is
evaluated on that grid, and a non-finite forecast on expected support fails the
task. Generate the baseline once with `scripts/submit_seasonal_naive.sh`; then
launch the parallel learned-model jobs with
`scripts/submit_foundation_models.sh`.

### Chronos-2 channel comparison

Compares native multivariate targets, independent univariate targets, and
past targets represented as past-only covariates on multivariate datasets.
Entry point: `scripts/channels_comparison.sh`. Its summaries consume the same
reusable Seasonal Naive baseline as the foundation-model benchmark.

### Dataset diagnostics

Audits source non-finiteness and forecast windows, then extracts reusable
dataset features. Entry point: `scripts/dataset_diagnostics.sh`.

## Planned families

- covariate ablations across every foundation model that declares support;
- input-normalization ablations with the transformation recorded in the task
  scientific identity;
- context-size ablations using explicit context limits rather than silent
  truncation.

Their exact grids, supported-model subsets, and aggregation policies have not
yet been selected. The migrated launchers do not silently implement them.
