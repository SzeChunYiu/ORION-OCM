# -*- coding: utf-8 -*-
"""Round 2 emitter for the #833 comment-checklist evidence sweep.

Reads ADJUDICATION_V2.json (105 rows, keyed on the exact `old` text, never a line
number) plus a FRESH fetch of the four live comment bodies, and refuses to emit
unless every `old` and every `anchor` is byte-exact and appears exactly once in
its comment, and every currently-open row is adjudicated exactly once.
"""
import io, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FETCH = os.environ.get("GMI833_FETCH", "/tmp/claude-501/prop2/final")
AI, AI8, AF, AJ = 5693666042, 5693704406, 5693269426, 5693954852
COMMENTS = (AI, AI8, AF, AJ)

bodies = {c: io.open(os.path.join(FETCH, "c_%d.md" % c), encoding="utf-8").read() for c in COMMENTS}
lines = {c: b.split("\n") for c, b in bodies.items()}

def anchor_for(c, n):
    """Nearest preceding '###' (or '## ') heading line, verbatim."""
    for i in range(n, -1, -1):
        if lines[c][i].startswith("###") or lines[c][i].startswith("## "):
            return lines[c][i]
    raise AssertionError("no anchor for %s:%s" % (c, n))

adj = json.load(io.open(os.path.join(HERE, "ADJUDICATION_V2.json"), encoding="utf-8"))["rows"]
assert len(adj) == 104, len(adj)

reps, nots, seen = [], [], {}
for e in adj:
    c, old = e["comment_id"], e["old"]
    assert old.startswith("- [ ] "), old
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
    assert not extra, "phantom rows in %d: %s" % (c, sorted(extra))

# each `old` appears exactly once under its anchor, across the whole emission
key = Counter((r["comment_id"], r["anchor"], r["old"]) for r in reps + nots)
assert all(v == 1 for v in key.values()), [k for k, v in key.items() if v > 1]
assert len(reps) + len(nots) == 104

out = {"schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1", "issue": 833,
       "round": 2, "source_main": os.environ.get("GMI833_MAIN", "349c2e62"),
       "supersedes": "research/gmi-833-comment-evidence-propagation-v1/ISSUE_833_COMMENT_RECONCILIATION_V1.json",
       "replacements": reps, "not_marked": nots}
dest = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
io.open(dest, "w", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

print("marked %d  not_marked %d  total %d" % (len(reps), len(nots), len(reps) + len(nots)))
for c in COMMENTS:
    m = sum(1 for r in reps if r["comment_id"] == c)
    h = Counter(x["status"] for x in nots if x["comment_id"] == c)
    print("  %d  EARNED=%d  %s" % (c, m, dict(h)))
print("wrote", dest)
sys.exit(0)
