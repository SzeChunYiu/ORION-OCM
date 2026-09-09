"""X7: charge the compiled table its bits, and find out whether X6's result was a
result or an accounting artefact.

X6 showed that the carry advantage stops needing a small language once a
consultation costs 1 rather than what it scans. It reached that by compiling the
unanimity verdict into a per-rule decision table, and it charged that table
nothing to hold.

That is not an oversight this study discovered afterwards -- X6 declared it in
its own limits -- but it is exactly the pattern every real correction in this
lane has followed. DEV-2 corrected DEV-1 by charging rule USE. X1 corrected E6 by
charging DELIBERATION. DEV-6 corrected DEV-5 by charging the SCAN, and then
refuted this lane's own proposed fix for it. Each time something previously free
was billed, and each time the sign of a result changed or its factor fell.

The inconsistency here is sharper than usual, because this lane has already
charged the analogous thing. DEV-3's guard paid RULE_BITS + GUARD_BITS out of the
same budget as the facts, and DEV-3's entire result was a window computed from
that charge. A compiled table is the same kind of object -- a bit of held
structure that saves work at query time -- and X6 held it for free.

So X7 charges it. A cell records a ternary verdict, excluded / not excluded /
undetermined, and the honest price of that is 2 bits. The cells come out of the
same budget as facts and guards, and when the budget cannot hold them the arm
discards whole tables, least recently consulted first, and degrades to paying the
scan again. Nothing about the verdict changes; only what it costs to keep.

The study also sweeps the price rather than asserting one, because the number
worth having is not "does it survive at 2 bits" but "up to what storage price
does a compiled table pay for itself". That number is computable in advance for a
real system, which is the form DEV-3's window had and the form this lane should
prefer.

If the advantage does not survive at 2 bits, X6's positive was an artefact of a
free table, and this study says so in those words.
"""
from __future__ import annotations

from typing import Any, Mapping

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from prereg import Commitment, commit
from retain import FACT_BITS
from x5 import BUDGETS
from x6 import ARM_MODES

__all__ = ["X7_PLAN", "COMMITMENT", "HONEST_CELL_BITS", "CELL_BIT_PRICES"]

#: A cell records one of three verdicts, so two bits, and this lane's convention
#: elsewhere is to charge the information a structure actually carries.
HONEST_CELL_BITS: int = 2

#: Zero is the PLACEBO: at zero the arms are X6's arms and must reproduce X6
#: exactly. The rest bracket the honest price on both sides, up to a quarter of
#: what an ANSWER costs to store, which is the parent's unit.
CELL_BIT_PRICES: tuple[int, ...] = (0, 1, 2, 4, 8)

