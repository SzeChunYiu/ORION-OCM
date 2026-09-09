#!/usr/bin/env bash
#SBATCH -J zoo-gateceil
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:30:00
#SBATCH -c 1
#SBATCH -o logs/gateceil_%j.out
#SBATCH -e logs/gateceil_%j.err
# GATE-CEILING census (FREEZE_V1_AMEND_5 prerequisite, UNSCORED truth): third
# exact T2 pass over the census bound, computing per-axis per-cell MAX dev so
# any candidate admission bar's reachable own-axis recovery CEILING is known
# before the bar is frozen.  Hard-asserts parity with CENSUS_P00C/HZD9 truth
# (Pareto digests, D2d/D3d cells, feasible count, q0.5 == HZD9 quality bar).
# P00C/HZD9 walls were ~157 s; 30 min is ample.
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/gate_ceiling.py "$ZOO_ROOT"
echo "GATE CEILING DONE"
