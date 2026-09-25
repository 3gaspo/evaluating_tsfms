# Evaluating TSFMs

Evaluating TSFMs studies how representation and input choices affect
zero-shot time-series foundation models on the public TIME benchmark. It is an
experiment repository derived from the source-only
[Improved TIME](https://github.com/3gaspo/improved_TIME) layer.

The repository inherits foundation execution, Seasonal Naive, dataset
diagnostics, feature-performance analysis, task recovery, reporting, and
DGX/Selena machinery from Improved TIME. It owns the Chronos-2 channel
comparison and its active schedule, which excludes TimesFM-3 and evaluates
three learned models plus Seasonal Naive.

## Scientific scope

The migrated runnable studies are:

- a reusable Seasonal Naive baseline plus parallel Chronos-Bolt, Chronos-2,
  and TS-ICL evaluations, with Seasonal-Naive-scaled MASE and
  inference timing on one shared Seasonal-defined evaluation grid;
- Chronos-2 native multivariate, independent univariate, and past-target-as-
  covariate comparison;
- five-value maximum-context grids for Chronos-Bolt, Chronos-2, and TS-ICL,
  with every successive value divided by two;
- per-window, per-variate input z-score normalization versus unchanged input,
  with predictions transformed back to the target units before evaluation;
- reusable dataset/window diagnostics and feature-performance associations.

Covariate use across every capable foundation model remains planned.

## Setup

Prepare the project environment on each execution host with `uv`. Learned
models run offline from checkpoints below `TIME_WEIGHTS`; the default names
are `chronos2/`, `chronos-bolt-base/`, and `tsicl/tsicl-v1.ckpt`. Download the
official saved-Arrow TIME data on an
internet-connected preparation host with:

```bash
PYTHONPATH=src uv run --no-sync python scripts/download_time_dataset.py \
  --destination datasets/hf_dataset
```

## Current experiment entry points

From a prepared DGX or Selena checkout:

```bash
bash scripts/submit_seasonal_naive.sh dgx shared
bash scripts/submit_foundation_models.sh dgx
bash scripts/channels_comparison.sh dgx
bash scripts/context_size.sh dgx
bash scripts/instance_normalization.sh dgx
bash scripts/dataset_diagnostics.sh dgx
```

Replace `dgx` by `selena` for the Selena fronts. The optional second Seasonal
argument is `shared` (the default) or `project`; consumers must use the same
`TIME_SEASONAL_SCOPE`, unless `TIME_SEASONAL_ROOT` explicitly selects the
artifact location. Run the Seasonal Naive command once and wait for it to
complete. It writes the baseline and the grid of cells with finite ground-truth
support, finite Seasonal Naive predictions on that support, and finite
Seasonal Naive MASE. Foundation-model and channel launchers require that grid,
then run without a Seasonal job dependency and may be submitted together. A
learned model that produces a non-finite forecast on the grid fails its task
instead of silently changing metric coverage. The three learned
foundation models run concurrently; their summary runs once after every model
terminates and reads the shared baseline. Each task is addressed by its
complete scientific configuration and has schema-1 lifecycle metadata.

The context-size launcher evaluates five maximum contexts per model:
Chronos-Bolt uses 2048, 1024, 512, 256, and 128; Chronos-2 uses 8192, 4096,
2048, 1024, and 512; TS-ICL uses 4096, 2048, 1024, 512, and 256. Its report
adds a horizon-by-context scaled-MASE figure with one panel per model. The
normalization launcher compares unchanged input with z-score normalization
using each variate's finite-value mean and population standard deviation over
the retained input context. Original missing positions remain missing;
constant finite inputs use scale one. Every predicted quantile is returned to
the original units before metrics are computed.

`sync_code_to_selena.sh`, `sync_results_to_dgx.sh`, and `publish_job.sh`
retain this project's code and artifacts without touching another TIME
project. Selena writes results to this project's scratch `outputs/` directory
and all job streams and stage logs to its `logs/` sibling. DGX pulls them into `outputs/selena/` and
`logs/selena/` in this checkout.

To regenerate reports for an existing completed launch, set `TIME_LAUNCH_ID`
to that launch's identity and submit the foundation-summary front directly.
For channels, use `TIME_REPORT_ONLY=1 TIME_LAUNCH_ID=<existing-channel-launch>
bash scripts/channels_comparison.sh selena`. This skips inference and saves
separate `channels_summary` status records without replacing evaluation statuses.

Model jobs, including the original Seasonal Naive job, save each metric's `mean`, `std`, `variance`, and
`dispersion_ddof=0` in `metrics_summary.json`. Dispersion uses the same finite
cells as the arithmetic task mean, not repeated-run uncertainty. For scaled
MASE, divide a task's MASE standard deviation by its matched Seasonal Naive
task mean; divide its variance by the square of that mean. Lightweight result
synchronization includes these JSON fields without transferring metric arrays.

The variance-ratio scatter uses model MASE variance divided by matched Seasonal
MASE variance; this differs from the variance of scaled MASE described above.
The completed Seasonal refresh's diagnostic `task_summary.csv` is retained as
plot evidence and included by lightweight synchronization; its temporary tools
have been retired.

Job reports live in `outputs/reports/<experiment>/<launch>/`, with an additional
mode folder for channel reports. Every summary writes a `performance/` bundle
beside its foundation table:
task-level inputs, raw/scaled MASE, reference-relative improvements, recorded
inference-time totals, and per-domain average tables (CSV, Markdown, LaTeX).
PNG/PDF figures show horizon-by-sampling-frequency loss and best-model maps,
per-domain loss bars, accuracy versus recorded inference time, and task mean
versus population standard deviation (one point per model/task). The relative
variance plot additionally requires positive matched Seasonal variance. Every
PNG has a same-stem PDF from the same figure; manifests list both. Heatmap
cells average task losses arithmetically; aggregate scaled MASE retains the
geometric mean. Relative outputs use matching Seasonal tasks, and ties remain
visible. Domain labels come from `src/timebench/config/dataset_domains.json`;
unmapped datasets are explicitly Unclassified.

Foundation task paths begin with the experiment and backbone. The two
ablations additionally put their tested value in the path:
`outputs/context_size/tasks/<backbone>/context_length/<value>/.../run_n` and
`outputs/instance_normalization/tasks/<backbone>/normalization/<mode>/.../run_n`.
This keeps concurrently submitted settings independent; `run_n` distinguishes
repetitions and remaining non-path configuration differences within one
setting.

Raw test inference is cached separately under
`outputs/<experiment>/inference/<backbone>/.../run_n/`. Its identity contains
only the test windows and model settings that can change the forecasts; it does
not contain `val_length`, report settings, metrics, or the Seasonal evaluation
grid. Task reductions under `tasks/` depend on that raw cache and the selected
grid, so metrics and reports can be rebuilt without repeating model inference.
The project does not perform validation-based model selection.

Lightweight synchronization/publication uses one shared file selector for report
bundles, compact stage metadata and timing JSON, excluding raw recovery arrays.
Both steps apply the same default per-file limit of 100000000 bytes, configurable
with `PUBLISH_MAX_FILE_BYTES`. `outputs/analysis/` holds separately requested
artifact analyses. Existing artifacts are not moved by report regeneration.
Each job logs allocated/visible devices, available GPU/host memory, and explicit
cgroup available/unavailable state before its stages; learned and CPU-only
stages also log the device they selected. Reporting uses headless Matplotlib;
dense accuracy/time comparisons use an external legend. Code synchronization preserves
Selena's environment and dependency manifests, so prepare that environment
independently before launching. The retired local leaderboard and sequential
all-model shells are no longer supported; use the launchers above.



## Documentation

- [Architecture](docs/architecture.md) describes ownership and execution flow.
- [Experiment catalog](docs/experiment_catalog.md) distinguishes runnable and
  planned experiment families.
- [Method overview](latex/method_overview.tex) states the evaluation questions.
- [Results recap](docs/results_recap.md) defines the current evidence boundary.
- [Scientific executive summary](latex/executive_summary.pdf) presents the
  current findings, mathematical task, essential protocols, tables, and plots
  ([LaTeX source](latex/executive_summary.tex)).
- [TIME dataset format](docs/DATASET_FORMAT.md) documents the inherited
  saved-Arrow representation.

## Source tree

```text
experiments/               inherited model/evaluation entry points
scripts/                   public experiment and analysis commands
slurm/                     DGX and Selena scheduler fronts
src/slurm/                 inherited workflows plus experiment schedule
src/timebench/             inherited reusable benchmark implementation
src/tests/                 shared and experiment-specific contract checks
docs/, latex/              architecture, protocol, and evidence documents
outputs/, logs/            ignored project-owned runtime artifacts
```

The code derives from the ICML 2026 TIME benchmark and remains under its
Apache-2.0 license.