X7_PLAN: Mapping[str, Any] = {
    "study_id": "X7_PRICED_TABLE_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "audits": "results/X6_COMPILED_CONSULTATION_V1.json",
    "scientific_question": (
        "X6's compiled table is charged 1 per consultation and nothing to hold, while "
        "DEV-3's guard paid bits from the same budget as the facts. Charged consistently "
        "with DEV-3, does the large-language carry advantage survive, and up to what "
        "storage price per cell does it survive?"),
    "evidence_class": "E2",
    "contribution_level": "L2",
    "why_this_audit_and_not_another": (
        "Every correction this lane has made came from charging something previously free: "
        "rule use in DEV-2, deliberation in X1, the scan in DEV-6 -- which then refuted the "
        "fix this lane proposed for it. The compiled table is the one remaining free thing "
        "in the arm that produced this lane's strongest result."),
    "the_charge": (
        f"A cell holds a ternary verdict and costs {HONEST_CELL_BITS} bits, taken from the "
        f"same budget as facts at {FACT_BITS} bits and guards at 16. When the budget cannot "
        "hold a new cell the arm discards WHOLE TABLES, least recently consulted first, and "
        "then pays the scan again on the next consultation. Whole tables rather than single "
        "cells because per-cell replacement would need bookkeeping this study does not "
        "measure, and choosing a coarse policy and declaring it is better than charging for "
        "a policy that was never run. The current rule is never discarded for itself."),
    "prior_information_audit": {
        "PRECOMPILED_DEMAND": "holds only the cells it was asked for, so it should pay "
                              "least and lose least",
        "PRECOMPILED_EAGER": "holds every index of every compiled rule, so it should pay "
                             "most and lose most",
        "UNANIMITY_NAIVE": "holds no table and is unaffected by any price, which makes it "
                           "the invariant this sweep is read against",
        "REPLAY_ONLY_PARENT": "unaffected by any price, for the same reason",
    },
    "capability_gate": (
        "A work figure is quoted only where correctness is 1.0 in every replicate, for the "
        "arm and for the replay parent it is divided by."),
    "predictions_frozen_before_execution": {
        "V0": ("THE PLACEBO. At a price of zero the compiled arms reproduce X6's grid "
               "EXACTLY -- same winning settings, same work to the unit. If they do not, "
               "the bit machinery changed something other than the price and the study is "
               "VOID."),
        "V1": ("THE HEADLINE. At the honest price of 2 bits per cell, PRECOMPILED_DEMAND "
               "still beats replay at at least one level-3 setting under SKEWED demand, "
               "where UNANIMITY_NAIVE beats it at none. If not, X6's positive was an "
               "artefact of a free table."),
        "V2": ("The advantage is smaller when it is paid for: the count of settings "
               "PRECOMPILED_DEMAND wins at 2 bits is strictly below its count at 0 bits."),
        "V3": ("PRECOMPILED_EAGER loses MORE to the charge than PRECOMPILED_DEMAND at every "
               "non-zero price, measured as settings lost relative to that arm's own count "
               "at zero. It holds every index of a rule and the demand-driven arm holds "
               "only what was asked for, so a storage price is exactly the axis on which "
               "eager preparation should be worse -- and X6 found the two nearly "
               "indistinguishable when storage was free."),
        "V4": ("The response to the price is MONOTONE: PRECOMPILED_DEMAND's winning-setting "
               "count is non-increasing across the prices 0, 1, 2, 4, 8. A non-monotone "
               "response would mean the discard policy, not the price, is driving the "
               "result, and would have to be reported that way."),
        "V5": ("There is a highest price at which the advantage still exists, and it is "
               "below 8 bits per cell -- four cells to an answer. If the advantage survives "
               "at 8, the table is far cheaper than this lane assumed and that is to be "
               "reported as a surprise rather than banked."),
    },
    "kill_criterion": (
        "If V1 fails, X6's positive was an artefact of a free table: the carry advantage on "
        "a large language does NOT survive an accounting consistent with DEV-3's, X6 must be "
        "corrected the way DEV-5 was, and this lane's only surviving carry advantage is once "
        "again confined to languages small enough to collapse. That is to be reported in "
        "those words, with X6's receipt unchanged."),
    "sweep": {
        "rule_count": 16, "extension": 16, "d0_length": 800, "d1_length": 1000,
        "budget_bits": list(BUDGETS), "levels": [3], "skews": [0.0, 1.0], "reps": 8,
        "cell_bit_prices": list(CELL_BIT_PRICES),
    },
    "why_level_three_only": (
        "Level 3 under skewed demand is the condition X5 measured the naive rule losing at "
        "all nine budgets and X6 measured the compiled arm winning at six. It is where the "
        "two stories disagree most, so it is where a price should be applied. Level 1 is "
        "not swept, and no claim is made about it."),
    "what_this_does_not_establish": (
        "One discard policy, declared and not measured against alternatives. One cell "
        "encoding. DEV-4's synthetic worlds at one D1 length. A price at which the advantage "
        "dies HERE is not a price for any real system, and nothing here concerns routing or "
        "learned policy."),
    "novelty": (
        "NONE CLAIMED. Charging a held structure for the bits it occupies is what DEV-3 did. "
        "The contribution is applying this lane's own accounting to this lane's own newest "
        "and most convenient result."),
}

COMMITMENT: Commitment = commit(X7_PLAN)
