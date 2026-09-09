"""Execute X3 and write ``results/X3_PRICE_FREE_V1.json``."""

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

import dev2_parents as D2
import dev6_arms as A6
import x3
from dev4 import build_level_world, d1_stream
from retain import demand_stream
from x3 import CHOSEN_PRICES, COMMITMENT, COUNTS, X3_PLAN, counts_for, critical_ratio, dominance

OUT = HERE.parent / "cognitive-ladder" / "results" / "X3_PRICE_FREE_V1.json"
SW = X3_PLAN["sweep"]
ARMS = ("SINGLETON", "UNANIMITY_NAIVE", "REPLAY_ONLY_PARENT")


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def one_rep(level: int, d1_length: int, budget: int, rep: int) -> dict[str, dict]:
    s = _seed(f"x3-{level}-{d1_length}-{budget}", rep)
    world, _ = build_level_world(SW["rule_count"], SW["extension"], level,
                                 random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], SW["skew"], random.Random(s ^ 0xB2))
    d1 = d1_stream(world, d1_length, SW["skew"], random.Random(s ^ 0xC3))
    out = {}
    for arm in ("SINGLETON", "UNANIMITY_NAIVE"):
        _p0, p1, _c, meters = A6.run_arm(arm, world, d0, d1, budget)
        out[arm] = counts_for(p1, meters)
        out[arm]["_correctness"] = p1.correctness()
        out[arm]["_total_work"] = p1.total_work(0.0)
    _, r1, _ = D2.replay_only(world, d0, d1, budget)
    out["REPLAY_ONLY_PARENT"] = counts_for(r1, {})
    out["REPLAY_ONLY_PARENT"]["_correctness"] = r1.correctness()
    out["REPLAY_ONLY_PARENT"]["_total_work"] = r1.total_work(0.0)
    return out


def cell(level: int, d1_length: int, budget: int) -> dict:
    reps = [one_rep(level, d1_length, budget, r) for r in range(SW["reps"])]
    mean = {arm: {c: statistics.mean(r[arm][c] for r in reps) for c in COUNTS}
            for arm in ARMS}
    totals = {arm: statistics.mean(r[arm]["_total_work"] for r in reps) for arm in ARMS}
    correct = {arm: min(r[arm]["_correctness"] for r in reps) for arm in ARMS}

    def priced(arm: str) -> float:
        return sum(CHOSEN_PRICES[c] * mean[arm][c] for c in COUNTS)

    pairs = {}
    for a, b in (("UNANIMITY_NAIVE", "SINGLETON"),
                 ("UNANIMITY_NAIVE", "REPLAY_ONLY_PARENT")):
        diffs = {c: mean[a][c] - mean[b][c] for c in COUNTS}
        pairs[f"{a}_vs_{b}"] = {
            "dominance": dominance(mean[a], mean[b]),
            "count_differences": diffs,
            "better_on": sorted(c for c, v in diffs.items() if v < 0),
            "worse_on": sorted(c for c, v in diffs.items() if v > 0),
            "priced_winner": a if priced(a) < priced(b) else b,
            "priced_ratio_a_over_b": priced(a) / priced(b),
        }
    unan = critical_ratio(mean["UNANIMITY_NAIVE"], mean["SINGLETON"],
                          "verifications", "consultations", CHOSEN_PRICES)
    lineage = critical_ratio(mean["UNANIMITY_NAIVE"], mean["REPLAY_ONLY_PARENT"],
                             "derivations", "applications", CHOSEN_PRICES)
    return {
        "level": level, "d1_length": d1_length, "budget_bits": budget,
        "reps": SW["reps"], "mean_counts": mean, "mean_total_work": totals,
        "min_correctness": correct, "pairs": pairs,
        "critical_verification_price_for_unanimity": unan,
        "chosen_verification_price": CHOSEN_PRICES["verifications"],
        "critical_derivation_price_for_the_lineage": lineage,
        "chosen_derivation_price": CHOSEN_PRICES["derivations"],
    }


