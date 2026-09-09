"""Execute X8 and write ``results/X8_TABLE_BREAK_EVEN_V1.json``.

The grid is built by ``run_x7.cell`` unchanged. That is deliberate: the overlap
control at 8 bits is only worth anything if the two studies run the same code on
the same seeds, and importing the function is the strongest way to say so.
"""

from __future__ import annotations

import json
import pathlib
import statistics
import sys
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import x8
from dev4 import language
from run_x6 import LANG_LEVEL
from run_x7 import ARMS, _key, _wins, cell, invariance_check
from x6 import ARM_MODES
from x8 import CELL_BIT_PRICES, COMMITMENT, OVERLAP_PRICE, X8_PLAN

OUT = HERE.parent / "cognitive-ladder" / "results" / "X8_TABLE_BREAK_EVEN_V1.json"
X7_RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X7_PRICED_TABLE_V1.json"
SW = X8_PLAN["sweep"]
ARM = "PRECOMPILED_DEMAND"
NAIVE = "UNANIMITY_NAIVE"


def overlap_check(cells: list[dict]) -> dict[str, Any]:
    """U0: at the overlap price this must BE X7, cell for cell."""
    if not X7_RECEIPT.exists():
        return {"comparable": False, "reason": "X7 receipt absent from this checkout"}
    x7 = {(c["level"], c["budget_bits"], c["skew"]): c
          for c in json.loads(X7_RECEIPT.read_text())["primary_grid"]
          if c["cell_bits"] == OVERLAP_PRICE}
    mismatches = []
    for c in cells:
        if c["cell_bits"] != OVERLAP_PRICE:
            continue
        other = x7.get(_key(c))
        if other is None:
            mismatches.append({"cell": _key(c), "why": "absent from X7"})
            continue
        for arm in ARMS:
            a = c["arms"][arm]["work_if_it_were_admissible"]
            b = other["arms"][arm]["work_if_it_were_admissible"]
            if a != b:
                mismatches.append({"cell": _key(c), "arm": arm, "x8": a, "x7": b})
    return {"comparable": True,
            "cells_compared": sum(1 for c in cells if c["cell_bits"] == OVERLAP_PRICE),
            "mismatches": mismatches, "reproduces_x7": not mismatches}


def degradation(cells: list[dict], price: int) -> dict[str, Any]:
    """U4: at the top price, does the arm do what the rule it compiles does?"""
    rows = []
    for c in cells:
        if c["cell_bits"] != price:
            continue
        arm = c["arms"][ARM]["work_if_it_were_admissible"]
        naive = c["arms"][NAIVE]["work_if_it_were_admissible"]
        rows.append({"budget_bits": c["budget_bits"], "skew": c["skew"],
                     "compiled": arm, "naive": naive,
                     "ratio": arm / naive if naive else None,
                     "within_five_percent": bool(naive and abs(arm - naive) / naive <= 0.05),
                     "worse_than_the_rule_it_compiles": bool(naive and arm > naive * 1.05)})
    return {"price": price, "rows": rows,
            "all_within_five_percent": all(r["within_five_percent"] for r in rows),
            "any_worse_than_naive": any(r["worse_than_the_rule_it_compiles"] for r in rows)}


def _terminal(v: dict[str, Any], overlap: dict, invariance: dict,
              break_even: int | None, degrade: dict) -> tuple[str, str]:
    if overlap.get("comparable") and not overlap["reproduces_x7"]:
        return ("VOID_THE_OVERLAP_DOES_NOT_REPRODUCE_X7",
                f"At {OVERLAP_PRICE} bits a cell X8 must be X7, because it is the same code "
                "on the same seeds. It is not, so this is not a continuation of that sweep "
                "and nothing in it can be read against X7. VOID.")
    if not invariance["holds"]:
        return ("VOID_A_PRICE_MOVED_AN_ARM_THAT_HOLDS_NO_TABLE",
                "The naive rule or the replay parent changed with the price of a table "
                "neither of them holds. VOID.")
    if degrade["any_worse_than_naive"]:
        return ("COMPILED_ARM_IS_WORSE_THAN_THE_RULE_IT_COMPILES_WHEN_STORAGE_IS_SCARCE",
                "At the top of the sweep the compiled arm does MORE work than the naive "
                "rule it is supposed to degrade into. Unable to keep a table it should pay "
                "the scan and match the rule; instead it pays the scan AND something else. "
                "That is a defect the cheap regime was hiding, it is reported as the result "
                "of this study, and any use of the compiled arm under storage pressure has "
                "to answer it first. X7's positive at two bits is unaffected and unwithdrawn.")
    if break_even is None:
        return ("NO_BREAK_EVEN_FOUND_BELOW_SIXTEEN_ANSWERS_PER_CELL",
                "The compiled arm still beats the replay parent at 128 bits a cell -- "
                "sixteen answers' worth of storage for one verdict. This lane did not "
                "believe that and registered the opposite. It is reported as a surprise "
                "rather than banked: what it means is that a verdict and a stored answer "
                "are not comparable units, and a study that says why is owed before the "
                "number is used for anything.")
    return ("BREAK_EVEN_LOCATED",
            f"The compiled arm stops beating the replay parent at {break_even} bits a cell, "
            f"which is {break_even // 8} answers' worth of storage for one verdict, and it "
            "degrades into the rule it compiles rather than into something worse. The "
            "advantage X6 found and X7 priced therefore has a located upper edge in "
            "storage, alongside the budget window X5 located and the soundness precondition "
            "DEV-4 proved. All three are computable before an arm is built.")


