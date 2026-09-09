#!/bin/bash
#SBATCH -A lu2026-2-51
#SBATCH -p gpua40
#SBATCH --gres=gpu:a40:1
#SBATCH -t 23:00:00
#SBATCH -c 16
#SBATCH -J gs_gpu_o
#SBATCH -o /home/scyiu/zoo221/gs-gpu/logs/gs_gpu_%j.out
#SBATCH -e /home/scyiu/zoo221/gs-gpu/logs/gs_gpu_%j.err

# GS GPU lane (#221 sec 18, worker O).  Torch is the GPU engine (jax/QDax
# staging blocked by home quota — see hpc/gs_gpu_recon.py header).  The
# scoring gate lives INSIDE gpu.firehose: without a sha-verified
# GRAND_SEARCH_R1_FREEZE.json every run is labelled SMOKE_NOT_SCORED.

set -u
BASE=$HOME/zoo221/gs-gpu
ZOO=$BASE/research/ocm-morphology-zoo-v1
FREEZE_DIR=$BASE/freeze
mkdir -p "$BASE/logs"
module load bioconda/bio-suite-py3.12-torch
cd "$ZOO"
export PYTHONPATH="$ZOO"
export ZOO_HOST=lunarc_gpu_a40
PY=python3

# rotate per-run failure log so every job's FAILURES.jsonl is its own
# (append-only otherwise; stale lines from a superseded run misattribute)
if [ -f "$ZOO/results/FAILURES.jsonl" ]; then
  mv "$ZOO/results/FAILURES.jsonl" \
     "$ZOO/results/FAILURES.jsonl.job$SLURM_JOB_ID"
fi

echo "=== [0] recon stamp ==="
$PY hpc/gs_gpu_recon.py --root "$ZOO"

echo "=== [1] vectorizable-fraction (LUNARC side, small n) ==="
$PY -m gpu.measure_fraction --root "$ZOO" --n 64 --seed 2210

FREEZE_ARGS=""
if [ -f "$FREEZE_DIR/GRAND_SEARCH_R1_FREEZE.json" ] && [ -f "$FREEZE_DIR/GRAND_SEARCH_R1_FREEZE.sha256" ]; then
  WANT=$(awk '{print $1}' "$FREEZE_DIR/GRAND_SEARCH_R1_FREEZE.sha256")
  GOT=$($PY - "$FREEZE_DIR/GRAND_SEARCH_R1_FREEZE.json" <<'EOF'
import hashlib, sys
print(hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())
EOF
)
  if [ "$WANT" = "$GOT" ]; then
    FREEZE_ARGS="--freeze $FREEZE_DIR/GRAND_SEARCH_R1_FREEZE.json --freeze-sha $GOT"
    echo "=== FREEZE VERIFIED ($GOT) — scored mode ==="
  else
    echo "=== FREEZE SHA MISMATCH (want $WANT got $GOT) — SMOKE ==="
  fi
else
  echo "=== NO FREEZE staged — SMOKE_NOT_SCORED ==="
fi

echo "=== [2] T0 firehose, random 60000, torch backend ON THE A40, hourly ckpts ==="
$PY -m gpu.firehose --root "$ZOO" --mode random --n 60000 --seed 4210 \
    --backend torch --device cuda --chunk 8192 --lane gpu_a40 \
    --checkpoint-every 3600 --tag R1 $FREEZE_ARGS

echo "=== [2b] chunk-scaling probe: one 60000-wide batch, cuda vs cpu-torch ==="
$PY -m gpu.firehose --root "$ZOO" --mode random --n 60000 --seed 4212 \
    --backend torch --device cuda --chunk 60000 --lane gpu_a40_probe \
    --checkpoint-every 3600 --tag R1c60k $FREEZE_ARGS

echo "=== [3] census closure sweep (56160 legal genomes, full, cuda) ==="
$PY -m gpu.firehose --root "$ZOO" --mode census --backend torch \
    --device cuda --chunk 4096 --lane gpu_a40 --checkpoint-every 3600 \
    --tag R1 $FREEZE_ARGS

echo "=== [4] search-side surrogate fit + calibration ==="
$PY -m gpu.surrogate_fit --root "$ZOO" --n 4000 --seed 4211 \
    --archive B_behavior_2d --backend torch --device cuda

echo "=== done; results in $ZOO/results ==="
ls -la "$ZOO/results" | tail -40
