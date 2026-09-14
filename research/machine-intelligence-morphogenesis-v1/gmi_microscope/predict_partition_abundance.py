"""FROZEN PREDICTION: resource partitioning and abundance.  Phase one, no measuring code.

Section G boxes 11 and 12 are the last two open in the ecology half.  Both are
answerable from data already on disk: R10's cells carry `charge_resident`,
`charge_invader` and `pool_spent` for all 192 competitions, and the outcome of
every contest is recorded at three budget pools.

BOX 11 -- RESOURCE PARTITIONING
    The pool is shared but the SPLIT has never been measured.  For each decided
    contest, compare the charge each competitor drew.

    P1  the winner draws MORE charge than the loser in a strict majority of
        decided contests.

    Reasoning: winning here means developing further within the shared pool, and
    development is what charge buys.  The alternative is real though -- a loser
    can burn charge and still fail, which would make charge a poor predictor of
    who wins, and that is the outcome that would make box 11 interesting in a
    different way.

    P2  the split is not degenerate: at least one decided contest has the LOSER
        drawing more.  Without this, "winner spends more" could be true by
        construction rather than by competition.

BOX 12 -- ABUNDANCE FROM ECOLOGY
    Abundance is read as win count: how many of its contests each carrier wins
    in a pool.

    P3  the carrier with the highest win count is THE SAME in all three pools.

    Reasoning: dominance was measured acyclic where both readings agree, and
    only 7 of 56 ordered pairs change winner under repricing.  A top carrier
    should survive that.  But repricing is now known to be non-monotone, and 2
    pairs oscillate, so the top slot can move -- this is a genuine risk.

    P4  win counts are not uniform: some carrier wins strictly more than
        another in at least one pool.  Without this, "abundance" has no
        variation to predict and P3 is vacuous.

WHY EACH RISKY CLAIM IS PAIRED WITH A CONTROL
    The same discipline that made box 10's zero and box 13's falsification
    believable: a bare claim about a majority or a maximum can be satisfied by a
    degenerate measurement, so each is paired with a check that the underlying
    quantity actually varies.

FALSIFIERS
    P1 fails if the winner draws more in half or fewer of the decided contests.
    P2 fails if the winner draws more in EVERY decided contest.
    P3 fails if the top carrier differs between any two pools.
    P4 fails if every carrier has the same win count in every pool.
"""

import json
import os

OUT = {
    "registration": "GMI_PARTITION_ABUNDANCE_PREDICTION_V1",
    "phase": "prediction -- no measurement performed or available in this script",
    "source_evidence": "STAGE_R10_INVASION_V1.json: cells charge_* and invasion_matrix_by_pool",
    "box_11_P1": "the winner draws more charge than the loser in a strict majority of decided contests",
    "box_11_P2": "at least one decided contest has the loser drawing more (non-degeneracy)",
    "box_12_P3": "the carrier with the highest win count is the same in all three pools",
    "box_12_P4": "win counts are not uniform in at least one pool (non-vacuity)",
    "reasoning_11": (
        "winning means developing further within the shared pool and development "
        "is what charge buys; the alternative -- a loser burning charge and still "
        "failing -- would make charge a poor predictor of who wins"),
    "reasoning_12": (
        "dominance is acyclic where both readings agree and only 7 of 56 ordered "
        "pairs change under repricing, so a top carrier should survive; but "
        "repricing is known non-monotone with 2 oscillating pairs, so the top "
        "slot can move"),
    "why_controls": (
        "a bare claim about a majority or a maximum can be satisfied by a "
        "degenerate measurement, so each risky claim is paired with a check that "
        "the underlying quantity actually varies"),
    "falsifiers": [
        "P1 fails if the winner draws more in half or fewer decided contests",
        "P2 fails if the winner draws more in EVERY decided contest",
        "P3 fails if the top carrier differs between any two pools",
        "P4 fails if every carrier has the same win count in every pool",
    ],
    "caveat_carried": (
        "the R10 allocation rule is a modelling choice and a different rule can "
        "reorder outcomes"),
}

print("=" * 78)
print("FROZEN PREDICTION -- resource partitioning (box 11) and abundance (box 12)")
print("=" * 78)
print("  BOX 11  P1 winner draws MORE charge than loser, strict majority")
print("          P2 at least one decided contest has the LOSER drawing more")
print()
print("  BOX 12  P3 the top-win-count carrier is the SAME in all three pools")
print("          P4 win counts are not uniform in at least one pool")
print()
print("  P2 and P4 are controls.  A claim about a majority or a maximum can be")
print("  satisfied by a degenerate measurement, so each risky claim is paired")
print("  with a check that the underlying quantity actually varies.")
print()
print("  P3 carries real risk: repricing is now known to be NON-monotone, with")
print("  2 oscillating pairs, so the top slot can move between pools.")
print()
print("  This script performs NO measurement.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_PARTITION_ABUNDANCE_PREDICTION_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print("  receipt: microscopes/results/STAGE_PARTITION_ABUNDANCE_PREDICTION_V1.json")
