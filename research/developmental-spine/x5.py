"""X5: why the two surviving carry advantages depend on the budget in OPPOSITE
directions, and whether either is a regime or an isolated cell.

X4 ended with two positives and no theory joining them.

    The GUARDED arm on a SMALL language beats replay at level 1 -- but only at
    the larger of the two budgets swept. At the smaller budget it loses.

    The UNANIMITY arm on the FULL language beats replay at level 3 -- but only
    at the SMALLER budget, and only under uniform demand. At the larger budget
    it loses.

Two mechanisms that both "carry competence" should not respond to a bit budget
with opposite signs, and a lane that cannot say why does not understand its own
result. Worse, with two budgets swept, a sign that flips between them is equally
well explained by a boundary and by noise dressed as one. This study exists to
decide that.

The proposed explanation is a single asymmetry, and it is registered here before
any of it is run.

    The replay parent's cost FALLS with budget: more bits means more answers
    cached, so more lookups and fewer derivations. It is the arm most sensitive
    to the budget because storing answers is the only thing it does.

    The unanimity arm's cost is dominated by DELIBERATION -- it scans a version
    space it holds regardless of how many facts fit -- so its cost is roughly
    FLAT in the budget. Flat beats falling at the low end and loses at the high
    end. It wins where the parent is starved.

    The guarded arm's BENEFIT is budget-GATED: a guard costs bits from the same
    budget as the facts, so below some budget the store cannot hold the rules,
    their guards and a working set of facts at once, and the arm degenerates. It
    wins only once the gate opens.

If that is right, one law covers both: a carry advantage appears where the arm's
cost curve in the budget crosses the parent's, and the two mechanisms cross from
opposite sides because one is flat and one is gated. Each has exactly ONE
crossing, and the crossings run in opposite directions.

DEV-3's own analytic window put the lower edge at rule_count * (RULE_BITS +
GUARD_BITS) = 768 bits, and X4 already refuted that: the guarded arm loses at
1024. So the gate, whatever it is, is strictly above the bits needed to hold the
guards. This study sweeps nine budgets rather than two and reads the gate off
the store's own state instead of guessing it a second time.

A third question is imported from outside this lane. The independent review of
PR #150 (research/evolvability-source-review-v1) shows by counterexample that a
calibrated posterior's perplexity chi = 2^H does not bound expected guess cost:
with N = 2^m repairs of probability 1/(mN) and one leading repair of probability
1 - 1/m, chi <= 4 while E[rank] = 1 + (N+1)/(2m) grows without bound. The same
objection applies here, because this lane's informal story has been "a small
language collapses, so the arm wins" -- which is a claim about the SIZE of a
surviving set. X5 registers the correction as a prediction: the size of the
version space does not determine the sign of the carry advantage; the COST of
consulting one does.
"""
from __future__ import annotations

from typing import Any, Mapping

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from prereg import Commitment, commit
from retain import FACT_BITS, RULE_BITS

__all__ = ["X5_PLAN", "COMMITMENT", "BUDGETS", "DEV3_ANALYTIC_LOWER_EDGE"]

#: Nine budgets, of which two (1024, 1536) were swept by X4 and reproduce it, and
#: seven are OUT OF SAMPLE for every prediction below.
BUDGETS: tuple[int, ...] = (768, 896, 1024, 1152, 1280, 1408, 1536, 1792, 2048)

#: rule_count * (RULE_BITS + GUARD_BITS) with rule_count 16 and GUARD_BITS 16.
#: DEV-3 offered this as the lower edge of its window. X4 refuted it at 1024.
DEV3_ANALYTIC_LOWER_EDGE: int = 16 * (RULE_BITS + 16)

