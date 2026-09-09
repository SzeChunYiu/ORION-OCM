"""Execute X6 and write ``results/X6_COMPILED_CONSULTATION_V1.json``."""

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
import x6
from dev4 import build_level_world, d1_stream, language
from retain import demand_stream
from run_x5 import _counters, _work_from_counters
from x6 import ARM_MODES, COMMITMENT, X6_PLAN

OUT = HERE.parent / "cognitive-ladder" / "results" / "X6_COMPILED_CONSULTATION_V1.json"
SW = X6_PLAN["sweep"]
ARMS = tuple(ARM_MODES) + ("REPLAY_ONLY_PARENT",)
#: every arm holds the full ladder, so the language is not an axis here
LANG_LEVEL = 3
#: the counters that compilation is FORBIDDEN to change (W2)
BEHAVIOURAL = ("derivations", "applications", "lookups", "inductions", "verifications",
               "compositions")


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(level: int, budget: int, skew: float, rep: int) -> dict[str, Any]:
    s = _seed(f"x6-{level}-{budget}-{skew}", rep)
    world, _ = build_level_world(SW["rule_count"], SW["extension"], level,
                                 random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, SW["d1_length"], skew, random.Random(s ^ 0xC3))
    out: dict[str, Any] = {}
    for arm, mode in ARM_MODES.items():
        _p0, p1, _c, m = A6._run(world, d0, d1, budget, mode, LANG_LEVEL)
        counters = _counters(p1, m["deliberation_total"])
        looked = m["cache_hits"] + m["cache_misses"]
        out[arm] = {"work": p1.total_work(0.0), "correctness": p1.correctness(),
                    "counters": counters,
                    "work_from_counters": _work_from_counters(counters),
                    "deliberation": m["deliberation_total"],
                    "consultations": m["consultations"],
                    "compilations": m["compilations"],
                    "compiled_cells": m["compiled_cells"],
                    "cache_hits": m["cache_hits"],
                    "cache_hit_rate": (m["cache_hits"] / looked) if looked else None}
    _p0, r1, _c = D2.replay_only(world, d0, d1, budget)
    counters = _counters(r1, 0)
    out["REPLAY_ONLY_PARENT"] = {
        "work": r1.total_work(0.0), "correctness": r1.correctness(), "counters": counters,
        "work_from_counters": _work_from_counters(counters), "deliberation": 0,
        "consultations": 0, "compilations": 0, "compiled_cells": 0, "cache_hits": 0,
        "cache_hit_rate": None}
    return out


def cell(level: int, budget: int, skew: float) -> dict[str, Any]:
    reps = [one_rep(level, budget, skew, r) for r in range(SW["reps"])]
    out: dict[str, Any] = {"level": level, "budget_bits": budget, "skew": skew,
                           "reps": SW["reps"], "arms": {}}
    for arm in ARMS:
        rows = [r[arm] for r in reps]
        sound = all(r["correctness"] == 1.0 for r in rows)
        rates = [r["cache_hit_rate"] for r in rows if r["cache_hit_rate"] is not None]
        out["arms"][arm] = {
            "min_correctness": min(r["correctness"] for r in rows),
            "sound_in_every_replicate": sound,
            "work": statistics.mean(r["work"] for r in rows) if sound else None,
            "work_if_it_were_admissible": statistics.mean(r["work"] for r in rows),
            "counters": {k: statistics.mean(r["counters"][k] for r in rows)
                         for k in rows[0]["counters"]},
            "deliberation": statistics.mean(r["deliberation"] for r in rows),
            "consultations": statistics.mean(r["consultations"] for r in rows),
            "compilations": statistics.mean(r["compilations"] for r in rows),
            "compiled_cells": statistics.mean(r["compiled_cells"] for r in rows),
            "cache_hit_rate": statistics.mean(rates) if rates else None,
            "counter_identity_residual": max(abs(r["work"] - r["work_from_counters"])
                                             for r in rows),
        }
    # W2: the control, checked per replicate rather than on the means, because two
    # different behaviours can average to the same number.
    control = []
    for r in reps:
        naive, comp = r["UNANIMITY_NAIVE"], r["PRECOMPILED_DEMAND"]
        diffs = {k: (naive["counters"][k], comp["counters"][k])
                 for k in BEHAVIOURAL if naive["counters"][k] != comp["counters"][k]}
        if naive["correctness"] != comp["correctness"]:
            diffs["correctness"] = (naive["correctness"], comp["correctness"])
        control.append(diffs)
    out["control_disagreements"] = [d for d in control if d]
    out["compilation_changed_only_cost"] = not out["control_disagreements"]

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


