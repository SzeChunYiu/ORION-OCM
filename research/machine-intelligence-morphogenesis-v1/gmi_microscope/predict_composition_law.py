"""FROZEN PREDICTION about an UNBUILT form: how composed obligations cost.

Phase one.  Committed and pushed in a commit containing no measuring code for
this claim; the adjudicator is written afterwards.  Commit order is the evidence.

Addresses checklist section K -- predict unseen forms and how far their
capability goes -- using the two-phase mechanism validated by
STAGE_INTERSECTION_INDEX_VERDICT_V1.json.

THE UNSEEN FORM
    Every family in the corpus is derived for ONE obligation.  Nothing has been
    built for a machine that must satisfy SEVERAL obligations at once, and no
    family states what that costs.  The generic answer is the product of the
    indices -- a machine that tracks each obligation separately.  The question
    is whether composition is ever cheaper than that, and by how much.

    This predicts the cost law for two composition kinds before either is built.

LAW 1 -- COMPOSING COUNTING OBLIGATIONS IS SUB-MULTIPLICATIVE, AND EXACTLY LCM

    A_m accepts iff the number of 'b's is divisible by m; its index is m.
    For a k-fold intersection over moduli m1..mk the product bound is prod(mi).

    PREDICTION: the Myhill-Nerode index is exactly  lcm(m1, ..., mk).

    Reason: the reachable product states are the residues jointly attainable by
    a single counter, and by the Chinese Remainder Theorem the pair
    (n mod m1, n mod m2) is determined by n mod lcm(m1, m2) and takes exactly
    lcm distinct values as n ranges over the integers.  The obligations are not
    independent because ONE counter drives all of them.  So composition is free
    wherever the moduli share factors, and costs the full product only when they
    are pairwise coprime.

LAW 2 -- COMPOSING WITH A SUFFIX OBLIGATION IS ADDITIVE, NOT MULTIPLICATIVE

    B accepts iff the string ends with "ab"; its index is 3.

    PREDICTION: intersecting ANY of the counting forms above with B costs
    exactly  +2  on top of that form's own index -- never x3.

    Reason: the suffix-state reached after reading z depends only on z whenever
    z contains an 'a', so the single letter 'b' is the only suffix whose effect
    depends on the incoming suffix-state.  That collapses all but two of the
    suffix distinctions, independently of how many counters are present.  The
    already-adjudicated single-modulus case measured m + 2; this predicts the
    same +2 holds over a composed counting form, which has not been tested.

CAPABILITY CEILING FOR THE FORM
    With k obligations drawn from moduli at most M, the reachable capability is
    bounded by max lcm over subsets, NOT by M^k.  PREDICTED CEILING for M = 12:
    the largest attainable index is 27720 = lcm(1..12), and no choice of moduli
    from that range exceeds it however many are composed.

FALSIFIERS, fixed now
    * any measured k-fold counting index != lcm(m1..mk);
    * any measured suffix-composed index != (counting index) + 2;
    * any composition of moduli <= 12 whose index exceeds 27720.

INPUTS ADMISSIBLE AT FREEZE TIME
    the obligation definitions; CRT; the three-state suffix automaton for "ab";
    the already-published m+2 result for ONE modulus.  No k-fold enumeration was
    run.  No adjudicating code for these laws exists at freeze time.
"""

import json
import os
from math import gcd

TUPLES = [(2, 3), (2, 4), (4, 6), (6, 10), (6, 15), (12, 18),
          (2, 3, 5), (4, 6, 9), (6, 10, 15), (2, 4, 8), (3, 5, 7)]


def lcm(*xs):
    out = 1
    for x in xs:
        out = out * x // gcd(out, x)
    return out


def prod(xs):
    out = 1
    for x in xs:
        out *= x
    return out


pred_count = {",".join(map(str, t)): lcm(*t) for t in TUPLES}
pred_suffix = {k: v + 2 for k, v in pred_count.items()}
prod_bound = {",".join(map(str, t)): prod(t) for t in TUPLES}

CEIL_M = 12
ceiling = lcm(*range(1, CEIL_M + 1))

OUT = {
    "registration": "GMI_COMPOSITION_LAW_PREDICTION_V1",
    "phase": "prediction -- no measurement performed or available in this script",
    "form": "a machine required to satisfy several obligations at once",
    "law_1": "k-fold intersection of counting obligations has index exactly lcm(m1..mk)",
    "law_2": "intersecting any counting form with 'ends with ab' costs exactly +2",
    "predicted_counting_index": pred_count,
    "predicted_suffix_composed_index": pred_suffix,
    "generic_product_bound": prod_bound,
    "capability_ceiling": {
        "moduli_at_most": CEIL_M,
        "predicted_max_index": ceiling,
        "claim": "no composition of moduli <= 12 exceeds lcm(1..12) however many are composed",
    },
    "falsifiers": [
        "any k-fold counting index != lcm",
        "any suffix-composed index != counting index + 2",
        "any composition of moduli <= 12 with index > lcm(1..12)",
    ],
    "inputs_admissible_at_freeze": [
        "obligation definitions", "Chinese Remainder Theorem",
        "three-state suffix automaton for 'ab'",
        "the published single-modulus m+2 result",
        "no k-fold enumeration was run",
    ],
}

print("=" * 78)
print("FROZEN PREDICTION -- composition law for an unbuilt form")
print("=" * 78)
print("  LAW 1: k-fold counting intersection has index exactly lcm(m1..mk)")
print("  LAW 2: composing any of them with 'ends with ab' costs exactly +2")
print()
print("  %-14s %-10s %-10s %s" % ("moduli", "product", "predicted", "with suffix"))
for t in TUPLES:
    k = ",".join(map(str, t))
    print("  %-14s %-10d %-10d %d" % (k, prod_bound[k], pred_count[k], pred_suffix[k]))
print()
print("  CAPABILITY CEILING, moduli <= %d : %d  (= lcm(1..%d))"
      % (CEIL_M, ceiling, CEIL_M))
print("  No composition from that range exceeds it, however many are composed.")
print()
print("  This script performs NO measurement of these laws.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_COMPOSITION_LAW_PREDICTION_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print("  receipt: microscopes/results/STAGE_COMPOSITION_LAW_PREDICTION_V1.json")
