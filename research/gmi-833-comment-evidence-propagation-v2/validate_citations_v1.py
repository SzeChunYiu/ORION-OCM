# -*- coding: utf-8 -*-
"""Resolve every evidence citation in the round-2 reconciliation, and prove the
resolver's recall on planted bad citations (a checker that never cries wolf is
not a checker; a checker that cries wolf on real data gets switched off)."""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REC = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
d = json.load(io.open(REC, encoding="utf-8"))

def resolve(spec):
    """Return (ok, detail). spec = path[#anchor]."""
    path, anc = (spec.split("#", 1) + [None])[:2] if "#" in spec else (spec, None)
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return False, "MISSING_FILE"
    if anc is None:
        return True, "file-only"
    txt = io.open(full, encoding="utf-8").read()
    if path.endswith(".json"):
        obj = json.loads(txt)
        # strongest: the anchor is a verbatim id/value in the document
        if ('"%s"' % anc) in txt:
            return True, "verbatim-value"
        cur, trail = obj, []
        for tok in re.findall(r"[^.\[\]]+", anc):
            if isinstance(cur, dict) and tok in cur:
                cur = cur[tok]; trail.append(tok); continue
            if isinstance(cur, list):
                hit = [e for e in cur if isinstance(e, dict) and tok in [str(v) for v in e.values()]]
                if hit:
                    cur = hit[0]; trail.append(tok); continue
            return False, "UNRESOLVED_KEY:" + tok
        return True, "keypath:" + ".".join(trail)
    if anc in txt:
        return True, "substring"
    for line in txt.split("\n"):
        if line.startswith("#") and anc.lower() in line.lower():
            return True, "heading"
    return False, "UNRESOLVED_ANCHOR"

bad, ok = [], 0
for r in d["replacements"]:
    for ev in r["evidence_paths"]:
        good, det = resolve(ev)
        if good: ok += 1
        else: bad.append((r["comment_id"], ev, det, r["old"][:60]))
print("evidence citations resolved: %d, failed: %d" % (ok, len(bad)))
for b in bad: print("  FAIL", b)

CTRL = [("research/gmi-833-af4-relative-computability-v1/NO_SUCH_FILE.json", "missing file"),
        ("research/gmi-833-af4-relative-computability-v1/RESULT_V1.json#totally_invented_key", "bogus json key"),
        ("research/gmi-833-af5-verification-barriers-v1/FORMALIZATION_V1.md#A Heading That Does Not Exist", "bogus md anchor"),
        ("research/gmi-833-update-law-space-v1/PARENT_OWNERSHIP_V1.md#9.9 A Section Nobody Wrote", "bogus md section"),
        ("research/machine-intelligence-morphogenesis-v1/PARENT_LEDGER_V2.json#P9A.NOT_A_REAL_PARENT", "bogus ledger id")]
print("control (all must FAIL):")
allfail = True
for c, lab in CTRL:
    g, det = resolve(c)
    print("   %-12s %-20s -> %s" % ("FAIL" if not g else "*** RESOLVED", lab, det))
    if g: allfail = False
print("control_ok:", allfail)

assert d["schema"] == "GMI_ISSUE_COMMENT_RECONCILIATION_V1" and d["issue"] == 833
for r in d["replacements"]:
    assert r["old"].startswith("- [ ] ") and r["new"].startswith("- [x] ")
    assert r["new"][6:].startswith(r["old"][6:])
    assert u" — ✅ `" in r["new"] and r["new"].endswith(".")
    assert r["status"] == "EARNED_BY_MERGED_EVIDENCE"
    assert r["comment_id"] and r["anchor"].startswith("###")
for r in d["not_marked"]:
    assert r["status"] in ("PARTIAL", "BLOCKED_ON_OPEN_PR", "NO_EVIDENCE")
    assert r["comment_id"] and r["reason"]
tot = len(d["replacements"]) + len(d["not_marked"])
closed = len(d.get("already_closed_upstream", []))
print("structural: OK  (%d replacements + %d not_marked + %d already_closed_upstream = %d)" % (len(d["replacements"]), len(d["not_marked"]), closed, tot + closed))
assert tot + closed == 104
sys.exit(1 if (bad or not allfail) else 0)
