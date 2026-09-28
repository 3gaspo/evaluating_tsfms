#!/usr/bin/env python3
"""Remove obsolete synchronized paths before the current Selena refresh.

Run once on DGX after pulling this revision and before synchronizing the three
active projects. It removes only paths superseded by the artifact migration;
current experiment caches outside those paths are retained. Delete this script
after the refreshed artifacts have been published.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


LEGACY_DIRECTORIES = {
    "evaluating_tsfms": (
        "outputs/selena/foundation_models/inference/seasonal_naive",
        "outputs/selena/foundation_models/tasks/seasonal_naive",
        "outputs/selena/reports",
        "logs/selena",
    ),
    "selectime": (
        "outputs/selena/selectime",
        "outputs/selena/reports",
        "logs/selena",
    ),
    "tsrag_time": (
        "outputs/selena/tsrag/reports",
        "logs/selena",
    ),
}


def remove(path: Path, dry_run: bool) -> None:
    if not path.exists() and not path.is_symlink():
        return
    print(f"{'PLAN' if dry_run else 'REMOVE'}: {path}")
    if dry_run:
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--projects-root",
        type=Path,
        default=Path.home() / "codes",
        help="Directory containing evaluating_tsfms, selectime, and tsrag_time",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    projects_root = args.projects_root.expanduser().resolve()

    for project, relative_paths in LEGACY_DIRECTORIES.items():
        project_root = (projects_root / project).resolve()
        if project_root.parent != projects_root or not (project_root / ".git").is_dir():
            raise FileNotFoundError(f"Expected project checkout: {project_root}")
        for relative in relative_paths:
            target = (project_root / relative).resolve()
            if project_root not in target.parents:
                raise ValueError(f"Refusing path outside {project_root}: {target}")
            remove(target, args.dry_run)
        outputs = project_root / "outputs/selena"
        if outputs.is_dir():
            for config in sorted(outputs.rglob("config.json")):
                if config.parent.name.startswith("run_"):
                    remove(config, args.dry_run)


if __name__ == "__main__":
    main()
