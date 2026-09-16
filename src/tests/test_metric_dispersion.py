"""Dependency-light regression for the maintained model-job statistics."""

from pathlib import Path
import unittest
import importlib.util
import json
import tempfile

import numpy as np

from timebench.evaluation.metrics import summarize_metric_values


class MetricDispersionTest(unittest.TestCase):
    def test_population_statistics_and_empty_support(self):
        values = np.array([[[1.0, np.nan], [3.0, np.inf]]])
        result = summarize_metric_values(values, 3)
        self.assertEqual(result, {
            "mean": 2.0, "std": 1.0, "variance": 1.0, "dispersion_ddof": 0,
            "finite_values": 2, "evaluation_values": 3, "total_values": 4,
        })
        empty = summarize_metric_values(np.array([np.nan]), 0)
        for field in ("mean", "std", "variance"):
            self.assertIsNone(empty[field])
        self.assertEqual(summarize_metric_values(np.array([7.0]), 1)["std"], 0.0)

    def test_mean_is_unchanged_and_saver_uses_shared_statistics(self):
        values = np.array([1.0, 2.0, 7.0, np.nan], dtype=np.float32)
        result = summarize_metric_values(values, 3)
        self.assertEqual(result["mean"], float(np.mean(values[np.isfinite(values)])))
        self.assertAlmostEqual(result["std"] ** 2, result["variance"])
        saver = Path(__file__).parents[1] / "timebench/evaluation/saver.py"
        self.assertIn("metric_summaries[metric_name] = summarize_metric_values(", saver.read_text(encoding="utf-8"))
        seasonal = Path(__file__).parents[2] / "experiments/seasonal_naive.py"
        self.assertIn("create_evaluation_grid=True", seasonal.read_text(encoding="utf-8"))

    def test_shared_seasonal_refresh_preserves_existing_fields(self):
        script = Path(__file__).parents[1] / "scripts/backfill_seasonal_dispersion.py"
        spec = importlib.util.spec_from_file_location("seasonal_refresh", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = {"evaluation_grid": {"definition": "finite_ground_truth_and_seasonal_naive_mase"},
                       "metrics": {"MASE": {"mean": 2.0, "finite_values": 2, "total_values": 3}},
                       "inference_seconds": 7.0}
            path = root / "metrics_summary.json"
            path.write_text(json.dumps(summary), encoding="utf-8")
            (root / "manifest.json").write_text(json.dumps({"status": "completed", "identity": {
                "model": "seasonal_naive", "dataset": "test", "frequency": "D", "term": "short"}}))
            np.savez(root / "metrics.npz", MASE=np.array([[[1.0, 3.0, np.nan]]]))
            np.savez(root / "evaluation_grid.npz", schema_version=1,
                     evaluation_mask=np.array([[[True, True, False]]]), target_mask=np.ones((1, 1, 3, 1), dtype=bool))
            row = module.refresh_task(path)
            updated = json.loads(path.read_text())
            self.assertEqual(row["variance"], 1.0)
            self.assertEqual(row["std"], 1.0)
            self.assertEqual(updated["inference_seconds"], 7.0)
            for key, value in summary["metrics"]["MASE"].items():
                self.assertEqual(updated["metrics"]["MASE"][key], value)


if __name__ == "__main__":
    unittest.main()
