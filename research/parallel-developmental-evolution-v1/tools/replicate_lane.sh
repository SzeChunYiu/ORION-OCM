#!/bin/bash
# AMENDMENT-3 replicate lane: re-measure frozen eval rows on THIS host.
# Pure addition: writes into <local>/replicates/<host>/, never touches the
# run root of record on LUNARC.  Usage:
#   replicate_lane.sh LOCAL ROOT GEN WAVE FIRST_INDEX LAST_INDEX
# LOCAL = directory containing capsule/ (ship9 execution dir) and bundle/
# (the frozen inputs copied from LUNARC: generations/... + lunaarc_rows/).
set -euo pipefail
LOCAL="$1"; GEN="$2"; WAVE="$3"; FIRST="$4"; LAST="$5"
HOST="$(hostname -s)"
RUNLOCAL="$LOCAL/replicate_run"
CAPS="$LOCAL/capsule"
mkdir -p "$LOCAL/replicates/$HOST"
rm -rf "$RUNLOCAL"
mkdir -p "$RUNLOCAL"
cp -R "$LOCAL/bundle/generations" "$RUNLOCAL/generations"
export PYTHONPATH="$CAPS:${PYTHONPATH:-}"
cd "$CAPS"
: > "$LOCAL/replicates/$HOST/rows.jsonl"
for IDX in $(seq "$FIRST" "$LAST"); do
  python3 "$CAPS/worker_evaluate.py" --run-root "$RUNLOCAL" \
    --generation "$GEN" --wave "$WAVE" --index "$IDX" \
    >> "$LOCAL/replicates/$HOST/rows.jsonl" 2>&1 || echo "idx $IDX rc=$?" \
    >> "$LOCAL/replicates/$HOST/errors.txt"
done
python3 - "$RUNLOCAL" "$LOCAL" "$GEN" "$WAVE" "$HOST" "$FIRST" "$LAST" <<'PYEOF'
import json, sys, time, pathlib
runlocal, local, gen, wave, host, first, last = sys.argv[1:8]
rows = []
for p in sorted(x for x in pathlib.Path(runlocal, "generations", "g%s" % gen,
                             "waves", "w%s" % wave, "eval").glob("*.json")
                if not x.name.endswith(".full.json")):
    d = json.loads(p.read_text())
    rows.append({
        "candidate_id": d["candidate_id"], "digest": d["digest"],
        "status": d["status"], "n": d.get("n"), "success": d.get("success"),
        "work": d.get("work"), "persistent_bytes": d.get("persistent_bytes"),
        "envelope": d.get("envelope"),
    })
claim = {
    "schema": "pdev217.replicate_claim.v1", "host": host,
    "generation": int(gen), "wave": int(wave),
    "index_range": [int(first), int(last)],
    "rows": rows, "row_count": len(rows),
    "written_unix": int(time.time()),
}
out = pathlib.Path(local, "replicates", host, "claim_g%sw%s.json" % (gen, wave))
out.write_text(json.dumps(claim, indent=2, sort_keys=True) + "\n")
print("claim written:", out, "rows:", len(rows))
PYEOF
