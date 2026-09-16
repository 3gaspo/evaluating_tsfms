"""Dependency-light regression for model-job statistics and their one-off refresh."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from timebench.evaluation.metrics import summarize_metric_values

SPEC = importlib.util.spec_from_file_location(
    "backfill_metric_dispersion", Path(__file__).parents[1] / "scripts/backfill_metric_dispersion.py"
)
REFRESH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFRESH)


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

    def test_refresh_matches_job_and_preserves_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory) / "run_1"
            task.mkdir()
            values = np.array([[[1.0, np.nan], [3.0, 5.0]]])
            original = {
                "launch_id": "selected_launch", "inference_seconds": 12.5,
                "evaluation_grid": {"definition": REFRESH.EVALUATION_GRID_DEFINITION},
                "metrics": {"MASE": {
                    "mean": 3.0, "finite_values": 3, "evaluation_values": 3, "total_values": 4,
                }},
            }
            summary = task / "metrics_summary.json"
            summary.write_text(json.dumps(original), encoding="utf-8")
            (task / "manifest.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
            np.savez_compressed(task / "metrics.npz", MASE=values)
            self.assertEqual(REFRESH.backfill([Path(directory)]), 1)
            updated = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(updated["metrics"]["MASE"], summarize_metric_values(values, 3))
            for key in ("launch_id", "inference_seconds", "evaluation_grid"):
                self.assertEqual(updated[key], original[key])
            self.assertEqual(REFRESH.backfill([Path(directory)]), 1)
            self.assertEqual(json.loads(summary.read_text(encoding="utf-8")), updated)

    def test_missing_arrays_fail_without_rewriting(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            summary = task / "metrics_summary.json"
            summary.write_text(json.dumps({
                "evaluation_grid": {"definition": REFRESH.EVALUATION_GRID_DEFINITION},
                "metrics": {},
            }), encoding="utf-8")
            (task / "manifest.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
            original = summary.read_text(encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                REFRESH.backfill([task])
            self.assertEqual(summary.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
