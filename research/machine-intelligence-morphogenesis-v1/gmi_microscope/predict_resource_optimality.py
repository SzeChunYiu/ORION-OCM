"""C box 11: PRE-REGISTERED predictions for resource-optimality of learning laws.

Box 12 compared the six learning laws on CAPABILITY alone and found that every
law loses somewhere, and that three laws are never UNIQUELY best.  Two of those
were explained by strict member containment; `state-only` was not, and was
committed to the record as unexplained.

Box 11 asks the next question: under what assumptions is each law RESOURCE-
optimal?  That requires charging cost, and a cost model has free choices that a
pure capability comparison does not.  This file fixes every one of those choices
BEFORE any of them is measured.  It contains NO measuring code.  The companion
`compare_resource_optimality.py` lands in a later commit; git commit order is
the evidence that these predictions were not written to fit the answer.

THE COST MODEL (fixed here, never to be retuned)

Two coordinates, both computed from the enumeration, neither stipulated:

  spec(P)   = ceil(log2 |P|)
              bits needed to say WHICH member of the paradigm you mean.
              Task-independent.  Integer.  This is a specification /
              search cost: a bigger paradigm is a bigger thing to search.

  mem(P,t)  = distinct states reachable from START, minimised over the
              members that achieve the paradigm's best score on t.
              Task-dependent.  Integer in 1..4.  This is a memory cost.

TIE-BREAK RULE (the single most load-bearing choice in this file)

`score(P,t)` is a MAX over members; cost is not, so "the cost of P on t" is
undefined until a member is chosen.  The rule is ARGMAX-SCORE THEN MIN-COST:
among the members achieving the paradigm's best score on t, take the cheapest.
Not min over all members (that would let a paradigm buy cheapness by giving up
capability it is not being charged for), and not min among members scoring at
least some threshold (that smuggles in a second free parameter).  Any later
reader who finds a different frontier should check this rule first.

A third coordinate -- rule-table size -- is deliberately NOT used.  Every update
object is an 8-tuple, so table size is the constant 8 for every member of every
paradigm; the only non-vacuous reading of it collapses into spec(P).

THE OBJECTIVE AND THE SWEEP

For weight w >= 0 (an exact Fraction, never a float):

    value(P, t, w) = score(P,t) - w * cost(P,t)

Scores are integers in 0..4 and costs are integers, so the argmax changes only
at finitely many exactly computable rational breakpoints.  "Assumptions under
which law L is resource-optimal" is then literally: the set of (t, w) at which
L is the unique argmax.

REGISTERED PREDICTIONS

P1  Under spec cost, `state-only` is on the Pareto frontier for NO task.
    Reasoning: its behaviours are exactly the four constant tuples, and every
    constant tuple is of the form (a,b,a,b) with a=b, which is the form of an
    `overwrite` behaviour.  So beh(state-only) is contained in beh(overwrite)
    while |state-only| = 256 > 16 = |overwrite|: same or worse capability on
    every task, strictly worse specification cost.  Charging cost therefore
    does NOT rescue box 12's unexplained law -- it condemns it further.  If
    this prediction holds, the box 12 anomaly survives cost-charging under a
    second, independent lens.

P2  The correct hypothesis for "never uniquely best" is BEHAVIOUR containment,
    not member containment.  beh(A) subset-of beh(B) implies score(A,t) <=
    score(B,t) for every t, hence A is never uniquely best.  Member containment
    implies behaviour containment, so box 12's theorem is a corollary of this
    one; `state-only` is predicted to be a witness that the converse fails --
    behaviour-contained in `overwrite` without being member-contained in it.
    If so, box 12's unexplained case is explained, and the explanation is that
    box 12 stated the theorem with an unnecessarily strong hypothesis.

P3  At w = 0 the ranking is capability-only and must reproduce box 12's win
    counts exactly.  This is a consistency check on the two boxes, and a
    disagreement means one of the two computations is wrong.

P4  As w grows without bound the objective is dominated by cost, so the argmax
    tends to the cheapest laws.  `additive` and `overwrite` both have
    spec = ceil(log2 16) = 4, so they TIE at high w and NO law is uniquely
    optimal there.  Prediction: the set of tasks admitting a unique optimum
    is non-empty at w = 0 and EMPTY for all sufficiently large w.

P5  Every law except `state-only` is uniquely optimal for at least one (t, w).
    A law optimal for no (t, w) under either coordinate is a negative result
    and gets a revival pass -- is there ANY coordinate under which it is
    optimal? -- before it is filed, not after.

P6  The two coordinates DISAGREE: there is at least one task where the spec
    frontier and the mem frontier name different laws.  Resource-optimality is
    coordinate-dependent, and a single "cost" number would hide that.

NON-VACUITY CONTROLS (a claim that cannot fail is not a result)

C1  spec is not constant across the six laws.
C2  some task has >= 2 Pareto-optimal laws and some task has exactly 1.
C3  the frontier is neither all six laws on every task nor one law on every task.
C4  mem genuinely varies -- not every paradigm reaches the same state count.
"""

SCHEMA = "GMI_RESOURCE_OPTIMALITY_PREDICTION_V1"

LAWS = ["additive", "overwrite", "insertion-monotone",
        "idempotent-on-repeat", "keep-or-replace", "state-only"]

TIE_BREAK = "argmax-score-then-min-cost"

COORDINATES = ["spec", "mem"]

PREDICTIONS = {
    "P1_state_only_never_on_spec_frontier": True,
    "P2_behaviour_containment_is_the_right_hypothesis": True,
    "P2_state_only_behaviour_contained_in_overwrite": True,
    "P2_state_only_member_contained_in_overwrite": False,
    "P3_w_zero_reproduces_box12_win_counts": True,
    "P4_unique_optimum_vanishes_at_high_w": True,
    "P5_every_law_but_state_only_uniquely_optimal_somewhere": True,
    "P6_the_two_coordinates_disagree_on_some_task": True,
}

CONTROLS = {
    "C1_spec_varies": True,
    "C2_frontier_size_varies": True,
    "C3_frontier_is_not_degenerate": True,
    "C4_mem_varies": True,
}

if __name__ == "__main__":
    print("=" * 88)
    print("C BOX 11: PRE-REGISTERED RESOURCE-OPTIMALITY PREDICTIONS")
    print("=" * 88)
    print("schema     : %s" % SCHEMA)
    print("laws       : %s" % ", ".join(LAWS))
    print("coordinates: %s" % ", ".join(COORDINATES))
    print("tie-break  : %s" % TIE_BREAK)
    print()
    print("predictions:")
    for k, v in PREDICTIONS.items():
        print("  %-52s %s" % (k, v))
    print()
    print("non-vacuity controls:")
    for k, v in CONTROLS.items():
        print("  %-52s %s" % (k, v))
    print()
    print("This file contains no measuring code.  The comparison lands later.")
