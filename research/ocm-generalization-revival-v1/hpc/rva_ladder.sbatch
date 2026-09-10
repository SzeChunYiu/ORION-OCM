#!/usr/bin/env bash
#SBATCH -J rva-ladder
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:40:00
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH --array=1-5
#SBATCH -o /home/scyiu/zoo221/rva/logs/lad_%A_%a.out
#SBATCH -e /home/scyiu/zoo221/rva/logs/lad_%A_%a.err
set -euo pipefail
ZOO_ROOT="$HOME/zoo221/gs_r2"
cd "$ZOO_ROOT"
S="${SLURM_ARRAY_TASK_ID}"
python3 "$HOME/zoo221/rva/rva_ladder.py" "$ZOO_ROOT" "$S" 120000 \
  "$HOME/zoo221/rva/RVA_LADDER_s${S}.json"
