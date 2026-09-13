#!/usr/bin/env bash
#SBATCH --job-name=parity3-v5
#SBATCH --output=parity3-v5-%j.out
#SBATCH --error=parity3-v5-%j.err
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#
# Frozen parity-3 V5 replication on a LUNARC compute node.
#
#   sbatch -A <your-project> run_lunarc.sbatch
#
# --exclusive is requested because the registered coordinates include wall and
# process time envelopes; a shared node makes those envelopes describe the
# node's other tenants as much as the candidates. The opcode coordinate is
# exact and unaffected.
#
# Adjust the module line to whatever provides CPython 3.11 or 3.12 on the
# cluster. CPython 3.13 is expected to fail the instrumentation gate and emit
# an invalid packet; that packet is still evidence and should be kept.
set -euo pipefail

module purge
# module load GCC/12.3.0 Python/3.11.3      # typical LUNARC COSMOS stack
PYTHON="${PARITY3_PYTHON:-python3}"

HOST_LABEL="${PARITY3_HOST_LABEL:-lunarc}"
HERE="${SLURM_SUBMIT_DIR:-$(pwd)}"
HARNESS="$HERE/../nn_nonnn_point_parity3_experiment_v5.py"

VERSION="$("$PYTHON" -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])')"
IMPL="$("$PYTHON" -c 'import platform;print(platform.python_implementation())')"
NODE="${SLURMD_NODENAME:-unknown-node}"
OUT="$HERE/../NN_NONNN_POINT_PARITY3_RESULT_V5_${HOST_LABEL}_${NODE}_${IMPL}${VERSION}.json"

echo "cluster    : ${SLURM_CLUSTER_NAME:-unknown}"
echo "node       : $NODE"
echo "job id     : ${SLURM_JOB_ID:-none}"
echo "interpreter: $IMPL $VERSION"
echo "packet     : $OUT"

"$PYTHON" -I -B "$HARNESS" --self-test > /dev/null
echo "instrument self-test: green"

"$PYTHON" -I -B "$HARNESS" --host-label "$HOST_LABEL" --out "$OUT" > /dev/null
echo "packet written: $OUT"
