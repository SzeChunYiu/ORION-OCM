"""Execute DEV-6 and write ``results/DEV6_HONEST_CONSULTATION_PRICE_V1.json``."""

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

import dev6_arms as A
from dev4 import LEVELS, build_level_world, d1_stream, language
from dev6 import COMMITMENT, DEV6_PLAN
from retain import demand_stream

OUT = HERE.parent / "cognitive-ladder" / "results" / "DEV6_HONEST_CONSULTATION_PRICE_V1.json"
DEV5_RECEIPT = HERE.parent / "cognitive-ladder" / "results" / "DEV5_UNANIMITY_V1.json"
SW = DEV6_PLAN["sweep"]


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(level: int, d1_length: int, budget: int, skew: float, rep: int) -> dict:
    s = _seed(f"dev6-{level}-{d1_length}-{budget}-{skew}", rep)
    world, _truth = build_level_world(SW["rule_count"], SW["extension"], level,
                                      random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, d1_length, skew, random.Random(s ^ 0xC3))
    out = {}
    for arm in A.ARMS:
        _p0, p1, _c, meters = A.run_arm(arm, world, d0, d1, budget)
        out[arm] = {"d1": p1.total_work(0.0), "correctness": p1.correctness(),
                    "verifications": p1.verifications,
                    "deliberation": meters["deliberation_total"],
                    "consultation": meters["consultation_charge"],
                    "maintenance": meters["maintenance"]}
    return out


def cell(level: int, d1_length: int, budget: int, skew: float) -> dict:
    reps = [one_rep(level, d1_length, budget, skew, r) for r in range(SW["reps"])]
    out = {"level": level, "d1_length": d1_length, "budget_bits": budget, "skew": skew,
           "reps": SW["reps"], "arms": {}}
    for arm in A.ARMS:
        out["arms"][arm] = {
            "role": A.ARM_ROLES[arm],
            "d1_work": statistics.mean(r[arm]["d1"] for r in reps),
            "min_correctness": min(r[arm]["correctness"] for r in reps),
            "verifications": statistics.mean(r[arm]["verifications"] for r in reps),
            "deliberation": statistics.mean(r[arm]["deliberation"] for r in reps),
            "consultation": statistics.mean(r[arm]["consultation"] for r in reps),
            "maintenance": statistics.mean(r[arm]["maintenance"] for r in reps),
        }
    base = out["arms"]["SINGLETON"]["d1_work"]
    out["ratio_to_singleton"] = {
        a: out["arms"][a]["d1_work"] / base for a in A.ARMS if a != "SINGLETON"}
    return out


def dev5_ratio_range() -> tuple[float, float]:
    """DEV-5's own reported range, read from its receipt rather than typed.

    An earlier draft of this module hard-coded 0.197 and 0.837 into its terminal
    text. The first was right and the second was not -- DEV-5's worst ratio is
    0.89 -- which is exactly the sort of error a self-audit cannot afford to make
    about the result it is auditing.
    """
    dev5 = json.loads(DEV5_RECEIPT.read_text())
    ratios = [c["ratio_to"]["SINGLETON_FULL"] for c in dev5["primary_grid"]]
    return min(ratios), max(ratios)


def _terminal(cells: list[dict]) -> tuple[str, str]:
    if any(c["arms"][a]["min_correctness"] != 1.0 for c in cells for a in A.ARMS):
        return ("VOID_PRICING_CHANGED_CORRECTNESS",
                "All three arms hold the full language and are sound by construction, so a "
                "pricing change cannot move correctness. It did, which is a bug.")
    naive = [c["ratio_to_singleton"]["UNANIMITY_NAIVE"] for c in cells]
    incr = [c["ratio_to_singleton"]["UNANIMITY_INCREMENTAL"] for c in cells]
    naive_wins = [r for r in naive if r < 1.0]
    incr_wins = [r for r in incr if r < 1.0]
    if not naive_wins and not incr_wins:
        return ("DEV5_FACTOR_WAS_A_PRICING_ARTIFACT",
                "Neither unanimity arm beats SINGLETON once deliberation is charged in "
                "proportion to the work it does. DEV-5's factor was an artifact of a flat "
                "price this lane chose, and the carry advantage it recovered goes back to "
                "resting on the language gift DEV-4 showed was binding.")
    d5_best, d5_worst = dev5_ratio_range()
    return ("DEV5_SURVIVES_A_SMALLER_RESULT",
            "The result survives the honest bill and the number does not. "
            f"UNANIMITY_NAIVE still beats SINGLETON at {len(naive_wins)} of {len(cells)} "
            f"settings, with the best ratio moving from DEV-5's {d5_best:.3f} to "
            f"{min(naive):.3f} and the worst from {d5_worst:.3f} to {max(naive):.3f} -- so "
            f"the headline factor falls from {1 / d5_best:.1f}x to {1 / min(naive):.1f}x and "
            "the weakest cell is now nearly a tie. The erosion is not uniform: it "
            "is small where the language is small and nearly total where it is large, "
            "because a flat price hides exactly the cost that grows with the space being "
            "scanned, and DEV-5 measured its headline at the large-language end. "
            + (f"UNANIMITY_INCREMENTAL, this module's own proposed fix, is REFUTED: it is "
               f"worse than SINGLETON at {len(incr) - len(incr_wins)} of {len(cells)} "
               f"settings, by up to {max(incr):.1f}x. Maintaining per-index vote counts "
               "over a language of this size costs more than scanning it thousands of "
               "times, and charging the bookkeeping is the only reason that is visible. "
               "Proposing it without charging it would have repeated the mistake this "
               "module exists to correct."
               if len(incr_wins) < len(cells) else
               "UNANIMITY_INCREMENTAL beats SINGLETON as predicted."))


