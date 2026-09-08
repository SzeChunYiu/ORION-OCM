"""Execute X7 and write ``results/X7_PRICED_TABLE_V1.json``."""

from __future__ import annotations

import json
import pathlib
import random
import statistics
import sys
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev2_parents as D2
import dev6_arms as A6
import x7
from dev4 import build_level_world, d1_stream, language
from retain import demand_stream
from run_x5 import _counters, _work_from_counters
from run_x6 import LANG_LEVEL, _seed as x6_seed
from x6 import ARM_MODES
from x7 import CELL_BIT_PRICES, COMMITMENT, HONEST_CELL_BITS, X7_PLAN

OUT = HERE.parent / "cognitive-ladder" / "results" / "X7_PRICED_TABLE_V1.json"
X6_RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "X6_COMPILED_CONSULTATION_V1.json"
SW = X7_PLAN["sweep"]
ARMS = tuple(ARM_MODES) + ("REPLAY_ONLY_PARENT",)
#: arms that hold no table and must therefore be identical at every price
PRICE_INVARIANT = ("UNANIMITY_NAIVE", "REPLAY_ONLY_PARENT")
COMPILED = ("PRECOMPILED_EAGER", "PRECOMPILED_DEMAND")


def one_rep(level: int, budget: int, skew: float, rep: int, price: int) -> dict[str, Any]:
    # X6's seeds exactly, so the price-zero grid is comparable to X6's receipt
    # cell by cell rather than only in distribution.
    s = x6_seed(f"x6-{level}-{budget}-{skew}", rep)
    world, _ = build_level_world(SW["rule_count"], SW["extension"], level,
                                 random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, SW["d1_length"], skew, random.Random(s ^ 0xC3))
    out: dict[str, Any] = {}
    for arm, mode in ARM_MODES.items():
        _p0, p1, _c, m = A6._run(world, d0, d1, budget, mode, LANG_LEVEL,
                                 table_cell_bits=price)
        counters = _counters(p1, m["deliberation_total"])
        looked = m["cache_hits"] + m["cache_misses"]
        out[arm] = {"work": p1.total_work(0.0), "correctness": p1.correctness(),
                    "counters": counters,
                    "work_from_counters": _work_from_counters(counters),
                    "deliberation": m["deliberation_total"],
                    "compilations": m["compilations"],
                    "compiled_cells": m["compiled_cells"],
                    "table_cells_held": m["table_cells_held"],
                    "tables_discarded": m["tables_discarded"],
                    "cells_refused": m["cells_refused"],
                    "cache_hit_rate": (m["cache_hits"] / looked) if looked else None}
    _p0, r1, _c = D2.replay_only(world, d0, d1, budget)
    counters = _counters(r1, 0)
    out["REPLAY_ONLY_PARENT"] = {
        "work": r1.total_work(0.0), "correctness": r1.correctness(), "counters": counters,
        "work_from_counters": _work_from_counters(counters), "deliberation": 0,
        "compilations": 0, "compiled_cells": 0, "table_cells_held": 0, "tables_discarded": 0, "cells_refused": 0,
        "cache_hit_rate": None}
    return out


def cell(level: int, budget: int, skew: float, price: int) -> dict[str, Any]:
    reps = [one_rep(level, budget, skew, r, price) for r in range(SW["reps"])]
    out: dict[str, Any] = {"level": level, "budget_bits": budget, "skew": skew,
                           "cell_bits": price, "reps": SW["reps"], "arms": {}}
    for arm in ARMS:
        rows = [r[arm] for r in reps]
        sound = all(r["correctness"] == 1.0 for r in rows)
        rates = [r["cache_hit_rate"] for r in rows if r["cache_hit_rate"] is not None]
        out["arms"][arm] = {
            "min_correctness": min(r["correctness"] for r in rows),
            "sound_in_every_replicate": sound,
            "work": statistics.mean(r["work"] for r in rows) if sound else None,
            "work_if_it_were_admissible": statistics.mean(r["work"] for r in rows),
            "deliberation": statistics.mean(r["deliberation"] for r in rows),
            "compilations": statistics.mean(r["compilations"] for r in rows),
            "compiled_cells": statistics.mean(r["compiled_cells"] for r in rows),
            "table_cells_held": statistics.mean(r["table_cells_held"] for r in rows),
            "tables_discarded": statistics.mean(r["tables_discarded"] for r in rows),
            "cells_refused": statistics.mean(r["cells_refused"] for r in rows),
            "cache_hit_rate": statistics.mean(rates) if rates else None,
            "counter_identity_residual": max(abs(r["work"] - r["work_from_counters"])
                                             for r in rows),
        }
    replay = out["arms"]["REPLAY_ONLY_PARENT"]
    ok = replay["sound_in_every_replicate"]
    out["ratio_to_replay"] = {
        a: (out["arms"][a]["work"] / replay["work"]
            if ok and out["arms"][a]["work"] is not None and replay["work"] else None)
        for a in ARM_MODES}
    out["beats_replay"] = {a: (v is not None and v < 1.0)
                           for a, v in out["ratio_to_replay"].items()}
    return out