def _terminal(cells: list[dict], w: dict[str, Any]) -> tuple[str, str]:
    if not w["W2_compilation_changed_only_cost"]:
        return ("VOID_THE_COMPILED_ARM_IS_A_DIFFERENT_DECISION_RULE",
                "PRECOMPILED_DEMAND and UNANIMITY_NAIVE disagree on a counter that "
                "compilation is not permitted to touch. The compiled arm is therefore not "
                "the same rule consulted more cheaply, and every comparison in this study "
                "is between two different rules rather than two prices. VOID.")
    if any(c["arms"][a]["counter_identity_residual"] != 0 for c in cells for a in c["arms"]):
        return ("COUNTER_IDENTITY_REFUTED",
                "Total work does not equal the sum of the priced events, so no margin here "
                "has an account of what produced it.")
    if not w["W5_compiled_wins_where_naive_never_did"]:
        return ("LANGUAGE_PRECONDITION_IS_NOT_REMOVABLE_BY_PRICING",
                "Making a consultation cost 1 over a 433-predicate language does not beat "
                "the replay parent at any budget under skewed demand, where the naive rule "
                "also beats it at none. So an O(1) consultation does NOT free the carry "
                "advantage from the language it is drawn from: DEV-4's precondition is not "
                "removable by pricing, the size story survives its sharpest test, and every "
                "carry advantage this lane has is confined to languages small enough to "
                "collapse. X4's and X5's receipts are unchanged.")
    if not w["W3_compiled_regime_is_a_strict_superset"]:
        return ("COMPILED_CONSULTATION_MOVES_THE_REGIME_RATHER_THAN_WIDENING_IT",
                "The compiled arm wins where the naive one does not AND loses where the "
                "naive one wins. Nothing but the price of a consultation differs between "
                "them, so a moved rather than widened regime is not explained by this "
                "study's own account of what it changed, and must be diagnosed before the "
                "positive is read as one.")
    return ("CARRY_ADVANTAGE_SURVIVES_ON_A_LARGE_LANGUAGE_WHEN_CONSULTATION_IS_CHEAP",
            "On the full 433-predicate language, with the version space unchanged and only "
            "the price of consulting it changed, the compiled arm beats the replay parent "
            "at settings where the same rule at the scanning price beats it at none -- "
            "including under skewed demand at level 3, where X5 measured the naive rule "
            "losing at all nine budgets. Every carry advantage this lane had previously "
            "shown required a language small enough to collapse. This one does not. The "
            "operative quantity is the COST OF A CONSULTATION and not the SIZE of the space "
            "consulted, which is what DEV-6, X5 and the independent review of PR #150 each "
            "argued from a different direction and none of them could show.")


def build() -> dict[str, Any]:
    cells = [cell(lvl, b, k) for lvl in SW["levels"] for b in SW["budget_bits"]
             for k in SW["skews"]]
    naive_wins = {_key(c) for c in cells if c["beats_replay"]["UNANIMITY_NAIVE"]}
    demand_wins = {_key(c) for c in cells if c["beats_replay"]["PRECOMPILED_DEMAND"]}
    eager_wins = {_key(c) for c in cells if c["beats_replay"]["PRECOMPILED_EAGER"]}
    skewed_l3 = [c for c in cells if c["level"] == 3 and c["skew"] == 1.0]

    w = {
        "W1_reuse_exists_and_lowers_deliberation": (
            any((c["arms"]["PRECOMPILED_DEMAND"]["cache_hit_rate"] or 0) > 0.5
                for c in cells)
            and all(c["arms"]["PRECOMPILED_DEMAND"]["deliberation"]
                    < c["arms"]["UNANIMITY_NAIVE"]["deliberation"] for c in cells)),
        "W2_compilation_changed_only_cost": all(
            c["compilation_changed_only_cost"] for c in cells),
        "W3_compiled_regime_is_a_strict_superset": (
            naive_wins < demand_wins),
        "W4_eager_costs_more_and_wins_nothing_extra": (
            all(c["arms"]["PRECOMPILED_EAGER"]["deliberation"]
                > c["arms"]["PRECOMPILED_DEMAND"]["deliberation"] for c in cells)
            and not (eager_wins - demand_wins)),
        "W5_compiled_wins_where_naive_never_did": (
            not any(c["beats_replay"]["UNANIMITY_NAIVE"] for c in skewed_l3)
            and any(c["beats_replay"]["PRECOMPILED_DEMAND"] for c in skewed_l3)),
    }
    terminal, reason = _terminal(cells, w)
    return {
        "study_id": "X6_COMPILED_CONSULTATION_V1",
        "authority": (
            "E2 synthetic. It adds an arm rather than an analysis and withdraws nothing "
            "from DEV-3, DEV-4, DEV-5, DEV-6, X3, X4 or X5."),
        "plan": X6_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": w,
        "language_size": len(language(LANG_LEVEL, SW["extension"])),
        "winning_settings": {
            "UNANIMITY_NAIVE": sorted(naive_wins),
            "PRECOMPILED_EAGER": sorted(eager_wins),
            "PRECOMPILED_DEMAND": sorted(demand_wins),
            "gained_by_compiling": sorted(demand_wins - naive_wins),
            "lost_by_compiling": sorted(naive_wins - demand_wins),
        },
        "the_control": (
            "PRECOMPILED_DEMAND and UNANIMITY_NAIVE were compared per replicate on every "
            "counter compilation is not permitted to touch. Disagreements are published in "
            "each cell as control_disagreements and any disagreement anywhere voids the "
            "study rather than reducing its confidence."),
        "control_disagreements_total": sum(
            len(c["control_disagreements"]) for c in cells),
        "what_this_does_not_establish": X6_PLAN["what_this_does_not_establish"],
        "novelty": X6_PLAN["novelty"],
        "primary_grid": cells,
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    print("control disagreements:", doc["control_disagreements_total"])
    for name, rows in doc["winning_settings"].items():
        print(f"  {name}: {len(rows)} -> {rows[:12]}")
    for c in doc["primary_grid"]:
        if c["level"] != 3 or c["skew"] != 1.0:
            continue
        r = c["ratio_to_replay"]
        a = c["arms"]["PRECOMPILED_DEMAND"]
        print(f"  L3 skew1 B={c['budget_bits']:5d} naive={r['UNANIMITY_NAIVE']} "
              f"eager={r['PRECOMPILED_EAGER']} demand={r['PRECOMPILED_DEMAND']} "
              f"hit={a['cache_hit_rate']} delib={a['deliberation']:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
