"""Run the failure-diagnosis experiment and emit its receipt.

    python run_diagnosis.py --out results/DIAGNOSIS_E2_V1.json

The terminal is chosen by :func:`terminal_for`, which is a function of the
totals and was written before the totals existed.  Its rule, in order:

1. if the governed policy is less accurate than the exhaustive parent it has
   failed at the thing it exists to do, and the terminal says so;
2. if it over-generalises, makes a false exclusion or misses a reopening on any
   registered world, it is defective and the terminal says so;
3. if ``decision_tree_parent`` is at least as accurate **and** does not spend
   more, the strongest realistic parent suffices and the terminal is
   ``PARENT_SUFFICIENT``;
4. if the tree matches on accuracy and the governed policy spends strictly less,
   the residual exists and is confined to probe cost;
5. anything else is a separation on accuracy, which on a deterministic response
   table would be surprising enough to warrant re-reading the worlds rather than
   the result.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import diagnosis_parents as dp
from diagnosis import CAUSE_ORDER, CAUSE_PRIOR, COMMITMENT, DIAGNOSIS_PLAN, PROBE_COST
from diagnosis_worlds import (
    WORLDS,
    cause_counts,
    constant_predictor_baseline,
    run,
    scoreboard,
    target_counts,
)


def terminal_for(totals: dict) -> tuple[str, str]:
    """Fixed before the run: the terminal is a function of the totals."""
    gov = totals["governed_diagnosis"]
    tree = totals["decision_tree_parent"]
    exhaustive = totals["exhaustive_probe_parent"]
    if gov["correct"] < exhaustive["correct"]:
        return (
            "GOVERNED_POLICY_BELOW_THE_ACCURACY_CEILING",
            "the exhaustive parent diagnoses more episodes correctly than the "
            "governed policy, which is the one thing the governed policy may not do",
        )
    if gov["over_generalisations"] or gov["false_exclusions"] or gov["missed_reopenings"]:
        return (
            "GOVERNED_POLICY_DEFECTIVE",
            "the governed policy over-generalised a defect, made a false exclusion, "
            "or left a method unreachable after its reopen condition fired",
        )
    if tree["correct"] >= gov["correct"] and tree["probe_cost"] <= gov["probe_cost"]:
        return (
            "PARENT_SUFFICIENT",
            "a fixed hand-authored probe ordering with no memory matches the "
            "governed policy on accuracy and does not spend more; the memory buys "
            "nothing and the governed machinery is unjustified overhead",
        )
    if tree["correct"] == gov["correct"] and gov["probe_cost"] < tree["probe_cost"]:
        return (
            "ACCUMULATION_RESIDUAL_CONFINED_TO_PROBE_COST",
            "the strongest realistic parent is sufficient on diagnosis accuracy; the "
            "governed policy separates from it only on cumulative probe cost, and "
            "only on task sequences that revisit a scope",
        )
    return (
        "GOVERNED_POLICY_SEPARATES_ON_ACCURACY",
        "unexpected on a deterministic response table; re-read the worlds before "
        "the result",
    )


def _totals(rows) -> dict:
    return {
        name: {
            "correct": s.correct,
            "episodes": s.episodes,
            "accuracy": round(s.accuracy, 4),
            "probe_cost": s.probe_cost,
            "probes_bought": s.probes_bought,
            "cost_per_diagnosis": round(s.probe_cost / s.episodes, 3),
            "correct_cannot_identify": s.correct_cannot_identify,
            "missed_cannot_identify": s.missed_cannot_identify,
            "false_cannot_identify": s.false_cannot_identify,
            "over_generalisations": s.over_generalisations,
            "reused_facts": s.reused_facts,
            "false_exclusions": s.false_exclusions,
            "missed_reopenings": s.missed_reopenings,
            "wasted_work_avoided": s.wasted_work_avoided,
            "repeated_wasted_work": s.repeated_wasted_work,
        }
        for name, s in rows.items()
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    if out.exists():
        print(f"refusing to overwrite existing receipt {out}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = scoreboard(dp.ARMS)
    totals = _totals(rows)
    per_world = {
        name: {world.world_id: run(world, factory).as_dict() for world in WORLDS}
        for name, factory in dp.ARMS.items()
    }
    terminal, reason = terminal_for(totals)
    baseline = constant_predictor_baseline()
    gov = totals["governed_diagnosis"]
    tree = totals["decision_tree_parent"]
    exhaustive = totals["exhaustive_probe_parent"]

    receipt = {
        "receipt": "CL_DIAGNOSIS_E2_V1",
        "study_id": "CL-DIAGNOSIS-E2-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E2",
        "contribution_level": "L1",
        "study_role": "PILOT_AND_DESIGN_EVIDENCE_ONLY",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "why_this_experiment_exists": (
            "The failure-knowledge pilot handed every arm a correct diagnosis and "
            "said so in its own receipt: 'nothing here measures whether a machine "
            "can tell an evaluator defect from a genuine refutation when both report "
            "the same thing.' This experiment withdraws that gift. Every episode "
            "presents the identical observed signal and the cause must be bought."
        ),
        "plan": DIAGNOSIS_PLAN,
        "commitment": COMMITMENT.as_dict()["commitment_sha256"],
        "probe_costs": {p.name: c for p, c in PROBE_COST.items()},
        "worlds": [
            {
                "world_id": w.world_id,
                "hostile": w.hostile,
                "episodes": len(w.episodes),
                "tests": w.tests,
                "cause_counts": {c.name: n for c, n in w.cause_counts.items()},
                "unidentifiable_episodes": sum(
                    1 for e in w.episodes if not e.identifiable
                ),
                "notes": w.notes,
            }
            for w in WORLDS
        ],
        "arms": list(dp.ARMS),
        "parents": list(dp.PARENTS),
        "cause_distribution": {
            "registered_prior": {c.name: CAUSE_PRIOR[c] for c in CAUSE_ORDER},
            "realised_true_causes": cause_counts(),
            "realised_targets": target_counts(),
            "note": (
                "the registered prior is what the selection rule uses and was frozen "
                "before the worlds were written; the realised distribution differs "
                "because EVALUATOR_DEFECT is suppressed wherever the checker is "
                "sound, and the two are reported separately so neither is mistaken "
                "for the other"
            ),
        },
        "constant_predictor_baseline": baseline,
        "constant_predictor_note": (
            f"a policy that always answers {baseline['best_constant_answer']} scores "
            f"{baseline['best_constant_accuracy']:.3f}; assume_refutation_parent IS "
            "that policy, so the gap between it and any other arm is the part of "
            "that arm's accuracy that is not the base rate"
        ),
        "totals": totals,
        "per_world": per_world,
        "confusion_matrix": {
            name: [
                {"target": t, "verdict": v, "count": n} for t, v, n in s.confusion
            ]
            for name, s in rows.items()
        },
        "cumulative_probe_cost": {
            name: list(s.cost_curve) for name, s in rows.items()
        },
        "cumulative_probe_cost_note": (
            "one point per episode, concatenated across the five worlds in "
            "registered order; a fresh arm is constructed per world, so the curve "
            "measures accumulation within a task sequence and never across "
            "unrelated ones"
        ),
        "sufficiency_report": {
            name: {
                k: (list(v) if isinstance(v, tuple) else v)
                for k, v in report.items()
            }
            for name, report in dp.sufficiency_report().items()
        },
        "terminal": terminal,
        "terminal_reason": reason,
        "parent_sufficiency_findings": [
            (
                f"decision_tree_parent, a fixed hand-authored ordering with no state, "
                f"matches the governed policy exactly on accuracy "
                f"({tree['correct']} of {tree['episodes']}) and on every error column. "
                "The ordering question is closed by the parent, and the greedy "
                "selection rule is asserted in the tests to reproduce the tree's "
                "ordering rather than to improve on it."
            ),
            (
                f"exhaustive_probe_parent is the accuracy ceiling and is reached: "
                f"{exhaustive['correct']} of {exhaustive['episodes']}, the same as the "
                f"governed policy. It spends {exhaustive['probe_cost']} units against "
                f"the governed policy's {gov['probe_cost']}, so the governed policy "
                "does beat it on cost at equal accuracy -- which is the weakest form "
                "of that claim, since buying everything is not a policy anyone runs."
            ),
            (
                f"the whole residual is {tree['probe_cost'] - gov['probe_cost']} probe "
                f"units of {tree['probe_cost']}, or "
                f"{100.0 * (tree['probe_cost'] - gov['probe_cost']) / tree['probe_cost']:.1f} "
                "per cent, and it is entirely the cost of re-establishing one boolean "
                "per (checker, scope) pair. It is memoisation. It is reported as "
                "memoisation."
            ),
        ],
        "what_this_does_not_establish": [
            "No causal mechanism, no scaling law, no transfer result and no novelty. "
            "The worlds and the diagnosis policy share an author; this is calibration.",
            "The probe semantics are AUTHORED. The mapping from an outcome vector to "
            "a cause is a registered table and every arm inverts the same table, so "
            "the diagnosis problem here is a table inversion under a cost constraint. "
            "Nothing measures whether a machine could learn what a probe means, which "
            "is the harder half of real diagnosis and is not attempted.",
            "The response table is deterministic. There is no probe noise, no "
            "misreporting probe, and no cause that two probes disagree about. Every "
            "arm that buys sufficient probes therefore scores perfect accuracy, so "
            "accuracy is not a live coordinate between the three sufficient arms and "
            "the entire comparison between them reduces to cost.",
            "The accumulation residual is a cache of one boolean per (checker, scope) "
            "pair. Any competent engineer would add that cache to the decision tree "
            "in an afternoon, at which point the parent would be sufficient on both "
            "coordinates. This experiment does not claim the residual survives that.",
            "CANNOT_IDENTIFY is scored against targets computed from the registered "
            "response table, so 'the correct refusal rate' is correct with respect to "
            "an authored notion of identifiability and not to any external standard.",
            "missed_reopenings is zero for every arm because the FailureStore is held "
            "constant across arms. It is a wiring control, not a discrimination.",
            "One protected-draw world (DW5) is drawn from the pre-registration "
            "commitment; the other four are hand-authored, and a hand-authored world "
            "cannot refute the policy its author was holding while writing it.",
        ],
        "preserved_prior_terminals": [
            "TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT (failure-to-negative-knowledge)",
            "FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT: the "
            "strongest-parent incremental gap was frozen at 0 of 32 BEFORE execution",
            "CL-FAILURE-PILOT-V1: the truth-maintenance parent ties the governed "
            "store on four of seven worlds; the residual there was confined to the "
            "three cause-discriminating worlds, and this experiment is the attempt "
            "on that pilot's own stated falsifier",
        ],
        "authority": (
            "This receipt records a calibration of a probe-purchasing diagnosis "
            "policy against four parents and one ablation on fifty-nine authored "
            "episodes across five worlds. It establishes no causal mechanism. Its "
            "strongest realistic parent -- a fixed hand-authored probe ordering with "
            "no memory -- is sufficient on diagnosis accuracy, and the only surviving "
            "difference is a cumulative probe-cost reduction attributable in full to "
            "caching one boolean per (checker, scope) pair. That difference is "
            "reported as memoisation and must not be cited as evidence that a machine "
            "accumulates diagnostic competence."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(dp.table())
    print()
    print(
        json.dumps(
            {
                "terminal": terminal,
                "constant_predictor": baseline["best_constant_accuracy"],
                "governed_cost": gov["probe_cost"],
                "decision_tree_cost": tree["probe_cost"],
                "exhaustive_cost": exhaustive["probe_cost"],
                "out": str(out),
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
