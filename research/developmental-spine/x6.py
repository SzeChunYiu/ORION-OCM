"""X6: a LARGE version space with an O(1) consultation, which is the case that
separates the two stories this lane has been telling.

Every carry advantage this lane has shown survives on a small language.

    DEV-3 won with a guard drawn from a 15-predicate language and was told by
    DEV-4 that the small language was a PRECONDITION, not a convenience.

    DEV-5 removed that dependency by acting on per-query unanimity over a large
    language, and DEV-6 then charged the scan that rule performs and took the
    factor from 5.1x to 3.4x.

    X4 found the one survivor after every audit: the small-language guarded arm,
    whose consultation is a dict lookup and a modular test and is honestly
    charged 1.

    X5 swept nine budgets and found the survivor lives in [1408, 1536] bits, a
    quarter of the window DEV-3 computed, and that on the full language the
    unanimity arm never beats replay under SKEWED demand at any budget.

Two explanations fit all of that, and this lane has never separated them.

    THE SIZE STORY. A small hypothesis space wins because it is small: it
    collapses, so the rule fires. Large spaces do not collapse, so nothing fires
    and the arm verifies. On this account DEV-4's precondition is permanent.

    THE CHARGE STORY. The size is irrelevant and the COST OF A CONSULTATION is
    what decides. The small language wins because consulting it costs 1; the
    large language loses because consulting it costs what it scans.

The independent review of PR #150 published in PR #153 shows the size story is
unsafe in general: a calibrated posterior's perplexity chi = 2^H does not bound
expected guess cost, since with N = 2^m repairs of probability 1/(mN) and one
leading repair of probability 1 - 1/m, chi is at most 4 while the expected
optimal guess rank is 1 + (N+1)/(2m). X5 tested the analogue here and found the
same language produces BOTH signs of the carry advantage. Neither result builds
the arm that would settle it.

This one does. It compiles the unanimity verdict into a per-rule decision table
and consults the table, so the version space stays at 433 predicates and a
consultation costs 1. The size story predicts this changes nothing, because the
space is still large. The charge story predicts it recovers the advantage on a
language nobody had to choose in advance -- which is what #151 actually wants
and what DEV-4 said could not be had.

The compilation is not free and is not treated as free. Two arms pay for it in
the two ways a system can:

    PRECOMPILED_EAGER compiles every index of a rule the moment the rule's
    version space changes, and is charged for the whole scan it performs. This
    is a compiled bank.

    PRECOMPILED_DEMAND compiles an index the first time that index is demanded
    and keeps it until the space actually shrinks. This is demand-driven
    grounding, which is the lever PR #153's grounding review names as the next
    one for the native lane, brought here where it can be measured exactly.

The point of running both is that this lane has already predicted, in
synthesis.py's NATIVE_LANE_CROSS_CHECK, that eager compilation buys nothing and
demand-driven compilation is what pays. That prediction was made about another
lane's units. Here it is cheap to check in this lane's own.
"""
from __future__ import annotations

from typing import Any, Mapping

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from prereg import Commitment, commit
from x5 import BUDGETS

__all__ = ["X6_PLAN", "COMMITMENT", "ARM_MODES"]

#: Every arm holds the FULL 433-predicate language. Only the charge differs.
ARM_MODES: Mapping[str, str] = {
    "UNANIMITY_NAIVE": "unanimity_naive",
    "PRECOMPILED_EAGER": "precompiled_eager",
    "PRECOMPILED_DEMAND": "precompiled_demand",
}

