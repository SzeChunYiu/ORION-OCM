#!/usr/bin/env bash
# Dataset custody (M4 §11): fetch MultiWOZ 2.4 (Ye, Manotumruksa, Yilmaz 2022; MIT licence per the
# public repository) into a local, git-ignored data directory and write a content-hash manifest.
# Nothing is copied into the repo.  Run on a compute host (billy-old / billy-laptop), never on the
# Mac.  MultiWOZ is a *comparator* for dialogue-state/reference tracking only (M4 §13); its slot
# schema is not the OCM dialogue ontology.
set -euo pipefail
RELEASE="${MULTIWOZ_RELEASE:-main}"
DEST="${1:-$HOME/ocm-data/multiwoz24-$RELEASE}"
BASE="https://raw.githubusercontent.com/smartyfh/MultiWOZ2.4/$RELEASE"
mkdir -p "$DEST"
curl -fsSL "$BASE/LICENSE" -o "$DEST/LICENSE"
curl -fsSL "$BASE/README.md" -o "$DEST/README.md"
curl -fsSL "$BASE/data/MULTIWOZ2.4.zip" -o "$DEST/MULTIWOZ2.4.zip"
python3 - "$DEST" "$RELEASE" "$BASE" <<'PY'
import hashlib, json, sys, datetime, pathlib, zipfile
dest, release, base = sys.argv[1:4]
rows = {}
for p in sorted(pathlib.Path(dest).iterdir()):
    if p.is_file() and p.name != "MANIFEST.json":
        rows[p.name] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
members = []
zp = pathlib.Path(dest, "MULTIWOZ2.4.zip")
if zp.exists():
    with zipfile.ZipFile(zp) as z:
        members = sorted(z.namelist())
manifest = {"dataset": "MultiWOZ 2.4", "release": release, "source": base, "license": "MIT (see LICENSE; verify against the repository at acquisition)", "acquired_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "files": rows, "zip_members": members, "note": "comparator for dialogue-state/reference tracking only; the test split is protected and consulted solely by the frozen evaluator; slot schema is not the OCM ontology"}
pathlib.Path(dest, "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: v["sha256"][:12] for k, v in rows.items()}), len(members), "zip members")
PY
echo "manifest: $DEST/MANIFEST.json"
