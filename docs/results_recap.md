# Results recap

## Completed shared-grid foundation benchmark

The current Evaluating TSFMs artifact lineage covers 50 TIME dataset-frequency
configurations and 98 horizon tasks for each active foundation model. Scaled
MASE divides each task MASE by its matching Seasonal Naive MASE and takes the
geometric mean over tasks; lower is better. Inference seconds are summed model-
inference time and exclude loading, data construction, metrics, and artifact
saving. TimesFM-3 is intentionally excluded from the active experiment set.

| Model | Scaled MASE | Dataset-frequency IQR | Configurations below baseline | Learned-model task wins | Inference seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Chronos-2 | 0.685489 | 0.612–0.774 | 48/50 | 74/98 | 425.6 |
| TS-ICL | 0.718394 | 0.673–0.808 | 47/50 | 20/98 | 2,673.0 |
| Chronos-Bolt | 0.759559 | 0.694–0.842 | 47/50 | 4/98 | 934.5 |
| Seasonal Naive | 1.000000 | 1.000–1.000 | — | — | 654.6 |

Chronos-2 is the strongest active foundation model. Its aggregate scaled MASE
is 31.5% below Seasonal Naive, 4.6% below TS-ICL, and 9.8% below Chronos-Bolt.
Its advantage is broad rather than driven only by the geometric aggregate: it
wins 74 of the 98 paired learned-model tasks. TS-ICL and Chronos-Bolt require
6.28 and 2.20 times Chronos-2's summed inference time, respectively.

Every active learned model completed all 98 selected task manifests and is
finite on all 111,071 values in the shared Seasonal grid. The grid excludes
106 of the 111,177 total candidate values because their target or Seasonal
baseline support is not finite. Identical support makes the model ranking
directly comparable.

## Chronos-2 channel representation

The completed channel comparison covers the 38 multivariate dataset-frequency
configurations and 74 horizon tasks common to its three modes.

| Representation | Scaled MASE | Accuracy versus native | Paired task-ratio IQR | Inference seconds | Time versus native |
| --- | ---: | ---: | ---: | ---: | ---: |
| Native multivariate | 0.690045 | reference | 1.000–1.000 | 326.8 | 1.00x |
| Independent univariate | 0.695590 | 0.80% worse | 0.997–1.014 | 341.8 | 1.05x |
| Past targets as covariates | 0.690045 | equivalent | 1.000–1.000 | 1,870.6 | 5.72x |

Native multivariate forecasting wins 46 of the 74 paired tasks against
independent univariate forecasting; univariate wins 28. The aggregate native
advantage is only 0.8%, and the paired univariate/native MASE ratio has an IQR
of 0.997–1.014, so the effect is small and heterogeneous.

Past-target covariates reproduce native-multivariate accuracy to numerical
precision: their aggregate values agree to six decimals and the maximum
taskwise relative MASE difference is below `5.75e-7`. They require 5.72 times
the summed inference time, so this experiment provides no accuracy
justification for the more expensive representation.

All three modes completed 74 selected manifests and are finite on all 91,319
values in their shared grid. Their aggregate reports now complete successfully
against the separately generated Seasonal baseline; the earlier summary-
ordering race is resolved.

## Dataset-feature associations

The completed feature analysis joins dataset-level scaled MASE to 50
dataset-frequency feature rows per learned model. The strongest consistent
Spearman associations are higher temporal heterogeneity (`rho` from +0.42 to
+0.50), higher trend Hurst values (+0.36 to +0.44), higher temporal scale and
location heterogeneity (+0.33 to +0.44), and a negative association with the
second detected period (-0.33 to -0.43). These associations are exploratory,
not causal, and no multiplicity-adjusted significance analysis was performed.

## Limitations and next evidence

- Each scientific configuration has one selected run. Cross-task and cross-
  dataset dispersion does not measure stochastic repeat or seed variability.
- The lightweight artifact snapshot contains terminal logs, manifests,
  configurations, metric summaries, aggregate reports, and feature-analysis
  outputs, but omits task-level `predictions.npz` and `metrics.npz`. Completed
  manifests report those required payloads on Selena, but their contents were
  not independently inspected in this checkout.
- Covariate generalization beyond Chronos-2, input normalization, and context-
  size studies remain planned rather than evidenced.
