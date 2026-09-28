#!/usr/bin/env python3
"""One-time migration of the shared Seasonal Naive store.

Run on Selena after pulling this revision. The script is idempotent, refuses
to overwrite different files, rewrites authoritative manifests, and keeps
manifest history and launch metadata intact. Delete it after every retained
shared Seasonal store has been migrated.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


RUN = re.compile(r"run_\d+$")


class Migration:
    def __init__(self, root: Path, dry_run: bool):
        self.root = root.expanduser().resolve()
        self.dry_run = dry_run
        self.replacements: list[tuple[str, str]] = []
        self.actions = 0

    def note(self, message: str) -> None:
        print(f"{'PLAN' if self.dry_run else 'APPLY'}: {message}")
        self.actions += 1

    def move(self, source: Path, target: Path) -> None:
        source = source.resolve()
        target = target.resolve()
        if source == target:
            return
        replacement = (str(source), str(target))
        if replacement not in self.replacements:
            self.replacements.append(replacement)
        if not source.exists():
            return
        self.note(f"move {source} -> {target}")
        if self.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            source.replace(target)
            return
        if source.is_file() or target.is_file():
            if source.is_file() and target.is_file() and source.read_bytes() == target.read_bytes():
                source.unlink()
                return
            raise FileExistsError(f"Refusing to overwrite different artifact: {target}")
        for child in sorted(source.iterdir(), key=lambda path: path.name):
            self.move(child, target / child.name)
        source.rmdir()

    def remove_empty(self, root: Path) -> None:
        if self.dry_run or not root.exists():
            return
        for path in sorted(
            (item for item in root.rglob("*") if item.is_dir()),
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            if path.exists() and not any(path.iterdir()):
                path.rmdir()

    def rewrite_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self.rewrite_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.rewrite_value(item) for item in value]
        if isinstance(value, str):
            for source, target in sorted(
                self.replacements, key=lambda item: len(item[0]), reverse=True
            ):
                value = value.replace(source, target)
                value = value.replace(source.replace("\\", "/"), target.replace("\\", "/"))
        return value

    @staticmethod
    def write_json(path: Path, value: Any) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temporary.replace(path)

    def migrate_run_configs(self) -> None:
        outputs = self.root / "outputs/seasonal_naive"
        for config_path in sorted(outputs.rglob("config.json")):
            manifest_path = config_path.parent / "manifest.json"
            if not RUN.fullmatch(config_path.parent.name) or not manifest_path.is_file():
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config.pop("launch_id", None)
            metadata = manifest.setdefault("artifact_metadata", {})
            existing = metadata.get("evaluation")
            if existing is not None and existing != config:
                raise ValueError(f"Conflicting evaluation metadata in {manifest_path}")
            metadata["evaluation"] = config
            manifest["required_artifacts"] = [
                name
                for name in manifest.get("required_artifacts", [])
                if Path(name).name != "config.json"
            ]
            self.note(f"move run configuration into {manifest_path}")
            if not self.dry_run:
                self.write_json(manifest_path, manifest)
                config_path.unlink()

    def rewrite_json(self) -> None:
        outputs = self.root / "outputs/seasonal_naive"
        for path in sorted(outputs.rglob("*.json")):
            if "manifest_history" in path.parts or path.name == "config.json":
                continue
            try:
                current = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            updated = self.rewrite_value(current)
            if isinstance(updated, dict) and path.name == "manifest.json":
                updated["experiment"] = (
                    "seasonal_naive_inference"
                    if "inference" in path.parts
                    else "seasonal_naive"
                )
            if isinstance(updated, dict) and updated.get("experiment") == "foundation_models":
                updated["experiment"] = "seasonal_naive"
            if updated != current:
                self.note(f"rewrite {path}")
                if not self.dry_run:
                    self.write_json(path, updated)

    def rewrite_logs(self) -> None:
        logs = self.root / "logs/seasonal_naive"
        if not logs.is_dir() or self.dry_run:
            return
        for path in sorted(item for item in logs.rglob("*") if item.is_file()):
            try:
                current = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            updated = self.rewrite_value(current)
            updated = updated.replace("experiment=foundation_models", "experiment=seasonal_naive")
            if updated != current:
                self.note(f"rewrite {path}")
                path.write_text(updated, encoding="utf-8")

    def run(self) -> None:
        old_outputs = self.root / "foundation_models"
        new_outputs = self.root / "outputs/seasonal_naive"
        self.move(
            old_outputs / "inference/seasonal_naive",
            new_outputs / "inference",
        )
        self.move(
            old_outputs / "tasks/seasonal_naive",
            new_outputs / "evaluations",
        )
        self.move(
            self.root / "logs/foundation_models",
            self.root / "logs/seasonal_naive",
        )
        self.move(
            self.root / "logs/seasonal_naive/workflow_status/foundation_models",
            self.root / "logs/seasonal_naive/workflow_status/seasonal_naive",
        )
        self.remove_empty(old_outputs)
        self.migrate_run_configs()
        self.rewrite_json()
        self.rewrite_logs()


def default_root() -> Path:
    nni_file = Path(os.environ.get("TIME_NNI_FILE", Path.home() / "codes/.secrets/nni"))
    nni = nni_file.read_text(encoding="utf-8").splitlines()[0].strip().lower()
    if re.fullmatch(r"[a-z][a-z0-9_-]*", nni) is None:
        raise ValueError(f"Invalid NNI in {nni_file}")
    return Path("/scratch/users") / nni / "codes/seasonal"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    migration = Migration(args.root or default_root(), args.dry_run)
    migration.run()
    print(f"{'Planned' if args.dry_run else 'Completed'} {migration.actions} migration actions")


if __name__ == "__main__":
    main()
