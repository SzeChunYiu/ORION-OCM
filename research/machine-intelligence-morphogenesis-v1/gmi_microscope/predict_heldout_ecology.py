"""C box 14: HELD-OUT prediction of which learning law dominates a NEW ecology.

Every result so far in Section C lives in one ecology: 4 states, 2 evidence
symbols, evidence sequences of length L = 2.  This file predicts what happens in
an ecology that has never been enumerated -- L = 3 -- using only the L = 2
results already published and one theorem proved below.  It contains NO
measuring code.  `compare_heldout_ecology.py` lands in a later commit.

A held-out prediction is only held-out if nothing about the target ecology was
looked at first.  Nothing at L = 3 has been computed at the time of this commit;
every number quoted below is from the committed L = 2 receipts
(STAGE_NEGATIVE_ECOLOGY_V1.json, STAGE_RESOURCE_OPTIMALITY_V1.json).

THE NEW ECOLOGY

  S = 4 states, E = 2 evidence symbols, L = 3.
  8 evidence sequences instead of 4, so a behaviour is an 8-tuple and there are
  4^8 = 65536 required behaviours (tasks) instead of 256.
  The update objects are unchanged: an update is still a map S x E -> S, so the
  same 65536 members and the same six paradigms carry over verbatim.

  This is a genuinely different ecology: the task space grows by 256x and the
  discriminating power of a task grows, because a length-3 sequence can separate
  update objects that a length-2 sequence cannot.

THEOREM (L-independence of the state-only containment)

  For every L >= 1,  beh_L(state-only) is a subset of beh_L(overwrite).

  Proof.  A `state-only` update ignores evidence, so it is a map f : S -> S
  applied once per symbol.  After any sequence of length L the final state is
  f^L(START), which does not depend on the sequence.  So every state-only
  behaviour is the constant L-tuple (c, ..., c) with c = f^L(START), and taking
  f constant at c shows every constant tuple is attained:
  beh_L(state-only) = { constant tuples } exactly, so |beh_L(state-only)| = S.

  An `overwrite` update satisfies u(s,e) = h(e) for some h : E -> S, so after a
  sequence (e_1 ... e_L) with L >= 1 the final state is h(e_L): the behaviour is
  determined by the last symbol alone.  Choosing h(0) = h(1) = c makes every
  entry c, so every constant tuple lies in beh_L(overwrite).

  Hence beh_L(state-only) is a subset of beh_L(overwrite) for every L >= 1. QED

  Corollary.  By the behaviour-containment theorem of box 11 -- if
  beh(A) is a subset of beh(B) then score(A,t) <= score(B,t) for every t, so A
  is never uniquely best -- `state-only` is never uniquely best in ANY of these
  ecologies, at any sequence length.  This is a structural, L-independent
  result, not an artefact of L = 2.

REGISTERED PREDICTIONS FOR L = 3

H1  beh(state-only) is a subset of beh(overwrite).
    Forced by the theorem.  If this fails, the theorem or the implementation is
    wrong, and that is the most valuable outcome available here.

H2  `state-only` is uniquely best on 0 of the 65536 tasks.
    Follows from H1 via the box 11 corollary.

H3  |beh(state-only)| = 4 and |beh(overwrite)| = 4, both exactly S and both
    INDEPENDENT of L.  For overwrite the behaviour is fixed by h(e_L) and h has
    S^E = 16 choices, but only the value on the last symbol is observable, so
    the distinct behaviours number exactly the tuples (h(last(sigma)))_sigma.
    At L = 2 this gave 16 because both symbols occur last among the four
    sequences; at L = 3 both symbols still occur last, so the count stays 16.
    Registered as 16, not 4, for overwrite -- and 4 for state-only.

H4  The set of laws that are never uniquely best at L = 3 is exactly
    {overwrite, keep-or-replace, state-only} -- the same three as at L = 2.
    Reasoning: each is behaviour-contained in another law at L = 2 by an
    argument that does not mention L (overwrite and keep-or-replace are both
    behaviour-contained in idempotent-on-repeat, state-only by the theorem
    above), so the containments should survive.  This is the prediction most
    likely to fail, because a longer sequence can break a containment that
    holds at L = 2 by exposing a distinction the shorter sequence could not
    probe.  That is exactly the probeability criterion from the composition
    law, applied here to containment rather than to index.

H5  The ORDER of the uniquely-best counts is preserved:
        idempotent-on-repeat > insertion-monotone > additive > 0.
    At L = 2 the counts were 20, 18, 14 out of 256 tasks.  The claim is about
    the order, not the values, because the task space changes size.

H6  The uniquely-best counts do NOT simply scale with the task space.  The
    fraction of tasks with a unique best law at L = 2 was 52/256 = 20.3%.
    Prediction: at L = 3 that fraction is STRICTLY SMALLER, because the task
    space grows 256x while the paradigms' behaviour sets grow far less, so
    most new tasks are matched poorly and by ties rather than uniquely.

NON-VACUITY CONTROLS

C1  the L = 3 behaviour sets are not all equal to their L = 2 counterparts --
    if nothing changed, the "new ecology" is not new.
C2  at least one task at L = 3 has a unique best law, and at least one does not.
C3  the number of distinct tasks actually achieved by some law is strictly
    less than 65536 -- the ecology is not trivially saturated.
"""

SCHEMA = "GMI_HELDOUT_ECOLOGY_PREDICTION_V1"

SOURCE_ECOLOGY = {"S": 4, "E": 2, "L": 2, "tasks": 256}
TARGET_ECOLOGY = {"S": 4, "E": 2, "L": 3, "tasks": 65536}

L2_UNIQUELY_BEST_ON = {"additive": 14, "idempotent-on-repeat": 20,
                       "insertion-monotone": 18, "keep-or-replace": 0,
                       "overwrite": 0, "state-only": 0}

PREDICTIONS = {
    "H1_state_only_behaviour_contained_in_overwrite": True,
    "H2_state_only_uniquely_best_on_zero_tasks": True,
    "H3_behaviour_counts": {"state-only": 4, "overwrite": 16},
    "H4_never_uniquely_best_set": ["keep-or-replace", "overwrite", "state-only"],
    "H5_order_preserved": ["idempotent-on-repeat", "insertion-monotone", "additive"],
    "H6_unique_fraction_strictly_smaller_than_l2": True,
}

CONTROLS = {
    "C1_ecology_is_actually_new": True,
    "C2_unique_and_nonunique_tasks_both_occur": True,
    "C3_ecology_is_not_saturated": True,
}

if __name__ == "__main__":
    print("=" * 88)
    print("C BOX 14: HELD-OUT PREDICTION FOR A NEW ECOLOGY (L = 3)")
    print("=" * 88)
    print("schema : %s" % SCHEMA)
    print("source : %s" % SOURCE_ECOLOGY)
    print("target : %s" % TARGET_ECOLOGY)
    print()
    print("predictions:")
    for k, v in PREDICTIONS.items():
        print("  %-52s %s" % (k, v))
    print()
    print("controls:")
    for k, v in CONTROLS.items():
        print("  %-52s %s" % (k, v))
    print()
    print("Nothing at L = 3 has been computed at the time of this commit.")
    print("This file contains no measuring code.")
