#!/usr/bin/env bash
#SBATCH -J zoo-isl
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 01:00:00
#SBATCH -c 1
#SBATCH --array=0-0%8
#SBATCH -o logs/isl_%A_%a.out
#SBATCH -e logs/isl_%A_%a.err
# MZ-D8 islands tranche.  GATED: not opened in this tranche.
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
echo "GATED: MZ-D8 islands tranche not opened (PROTOCOL_V1.md); refusing"
exit 3
