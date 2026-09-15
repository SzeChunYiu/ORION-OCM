#!/usr/bin/env bash
# Run physical metering (+ optional B19 witness) on local + ssh hosts.
# Usage: ./run_hosts.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/research/gmi-physical-resource-metering-v1"
RECEIPTS="$PKG/receipts"
mkdir -p "$RECEIPTS"

run_local() {
  python3 "$PKG/physical_resource_metering_v1.py" --scope-id "gmi-physical-metering-v1-local" --host-tag local --out "$RECEIPTS/HOST_RECEIPT_V1.json"
  python3 "$PKG/continual_real_sequence_b19_v1.py"
}

run_remote() {
  local host="$1"
  local tag="$2"
  echo "== metering on $host ($tag) =="
  # Prefer repo remote_verify helper when present; otherwise direct ssh+rsync.
  if [[ -x "$ROOT/scripts/remote_verify.sh" ]]; then
    "$ROOT/scripts/remote_verify.sh" "$host" -- \
      "python3 research/gmi-physical-resource-metering-v1/physical_resource_metering_v1.py --scope-id gmi-physical-metering-v1-$tag --host-tag $tag --out research/gmi-physical-resource-metering-v1/receipts/HOST_RECEIPT_V1.json"
    # pull receipt back
    rsync -az "$host:~/ocm-verify/$(basename "$ROOT")/research/gmi-physical-resource-metering-v1/receipts/HOST_RECEIPT_V1_${tag}.json" \
      "$RECEIPTS/HOST_RECEIPT_V1_${tag}.json" || true
  else
    ssh "$host" "mkdir -p ~/ocm-verify/physical-metering"
    rsync -az --delete \
      --exclude .venv --exclude .git --exclude __pycache__ --exclude .pytest_cache \
      "$PKG/" "$host:~/ocm-verify/physical-metering/"
    ssh "$host" "cd ~/ocm-verify/physical-metering && python3 physical_resource_metering_v1.py --scope-id gmi-physical-metering-v1-$tag --host-tag $tag --out receipts/HOST_RECEIPT_V1.json"
    rsync -az "$host:~/ocm-verify/physical-metering/receipts/HOST_RECEIPT_V1_${tag}.json" \
      "$RECEIPTS/HOST_RECEIPT_V1_${tag}.json"
  fi
}

run_local
for pair in "billy-old:billy-old" "billy-laptop:billy-laptop"; do
  host="${pair%%:*}"
  tag="${pair##*:}"
  if ssh -o BatchMode=yes -o ConnectTimeout=8 "$host" "true" 2>/dev/null; then
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
