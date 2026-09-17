# Architecture

Evaluating TSFMs inherits dataset, model-adapter, covariate, metric, timing,
feature, task-manifest, Seasonal Naive, diagnostic, reporting, artifact, and
cluster-runtime behavior from Improved TIME. The `experiments/` Python entry
points call those common owners. Public commands in `scripts/` select an
experiment family and submit the inherited cluster fronts in `slurm/`, whose
workflow implementations live in `src/slurm/`. The project-owned
`foundation_model_schedule.sh` excludes TimesFM-3 without changing the shared
capability registry.

```text
saved-Arrow TIME dataset
        |
        v
src/timebench/evaluation + experiments/<model>.py
        |
        v
schema-1 task runs in outputs/<experiment>/tasks
        |
        +<-- reusable Seasonal Naive task store
        |
        +--> summary tables
        `--> feature-performance analysis
```

`src/timebench/pipeline/` owns run allocation, exact-configuration identity,
recovery, interruption, and result selection. `src/timebench/feature/` owns
dataset features and reusable association calculations. Experiment scripts
compose these components but do not redefine their contracts.

`src/timebench/results/performance.py` builds generic tables and report
bundles from already selected, repeat/configuration-reduced task statistics.
`src/timebench/visualization/performance.py` plots those aggregates without
reloading models or pooling metric cells. The compact-summary CLI composes
both owners and records every produced artifact in its report manifest.
`src/timebench/pipeline/runtime_resources.py` provides the compute-node
device/memory snapshot invoked once per allocation by the runtime shell.

The inherited Seasonal Naive producer can own a reusable shared task store or
a project-owned task store outside the learned-model and channel roots. Each
task also writes the common evaluation
grid: finite target steps and cells whose Seasonal Naive median and MASE are
finite. Consumers resolve that selected grid before inference, use it for
every metric, and reject non-finite forecasts on its support. Learned-model
jobs never write to the shared store, and summaries wait only for the learned
jobs belonging to their launch.

DGX and Selena retain independent environments and project-scoped output/log
roots. Code synchronization excludes every dataset, weight, output, log,
environment, and private lifecycle file. Results move only between execution
surfaces of this repository.
