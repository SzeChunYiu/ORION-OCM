"""X4: one accounting standard applied to every carry-advantage claim this lane made.

X3 left the lane in an unresolved state, and this module exists to resolve it
rather than leave it as a caveat.

    DEV-3 reported a carry advantage from a GUARDED rule: a single collapsed
    predicate, consulted in O(1), charged nothing.

    DEV-5 reported a carry advantage from UNANIMITY over a large version space,
    charged a flat price per consultation.

    DEV-6 showed the flat price was this lane's own choice and re-priced the
    unanimity arm in proportion to what it scans. It re-checked unanimity against
    the SINGLETON rule and did not re-check either against REPLAY.

    X3 did re-check that, and found the unanimity lineage loses to replay at four
    of six settings under the honest price.

What was never done is the obvious one: re-price DEV-3. Its guard is a single
predicate, so a consultation is a dict lookup and a modular test -- genuinely
O(1) -- and the honest charge for it is 1, exactly what DEV-6 charged the
singleton rule. So DEV-6 already priced DEV-3's MECHANISM correctly and ran it
over the wrong LANGUAGE: 433 predicates rather than the 15 DEV-3 used. A version
space that large almost never collapses, so the singleton rule almost never
fires, and the arm verifies on nearly every demand. That is a fact about language
size, not about guards.

This module runs the singleton rule over BOTH languages under one charge rule --
a consultation costs what it examines -- against replay, on the same worlds, at
the same budgets. It answers the question the lane has been circling for six
experiments:

    after every audit, does any carry advantage survive, and on what condition?

The honest possibilities are all live. If the small-language guarded arm beats
replay under the honest charge, DEV-3's result stands and the lane has a carry
advantage conditional on DEV-4's language precondition. If it does not, the lane
has no carry advantage under any representation it has tried, X3's finding
generalises, and DEV-3 must be corrected the way DEV-5 was.
"""
from __future__ import annotations

from typing import Any, Mapping

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from dev4 import LEVELS, language
from prereg import Commitment, commit

__all__ = ["X4_PLAN", "COMMITMENT", "ARM_LANGUAGES"]

#: The language each arm searches. This is the axis DEV-6 held fixed and should
#: not have: DEV-3's arm never had 433 candidates to collapse through.
ARM_LANGUAGES: Mapping[str, int] = {
    "GUARDED_SMALL_LANGUAGE": 1,   # DEV-3's regime: few predicates, collapses fast
    "SINGLETON_FULL_LANGUAGE": 3,  # DEV-6's regime: contains every truth, collapses slowly
    "UNANIMITY_FULL_LANGUAGE": 3,  # DEV-5's rule, honestly charged
}

X4_PLAN: Mapping[str, Any] = {
    "study_id": "X4_FINAL_ACCOUNTING_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "resolves": "results/X3_PRICE_FREE_V1.json",
    "audits": ["results/DEV3_GUARDED_RULES_V1.json", "results/DEV5_UNANIMITY_V1.json"],
    "scientific_question": (
        "DEV-6 re-priced this lane's consultation honestly and DEV-3 was never re-priced. "
        "Under one charge rule -- a consultation costs what it examines -- does any carry "
        "advantage this lane has claimed survive against the replay parent, and on what "
        "condition?"),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "the_confound_being_removed": (
        "DEV-6 charged the singleton rule correctly and ran it over the full 433-predicate "
        "language, which is not the language DEV-3 used. A version space that large rarely "
        "collapses to a singleton, so the rule rarely fires and the arm verifies on nearly "
        "every demand. Attributing that to the guarded MECHANISM rather than to LANGUAGE "
        "SIZE would misread DEV-6, and X3 inherited the misreading when it concluded from "
        "DEV-6's arms that the carry advantage fails."),
    "decisive_causal_question": (
        "Language size is the only thing that differs between GUARDED_SMALL_LANGUAGE and "
        "SINGLETON_FULL_LANGUAGE. Same decision rule, same charge, same worlds, same "
        "streams, same budgets. Any difference between them is caused by how many "
        "candidates the space holds or by nothing."),
    "charge_rule": (
        "A consultation costs what it examines: 1 for the singleton test, which inspects "
        "whether a set has one element, and len(survivors) for the unanimity scan. This is "
        "E6's standard, adopted in DEV-6, and it is applied here to every arm including the "
        "one this lane most wants to survive."),
    "prior_information_audit": {
        "GUARDED_SMALL_LANGUAGE": "the level-1 language only; unsound wherever the truth is "
                                  "outside it, which DEV-4 established and this study "
                                  "re-checks rather than assumes",
        "SINGLETON_FULL_LANGUAGE": "the full language, sound everywhere, slow to collapse",
        "UNANIMITY_FULL_LANGUAGE": "the full language with the weaker decision rule",
        "REPLAY_ONLY_PARENT": "no guards; sound everywhere; the parent to beat",
    },
    "capability_gate": (
        "A work figure is quoted only where correctness is 1.0 in every replicate. "
        "GUARDED_SMALL_LANGUAGE is expected to fail this at levels 2 and 3, exactly as "
        "DEV-4 measured, and to have no admissible cost there."),
    "predictions_frozen_before_execution": {
        "Z1": ("At level 1, where its language contains the truth, "
               "GUARDED_SMALL_LANGUAGE is sound and BEATS REPLAY_ONLY_PARENT under the "
               "honest charge. DEV-3's result then stands and X3's negative was a "
               "statement about language size, not about guards."),
        "Z2": ("SINGLETON_FULL_LANGUAGE loses to replay at level 1, reproducing DEV-6 and "
               "X3, so the difference between it and the small-language arm is the "
               "language and nothing else."),
        "Z3": ("GUARDED_SMALL_LANGUAGE is unsound at level 3 and has no admissible work "
               "figure there, reproducing DEV-4."),
        "Z4": ("UNANIMITY_FULL_LANGUAGE beats SINGLETON_FULL_LANGUAGE everywhere, "
               "reproducing DEV-6, so nothing here withdraws that result."),
        "Z5": ("No arm beats replay at level 3 at matched correctness. If one does, the "
               "carry advantage is broader than this lane has ever claimed and that must be "
               "reported as a surprise rather than banked."),
    },
    "kill_criterion": (
        "If GUARDED_SMALL_LANGUAGE does not beat replay at level 1 under the honest charge, "
        "this lane has NO carry advantage under any representation it has tried. DEV-3 must "
        "then be corrected the way DEV-5 was, X3's finding generalises, and the developmental "
        "spine's one measured transition loses its positive. That is to be reported in those "
        "words."),
    "sweep": {
        "rule_count": 16, "extension": 16, "d0_length": 800,
        "d1_lengths": [1000, 4000], "budget_bits": [1024, 1536],
        "levels": list(LEVELS), "skews": [0.0, 1.0], "reps": 8,
    },
    "what_this_does_not_establish": (
        "One charge rule, defended but not canonical, exactly as DEV-6 conceded. The worlds "
        "are DEV-4's, so every limitation declared there applies unchanged. What this "
        "settles is an internal inconsistency in this lane's own accounting, not a fact "
        "about routing or about real systems."),
    "novelty": (
        "NONE CLAIMED. This is bookkeeping applied evenly. The contribution is noticing that "
        "the lane had priced one of its two carry-advantage claims and not the other, and "
        "that the unpriced one had been judged by a proxy running the wrong language."),
}

COMMITMENT: Commitment = commit(X4_PLAN)
