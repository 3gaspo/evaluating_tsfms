#!/bin/bash
#SBATCH --job-name=seasonal_dispersion
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --time=01:00:00
#SBATCH --partition=an
#SBATCH --qos=an_preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8000
#SBATCH --wckey=P12CU:DATASCIENCE

set -euo pipefail
PROJECT_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
cd "$PROJECT_ROOT"
export PROJECT_ROOT
export TIME_SEASONAL_SCOPE=shared
source "$PROJECT_ROOT/src/slurm/selena_runtime.sh"
echo "Refreshing shared Seasonal tasks: $TIME_SEASONAL_TASKS_ROOT"
uv run --no-sync python src/scripts/backfill_seasonal_dispersion.py \
    --tasks-root "$TIME_SEASONAL_TASKS_ROOT" \
    --output "$TIME_OUTPUTS/analysis/seasonal_dispersion/task_summary.csv"
