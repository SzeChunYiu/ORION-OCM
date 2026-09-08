"""Execute X5 and write ``results/X5_BUDGET_CROSSING_V1.json``."""

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
import x5
from dev1 import COMPOSE_COST, VERIFY_COST
from dev4 import build_level_world, d1_stream, language
from dev3 import GUARD_BITS
from retain import (APPLY_COST, DERIVE_COST, FACT_BITS, INDUCE_COST, LOOKUP_COST,
                    RULE_BITS, demand_stream)
from x5 import BUDGETS, COMMITMENT, DEV3_ANALYTIC_LOWER_EDGE, X5_PLAN

OUT = HERE.parent / "cognitive-ladder" / "results" / "X5_BUDGET_CROSSING_V1.json"
SW = X5_PLAN["sweep"]

#: arm -> (language level, decision rule). REPLAY_ONLY_PARENT holds no language.
ARM_SPEC = {"GUARDED_SMALL_LANGUAGE": (1, "singleton"),
            "UNANIMITY_FULL_LANGUAGE": (3, "unanimity_naive")}
ARMS = tuple(ARM_SPEC) + ("REPLAY_ONLY_PARENT",)


def _seed(tag: str, rep: int) -> int:
    acc = 0
    for ch in tag:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return int(COMMITMENT.protected_seed[:12], 16) ^ (acc + rep * 7919)


def _counters(phase, deliberation: int) -> dict[str, int]:
    """The priced events of one phase, with deliberation split out of lookup work.

    ``lookup_work`` carries both real lookups and the consultation charge, because
    DEV-6 charged deliberation into it. Y5(b) needs them separated.
    """
    pure_lookup_work = phase.lookup_work - deliberation
    assert pure_lookup_work % LOOKUP_COST == 0, "lookup work is not a multiple of its price"
    return {"derivations": phase.derivations, "applications": phase.applications,
            "lookups": pure_lookup_work // LOOKUP_COST, "inductions": phase.inductions,
            "verifications": phase.verifications, "compositions": phase.served,
            "deliberation": deliberation}


def _work_from_counters(c: dict[str, int]) -> int:
    """Total work rebuilt from the priced events alone. Must equal total_work(0)."""
    return (DERIVE_COST * c["derivations"] + APPLY_COST * c["applications"]
            + LOOKUP_COST * c["lookups"] + INDUCE_COST * c["inductions"]
            + VERIFY_COST * c["verifications"] + COMPOSE_COST * c["compositions"]
            + c["deliberation"])


def one_rep(level: int, budget: int, skew: float, rep: int) -> dict[str, Any]:
    s = _seed(f"x5-{level}-{budget}-{skew}", rep)
    world, _ = build_level_world(SW["rule_count"], SW["extension"], level,
                                 random.Random(s ^ 0xA1))
    d0 = demand_stream(world.base, SW["d0_length"], skew, random.Random(s ^ 0xB2))
    d1 = d1_stream(world, SW["d1_length"], skew, random.Random(s ^ 0xC3))
    out: dict[str, Any] = {}
    for arm, (lang_level, mode) in ARM_SPEC.items():
        _p0, p1, _c, meters = A6._run(world, d0, d1, budget, mode, lang_level)
        counters = _counters(p1, meters["deliberation_total"])
        out[arm] = {"work": p1.total_work(0.0), "correctness": p1.correctness(),
                    "counters": counters,
                    "work_from_counters": _work_from_counters(counters),
                    "held_rules_final": meters["held_rules_final"],
                    "rules_final": meters["rules_final"],
                    "consultations": meters["consultations"],
                    "language_size": meters["language_size"]}
    _p0, r1, _c = D2.replay_only(world, d0, d1, budget)
    counters = _counters(r1, 0)
    out["REPLAY_ONLY_PARENT"] = {"work": r1.total_work(0.0), "correctness": r1.correctness(),
                                 "counters": counters,
                                 "work_from_counters": _work_from_counters(counters),
                                 "held_rules_final": 0, "rules_final": 0,
                                 "consultations": 0, "language_size": 0}
    return out


