#!/usr/bin/env bash
# Dataset custody (M6 §4): fetch a fixed list of Simple English Wikipedia articles (CC BY-SA 4.0)
# via the MediaWiki API with their exact revision ids into a local, git-ignored directory and write
# a manifest (title, revision id, timestamp, licence, sha256, word count).  Nothing is copied into
# the repo; article text is treated as *source assertion*, never verified fact.  Run on a compute
# host (billy-old / billy-laptop), never on the Mac.
set -euo pipefail
DEST="${1:-$HOME/ocm-data/simplewiki}"
TITLES="${SIMPLEWIKI_TITLES:-Robot Door Cat Moon Earth Water Paris France Calendar Week}"
mkdir -p "$DEST"
for t in $TITLES; do
  curl -fsSL -A "ocm-custody/1.0 (research; contact via repository)" "https://simple.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids|timestamp|content&rvslots=main&format=json&titles=$t" -o "$DEST/$t.json"
done
python3 - "$DEST" "$TITLES" <<'PY'
import hashlib, json, sys, datetime, pathlib
dest, titles = sys.argv[1:3]
rows = {}
for t in titles.split():
    p = pathlib.Path(dest, f"{t}.json")
    d = json.loads(p.read_text(encoding="utf-8"))
    pages = d["query"]["pages"]
    page = next(iter(pages.values()))
    rev = page.get("revisions", [{}])[0]
    text = rev.get("slots", {}).get("main", {}).get("*", "") or rev.get("*", "")
    rows[t] = {"pageid": page.get("pageid"), "revid": rev.get("revid"), "timestamp": rev.get("timestamp"), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "words": len(text.split())}
manifest = {"dataset": "Simple English Wikipedia (selected articles)", "source": "https://simple.wikipedia.org/w/api.php", "license": "CC BY-SA 4.0", "acquired_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "articles": rows, "treatment": "source assertion only; extraction rules recorded at ingestion; never verified fact by repetition"}
pathlib.Path(dest, "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: (v["revid"], v["words"]) for k, v in rows.items()}))
PY
echo "manifest: $DEST/MANIFEST.json"
