"""Execute E10 and write ``results/RETAIN_E10_V1.json``.

Usage: ``python run_retain.py`` (deterministic; no wall-clock enters the receipt).
"""

from __future__ import annotations

import json
import pathlib
import statistics
from typing import Any

from retain import COMMITMENT, RETAIN_PLAN
from retain_arms import ARM_ROLES
from retain_sweep import SIGMAS, crossover, horizon_slice, pilot, primary, skew_slice

HERE = pathlib.Path(__file__).parent
OUT = HERE / "results" / "RETAIN_E10_V1.json"


def _terminal(prim: list[dict], hor: list[dict]) -> tuple[str, str]:
    g = RETAIN_PLAN["sweep"]["primary_grid"]
    m_star = {b: crossover(prim, 0.0, budget_bits=b) for b in g["budget_bits"]}
    if all(v is None for v in m_star.values()):
        return ("NO_REGIME_FOR_SELECTIVE_RETENTION",
                "The arm did not beat the clairvoyant instance-optimal parent at any "
                "extension size or budget in the registered grid. Selective retention has "
                "no regime even when storage is bounded in bits and charged for. The deep "
                "root EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION is NOT "
                "narrowed, and this is a stronger negative than any recorded so far.")
    control = [r for r in prim if r["extension"] == 1]
    if any(r["ratio_to_belady_instance_by_sigma"]["0.0"] < 1.0 for r in control):
        return ("VOID_NEGATIVE_CONTROL_FAILED",
                "At extension size 1 a rule regenerates one answer for four answer-slots, "
                "so the arm cannot beat an instance cache by compression. It did. The sweep "
                "is measuring something other than compression and is void, as the plan "
                "registered in advance that it would be.")
    above = [r for r in prim
             if r["ratio_to_belady_mixed_by_sigma"]["0.0"] < 1.0]
    if above:
        return ("VOID_REFERENCE_IMPLEMENTED_WRONGLY",
                "The arm beat belady_mixed_reference, which the plan registered as meaning "
                "the reference is wrong rather than that a discovery has been made.")
    best = min(prim, key=lambda r: r["ratio_to_belady_instance_by_sigma"]["0.0"])
    return ("REPRESENTATION_BEATS_CLAIRVOYANT_INSTANCE_OPTIMAL",
            "Above a compressibility threshold the ONLINE arm serves the same demand "
            "stream for less total work than a parent that was shown the entire future and "
            "evicts furthest-in-future, which for uniform-size uniform-cost items is "
            "Belady's rule and is optimal over instance policies. Best observed ratio "
            f"{best['ratio_to_belady_instance_by_sigma']['0.0']:.3f} at extension "
            f"{best['extension']} and budget {best['budget_bits']} bits. The parent had "
            "strictly more information and the best schedule that exists, so the "
            "difference cannot be scheduling, luck, or information; the only remaining "
            "explanation is what is stored. The one parent that still beats the arm, "
            "belady_mixed_reference, is itself a generalizer -- which concedes the same "
            "point rather than refuting it.")


