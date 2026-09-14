"""FROZEN PREDICTION: is pairwise dominance transitive?  Phase one, no measuring code.

Section G box 16 asks for multi-species ecologies.  GMI_SPECIES_ECOLOGY_V1.md
records that every existing competition result is a TWO-BODY contest, and that
pairwise exclusion does not in general determine multi-species outcomes.  That
was stated as a caution.  This turns it into a decidable question about the
corpus's own data.

THE QUESTION
    R10 already competed 8 carriers pairwise under a shared budget, in three
    budget pools.  Read a dominance relation off that matrix: A dominates B when
    A wins their contest.  Is that relation TRANSITIVE?

WHY IT DECIDES BOX 16
    If dominance is transitive, it is a total order, every pool has an
    unambiguous strongest carrier, and multi-species occupancy MIGHT be readable
    off the pairwise table -- box 16 would then be a matter of confirming an
    order that already exists.

    If there is an intransitive triple -- A beats B, B beats C, C beats A --
    then NO scalar ranking reproduces the pairwise outcomes, and pairwise data
    provably cannot determine the three-species outcome.  Box 16 would then be
    necessary rather than merely unfinished, and the caution in the ecology
    document would be a theorem about this corpus rather than a general warning.

THE PREDICTION
    At least one intransitive triple exists, in at least one pool.

REASONING, from what is already published
    R10's registered and upheld finding is that occupancy under a shared budget
    is NOT a function of the solo scores: 65 of 192 cells disagree with solo
    scoring, 45 of them off-diagonal.  A transitive dominance relation is
    exactly a scalar ranking of carriers.  A system whose outcomes cannot be
    recovered from per-carrier scalars is one where a scalar ranking is already
    known to lose information -- so I expect the pairwise relation not to be an
    order either.

    This is an inference, not an implication.  "Not a function of solo scores"
    does not formally entail intransitivity: the competition could depend on the
    pair jointly and still induce a transitive winner relation.  So the
    prediction can fail, and if it does the corpus gains a transitive dominance
    order, which is a stronger and more useful result than the one I expect.

FALSIFIER
    dominance transitive in all three pools -- zero intransitive triples anywhere.

ALSO CHECKED BY THE ADJUDICATOR, and not predicted here
    the matrix's two readings must agree: matrix[A][B] == INVADER_REPLACES and
    matrix[B][A] == RESIDENT_HOLDS are the same claim, and a disagreement would
    mean the dominance relation is not well defined at all.
"""

import json
import os

OUT = {
    "registration": "GMI_INTRANSITIVITY_PREDICTION_V1",
    "phase": "prediction -- no measurement performed or available in this script",
    "question": "is pairwise dominance among the 8 R10 carriers transitive?",
    "source_evidence": "STAGE_R10_INVASION_V1.json, invasion_matrix_by_pool",
    "prediction": "at least one intransitive triple exists, in at least one pool",
    "reasoning": (
        "R10's upheld finding is that occupancy is not a function of the solo "
        "scores (65 of 192 cells disagree, 45 off-diagonal); a transitive "
        "dominance relation is exactly a scalar ranking, and a system whose "
        "outcomes are known to lose information under per-carrier scalars is "
        "unlikely to induce one"),
    "inference_not_implication": (
        "'not a function of solo scores' does not formally entail "
        "intransitivity -- the contest could depend on the pair jointly and "
        "still induce a transitive winner relation, so this prediction can fail"),
    "falsifier": "dominance transitive in all three pools, zero intransitive triples",
    "if_falsified": (
        "the corpus gains a transitive dominance order, which is a stronger and "
        "more useful result than the one predicted"),
    "decides": (
        "box 16: intransitivity makes multi-species ecologies NECESSARY rather "
        "than merely unfinished, because no scalar ranking reproduces pairwise "
        "outcomes"),
    "also_checked_not_predicted": (
        "the matrix's two readings must agree; disagreement would mean the "
        "dominance relation is not well defined"),
}

print("=" * 78)
print("FROZEN PREDICTION -- is pairwise dominance transitive?")
print("=" * 78)
print("  source : R10 invasion matrix, 8 carriers, 3 budget pools")
print()
print("  PREDICTION: at least one intransitive triple exists, in >= 1 pool.")
print()
print("  If TRANSITIVE : dominance is a total order, and multi-species occupancy")
print("                  might be readable off the pairwise table.")
print("  If INTRANSITIVE: no scalar ranking reproduces the pairwise outcomes, so")
print("                  pairwise data CANNOT determine three-species outcomes,")
print("                  and box 16 is necessary rather than merely unfinished.")
print()
print("  The reasoning is an inference, not an implication -- 'not a function of")
print("  solo scores' does not formally entail intransitivity.  The prediction")
print("  can fail, and failure would be the better outcome for the corpus.")
print()
print("  This script performs NO measurement.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_INTRANSITIVITY_PREDICTION_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print("  receipt: microscopes/results/STAGE_INTRANSITIVITY_PREDICTION_V1.json")