X6_PLAN: Mapping[str, Any] = {
    "study_id": "X6_COMPILED_CONSULTATION_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "extends": ["results/X4_FINAL_ACCOUNTING_V1.json",
                "results/X5_BUDGET_CROSSING_V1.json"],
    "imports": "PR #153 research/native-grounding-review-v1/DECISION.md",
    "scientific_question": (
        "Every carry advantage this lane has shown needs a small language. Is that because "
        "small spaces COLLAPSE, or because small spaces are CHEAP TO CONSULT? Compiling the "
        "unanimity verdict into a per-rule table keeps the space at 433 predicates and makes "
        "a consultation cost 1, which separates the two for the first time."),
    "evidence_class": "E2",
    "contribution_level": "L2",
    "what_is_new_here": (
        "An arm, not an analysis. DEV-6 charged the scan and X5 showed the charge predicts "
        "the sign; neither built a mechanism that pays the charge differently. The compiled "
        "table is that mechanism, and it is the first thing in this lane that could remove "
        "DEV-4's language precondition rather than work around it."),
    "the_control_that_makes_this_readable": (
        "PRECOMPILED_DEMAND must return the SAME verdict as UNANIMITY_NAIVE at every "
        "consultation. Compilation is permitted to change what a consultation costs and "
        "nothing else. Every non-deliberation counter and the correctness of both arms must "
        "therefore be identical at every setting. If they are not, the compiled arm is a "
        "different decision rule wearing the same name and this study is VOID."),
    "prior_information_audit": {
        "UNANIMITY_NAIVE": "the full language; DEV-5's rule at DEV-6's honest price",
        "PRECOMPILED_EAGER": "the same language and the same verdicts, compiled for every "
                             "index on every change and charged for the whole scan",
        "PRECOMPILED_DEMAND": "the same language and the same verdicts, compiled for an "
                              "index the first time it is demanded and kept until the "
                              "version space actually shrinks",
        "REPLAY_ONLY_PARENT": "no rules, no guards, stores answers; the parent to beat",
    },
    "capability_gate": (
        "A work figure is quoted only where correctness is 1.0 in every replicate, for the "
        "arm and for the replay parent it is divided by."),
    "predictions_frozen_before_execution": {
        "W1": ("Reuse exists: PRECOMPILED_DEMAND's cache hit rate exceeds 0.5 at some "
               "setting, and its deliberation is strictly below UNANIMITY_NAIVE's at every "
               "setting. If the hit rate is low everywhere, demand-driven compilation has "
               "nothing to amortise over and the mechanism is inert."),
        "W2": ("THE CONTROL. PRECOMPILED_DEMAND and UNANIMITY_NAIVE agree on correctness "
               "and on every non-deliberation counter -- derivations, applications, "
               "lookups, inductions, verifications -- at every setting. Failure VOIDS the "
               "study rather than refuting a prediction."),
        "W3": ("The set of settings where PRECOMPILED_DEMAND beats replay is a STRICT "
               "SUPERSET of the set where UNANIMITY_NAIVE does. Cheaper consultation can "
               "only widen a regime, never move it, because nothing else changed."),
        "W4": ("PRECOMPILED_EAGER's deliberation exceeds PRECOMPILED_DEMAND's at every "
               "setting, and eager beats replay at no setting where demand-driven does not. "
               "This is the lane-internal form of the prediction synthesis.py already made "
               "about the native lane: compiling the whole bank buys nothing, and making "
               "the fixed cost proportional to the demand is what pays."),
        "W5": ("THE DECISIVE ONE. At level 3 under SKEWED demand -- where X5 measured that "
               "UNANIMITY_NAIVE beats replay at NONE of the nine budgets -- "
               "PRECOMPILED_DEMAND beats replay at at least one budget at correctness 1.0. "
               "The size story predicts this cannot happen, because the space is still 433 "
               "predicates. The charge story predicts it, because a consultation now costs "
               "1. There is no third account under which it happens."),
    },
    "kill_criterion": (
        "If W5 fails, then making a consultation O(1) does NOT free the carry advantage "
        "from the language it is drawn from. DEV-4's precondition is then not removable by "
        "pricing, the size story survives its sharpest test, and every carry advantage this "
        "lane has is confined to languages small enough to collapse -- which must be "
        "reported in those words, with X4's and X5's receipts unchanged."),
    "sweep": {
        "rule_count": 16, "extension": 16, "d0_length": 800, "d1_length": 1000,
        "budget_bits": list(BUDGETS), "levels": [1, 3], "skews": [0.0, 1.0], "reps": 8,
    },
    "what_this_does_not_establish": (
        "The compiled table is charged 1 per consultation and its own storage is NOT charged "
        "bits, exactly as DEV-3's guard was charged bits and DEV-5's version space was not. "
        "That is this lane's existing and imperfect convention, applied unchanged so the "
        "comparison is about the charge rule and not about a new one. A study that prices "
        "the table in bits is the obvious successor and is not this study. Nothing here "
        "concerns routing, learned policy, or any real system."),
    "novelty": (
        "NONE CLAIMED as a technique: a compiled decision table over a version space is "
        "ordinary memoisation, and demand-driven compilation is the magic-set idea PR #153's "
        "grounding review cites from Souffle. The contribution is using them to decide "
        "between two explanations of this lane's own results."),
}

COMMITMENT: Commitment = commit(X6_PLAN)