def cell(level: int, budget: int, skew: float) -> dict[str, Any]:
    reps = [one_rep(level, budget, skew, r) for r in range(SW["reps"])]
    out: dict[str, Any] = {"level": level, "budget_bits": budget, "skew": skew,
                           "reps": SW["reps"], "arms": {}}
    for arm in ARMS:
        rows = [r[arm] for r in reps]
        sound = all(r["correctness"] == 1.0 for r in rows)
        out["arms"][arm] = {
            "min_correctness": min(r["correctness"] for r in rows),
            "sound_in_every_replicate": sound,
            "work": statistics.mean(r["work"] for r in rows) if sound else None,
            "work_if_it_were_admissible": statistics.mean(r["work"] for r in rows),
            "counters": {k: statistics.mean(r["counters"][k] for r in rows)
                         for k in rows[0]["counters"]},
            "held_rules_final": statistics.mean(r["held_rules_final"] for r in rows),
            "min_held_rules_final": min(r["held_rules_final"] for r in rows),
            "consultations": statistics.mean(r["consultations"] for r in rows),
            "language_size": rows[0]["language_size"],
            "counter_identity_residual": max(abs(r["work"] - r["work_from_counters"])
                                             for r in rows),
        }
    replay = out["arms"]["REPLAY_ONLY_PARENT"]
    admissible = replay["sound_in_every_replicate"]
    out["ratio_to_replay"] = {
        a: (out["arms"][a]["work"] / replay["work"]
            if admissible and out["arms"][a]["work"] is not None and replay["work"] else None)
        for a in ARM_SPEC}
    out["margin"] = {
        a: (replay["work"] - out["arms"][a]["work"]
            if admissible and out["arms"][a]["work"] is not None else None)
        for a in ARM_SPEC}
    out["beats_replay"] = {a: (v is not None and v < 1.0)
                           for a, v in out["ratio_to_replay"].items()}
    return out


def _series(cells: list[dict], arm: str, level: int, skew: float) -> list[dict]:
    rows = [c for c in cells if c["level"] == level and c["skew"] == skew]
    return sorted(rows, key=lambda c: c["budget_bits"])


def crossings(cells: list[dict], arm: str, level: int, skew: float) -> dict[str, Any]:
    """Where the sign of the margin changes as the budget grows.

    Returns every sign change, not only the first, so that "exactly once" is a
    finding rather than an artefact of stopping at the first one. Budgets with no
    admissible figure are skipped and reported, never imputed.
    """
    rows = [c for c in _series(cells, arm, level, skew) if c["margin"][arm] is not None]
    signs = [(c["budget_bits"], c["margin"][arm] > 0) for c in rows]
    changes = [{"between": [signs[i][0], signs[i + 1][0]],
                "direction": "TO_WINNING" if signs[i + 1][1] else "TO_LOSING"}
               for i in range(len(signs) - 1) if signs[i][1] != signs[i + 1][1]]
    skipped = [c["budget_bits"] for c in _series(cells, arm, level, skew)
               if c["margin"][arm] is None]
    return {"arm": arm, "level": level, "skew": skew,
            "budgets_with_an_admissible_figure": [b for b, _ in signs],
            "budgets_skipped_for_correctness": skipped,
            "wins_at": [b for b, w in signs if w], "loses_at": [b for b, w in signs if not w],
            "sign_changes": changes, "crossing_count": len(changes),
            "single_crossing": len(changes) == 1,
            "direction": changes[0]["direction"] if len(changes) == 1 else None}


def _spread(cells: list[dict], arm: str, level: int, skew: float) -> float | None:
    vals = [c["arms"][arm]["work_if_it_were_admissible"]
            for c in _series(cells, arm, level, skew)]
    vals = [v for v in vals if v]
    return max(vals) / min(vals) if vals else None