def _key(c: dict) -> tuple:
    return (c["level"], c["budget_bits"], c["skew"])


def _wins(cells: list[dict], arm: str, price: int) -> set[tuple]:
    return {_key(c) for c in cells if c["cell_bits"] == price and c["beats_replay"][arm]}


def placebo_check(cells: list[dict]) -> dict[str, Any]:
    """V0: at a price of zero this must BE X6, cell for cell."""
    if not X6_RECEIPT.exists():
        return {"comparable": False, "reason": "X6 receipt absent from this checkout"}
    x6 = {(c["level"], c["budget_bits"], c["skew"]): c
          for c in json.loads(X6_RECEIPT.read_text())["primary_grid"]}
    mismatches = []
    for c in cells:
        if c["cell_bits"] != 0:
            continue
        other = x6.get(_key(c))
        if other is None:
            mismatches.append({"cell": _key(c), "why": "absent from X6"})
            continue
        for arm in ARMS:
            a = c["arms"][arm]["work_if_it_were_admissible"]
            b = other["arms"][arm]["work_if_it_were_admissible"]
            if a != b:
                mismatches.append({"cell": _key(c), "arm": arm, "x7": a, "x6": b})
    return {"comparable": True, "cells_compared": sum(1 for c in cells if c["cell_bits"] == 0),
            "mismatches": mismatches, "reproduces_x6": not mismatches}


def invariance_check(cells: list[dict]) -> dict[str, Any]:
    """Arms that hold no table must be identical at every price. If they are not,
    the bit machinery is reaching something it has no business touching."""
    by_key: dict[tuple, dict[str, set]] = {}
    for c in cells:
        seen = by_key.setdefault(_key(c), {a: set() for a in PRICE_INVARIANT})
        for arm in PRICE_INVARIANT:
            seen[arm].add(c["arms"][arm]["work_if_it_were_admissible"])
    offenders = [{"cell": k, "arm": a, "distinct_values": sorted(v)}
                 for k, d in by_key.items() for a, v in d.items() if len(v) > 1]
    return {"offenders": offenders, "holds": not offenders}


def _terminal(cells: list[dict], v: dict[str, Any], placebo: dict,
              invariance: dict) -> tuple[str, str]:
    if placebo.get("comparable") and not placebo["reproduces_x6"]:
        return ("VOID_THE_PLACEBO_DOES_NOT_REPRODUCE_X6",
                "At a price of zero the compiled arms must be X6's arms and are not. The "
                "bit machinery changed something other than the price, so no comparison "
                "across prices in this study means anything. VOID.")
    if not invariance["holds"]:
        return ("VOID_A_PRICE_MOVED_AN_ARM_THAT_HOLDS_NO_TABLE",
                "The naive rule or the replay parent changed with the price of a table "
                "neither of them holds. VOID.")
    if any(c["arms"][a]["counter_identity_residual"] != 0 for c in cells for a in c["arms"]):
        return ("COUNTER_IDENTITY_REFUTED",
                "Total work does not equal the sum of the priced events.")
    if not v["V1_survives_the_honest_price"]:
        return ("X6_WAS_AN_ARTEFACT_OF_A_FREE_TABLE",
                "At the honest price of two bits per cell the compiled arm does not beat "
                "the replay parent at any level-3 setting under skewed demand, where the "
                "naive rule beats it at none either. The carry advantage on a large "
                "language therefore does NOT survive an accounting consistent with DEV-3's, "
                "which charged a guard bits from the same budget. X6 must be corrected the "
                "way DEV-5 was, and this lane's only surviving carry advantage is once again "
                "confined to languages small enough to collapse. X6's receipt is unchanged.")
    if not v["V4_response_to_price_is_monotone"]:
        return ("SURVIVES_BUT_THE_PRICE_RESPONSE_IS_NOT_MONOTONE",
                "The advantage survives the honest price, but the count of settings won "
                "does not fall monotonically as the price rises. Something other than the "
                "price -- most likely the whole-table discard policy, which this study "
                "chose and did not measure against alternatives -- is driving part of the "
                "result, and the surviving positive must be read with that named.")
    return ("CARRY_ADVANTAGE_SURVIVES_A_PRICED_TABLE",
            "The compiled arm still beats the replay parent at level 3 under skewed demand "
            "when its table is charged bits from the same budget as the facts, on the same "
            "accounting DEV-3 used for its guard. The advantage is smaller than X6 reported, "
            "falls monotonically as the price rises, and dies at a locatable price -- which "
            "is the form this lane prefers, because it is computable before the arm is "
            "built rather than discovered after.")


