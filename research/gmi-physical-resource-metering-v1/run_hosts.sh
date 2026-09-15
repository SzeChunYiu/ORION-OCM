#!/usr/bin/env bash
# Run physical metering on local + ssh hosts (stdlib only; no venv required).
# Usage: ./run_hosts.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/research/gmi-physical-resource-metering-v1"
SIBLING="$ROOT/research/gmi-resource-lifecycle-ledger-v1"
RECEIPTS="$PKG/receipts"
mkdir -p "$RECEIPTS"

run_local() {
  echo "== metering local =="
  python3 "$PKG/physical_resource_metering_v1.py" \
    --scope-id "gmi-physical-metering-v1-local" \
    --host-tag local \
    --out "$RECEIPTS/HOST_RECEIPT_V1.json"
  python3 "$PKG/continual_real_sequence_b19_v1.py"
}

run_remote() {
  local host="$1"
  local tag="$2"
  local remote_dir="~/ocm-verify/gmi-physical-resource-metering-v1"
  echo "== metering on $host ($tag) =="
  ssh "$host" "mkdir -p $remote_dir/research/gmi-physical-resource-metering-v1/receipts $remote_dir/research/gmi-resource-lifecycle-ledger-v1"
  rsync -az \
    "$PKG/physical_resource_metering_v1.py" \
    "$PKG/PHYSICAL_METERING_CONTRACT_V1.json" \
    "$PKG/continual_real_sequence_b19_v1.py" \
    "$host:$remote_dir/research/gmi-physical-resource-metering-v1/"
  rsync -az \
    "$SIBLING/RESOURCE_LIFECYCLE_LEDGER_V1.json" \
    "$host:$remote_dir/research/gmi-resource-lifecycle-ledger-v1/"
  ssh "$host" "cd $remote_dir && python3 research/gmi-physical-resource-metering-v1/physical_resource_metering_v1.py --scope-id gmi-physical-metering-v1-$tag --host-tag $tag --out research/gmi-physical-resource-metering-v1/receipts/HOST_RECEIPT_V1.json"
  rsync -az \
    "$host:$remote_dir/research/gmi-physical-resource-metering-v1/receipts/HOST_RECEIPT_V1_${tag}.json" \
    "$RECEIPTS/HOST_RECEIPT_V1_${tag}.json"
}

run_local
for pair in "billy-old:billy-old" "billy-laptop:billy-laptop"; do
  host="${pair%%:*}"
  tag="${pair##*:}"
  if ssh -o BatchMode=yes -o ConnectTimeout=12 "$host" "true" 2>/dev/null; then
    run_remote "$host" "$tag"
  else
    echo "SKIP $host (unreachable)"
  fi
done

cd "$ROOT"
python3 - <<PY
import json
from pathlib import Path
receipts = sorted(Path("$RECEIPTS").glob("HOST_RECEIPT_V1*.json"))
summary = {"hosts": [], "schema": "gmi-physical-metering-host-summary-v1"}
for path in receipts:
    data = json.loads(path.read_text())
    summary["hosts"].append({
        "file": path.name,
        "hostname": data.get("host", {}).get("hostname"),
        "claim_ceiling": data.get("claim_ceiling"),
        "statuses": {s["coordinate"]: s["status"] for s in data.get("statuses", [])},
    })
out = Path("$RECEIPTS") / "HOST_SUMMARY_V1.json"
out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2, sort_keys=True))
PY
