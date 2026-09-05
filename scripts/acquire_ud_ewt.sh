#!/usr/bin/env bash
# Dataset custody (M3 §9): fetch Universal Dependencies English EWT (CC BY-SA 4.0) into a local,
# git-ignored data directory and write a content-hash manifest.  Nothing is copied into the repo.
# Run on a compute host (billy-old / billy-laptop), never on the Mac.  Records: source URL,
# release tag, acquisition date, sha256 of every file, licence pointer.
set -euo pipefail
RELEASE="${UD_EWT_RELEASE:-r2.14}"
DEST="${1:-$HOME/ocm-data/ud-ewt-$RELEASE}"
BASE="https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/$RELEASE"
mkdir -p "$DEST"
for f in en_ewt-ud-train.conllu en_ewt-ud-dev.conllu en_ewt-ud-test.conllu LICENSE.txt README.md; do
  curl -fsSL "$BASE/$f" -o "$DEST/$f"
done
python3 - "$DEST" "$RELEASE" "$BASE" <<'PY'
import hashlib, json, sys, datetime, pathlib
dest, release, base = sys.argv[1:4]
rows = {}
for p in sorted(pathlib.Path(dest).iterdir()):
    if p.is_file() and p.name != "MANIFEST.json":
        rows[p.name] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
manifest = {"dataset": "UD_English-EWT", "release": release, "source": base, "license": "CC BY-SA 4.0 (see LICENSE.txt)", "acquired_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "files": rows, "note": "annotations are visible for the dev/train files only; test is protected and consulted solely by the frozen evaluator"}
pathlib.Path(dest, "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: v["sha256"][:12] for k, v in rows.items()}))
PY
echo "manifest: $DEST/MANIFEST.json"
