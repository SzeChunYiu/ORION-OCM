#!/usr/bin/env bash
#SBATCH -J zoo-poet
#SBATCH -A snic2025-22-104
#SBATCH -p cosmos
#SBATCH -t 01:00:00
#SBATCH -c 1
#SBATCH --array=0-0%8
#SBATCH -o logs/poet_%A_%a.out
#SBATCH -e logs/poet_%A_%a.err
# MZ-D8 POET tranche.  GATED: not opened; POET/META only after fixed-ecology
# calibration (#221 sec 10 ladder).
source "$(dirname "$0")/common_env.sh"
echo "GATED: MZ-D8 POET tranche not opened (PROTOCOL_V1.md); refusing"
exit 3
