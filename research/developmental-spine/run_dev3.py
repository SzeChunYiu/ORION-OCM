"""Execute DEV-3 and write ``results/DEV3_GUARDED_RULES_V1.json``."""

from __future__ import annotations

import json
import pathlib
import random
import statistics
import sys
from typing import Any

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cognitive-ladder"))

import dev1_arms as A
import dev2_parents as D2
import dev3_arms as G
from dev3 import (COMMITMENT, DEV3_PLAN, GUARD_BITS, build_random_world,
                  build_structured_world, d1_stream)
from retain import FACT_BITS, RULE_BITS, demand_stream

OUT = HERE.parent / "cognitive-ladder" / "results" / "DEV3_GUARDED_RULES_V1.json"
SW = DEV3_PLAN["sweep"]

WINDOW_LO = SW["rule_count"] * (RULE_BITS + GUARD_BITS)
WINDOW_HI = SW["rule_count"] * SW["extension"] * FACT_BITS


def in_window(budget: int) -> bool:
    return WINDOW_LO <= budget < WINDOW_HI


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(regime: str, d1_length: int, budget: int, skew: float, rep: int) -> dict:
    s = _seed(f"dev3-{d1_length}-{budget}-{skew}", rep)
    structured, _truth = build_structured_world(SW["rule_count"], SW["extension"],
                                                random.Random(s ^ 0xA1))
    if regime == "STRUCTURED":
        world = structured
    else:
        # the SAME number of exceptions, placed at random
        world, _ = build_random_world(SW["rule_count"], SW["extension"],
                                      len(structured.exceptions), random.Random(s ^ 0xD4))
    d0 = demand_stream(world.base, SW["d0_length"], skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, d1_length, skew, random.Random(s ^ 0xC3))

    gp0, gp1, carried = G.guarded_lineage(world, d0, d1, budget)
    base, up0 = A.run_d0(world, d0, budget)
    _, up1 = A.run_d1(world, d1, budget, base.copy())
    _, rp1, _ = D2.replay_only(world, d0, d1, budget)
    return {
        "exception_count": len(world.exceptions),
        "GUARDED_LINEAGE": {"d1": gp1.total_work(0.0), "correctness": gp1.correctness(),
                            "verifications": gp1.verifications,
                            "applications": gp1.applications,
                            "guards_carried": len(carried.guards)},
        "UNGUARDED_LINEAGE": {"d1": up1.total_work(0.0), "correctness": up1.correctness(),
                              "verifications": up1.verifications,
                              "applications": up1.applications, "guards_carried": 0},
        "REPLAY_ONLY_PARENT": {"d1": rp1.total_work(0.0), "correctness": rp1.correctness(),
                               "verifications": 0, "applications": 0, "guards_carried": 0},
    }


def cell(regime: str, d1_length: int, budget: int, skew: float) -> dict:
    reps = [one_rep(regime, d1_length, budget, skew, r) for r in range(SW["reps"])]
    arms = ("GUARDED_LINEAGE", "UNGUARDED_LINEAGE", "REPLAY_ONLY_PARENT")
    out = {"regime": regime, "d1_length": d1_length, "budget_bits": budget, "skew": skew,
           "reps": SW["reps"], "in_analytic_window": in_window(budget),
           "mean_exception_count": statistics.mean(r["exception_count"] for r in reps),
           "arms": {}}
    for arm in arms:
        out["arms"][arm] = {
            "d1_work": statistics.mean(r[arm]["d1"] for r in reps),
            "correctness": min(r[arm]["correctness"] for r in reps),
            "verifications": statistics.mean(r[arm]["verifications"] for r in reps),
            "applications": statistics.mean(r[arm]["applications"] for r in reps),
            "guards_carried": statistics.mean(r[arm]["guards_carried"] for r in reps),
        }
    g = out["arms"]["GUARDED_LINEAGE"]["d1_work"]
    out["ratio_to_replay"] = g / out["arms"]["REPLAY_ONLY_PARENT"]["d1_work"]
    out["ratio_to_unguarded"] = g / out["arms"]["UNGUARDED_LINEAGE"]["d1_work"]
    out["guarded_beats_replay"] = out["ratio_to_replay"] < 1.0
    return out


