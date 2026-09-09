"""Withdrawing DEV-3's gift: what happens when the guard language may not contain the truth.

DEV-3 declared one gift and this module is about whether it was a convenience or
a requirement:

    The gift that IS taken, declared: the guard language contains the truth in
    the STRUCTURED regime.  A world where the guard language must also be learned
    is a different and larger experiment, and it can only make the arm's position
    worse.

"Can only make it worse" is the sort of sentence a lane writes about an
experiment it has not run.  This runs it, and the answer is sharper than "worse":
starting with a language too small to express the truth is not merely expensive,
it is UNSOUND, and the soundness argument DEV-3 relied on collapses.

Why, stated before it is measured
---------------------------------

DEV-3's arm may skip a scope check when its version space is a singleton, and
that is sound for one reason only: the truth is always consistent with the
observations, so if exactly one candidate survives, it is the truth.  That
argument needs the truth to be a candidate.  Remove the guarantee and it fails in
a way that is invisible from inside the arm:

    a level-1 predicate can be consistent with every observation so far while the
    truth is a level-3 predicate that agrees with it on everything seen and
    differs on something not yet seen

The arm then holds a SINGLETON version space containing a FALSE guard, skips a
check it has not earned, and answers wrongly.  Nothing in its own state
distinguishes that case from the sound one.  So the interesting question is not
whether a staged, self-expanding language is cheaper -- it is whether it can be
correct at all, and #143 lists self-expansion as a late-stage dependent
hypothesis, which is exactly the status this result would leave it in.

The three levels
----------------

``L1``   no exceptions, or ``index % p == phase`` for ``p`` in 2, 3
``L2``   L1, plus ``p`` in 4, 5, 6, 7
``L3``   L2, plus ``index % p == phase AND index < t``

Each world's true guard is drawn from a declared level.  A world at L3 is one
where an arm holding only L1 can be confidently wrong; a world at L1 is one where
holding L3 costs only slower identification, not correctness.

The arms, and what the capability gate does to them
---------------------------------------------------

``EXPANDING_ARM``        starts at L1 and widens a rule's language when that
                         rule's version space empties.  This is the
                         self-expansion hypothesis in its most favourable form:
                         it pays for expressiveness only when it has evidence it
                         needs it.
``FIXED_FULL_PARENT``    holds L3 from the start.  Slower to identify, because a
                         larger space needs more observations to collapse, and
                         SOUND, because the truth is always in it.
``FIXED_SMALL_PARENT``   holds L1 for ever.  Fastest to identify and wrong
                         whenever the world is not L1.
``REPLAY_ONLY_PARENT``   unchanged from DEV-2. It has no guards, so it is sound
                         everywhere and is the parent both guarded arms have to
                         beat.

Under publication constitution section 7 a work comparison is admissible only
between arms at matched correctness.  If the expanding arm is unsound on L2 and
L3 worlds then it has NO admissible work figure there, and reporting that it was
cheaper would be reporting the speed of a wrong answer.  That is the whole design:
the gate, not the arithmetic, is what decides this experiment.

What would make self-expansion survive
--------------------------------------

If the expanding arm stays at correctness 1.0 across all three levels, then a
level-1 singleton is in practice reliable in this world, the soundness worry is
theoretical rather than real, and the work comparison proceeds. That outcome is
registered as possible and would be the more interesting one.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from dev1 import D1World, Pair, VERIFY_COST, d1_stream
from dev3 import GUARD_BITS
from prereg import Commitment, commit
from retain import FACT_BITS, RULE_BITS, build_world

__all__ = ["DEV4_PLAN", "COMMITMENT", "Pred", "LEVELS", "language", "draw_truth",
           "build_level_world", "EXPAND_COST", "level_of"]


#: Charged once when a rule's language is widened: re-examining the evidence
#: already collected under a larger hypothesis space is work, not free.
EXPAND_COST: int = 15

LEVELS: tuple[int, ...] = (1, 2, 3)


@dataclass(frozen=True)
class Pred:
    """``period`` None means 'no exceptions'. ``limit`` None means no upper bound."""

    period: int | None
    phase: int = 0
    limit: int | None = None

    def excludes(self, index: int) -> bool:
        if self.period is None:
            return False
        if index % self.period != self.phase:
            return False
        return self.limit is None or index < self.limit


def language(level: int, extension: int) -> tuple[Pred, ...]:
    out = [Pred(None)]
    periods = {1: (2, 3), 2: (2, 3, 4, 5, 6, 7), 3: (2, 3, 4, 5, 6, 7)}[level]
    for p in periods:
        for phase in range(p):
            out.append(Pred(p, phase))
    if level >= 3:
        for p in periods:
            for phase in range(p):
                for limit in range(1, extension):
                    out.append(Pred(p, phase, limit))
    return tuple(out)


def level_of(pred: Pred, extension: int) -> int:
    for level in LEVELS:
        if pred in language(level, extension):
            return level
    raise ValueError(pred)


def draw_truth(level: int, extension: int, rng: random.Random) -> Pred:
    """A predicate that is IN the declared level and NOT in any lower one.

    Drawing from the level itself would let a level-3 world hand out level-1
    predicates, and the arm that starts small would look sound by luck. The
    levels have to be disjoint for the experiment to mean anything.
    """
    pool = [p for p in language(level, extension)
            if level == 1 or p not in language(level - 1, extension)]
    return rng.choice(pool)


def build_level_world(rule_count: int, extension: int, level: int,
                      rng: random.Random) -> tuple[D1World, dict[int, Pred]]:
    base = build_world(rule_count, extension)
    truth: dict[int, Pred] = {}
    exceptions: set[int] = set()
    for r in range(rule_count):
        pred = draw_truth(level, extension, rng)
        truth[r] = pred
        for index, answer in enumerate(base.members[r]):
            if pred.excludes(index):
                exceptions.add(answer)
    return D1World(base, frozenset(exceptions)), truth


DEV4_PLAN: Mapping[str, Any] = {
    "study_id": "DEV4_LANGUAGE_EXPANSION_V1",
    "programme": "SzeChunYiu/ORION-OCM#151, #143 self-expansion",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "withdraws_the_gift_declared_in": "results/DEV3_GUARDED_RULES_V1.json",
    "scientific_question": (
        "DEV-3's guarded arm was given a language containing the truth, and said so. If the "
        "language may NOT contain the truth, can a machine that starts small and widens its "
        "language on evidence remain CORRECT -- and if it can, is it cheaper than one that "
        "holds the full language throughout?"),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "the_argument_this_tests": (
        "DEV-3's soundness rests on the truth being a candidate: a singleton version space "
        "provably contains the truth only if the truth is in the space. Remove that and a "
        "small language can produce a singleton that is FALSE and indistinguishable, from "
        "inside the arm, from a sound one. The prediction is therefore about CORRECTNESS "
        "and not about cost, and the capability gate rather than the arithmetic decides it."),
    "decisive_causal_question": (
        "World level is the only knob. At level 1 every arm's language contains the truth "
        "and the comparison is about identification speed. At levels 2 and 3 the expanding "
        "arm and the small-language parent start outside the truth's family. Any correctness "
        "difference across levels is caused by that or by nothing."),
    "strongest_parent_attack": (
        "FIXED_FULL_PARENT holds the whole language from the start. It is slower to identify "
        "-- a bigger space needs more observations to collapse to a singleton -- and it is "
        "SOUND at every level. If self-expansion has a point, it is to beat this arm's "
        "identification speed without giving up its correctness."),
    "prior_information_audit": {
        "EXPANDING_ARM": "the level-1 language; it may widen on evidence at a charged cost, "
                         "and is never told the world's level",
        "FIXED_FULL_PARENT": "the level-3 language, which contains the truth at every level",
        "FIXED_SMALL_PARENT": "the level-1 language and no way to widen",
        "REPLAY_ONLY_PARENT": "no guards at all, so nothing to be wrong about",
        "ORACLE_LEVEL_PARENT": "the world's LEVEL for free, and the language for it. A "
                               "ceiling on what knowing how expressive to be is worth",
    },
    "capability_gate": (
        "A work figure is quoted for an arm only where its correctness is 1.0. An arm that "
        "is faster and wrong has no admissible cost, and the receipt reports NOT ADMISSIBLE "
        "rather than a number. This is the first experiment in this lane where the gate is "
        "expected to exclude the machine rather than a parent."),
    "predictions_frozen_before_execution": {
        "E1": ("At level 1 every arm reaches correctness 1.0, because every language "
               "contains the truth."),
        "E2": ("At levels 2 and 3 the EXPANDING_ARM and FIXED_SMALL_PARENT fall below "
               "correctness 1.0, because a level-1 singleton can be false. If they do not, "
               "the soundness worry is theoretical in this world and the receipt says so."),
        "E3": ("FIXED_FULL_PARENT stays at correctness 1.0 at every level."),
        "E4": ("Where the expanding arm IS admissible -- level 1 -- it beats "
               "FIXED_FULL_PARENT on work, because a smaller space collapses to a singleton "
               "on fewer observations and it starts skipping checks sooner."),
        "E5": ("Taken across all three levels, self-expansion does NOT survive as a "
               "developmental mechanism here: its advantage exists only where it is not "
               "needed, and where it is needed it is unsound. Registered in that direction "
               "because it is the outcome least favourable to the hypothesis #143 lists."),
    },
    "kill_criterion": (
        "If the expanding arm holds correctness 1.0 at every level AND beats "
        "FIXED_FULL_PARENT on work, self-expansion survives its first real test and DEV-3's "
        "gift was a convenience rather than a requirement. That would be a positive for the "
        "self-expansion hypothesis and is to be reported as one."),
    "pilot_disclosure": (
        "A pilot preceded this plan and changed its shape. At a single seed with 2000 D0 "
        "demands every arm reached correctness 1.0, which looked like a refutation of "
        "prediction E2 -- and was not. With near-complete evidence over a finite extension, "
        "what a guard needs is not the true FORMULA but a predicate extensionally equal to "
        "it on the sixteen indices, and a small language often contains one. The failure "
        "mode therefore lives at LOW EVIDENCE, so D0 length became a swept axis rather than "
        "a fixed setting. Across seeds it turned out that the expanding arm is below "
        "correctness 1.0 at level 3 at EVERY evidence length tested, including the longest, "
        "so E2 holds and the pilot's single seed was the misleading observation. The "
        "protected sweep runs on a disjoint seed and the pilot's numbers are published."),
    "sweep": {
        "rule_count": 16,
        "extension": 16,
        "d0_lengths": [50, 200, 800, 2000],
        "d1_length": 1000,
        "budget_bits": [1024],
        "levels": list(LEVELS),
        "skews": [0.0, 1.0],
        "reps": 8,
    },
    "why_d0_length_is_the_axis": (
        "Soundness here is not a property of the language alone but of the language TOGETHER "
        "with how much of each rule's extension has been observed. A version space collapses "
        "to a singleton on partial evidence, and a singleton reached on partial evidence can "
        "be false. Sweeping evidence is therefore sweeping the thing that decides the "
        "question, and holding it fixed -- as the first version of this plan did -- would "
        "have answered a different question at one arbitrary point on it."),
    "the_mechanism_to_watch": (
        "Expansion triggers when a version space EMPTIES. The failure mode is not emptiness, "
        "it is premature CERTAINTY: a wrong singleton never empties, so expansion never "
        "fires and cannot help. If the expanding arm's correctness tracks the fixed small "
        "parent's exactly, that is this mechanism showing, and it means the expansion "
        "machinery is inert against the failure that matters."),
    "costs": {"expand": EXPAND_COST, "guard_bits": GUARD_BITS, "verify": VERIFY_COST,
              "rule_bits": RULE_BITS, "fact_bits": FACT_BITS},
    "language_sizes": "computed in the receipt from language(level, extension)",
    "levels_are_disjoint": (
        "A world at level k draws truths that are in level k and NOT in level k-1. Drawing "
        "from the level itself would let a level-3 world hand out level-1 predicates and an "
        "arm starting small would look sound by luck."),
    "what_this_does_not_establish": (
        "Three levels of one predicate family, chosen by hand. A machine that could invent "
        "predicate families rather than move between three given ones is the thing #143 "
        "actually asks about, and it is not built here. The result bounds staged expansion "
        "over a given ladder of languages; it says nothing about inventing the ladder."),
    "novelty": (
        "NONE CLAIMED. Version-space learning is Mitchell 1982; the bias-variance tradeoff "
        "between hypothesis-space size and identification data is older than that; staged "
        "hypothesis-space expansion is standard in grammar induction and program synthesis. "
        "The contribution is running it against the capability gate."),
}

COMMITMENT: Commitment = commit(DEV4_PLAN)
