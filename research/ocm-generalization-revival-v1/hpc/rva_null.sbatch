#!/usr/bin/env bash
#SBATCH -J rva-null
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 01:00:00
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH --array=0-5
#SBATCH -o /home/scyiu/zoo221/rva/logs/null_%A_%a.out
#SBATCH -e /home/scyiu/zoo221/rva/logs/null_%A_%a.err
set -euo pipefail
ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs_r2}"
OUTDIR="$HOME/zoo221/rva/null"
mkdir -p "$OUTDIR"
SEED="${SLURM_ARRAY_TASK_ID}"
cd "$ZOO_ROOT"
echo "seed=$SEED host=$(hostname) freeze=e9566c31663a405e0fb207af1407bf0bd100d202774aa9766d71f9f362340b5c"
python3 "$HOME/zoo221/rva/rva_null.py" "$ZOO_ROOT" "$SEED" 400000 "$OUTDIR/RVA_NULL_s${SEED}.json"
