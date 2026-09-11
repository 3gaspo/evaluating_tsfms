# Architecture

Evaluating TSFMs inherits dataset, model-adapter, covariate, metric, timing,
feature, and task-manifest behavior from Improved TIME. The `experiments/`
Python entry points call those common owners. Public commands in `scripts/`
select an experiment family and submit the cluster fronts in `slurm/`, whose
workflow implementations live in `src/slurm/`.

```text
saved-Arrow TIME dataset
        |
        v
src/timebench/evaluation + experiments/<model>.py
        |
        v
schema-1 task runs in outputs/<experiment>/tasks
        |
        +--> summary tables
        `--> feature-performance analysis
```

`src/timebench/pipeline/` owns run allocation, exact-configuration identity,
recovery, interruption, and result selection. `src/timebench/feature/` owns
dataset features and reusable association calculations. Experiment scripts
compose these components but do not redefine their contracts.

DGX and Selena retain independent environments and project-scoped output/log
roots. Code synchronization excludes every dataset, weight, output, log,
environment, and private lifecycle file. Results move only between execution
surfaces of this repository.
