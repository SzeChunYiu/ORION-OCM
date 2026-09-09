# Shared Slurm environment (sourced by every zoo sbatch script).
# Explicit environment: stdlib python3 (capsule needs no third-party deps).
# If manifests/zoo221.sif exists, apptainer wraps python3 for reproducibility.
export ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/capsule}"
export ZOO_PY="${ZOO_PY:-python3}"
if [ -x "$(command -v apptainer 2>/dev/null)" ] && [ -f "$ZOO_ROOT/manifests/zoo221.sif" ]; then
  export ZOO_PY="apptainer exec $ZOO_ROOT/manifests/zoo221.sif python3"
fi
export ZOO_HOST="$(hostname -s)"
export TMPDIR="${SNIC_TMP:-${TMPDIR:-/tmp}}"
mkdir -p "$ZOO_ROOT/logs" "$ZOO_ROOT/results" "$ZOO_ROOT/archives" "$ZOO_ROOT/manifests/receipts"
echo "env: host=$ZOO_HOST py=$ZOO_PY tmp=$TMPDIR root=$ZOO_ROOT" >&2
