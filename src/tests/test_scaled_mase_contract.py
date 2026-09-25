"""Focused regression checks for finite-pair and scaled-MASE behavior."""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import warnings
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = PROJECT_ROOT / "src/timebench/evaluation/metrics.py"
SPEC = importlib.util.spec_from_file_location("timebench_metrics", METRICS_PATH)
assert SPEC is not None and SPEC.loader is not None
METRICS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(METRICS)

PIPELINE = types.ModuleType("timebench.pipeline")
PIPELINE.select_completed_runs = lambda *args, **kwargs: []
PIPELINE.parse_config_filters = lambda values: {}
sys.modules.setdefault("timebench", types.ModuleType("timebench"))
sys.modules["timebench.pipeline"] = PIPELINE
PERFORMANCE_PATH = PROJECT_ROOT / "src/timebench/feature/performance.py"
PERFORMANCE_SPEC = importlib.util.spec_from_file_location(
    "timebench_feature_performance", PERFORMANCE_PATH
)
assert PERFORMANCE_SPEC is not None and PERFORMANCE_SPEC.loader is not None
PERFORMANCE = importlib.util.module_from_spec(PERFORMANCE_SPEC)
PERFORMANCE_SPEC.loader.exec_module(PERFORMANCE)

PATHS = types.ModuleType("timebench.paths")
PATHS.foundation_experiment_root = lambda: Path(".")
PATHS.outputs_root = lambda: Path(".")
PATHS.foundation_experiment_name = lambda experiment=None: experiment or "foundation_models"
sys.modules["timebench.paths"] = PATHS
SUMMARY_PATH = PROJECT_ROOT / "scripts/compute_foundation_summary.py"
SUMMARY_SPEC = importlib.util.spec_from_file_location(
    "timebench_foundation_summary", SUMMARY_PATH
)
assert SUMMARY_SPEC is not None and SUMMARY_SPEC.loader is not None
SUMMARY = importlib.util.module_from_spec(SUMMARY_SPEC)
SUMMARY_SPEC.loader.exec_module(SUMMARY)

RESULTS_PATH = PROJECT_ROOT / "src/timebench/results/performance.py"
RESULTS_SPEC = importlib.util.spec_from_file_location(
    "timebench_results_performance", RESULTS_PATH
)
assert RESULTS_SPEC is not None and RESULTS_SPEC.loader is not None
RESULTS = importlib.util.module_from_spec(RESULTS_SPEC)
RESULTS_SPEC.loader.exec_module(RESULTS)


