#!/bin/bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -t 02:00:00
#SBATCH -J fo_d26
#SBATCH -o %x_%j.out
#SBATCH -e %x_%j.err
# D26 cross-domain operator transfer matrix (4 operators x 3 domains).
set -u
# Stage from SCRATCH, not $HOME. Home carries a per-user quota that df cannot
# see -- it reported 134T free on the same filesystem while a write failed with
# "Disk quota exceeded" -- and lfs quota and quota are both unavailable, so the
# only reliable probe is actually writing a file. An earlier campaign lost 94
# array tasks to Errno 122 mid-write. Scratch is 564T free.
BASE="${FO_BASE:-/projects/hep/fs12/scratch/scyiu-formoracle}"
[ -d "$BASE" ] || BASE="$HOME/zoo221/formoracle"
export PYTHONPATH="$BASE/zoo:$BASE/fo:$BASE"
cd "$BASE" || exit 1
mkdir -p fo/results
srun python3 -u fo/oracle/d26_operators.py \
  --max-worlds "${FO_D26_WORLDS:-40}" --out fo/results/FO_D26_TRANSFER.json
RC=$?
echo "d26 rc=$RC"
exit $RC