def _terminal(cells: list[dict]) -> tuple[str, str]:
    if any(c["arms"][a]["correctness"] != 1.0 for c in cells for a in c["arms"]):
        return ("INADMISSIBLE_CORRECTNESS_NOT_MATCHED",
                "Some arm fell below correctness 1.0. A guarded arm that is ever wrong has "
                "skipped a check it had not earned, and no work figure is quoted.")
    window = [c for c in cells if c["in_analytic_window"]]
    struct_win = [c for c in window if c["regime"] == "STRUCTURED"]
    rand_win = [c for c in window if c["regime"] == "RANDOM"]
    control_breaks = [c for c in rand_win if c["guarded_beats_replay"]]
    wins = [c for c in struct_win if c["guarded_beats_replay"]]
    if not wins:
        return ("NO_CARRY_ADVANTAGE_UNDER_ANY_REPRESENTATION_TRIED",
                "The guarded arm did not beat REPLAY_ONLY_PARENT anywhere in the structured "
                "regime inside the analytic window. Removing the per-use check is therefore "
                "not sufficient to make abstraction pay, DEV-2's explanation is incomplete, "
                "and this lane has no carry advantage under any representation it has "
                "tried.")
    best = min(wins, key=lambda c: c["ratio_to_replay"])
    frac = len(wins) / len(struct_win)
    reason = (
        "The guarded lineage beats experience replay in the STRUCTURED regime inside the "
        f"analytic window, at {len(wins)} of {len(struct_win)} settings and by "
        f"{1 / best['ratio_to_replay']:.2f}x at its best ({best['d1_length']} demands, "
        f"{best['budget_bits']} bits, skew {best['skew']}), at correctness 1.0. This is the "
        "first result in this lane where carried structure beats the strongest parent that "
        "has beaten it before, and the mechanism is the one DEV-2 priced: a guard removes "
        "the per-use scope check, and it is paid for in bits from the same budget. "
        f"Against the unguarded lineage the same arm is {1 / best['ratio_to_unguarded']:.2f}x "
        "cheaper at that setting, so the guard and not the harness is doing the work.")
    if control_breaks:
        reason += (
            f" THE CONTROL IS NOT CLEAN. At {len(control_breaks)} of {len(rand_win)} "
            "settings the guarded arm also beats replay in the RANDOM regime, where no "
            "guard is learnable and the arm is DEV-1's unguarded lineage exactly. Those "
            "cells are wins for coverage rather than for guards -- a bounded buffer under "
            "uniform demand holds a small fraction of the answer space while a rule covers "
            "all of it -- and they are listed in control_exceptions. They mean the "
            "structured result is not attributable to guards alone at every setting, and "
            "the honest reading of the headline is narrowed to the cells where the random "
            "regime loses.")
    else:
        reason += (
            " The control is clean: in the RANDOM regime, where no guard in the language is "
            "sound and the arm degenerates to the unguarded lineage, replay wins at every "
            "setting in the window, reproducing DEV-2.")
    return ("GUARDED_CARRY_ADVANTAGE_INSIDE_THE_ANALYTIC_WINDOW", reason)


