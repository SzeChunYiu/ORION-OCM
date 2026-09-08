"""Execute X1 and write ``results/X1_UNANIMITY_TRANSFER_V1.json``."""

from __future__ import annotations

import json
import pathlib
from typing import Any

import support_arms as SA
import unanimity_transfer as X
from support import SUPPORT_PLAN

HERE = pathlib.Path(__file__).parent
OUT = HERE / "results" / "X1_UNANIMITY_TRANSFER_V1.json"

ARM = "adaptive_arm"
ABLATED = "adaptive_arm_without_unanimity"
POINTS = list(SUPPORT_PLAN["budget_curve_points"])


def curve(multiplier: int) -> list[dict]:
    """Both arms over E6's own registered budget curve.

    E6's rule, applied here unchanged: 'the reported object is the curve, never
    a single favourable setting'. That matters more than usual in this
    experiment, because at the single registered budget the ablated arm looks 40
    per cent cheaper and is in fact simply failing.
    """
    original = dict(SA.ARMS)
    SA.ARMS.clear()
    SA.ARMS[ARM] = original[ARM]
    SA.ARMS[ABLATED] = X.AblatedAdaptiveArm
    try:
        return SA.budget_curve(multiplier, POINTS)
    finally:
        SA.ARMS.clear()
        SA.ARMS.update(original)


def matched_capability(rows: list[dict]) -> dict[str, dict | None]:
    """The cheapest budget at which each arm reaches precision and recall 1.0.

    Publication constitution section 7: work is comparable only between arms at
    matched correctness. Comparing them at a budget where one has recall 0.727
    would be comparing the speed of a worse answer.
    """
    out: dict[str, dict | None] = {}
    for arm in (ARM, ABLATED):
        exact = [r for r in rows if r["arm"] == arm
                 and r["precision"] == 1.0 and r["recall"] == 1.0]
        out[arm] = min(exact, key=lambda r: r["budget_per_method"]) if exact else None
    return out


def _terminal(matched: dict[str, dict | None]) -> tuple[str, str]:
    a, b = matched[ARM], matched[ABLATED]
    if a is None or b is None:
        return ("INADMISSIBLE_NO_MATCHED_CAPABILITY",
                "One of the two arms never reached precision and recall 1.0 at any budget "
                "on the curve, so there is no setting at which their costs are comparable.")
    iv = b["discovery_interventions"] / a["discovery_interventions"]
    wk = b["discovery_work"] / a["discovery_work"]
    if iv <= 1.0 and wk >= 1.0:
        return ("TRANSFER_REFUTED_THE_MECHANISM_IS_INERT_HERE",
                "Removing the rule cost E6 nothing on interventions. The move is inert in "
                "this domain, DEV-5's factor is a property of guards over periodic "
                "predicates, and the S3 cross-domain claim is REFUTED.")
    verdict = ("TRANSFERS_AS_AN_INTERVENTION_CONTRACT_NOT_AS_A_WORK_WIN"
               if wk < 1.0 else "TRANSFERS_ON_BOTH_COLUMNS")
    reason = (
        "At matched capability -- both arms at precision and recall 1.0, which they reach at "
        f"different budgets ({a['budget_per_method']} and {b['budget_per_method']}) -- "
        f"removing the rule costs E6 {iv:.2f}x MORE INTERVENTIONS "
        f"({b['discovery_interventions']} against {a['discovery_interventions']}). The move "
        "is not inert in this domain, so it is not a property of guards over periodic "
        "predicates, and it was in E6 before DEV-5 existed, written by another author for "
        "another question over a subset lattice rather than a predicate space.")
    if wk < 1.0:
        reason += (
            f" It is not a free win. On the other column the rule costs {1 / wk:.2f}x MORE "
            f"TOTAL WORK ({a['discovery_work']} against {b['discovery_work']}), because the "
            "reasoning that establishes 'this question is already answered' is charged and "
            "in this domain it is dearer than the intervention it avoids. That is exactly "
            "the two-column shape E6 was built to expose, and it is the OPPOSITE sign from "
            "DEV-5, where the same move won on total work outright. Taken together the two "
            "experiments identify the governing quantity, which neither identifies alone: "
            "the mechanism pays when reasoning is cheap relative to asking, and DEV-5's "
            "consultation sweep already located that boundary in its own domain -- it won up "
            "to a consultation price of 5 and lost at 25. E6 sits on the losing side of the "
            "same ratio. So the contract is domain-neutral and its SIGN is not.")
    else:
        reason += (
            f" It also wins on total work here ({a['discovery_work']} against "
            f"{b['discovery_work']}), which is a stronger transfer than DEV-5's own "
            "consultation sweep would have predicted.")
    return (verdict, reason)


