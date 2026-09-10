#!/bin/bash
# HSG continuous calibration scheduler — results -> uncertainty -> next frozen
# experiment -> new jobs. Reads UNCERTAINTY_LEDGER_V1.json; for each UNMEASURED
# entry whose next_experiment is CONT-CAL-*, freezes the spec (sha-committed),
# submits it (sbatch on LUNARC, nohup fallback on a laptop), and on later cycles
# flips finished runs into the ledger via calibrate.py --update-ledger.
# Appends EVENTS.jsonl (append-only trace).
#
# Usage: ./scheduler.sh [--once|--loop]   (default --once)
# Requires: python3, the donor bank + atoms files built by donor_bank.py.
set -euo pipefail
cd "$(dirname "$0")"
# Compute belongs on LUNARC (sbatch) or a laptop (nohup fallback) — never the
# Mac mini. Override with FORCE_LOCAL=1 only for smoke validation.
if [ "$(uname)" = "Darwin" ] && [ "${FORCE_LOCAL:-0}" != "1" ]; then
  echo "refusing to run calibration compute on Darwin (hard rule: compute off-Mac); set FORCE_LOCAL=1 to override for smoke" >&2
  exit 64
fi
MODE="${1:---once}"
LEDGER=UNCERTAINTY_LEDGER_V1.json
EVENTS=EVENTS.jsonl
BANK=${BANK:-DONOR_BANK_V1.jsonl}
ATOMS=${ATOMS:-ATOM_BANK_V1.jsonl}
VOCAB=${VOCAB:-TERM_VOCAB_V1.json}

now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
event() { printf '{"ts":"%s",%s}\n' "$(now)" "$1" >> "$EVENTS"; }

submit() { # spec_file -> job handle
  if command -v sbatch >/dev/null 2>&1; then
    sbatch --parsable --job-name="$(basename "$1" .json)" \
      --wrap="python3 calibrate.py --spec $1 --bank $BANK --atoms $ATOMS --term-vocab $VOCAB --update-ledger"
  else
    nohup python3 calibrate.py --spec "$1" --bank "$BANK" --atoms "$ATOMS" \
      --term-vocab "$VOCAB" --update-ledger > "${1%.json}.out" 2>&1 & echo $!
  fi
}

run_cycle() {
  # 1) freeze specs for runnable entries
  /usr/bin/python3 - "$LEDGER" <<'PY'
import json, sys, hashlib, os, re
led = json.load(open(sys.argv[1]))
os.makedirs("specs", exist_ok=True)
for e in led["entries"]:
    # experiment id = the token before any ':' / whitespace, must start CONT-CAL
    exp_id = re.split(r"[:\s]", e.get("next_experiment", "").strip())[0]
    if e["status"] == "UNMEASURED" and exp_id.startswith("CONT-CAL"):
        spec = {"experiment": exp_id, "quantity": e["quantity"],
                "entry_id": e["id"], "frozen_sha": None,
                "budget": 1000, "probe_share": 0.05, "seeds": [0, 1, 2],
                "n_pairs": 20}
        spec["frozen_sha"] = hashlib.sha256(
            json.dumps(spec, sort_keys=True).encode()).hexdigest()
        open(f"specs/{spec['experiment']}.json", "w").write(
            json.dumps(spec, indent=1) + "\n")
PY
  # 2) submit every frozen spec whose results file is missing
  for spec in specs/CONT-CAL-*.json; do
    [ -e "$spec" ] || continue
    exp="$(basename "$spec" .json)"
    if [ ! -e "results/$exp.results.jsonl" ]; then
      handle="$(submit "$spec")"
      event "\"action\":\"submit\",\"experiment\":\"$exp\",\"handle\":\"$handle\""
    fi
  done
}

case "$MODE" in
  --loop) while true; do run_cycle; sleep 300; done ;;
  *) run_cycle ;;
esac