def window_analysis(cells: list[dict]) -> dict[str, Any]:
    """DEV-3's analytic window, checked at budgets DEV-3 never ran.

    POST HOC WITHIN X5: nothing here was registered in X5_PLAN, and the fields
    below were added after the sweep printed its crossings. What is NOT post hoc
    is DEV-3's window itself. DEV-3 computed both edges from the cost constants
    before any of these nine budgets existed:

        lower edge  rule_count * (RULE_BITS + GUARD_BITS)  -- below it the store
                    cannot hold the rules and their guards at all
        upper edge  rule_count * extension * FACT_BITS     -- at or above it the
                    replay parent can memoise the entire answer space

    So this section tests a prior study's registered arithmetic out of sample and
    reports the outcome for each edge separately.
    """
    rule_count, extension = SW["rule_count"], SW["extension"]
    lower = rule_count * (RULE_BITS + GUARD_BITS)
    upper = rule_count * extension * FACT_BITS
    arm = "GUARDED_SMALL_LANGUAGE"
    rows = {k: _series(cells, arm, 1, k) for k in SW["skews"]}

    def wins(k: int, b: int) -> bool | None:
        for c in rows[k]:
            if c["budget_bits"] == b:
                return None if c["margin"][arm] is None else c["margin"][arm] > 0
        return None

    at_or_above_upper = [b for b in BUDGETS if b >= upper]
    inside = [b for b in BUDGETS if lower <= b < upper]
    losses_inside = sorted({b for k in SW["skews"] for b in inside if wins(k, b) is False})
    # The largest contiguous run of budgets, ending below the upper edge, that the
    # arm wins at EVERY skew. This is the regime, as opposed to isolated wins.
    regime: list[int] = []
    for b in reversed(inside):
        if all(wins(k, b) for k in SW["skews"]):
            regime.insert(0, b)
        elif regime:
            break
    return {
        "provenance": (
            "POST HOC within X5 and registered in DEV-3. The edges below were computed "
            "by DEV3_GUARDED_RULES_V1 from the cost constants alone, before any of these "
            "nine budgets was swept, so the two edge questions are out-of-sample tests of "
            "a prior registration. The decision to ask them HERE was made after seeing "
            "X5's crossings, and no claim in this section is treated as pre-registered."),
        "dev3_lower_edge_bits": lower,
        "dev3_upper_edge_bits": upper,
        "upper_edge_holds": all(wins(k, b) is False for k in SW["skews"]
                                for b in at_or_above_upper),
        "upper_edge_reading": (
            f"At {upper} bits the parent stores every one of the {rule_count * extension} "
            f"answers ({rule_count * extension} * {FACT_BITS} = {upper}), its derivations "
            "collapse, and no representation can beat a complete memo. DEV-3 computed that "
            "edge and this study is the first to run a budget at it."),
        "lower_edge_is_sufficient": not losses_inside,
        "budgets_inside_the_window_that_the_arm_loses": losses_inside,
        "lower_edge_reading": (
            "DEV-3's lower edge counts the bits needed to STORE the rules and their "
            "guards. It does not count the bits needed to KEEP them while the same budget "
            "also serves facts. Under eviction pressure the arm holds only a fraction of "
            "its guards until well above that edge, so the edge is necessary and NOT "
            "sufficient, and the window overstates the regime at its bottom."),
        "measured_carry_regime_bits": regime,
        "held_guards_by_budget": {
            str(k): {str(c["budget_bits"]): c["arms"][arm]["held_rules_final"]
                     for c in rows[k]} for k in SW["skews"]},
        "arm_work_by_budget": {
            str(k): {str(c["budget_bits"]):
                     c["arms"][arm]["work_if_it_were_admissible"] for c in rows[k]}
            for k in SW["skews"]},
        "replay_work_by_budget": {
            str(k): {str(c["budget_bits"]):
                     c["arms"]["REPLAY_ONLY_PARENT"]["work_if_it_were_admissible"]
                     for c in rows[k]} for k in SW["skews"]},
        "why_the_margin_is_not_monotone": (
            "Both curves fall with the budget and neither falls at a constant rate. The "
            "arm's work is nearly flat while it holds a minority of its guards, then drops "
            "sharply as the held count approaches rule_count, then saturates. The parent's "
            "falls smoothly throughout and then collapses at the memoisation edge. A margin "
            "that is the difference of two such curves can change sign more than once, and "
            "it does. Y1 asked for a single crossing and was refuted for this reason; the "
            "refutation is a fact about the shape of the two cost curves, not about whether "
            "a guard pays."),
    }


