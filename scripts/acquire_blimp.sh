#!/usr/bin/env bash
# Dataset custody (M3 §9): fetch BLiMP (Warstadt et al. 2020, CC BY 4.0) minimal-pair suites into a
# local, git-ignored data directory and write a content-hash manifest.  Nothing is copied into the
# repo.  Run on a compute host (billy-old / billy-laptop), never on the Mac.  BLiMP is used only as
# an acceptability *comparator suite* (M3 §11): the OCM does not train on it; a frozen subset of
# phenomena is chosen by name before any result is looked at.
set -euo pipefail
RELEASE="${BLIMP_RELEASE:-master}"
DEST="${1:-$HOME/ocm-data/blimp-$RELEASE}"
BASE="https://raw.githubusercontent.com/alexwarstadt/blimp/$RELEASE"
PHENOMENA="${BLIMP_PHENOMENA:-determiner_noun_agreement_1 regular_plural_subject_verb_agreement_1 irregular_past_participle_verbs passive_1 wh_questions_object_gap anaphor_number_agreement}"
mkdir -p "$DEST/data"
curl -fsSL "$BASE/LICENSE" -o "$DEST/LICENSE" || curl -fsSL "$BASE/README.md" -o "$DEST/README.md"
for p in $PHENOMENA; do
  curl -fsSL "$BASE/data/$p.jsonl" -o "$DEST/data/$p.jsonl"
done
python3 - "$DEST" "$RELEASE" "$BASE" "$PHENOMENA" <<'PY'
import hashlib, json, sys, datetime, pathlib
dest, release, base, phen = sys.argv[1:5]
rows = {}
for p in sorted(pathlib.Path(dest).rglob("*")):
    if p.is_file() and p.name != "MANIFEST.json":
        rows[str(p.relative_to(dest))] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size, "lines": sum(1 for _ in p.open("rb")) if p.suffix == ".jsonl" else None}
manifest = {"dataset": "BLiMP", "release": release, "source": base, "license": "CC BY 4.0 (Warstadt et al. 2020)", "phenomena_frozen": phen.split(), "acquired_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "files": rows, "note": "comparator suite only; never used for acquisition; phenomena list frozen before any evaluation"}
pathlib.Path(dest, "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: v["sha256"][:12] for k, v in rows.items()}))
PY
echo "manifest: $DEST/MANIFEST.json"