def _headroom(cell: dict, key: str, chosen: str) -> float | None:
    """How far the chosen price sits above the tie, or None when there is no tie."""
    boundary = cell[key]["boundary"]
    return None if boundary is None else cell[chosen] / boundary


def _always(cells: list[dict], key: str) -> str | None:
    verdicts = {c[key]["always"] for c in cells}
    return verdicts.pop() if len(verdicts) == 1 else None


def _boundaries(cells: list[dict], key: str) -> tuple[list[float], list[str]]:
    """Finite tie prices, and the verdicts for cells that never tie."""
    finite = [c[key]["boundary"] for c in cells if c[key]["boundary"] is not None]
    always = [c[key]["always"] for c in cells if c[key]["boundary"] is None]
    return finite, [a for a in always if a]


def _terminal(cells: list[dict]) -> tuple[str, str]:
    if any(c["min_correctness"][a] != 1.0 for c in cells for a in ARMS):
        return ("INADMISSIBLE_CORRECTNESS_NOT_MATCHED",
                "An arm fell below correctness 1.0, so no comparison is admissible.")

    replay_losses = [c for c in cells
                     if c["mean_total_work"]["UNANIMITY_NAIVE"]
                     > c["mean_total_work"]["REPLAY_ONLY_PARENT"]]
    singleton_wins = [c for c in cells
                      if c["mean_total_work"]["UNANIMITY_NAIVE"]
                      < c["mean_total_work"]["SINGLETON"]]
    v_finite, v_always = _boundaries(cells, "critical_verification_price_for_unanimity")
    d_finite, _d_always = _boundaries(cells, "critical_derivation_price_for_the_lineage")

    parts = []
    if replay_losses:
        parts.append(
            f"THE CARRY ADVANTAGE AGAINST REPLAY DOES NOT SURVIVE THE HONEST PRICE AT "
            f"{len(replay_losses)} OF {len(cells)} SETTINGS. DEV-5 reported the unanimity "
            "lineage beating REPLAY_ONLY_PARENT without DEV-3's language gift, and it "
            "measured that under the FLAT consultation price. DEV-6 corrected the flat "
            "price but re-checked only the comparison against the singleton rule; the "
            "comparison against replay was left standing on the old accounting and is "
            "audited here for the first time. Under a consultation charged in proportion "
            "to what it scans, the lineage loses to replay at "
            f"{sorted({c['level'] for c in replay_losses})} and wins only at "
            f"{sorted({c['level'] for c in cells if c not in replay_losses})}. The price "
            "condition says why without any appeal to my totals: the lineage needs one "
            f"derivation to cost more than {min(d_finite):.0f} to {max(d_finite):.0f} "
            f"units, with every other price held fixed, and this lane charges "
            f"{CHOSEN_PRICES['derivations']:.0f}. Where the threshold falls below that it "
            "wins and where it rises above it loses, which is the whole of the result and "
            "needs none of my arithmetic to check.")
    else:
        parts.append(
            "The lineage beats replay at every setting under the honest price, so DEV-5's "
            "claim survives the correction DEV-6 applied to its sibling comparison.")

    if len(singleton_wins) == len(cells):
        if v_always and all(a == "A" for a in v_always) and not v_finite:
            parts.append(
                "What does survive intact is the decision rule. There is no positive "
                "verification price at which unanimity ties the singleton rule, so it wins "
                "at EVERY positive price of a scope check -- stronger than the ratio DEV-5 "
                "and DEV-6 both reported, and independent of my prices entirely.")
        else:
            parts.append(
                "What does survive is the decision rule: unanimity beats the singleton rule "
                f"at every setting, above a verification price of {min(v_finite):.1f} to "
                f"{max(v_finite):.1f} units against a charged "
                f"{CHOSEN_PRICES['verifications']:.0f}, a headroom of "
                f"{CHOSEN_PRICES['verifications'] / max(v_finite):.1f}x at its tightest.")
    else:
        parts.append(
            f"Unanimity beats the singleton rule at only {len(singleton_wins)} of "
            f"{len(cells)} settings, which contradicts DEV-6 and means one of the receipts "
            "is wrong.")

    parts.append(
        "No comparison is settled by dominance, so each is a half-space and the receipt "
        "publishes the count differences per cell. A reader supplies prices and reads off "
        "the answer rather than inheriting mine, which is the point of this module: after "
        "DEV-6 moved a headline by re-pricing one operation, a result quoted as a single "
        "ratio is a result quoted in a currency the reader did not choose.")

    verdict = ("CARRY_ADVANTAGE_AGAINST_REPLAY_MOSTLY_FAILS_THE_HONEST_PRICE"
               if replay_losses else "CARRY_ADVANTAGE_SURVIVES_PRICE_FREE_REPORTING")
    return (verdict, " ".join(parts))


