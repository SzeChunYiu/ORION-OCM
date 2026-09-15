"""D: does each morphology class have a demonstrated phase-law win?

Six of section D's boxes ask for at least one phase law where a given class wins:
neural-like, symbolic/programmatic, probabilistic, memory/retrieval,
search/planning, hybrid.

This is an EXISTENCE question, which is what makes it safely auditable.  The
corpus reports 38 distinct winner values across its receipts, and classifying
all of them into six buckets would be judgement-heavy and contestable.  It is
not necessary: to answer "does this class win somewhere", only UNAMBIGUOUS
winners need assigning.  Values whose class is arguable are left UNASSIGNED and
reported as such, and they cannot affect a positive finding -- at worst they
hide one, which is the safe direction to err.

Section D is actively being derived by another lane.  This audits what the
corpus already demonstrates; it derives no new phase law.
"""

import json
import glob
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "microscopes", "results")

# Unambiguous assignments only.  Anything arguable is deliberately absent.
CLASS = {
    "neural-like": ["parametric", "gated", "register", "threshold_dnf",
                    "sum_threshold", "dense", "gradient"],
    "symbolic/programmatic": ["symbolic", "rule", "compile", "compiled_search",
                              "program", "program_search", "rewrite"],
    "probabilistic": ["simulate", "particles", "posterior", "belief",
                      "full posterior", "sampling"],
    "memory/retrieval": ["exemplar", "tables", "prototype", "table",
                         "hamming_knn_k3", "soft_retrieval", "store",
                         "nearest", "retrieval", "kvstore"],
    "search/planning": ["search", "act&observe", "replan", "plan",
                        "frontier", "lookahead"],
    "hybrid": ["hybrid", "mixed", "differentiated", "mixture"],
}
ASSIGNED = {v: k for k, vs in CLASS.items() for v in vs}

WINNER_KEY = re.compile(r"winner|wins|cheaper|best|dominant|argmin|winning")


def walk(o, hits, path):
    if isinstance(o, dict):
        for k, v in o.items():
            if WINNER_KEY.fullmatch(str(k).lower()):
                vals = v if isinstance(v, list) else [v]
                for x in vals:
                    if isinstance(x, str):
                        hits.append((x.lower().strip(), path))
            walk(v, hits, path)
    elif isinstance(o, list):
        for v in o[:80]:
            walk(v, hits, path)


hits = []
for f in sorted(glob.glob(os.path.join(RESULTS, "STAGE_*.json"))):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if isinstance(d, dict) and d.get("corpus_audit") is True:
        continue
    walk(d, hits, os.path.basename(f))

print("=" * 96)
print("D: DOES EACH MORPHOLOGY CLASS HAVE A DEMONSTRATED WIN?")
print("=" * 96)
print("  winner records found: %d" % len(hits))
vals = Counter(v for v, _ in hits)
print("  distinct winner values: %d" % len(vals))

demonstrated, absent, unassigned = {}, [], sorted(v for v in vals if v not in ASSIGNED)
for cls in CLASS:
    ex = [(v, p) for v, p in hits if ASSIGNED.get(v) == cls]
    if ex:
        demonstrated[cls] = {"winner_values": sorted({v for v, _ in ex}),
                             "example_receipt": ex[0][1],
                             "occurrences": len(ex)}
    else:
        absent.append(cls)

print()
print("-" * 96)
print("PER CLASS")
print("-" * 96)
for cls in CLASS:
    if cls in demonstrated:
        d = demonstrated[cls]
        print("  WINS      %-24s %-3d occurrences  e.g. %s"
              % (cls, d["occurrences"], ", ".join(d["winner_values"][:3])))
    else:
        print("  --        %-24s no unambiguous winner found" % cls)

print()
print("  classes with a demonstrated win : %d of %d" % (len(demonstrated), len(CLASS)))
print("  classes with none               : %s" % (", ".join(absent) or "none"))
print()
print("  unassigned winner values (%d), which cannot create a positive finding"
      % len(unassigned))
print("  and at worst hide one: %s" % ", ".join(unassigned[:12]))

assert demonstrated, "no class has a demonstrated win; the assignment is broken"
assert len(vals) > len(CLASS), "fewer winner values than classes; suspect the scan"
assert unassigned, (
    "every winner value is assigned, which for 38 heterogeneous strings would "
    "mean the assignment is straining to classify arguable cases")

OUT = {
    "corpus_audit": True,
    "winner_records": len(hits),
    "distinct_winner_values": len(vals),
    "classes_total": len(CLASS),
    "classes_with_a_demonstrated_win": sorted(demonstrated),
    "classes_without": absent,
    "evidence": demonstrated,
    "unassigned_winner_values": unassigned,
    "method": (
        "existence question only: unambiguous winner values are assigned to "
        "classes by hand, arguable ones are left unassigned and cannot create a "
        "positive finding"),
    "scope": (
        "a winner value in a receipt shows the class won in SOME cell; it is "
        "not a phase LAW, which additionally requires the boundary to be "
        "derived and frozen.  Section D is being derived by another lane; this "
        "audits what the corpus already demonstrates and derives nothing"),
}
os.makedirs(RESULTS, exist_ok=True)
with open(os.path.join(RESULTS, "STAGE_PHASE_WIN_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 96)
print("  NOT a phase law.  A winner value shows the class won in SOME cell; a")
print("  phase LAW additionally requires the boundary to be derived and frozen.")
print("  This distinguishes 'has been observed to win' from 'has a law', and")
print("  only the first is measured here.")
print()
print("  receipt: microscopes/results/STAGE_PHASE_WIN_V1.json")
