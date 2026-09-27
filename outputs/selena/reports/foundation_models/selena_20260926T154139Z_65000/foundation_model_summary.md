# Foundation-model benchmark summary

Each task MASE is divided by the matching Seasonal Naive MASE, then task ratios are combined with the TIME leaderboard geometric mean. Inference seconds are summed over the same test forecasting tasks; a blank total means at least one task lacks timing metadata.

| Model | Target mode | State | Exit | Scaled MASE (GM) | Inference seconds | Datasets | Tasks | Timed tasks | MASE finite/grid/total | Prediction NaNs/values |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| chronos2 | multivariate,univariate | completed | 0 | 0.685489 | 438.922 | 50 | 98 | 98 | 111071/111071/111177 | 0/69425883 |
| ts_icl | univariate | completed | 0 | 0.718394 | 2683.587 | 50 | 98 | 98 | 111071/111071/111177 | 0/69425883 |
| chronos_bolt | univariate | completed | 0 | 0.759559 | 953.397 | 50 | 98 | 98 | 111071/111071/111177 | 0/69425883 |
| seasonal_naive | univariate | completed | 0 | 1.000000 | 653.031 | 50 | 98 | 98 | 111071/111071/111177 | 0/69425883 |