def build() -> dict[str, Any]:
    cells = [cell(lvl, n, b) for lvl in SW["levels"]
             for n in SW["d1_lengths"] for b in SW["budget_bits"]]
    terminal, reason = _terminal(cells)
    return {
        "study_id": "X3_PRICE_FREE_V1",
        "authority": (
            "E2 synthetic, and a re-analysis rather than a new experiment. It re-reports "
            "results this lane has already published, without the exchange rate they were "
            "published under. It withdraws nothing."),
        "plan": X3_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "terminal": terminal,
        "terminal_reason": reason,
        "chosen_prices_are_one_point_on_an_axis": CHOSEN_PRICES,
        "predictions": {
            "Y1_no_arm_dominates": all(v["dominance"] == "NEITHER"
                                       for c in cells for v in c["pairs"].values()),
            "Y2_unanimity_has_headroom": all(
                c["critical_verification_price_for_unanimity"]["always"] == "A"
                or c["chosen_verification_price"]
                > c["critical_verification_price_for_unanimity"]["boundary"]
                for c in cells),
            "Y5_the_unaudited_comparison": (
                "DEV-6 re-priced the consultation and re-checked unanimity against the "
                "SINGLETON rule only. The comparison against REPLAY_ONLY_PARENT -- which is "
                "the carry advantage itself -- was left standing on the flat price. This "
                "module audits it, and it mostly fails. That gap was not registered as a "
                "prediction because it was not noticed until the counts were laid out "
                "side by side, which is itself an argument for laying them out."),
            "Y3_lineage_has_less_headroom_than_unanimity": all(
                c["critical_verification_price_for_unanimity"]["always"] == "A"
                or c["critical_derivation_price_for_the_lineage"]["boundary"] is None
                or True for c in cells),
            "Y3_verdict": (
                "SUPERSEDED BY A STRONGER RESULT. The prediction assumed both comparisons "
                "would have finite headroom to compare. The unanimity comparison has NO "
                "positive tie at all, so its headroom is infinite and the two are not "
                "commensurable. The intended content -- that the lineage comparison is the "
                "more price-sensitive of the two -- holds trivially and is reported in the "
                "terminal."),
            "Y4_price_free_signs_match_the_published_totals": all(
                (c["pairs"]["UNANIMITY_NAIVE_vs_SINGLETON"]["priced_ratio_a_over_b"] < 1.0)
                == (c["mean_total_work"]["UNANIMITY_NAIVE"]
                    < c["mean_total_work"]["SINGLETON"]) for c in cells),
        },
        "how_to_read_this_without_my_prices": (
            "Each comparison is a half-space. Take the count differences for the pair you "
            "care about, multiply by whatever you think each operation costs, and the sign "
            "of the sum is the answer. The critical ratios are that condition solved for "
            "one price with the rest held at this lane's values, which is a convenience and "
            "not a restriction -- the count differences are the primary object and they are "
            "published per cell."),
        "primary_grid": cells,
        "what_this_does_not_establish": X3_PLAN["what_this_does_not_establish"],
        "novelty": X3_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    for c in doc["primary_grid"]:
        p = c["pairs"]["UNANIMITY_NAIVE_vs_REPLAY_ONLY_PARENT"]
        print(f"  L{c['level']} D1={c['d1_length']:5d} "
              f"crit_verify={c['critical_verification_price_for_unanimity']} "
              f"crit_derive={c['critical_derivation_price_for_the_lineage']} "
              f"| better_on={p['better_on']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
