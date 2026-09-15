# Evaluating TSFMs

Evaluating TSFMs studies how representation and input choices affect
zero-shot time-series foundation models on the public TIME benchmark. It is an
experiment repository derived from the source-only
[Improved TIME](https://github.com/3gaspo/improved_TIME) layer.

The initial migration preserves the former Improved repository's five-model
foundation benchmark, Chronos-2 channel comparison, dataset diagnostics,
feature-performance analysis, task recovery, and DGX/Selena launch machinery.
No result is claimed for this new repository until those experiments are
rerun under its own artifact lineage.

## Scientific scope

The migrated runnable studies are:

- a reusable Seasonal Naive baseline plus parallel Chronos-Bolt, Chronos-2,
  TimesFM-3, and TS-ICL evaluations, with Seasonal-Naive-scaled MASE and
  inference timing on one shared Seasonal-defined evaluation grid;
- Chronos-2 native multivariate, independent univariate, and past-target-as-
  covariate comparison;
- reusable dataset/window diagnostics and feature-performance associations.

Planned additions will evaluate covariate use across capable foundation
models, input normalization, and context-size effects. Those axes remain
planned until their exact configurations and launchers are implemented.

## Setup

Prepare the project environment on each execution host with `uv`. Learned
models run offline from checkpoints below `TIME_WEIGHTS`; the default names
are `chronos2/`, `chronos-bolt-base/`, `timesfm3/`, and
`tsicl/tsicl-v1.ckpt`. Download the official saved-Arrow TIME data on an
internet-connected preparation host with:

```bash
PYTHONPATH=src uv run --no-sync python scripts/download_time_dataset.py \
  --destination datasets/hf_dataset
```

## Current experiment entry points

From a prepared DGX or Selena checkout:

```bash
bash scripts/submit_seasonal_naive.sh dgx
bash scripts/submit_foundation_models.sh dgx
bash scripts/channels_comparison.sh dgx
bash scripts/dataset_diagnostics.sh dgx
```

Replace `dgx` by `selena` for the Selena fronts. Run the Seasonal Naive command
once and wait for it to complete. It writes the shared baseline selected by
`TIME_SEASONAL_ROOT`, including the grid of cells with finite ground-truth
support, finite Seasonal Naive predictions on that support, and finite
Seasonal Naive MASE. Foundation-model and channel launchers require that grid,
then run without a Seasonal job dependency and may be submitted together. A
learned model that produces a non-finite forecast on the grid fails its task
instead of silently changing metric coverage. The four learned
foundation models run concurrently; their summary runs once after every model
terminates and reads the shared baseline. Each task is addressed by its
complete scientific configuration and has schema-1 lifecycle metadata.

`sync_code_to_selena.sh`, `sync_results_to_dgx.sh`, and `publish_job.sh`
retain this project's code and artifacts without touching another TIME
project. Generated results live in `outputs/`; runtime streams live in
`logs/`.

## Documentation

- [Architecture](docs/architecture.md) describes ownership and execution flow.
- [Experiment catalog](docs/experiment_catalog.md) distinguishes runnable and
  planned experiment families.
- [Method overview](latex/method_overview.tex) states the evaluation questions.
- [Results recap](docs/results_recap.md) defines the current evidence boundary.
- [TIME dataset format](docs/DATASET_FORMAT.md) documents the inherited
  saved-Arrow representation.

## Source tree

```text
experiments/               inherited model/evaluation entry points
scripts/                   public experiment and analysis commands
slurm/                     DGX and Selena scheduler fronts
src/slurm/                 scheduler workflow implementations
src/timebench/             inherited reusable benchmark implementation
src/tests/                 shared and experiment-specific contract checks
docs/, latex/              architecture, protocol, and evidence documents
outputs/, logs/            ignored project-owned runtime artifacts
```

The code derives from the ICML 2026 TIME benchmark and remains under its
Apache-2.0 license.
