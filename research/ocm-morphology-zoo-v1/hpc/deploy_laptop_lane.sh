#!/bin/bash
# Deploy a GS scored laptop lane (#221 sec 18 / GS-R1h, worker O).
# Run FROM the Mac (rsync + ssh only — no execution on the Mac).
#
# Usage:
#   deploy_laptop_lane.sh <ssh-target> <lane> <workers> [--start-runner]
#     ssh-target  e.g. billy-laptop | 100.104.240.15 (billy-old, direct)
#     lane        laptop_billy | laptop_old
#
# Layout on the laptop (~/gs-run):
#   zoo/research/ocm-morphology-zoo-v1/   code capsule (this tree, no git)
#   queue/{incoming,running,done,rejected}
#   freeze/   GRAND_SEARCH_R1_FREEZE.json + .sha256 (when centre stages it)
#   logs/     runner.out, runner.pid, <spec>.shard<k>.log
set -eu

TARGET=$1; LANE=$2; WORKERS=$3; START=${4:-}
HERE=$(cd "$(dirname "$0")/.." && pwd)   # .../ocm-morphology-zoo-v1

ssh "$TARGET" 'mkdir -p ~/gs-run/zoo/research ~/gs-run/queue/incoming ~/gs-run/queue/running ~/gs-run/queue/done ~/gs-run/queue/rejected ~/gs-run/freeze ~/gs-run/logs'
rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' \
      --exclude 'results' --exclude '.git' \
      "$HERE/" "$TARGET:gs-run/zoo/research/ocm-morphology-zoo-v1/"

if [ "$START" = "--start-runner" ]; then
  ssh "$TARGET" "cd ~/gs-run/zoo/research/ocm-morphology-zoo-v1 && \
    nohup python3 hpc/laptop_runner.py \
      --zoo-root ~/gs-run/zoo/research/ocm-morphology-zoo-v1 \
      --lane $LANE --workers $WORKERS --queue ~/gs-run/queue \
      --freeze-dir ~/gs-run/freeze >> ~/gs-run/logs/runner.out 2>&1 & \
    echo runner_pid \$!"
  echo "runner started on $TARGET (lane $LANE, workers $WORKERS)"
fi