X5_PLAN: Mapping[str, Any] = {
    "study_id": "X5_BUDGET_CROSSING_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "resolves": "results/X4_FINAL_ACCOUNTING_V1.json open question: opposite budget signs",
    "imports": "PR #153 research/evolvability-source-review-v1/PR150-MATH-REVIEW.md",
    "scientific_question": (
        "X4 left two carry advantages with opposite budget dependence and no account of "
        "why. Is each a REGIME with a single crossing in the budget, and is one asymmetry "
        "-- a flat-cost arm against a falling-cost parent, versus a gated-benefit arm -- "
        "enough to explain both signs?"),
    "evidence_class": "E2",
    "contribution_level": "L2",
    "why_this_is_not_a_curve_fit": (
        "Two of the nine budgets are X4's and seven are new. Every prediction below is "
        "about the SHAPE of the margin over the seven unswept budgets, registered before "
        "any of them is executed, and each is refutable by a shape the sweep can produce: "
        "no crossing, more than one crossing, or a crossing in the wrong direction."),
    "prior_information_audit": {
        "known_before_this_study": (
            "X4's twenty-four cells: at level 1 the guarded arm wins at 1536 and loses at "
            "1024; at level 3 the unanimity arm wins at 1024 under uniform demand and "
            "loses at 1536. Both budgets are re-run here and must reproduce, which is a "
            "control on the harness and not a prediction."),
        "not_known_before_this_study": (
            "Anything about the seven other budgets, where either crossing lies, whether "
            "either is single, and whether the held-guard count explains the gate."),
    },
    "capability_gate": (
        "A work figure is quoted only where correctness is 1.0 in every replicate, for the "
        "arm AND for the replay parent it is divided by. The small-language arm has no "
        "admissible figure at level 3 and is not quoted there."),
    "predictions_frozen_before_execution": {
        "Y1": ("The guarded small-language arm's margin against replay at level 1 crosses "
               "zero EXACTLY ONCE over the nine budgets, from losing at low budgets to "
               "winning at high ones, and stays won above the crossing."),
        "Y2": ("That crossing is the GATE and the gate is visible in the store: the arm's "
               "held guarded-rule count, averaged over replicates, is strictly below "
               "rule_count at every budget below the crossing and equal to rule_count at "
               "every budget at or above it. If the held count is already saturated below "
               "the crossing, Y2 is REFUTED and the gate is something else, which must "
               "then be named from the counters rather than left as a curve."),
        "Y3": ("The unanimity full-language arm's margin at level 3 under uniform demand "
               "crosses zero EXACTLY ONCE and in the OPPOSITE direction: winning at low "
               "budgets, losing at high ones."),
        "Y4": ("The asymmetry that produces the opposite signs is that the unanimity arm's "
               "total work is FLAT in the budget while the replay parent's FALLS. "
               "Registered quantitatively: over the nine budgets the unanimity arm's work "
               "varies by less than a factor of 1.5 between its smallest and largest "
               "value, while the replay parent's varies by more than a factor of 2."),
        "Y5": ("The SIZE of the version space does not determine the sign of the carry "
               "advantage; the COST of a consultation does. Registered as two concrete "
               "requirements. (a) There exist two cells with the SAME language, hence the "
               "same version-space size regime, and OPPOSITE carry sign -- so no function "
               "of language size alone predicts the sign. (b) The margin recomputed from "
               "the priced event counters alone reproduces the measured work difference "
               "to the integer in EVERY cell, so the sign is a function of what was "
               "charged, not of what was held."),
    },
    "kill_criterion": (
        "If Y1 and Y3 both fail -- neither margin has a single clean crossing over nine "
        "budgets -- then this lane cannot describe the boundary of its own result, X4's "
        "positive is an isolated cell rather than a regime, and the carry advantage must "
        "be reported as UNCHARACTERISED. That is to be reported in those words, and X4's "
        "receipt is not withdrawn on account of it."),
    "sweep": {
        "rule_count": 16, "extension": 16, "d0_length": 800, "d1_length": 1000,
        "budget_bits": list(BUDGETS), "levels": [1, 3], "skews": [0.0, 1.0], "reps": 8,
    },
    "arms": {
        "GUARDED_SMALL_LANGUAGE": "level-1 language, singleton rule, charged 1",
        "UNANIMITY_FULL_LANGUAGE": "level-3 language, unanimity rule, charged len(survivors)",
        "REPLAY_ONLY_PARENT": "no guards, no rules, stores answers only",
    },
    "what_this_does_not_establish": (
        "The same single charge rule X4 defended and did not canonise, on DEV-4's synthetic "
        "worlds, at one D1 length. A crossing located here is a crossing in THESE worlds. "
        "Nothing here concerns routing, learned policy or any real system, and nothing here "
        "licenses one."),
    "novelty": (
        "NONE CLAIMED as a mechanism. The contribution is a boundary: turning two isolated "
        "positive cells into two regimes with located edges, or failing to and saying so."),
}

COMMITMENT: Commitment = commit(X5_PLAN)
