# Results recap

## First project-owned Selena evidence

The first Evaluating TSFMs artifact lineage covers 50 TIME dataset-frequency
configurations and 98 horizon tasks for each completed foundation model.
Scaled MASE divides each task MASE by its matching Seasonal Naive MASE and
takes the geometric mean over tasks; lower is better. Inference seconds are
summed model-inference time and exclude loading, data construction, metrics,
and artifact saving.

| Model | Scaled MASE | Task IQR | Tasks below baseline | Inference seconds |
| --- | ---: | ---: | ---: | ---: |
| Chronos-2 | 0.685489 | 0.634–0.797 | 96/98 | 427.1 |
| TS-ICL | 0.718394 | 0.650–0.817 | 94/98 | 2,670.5 |
| Chronos-Bolt | 0.759559 | 0.691–0.864 | 91/98 | 942.2 |
| Seasonal Naive | 1.000000 | 1.000–1.000 | — | 653.0 |

Chronos-2 is the strongest completed foundation model: its aggregate scaled
MASE is 4.6% below TS-ICL and 9.8% below Chronos-Bolt. TimesFM-3 has no result;
its evaluator stopped before inference because the local safetensors checkpoint
was incomplete. The aggregate report therefore contains the four available
rows but the five-model feature plot did not run.

## Chronos-2 channel representation

The channel comparison covers the 38 multivariate dataset-frequency
configurations and 74 horizon tasks common to its three modes.

| Representation | Scaled MASE | Task IQR | Tasks below baseline | Inference seconds |
| --- | ---: | ---: | ---: | ---: |
| Native multivariate | 0.690045 | 0.639–0.789 | 72/74 | 342.7 |
| Independent univariate | 0.695590 | 0.639–0.807 | 72/74 | 341.7 |
| Past targets as covariates | 0.690045 | 0.639–0.789 | 72/74 | 1,858.2 |

Native multivariate forecasting has 0.8% lower geometric scaled MASE than
independent univariate forecasting and wins 46 of the 74 paired tasks, while
independent univariate wins 28. The taskwise ratio has an interquartile range
of 0.987–1.003, so the aggregate advantage is small and heterogeneous.

Past-target covariates reproduce native-multivariate accuracy to numerical
precision: their aggregate values agree to six decimals and the maximum
taskwise relative MASE difference is below `6e-7`. They require 5.4 times the
summed inference time, so this run provides no accuracy justification for the
more expensive representation. The native-multivariate and independent-
univariate summary jobs in the first launch ran before their Seasonal Naive
baseline completed. The task metrics above were analyzed after synchronization,
but their official summary artifacts still need regeneration. The corrected
launch contract consumes a separately precomputed shared baseline, removing
that ordering race.

## Limitations and next evidence

- Each scientific configuration has one `run_0`; the IQRs describe variation
  across TIME tasks, not stochastic repeat or seed variability.
- The four completed foundation models each contain 111,071 finite MASE values
  out of 111,177. Each channel mode contains 91,319 out of 91,425. Aggregates
  use the finite values recorded by the task metric contract.
- The lightweight artifact snapshot omits task-level prediction and metric
  arrays. Terminal logs and completed manifests report them on the execution
  host, but this checkout could verify only configs and metric summaries.
- TimesFM-3 must be completed before the five-model ranking and feature-
  performance analysis are complete. Dataset-diagnostic evidence is also not
  yet available.
- Covariate generalization beyond Chronos-2, input normalization, and context-
  size studies remain planned rather than evidenced.
