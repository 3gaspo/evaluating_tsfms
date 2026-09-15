# Foundation-model benchmark summary

Each task MASE is divided by the matching Seasonal Naive MASE, then task ratios are combined with the TIME leaderboard geometric mean. Inference seconds are summed over the same test forecasting tasks; a blank total means at least one task lacks timing metadata.

| Model | Target mode | State | Exit | Scaled MASE (GM) | Inference seconds | Datasets | Tasks | Timed tasks | MASE finite/total |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| chronos2 | univariate | completed | 0 | 0.690045 | 1858.213 | 38 | 74 | 74 | 91319/91425 |
