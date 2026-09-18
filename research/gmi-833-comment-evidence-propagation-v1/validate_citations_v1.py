# -*- coding: utf-8 -*-
import json, io, os, re, sys
ROOT="/Users/billy/Desktop/projects/ORION-OCM-wt-833/propagate"
REC=ROOT+"/research/gmi-833-comment-evidence-propagation-v1/ISSUE_833_COMMENT_RECONCILIATION_V1.json"
d=json.load(io.open(REC,encoding="utf-8"))

def resolve(spec):
    """Return (ok, detail). spec = path[#anchor]."""
    if "#" in spec: path,anc=spec.split("#",1)
    else: path,anc=spec,None
    full=os.path.join(ROOT,path)
    if not os.path.exists(full): return False,"MISSING_FILE"
    if anc is None: return True,"file-only"
    txt=io.open(full,encoding="utf-8").read()
    if path.endswith(".json"):
        obj=json.loads(txt)
        # try dotted/bracketed key path
        cur=obj; trail=[]
        for tok in re.findall(r"[^.\[\]]+", anc):
            if isinstance(cur,dict) and tok in cur:
                cur=cur[tok]; trail.append(tok); continue
            if isinstance(cur,list):
                # match a list element carrying that id
                hit=[e for e in cur if isinstance(e,dict) and tok in [str(v) for v in e.values()]]
                if hit: cur=hit[0]; trail.append(tok); continue
            # last resort: the anchor token must appear as a key or value anywhere
            if tok in txt: return True,"token-present:"+tok
            return False,"UNRESOLVED_KEY:"+tok
        return True,"keypath:"+".".join(trail)
    # markdown / py: heading or literal substring
    if anc in txt: return True,"substring"
    for line in txt.split("\n"):
        if line.startswith("#") and anc.lower() in line.lower(): return True,"heading"
    return False,"UNRESOLVED_ANCHOR"

bad=[]; ok=0
for r in d["replacements"]:
    for ev in r["evidence_paths"]:
        good,det=resolve(ev)
        if good: ok+=1
        else: bad.append((r["comment_id"],ev,det,r["old"][:60]))
print("evidence citations resolved: %d, failed: %d"%(ok,len(bad)))
for b in bad: print("  FAIL",b)

# no-alarm/recall control: these MUST fail
ctrl=[("research/gmi-833-ai0-convergence-spine-v1/NO_SUCH_FILE.json","missing file"),
      ("research/gmi-833-ai0-convergence-spine-v1/RESULT_V1.json#totally_invented_key","bogus json key"),
      ("research/gmi-833-aj11-bounded-completeness-v1/THEORY.md#A Heading That Does Not Exist Anywhere","bogus md anchor")]
print("control (all must be FAIL):")
allfail=True
for c,lab in ctrl:
    g,det=resolve(c); print("   %-12s %s -> %s"%("FAIL" if not g else "*** PASSED",lab,det))
    if g: allfail=False
print("control_ok:",allfail)

# structural checks
assert d["schema"]=="GMI_ISSUE_COMMENT_RECONCILIATION_V1" and d["issue"]==833
for r in d["replacements"]:
    assert r["old"].startswith("- [ ] ") and r["new"].startswith("- [x] ")
    assert r["new"][6:6+len(r["old"])-6].startswith(r["old"][6:6+30])
    assert " — ✅ `" in r["new"]
    assert r["status"]=="EARNED_BY_MERGED_EVIDENCE"
print("structural: OK  (%d replacements, %d not_marked)"%(len(d["replacements"]),len(d["not_marked"])))
sys.exit(1 if (bad or not allfail) else 0)
