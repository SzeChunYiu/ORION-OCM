"""FROZEN PREDICTION: when composition is NOT free.  Phase one, no measuring code.

The two laws already adjudicated both say composition is cheap: k-fold counting
intersections cost lcm rather than the product, and adding "ends with ab" costs
+2 rather than x3.  A mechanism that only ever predicts collapse is weak: it has
never been asked to predict that something is EXPENSIVE.

This predicts a case with NO collapse at all, and gives the criterion separating
the two.

THE CRITERION
    Composition is free exactly when the second obligation's distinctions cannot
    be PROBED by suffixes.

    "ends with ab" is a property of the very end of the string.  The suffix-state
    reached after reading z is fixed by z alone whenever z contains an 'a', so
    only the single letter 'b' can expose the incoming suffix-state.  Almost
    every distinction collapses -- hence +2.

    "contains aba" is different in kind: it is MONOTONE.  Once satisfied it stays
    satisfied, so the tracker is absorbing, and a suffix can always be chosen
    that completes the pattern from one state and provably cannot complete it
    from another.  Those distinctions are probeable, so nothing collapses.

LAW 3, PREDICTED
    The intersection of "count of 'b' divisible by m" with "contains aba" has
    Myhill-Nerode index exactly  4m  -- the FULL product, with no collapse.

    Reason: write a state as (r, s) with s in {0,1,2,3} the progress towards
    "aba", s=3 absorbing.  Acceptance is (r + count(z) = 0 mod m) AND (z drives
    s to 3).  The count condition separates every distinct r within a fixed s,
    because a completing suffix can carry any b-count.  For distinct s the
    separating suffixes are explicit: "a" then b^(m-r) reaches 3 from s=2 but
    never from s=1, since from s=1 a run of b's cycles 1->2->0 and never reaches
    3 without a further 'a'; "ba" then b^(m-r-1) reaches 3 from s=1 but not from
    s=0.  And b^(m-r) alone reaches acceptance from s=3 but from no other s,
    because b's alone never complete the pattern.  So all 4m states survive.

WHY THIS IS THE RISKY ONE
    If the measured index comes out below 4m, Law 3 is false and the probeability
    criterion that motivates it is wrong or incomplete.  That would also put the
    +2 law's EXPLANATION in doubt even though its number stands.  The prediction
    is recorded so that outcome is reportable rather than revisable.

FALSIFIER
    any measured index != 4m at any tested m >= 2.

PREDICTED
    m = 2,3,4,5,6,8,10,12  ->  8,12,16,20,24,32,40,48
"""

import json
import os

MS = [2, 3, 4, 5, 6, 8, 10, 12]

OUT = {
    "registration": "GMI_PROBE_LAW_PREDICTION_V1",
    "phase": "prediction -- no measurement performed or available in this script",
    "obligation_a": "count of 'b' divisible by m",
    "obligation_b": "contains the substring 'aba'",
    "criterion": (
        "composition is free exactly when the second obligation's distinctions "
        "cannot be probed by suffixes; a monotone (absorbing) obligation is "
        "always probeable, so it costs the full product"),
    "law_3": "index of the intersection is exactly 4m -- the full product, no collapse",
    "predicted_index": {str(m): 4 * m for m in MS},
    "product_bound": {str(m): 4 * m for m in MS},
    "contrast": (
        "'ends with ab' costs +2 over the same counting form; 'contains aba' is "
        "predicted to cost x4.  Same counter, same alphabet, opposite outcome"),
    "falsifier": "any measured index != 4m at any tested m >= 2",
    "risk": (
        "if the measured index is below 4m the probeability criterion is wrong, "
        "and the +2 law's explanation is in doubt even though its number stands"),
    "inputs_admissible_at_freeze": [
        "obligation definitions",
        "the four-state KMP automaton for 'aba' with absorbing accept",
        "the published m+2 and lcm results",
        "no enumeration of this intersection was run",
    ],
}

print("=" * 78)
print("FROZEN PREDICTION -- Law 3: when composition is NOT free")
print("=" * 78)
print("  A: count of 'b' divisible by m     B: contains 'aba'")
print()
print("  CRITERION: composition is free exactly when the second obligation's")
print("  distinctions cannot be probed by suffixes.  'contains aba' is monotone,")
print("  hence always probeable, hence predicted to cost the FULL product.")
print()
print("  %-6s %-14s %s" % ("m", "product bound", "predicted"))
for m in MS:
    print("  %-6d %-14d %d" % (m, 4 * m, 4 * m))
print()
print("  Contrast: 'ends with ab' costs +2 over the same counting form.")
print("  Same counter, same alphabet, opposite outcome.")
print()
print("  RISK: if the measured index is below 4m, the criterion is wrong and the")
print("  +2 law's explanation is in doubt even though its number stands.")
print()
print("  This script performs NO measurement.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_PROBE_LAW_PREDICTION_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print("  receipt: microscopes/results/STAGE_PROBE_LAW_PREDICTION_V1.json")