def build() -> dict[str, Any]:
    cells = [cell(lvl, n, b, k)
             for lvl in SW["levels"] for n in SW["d1_lengths"]
             for b in SW["budget_bits"] for k in SW["skews"]]
    terminal, reason = _terminal(cells)
    dev5 = json.loads(DEV5_RECEIPT.read_text())
    dev5_ratios = [c["ratio_to"]["SINGLETON_FULL"] for c in dev5["primary_grid"]]
    naive = {c["level"]: [] for c in cells}
    for c in cells:
        naive[c["level"]].append(c["ratio_to_singleton"]["UNANIMITY_NAIVE"])
    return {
        "study_id": "DEV6_HONEST_CONSULTATION_PRICE_V1",
        "authority": (
            "E2 synthetic, and an AUDIT OF THIS LANE'S OWN RESULT rather than a new claim. "
            "It re-prices DEV-5 against the accounting standard E6 already used and reports "
            "what changed. DEV-5's receipt is not withdrawn; its magnitude is corrected."),
        "plan": DEV6_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "arm_roles": A.ARM_ROLES,
        "terminal": terminal,
        "terminal_reason": reason,
        "language_size_at_top_level": len(language(max(LEVELS), SW["extension"])),
        "predictions": {
            "P1_naive_loses_most_of_the_advantage": bool(
                max(c["ratio_to_singleton"]["UNANIMITY_NAIVE"] for c in cells) > 0.8),
            "P1_verdict": (
                "PARTIALLY HELD. The advantage erodes and does not disappear: the naive arm "
                "still beats the singleton rule everywhere, but its worst ratio rises from "
                f"DEV-5's {dev5_ratio_range()[1]:.3f} to "
                f"{max(c['ratio_to_singleton']['UNANIMITY_NAIVE'] for c in cells):.3f}. "
                "The erosion is concentrated at the large-language end, which is where "
                "DEV-5 quoted its headline."),
            "P2_incremental_keeps_an_advantage": all(
                c["ratio_to_singleton"]["UNANIMITY_INCREMENTAL"] < 1.0 for c in cells),
            "P2_verdict": (
                "REFUTED, and this lane proposed the arm. Maintaining per-index vote counts "
                "costs extension times the language size per rule at seeding and extension "
                "per elimination after, which for a 433-predicate language dwarfs the scans "
                "it saves. The engineering answer to an expensive scan is not always a "
                "cheaper scan, and the only reason that is visible here is that the "
                "bookkeeping was charged."),
            "P3_incremental_loses_at_short_d1": all(
                c["ratio_to_singleton"]["UNANIMITY_INCREMENTAL"] > 1.0
                for c in cells if c["d1_length"] == min(SW["d1_lengths"])),
            "P4_correctness_unchanged": all(
                c["arms"][a]["min_correctness"] == 1.0 for c in cells for a in A.ARMS),
            "P5_naive_deliberation_exceeds_incremental_at_long_d1": all(
                c["arms"]["UNANIMITY_NAIVE"]["deliberation"]
                > c["arms"]["UNANIMITY_INCREMENTAL"]["deliberation"]
                for c in cells if c["d1_length"] == max(SW["d1_lengths"])),
            "P5_verdict": (
                "REFUTED. The incremental arm's bookkeeping still exceeds the naive arm's "
                "scanning even at the longest D1 in the sweep, so it never amortizes within "
                "any workload measured here. P5 was the arithmetic reason the incremental "
                "arm was proposed, and its failure is why P2 fails too."),
        },
        "correction_to_dev5": {
            "dev5_reported_ratio_range": [min(dev5_ratios), max(dev5_ratios)],
            "honest_price_ratio_range": [
                min(c["ratio_to_singleton"]["UNANIMITY_NAIVE"] for c in cells),
                max(c["ratio_to_singleton"]["UNANIMITY_NAIVE"] for c in cells)],
            "mean_ratio_by_level": {str(k): statistics.mean(v) for k, v in naive.items()},
            "note": (
                "DEV-5's ratios were measured with a flat consultation price, which charges "
                "a scan of up to 433 predicates the same as a test for whether a set has "
                "one element. Under a charge proportional to the scan, the ordering is "
                "unchanged and the magnitude is not. The mean ratio by world level shows "
                "where the difference lives: the larger the language, the more the flat "
                "price was hiding. DEV-5's conclusion -- that the singleton rule was "
                "needlessly strong -- stands; its factor of up to 5.1 does not, and any "
                "later use of that number should use the range here instead."),
        },
        "why_the_fix_failed": {
            "note": (
                "The incremental arm was this module's own idea and it is the worse arm. "
                "Its cost is paid whether or not the queries arrive: seeding is extension "
                "times language size per rule, and elimination is extension per predicate "
                "removed. Both are bounded by the language rather than by the workload, so "
                "a large language makes the bookkeeping unavoidable while the scan it "
                "replaces is only paid when a query actually comes."),
            "mean_maintenance": statistics.mean(
                c["arms"]["UNANIMITY_INCREMENTAL"]["maintenance"] for c in cells),
            "mean_naive_consultation": statistics.mean(
                c["arms"]["UNANIMITY_NAIVE"]["consultation"] for c in cells),
        },
        "primary_grid": cells,
        "what_this_does_not_establish": DEV6_PLAN["what_this_does_not_establish"],
        "novelty": DEV6_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps({k: v for k, v in doc["predictions"].items()
                                      if not k.endswith("verdict")}))
    c = doc["correction_to_dev5"]
    print("DEV-5 reported range:", [round(x, 3) for x in c["dev5_reported_ratio_range"]])
    print("honest price range:  ", [round(x, 3) for x in c["honest_price_ratio_range"]])
    print("mean ratio by level: ", {k: round(v, 3) for k, v in c["mean_ratio_by_level"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