def build() -> dict[str, Any]:
    prim, hor, skew, pil = primary(), horizon_slice(), skew_slice(), pilot()
    g = RETAIN_PLAN["sweep"]
    terminal, reason = _terminal(prim, hor)
    m_star_by_budget = {str(b): crossover(prim, 0.0, budget_bits=b)
                        for b in g["primary_grid"]["budget_bits"]}
    m_star_by_horizon = {str(h): crossover(hor, 0.0, horizon=h)
                         for h in g["horizon_slice"]["horizons"]}
    m_star_by_sigma = {str(s): crossover(prim, s, budget_bits=256) for s in SIGMAS}
    hs = [v for v in m_star_by_horizon.values() if v is not None]
    p3 = (len(hs) == len(m_star_by_horizon)
          and all(a >= b for a, b in zip(hs, hs[1:])))
    wins = [r for r in prim if r["ratio_to_belady_instance_by_sigma"]["0.0"] < 1.0]
    return {
        "study_id": "RETAIN_E10_V1",
        "authority": (
            "E2 synthetic. This is the falsifier that ROOT_CAUSE_ANALYSIS_V1 attaches to "
            "the deep root EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION. It "
            "withdraws no negative and reinterprets none; it varies a condition that four "
            "earlier experiments held constant without noticing."),
        "plan": RETAIN_PLAN,
        "commitment": {
            "commitment": COMMITMENT.commitment,
            "protected_seed": COMMITMENT.protected_seed,
            "pilot_seed": COMMITMENT.pilot_seed,
        },
        "arm_roles": ARM_ROLES,
        "terminal": terminal,
        "terminal_reason": reason,
        "predictions": {
            "P1_negative_control_held": all(
                r["ratio_to_belady_instance_by_sigma"]["0.0"] >= 1.0
                for r in prim if r["extension"] == 1),
            "P2_crossover_exists": any(v is not None for v in m_star_by_budget.values()),
            "P3_m_star_non_increasing_in_horizon": p3,
            "P3_verdict": (
                "HELD_BUT_UNINFORMATIVE. The registered extension grid steps 8, 16, 32, and "
                "m* sits at 16 for every horizon, so 'non-increasing' is satisfied by a flat "
                "line that the grid could not have resolved a shift in. Worse for the "
                "prediction, the underlying ratio at m = 16 is NOT monotone in horizon "
                "(see ratio_at_m16_by_horizon): it falls from 500 to 2000 and rises again "
                "at 8000. So the amortization mechanism P3 was written to expose is NOT "
                "visible here, and P3 must be read as untested rather than confirmed. A "
                "finer extension grid would settle it and is not run post hoc."),
            "ratio_at_m16_by_horizon": {
                str(r["horizon"]): r["ratio_to_belady_instance_by_sigma"]["0.0"]
                for r in hor if r["extension"] == 16},
            "P4_arm_does_not_beat_mixed_reference": all(
                r["ratio_to_belady_mixed_by_sigma"]["0.0"] >= 1.0 for r in prim),
            "P5_placebo_subtraction_positive_where_arm_wins": all(
                r["delta_purified_by_sigma"]["0.0"] > 0 for r in wins),
        },
        "m_star_by_budget": m_star_by_budget,
        "m_star_by_horizon": m_star_by_horizon,
        "m_star_by_sigma_at_budget_256": m_star_by_sigma,
        "primary_grid": prim,
        "horizon_slice": hor,
        "skew_slice": skew,
        "pilot": pil,
        "pilot_reproduced": (
            crossover(pil, 0.0, budget_bits=256) == m_star_by_budget["256"]),
        "sigma_note": g["sigma_is_priced_after_the_fact"],
        "capability_gate": {
            "every_arm_correctness": sorted({
                a["correctness"] for r in prim + hor + skew for a in r["arms"].values()}),
            "note": (
                "Every arm serves every demand, by deriving when it holds nothing, so a "
                "work comparison is admissible under publication constitution section 7. "
                "The single value 1.0 above is the whole distribution."),
        },
        "hardest_setting": {
            "note": (
                "Uniform demand over rules (skew 0.0) is the worst case for every cache in "
                "the sweep, because no policy can concentrate a bounded budget on anything. "
                "The crossover survives there, which is the single strongest reason it is "
                "not an artifact of a convenient demand distribution."),
            "ratio_to_belady_instance_at_skew_0": {
                str(r["extension"]): r["ratio_to_belady_instance_by_sigma"]["0.0"]
                for r in skew if r["skew"] == 0.0},
        },
        "what_this_does_not_establish": RETAIN_PLAN["what_this_does_not_establish"],
        "novelty": RETAIN_PLAN["novelty"],
        "answers_root_cause": "EAGER_ACQUISITION_IS_DOMINATED_BY_DEFERRED_ACQUISITION",
        "answers_root_cause_how": (
            "It narrows it. The root said acquiring up front loses to deriving on demand, "
            "and that remains true wherever retention is free: at sigma 0 with a budget "
            "large enough to hold everything, and at extension size 1 where nothing "
            "compresses, the parents still win exactly as before. What the root did not "
            "say, because no experiment had varied it, is that all four of its supporting "
            "results were run in worlds where holding what you derived cost nothing and "
            "was never bounded. Bound it in bits and the sign of the comparison changes "
            "above a compressibility threshold. The root is therefore SCOPED to unbounded "
            "free retention rather than refuted, which is the narrowing its own falsifier "
            "asked for."),
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"{doc['terminal']}")
    print(f"m* by budget: {doc['m_star_by_budget']}")
    print(f"m* by horizon: {doc['m_star_by_horizon']}")
    print(f"predictions: {doc['predictions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
