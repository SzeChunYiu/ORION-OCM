# -*- coding: utf-8 -*-
"""Round 2 emitter for the #833 comment-checklist evidence sweep.

Reads ADJUDICATION_V2.json (105 rows, keyed on the exact `old` text, never a line
number) plus a FRESH fetch of the four live comment bodies, and refuses to emit
unless every `old` and every `anchor` is byte-exact and appears exactly once in
its comment, and every currently-open row is adjudicated exactly once.
"""
import argparse
import io, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOTS = os.path.join(HERE, "comment_snapshots")
FETCH = os.environ.get("GMI833_FETCH")
AI, AI8, AF, AJ = 5693666042, 5693704406, 5693269426, 5693954852
COMMENTS = (AI, AI8, AF, AJ)


def load_bodies(offline=None):
    root = offline or FETCH or SNAPSHOTS
    out = {}
    for c in COMMENTS:
        jp = os.path.join(root, "c_%d.json" % c)
        mp = os.path.join(root, "c_%d.md" % c)
        if os.path.exists(jp):
            doc = json.load(io.open(jp, encoding="utf-8"))
            out[c] = doc["body"] if isinstance(doc, dict) else doc
        else:
            out[c] = io.open(mp, encoding="utf-8").read()
    return out

parser = argparse.ArgumentParser()
parser.add_argument("--offline", metavar="PKGDIR", help="read comment_snapshots/ from this package")
args = parser.parse_args()
bodies = load_bodies(os.path.join(args.offline, "comment_snapshots") if args.offline else None)
lines = {c: b.split("\n") for c, b in bodies.items()}

def anchor_for(c, n):
    """Nearest preceding '###' (or '## ') heading line, verbatim."""
    for i in range(n, -1, -1):
        if lines[c][i].startswith("###") or lines[c][i].startswith("## "):
            return lines[c][i]
    raise AssertionError("no anchor for %s:%s" % (c, n))

adj = json.load(io.open(os.path.join(HERE, "ADJUDICATION_V2.json"), encoding="utf-8"))["rows"]
assert len(adj) == 104, len(adj)

reps, nots, seen, already_closed = [], [], {}, []
for e in adj:
    c, old = e["comment_id"], e["old"]
    assert old.startswith("- [ ] "), old
    if old not in bodies[c]:
        closed = "- [x] " + old[6:]
        hits = [l for l in lines[c] if l == closed or l.startswith(closed + " — ✅")]
        assert len(hits) == 1, "adjudicated row is neither open nor uniquely closed: %r" % old
        already_closed.append({"comment_id": c, "old_at_round_1": old,
                               "live_state": hits[0], "round_1_status": e["verdict"],
                               "note": "Already checked upstream; recorded rather than re-emitted."})
        continue
    cnt = bodies[c].count(old)
    assert cnt == 1, "old not unique (%d occurrences) in %d: %r" % (cnt, c, old)
    idx = [i for i, l in enumerate(lines[c]) if l == old]
    assert len(idx) == 1, (c, old)
    n = idx[0]
    assert n not in seen.get(c, set()), "double-adjudicated %s:%s" % (c, n)
    seen.setdefault(c, set()).add(n)
    anc = anchor_for(c, n)
    acnt = bodies[c].count(anc)
    assert acnt == 1, "anchor not unique (%d) in %d: %r" % (acnt, c, anc)
    if e["verdict"] == "EARNED_BY_MERGED_EVIDENCE":
        new = "- [x] " + old[6:] + u" — ✅ `" + e["package"] + "` " + e["evidence"] + "."
        reps.append({"comment_id": c, "anchor": anc, "old": old, "new": new,
                     "evidence_paths": e["evidence_paths"],
                     "status": "EARNED_BY_MERGED_EVIDENCE"})
    else:
        nots.append({"comment_id": c, "anchor": anc, "old": old,
                     "status": e["verdict"], "reason": e["reason"]})

# every currently-open row must be adjudicated exactly once
for c in COMMENTS:
    openrows = {i for i, l in enumerate(lines[c]) if l.startswith("- [ ]")}
    missing = openrows - seen.get(c, set())
    extra = seen.get(c, set()) - openrows
    assert not missing, "unadjudicated open rows in %d: %s" % (c, sorted(missing))
    bad_extra = [i for i in extra if not lines[c][i].startswith("- [x]")]
    assert not bad_extra, "phantom rows in %d: %s" % (c, sorted(bad_extra))

# each `old` appears exactly once under its anchor, across the whole emission
key = Counter((r["comment_id"], r["anchor"], r["old"]) for r in reps + nots)
assert all(v == 1 for v in key.values()), [k for k, v in key.items() if v > 1]
assert len(reps) + len(nots) + len(already_closed) == 104

src = json.load(io.open(os.path.join(HERE, "ADJUDICATION_V2.json"), encoding="utf-8"))
out = {"schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1", "issue": 833,
       "already_closed_upstream": already_closed,
       "round": 2, "source_main": os.environ.get("GMI833_MAIN", "0fb55057"),
       "supersedes": "research/gmi-833-comment-evidence-propagation-v1/ISSUE_833_COMMENT_RECONCILIATION_V1.json",
       "replacements": reps, "not_marked": nots}
dest = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
io.open(dest, "w", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

print("marked %d  not_marked %d  already_closed_upstream %d  total %d" % (len(reps), len(nots), len(already_closed), len(reps) + len(nots) + len(already_closed)))
for c in COMMENTS:
    m = sum(1 for r in reps if r["comment_id"] == c)
    h = Counter(x["status"] for x in nots if x["comment_id"] == c)
    print("  %d  EARNED=%d  %s" % (c, m, dict(h)))
print("wrote", dest)
sys.exit(0)