def build() -> dict[str, Any]:
    cells = [cell(regime, n, b, k)
             for regime in SW["regimes"] for n in SW["d1_lengths"]
             for b in SW["budget_bits"] for k in SW["skews"]]
    terminal, reason = _terminal(cells)
    window = [c for c in cells if c["in_analytic_window"]]
    struct = [c for c in window if c["regime"] == "STRUCTURED"]
    rand = [c for c in window if c["regime"] == "RANDOM"]
    outside = [c for c in cells if not c["in_analytic_window"]]
    by_skew = {}
    for k in SW["skews"]:
        rows = [c for c in struct if c["skew"] == k]
        by_skew[str(k)] = (statistics.mean(c["ratio_to_replay"] for c in rows)
                           if rows else None)
    matched = all(
        abs(a["mean_exception_count"] - b["mean_exception_count"]) < 1e-9
        for a in struct for b in rand
        if (a["d1_length"], a["budget_bits"], a["skew"])
        == (b["d1_length"], b["budget_bits"], b["skew"]))
    return {
        "study_id": "DEV3_GUARDED_RULES_V1",
        "authority": (
            "E2 synthetic. Responds to DEV2_CONTINUAL_PARENTS_V1, which withdrew this "
            "lane's only developmental positive and priced the reason. It withdraws no "
            "negative."),
        "plan": DEV3_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed,
                       "pilot_seed": COMMITMENT.pilot_seed},
        "arm_roles": {"GUARDED_LINEAGE": "MACHINE",
                      "UNGUARDED_LINEAGE": "PRIOR_MACHINE_DEV1",
                      "REPLAY_ONLY_PARENT": "PARENT_THAT_BEAT_US_IN_DEV2"},
        "terminal": terminal,
        "terminal_reason": reason,
        "analytic_window": {
            "low_bits": WINDOW_LO, "high_bits": WINDOW_HI,
            "low_is": "rule_count * (RULE_BITS + GUARD_BITS): below this the rules and "
                      "their guards do not fit at all",
            "high_is": "rule_count * extension * FACT_BITS: at or above this the replay "
                       "buffer holds the ENTIRE answer space and wins by arithmetic",
            "note": "Both bounds are computed from the registered constants, not searched.",
        },
        "predictions": {
            "G0_exception_counts_are_matched_across_regimes": matched,
            "G1_control_replay_beats_the_arm_under_random_exceptions": all(
                not c["guarded_beats_replay"] for c in rand),
            "G2_guarded_beats_replay_under_structured_exceptions": any(
                c["guarded_beats_replay"] for c in struct),
            "G3_guarded_ties_unguarded_under_random_exceptions": all(
                abs(c["ratio_to_unguarded"] - 1.0) < 0.05 for c in rand),
            "G4_correctness_is_one_everywhere": all(
                c["arms"][a]["correctness"] == 1.0 for c in cells for a in c["arms"]),
            "G5_advantage_is_confined_to_the_window": not any(
                c["guarded_beats_replay"] for c in outside
                if c["regime"] == "STRUCTURED" and c["budget_bits"] >= WINDOW_HI),
            "G6_advantage_survives_uniform_demand": (
                by_skew.get("0.0") is not None and by_skew["0.0"] <= by_skew["1.0"]),
        },
        "mean_ratio_to_replay_by_skew_in_window": by_skew,
        "control_exceptions": [
            {"regime": c["regime"], "d1_length": c["d1_length"],
             "budget_bits": c["budget_bits"], "skew": c["skew"],
             "ratio_to_replay": c["ratio_to_replay"],
             "guards_carried": c["arms"]["GUARDED_LINEAGE"]["guards_carried"]}
            for c in rand if c["guarded_beats_replay"]],
        "why_the_pilot_lost": {
            "note": (
                "The pilot's guarded arm held every guard it had learned and used almost "
                "none of them, because facts were allowed to evict guards. The corrected "
                "policy admits a guard with its rule and discards it with its rule. The "
                "verification counts below are what that correction bought; they are "
                "reported because a reader is entitled to check that the guard is being "
                "USED and not merely held."),
            "verifications_by_arm_in_window": {
                arm: statistics.mean(c["arms"][arm]["verifications"] for c in struct)
                for arm in ("GUARDED_LINEAGE", "UNGUARDED_LINEAGE")},
            "applications_by_arm_in_window": {
                arm: statistics.mean(c["arms"][arm]["applications"] for c in struct)
                for arm in ("GUARDED_LINEAGE", "UNGUARDED_LINEAGE")},
        },
        "what_this_does_not_establish": DEV3_PLAN["what_this_does_not_establish"],
        "novelty": DEV3_PLAN["novelty"],
        "primary_grid": cells,
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    print(f"window: {WINDOW_LO}..{WINDOW_HI}")
    for c in doc["primary_grid"]:
        if not c["in_analytic_window"]:
            continue
        print(f"  {c['regime']:10s} D1={c['d1_length']:5d} B={c['budget_bits']:5d} "
              f"skew={c['skew']} g/replay={c['ratio_to_replay']:.3f} "
              f"g/unguarded={c['ratio_to_unguarded']:.3f} "
              f"verif={c['arms']['GUARDED_LINEAGE']['verifications']:.0f}")
    print("control exceptions:", len(doc["control_exceptions"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