def _terminal(cells: list[dict], y: dict[str, Any]) -> tuple[str, str]:
    if any(c["arms"][a]["counter_identity_residual"] != 0
           for c in cells for a in c["arms"]):
        return ("COUNTER_IDENTITY_REFUTED",
                "Total work does not equal the sum of the priced events. Some cost in this "
                "lane is charged outside the six named channels, so every margin it has "
                "reported is a number without an account of what produced it. Nothing "
                "downstream of this is interpretable until it is found.")
    if not y["Y1_guarded_single_crossing_upward"] and not y["Y3_unanimity_single_crossing_downward"]:
        return ("CARRY_ADVANTAGE_UNCHARACTERISED",
                "Neither margin has a single clean crossing over nine budgets. This lane "
                "cannot describe the boundary of its own result: X4's positive is an "
                "isolated cell rather than a regime, and the carry advantage is "
                "UNCHARACTERISED. X4's receipt is not withdrawn on account of this.")
    if y["Y1_guarded_single_crossing_upward"] and y["Y3_unanimity_single_crossing_downward"]:
        return ("TWO_REGIMES_WITH_OPPOSITE_BUDGET_EDGES",
                "Both margins cross zero exactly once over nine budgets and in opposite "
                "directions: the gated guarded arm from losing to winning as the budget "
                "grows, the flat-cost unanimity arm from winning to losing. The two "
                "positives X4 reported are regimes with located edges rather than isolated "
                "cells, and one asymmetry -- a parent whose cost falls with the budget "
                "against one arm whose cost is flat and one arm whose benefit is gated -- "
                "covers both signs.")
    which = "guarded" if y["Y1_guarded_single_crossing_upward"] else "unanimity"
    return ("ONE_REGIME_ONE_UNCHARACTERISED",
            f"Exactly one of the two margins is a regime with a single located edge (the "
            f"{which} arm). The other is not, so half of X4's open question is answered and "
            f"half is not, and the unresolved half is reported as uncharacterised rather "
            f"than described.")


