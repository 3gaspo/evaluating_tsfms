# Foundation-model benchmark summary

Each task MASE is divided by the matching Seasonal Naive MASE, then task ratios are combined with the TIME leaderboard geometric mean. Inference seconds are summed over the same test forecasting tasks; a blank total means at least one task lacks timing metadata.

| Model | Target mode | State | Exit | Scaled MASE (GM) | Inference seconds | Datasets | Tasks | Timed tasks | MASE finite/grid/total |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| chronos2__experiment_config.instance_normalization-none | multivariate,univariate | completed | 0 | 0.685489 | 434.594 | 50 | 98 | 98 | 111071/111071/111177 |
| chronos2__experiment_config.instance_normalization-zscore | multivariate,univariate | completed | 0 | 0.685489 | 431.707 | 50 | 98 | 98 | 111071/111071/111177 |
| ts_icl__experiment_config.instance_normalization-zscore | univariate | completed | 0 | 0.718394 | 2686.796 | 50 | 98 | 98 | 111071/111071/111177 |
| ts_icl__experiment_config.instance_normalization-none | univariate | completed | 0 | 0.718394 | 2681.103 | 50 | 98 | 98 | 111071/111071/111177 |
| chronos_bolt__experiment_config.instance_normalization-zscore | univariate | completed | 0 | 0.759558 | 1001.577 | 50 | 98 | 98 | 111071/111071/111177 |
| chronos_bolt__experiment_config.instance_normalization-none | univariate | completed | 0 | 0.759559 | 945.597 | 50 | 98 | 98 | 111071/111071/111177 |
