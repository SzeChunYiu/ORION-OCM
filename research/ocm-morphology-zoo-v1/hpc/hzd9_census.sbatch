#!/usr/bin/env bash
#SBATCH -J zoo-hzd9
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:30:00
#SBATCH -c 1
#SBATCH -o logs/hzd9_%j.out
#SBATCH -e logs/hzd9_%j.err
# HZD9 census (FREEZE_V1_AMEND_4 prerequisite, UNSCORED truth): exact T2 pass
# over the whole census bound with the MZ-D9 lens (collapse, quality bar,
# descriptor purity/eta^2, island-region tables).  Hard-asserts parity with
# CENSUS_P00C truth (Pareto digests, D2d/D3d cells, feasible count) — a free
# whole-stack determinism audit.  P00C wall was 157 s; 30 min is ample.
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/hzd9_census.py "$ZOO_ROOT"
echo "HZD9 CENSUS DONE"
