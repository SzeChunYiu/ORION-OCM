#!/usr/bin/env bash
#SBATCH -J zoo-agg
#SBATCH -A snic2025-22-104
#SBATCH -p cosmos
#SBATCH -t 00:20:00
#SBATCH -c 1
#SBATCH -o logs/agg_%j.out
#SBATCH -e logs/agg_%j.err
source "$(dirname "$0")/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/aggregate.py "$ZOO_ROOT"