def build() -> dict[str, Any]:
    cells = [cell(lvl, b, k, p) for p in SW["cell_bit_prices"] for lvl in SW["levels"]
             for b in SW["budget_bits"] for k in SW["skews"]]
    placebo = placebo_check(cells)
    invariance = invariance_check(cells)
    counts = {arm: {p: len(_wins(cells, arm, p)) for p in SW["cell_bit_prices"]}
              for arm in ARM_MODES}
    skewed = [c for c in cells if c["skew"] == 1.0]
    naive_skewed_wins = any(c["beats_replay"]["UNANIMITY_NAIVE"] for c in skewed)
    demand = counts["PRECOMPILED_DEMAND"]
    eager = counts["PRECOMPILED_EAGER"]
    surviving = [p for p in SW["cell_bit_prices"] if demand[p] > 0]

    v = {
        "V0_placebo_reproduces_x6": bool(placebo.get("reproduces_x6")),
        "V1_survives_the_honest_price": (
            not naive_skewed_wins
            and any(c["beats_replay"]["PRECOMPILED_DEMAND"] for c in skewed
                    if c["cell_bits"] == HONEST_CELL_BITS)),
        "V2_advantage_is_smaller_when_paid_for": (
            demand[HONEST_CELL_BITS] < demand[0]),
        "V3_eager_loses_more_than_demand": all(
            (eager[0] - eager[p]) > (demand[0] - demand[p])
            for p in SW["cell_bit_prices"] if p),
        "V4_response_to_price_is_monotone": all(
            demand[a] >= demand[b] for a, b in
            zip(SW["cell_bit_prices"], SW["cell_bit_prices"][1:])),
        "V5_dies_below_eight_bits_per_cell": demand[8] == 0,
    }
    terminal, reason = _terminal(cells, v, placebo, invariance)
    return {
        "study_id": "X7_PRICED_TABLE_V1",
        "authority": (
            "E2 synthetic, and an audit of X6 by this lane's own accounting. It withdraws "
            "nothing from X6, X5, X4 or anything earlier."),
        "plan": X7_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": v,
        "placebo": placebo,
        "price_invariance": invariance,
        "winning_setting_counts_by_price": counts,
        "recompilation_by_price": {
            arm: {p: statistics.mean(c["arms"][arm]["compilations"] for c in cells
                                     if c["cell_bits"] == p)
                  for p in SW["cell_bit_prices"]} for arm in ARM_MODES},
        "how_to_read_recompilation": (
            "A table discarded under budget pressure is compiled again when its rule is "
            "next consulted, and the compilation is charged again. An arm whose table "
            "almost fits can therefore churn: it evicts a neighbour to make room, is "
            "evicted in turn, and pays the full compile each time. This is a property of "
            "the whole-table discard policy this study declared and chose, not a fact "
            "about compilation in general, and the counts here are published so the "
            "difference between the two is visible rather than argued."),
        "highest_price_the_advantage_survives": max(surviving) if surviving else None,
        "settings_per_price": len(SW["budget_bits"]) * len(SW["skews"]) * len(SW["levels"]),
        "language_size": len(language(LANG_LEVEL, SW["extension"])),
        "honest_cell_bits": HONEST_CELL_BITS,
        "what_this_does_not_establish": X7_PLAN["what_this_does_not_establish"],
        "novelty": X7_PLAN["novelty"],
        "primary_grid": cells,
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    print("placebo reproduces X6:", doc["placebo"].get("reproduces_x6"),
          "| price invariance:", doc["price_invariance"]["holds"])
    print("wins by price (of", doc["settings_per_price"], "settings):",
          json.dumps(doc["winning_setting_counts_by_price"]))
    print("highest surviving price:", doc["highest_price_the_advantage_survives"])
    for c in doc["primary_grid"]:
        if c["skew"] != 1.0 or c["cell_bits"] != doc["honest_cell_bits"]:
            continue
        r = c["ratio_to_replay"]
        a = c["arms"]["PRECOMPILED_DEMAND"]
        print(f"  B={c['budget_bits']:5d} naive={r['UNANIMITY_NAIVE']} "
              f"eager={r['PRECOMPILED_EAGER']} demand={r['PRECOMPILED_DEMAND']} "
              f"cells={a['table_cells_held']:.1f} dropped={a['tables_discarded']:.1f} "
              f"refused={a['cells_refused']:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
