#!/usr/bin/env bash
# Dataset custody (M5 §7): fetch a small, fixed list of public-domain English texts from Project
# Gutenberg (plain-text UTF-8) into a local, git-ignored data directory and write a manifest with
# title, edition id, public-domain basis, acquisition date, sha256, word count.  Nothing is copied
# into the repo.  Run on a compute host (billy-old / billy-laptop), never on the Mac.  Books test
# acquisition of form, style, discourse and lexical distribution — never factual truth (E2).
set -euo pipefail
DEST="${1:-$HOME/ocm-data/gutenberg}"
# id:title — fixed before any evaluation; Gutenberg ids are stable
BOOKS="${GUTENBERG_BOOKS:-1342:Pride_and_Prejudice 11:Alice_in_Wonderland 84:Frankenstein 1661:Sherlock_Holmes_Adventures 2701:Moby_Dick}"
mkdir -p "$DEST"
for b in $BOOKS; do
  id="${b%%:*}"; name="${b#*:}"
  url="https://www.gutenberg.org/cache/epub/$id/pg$id.txt"
  curl -fsSL -A "ocm-custody/1.0" "$url" -o "$DEST/pg$id.txt" || curl -fsSL -A "ocm-custody/1.0" "https://www.gutenberg.org/files/$id/$id-0.txt" -o "$DEST/pg$id.txt"
done
python3 - "$DEST" "$BOOKS" <<'PY'
import hashlib, json, sys, datetime, pathlib, re
dest, books = sys.argv[1:3]
rows = {}
for b in books.split():
    gid, name = b.split(":", 1)
    p = pathlib.Path(dest, f"pg{gid}.txt")
    text = p.read_text(encoding="utf-8", errors="replace")
    body = text
    m = re.search(r"\*\*\* START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text)
    if m:
        body = text[m.end():]
    e = re.search(r"\*\*\* END OF (THE|THIS) PROJECT GUTENBERG EBOOK", body)
    if e:
        body = body[:e.start()]
    rows[p.name] = {"gutenberg_id": int(gid), "title": name.replace("_", " "), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size, "words_body": len(body.split()), "public_domain_basis": "Project Gutenberg public-domain text (US); header/footer stripped for the body count only", "preprocessing": "none stored; body = between START/END markers"}
manifest = {"dataset": "Project Gutenberg public-domain selection", "source": "https://www.gutenberg.org/", "acquired_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "files": rows, "held_out_overlap_check": "protected evaluation text must be checked for overlap by sha256 of sentences before use", "note": "form/style/discourse acquisition only (E2); factual claims in books are never trusted knowledge"}
pathlib.Path(dest, "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: (v["words_body"], v["sha256"][:12]) for k, v in rows.items()}))
PY
echo "manifest: $DEST/MANIFEST.json"
