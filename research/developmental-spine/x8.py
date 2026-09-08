"""X8: find the price at which a compiled verdict stops being worth its bits.

X7 charged X6's compiled table 2 bits a cell and the carry advantage survived.
It swept 0, 1, 2, 4 and 8 bits and reported the advantage still alive at 8 --
which is the top of that sweep, so the number is a LOWER BOUND on the break-even
price and not the break-even price. X7 predicted the advantage would die below 8
and it did not.

That refutation is worth more than the prediction would have been, because 8 bits
is exactly what this lane charges to store one ANSWER. A compiled verdict costing
as much as a cached answer, and still beating a parent that does nothing but
cache answers, says the two are not comparable objects: a cell decides an index
for a rule and licenses an application at 10 where the parent derives at 100,
and it does that every time the index is demanded, while a cached answer serves
only itself.

So the question X7 could not answer is the one worth answering. Where does it
actually end? This study continues the same sweep upward -- 8, 16, 32, 64, 128
bits a cell, up to sixteen answers' worth of storage for one verdict -- on the
same worlds, the same arms, the same budgets and the same seeds, and overlaps X7
at 8 so that the continuation is verifiable rather than asserted.

It also asks what happens at the end, which X7 did not. An arm that cannot afford
its table should fall back to paying the scan and end up doing what the rule it
compiles does. If instead it ends up doing MORE work than the naive rule, the
compiled arm has a pathology that its cheap regime was hiding, and that is worth
finding before anything is built on it.
"""
from __future__ import annotations

from typing import Any, Mapping

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "cognitive-ladder"))

from prereg import Commitment, commit
from retain import FACT_BITS
from x5 import BUDGETS

__all__ = ["X8_PLAN", "COMMITMENT", "CELL_BIT_PRICES", "OVERLAP_PRICE"]

#: The price X7 also ran. X8 must reproduce X7 there, cell for cell.
OVERLAP_PRICE: int = 8

#: Up to sixteen answers' worth of storage for a single compiled verdict.
CELL_BIT_PRICES: tuple[int, ...] = (8, 16, 32, 64, 128)

X8_PLAN: Mapping[str, Any] = {
    "study_id": "X8_TABLE_BREAK_EVEN_V1",
    "programme": "SzeChunYiu/ORION-OCM#151",
    "doctrine": "PR #150 PARENT_SYNTHESIS_DOCTRINE_V0_2.md",
    "continues": "results/X7_PRICED_TABLE_V1.json",
    "scientific_question": (
        "X7's sweep ended while the advantage was still alive, so its highest surviving "
        f"price of {OVERLAP_PRICE} bits a cell is a lower bound and not a boundary. At what "
        "storage price does a compiled verdict stop paying for itself, and does the arm "
        "degrade to the rule it compiles or to something worse?"),
    "evidence_class": "E2",
    "contribution_level": "L2",
    "what_x7_established_and_did_not": (
        "Established: the advantage survives an accounting consistent with DEV-3's, falls "
        "monotonically with the price, and the eager arm collapses under a storage price "
        "while the demand-driven one does not. Not established: where it ends. X7's V5 "
        f"predicted death below {OVERLAP_PRICE} bits and was refuted, which is why this "
        "study exists rather than a restatement of that number."),
    "why_the_refutation_matters": (
        f"{OVERLAP_PRICE} bits is exactly FACT_BITS, what this lane charges to store one "
        "answer. A verdict that costs as much as an answer and still beats a parent made "
        "entirely of answers means the two are not the same kind of object. A cell decides "
        "an index for a whole rule and licenses an application at APPLY_COST where the "
        "parent pays DERIVE_COST, and it does so on every demand for that index; a stored "
        "answer serves only itself."),
    "prior_information_audit": {
        "known": "X7's grid at prices 0, 1, 2, 4 and 8, including that PRECOMPILED_DEMAND "
                 "wins 8 of 18 settings at 8 bits and that UNANIMITY_NAIVE wins 6 at every "
                 "price. The overlap at 8 is therefore a CONTROL and not a prediction.",
        "not_known": "anything at 16, 32, 64 or 128 bits a cell, where the boundary is, or "
                     "what the arm does once it can hold almost nothing.",
    },
    "capability_gate": (
        "A work figure is quoted only where correctness is 1.0 in every replicate, for the "
        "arm and for the replay parent it is divided by."),
    "predictions_frozen_before_execution": {
        "U0": (f"THE OVERLAP CONTROL. At {OVERLAP_PRICE} bits X8 reproduces X7's grid cell "
               "for cell, because it is the same code on the same seeds. If it does not, "
               "the continuation is not a continuation and the study is VOID."),
        "U1": ("There is a price in this sweep at which PRECOMPILED_DEMAND beats replay at "
               "ZERO settings. If there is not, a compiled verdict is worth holding at "
               "sixteen answers' worth of storage, which this lane would not have believed "
               "and must report as a surprise rather than bank."),
        "U2": ("The response stays monotone: PRECOMPILED_DEMAND's winning-setting count is "
               "non-increasing across 8, 16, 32, 64 and 128."),
        "U3": (f"The break-even price is above {2 * FACT_BITS} bits a cell -- twice what an "
               "answer costs. X7 already showed survival at one answer's worth, so the "
               "cheap end of this claim is known; two answers' worth is not."),
        "U4": ("GRACEFUL DEGRADATION. At the highest price, where the arm can hold almost "
               "nothing, PRECOMPILED_DEMAND's work is within 5 percent of UNANIMITY_NAIVE's "
               "at every budget: unable to keep a table, it pays the scan and does what the "
               "rule it compiles does. If it does MORE work than the naive rule, the "
               "compiled arm carries a pathology its cheap regime was hiding, and that is "
               "to be reported as a defect rather than a footnote."),
        "U5": ("The mechanism at the top of the sweep is REFUSAL, not churn: cells_refused "
               "rises with the price while tables_discarded falls, because a table that "
               "cannot be afforded is never built and so is never discarded."),
    },
    "kill_criterion": (
        "There is no kill criterion for the carry advantage here, because X7 already "
        "established it at the honest price and this study cannot withdraw that. What can "
        "fail is the CHARACTERISATION: if U1 fails there is no boundary in this range, and "
        "if U4 fails the compiled arm is worse than the rule it compiles once storage is "
        "scarce. Either is reported as the result rather than as a caveat on a positive."),
    "sweep": {
        "rule_count": 16, "extension": 16, "d0_length": 800, "d1_length": 1000,
        "budget_bits": list(BUDGETS), "levels": [3], "skews": [0.0, 1.0], "reps": 8,
        "cell_bit_prices": list(CELL_BIT_PRICES),
    },
    "what_this_does_not_establish": (
        "The same single discard policy X7 declared and did not measure against "
        "alternatives, the same cell encoding, the same synthetic worlds at one D1 length. "
        "A break-even price located here is a price in THESE worlds under THIS policy. It "
        "is reported because it is the shape a real system could compute in advance, not "
        "because it transfers."),
    "novelty": (
        "NONE CLAIMED. Continuing a sweep past the point where it stopped is not a "
        "contribution; the contribution is refusing to report a censored bound as a "
        "boundary."),
}

COMMITMENT: Commitment = commit(X8_PLAN)