def build() -> dict[str, Any]:
    cells = [cell(lvl, b, k, p) for p in SW["cell_bit_prices"] for lvl in SW["levels"]
             for b in SW["budget_bits"] for k in SW["skews"]]
    overlap = overlap_check(cells)
    invariance = invariance_check(cells)
    counts = {arm: {p: len(_wins(cells, arm, p)) for p in SW["cell_bit_prices"]}
              for arm in ARM_MODES}
    demand = counts[ARM]
    dead = [p for p in SW["cell_bit_prices"] if demand[p] == 0]
    break_even = min(dead) if dead else None
    top = max(SW["cell_bit_prices"])
    degrade = degradation(cells, top)

    v = {
        "U0_overlap_reproduces_x7": bool(overlap.get("reproduces_x7")),
        "U1_a_price_kills_the_advantage": break_even is not None,
        "U2_response_stays_monotone": all(
            demand[a] >= demand[b] for a, b in
            zip(SW["cell_bit_prices"], SW["cell_bit_prices"][1:])),
        "U3_break_even_is_above_two_answers": (
            break_even is None or break_even > 16),
        "U4_degrades_into_the_rule_it_compiles": degrade["all_within_five_percent"],
        "U5_the_end_is_refusal_not_churn": all(
            statistics.mean(c["arms"][ARM]["cells_refused"] for c in cells
                            if c["cell_bits"] == top)
            >= statistics.mean(c["arms"][ARM]["cells_refused"] for c in cells
                               if c["cell_bits"] == p)
            and statistics.mean(c["arms"][ARM]["tables_discarded"] for c in cells
                                if c["cell_bits"] == top)
            <= statistics.mean(c["arms"][ARM]["tables_discarded"] for c in cells
                               if c["cell_bits"] == p)
            for p in SW["cell_bit_prices"] if p != top),
    }
    terminal, reason = _terminal(v, overlap, invariance, break_even, degrade)
    return {
        "study_id": "X8_TABLE_BREAK_EVEN_V1",
        "authority": (
            "E2 synthetic. It continues X7's sweep and withdraws nothing from X7, X6 or "
            "anything earlier. It exists because X7's highest surviving price was the top "
            "of X7's sweep, which is a bound and not a boundary."),
        "plan": X8_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": v,
        "overlap_control": overlap,
        "price_invariance": invariance,
        "winning_setting_counts_by_price": counts,
        "break_even_cell_bits": break_even,
        "break_even_in_answers": (break_even / 8) if break_even else None,
        "x7_reported_bound": OVERLAP_PRICE,
        "what_x7s_number_was": (
            f"X7 reported the advantage alive at {OVERLAP_PRICE} bits, which was the top of "
            "its sweep. That is a lower bound on the break-even price. It is corrected here "
            "by continuing the sweep, not by reinterpreting X7's number."),
        "degradation_at_the_top_price": degrade,
        "mechanism_by_price": {
            str(p): {
                "cells_held": statistics.mean(c["arms"][ARM]["table_cells_held"]
                                              for c in cells if c["cell_bits"] == p),
                "tables_discarded": statistics.mean(c["arms"][ARM]["tables_discarded"]
                                                    for c in cells if c["cell_bits"] == p),
                "cells_refused": statistics.mean(c["arms"][ARM]["cells_refused"]
                                                 for c in cells if c["cell_bits"] == p),
                "deliberation": statistics.mean(c["arms"][ARM]["deliberation"]
                                                for c in cells if c["cell_bits"] == p),
            } for p in SW["cell_bit_prices"]},
        "language_size": len(language(LANG_LEVEL, SW["extension"])),
        "settings_per_price": len(SW["budget_bits"]) * len(SW["skews"]) * len(SW["levels"]),
        "what_this_does_not_establish": X8_PLAN["what_this_does_not_establish"],
        "novelty": X8_PLAN["novelty"],
        "primary_grid": cells,
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    print("overlap reproduces X7:", doc["overlap_control"].get("reproduces_x7"),
          "| invariance:", doc["price_invariance"]["holds"])
    print("wins by price (of", doc["settings_per_price"], "):",
          json.dumps(doc["winning_setting_counts_by_price"]))
    print("break-even:", doc["break_even_cell_bits"], "bits =",
          doc["break_even_in_answers"], "answers")
    print("mechanism:", json.dumps(doc["mechanism_by_price"]))
    for r in doc["degradation_at_the_top_price"]["rows"]:
        print(f"  top-price B={r['budget_bits']:5d} k={r['skew']} "
              f"compiled/naive={r['ratio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
