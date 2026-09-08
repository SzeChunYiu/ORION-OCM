"""Unanimity: acting on a version space that has not collapsed.

DEV-4 left the lane with a dilemma it did not resolve, and this module is about
whether the dilemma was real or an artifact of one arbitrary decision rule.

    FIXED_FULL_PARENT holds a language containing the truth, so it is SOUND at
    every level -- and it is slow, because a 433-predicate space rarely collapses
    to a singleton, so it pays a scope check almost every time.

    The expanding and small-language arms reach a singleton quickly and are
    UNSOUND wherever the truth is outside their language, which is exactly where
    the mechanism was supposed to help.

Both horns come from the same rule: *use a guard only when the version space is a
SINGLETON*.  That rule is sufficient for soundness and it is not necessary, and
DEV-3 and DEV-4 both took it as given without noticing it was a choice.

The weaker rule that is still sound
-----------------------------------

A guard is consulted about ONE index at a time.  The arm does not need to know
which predicate is true; it needs to know what the true predicate SAYS about this
index.  So:

    if every surviving candidate agrees on ``excludes(index)``, the answer is
    determined whichever candidate is the truth

That is sound for exactly the same reason the singleton rule is -- the truth is
always among the survivors -- and it fires far more often, because a large
version space can be unanimous about most indices while remaining undecided about
which predicate it is.  A version space of 433 predicates that disagrees about
one index is still decisive about the other fifteen.

This is per-QUERY rather than per-RULE, and that is the whole idea: DEV-3 and
DEV-4 asked "do I know the guard", which is a question about the rule, when the
question they actually needed answered was "do I know this answer's status",
which is a question about the query.

What this does NOT rescue
-------------------------

Unanimity is sound only while the truth is among the survivors.  Give it a
language that cannot express the truth and it inherits exactly the failure DEV-4
measured, because a small version space is unanimous more often and is unanimously
WRONG more often.  ``UNANIMITY_SMALL`` is in the arm set to make that visible: if
unanimity looked like a general fix rather than a fix for the decision rule, that
arm is where the illusion breaks.

Charging for the consultation
-----------------------------

Deciding unanimity means scanning the surviving candidates; deciding singleton
means checking whether there is one.  Neither is free and neither was charged in
DEV-3 or DEV-4.  Both are charged here at ``CONSULT_COST`` per guard consultation,
identically, and the receipt sweeps that price from zero to the price of a real
scope check.  If unanimity only wins when consulting its own store is far cheaper
than querying the world, the sweep says so.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from dev1 import VERIFY_COST, d1_stream
from dev3 import GUARD_BITS
from dev4 import EXPAND_COST, LEVELS, build_level_world, language
from prereg import Commitment, commit

__all__ = ["DEV5_PLAN", "COMMITMENT", "CONSULT_COST"]


#: Charged per guard consultation, to BOTH decision rules, so that neither is
#: handed free computation. Registered at the price of a store lookup, because
#: consulting a structure you already hold is what it is.
CONSULT_COST: int = 1


DEV5_PLAN: Mapping[str, Any] = {
    "study_id": "DEV5_UNANIMITY_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "responds_to": "results/DEV4_LANGUAGE_EXPANSION_V1.json",
    "scientific_question": (
        "DEV-3 and DEV-4 both used a guard only when its version space was a SINGLETON. "
        "That rule is sufficient for soundness and not necessary. If the arm instead asks, "
        "per query, whether every surviving candidate AGREES about this index, does it keep "
        "the full language's soundness and gain the small language's speed?"),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "the_argument": (
        "A guard is consulted about one index at a time. Unanimity among survivors "
        "determines the answer whichever survivor is the truth, so it is sound for exactly "
        "the reason the singleton rule is -- the truth is always among the survivors -- and "
        "it fires far more often, because a version space can be unanimous about most "
        "indices while undecided about which predicate it is."),
    "decisive_causal_question": (
        "SINGLETON_FULL and UNANIMITY_FULL hold the SAME language, see the same streams, "
        "run the same budget and differ in one line: when they are willing to act. Any "
        "difference between them is caused by the decision rule or by nothing."),
    "strongest_parent_attack": (
        "REPLAY_ONLY_PARENT, which beat this lane in DEV-2 and lost to DEV-3's guarded arm "
        "only under a declared gift that DEV-4 then showed was a precondition. If unanimity "
        "beats it WITHOUT that gift -- holding a language large enough to contain the truth "
        "at every level, rather than one hand-fitted to the world -- the DEV-3 result stops "
        "depending on the condition DEV-4 found binding."),
    "prior_information_audit": {
        "UNANIMITY_FULL": "the full language, which contains every world's truth; no world "
                          "level, no guard, no exception set",
        "SINGLETON_FULL": "identical, and acts only on a singleton",
        "UNANIMITY_SMALL": "the level-1 language only; unanimity over a space that may not "
                           "contain the truth, which is the control",
        "REPLAY_ONLY_PARENT": "no guards at all",
        "ORACLE_GUARD_PARENT": "the true guard for every rule, free. A ceiling",
    },
    "capability_gate": (
        "A work figure is quoted only where correctness is 1.0 in every replicate. "
        "UNANIMITY_SMALL is expected to fail this at levels 2 and 3 and to have no "
        "admissible cost there, exactly as DEV-4's small-language arms did."),
    "predictions_frozen_before_execution": {
        "U1": ("UNANIMITY_FULL holds correctness 1.0 at every level and evidence length. It "
               "is sound by construction and a failure here is a harness bug, not a finding."),
        "U2": ("UNANIMITY_FULL beats SINGLETON_FULL on work at every setting, because it "
               "acts strictly more often on the same information at the same soundness."),
        "U3": ("UNANIMITY_FULL beats REPLAY_ONLY_PARENT inside DEV-3's analytic budget "
               "window, WITHOUT the language gift DEV-3 needed."),
        "U4": ("UNANIMITY_FULL does not beat ORACLE_GUARD_PARENT. If it does, the ceiling "
               "is wrong and the run is void."),
        "U5": ("UNANIMITY_SMALL is unsound at levels 2 and 3, showing that unanimity fixes "
               "the DECISION RULE and not a deficient language. If it is sound there, the "
               "DEV-4 result does not mean what it was taken to mean."),
    },
    "kill_criterion": (
        "If UNANIMITY_FULL does not beat SINGLETON_FULL, the version space is rarely "
        "unanimous about an index it has not decided, the weaker rule is inert, and the "
        "dilemma DEV-4 left is real rather than an artifact of the decision rule."),
    "sweep": {
        "rule_count": 16,
        "extension": 16,
        "d0_lengths": [200, 800, 2000],
        "d1_length": 1000,
        "budget_bits": [1024, 1536],
        "levels": list(LEVELS),
        "skews": [0.0, 1.0],
        "reps": 8,
    },
    "consult_cost_sweep": [0, 1, 5, 25],
    "registered_consult_cost": CONSULT_COST,
    "consult_cost_note": (
        "Deciding unanimity scans the survivors; deciding singleton tests whether there is "
        "one. Neither is free and neither was charged in DEV-3 or DEV-4. Both are charged "
        "here, identically, and the price is swept up to the price of a real scope check so "
        "that a reader can see whether the result needs consultation to be cheap."),
    "costs": {"consult": CONSULT_COST, "verify": VERIFY_COST, "guard_bits": GUARD_BITS,
              "expand": EXPAND_COST},
    "what_this_does_not_establish": (
        "Unanimity is an old idea about version spaces and is not new here. The languages "
        "and the world are DEV-4's, so every limitation declared there applies unchanged: "
        "three levels of one hand-chosen predicate family, disjoint uniform rules, "
        "error-free induction, one stage pair. What changes is a decision rule, and the "
        "claim is about that rule and nothing wider."),
    "novelty": (
        "NONE CLAIMED. Acting on the unanimous part of an uncollapsed version space is "
        "Mitchell 1982 and is standard in version-space and abstaining-classifier work. "
        "The contribution is noticing that two earlier experiments in this lane had taken "
        "the stronger rule for granted, and measuring what that cost them."),
}

COMMITMENT: Commitment = commit(DEV5_PLAN)
