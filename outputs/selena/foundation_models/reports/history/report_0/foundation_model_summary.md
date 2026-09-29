# Foundation-model benchmark summary

Each task MASE is divided by the matching Seasonal Naive MASE, then task ratios are combined with the TIME leaderboard geometric mean. Inference seconds are summed over the same test forecasting tasks; a blank total means at least one task lacks timing metadata.

| Model | Target mode | State | Exit | Scaled MASE (GM) | Inference seconds | Datasets | Tasks | Timed tasks | MASE finite/grid/total | Prediction NaNs/values |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| chronos2 |  | failed | 1 |  |  | 0 | 0 | 0 | 0/0/0 | 0/0 |
| chronos_bolt |  | failed | 1 |  |  | 0 | 0 | 0 | 0/0/0 | 0/0 |
| seasonal_naive |  | completed | 0 |  |  | 0 | 0 | 0 | 0/0/0 | 0/0 |
| ts_icl |  | failed | 1 |  |  | 0 | 0 | 0 | 0/0/0 | 0/0 |
