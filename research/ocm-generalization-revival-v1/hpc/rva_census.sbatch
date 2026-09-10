#!/usr/bin/env bash
#SBATCH -J rva-census
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 02:00:00
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH --array=0-239%96
#SBATCH -o /home/scyiu/zoo221/rva/logs/cen_%A_%a.out
#SBATCH -e /home/scyiu/zoo221/rva/logs/cen_%A_%a.err
set -euo pipefail
ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs_r2}"
OUTDIR="$HOME/zoo221/rva/census"
mkdir -p "$OUTDIR"
I="${SLURM_ARRAY_TASK_ID}"; N=240
cd "$ZOO_ROOT"
echo "shard=$I/$N host=$(hostname)"
python3 "$HOME/zoo221/rva/rva_census.py" "$ZOO_ROOT" "$I" "$N" \
  "$OUTDIR/RVA_CENSUS_sh${I}.json" "$OUTDIR/RVA_CENSUS_sh${I}.jsonl"
