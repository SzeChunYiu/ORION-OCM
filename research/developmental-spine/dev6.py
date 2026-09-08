"""X2 / DEV-6: re-pricing DEV-5's consultation the way the other lane prices it.

X1 compared the same abstract mechanism in two domains and found opposite signs
on total work.  Chasing that down turns up something less comfortable than a
domain difference: the two lanes PRICE THE MECHANISM'S OWN DELIBERATION
DIFFERENTLY, and the lane that made it look free was mine.

    E6 charges ``determined`` proportionally: ``ledger.predicate_evaluations +=
    len(up) + len(down)``, so establishing "this question is already answered"
    costs in proportion to the knowledge being consulted.

    DEV-5 charged ``decide`` a FLAT ``CONSULT_COST`` per consultation, whether
    the rule tested for a singleton -- which needs to look at one thing -- or
    scanned a surviving set of up to 433 predicates for unanimity.

That is not a fair charge and it is mine, not inherited.  A flat price makes the
weaker decision rule free exactly where it does the most work, and DEV-5's
headline factor of up to 5.1 was measured under it.  This module re-prices it and
finds out what survives.

Three arms, one decision rule between them
------------------------------------------

``SINGLETON``              tests whether the survivor set has exactly one member.
                           Genuinely O(1), charged 1.
``UNANIMITY_NAIVE``        scans the survivors on every query.  Charged
                           ``len(survivors)``, which is what it costs. This is
                           DEV-5's arm with an honest bill.
``UNANIMITY_INCREMENTAL``  maintains, per (rule, index), the number of survivors
                           voting each way.  A query is then O(1) -- determined
                           exactly when one count is zero -- and the cost moves
                           to MAINTENANCE: when a survivor is eliminated, its
                           votes are withdrawn from every index, charged
                           ``extension`` per elimination.

The third arm is the engineering answer to the second, and it is here because
proposing it without charging it would repeat the mistake this module exists to
correct.  Its maintenance is bounded by ``|language| * extension`` per rule and
is paid whether or not the queries ever arrive, so it is a bet on query volume
and can lose.

What would overturn DEV-5
-------------------------

If neither unanimity arm beats ``SINGLETON`` once deliberation is charged
proportionally, then DEV-5's factor was an artifact of a flat price I chose, the
carry advantage it recovered goes back to resting on DEV-3's language gift, and
this module says so in those words.  That is registered as the outcome to look
for rather than the one to avoid.
"""

from __future__ import annotations

from typing import Any, Mapping

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from dev1 import VERIFY_COST
from dev4 import LEVELS, language
from prereg import Commitment, commit

__all__ = ["DEV6_PLAN", "COMMITMENT", "PRICING_MODES"]

PRICING_MODES = ("singleton", "unanimity_naive", "unanimity_incremental")


DEV6_PLAN: Mapping[str, Any] = {
    "study_id": "DEV6_HONEST_CONSULTATION_PRICE_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "audits": "results/DEV5_UNANIMITY_V1.json",
    "prompted_by": "results/X1_UNANIMITY_TRANSFER_V1.json",
    "scientific_question": (
        "DEV-5 charged a flat price for consulting a version space, whether the arm tested "
        "for a singleton or scanned up to 433 predicates for unanimity. E6 charges the same "
        "kind of deliberation in proportion to the knowledge consulted. Under E6's "
        "accounting standard, does DEV-5's result survive?"),
    "evidence_class": "E2",
    "contribution_level": "L1",
    "why_this_is_an_audit_of_our_own_result": (
        "The flat price was not inherited from anywhere; it was chosen in DEV-5 and it "
        "flatters the arm DEV-5 was testing. X1 exposed it by accident, because the other "
        "lane's proportional charge is what made the same mechanism lose there. A lane that "
        "noticed this and did not re-run would be keeping a number it had reason to doubt."),
    "decisive_causal_question": (
        "Pricing is the only thing that changes. Same worlds, same streams, same budgets, "
        "same languages, same decision rules. Any change in the comparison is caused by the "
        "bill or by nothing."),
    "prior_information_audit": {
        "SINGLETON": "as DEV-5; charged 1 per consultation, which is what the test costs",
        "UNANIMITY_NAIVE": "as DEV-5; charged len(survivors), which is what the scan costs",
        "UNANIMITY_INCREMENTAL": "the same information, reorganised into per-index vote "
                                 "counts; charged extension per eliminated survivor at "
                                 "maintenance time and 1 per query",
    },
    "capability_gate": (
        "All three hold the full language, so all three are sound and correctness is 1.0 by "
        "construction. Pricing cannot change that, which is why this audit is about cost "
        "alone."),
    "predictions_frozen_before_execution": {
        "P1": ("UNANIMITY_NAIVE loses most or all of DEV-5's advantage once charged what it "
               "scans. Registered in the direction that costs this lane its own result."),
        "P2": ("UNANIMITY_INCREMENTAL keeps a real advantage over SINGLETON, because its "
               "per-query cost is O(1) and its maintenance is bounded by the language size "
               "rather than by the query count."),
        "P3": ("UNANIMITY_INCREMENTAL loses to SINGLETON at SHORT D1 lengths, where the "
               "maintenance is paid and the queries never arrive to amortize it. If it wins "
               "everywhere the maintenance is not being charged properly."),
        "P4": ("Correctness stays 1.0 for all three at every setting; a pricing change that "
               "moves correctness is a bug."),
        "P5": ("Total deliberation charged to UNANIMITY_NAIVE exceeds that charged to "
               "UNANIMITY_INCREMENTAL at every setting where D1 is long, which is the "
               "arithmetic reason the incremental arm exists."),
    },
    "kill_criterion": (
        "If neither unanimity arm beats SINGLETON under proportional pricing, DEV-5's "
        "factor was an artifact of a flat price this lane chose, and the carry advantage it "
        "recovered goes back to resting on the language gift DEV-4 showed was binding. That "
        "is to be reported in those words and DEV-5's receipt annotated accordingly."),
    "sweep": {
        "rule_count": 16,
        "extension": 16,
        "d0_length": 800,
        "d1_lengths": [100, 400, 1000, 4000],
        "budget_bits": [1024, 1536],
        "levels": list(LEVELS),
        "skews": [1.0],
        "reps": 8,
    },
    "language_size_at_top_level": "computed in the receipt",
    "costs": {"verify": VERIFY_COST,
              "singleton_consultation": 1,
              "naive_unanimity_consultation": "len(survivors)",
              "incremental_query": 1,
              "incremental_maintenance": "extension per eliminated survivor"},
    "what_this_does_not_establish": (
        "Two pricing schemes, both declared. There is no fact of the matter about what a "
        "version-space consultation 'really' costs outside an implementation, and a lane "
        "that wanted a particular answer could get it by choosing a scheme. What can be "
        "defended is that the charge should scale with the work the operation does, that "
        "E6's does and DEV-5's did not, and that the arm proposed to fix it is charged for "
        "the bookkeeping it adds."),
    "novelty": (
        "NONE CLAIMED. Maintaining per-element vote counts under set elimination is "
        "ordinary incremental bookkeeping. The contribution is re-pricing a result of ours "
        "against another lane's accounting standard and reporting what changed."),
}

COMMITMENT: Commitment = commit(DEV6_PLAN)