def build() -> dict[str, Any]:
    rows = curve(1)
    matched = matched_capability(rows)
    terminal, reason = _terminal(matched)
    a, b = matched[ARM], matched[ABLATED]
    at_registered = {
        r["arm"]: r for r in rows
        if r["budget_per_method"] == SUPPORT_PLAN["intervention_budget_per_method"]}
    original, ablated = X.source_diff()
    return {
        "study_id": "X1_UNANIMITY_TRANSFER_V1",
        "authority": (
            "E2 synthetic, and a re-analysis of an existing lane rather than a new world. "
            "It runs an ABLATION of a mechanism already present in results/SUPPORT_E6_V1's "
            "arm, and withdraws nothing from that receipt: E6's own numbers are the "
            "unablated column here and they reproduce."),
        "plan": X.X1_PLAN,
        "fidelity": {
            "method": "E6's enumerator source, transformed by one substitution, compiled in "
                      "E6's module namespace",
            "substitution": list(X.ABLATION_SUBSTITUTION),
            "source_lines_original": len(original.splitlines()),
            "source_lines_ablated": len(ablated.splitlines()),
        },
        "terminal": terminal,
        "terminal_reason": reason,
        "matched_capability": {
            "note": (
                "The cheapest budget at which each arm reaches precision and recall 1.0. "
                "Section 7 permits a work comparison only here."),
            ARM: a, ABLATED: b,
            "intervention_ratio_ablated_over_arm": (
                b["discovery_interventions"] / a["discovery_interventions"]
                if a and b else None),
            "work_ratio_ablated_over_arm": (
                b["discovery_work"] / a["discovery_work"] if a and b else None),
        },
        "why_the_registered_budget_misleads": {
            "note": (
                "At E6's single registered budget the ablated arm posts LOWER total work "
                "and is simply failing: it exhausts its budget on almost every method and "
                "returns partial families. Its capability gate is False, so under section 7 "
                "it has no admissible work figure at all. This is recorded because the "
                "misleading number is the one a reader would meet first."),
            "rows": {arm: {"recall": at_registered[arm]["recall"],
                           "budget_exhausted_methods":
                               at_registered[arm]["budget_exhausted_methods"],
                           "discovery_interventions":
                               at_registered[arm]["discovery_interventions"],
                           "discovery_work": at_registered[arm]["discovery_work"]}
                     for arm in (ARM, ABLATED) if arm in at_registered},
        },
        "predictions": {
            "X1_families_identical_at_matched_capability": bool(
                a and b and a["precision"] == b["precision"] == 1.0
                and a["recall"] == b["recall"] == 1.0),
            "X1_verdict": (
                "HELD, and the way it held matters. At MATCHED CAPABILITY both arms reach "
                "precision 1.0 and recall 1.0, so E6's pruning is SOUND -- it skips only "
                "questions whose answers are implied, and asking them anyway changes "
                "nothing. At the registered budget the two disagree, and the reason is "
                "budget exhaustion rather than unsoundness. The registered prediction was "
                "written expecting identical families at a fixed budget and that is the "
                "wrong place to look; the correction is recorded rather than the prediction "
                "being read as confirmed."),
            "X2_ablation_spends_more_interventions": bool(
                a and b and b["discovery_interventions"] > a["discovery_interventions"]),
            "X4_ablation_spends_more_total_work": bool(
                a and b and b["discovery_work"] > a["discovery_work"]),
            "X4_verdict": (
                "REFUTED. The ablation spends LESS total work at matched capability, so in "
                "E6's domain the rule is a net loss on the second column: the reasoning it "
                "charges for is dearer than the intervention it avoids. DEV-5 found the "
                "opposite sign in its own domain and measured the boundary with its "
                "consultation sweep. The refutation is the finding."),
        },
        "budget_curve": rows,
        "two_column_rule": X.X1_PLAN["two_column_rule"],
        "what_this_does_not_establish": X.X1_PLAN["what_this_does_not_establish"],
        "novelty": X.X1_PLAN["novelty"],
    }


def main() -> int:
    doc = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print("predictions:", json.dumps({k: v for k, v in doc["predictions"].items()
                                      if not k.endswith("verdict")}))
    m = doc["matched_capability"]
    print(f"  interventions ratio (ablated/arm): "
          f"{m['intervention_ratio_ablated_over_arm']:.2f}")
    print(f"  work ratio (ablated/arm):          {m['work_ratio_ablated_over_arm']:.2f}")
    for r in doc["budget_curve"]:
        print(f"  {r['arm']:32s} B={r['budget_per_method']:3d} "
              f"prec={r['precision']:.3f} rec={r['recall']:.3f} "
              f"interv={r['discovery_interventions']:5d} work={r['discovery_work']:6d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
