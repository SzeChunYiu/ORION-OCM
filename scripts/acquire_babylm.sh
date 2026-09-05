#!/usr/bin/env bash
# Dataset custody (M5 §8): record the BabyLM release the sample-efficiency programme pins to.  The
# official corpora are distributed under the challenge's terms (OSF); this script downloads only if
# BABYLM_URL is provided explicitly (the URL and terms must be checked at execution time) and
# otherwise writes a manifest with status CANNOT_CHECK_BABYLM_DATA so that no result is claimed.
# Run on a compute host (billy-old / billy-laptop), never on the Mac.
set -euo pipefail
DEST="${1:-$HOME/ocm-data/babylm}"
mkdir -p "$DEST"
STATUS="CANNOT_CHECK_BABYLM_DATA"
if [ -n "${BABYLM_URL:-}" ]; then
  curl -fsSL "$BABYLM_URL" -o "$DEST/babylm_release.zip" && STATUS="ACQUIRED"
fi
python3 - "$DEST" "$STATUS" "${BABYLM_URL:-}" "${BABYLM_RELEASE:-2026}" <<'PY'
import hashlib, json, sys, datetime, pathlib
dest, status, url, release = sys.argv[1:5]
rows = {}
for p in sorted(pathlib.Path(dest).iterdir()):
    if p.is_file() and p.name != "MANIFEST.json":
        rows[p.name] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
manifest = {"dataset": "BabyLM", "release": release, "status": status, "source": url or "https://babylm.github.io/ (official release; terms checked at execution time)", "tracks": {"strict_small": "<=10M words", "strict": "<=100M words"}, "acquired_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "files": rows, "note": "the mechanism arm must disclose every word/lesson/annotation channel; aligned semantic supervision is extra information and is never compared naively with text-only parents"}
pathlib.Path(dest, "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(status, len(rows), "files")
PY
echo "manifest: $DEST/MANIFEST.json"
