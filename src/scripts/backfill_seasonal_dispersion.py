"""Temporary refresh of shared Seasonal statistics without forecasting."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from timebench.evaluation.grid import EVALUATION_GRID_DEFINITION, load_evaluation_grid
from timebench.evaluation.metrics import summarize_metric_values


def refresh_task(path: Path) -> dict:
    manifest = json.loads(path.with_name("manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed"
    assert manifest["identity"]["model"] == "seasonal_naive"
    summary = json.loads(path.read_text(encoding="utf-8"))
    assert summary["evaluation_grid"]["definition"] == EVALUATION_GRID_DEFINITION
    _, mask = load_evaluation_grid(path.with_name("evaluation_grid.npz"))
    with np.load(path.with_name("metrics.npz"), allow_pickle=False) as arrays:
        for name, current in summary["metrics"].items():
            values = arrays[name]
            assert values.shape == mask.shape
            assert not np.any(np.isfinite(values) & ~mask)
            statistics = summarize_metric_values(values, int(mask.sum()))
            assert statistics["finite_values"] == current["finite_values"]
            assert statistics["total_values"] == current["total_values"]
            assert (current["mean"] is None and statistics["mean"] is None) or np.isclose(
                current["mean"], statistics["mean"], rtol=1e-12, atol=1e-12)
            for field in ("std", "variance", "dispersion_ddof"):
                current[field] = statistics[field]
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    metric = summary["metrics"]["MASE"]
    identity = manifest["identity"]
    return {**{key: identity[key] for key in ("dataset", "frequency", "term")},
            **{key: metric[key] for key in ("mean", "std", "variance", "dispersion_ddof", "finite_values")},
            "manifest": str(path.with_name("manifest.json")),
            "evaluation_grid": str(path.with_name("evaluation_grid.npz"))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.tasks_root.resolve() / "seasonal_naive"
    if not root.is_dir():
        raise FileNotFoundError(root)
    paths = []
    for path in sorted(root.rglob("metrics_summary.json")):
        manifest = json.loads(path.with_name("manifest.json").read_text(encoding="utf-8"))
        summary = json.loads(path.read_text(encoding="utf-8"))
        if manifest["status"] == "completed" and summary.get("evaluation_grid", {}).get("definition") == EVALUATION_GRID_DEFINITION:
            paths.append(path)
    if not paths:
        raise ValueError(f"No completed current-grid Seasonal tasks in {root}")
    for path in paths:
        for name in ("metrics.npz", "evaluation_grid.npz"):
            if not path.with_name(name).is_file():
                raise FileNotFoundError(path.with_name(name))
    rows = [refresh_task(path) for path in paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {len(rows)} shared Seasonal summaries; means unchanged; no inference.")
    print(f"Lightweight-sync diagnostic table: {args.output}")


if __name__ == "__main__":
    main()