def build() -> dict[str, Any]:
    cells = [cell(lvl, b, k) for lvl in SW["levels"] for b in SW["budget_bits"]
             for k in SW["skews"]]
    guarded = [crossings(cells, "GUARDED_SMALL_LANGUAGE", 1, k) for k in SW["skews"]]
    unan = [crossings(cells, "UNANIMITY_FULL_LANGUAGE", 3, k) for k in SW["skews"]]
    unan_uniform = [x for x in unan if x["skew"] == 0.0][0]

    # Y2: the gate must be visible in the store, below the crossing and not above.
    gate_rows = []
    for cr in guarded:
        if not cr["single_crossing"]:
            gate_rows.append({"skew": cr["skew"], "testable": False}); continue
        edge = cr["sign_changes"][0]["between"][1]
        rows = _series(cells, "GUARDED_SMALL_LANGUAGE", 1, cr["skew"])
        below = [c for c in rows if c["budget_bits"] < edge]
        at_or_above = [c for c in rows if c["budget_bits"] >= edge]
        gate_rows.append({
            "skew": cr["skew"], "testable": True, "crossing_at_budget": edge,
            "held_below": [c["arms"]["GUARDED_SMALL_LANGUAGE"]["min_held_rules_final"]
                           for c in below],
            "held_at_or_above": [c["arms"]["GUARDED_SMALL_LANGUAGE"]["min_held_rules_final"]
                                 for c in at_or_above],
            "starved_below": all(c["arms"]["GUARDED_SMALL_LANGUAGE"]["min_held_rules_final"]
                                 < SW["rule_count"] for c in below),
            "saturated_at_or_above": all(
                c["arms"]["GUARDED_SMALL_LANGUAGE"]["min_held_rules_final"]
                == SW["rule_count"] for c in at_or_above)})

    # Y5(a): same language, opposite carry sign.
    same_language_opposite_sign = {}
    for arm in ARM_SPEC:
        wins = [(c["level"], c["budget_bits"], c["skew"]) for c in cells
                if c["beats_replay"][arm]]
        losses = [(c["level"], c["budget_bits"], c["skew"]) for c in cells
                  if c["margin"][arm] is not None and not c["beats_replay"][arm]]
        same_language_opposite_sign[arm] = {
            "wins": wins, "losses": losses,
            "both_signs_occur": bool(wins) and bool(losses)}

    y = {
        "Y1_guarded_single_crossing_upward": all(
            cr["single_crossing"] and cr["direction"] == "TO_WINNING" for cr in guarded),
        "Y2_gate_is_the_held_guard_count": all(
            g["testable"] and g["starved_below"] and g["saturated_at_or_above"]
            for g in gate_rows),
        "Y3_unanimity_single_crossing_downward": (
            unan_uniform["single_crossing"] and unan_uniform["direction"] == "TO_LOSING"),
        "Y4_unanimity_flat_replay_falling": all(
            (_spread(cells, "UNANIMITY_FULL_LANGUAGE", 3, k) or 99) < 1.5
            and (_spread(cells, "REPLAY_ONLY_PARENT", 3, k) or 0) > 2.0
            for k in SW["skews"]),
        "Y5a_same_language_opposite_sign": any(
            v["both_signs_occur"] for v in same_language_opposite_sign.values()),
        "Y5b_margin_is_a_function_of_what_was_charged": all(
            c["arms"][a]["counter_identity_residual"] == 0 for c in cells for a in c["arms"]),
    }
    terminal, reason = _terminal(cells, y)
    return {
        "study_id": "X5_BUDGET_CROSSING_V1",
        "authority": (
            "E2 synthetic. It locates the edges of two results X4 reported and withdraws "
            "nothing from X4, X3, DEV-6 or DEV-5."),
        "plan": X5_PLAN,
        "commitment": {"commitment": COMMITMENT.commitment,
                       "protected_seed": COMMITMENT.protected_seed},
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": y,
        "dev3_analytic_lower_edge_bits": DEV3_ANALYTIC_LOWER_EDGE,
        "dev3_analytic_lower_edge_status": (
            "ALREADY REFUTED by X4, which measured a loss at 1024 bits, well above this "
            "edge. X5 does not re-guess an arithmetic gate; it reads the gate off the "
            "store's own held-guard count and reports whether that explains the crossing."),
        "language_sizes": {a: len(language(lvl, SW["extension"]))
                           for a, (lvl, _) in ARM_SPEC.items()},
        "crossings": {"GUARDED_SMALL_LANGUAGE_level1": guarded,
                      "UNANIMITY_FULL_LANGUAGE_level3": unan},
        "gate_evidence": gate_rows,
        "window_analysis": window_analysis(cells),
        "sign_by_arm": same_language_opposite_sign,
        "work_spread_over_budget": {
            f"level{lvl}_skew{k}": {a: _spread(cells, a, lvl, k) for a in ARMS}
            for lvl in SW["levels"] for k in SW["skews"]},
        "what_the_chi_review_changes_here": (
            "The independent review of PR #150 shows that a calibrated posterior's "
            "perplexity does not bound expected guess cost. The analogous claim in this "
            "lane would be that a small version space wins because it is small. Y5 tests "
            "that directly and the result is recorded whichever way it falls: if the same "
            "language produces both signs, size cannot be the operative quantity, and the "
            "operative quantity is the charge -- which is what this lane has been measuring "
            "since DEV-6 and what X4's positive actually rests on."),
        "primary_grid": cells,
        "what_this_does_not_establish": X5_PLAN["what_this_does_not_establish"],
        "novelty": X5_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps(doc["predictions"]))
    for name, rows in doc["crossings"].items():
        for cr in rows:
            print(f"  {name} skew={cr['skew']}: wins_at={cr['wins_at']} "
                  f"loses_at={cr['loses_at']} crossings={cr['crossing_count']} "
                  f"dir={cr['direction']}")
    print("gate:", json.dumps(doc["gate_evidence"]))
    print("spread:", json.dumps(doc["work_spread_over_budget"]))
    w = doc["window_analysis"]
    print(f"window: dev3=[{w['dev3_lower_edge_bits']}, {w['dev3_upper_edge_bits']}] "
          f"upper_holds={w['upper_edge_holds']} lower_sufficient={w['lower_edge_is_sufficient']} "
          f"losses_inside={w['budgets_inside_the_window_that_the_arm_loses']} "
          f"measured_regime={w['measured_carry_regime_bits']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
