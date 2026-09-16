"""Temporary in-place refresh of compact dispersion from saved metric arrays."""

import argparse
import json
from pathlib import Path

import numpy as np

from timebench.evaluation.grid import EVALUATION_GRID_DEFINITION
from timebench.evaluation.metrics import summarize_metric_values


def refresh_task(summary_path: Path) -> None:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    with np.load(summary_path.with_name("metrics.npz")) as arrays:
        for name, current in summary["metrics"].items():
            statistics = summarize_metric_values(arrays[name], current["evaluation_values"])
            for field in ("std", "variance", "dispersion_ddof"):
                current[field] = statistics[field]
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def backfill(roots: list[Path]) -> int:
    summaries = set()
    for root in roots:
        if not root.is_dir():
            raise FileNotFoundError(root)
        for path in root.rglob("metrics_summary.json"):
            manifest = json.loads(path.with_name("manifest.json").read_text(encoding="utf-8"))
            summary = json.loads(path.read_text(encoding="utf-8"))
            if manifest["status"] != "completed":
                continue
            if summary.get("evaluation_grid", {}).get("definition") != EVALUATION_GRID_DEFINITION:
                continue
            summaries.add(path.resolve())
    # Fail before rewriting anything if a completed task lacks its raw metrics.
    for path in summaries:
        if not path.with_name("metrics.npz").is_file():
            raise FileNotFoundError(path.with_name("metrics.npz"))
    for path in sorted(summaries):
        refresh_task(path)
    return len(summaries)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_roots", type=Path, nargs="+")
    args = parser.parse_args()
    count = backfill(args.task_roots)
    print(f"Refreshed dispersion in {count} completed current-grid task summaries; no inference run.")


if __name__ == "__main__":
    main()
