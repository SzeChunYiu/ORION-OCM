"""X3: the carry advantage without an exchange rate.

Every comparison in this lane so far has been a comparison of TOTAL WORK, and
total work is a weighted sum whose weights I chose.  DEV-6 showed how much that
matters: changing one weight moved the headline from 5.1x to 3.4x and turned the
weakest cell into a near-tie.  It also showed there is no fact of the matter
about the right weights, only better and worse arguments for them.

So the objection that survives DEV-6 is not "your prices are wrong", it is "your
result depends on prices at all".  This module removes that dependence.

Two ways to state a result without prices
-----------------------------------------

**Dominance.**  If arm A uses no more of every counted resource than arm B, and
strictly less of at least one, then A is cheaper under EVERY positive price
vector.  No exchange rate is needed and none can be argued with.  This is the
strongest form a result of this kind can take and it is usually unavailable,
because arms trade resources rather than strictly dominating.

**The price condition.**  When there is no dominance, the comparison is a
half-space: with ``d_c`` the difference in the count of resource ``c``, arm A
wins exactly when ``sum_c p_c d_c < 0``.  That is not a weaker claim than a
total, it is a COMPLETE one -- the reader supplies prices and reads off the
answer -- and for the two comparisons this lane cares about it collapses to a
single critical ratio each:

    unanimity against singleton   wins iff  p_verify  >  a threshold set by the other counts
    lineage against replay        wins iff  p_derive  >  a threshold set by the other counts

Each threshold is an ABSOLUTE price for one operation with the others held at this
lane's values -- not a ratio between two prices, which an earlier draft of this
module's own docstring said and which would have been a different and wrong
claim.

Reporting the ratio rather than the total is strictly more informative, and it
makes the arbitrary part of DEV-6 visible: my chosen prices are one point on an
axis, and the receipt says where that point sits relative to the boundary.

What this cannot do
-------------------

It cannot make the counts themselves neutral.  Which operations exist, and which
of them are counted at all, is a modelling choice as consequential as the prices,
and it is the same choice in every arm here because they share a harness.  A
harness that failed to count something the lineage does would hide it just as
effectively as a price of zero, and no amount of price-free reporting would
reveal that.  What price-free reporting buys is immunity to one specific
objection, not to the general one.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

import dev2_parents as D2
import dev6_arms as A6
from dev1 import COMPOSE_COST, VERIFY_COST
from dev4 import LEVELS, build_level_world, d1_stream
from prereg import Commitment, commit
from retain import APPLY_COST, DERIVE_COST, INDUCE_COST, LOOKUP_COST, demand_stream

__all__ = ["X3_PLAN", "COMMITMENT", "COUNTS", "counts_for", "dominance",
           "critical_ratio", "CHOSEN_PRICES"]


#: The resources this harness counts. Compositions are charged identically to
#: every arm and cancel in every difference, so they are listed and then ignored.
COUNTS = ("derivations", "applications", "lookups", "verifications", "inductions",
          "consultations", "maintenance", "compositions")

#: The prices used everywhere else in this lane, recorded here as ONE POINT on an
#: axis rather than as the accounting.
CHOSEN_PRICES: Mapping[str, float] = {
    "derivations": DERIVE_COST, "applications": APPLY_COST, "lookups": LOOKUP_COST,
    "verifications": VERIFY_COST, "inductions": INDUCE_COST, "consultations": 1.0,
    "maintenance": 1.0, "compositions": COMPOSE_COST,
}


def counts_for(phase, meters: Mapping[str, int]) -> dict[str, float]:
    """Raw resource counts, with the three things ``lookup_work`` conflates split.

    ``dev6_arms`` charges consultations and maintenance into ``lookup_work``
    alongside real lookups, which is fine for a total and useless for a
    price-free comparison. The meters carry the two charges separately, so the
    real lookup count is recoverable exactly rather than estimated.
    """
    consult = meters.get("consultation_charge", 0)
    maintain = meters.get("maintenance", 0)
    raw_lookup_work = phase.lookup_work - consult - maintain
    return {
        "derivations": phase.derivations,
        "applications": phase.applications,
        "lookups": raw_lookup_work / LOOKUP_COST,
        "verifications": phase.verifications,
        "inductions": phase.inductions,
        "consultations": consult,
        "maintenance": maintain,
        "compositions": phase.served,
    }


def dominance(a: Mapping[str, float], b: Mapping[str, float]) -> str:
    """Does one count vector dominate the other under every positive price?"""
    diffs = {c: a[c] - b[c] for c in COUNTS}
    if all(v <= 0 for v in diffs.values()) and any(v < 0 for v in diffs.values()):
        return "A_DOMINATES"
    if all(v >= 0 for v in diffs.values()) and any(v > 0 for v in diffs.values()):
        return "B_DOMINATES"
    return "NEITHER"


def critical_ratio(a: Mapping[str, float], b: Mapping[str, float],
                   numerator: str, denominator: str,
                   fixed: Mapping[str, float]) -> dict[str, Any]:
    """Where A and B tie as the price of ``numerator`` varies, if they tie at all.

    Every other resource is held at ``fixed``. The interesting case is that there
    is NO positive tie, which the first version of this function reported as a
    bare ``None`` and which is not a missing value: it means one arm wins at
    EVERY positive price of that resource, which is the strongest statement
    available short of full dominance. The verification-price comparison turns
    out to be exactly that case, so returning ``None`` there would have thrown
    away the result rather than reporting it.
    """
    d = {c: a[c] - b[c] for c in COUNTS}
    rest = sum(fixed[c] * d[c] for c in COUNTS if c not in (numerator, denominator))
    dn, dd = d[numerator], d[denominator]
    base = dd * fixed[denominator] + rest
    if dn == 0:
        return {"boundary": None,
                "always": "A" if base < 0 else ("B" if base > 0 else None),
                "reason": f"the two arms use the same number of {numerator}, so its price "
                          "cannot change the comparison"}
    boundary = -base / dn
    if boundary > 0:
        return {"boundary": boundary, "always": None,
                "wins_above": "A" if dn < 0 else "B",
                "units": "absolute price of one " + numerator + ", with every other price "
                         "held at this lane's values",
                "reason": f"A wins when one {numerator} costs "
                          f"{'more' if dn < 0 else 'less'} than {boundary:.3f}, with every "
                          "other price held at this lane's values"}
    # no positive tie: the sign of the objective never changes for p > 0
    at_one = base + dn
    return {"boundary": None,
            "always": "A" if at_one < 0 else "B",
            "reason": f"there is no positive price of {numerator} at which the two tie, so "
                      f"{'A' if at_one < 0 else 'B'} wins at EVERY positive price of it -- "
                      "the other coordinates already decide the comparison"}


X3_PLAN: Mapping[str, Any] = {
    "study_id": "X3_PRICE_FREE_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "audits": "results/DEV5_UNANIMITY_V1.json, results/DEV6_HONEST_CONSULTATION_PRICE_V1.json",
    "scientific_question": (
        "The carry advantage has been reported as a ratio of total work, and total work is a "
        "weighted sum whose weights this lane chose. DEV-6 showed one weight moving the "
        "headline from 5.1x to 3.4x. Does the ordering survive WITHOUT any weights -- by "
        "dominance -- and if not, at exactly which prices does it hold?"),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "method": (
        "Report raw counts per resource. Test pairwise dominance, which is price-free by "
        "construction. Where no arm dominates, report the exact price condition as a "
        "critical ratio, and state where this lane's chosen prices sit relative to it."),
    "predictions_frozen_before_execution": {
        "Y1": ("No arm DOMINATES: the lineage trades derivations for applications and "
               "verifications, and unanimity trades verifications for consultations. If "
               "something dominates, the result is stronger than anything claimed so far "
               "and should be said so."),
        "Y2": ("The unanimity-against-singleton comparison collapses to one critical ratio "
               "of verification price to consultation price, and this lane's chosen prices "
               "sit on the winning side of it with room to spare."),
        "Y3": ("The lineage-against-replay comparison collapses to a critical ratio of "
               "derivation price to application price, and this lane's chosen prices sit on "
               "the winning side but by LESS room, because that comparison is the one DEV-6 "
               "brought near a tie."),
        "Y4": ("Reporting the ratio changes no ordering: at the chosen prices every sign "
               "matches the totals already published. A disagreement means one of the "
               "receipts is arithmetically wrong."),
    },
    "kill_criterion": (
        "If this lane's chosen prices sit CLOSE to a boundary on the lineage-against-replay "
        "comparison -- within a factor of two of the tie -- then the carry advantage is a "
        "claim about a price regime rather than about a mechanism, and it must be stated "
        "that way wherever it is quoted."),
    "sweep": {
        "rule_count": 16, "extension": 16, "d0_length": 800,
        "d1_lengths": [1000, 4000], "budget_bits": [1536],
        "levels": list(LEVELS), "skew": 1.0, "reps": 8,
    },
    "what_this_does_not_establish": (
        "Immunity to price objections is not immunity to modelling objections. Which "
        "operations exist and which are counted is a choice as consequential as the prices, "
        "and it is shared by every arm because they share a harness. A harness that failed "
        "to count something the lineage does would hide it exactly as a price of zero "
        "would, and no price-free reporting would reveal it."),
    "novelty": (
        "NONE CLAIMED. Pareto dominance and half-space characterisations of weighted-sum "
        "comparisons are elementary. The contribution is applying them to this lane's own "
        "headline after discovering that it moved when a weight did."),
}

COMMITMENT: Commitment = commit(X3_PLAN)


#: Recorded AFTER execution and deliberately OUTSIDE X3_PLAN, so the commitment
#: digest above is unchanged and this receipt is not retroactively edited.
#:
#: X3's counts are correct. Its READING was too broad. Every arm it compared held
#: the full 433-predicate language, inherited from DEV-6, and DEV-6 had run the
#: singleton rule over that language rather than over the small one DEV-3 used. A
#: version space that large rarely collapses, so the rule rarely fires, and the
#: resulting loss to replay is a statement about language SIZE and not about
#: whether a guard pays. X4_FINAL_ACCOUNTING_V1 ran both languages under one
#: charge rule and found the small-language arm beats replay at four of eight
#: level-1 settings at correctness 1.0. Nothing here is withdrawn from X3.
READING_CORRECTED_BY: str = "X4_FINAL_ACCOUNTING_V1"
READING_CORRECTION: str = (
    "X3 concluded the carry advantage against replay mostly fails the honest price. "
    "That holds for the LARGE-language arms it measured and does not generalise to the "
    "small-language guarded arm DEV-3 actually used, which X4 measured directly.")
