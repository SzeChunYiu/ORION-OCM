"""FROZEN PREDICTION, written and committed BEFORE the measuring script exists.

This is phase one of the two-phase pattern the RV-377 revival work already uses
(`predict_sym.py` emits a prediction receipt; `compare_sym.py` adjudicates against
it in a separate later run).  The audit measured
`prediction_frozen_before_outcome` as true for ZERO of 21 derivation families --
every one states its prediction and measures it inside a single script.  This
closes that for one claim, by the corpus's own mechanism rather than new
machinery.

INTEGRITY CONDITION, checkable by a reader from git history:
    this file and its receipt are committed and pushed in a commit that contains
    NO measuring code.  The measuring script is written afterwards, in a later
    commit.  Commit order is the evidence; nothing here is adjudicated by the
    same process that produced it.

WHAT IS BEING PREDICTED
    Obligation A : accept iff the number of 'b's is divisible by m.   Index m.
    Obligation B : accept iff the string ends with "ab".              Index 3.
    Target       : their INTERSECTION -- accept iff both hold.

    The generic Myhill-Nerode bound for an intersection is the product, 3m,
    attained when the two obligations are independent.  They are not obviously
    independent here, because reading a letter advances both the counter and the
    suffix tracker.

INPUTS ADMISSIBLE AT FREEZE TIME
    (a) the two obligations' own definitions;
    (b) the standard suffix automaton for "ab" -- three states: no progress,
        saw 'a', saw "ab";
    (c) pencil-and-paper reasoning about which pairs collapse.  No enumeration
        of the intersection was run.  No measuring code exists at freeze time.

THE PREDICTION, AND THE REASONING THAT PRODUCED IT

    A distinguishing suffix z acts on a state (r, s) -- counter residue r,
    suffix-state s -- and the accepting condition is "residue 0 AND suffix-state
    2".  The key observation is that the suffix-state reached after reading z
    is determined by z ALONE whenever z contains an 'a', because 'a' resets the
    tracker's progress.  The only suffix whose effect depends on the incoming
    suffix-state is z = "b" (single letter): from "saw a" it reaches "saw ab",
    and from either other state it reaches "no progress".

    So the suffix-state can only ever be used to separate two states through
    that one suffix, which forces almost every pair to collapse:

      * (r, no-progress) and (r, saw-a) are separated only by z = "b", which
        requires r + 1 = 0 mod m.  They therefore merge for every r except
        r = m-1.
      * (r, no-progress) and (r, saw-ab) are separated only by z = empty,
        which requires r = 0.  They therefore merge for every r except r = 0.

    That leaves the m states (r, no-progress) as representatives, plus exactly
    two survivors that refuse to merge: (m-1, saw-a) and (0, saw-ab).

    PREDICTED INDEX = m + 2,  for every m >= 3.

    NOT 3m.  The prediction is that the intersection is very nearly free: it
    costs two states beyond the counter, not a factor of three.

FALSIFIER, stated now so it cannot be renegotiated later
    Any measured index other than m + 2, at any tested m >= 3, falsifies this.
    In particular a measured 3m falsifies it, and so does m + 1 or m + 3.
    The measuring script must compute the Myhill-Nerode index by explicit
    quotient construction over reachable states, not by consulting this file.

PREDICTED FOR THESE m
    3, 4, 5, 6, 7, 8, 12, 20  ->  5, 6, 7, 8, 9, 10, 14, 22
"""

import json
import os

MS = [3, 4, 5, 6, 7, 8, 12, 20]

OUT = {
    "registration": "GMI_INTERSECTION_INDEX_PREDICTION_V1",
    "phase": "prediction -- no measurement performed or available in this script",
    "obligation_a": "count of 'b' divisible by m",
    "obligation_b": "string ends with 'ab'",
    "target": "intersection of A and B",
    "generic_product_bound": {str(m): 3 * m for m in MS},
    "predicted_index": {str(m): m + 2 for m in MS},
    "predicted_rule": "index = m + 2 for every m >= 3",
    "falsifier": (
        "any measured index != m + 2 at any tested m >= 3; a measured 3m "
        "falsifies it, and so do m+1 and m+3"),
    "reasoning_digest": (
        "the suffix-state reached after reading z depends only on z whenever z "
        "contains an 'a'; the sole state-dependent suffix is the single letter "
        "'b'; so (r,no-progress)~(r,saw-a) except at r=m-1 and "
        "(r,no-progress)~(r,saw-ab) except at r=0, leaving m + 2 classes"),
    "inputs_admissible_at_freeze": [
        "definitions of obligations A and B",
        "the three-state suffix automaton for 'ab'",
        "pencil-and-paper collapse argument; no enumeration was run",
    ],
    "integrity": (
        "committed and pushed in a commit containing no measuring code; the "
        "measuring script is written in a later commit, so commit order is the "
        "evidence"),
}

print("=" * 78)
print("FROZEN PREDICTION -- intersection index")
print("=" * 78)
print("  A: count of 'b' divisible by m      (index m)")
print("  B: string ends with 'ab'            (index 3)")
print("  target: A AND B")
print()
print("  generic product bound : 3m")
print("  PREDICTED             : m + 2, for every m >= 3")
print()
print("  %-6s %-16s %s" % ("m", "product bound", "predicted"))
for m in MS:
    print("  %-6d %-16d %d" % (m, 3 * m, m + 2))
print()
print("  Falsifier: any measured index other than m + 2 at any tested m >= 3.")
print()
print("  This script performs NO measurement.  It is committed before the")
print("  measuring script exists, so commit order is what makes the freeze")
print("  checkable rather than asserted.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_INTERSECTION_INDEX_PREDICTION_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_INTERSECTION_INDEX_PREDICTION_V1.json")