def main() -> None:
    # Removing the internal NaN would incorrectly produce mean(|3-1|, |4-3|)=1.5.
    context = np.asarray([1.0, np.nan, 3.0, 4.0, np.nan])
    assert METRICS.seasonal_naive_scale(context, 1) == 1.0
    assert METRICS.seasonal_naive_scale(context, 1, squared=True) == 1.0

    predictions = np.asarray([[[[[1.0, np.nan, 5.0]]]]])
    ground_truth = np.asarray([[[[1.0, 3.0, 3.0]]]])
    metric_context = np.asarray([[[[0.0, 1.0, 2.0]]]])
    metrics = METRICS.compute_per_window_metrics_from_quantiles(
        predictions,
        ground_truth,
        metric_context,
        quantile_levels=[0.5],
    )
    assert metrics["MAE"][0, 0, 0] == 1.0
    assert metrics["MSE"][0, 0, 0] == 2.0
    assert metrics["ND"][0, 0, 0] == 0.5
    invalid_predictions = predictions.copy()
    invalid_predictions[0, 0, 0, 0, 1] = np.inf
    try:
        METRICS.compute_per_window_metrics_from_quantiles(
            invalid_predictions,
            ground_truth,
            metric_context,
            quantile_levels=[0.5],
        )
    except ValueError as error:
        assert "infinite forecast" in str(error)
    else:
        raise AssertionError("infinite forecasts must remain invalid")

    for runner in ("chronos2.py", "chronos_bolt.py", "ts_icl.py", "run_timesfm3.py"):
        source = (PROJECT_ROOT / "experiments" / runner).read_text(encoding="utf-8")
        ast.parse(source)
        assert 'foundation_experiment_root("foundation_models").parent / "inference"' in source
        assert '"foundation_models_raw_inference"' in source

    summary = (PROJECT_ROOT / "scripts/compute_foundation_summary.py").read_text(
        encoding="utf-8"
    )
    channel = (PROJECT_ROOT / "src/slurm/run_chronos2_comparison.sh").read_text(
        encoding="utf-8"
    )
    assert "scaled_MASE" in summary
    assert "geometric_mean_over_tasks" in summary
    assert "MASE_finite_values" in summary
    assert "--seasonal-naive-results-dir" in channel
    ast.parse(summary)

    repeated_cells = [
        {
            "model": "model_a",
            "base_model": "model_a",
            "target_mode": "univariate",
            "dataset_id": "toy/H",
            "horizon": "short",
            "MASE": mase,
            "MASE_std": mase / 2,
            "MASE_variance": mase ** 2 / 4,
            "MASE_finite_values": finite,
            "MASE_evaluation_values": total,
            "MASE_total_values": total,
            "prediction_nan_values": total - finite,
            "prediction_values": total,
            "evaluation_grid": {"definition": "toy"},
            "inference_seconds": 1.0,
            "scientific_config": {"value": 1},
        }
        for mase, finite, total in ((1.0, 2, 3), (3.0, 3, 4))
    ]
    effective = SUMMARY._effective_cells(repeated_cells)
    assert len(effective) == 1
    assert effective[0]["MASE"] == 2.0
    assert effective[0]["MASE_finite_values"] == 5
    assert effective[0]["MASE_total_values"] == 7
    assert effective[0]["prediction_nan_values"] == 2
    assert effective[0]["prediction_values"] == 7

    report_tasks = RESULTS.prepare_tasks([
        {
            "model": model,
            "dataset": dataset,
            "frequency": "H",
            "term": "short",
            "horizon_steps": 2,
            "MASE": loss,
            "scaled_MASE": loss,
            "inference_seconds": 1.0,
            "prediction_nan_values": nan_values,
            "prediction_values": 3,
        }
        for model, dataset, loss, nan_values in (
            ("seasonal_naive", "a", 1.0, 0),
            ("seasonal_naive", "b", 1.0, 0),
            ("candidate", "a", 0.5, 1),
            ("candidate", "b", np.nan, 3),
        )
    ], domains={"a": "Toy", "b": "Toy"})
    _, report_summary, _ = RESULTS.build_performance_tables(
        report_tasks, reference="seasonal_naive"
    )
    candidate = report_summary.set_index("model").loc["candidate"]
    assert candidate["finite_MASE_tasks"] == 1
    assert candidate["mean_task_MASE"] == 0.5
    assert candidate["relative_tasks"] == 1
    assert candidate["prediction_nan_values"] == 4
    assert candidate["prediction_values"] == 6

    frame = pd.DataFrame(
        {
            "dataset_id": ["a", "b", "c", "d"] * 2,
            "model": ["seasonal_naive"] * 4 + ["chronos2"] * 4,
            "feature": [1.0, 2.0, 3.0, 4.0] * 2,
            "scaled_MASE": [1.0] * 4 + [4.0, 3.0, 2.0, 1.0],
        }
    )
    with warnings.catch_warnings(record=True) as caught:
        correlations = PERFORMANCE.feature_correlations(frame, ["feature"])
    seasonal = correlations[correlations["model"] == "seasonal_naive"].iloc[0]
    learned = correlations[correlations["model"] == "chronos2"].iloc[0]
    mean = correlations[correlations["model"] == "mean_absolute"].iloc[0]
    assert np.isnan(seasonal["spearman_rho"])
    assert np.isclose(learned["spearman_rho"], -1.0)
    assert np.isclose(mean["spearman_rho"], 1.0)
    assert not caught
    print("Finite-pair, scaled-MASE, and constant-correlation contracts passed.")


if __name__ == "__main__":
    main()
